"""
End-to-end browser tests (development only — not needed to run the website).

Runs the real pages in headless Chromium. The site is served from a
SUBFOLDER (http://127.0.0.1:<port>/<project-folder>/) to check that every
path works the way it will on GitHub Pages (https://user.github.io/repo/).

Requirements:  pip install playwright  &&  python -m playwright install chromium
Run:           python tests/e2e_test.py

The tests start from an empty website: they serve a temporary copy of the
project in which the data files (the five content files and the vocabulary
questions) are empty, so the real lessons and questions are never read or
changed.

All test content is typed into the content manager during the test (or
served from inside this script). It is placeholder text such as
"Test prompt one", not educational content, and it is never written to the
project's data files.
"""
import functools
import http.server
import json
import os
import pathlib
import re
import time
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback

from playwright.sync_api import expect, sync_playwright

PROJECT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = pathlib.Path(os.environ.get("E2E_SCREENSHOTS", tempfile.mkdtemp(prefix="g12-shots-")))
SHOTS.mkdir(parents=True, exist_ok=True)
DOWNLOADS = pathlib.Path(tempfile.mkdtemp(prefix="g12-downloads-"))

results = []  # (section, ok, detail)


def record(section, ok, detail=""):
    results.append((section, ok, detail))
    print(("PASS " if ok else "FAIL ") + section + (": " + detail if detail else ""))


# ---------------------------------------------------------------- server

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


DATA_FILES = [("units.json", "units"), ("grammar-lessons.json", "lessons"), ("grammar-summaries.json", "summaries"),
              ("grammar-questions.json", "questions"), ("reading-passages.json", "passages"),
              ("vocabulary-questions.json", "units")]


def empty_copy():
    """A temporary copy of the website (same folder name) with empty data files."""
    root = pathlib.Path(tempfile.mkdtemp(prefix="g12-site-"))
    site = root / PROJECT.name
    shutil.copytree(PROJECT, site, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
    for name, key in DATA_FILES:
        (site / name).write_text(json.dumps({"schemaVersion": 2, key: []}, indent=2) + "\n", encoding="utf-8")
    return site


def start_server():
    site = empty_copy()
    handler = functools.partial(QuietHandler, directory=str(site.parent))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/%s/" % (server.server_address[1], site.name)


# ---------------------------------------------------------------- helpers

AUDIT_JS = r"""
() => {
  const problems = [];
  const seen = {};
  document.querySelectorAll('[id]').forEach(n => {
    if (seen[n.id]) problems.push('duplicate id: ' + n.id);
    seen[n.id] = true;
  });
  document.querySelectorAll('input, select, textarea').forEach(n => {
    if (n.type === 'hidden') return;
    const ok = (n.labels && n.labels.length) || n.getAttribute('aria-label') || n.getAttribute('aria-labelledby');
    if (!ok) problems.push('control without label: ' + (n.id || n.name || n.outerHTML.slice(0, 80)));
  });
  document.querySelectorAll('a[href], button').forEach(n => {
    const name = (n.getAttribute('aria-label') || n.textContent || '').trim();
    if (!name) problems.push('link/button without a name: ' + n.outerHTML.slice(0, 80));
  });
  const h1 = document.querySelectorAll('h1').length;
  if (h1 !== 1) problems.push('page has ' + h1 + ' h1 headings');
  if (!document.documentElement.lang) problems.push('html lang missing');
  let previous = 0;
  document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
    if (h.closest('[hidden]')) return;
    const level = Number(h.tagName[1]);
    if (previous && level > previous + 1) problems.push('heading jumps from h' + previous + ' to h' + level + ': ' + h.textContent.trim().slice(0, 40));
    previous = level;
  });
  ['aria-describedby', 'aria-labelledby'].forEach(attr => {
    document.querySelectorAll('[' + attr + ']').forEach(n => {
      n.getAttribute(attr).split(/\s+/).filter(Boolean).forEach(id => {
        if (!document.getElementById(id)) problems.push(attr + ' points to missing id: ' + id);
      });
    });
  });
  if (document.documentElement.scrollWidth > window.innerWidth + 1) {
    problems.push('page scrolls sideways: ' + document.documentElement.scrollWidth + ' > ' + window.innerWidth);
  }
  return problems;
}
"""


def audit(page, label):
    problems = page.evaluate(AUDIT_JS)
    record("accessibility checks: " + label, not problems, "; ".join(problems[:6]))


def watch(page):
    """Collect console errors, page errors and failed requests."""
    page.errors = []
    # Errors, and warnings about interface text with no Arabic translation.
    page.on("console", lambda m: page.errors.append("console %s: %s" % (m.type, m.text))
            if m.type == "error" or "[i18n]" in m.text else None)
    page.on("pageerror", lambda e: page.errors.append("page error: %s" % e))
    page.on("requestfailed", lambda r: page.errors.append("request failed: %s" % r.url))
    return page


def no_errors(page, label):
    record("no browser errors: " + label, not page.errors, "; ".join(page.errors[:5]))
    page.errors.clear()


def settle(page):
    """Wait until the page has finished loading its content (and its data
    requests are done, so leaving the page does not cancel one)."""
    page.wait_for_function("!document.querySelector('.loading')")
    page.wait_for_load_state("networkidle")


def draft(page):
    raw = page.evaluate("() => localStorage.getItem('g12-content-draft-v1')")
    return json.loads(raw)["library"] if raw else None


# The data files: the five content files and the vocabulary questions (at the top level, next to index.html).
DATA_ROUTE = re.compile(r".*/(units|grammar-lessons|grammar-summaries|grammar-questions|reading-passages|vocabulary-questions)\.json(\?.*)?$")
# Every stylesheet, script and data file of the site.
ASSET_ROUTE = re.compile(r".*/[^/]+\.(css|js|json)(\?.*)?$")


def run_section(name, fn, *args):
    try:
        fn(*args)
    except Exception as error:  # noqa: BLE001 - report and continue with the next section
        record(name + " (section stopped)", False, "%s\n%s" % (error, traceback.format_exc(limit=3)))


# ---------------------------------------------------------------- 1. empty site

def empty_site(browser, base):
    context = browser.new_context()
    page = watch(context.new_page())
    pages = {
        "index.html": ("No content added yet", "manage.html"),
        "summaries.html": ("No summaries added yet", "manage.html#summaries/new"),
        "practice.html": ("No practice questions added yet", "manage.html#questions/new"),
        "reading.html": ("No reading passages added yet", "manage.html#passages/new"),
        "vocabulary.html": ("No vocabulary questions yet", None),
    }
    for path, (heading, href) in pages.items():
        page.goto(base + path)
        expect(page.locator(".empty-state h2")).to_have_text(heading)
        if href is None:  # vocabulary questions are added to their file, not in the content manager
            record("empty state on " + path, page.locator(".empty-state a").count() == 0)
        else:
            link = page.locator(".empty-state a").first
            record("empty state on " + path, link.get_attribute("href") == href, "button links to " + str(link.get_attribute("href")))
        audit(page, path + " (empty)")
        no_errors(page, path + " (empty)")
    page.goto(base + "index.html")
    page.screenshot(path=str(SHOTS / "01-home-empty.png"), full_page=True)
    # An unknown passage id shows a friendly message.
    page.goto(base + "reading.html?passage=does-not-exist")
    expect(page.locator("h1")).to_have_text("Passage not found")
    record("unknown passage shows 'not found'", True)
    # The Grammar Lessons page was removed from the website.
    record("the Grammar Lessons page is gone", not (PROJECT / "grammar.html").exists() and not (PROJECT / "grammar.js").exists())
    no_errors(page, "not-found pages")
    context.close()


# ---------------------------------------------------------------- 2. content manager

def manager_flow(context, base):
    page = watch(context.new_page())
    dialogs = []

    def on_dialog(dialog):
        dialogs.append(dialog.message)
        if getattr(page, "dismiss_next", False):
            page.dismiss_next = False
            dialog.dismiss()
        else:
            dialog.accept()

    page.on("dialog", on_dialog)
    page.goto(base + "manage.html")
    expect(page.locator("#manager-view .empty-state h3")).to_have_text("No lessons added yet")
    expect(page.locator(".status-bar")).to_contain_text("No unpublished changes")
    audit(page, "manager (empty)")

    # --- Lesson 1: validation, then four section types
    page.click("text=Add a lesson >> nth=0")
    expect(page).to_have_url(re.compile(r"#lessons/new$"))
    page.click("button:has-text('Save lesson')")
    expect(page.locator(".error-summary")).to_contain_text("Enter a title")
    record("empty lesson form shows an error summary",
           page.evaluate("() => document.activeElement.classList.contains('error-summary')")
           and page.get_attribute("#f-title", "aria-invalid") == "true")

    page.fill("#f-title", "Test lesson one")
    record("lesson ID fills in from the title", page.input_value("#f-id") == "test-lesson-one", page.input_value("#f-id"))
    page.fill("#f-description", "Placeholder description")
    page.click("button:has-text('Add section')")
    page.fill("#sec-0-heading", "Heading A")
    page.fill("#sec-0-text", "Paragraph one.\n\nParagraph two.")
    page.click("button:has-text('Add section')")
    page.select_option("#sec-1-type", "table")
    page.fill("#sec-1-columns", "Col 1\nCol 2")
    page.fill("#sec-1-rows", "a | b\nc")
    page.click("button:has-text('Add section')")
    page.select_option("#sec-2-type", "mistakes")
    page.fill("#sec-2-m-0-avoid", "wrong text")
    page.fill("#sec-2-m-0-use", "right text")
    page.click("button:has-text('Add section')")
    page.select_option("#sec-3-type", "note")
    page.fill("#sec-3-text", "نص تجريبي")
    page.select_option("#sec-3-lang", "ar")
    page.click("button:has-text('Save lesson')")
    expect(page.locator(".error-summary")).to_contain_text("row 2 has 1 cell, but the table has 2 columns")
    record("bad table row is reported and linked to its section", page.get_attribute("#sec-1-type", "aria-invalid") == "true")
    page.fill("#sec-1-rows", "a | b\nc | d")
    page.screenshot(path=str(SHOTS / "02-lesson-editor.png"), full_page=True)
    audit(page, "lesson editor")
    page.click("button:has-text('Save lesson')")
    expect(page).to_have_url(re.compile(r"#lessons$"))
    expect(page.locator(".manager-message")).to_contain_text("Lesson “Test lesson one” saved.")
    record("lesson saved and listed", page.locator(".manager-row").count() == 1)

    # --- Lesson 2 (reviewed), then reorder
    page.click("text=Add a lesson >> nth=0")
    page.fill("#f-title", "Test lesson two")
    page.check("#f-reviewed")
    page.click("button:has-text('Add section')")
    page.fill("#sec-0-text", "Only paragraph.")
    page.click("button:has-text('Save lesson')")
    expect(page.locator(".manager-row")).to_have_count(2)
    page.click("[data-id='test-lesson-two'][data-action='up']")
    expect(page.locator(".manager-row-title").first).to_have_text("Test lesson two")
    focused = page.evaluate("() => document.activeElement.getAttribute('data-id')")
    record("move up reorders lessons and keeps focus on the moved item", focused == "test-lesson-two", "focus on " + str(focused))

    # --- Summary with a point-level validation error
    page.click(".manager-nav >> text=Summaries")
    page.click("text=Add a summary >> nth=0")
    page.fill("#f-title", "Test summary")
    page.select_option("#f-topic", "test-lesson-one")
    page.fill("#pt-0-title", "P1")
    page.fill("#pt-0-rule", "Rule one")
    page.fill("#pt-0-example", "Example one")
    page.click("button:has-text('Add point')")
    page.fill("#pt-1-example", "Example without a rule")
    page.fill("#f-remember", "Reminder one\nReminder two")
    page.click("button:has-text('Save summary')")
    expect(page.locator(".error-summary")).to_contain_text("Point 2 needs a rule.")
    page.fill("#pt-1-rule", "Rule two")
    page.click("button:has-text('Save summary')")
    expect(page.locator(".manager-row")).to_have_count(1)
    record("summary saved after fixing the point error", True)

    # --- Grammar questions
    page.click(".manager-nav >> text=Grammar questions")
    page.click("text=Add a question >> nth=0")
    page.select_option("#f-topic", "test-lesson-one")
    page.fill("#f-prompt", "Test prompt ___ one")
    for i, text in enumerate(["Opt A", "Opt B", "Opt C", "Opt D"]):
        page.fill("#f-option-%d" % i, text)
    page.check("#f-correct-1")
    page.fill("#f-explanation", "Placeholder explanation")
    page.select_option("#f-difficulty", "easy")
    audit(page, "question editor")
    page.click("button:has-text('Save and add another')")
    expect(page.locator(".manager-message")).to_contain_text("Question q-001 saved.")
    expect(page).to_have_url(re.compile(r"#questions/new$"))
    record("'Save and add another' keeps the same topic", page.input_value("#f-topic") == "test-lesson-one")

    page.fill("#f-prompt", "Test prompt two")
    page.fill("#f-option-0", "X")
    page.fill("#f-option-1", "Y")
    page.check("#f-correct-0")
    page.check("#f-reviewed")
    page.click("button:has-text('Save question')")
    expect(page.locator(".manager-row")).to_have_count(2)

    page.click("text=Add a question >> nth=0")
    page.click("button:has-text('Save question')")
    summary = page.locator(".error-summary").inner_text()
    record("question form requires a prompt and a correct option",
           "Write the question." in summary and "Mark which option is the correct answer." in summary, summary.replace("\n", " | "))
    page.fill("#f-prompt", "Test prompt three")
    page.fill("#f-option-0", "Same")
    page.fill("#f-option-1", "Same")
    page.check("#f-correct-0")
    page.click("button:has-text('Save question')")
    expect(page.locator(".error-summary")).to_contain_text("is the same as another option")
    page.check("#f-type-short")
    page.fill("#f-model-answer", "Placeholder model answer")
    page.click("button:has-text('Save question')")
    expect(page.locator(".manager-row")).to_have_count(3)
    record("three grammar questions saved (2 multiple choice, 1 short answer)", True)

    page.select_option("#filter-topic", "")
    expect(page.locator("#manager-view")).to_contain_text("Showing 0 of 3 questions")
    page.select_option("#filter-topic", "__all__")
    page.fill("#filter-text", "two")
    expect(page.locator(".manager-row")).to_have_count(1)
    record("question filters work", True)
    page.fill("#filter-text", "")

    # --- Reading passage and its questions
    page.click(".manager-nav >> text=Reading passages")
    page.click("text=Add a passage >> nth=0")
    page.fill("#f-title", "Test passage")
    page.fill("#f-level", "Test level")
    page.fill("#f-text", "First paragraph has five words.\n\nSecond paragraph.")
    expect(page.locator("#f-text-count")).to_have_text("2 paragraphs · 7 words")
    page.click("button:has-text('Save passage')")
    expect(page).to_have_url(re.compile(r"#passages/edit/test-passage$"))
    expect(page.locator(".manager-message")).to_contain_text("You can now add questions")
    page.click("text=Add a question")
    page.fill("#f-prompt", "Passage question one")
    page.fill("#f-option-0", "P")
    page.fill("#f-option-1", "Q")
    page.check("#f-correct-1")
    page.click("button:has-text('Save question')")
    expect(page).to_have_url(re.compile(r"#passages/edit/test-passage$"))
    page.click("text=Add a question")
    page.check("#f-type-short")
    page.fill("#f-prompt", "Passage question two")
    page.fill("#f-model-answer", "Placeholder passage answer")
    page.click("button:has-text('Save question')")
    expect(page.locator("#passage-questions-heading")).to_have_text("Questions about this passage (2)")
    page.click("[data-id='q-002'][data-action='up']")
    expect(page.locator(".manager-row-title").first).to_have_text("Passage question two")
    record("passage questions added and reordered", True)

    # --- Rename a lesson id: links follow
    page.click(".manager-nav >> text=Lessons")
    page.click("[aria-label='Edit lesson “Test lesson one”']")
    page.fill("#f-id", "renamed-lesson")
    page.click("button:has-text('Save changes')")
    expect(page.locator(".manager-message")).to_contain_text("now use the new topic ID")
    library = draft(page)
    record("renaming a lesson updates linked questions and summaries",
           all(q.get("topicId") == "renamed-lesson" for q in library["questions"]) and library["summaries"][0]["topicId"] == "renamed-lesson")

    # --- Delete lesson two
    page.click("[data-id='test-lesson-two'][data-action='delete']")
    expect(page.locator(".manager-row")).to_have_count(1)
    record("delete asks for confirmation and removes the lesson", any("Delete the lesson" in d for d in dialogs))

    # --- Unsaved-changes guard
    page.click("text=Add a lesson >> nth=0")
    page.fill("#f-title", "Unsaved title")
    page.dismiss_next = True
    page.click(".manager-nav >> text=Summaries")
    page.wait_for_timeout(200)
    record("leaving a form with unsaved changes asks first (Cancel stays)",
           page.url.endswith("#lessons/new") and page.input_value("#f-title") == "Unsaved title")
    page.click(".manager-nav >> text=Summaries")  # accept this time
    expect(page).to_have_url(re.compile(r"#summaries$"))

    nav = page.locator(".manager-nav").inner_text()
    record("navigation counts", all(s in nav for s in ["Lessons (1)", "Summaries (1)", "Grammar questions (3)", "Reading passages (1)"]), nav.replace("\n", " "))
    expect(page.locator(".status-bar")).to_contain_text("You have unpublished changes")
    page.click(".manager-nav >> text=Import & export")
    expect(page.locator("#check-heading + p + p")).to_have_text("No errors found.")
    audit(page, "import & export view")
    page.screenshot(path=str(SHOTS / "03-manager-tools.png"), full_page=True)
    no_errors(page, "content manager")
    return page


# ---------------------------------------------------------------- 3. preview on student pages

def answer_current(page, choice):
    page.click(".options label:has-text('%s')" % choice)
    page.click("button:has-text('Submit answer')")


def student_pages_in_preview(page, base):
    page.goto(base + "manage.html")
    page.check("#preview-toggle")
    expect(page.locator(".manager-message")).to_contain_text("Preview is on")

    page.goto(base + "index.html")
    expect(page.locator("#preview-banner")).to_be_visible()
    counts = [page.inner_text("[data-count='%s']" % k) for k in ["summaries", "questions", "passages", "vocabulary"]]
    record("home page counts in preview", counts == ["1 summary", "3 questions", "1 passage", "No questions yet"], str(counts))
    record("home page has no Grammar Lessons card", page.locator("[data-count='lessons'], a[href^='grammar.html']").count() == 0)

    page.goto(base + "summaries.html?topic=renamed-lesson")
    expect(page.locator(".summary-card h2, .summary-card h3").first).to_have_text("Test summary")
    expect(page.locator(".summary-card tbody tr")).to_have_count(2)
    record("summary links to practice, not to a lesson page",
           page.locator("a[href^='grammar.html']").count() == 0 and page.locator("a[href^='practice.html?topic=renamed-lesson']").count() >= 1)
    audit(page, "summaries page")
    page.screenshot(path=str(SHOTS / "04-summaries-page.png"), full_page=True)

    # --- Practice: unreviewed wording, retry, reviewed wording, short answer, results
    page.goto(base + "practice.html?topic=renamed-lesson")
    record("practice topic is preselected from the link", page.input_value("#practice-topic") == "renamed-lesson")
    expect(page.locator("label[for='practice-count-all']")).to_have_text("All available questions (3)")
    audit(page, "practice setup")
    page.click("button:has-text('Start practice')")
    record("practice: no review label next to the question",
           page.locator(".quiz .badge--reviewed, .quiz .badge--unreviewed").count() == 0)
    seen = set()
    for _ in range(3):
        legend = page.locator(".question-legend").inner_text()
        if "one" in legend:
            answer_current(page, "Opt A")
            expect(page.locator(".feedback")).to_contain_text("different from the suggested answer")
            record("unreviewed wrong answer is not called 'incorrect'", "Not correct" not in page.locator(".feedback").inner_text())
            record("focus moves to the feedback after submitting",
                   page.evaluate("() => document.activeElement.classList.contains('feedback')"))
            page.click("button:has-text('Try again')")
            record("tried option is disabled on retry", page.is_disabled(".options input >> nth=0"))
            answer_current(page, "Opt B")
            expect(page.locator(".feedback")).to_contain_text("matches the suggested answer")
            expect(page.locator(".feedback .review-note")).to_be_visible()
            page.screenshot(path=str(SHOTS / "05-practice-feedback.png"), full_page=True)
            seen.add("unreviewed")
        elif "two" in legend:
            answer_current(page, "X")
            expect(page.locator(".feedback-title")).to_have_text("Correct!")
            seen.add("reviewed")
        else:
            page.fill(".question-form textarea", "My placeholder answer")
            page.click("button:has-text('Submit answer')")
            expect(page.locator(".feedback")).to_contain_text("Placeholder model answer")
            seen.add("short")
        audit(page, "practice question")
        page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
    record("all three question kinds were shown", seen == {"unreviewed", "reviewed", "short"}, str(seen))
    expect(page.locator(".score-number")).to_have_text("1 / 2")
    expect(page.locator(".quiz .notice")).to_contain_text("Provisional score")
    audit(page, "practice results")
    page.screenshot(path=str(SHOTS / "06-practice-results.png"), full_page=True)
    page.click("button:has-text('Retry missed questions (1)')")
    expect(page.locator(".quiz-progress-text")).to_have_text("Missed questions — Question 1 of 1")
    answer_current(page, "Opt C")
    page.click("button:has-text('Show suggested answer')")
    expect(page.locator(".feedback-title")).to_have_text("Suggested answer: Opt B")
    page.click("button:has-text('See results')")
    expect(page.locator(".score-number")).to_have_text("0 / 1")
    page.click("button:has-text('Restart quiz')")
    expect(page.locator(".quiz-progress-text")).to_have_text("Question 1 of 3")
    page.click("text=← Change practice settings")
    expect(page.locator("#setup-heading")).to_be_visible()
    record("practice: score, retry missed, show answer, restart and change settings work", True)

    # --- Reading
    page.goto(base + "reading.html")
    expect(page.locator(".card .passage-meta")).to_contain_text("2 questions")
    page.click("text=Read passage")
    expect(page.locator(".passage-paragraphs li")).to_have_count(2)
    expect(page.locator(".mode-switch button[aria-pressed='true']")).to_have_text("All questions")
    expect(page.locator(".worksheet-q .question-legend").first).to_contain_text("Passage question two")
    page.click(".mode-switch button:has-text('One at a time')")
    expect(page.locator(".question-legend, .question-form label.question-legend").first).to_contain_text("Passage question two")
    page.fill(".question-form textarea", "Reading answer")
    page.click("button:has-text('Submit answer')")
    page.click("button:has-text('Next question')")
    answer_current(page, "P")
    page.click("button:has-text('Show suggested answer')")
    page.click("button:has-text('See results')")
    expect(page.locator(".score-number")).to_have_text("0 / 1")
    expect(page.locator(".review-list li")).to_have_count(2)
    record("reading: passage, questions in set order, short answer and results work", True)
    audit(page, "reading results")
    page.screenshot(path=str(SHOTS / "07-reading.png"), full_page=True)

    # --- Phone width
    page.set_viewport_size({"width": 375, "height": 800})
    for path in ["index.html", "summaries.html", "practice.html", "reading.html?passage=test-passage", "vocabulary.html", "manage.html#lessons/edit/renamed-lesson"]:
        page.goto(base + path)
        page.wait_for_timeout(250)
        audit(page, "phone width " + path)
    page.screenshot(path=str(SHOTS / "08-phone-lesson-editor.png"), full_page=True)
    page.goto(base + "practice.html")
    page.click("button:has-text('Start practice')")
    page.screenshot(path=str(SHOTS / "09-phone-practice.png"), full_page=True)
    page.set_viewport_size({"width": 1280, "height": 900})

    # --- Stop preview: back to the (empty) published files
    page.goto(base + "summaries.html")
    page.click("#preview-banner button:has-text('Stop preview')")
    expect(page.locator(".empty-state h2")).to_have_text("No summaries added yet")
    record("stopping preview shows the published files again", page.locator("#preview-banner").count() == 0)
    no_errors(page, "student pages in preview")


# ---------------------------------------------------------------- 4. export and publish

def export_files(page, base):
    page.goto(base + "manage.html#tools")
    names = {}
    for key, file in [("units", "units.json"), ("lessons", "grammar-lessons.json"), ("summaries", "grammar-summaries.json"),
                      ("questions", "grammar-questions.json"), ("passages", "reading-passages.json")]:
        with page.expect_download() as info:
            page.click("button:has-text('Download %s')" % file)
        download = info.value
        target = DOWNLOADS / download.suggested_filename
        download.save_as(target)
        names[key] = target
    with page.expect_download() as info:
        page.click("button:has-text('Download backup file')")
    backup = DOWNLOADS / info.value.suggested_filename
    info.value.save_as(backup)
    record("five data files and a backup downloaded",
           all(p.exists() for p in names.values()) and re.match(r"grade12-english-backup-\d{4}-\d{2}-\d{2}\.json", backup.name) is not None,
           ", ".join(sorted(p.name for p in names.values())) + ", " + backup.name)

    check = subprocess.run(["node", str(PROJECT / "tools" / "validate-content.js"), str(DOWNLOADS)], capture_output=True, text=True)
    record("exported files pass the command-line validator", check.returncode == 0, check.stdout.strip().splitlines()[-1] if check.stdout else check.stderr)
    return names, backup


def serve_json(body, status=200):
    """Route handler that answers with the given text (one argument only: route)."""
    def handler(route):
        route.fulfill(status=status, content_type="application/json", body=body)
    return handler


def published_site(browser, base, files):
    """Serve the exported files as if they were uploaded to GitHub (no draft in this browser)."""
    context = browser.new_context()
    for key, path in files.items():
        context.route("**/" + path.name, serve_json(path.read_text(encoding="utf-8")))
    page = watch(context.new_page())
    page.goto(base + "summaries.html")
    expect(page.locator(".summary-card").first).to_contain_text("Test summary")
    record("published files show on the student pages without preview", page.locator("#preview-banner").count() == 0)
    page.goto(base + "manage.html")
    expect(page.locator(".status-bar")).to_contain_text("No unpublished changes")
    record("manager loads published content as its starting point", "Lessons (1)" in page.locator(".manager-nav").inner_text())
    no_errors(page, "published site")
    context.close()

    # A hand-edited file with one broken question: the rest still works.
    context = browser.new_context()
    broken = {"schemaVersion": 1, "questions": [
        {"id": "q-001", "type": "mcq", "prompt": "Works", "options": ["A", "B"], "answer": "A", "reviewStatus": "unreviewed"},
        {"id": "q-002", "type": "mcq", "prompt": "Broken", "options": ["A", "B"], "answer": "C", "reviewStatus": "unreviewed"}]}
    context.route("**/grammar-questions.json", serve_json(json.dumps(broken)))
    page = watch(context.new_page())
    page.goto(base + "practice.html")
    expect(page.locator("main")).to_contain_text("1 item could not be shown")
    expect(page.locator("#practice-topic option").first).to_have_text("All topics (1)")
    record("a broken item is skipped with a notice; the rest still works", True)
    no_errors(page, "broken item")
    context.close()

    # Invalid JSON and a missing file show a clear message instead of a blank page.
    context = browser.new_context()
    context.route("**/reading-passages.json", serve_json("{ not json"))
    context.route("**/grammar-summaries.json", serve_json("missing", status=404))
    context.route("**/vocabulary-questions.json", serve_json("{ not json"))
    page = context.new_page()
    page.goto(base + "reading.html")
    expect(page.locator(".notice--error")).to_contain_text("contains invalid JSON")
    page.goto(base + "summaries.html")
    expect(page.locator(".notice--error")).to_contain_text("HTTP 404")
    page.goto(base + "vocabulary.html")
    expect(page.locator(".notice--error")).to_contain_text("contains invalid JSON")
    record("invalid or missing data files show an error message", True)
    context.close()


# ---------------------------------------------------------------- 5. import

def import_flow(browser, base, backup):
    context = browser.new_context()
    page = watch(context.new_page())
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto(base + "manage.html#tools")

    page.set_input_files("#import-files", str(backup))
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator("#import-result")).to_contain_text("Import complete")
    nav = page.locator(".manager-nav").inner_text()
    record("backup import (merge) restores everything", "Lessons (1)" in nav and "Grammar questions (3)" in nav and "Reading passages (1)" in nav, nav.replace("\n", " "))

    page.set_input_files("#import-files", str(backup))
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator("#import-result")).to_contain_text("Lessons: 0 added, 1 updated.")
    record("importing the same backup again updates instead of duplicating", True)

    bad = DOWNLOADS / "bad-questions.json"
    bad.write_text(json.dumps({"schemaVersion": 1, "questions": [
        {"id": "q-900", "type": "mcq", "prompt": "Bad", "options": ["A", "B"], "answer": "Z", "reviewStatus": "unreviewed"}]}))
    page.set_input_files("#import-files", str(bad))
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator("#import-result")).to_contain_text("Nothing was imported")
    expect(page.locator("#import-result")).to_contain_text("does not exactly match any option")
    record("an invalid file is rejected and nothing changes", "Grammar questions (3)" in page.locator(".manager-nav").inner_text())

    notjson = DOWNLOADS / "not-json.json"
    notjson.write_text("hello")
    page.set_input_files("#import-files", str(notjson))
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator("#import-result")).to_contain_text("is not valid JSON")

    single = DOWNLOADS / "one-question.json"
    single.write_text(json.dumps({"schemaVersion": 1, "questions": [
        {"id": "q-777", "type": "mcq", "prompt": "Replacement", "options": ["A", "B"], "answer": "A", "reviewStatus": "unreviewed"}]}))
    page.set_input_files("#import-files", str(single))
    page.check("#import-replace")
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator(".manager-nav")).to_contain_text("Grammar questions (1)")
    record("replace import swaps only the imported type", "Lessons (1)" in page.locator(".manager-nav").inner_text())

    page.click("button:has-text('Discard my draft')")
    expect(page.locator(".manager-nav")).to_contain_text("Lessons (0)")
    record("discarding the draft returns to the published (empty) files", draft(page) is None)
    no_errors(page, "import")
    context.close()


# ---------------------------------------------------------------- 6. missing files, loading and error states

def missing_files_and_states(browser, base):
    # a) Website files not uploaded (only the pages): a clear message, in both languages.
    context = browser.new_context()
    context.route(ASSET_ROUTE, serve_json("Not found", status=404))
    page = context.new_page()
    for path in ["index.html", "vocabulary.html"]:
        page.goto(base + path)
        alert = page.locator("#load-failure")
        expect(alert).to_be_visible()
        text = alert.inner_text()
        record("missing files: clear message on " + path,
               "style.css" in text and "i18n-ar.js" in text and "common.js" in text
               and "top level of the GitHub repository, next to index.html" in text, text[:160])
        record("missing files: no endless 'Loading…' on " + path,
               page.locator(".loading").count() == 0 and "This content could not be loaded." in page.inner_text("main"))
    page.screenshot(path=str(SHOTS / "10-missing-files-message.png"))
    page.evaluate("() => localStorage.setItem('g12-lang', 'ar')")
    page.goto(base + "index.html")
    expect(page.locator("#load-failure")).to_be_visible()
    record("missing files: the message is in Arabic when Arabic was chosen",
           "المستوى الأعلى في مستودع GitHub" in page.locator("#load-failure").inner_text())
    context.close()

    # b) Only the stylesheet missing: message shown, content still works.
    context = browser.new_context()
    context.route("**/style.css", serve_json("Not found", status=404))
    page = context.new_page()
    page.goto(base + "summaries.html")
    expect(page.locator("#load-failure")).to_contain_text("style.css")
    expect(page.locator(".empty-state h2")).to_have_text("No summaries added yet")
    record("missing stylesheet only: message shown and page content still loads", True)
    context.close()

    # c) Data files missing: error state with heading, reason and Try again.
    context = browser.new_context()
    context.route(DATA_ROUTE, serve_json("Not found", status=404))
    page = watch(context.new_page())
    titles = {"summaries.html": "Grammar Summaries", "practice.html": "Grammar Practice",
              "reading.html": "Reading Comprehension", "vocabulary.html": "Vocabulary"}
    for path, title in titles.items():
        page.goto(base + path)
        expect(page.locator(".error-state h2")).to_have_text("This content could not be loaded")
        record("data missing: error state on " + path,
               page.locator("h1").inner_text() == title
               and "was not found (HTTP 404)" in page.locator(".error-state").inner_text()
               and page.locator(".error-state button:has-text('Try again')").count() == 1,
               page.locator(".error-state").inner_text().replace("\n", " | ")[:160])
        audit(page, "error state " + path)
    # The content manager keeps working (so a teacher can still reach the draft)
    # and shows the problem in its status bar instead.
    page.goto(base + "manage.html")
    expect(page.locator(".status-bar .notice--error")).to_contain_text("could not be loaded")
    record("data missing: content manager warns but stays usable",
           "was not found (HTTP 404)" in page.locator(".status-bar").inner_text()
           and page.locator(".manager-nav a").count() == 6)
    page.goto(base + "index.html")
    expect(page.locator("#home-status .error-state")).to_be_visible()
    record("data missing: home page shows the error and 'Could not load' counts",
           page.locator("[data-count='summaries']").inner_text() == "Could not load"
           and page.locator("[data-count='vocabulary']").inner_text() == "Could not load"
           and page.locator("#home-status a:has-text('Go to the home page')").count() == 0)
    page.screenshot(path=str(SHOTS / "11-error-state.png"))
    # Try again reloads and works once the files are back.
    page.goto(base + "summaries.html")
    expect(page.locator(".error-state")).to_be_visible()  # wait until the failed load is shown
    context.unroute(DATA_ROUTE)
    page.click("button:has-text('Try again')")
    expect(page.locator(".empty-state h2")).to_have_text("No summaries added yet")
    record("'Try again' reloads the page and recovers", True)
    page.errors.clear()  # the 404s above were intentional
    context.close()

    # d) Loading state, slow-network notice and timeout (fake clock, data never answers).
    context = browser.new_context()
    held = []
    context.route(DATA_ROUTE, lambda route: held.append(route))  # hold every data request (never answer)
    page = context.new_page()
    page.clock.install()
    page.goto(base + "summaries.html")
    loading = page.locator("#page-root .loading")
    expect(loading).to_have_text("Loading…")
    record("loading state shows a spinner",
           page.evaluate("getComputedStyle(document.querySelector('.loading'), '::before').animationName") == "g12-spin")
    page.clock.run_for(9000)
    expect(loading).to_contain_text("taking longer than usual")
    record("slow loading: 'taking longer than usual' notice after 8 seconds", True)
    page.clock.run_for(22000)
    expect(page.locator(".error-state")).to_contain_text("took too long")
    record("loading gives up after 30 seconds with an error and Try again", True)
    for route in held:  # answer the held requests so closing the browser is quiet
        route.abort()
    page.wait_for_timeout(200)
    context.close()


# ---------------------------------------------------------------- 7. navigation and mobile menu

def navigation(browser, base):
    labels = ["Home", "Grammar Summaries", "Grammar Practice", "Reading Comprehension", "Vocabulary"]
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = watch(context.new_page())
    page.goto(base + "index.html")
    links = page.locator("#site-nav a")
    record("navigation: Home, then the four English sections in order (Vocabulary fourth)", links.all_inner_texts() == labels, str(links.all_inner_texts()))
    record("desktop: menu button hidden, links visible",
           not page.is_visible(".nav-toggle") and page.is_visible("#site-nav"))
    for href, label in [("summaries.html", "Grammar Summaries"), ("practice.html", "Grammar Practice"),
                        ("reading.html", "Reading Comprehension"), ("vocabulary.html", "Vocabulary"), ("index.html", "Home")]:
        settle(page)
        page.click("#site-nav a:has-text('%s')" % label)
        expect(page).to_have_url(re.compile(re.escape(href) + "$"))
        current = page.locator("#site-nav a[aria-current='page']")
        record("nav link works and marks current page: " + label, current.inner_text() == label)
    page.screenshot(path=str(SHOTS / "12-home-desktop.png"), full_page=True)
    for width in [1024, 768]:
        page.set_viewport_size({"width": width, "height": 900})
        page.goto(base + "index.html")
        audit(page, "home at %dpx" % width)
    no_errors(page, "navigation desktop")

    page.set_viewport_size({"width": 375, "height": 800})
    page.goto(base + "index.html")
    toggle = page.locator(".nav-toggle")
    record("phone: menu button shown, links hidden until opened",
           toggle.is_visible() and not page.is_visible("#site-nav") and toggle.get_attribute("aria-expanded") == "false")
    brand = page.locator(".brand").bounding_box()
    button = toggle.bounding_box()
    record("phone: menu button sits beside the site name",
           abs((brand["y"] + brand["height"] / 2) - (button["y"] + button["height"] / 2)) < 25 and button["x"] >= brand["x"] + brand["width"])
    page.screenshot(path=str(SHOTS / "13-home-phone-closed.png"), full_page=True)
    toggle.click()
    record("phone: menu opens and reports aria-expanded=true",
           page.is_visible("#site-nav") and toggle.get_attribute("aria-expanded") == "true")
    audit(page, "phone menu open")
    page.screenshot(path=str(SHOTS / "14-home-phone-open.png"), full_page=False)
    page.keyboard.press("Tab")
    page.keyboard.press("Escape")
    record("phone: Escape closes the menu and returns focus to the button",
           not page.is_visible("#site-nav") and page.evaluate("document.activeElement.classList.contains('nav-toggle')"))
    settle(page)
    toggle.click()
    page.click("#site-nav a:has-text('Reading Comprehension')")
    expect(page).to_have_url(re.compile(r"reading\.html$"))
    record("phone: menu link navigates", True)
    no_errors(page, "navigation phone")
    context.close()

    # Without JavaScript the full navigation must stay visible.
    context = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 800})
    page = context.new_page()
    page.goto(base + "index.html")
    record("no JavaScript: navigation visible, menu button hidden",
           page.is_visible("#site-nav") and not page.is_visible(".nav-toggle") and page.locator("#site-nav a").count() == 5)
    page.goto(base + "vocabulary.html")
    record("no JavaScript: page explains that JavaScript is needed", "needs JavaScript" in page.inner_text("main"))
    context.close()


# ---------------------------------------------------------------- 8. Phase 2: units, topics, answer-all

def fixture_question(qid, **extra):
    question = {"id": qid, "type": "mcq", "prompt": "Test prompt " + qid, "options": ["Opt A", "Opt B", "Opt C"],
                "answer": "Opt B", "reviewStatus": "unreviewed"}
    question.update(extra)
    return question


# Placeholder test data only (served by the test, never written to the project's data files).
# Summaries and questions deliberately use the old version 1 field names.
PHASE2_DATA = {
    "units.json": {"schemaVersion": 2, "units": [
        {"id": "u1", "title": "Test unit one", "description": "Placeholder unit description"},
        {"id": "u2", "title": "Test unit two"}]},
    "grammar-lessons.json": {"schemaVersion": 2, "lessons": [
        {"id": "l1", "unitId": "u1", "title": "Test topic one", "reviewStatus": "unreviewed",
         "sections": [{"type": "text", "paragraphs": ["Line one\nLine two"]}]},
        {"id": "l2", "title": "Test topic without unit", "reviewStatus": "unreviewed", "sections": []}]},
    "grammar-summaries.json": {"schemaVersion": 1, "summaries": [
        {"id": "s1", "lessonId": "l1", "title": "Test summary", "reviewStatus": "unreviewed", "remember": ["Reminder"]}]},
    "grammar-questions.json": {"schemaVersion": 1, "questions": [
        fixture_question("q1", topic="l1"),
        fixture_question("q2", unitId="u1", reviewStatus="reviewed"),
        {"id": "q3", "type": "short", "prompt": "Short prompt", "modelAnswer": "Model text", "reviewStatus": "unreviewed", "unitId": "u1"},
        fixture_question("q4", answer="B"),
        fixture_question("q5")]},
    "reading-passages.json": {"schemaVersion": 2, "passages": [
        {"id": "p1", "unitId": "u1", "title": "Test passage", "reviewStatus": "unreviewed",
         "paragraphs": ["Para one line 1\nPara one line 2", "Para   two"],
         "questions": [fixture_question("rq1"),
                       {"id": "rq2", "type": "short", "prompt": "Reading short", "modelAnswer": "Model r", "reviewStatus": "unreviewed"},
                       fixture_question("rq3", answer="Opt C")]},
        {"id": "p2", "title": "Plain passage", "showParagraphNumbers": False, "reviewStatus": "unreviewed",
         "paragraphs": ["Only paragraph"], "questions": []}]},
    "vocabulary-questions.json": {"schemaVersion": 2, "units": [
        {"id": "vu1", "title": "Test vocabulary unit one", "questions": [
            fixture_question("v1", difficulty="medium", explanation="✓ Opt B: placeholder\n✗ Opt A: placeholder\n✗ Opt C: placeholder"),
            fixture_question("v2", difficulty="hard"),
            fixture_question("v3", difficulty="medium"),
            fixture_question("v4", answer="Not an option")]},
        {"id": "vu2", "title": "Test vocabulary unit two", "questions": [fixture_question("v5", difficulty="hard")]},
        {"id": "vu3", "title": "Test unit without questions", "questions": []}]},
}


def phase2_pages(browser, base):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    for name, body in PHASE2_DATA.items():
        context.route("**/" + name, serve_json(json.dumps(body)))
    page = watch(context.new_page())

    # Vocabulary: its own file and page, units with counts, levels and explained answers
    page.goto(base + "vocabulary.html")
    settle(page)
    expect(page.locator("main")).to_contain_text("1 item could not be shown")
    options = page.locator("#vocabulary-unit option").all_inner_texts()
    record("vocabulary: units listed with counts (a unit without questions is hidden)",
           options == ["All units (4)", "Test vocabulary unit one (3)", "Test vocabulary unit two (1)"], str(options))
    record("vocabulary: no easy questions, so Easy is disabled",
           page.is_disabled("#vocabulary-level-easy") and page.locator("label[for='vocabulary-level-medium']").inner_text() == "Medium (2)",
           page.locator("label[for='vocabulary-level-medium']").inner_text())
    audit(page, "vocabulary setup")
    page.goto(base + "vocabulary.html?unit=vu2")
    settle(page)
    record("vocabulary: ?unit= preselects the unit", page.input_value("#vocabulary-unit") == "vu2")
    main_text = page.inner_text("main")
    record("vocabulary: no 'not yet reviewed' warning on the page",
           "reviewed" not in main_text.lower() and "checked by a teacher" not in main_text and "suggestions" not in main_text, main_text[:200])
    page.select_option("#vocabulary-unit", "vu1")
    page.check("#vocabulary-count-all")
    page.click("button:has-text('Start practice')")
    expect(page.locator(".quiz-progress-text")).to_have_text("Question 1 of 3")
    expect(page.locator(".vocabulary-unit")).to_contain_text("Test vocabulary unit one")
    record("vocabulary: no review label next to the question",
           page.locator(".quiz .badge--reviewed, .quiz .badge--unreviewed").count() == 0
           and "reviewed" not in page.locator(".quiz").inner_text().lower())
    for _ in range(3):
        legend = page.locator(".question-legend").inner_text()
        answer_current(page, "Opt B")
        expect(page.locator(".feedback-title")).to_have_text("Correct!")
        record("vocabulary: answers shown as the answer key, with no 'not reviewed' note",
               page.locator(".feedback .review-note").count() == 0 and "suggested" not in page.locator(".feedback").inner_text().lower())
        if "v1" in legend:
            text = page.locator(".feedback .explanation-text").evaluate("e => e.textContent")
            spacing = page.locator(".feedback .explanation-text").evaluate("e => getComputedStyle(e).whiteSpace")
            record("vocabulary: the explanation keeps one line per choice", text.count("\n") == 2 and spacing == "pre-line", repr(text) + " " + spacing)
            audit(page, "vocabulary question")
        page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
    expect(page.locator(".score-number")).to_have_text("3 / 3")
    record("vocabulary: one-at-a-time practice and score work", True)
    page.click("text=← Change practice settings")
    page.check("#vocabulary-mode-all")
    page.click("button:has-text('Start practice')")
    expect(page.locator(".worksheet-q")).to_have_count(3)
    record("vocabulary: answer-all mode works", True)
    page.set_viewport_size({"width": 375, "height": 800})
    audit(page, "vocabulary answer-all at phone width")
    page.set_viewport_size({"width": 1280, "height": 900})

    # Summaries by unit and topic (old field name lessonId is upgraded)
    page.goto(base + "summaries.html?topic=l1")
    settle(page)
    expect(page.locator(".summary-card h2")).to_have_text("Test summary")
    record("summaries: ?topic= shows the topic's summary (old 'lessonId' field upgraded)", True)
    page.goto(base + "summaries.html?topic=l2")
    settle(page)
    expect(page.locator(".empty-state h2")).to_have_text("No summary for this topic yet")
    page.goto(base + "summaries.html?unit=u2")
    settle(page)
    expect(page.locator(".empty-state h3")).to_have_text("No summaries in this unit yet")
    page.goto(base + "summaries.html")
    settle(page)
    record("summaries: grouped by unit", page.locator("#unit-u1 a").inner_text() == "Test unit one"
           and "No summaries in this unit yet." in page.inner_text("main"))
    audit(page, "summaries by unit")

    # Practice: unit and topic selection, empty states, broken answer key skipped
    page.goto(base + "practice.html")
    settle(page)
    expect(page.locator("main")).to_contain_text("1 item could not be shown")
    options = page.locator("#practice-unit option").all_inner_texts()
    record("practice: units listed with counts and 'no questions yet'",
           options == ["All units (4)", "Test unit one (3)", "Test unit two (no questions yet)", "Questions without a unit (1)"], str(options))
    page.select_option("#practice-unit", "u2")
    expect(page.locator(".practice-empty")).to_contain_text("No practice questions for this unit yet.")
    record("practice: empty unit disables Start", page.is_disabled("button:has-text('Start practice')"))
    audit(page, "practice empty unit")
    page.goto(base + "practice.html?topic=l1")
    settle(page)
    record("practice: ?topic= preselects the topic and its unit",
           page.input_value("#practice-unit") == "u1" and page.input_value("#practice-topic") == "l1")

    # Answer-all mode: nothing answered can never score
    page.goto(base + "practice.html?unit=u1")
    settle(page)
    page.check("#practice-mode-all")
    page.click("button:has-text('Start practice')")
    expect(page.locator(".worksheet-q")).to_have_count(3)
    expect(page.locator(".answered-count")).to_have_text("Answered 0 of 3")
    page.click("button:has-text('Check my answers')")
    expect(page.locator(".worksheet-warning")).to_contain_text("You have not answered 3 questions: 1, 2, 3.")
    record("answer-all: unanswered questions are listed before checking", True)
    page.click("button:has-text('Check anyway')")
    expect(page.locator(".worksheet-score .score-number")).to_have_text("0 / 2")
    breakdown = page.locator(".score-breakdown").inner_text()
    record("answer-all: unanswered questions score nothing", "Not answered: 2" in breakdown, breakdown.replace("\n", " | "))
    record("answer-all: each unanswered question says 'Not answered'",
           page.locator(".feedback--warning .feedback-title:has-text('Not answered')").count() == 3)
    audit(page, "answer-all results")
    page.screenshot(path=str(SHOTS / "15-answer-all-unanswered.png"), full_page=True)
    page.click("button:has-text('Retry missed questions (2)')")
    expect(page.locator(".worksheet h2")).to_have_text("Missed questions (2)")
    for index in range(2):
        page.locator(".worksheet-q").nth(index).locator("label:has-text('Opt B')").click()
    expect(page.locator(".answered-count")).to_have_text("Answered 2 of 2")
    page.click("button:has-text('Check my answers')")
    expect(page.locator(".worksheet-score .score-number")).to_have_text("2 / 2")
    record("answer-all: retry missed, answer all, full score", True)

    # Reading: formatting kept, questions in stored order, both modes
    page.goto(base + "reading.html?passage=p1")
    settle(page)
    first = page.locator(".passage-paragraphs li").first
    record("reading: line breaks and spacing kept exactly",
           first.evaluate("li => getComputedStyle(li).whiteSpace") == "pre-wrap"
           and page.locator(".passage-paragraphs li").nth(1).evaluate("li => li.textContent") == "Para   two")
    prompts = page.locator(".worksheet-q .question-legend, .worksheet-q label.question-legend").all_inner_texts()
    record("reading: questions in the stored order", [p.split("\n")[-1] for p in prompts] == ["Test prompt rq1", "Reading short", "Test prompt rq3"], str(prompts))
    record("reading: passage stays in view on wide screens",
           page.locator("article.passage").evaluate("a => getComputedStyle(a).position") == "sticky")
    page.locator(".worksheet-q").nth(0).locator("label:has-text('Opt B')").click()
    page.locator(".worksheet-q").nth(2).locator("label:has-text('Opt A')").click()
    page.click("button:has-text('Check my answers')")
    page.click("button:has-text('Check anyway')")
    expect(page.locator(".worksheet-score .score-number")).to_have_text("1 / 2")
    record("reading: matched, different and unanswered are reported separately",
           "Matched: 1" in page.locator(".score-breakdown").inner_text() and "Different: 1" in page.locator(".score-breakdown").inner_text())
    audit(page, "reading answer-all")
    page.screenshot(path=str(SHOTS / "16-reading-answer-all.png"), full_page=True)
    page.click(".mode-switch button:has-text('One at a time')")
    expect(page.locator(".quiz-progress-text")).to_have_text("Question 1 of 3")
    expect(page.locator(".question-legend")).to_contain_text("Test prompt rq1")
    record("reading: one-at-a-time mode keeps the stored order", True)
    page.goto(base + "reading.html?passage=p2")
    settle(page)
    record("reading: paragraph numbers can be turned off",
           page.locator(".passage-paragraphs").count() == 0 and page.locator(".passage-text p").inner_text() == "Only paragraph")
    page.goto(base + "reading.html?unit=u2")
    settle(page)
    expect(page.locator(".empty-state h3")).to_have_text("No passages in this unit yet")
    page.goto(base + "reading.html")
    settle(page)
    audit(page, "reading by unit")
    no_errors(page, "phase 2 student pages")
    context.close()

    # Without units.json (a site uploaded before units existed) pages still work.
    context = browser.new_context()
    context.route("**/units.json", serve_json("Not found", status=404))
    page = watch(context.new_page())
    page.goto(base + "summaries.html")
    settle(page)
    expect(page.locator(".empty-state h2")).to_have_text("No summaries added yet")
    page.errors = [e for e in page.errors if "units.json" not in e]
    record("missing units.json is treated as 'no units'", page.locator(".error-state").count() == 0)
    context.close()


def phase2_manager(browser, base):
    context = browser.new_context(accept_downloads=True)
    page = watch(context.new_page())
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto(base + "manage.html#units")
    settle(page)
    expect(page.locator(".empty-state h3")).to_have_text("No units added yet")
    for title in ["Test unit A", "Test unit B"]:
        page.click("text=Add a unit >> nth=0")
        page.fill("#f-title", title)
        page.click("button:has-text('Save unit')")
        expect(page.locator(".manager-message")).to_contain_text("Unit “%s” saved." % title)
    record("manager: units added", page.locator(".manager-row").count() == 2)
    audit(page, "manager units list")

    page.click(".manager-nav >> text=Lessons")
    page.click("text=Add a lesson >> nth=0")
    page.fill("#f-title", "Test topic A")
    page.select_option("#f-unit", "test-unit-a")
    page.click("button:has-text('Add section')")
    page.fill("#sec-0-text", "Placeholder text.")
    page.click("button:has-text('Save lesson')")
    expect(page.locator(".manager-row-meta")).to_contain_text("Unit: Test unit A")

    page.click(".manager-nav >> text=Grammar questions")
    page.click("text=Add a question >> nth=0")
    page.select_option("#f-topic", "test-topic-a")
    record("manager: choosing a topic selects its unit", page.input_value("#f-unit") == "test-unit-a")
    page.select_option("#f-unit", "test-unit-b")
    page.fill("#f-prompt", "Linked prompt")
    page.fill("#f-option-0", "X")
    page.fill("#f-option-1", "Y")
    page.check("#f-correct-0")
    page.click("button:has-text('Save question')")
    expect(page.locator(".error-summary")).to_contain_text("is in the unit “Test unit A”")
    record("manager: a unit that disagrees with the topic is refused", page.get_attribute("#f-unit", "aria-invalid") == "true")
    audit(page, "question editor with unit and topic")
    page.select_option("#f-unit", "test-unit-a")
    page.click("button:has-text('Save question')")
    expect(page.locator(".manager-row")).to_have_count(1)
    page.click("text=Add a question >> nth=0")
    page.select_option("#f-topic", "")
    page.select_option("#f-unit", "test-unit-b")
    page.fill("#f-prompt", "Unit-only prompt")
    page.fill("#f-option-0", "X")
    page.fill("#f-option-1", "Y")
    page.check("#f-correct-1")
    page.click("button:has-text('Save question')")
    library = draft(page)
    q1, q2 = library["questions"]
    record("manager: questions store topicId, and unitId only when there is no topic",
           q1.get("topicId") == "test-topic-a" and "unitId" not in q1 and q2.get("unitId") == "test-unit-b" and "topicId" not in q2,
           json.dumps(library["questions"]))
    page.select_option("#filter-unit", "test-unit-b")
    expect(page.locator(".manager-row")).to_have_count(1)
    record("manager: questions can be filtered by unit", True)

    page.click(".manager-nav >> text=Reading passages")
    page.click("text=Add a passage >> nth=0")
    page.fill("#f-title", "Test passage A")
    page.select_option("#f-unit", "test-unit-a")
    page.fill("#f-text", "Line 1\nLine 2\n\nSecond paragraph")
    page.uncheck("#f-numbers")
    page.click("button:has-text('Save passage')")
    passage = draft(page)["passages"][0]
    record("manager: passage keeps line breaks, unit and paragraph-number setting",
           passage["paragraphs"] == ["Line 1\nLine 2", "Second paragraph"] and passage.get("unitId") == "test-unit-a"
           and passage.get("showParagraphNumbers") is False, json.dumps(passage))

    page.click(".manager-nav >> text=Units")
    meta = page.locator(".manager-row-meta").first.inner_text()
    record("manager: unit list shows what each unit contains", "1 lesson" in meta and "1 question" in meta and "1 passage" in meta, meta)
    page.click("[aria-label='Edit unit “Test unit A”']")
    page.fill("#f-id", "unit-a")
    page.click("button:has-text('Save changes')")
    library = draft(page)
    record("manager: renaming a unit ID updates its lessons and passages",
           library["lessons"][0]["unitId"] == "unit-a" and library["passages"][0]["unitId"] == "unit-a")
    page.click("[data-id='test-unit-b'][data-action='delete']")
    library = draft(page)
    record("manager: deleting a unit keeps its content and removes the link",
           len(library["units"]) == 1 and len(library["questions"]) == 2 and "unitId" not in library["questions"][1])

    page.click(".manager-nav >> text=Import & export")
    expect(page.locator("button:has-text('Download all five files')")).to_be_visible()
    with page.expect_download() as info:
        page.click("button:has-text('Download units.json')")
    record("manager: units.json can be downloaded", info.value.suggested_filename == "units.json")
    old_format = DOWNLOADS / "old-format-questions.json"
    old_format.write_text(json.dumps({"schemaVersion": 1, "questions": [fixture_question("q-900", topic="test-topic-a")]}))
    page.set_input_files("#import-files", str(old_format))
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator("#import-result")).to_contain_text("Import complete")
    imported = [q for q in draft(page)["questions"] if q["id"] == "q-900"][0]
    record("manager: importing a version 1 file upgrades its field names", imported.get("topicId") == "test-topic-a" and "topic" not in imported)
    letter = DOWNLOADS / "letter-answer.json"
    letter.write_text(json.dumps({"schemaVersion": 2, "questions": [fixture_question("q-901", answer="B")]}))
    page.set_input_files("#import-files", str(letter))
    page.click("#import-result >> xpath=.. >> button:has-text('Import')")
    expect(page.locator("#import-result")).to_contain_text("looks like an option letter")
    record("manager: an answer key written as a letter is rejected with a hint", True)
    no_errors(page, "phase 2 manager")
    context.close()


# ---------------------------------------------------------------- 10. Arabic / English interface

PAGES = ["index.html", "summaries.html", "practice.html", "reading.html", "vocabulary.html", "manage.html"]
NAV_HREFS = ["index.html", "summaries.html", "practice.html", "reading.html", "vocabulary.html"]
NAV_EN = ["Home", "Grammar Summaries", "Grammar Practice", "Reading Comprehension", "Vocabulary"]
NAV_AR = ["الرئيسية", "ملخصات القواعد", "تدريبات القواعد", "القراءة والفهم", "المفردات"]
ARABIC = re.compile(r"[؀-ۿ]")


def page_language(page):
    return page.evaluate("() => [document.documentElement.lang, document.documentElement.dir, localStorage.getItem('g12-lang')]")


def use_arabic(page, base):
    page.goto(base + "index.html")
    settle(page)  # let the page finish loading, so the next page.goto does not cancel its requests
    page.evaluate("() => localStorage.setItem('g12-lang', 'ar')")


def language_switch(browser, base):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = watch(context.new_page())

    # English is the default on every page, and every page offers Arabic.
    for path in PAGES:
        page.goto(base + path)
        settle(page)
        toggle = page.locator(".lang-toggle")
        lang, direction, saved = page_language(page)
        record("language button on %s (English page offers العربية)" % path,
               toggle.is_visible() and toggle.inner_text() == "العربية" and toggle.get_attribute("lang") == "ar"
               and lang == "en" and direction == "ltr" and saved is None, "%s %s %s" % (lang, direction, toggle.inner_text()))

    # Switch on the home page: immediately, without reloading the page.
    page.goto(base + "index.html")
    settle(page)
    page.evaluate("window.__samePage = true")
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'ar'")
    settle(page)
    record("switching to Arabic happens immediately, without reloading the page",
           page.evaluate("window.__samePage === true"))
    record("Arabic: the page content changes too, not only the button",
           page.locator(".empty-state h2").inner_text() == "لم يُضف أي محتوى بعد"
           and page.locator("[data-count='summaries']").inner_text() == "لا توجد ملخصات بعد"
           and page.locator(".card h2").first.inner_text() == "ملخصات القواعد"
           and page.locator(".card h2").nth(3).inner_text() == "المفردات"
           and page.locator(".site-footer p").first.inner_text().startswith("مصدر مجاني"),
           page.locator(".empty-state h2").inner_text())
    focused = page.evaluate("document.activeElement.classList.contains('lang-toggle')")
    record("keyboard focus stays on the language button after switching", focused)
    lang, direction, saved = page_language(page)
    links = page.locator("#site-nav a")
    record("switching to Arabic: lang=ar, dir=rtl and the choice is saved", (lang, direction, saved) == ("ar", "rtl", "ar"),
           "%s %s %s" % (lang, direction, saved))
    record("Arabic navigation labels, same links",
           links.all_inner_texts() == NAV_AR
           and links.evaluate_all("list => list.map(a => a.getAttribute('href'))") == NAV_HREFS, str(links.all_inner_texts()))
    record("Arabic: the button now offers English",
           page.locator(".lang-toggle").inner_text() == "English" and page.locator(".lang-toggle").get_attribute("lang") == "en")
    # The website name stays in English in both languages, so the home page's tab title is the name itself.
    record("Arabic: headings are translated; the tab title is the website name",
           page.title() == "Learn for Grade 12" and ARABIC.search(page.locator("h1").inner_text()) is not None, page.title())

    # Straight back to English on the same page, still without a reload.
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'en'")
    record("switching back to English immediately: English text, left-to-right, saved",
           page.evaluate("window.__samePage === true") and page_language(page) == ["en", "ltr", "en"]
           and page.locator("#site-nav a").all_inner_texts() == NAV_EN
           and page.locator("h1").inner_text() == "Free English practice for Grade 12"
           and page.locator(".empty-state h2").inner_text() == "No content added yet"
           and page.locator("[data-count='summaries']").inner_text() == "No summaries yet"
           and page.locator(".lang-toggle").inner_text() == "العربية" and page.title() == "Learn for Grade 12")
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'ar'")

    # The choice is remembered on every page and after reloading.
    for path in PAGES:
        page.goto(base + path)
        settle(page)
        lang, direction, saved = page_language(page)
        texts = page.locator("#site-nav a").all_inner_texts()
        record("Arabic remembered on " + path,
               (lang, direction) == ("ar", "rtl") and texts == NAV_AR and ARABIC.search(page.locator("h1").inner_text()) is not None,
               "%s %s %s" % (lang, direction, page.locator("h1").inner_text()))
        audit(page, "Arabic " + path)
        page.screenshot(path=str(SHOTS / ("20-ar-%s.png" % path.replace(".html", ""))), full_page=True)
    page.reload()
    settle(page)
    record("Arabic still chosen after a reload", page_language(page)[:2] == ["ar", "rtl"])
    no_errors(page, "Arabic pages (also: no text missing from the Arabic dictionary)")

    # Arabic on a phone: the language button and the menu both work.
    page.set_viewport_size({"width": 375, "height": 800})
    page.goto(base + "index.html")
    settle(page)
    toggle = page.locator(".nav-toggle")
    record("Arabic phone: menu button and language button visible, links hidden",
           toggle.is_visible() and page.locator(".lang-toggle").is_visible() and not page.is_visible("#site-nav"))
    toggle.click()
    record("Arabic phone: menu opens with Arabic links", page.is_visible("#site-nav") and page.locator("#site-nav a").first.inner_text() == "الرئيسية")
    audit(page, "Arabic phone menu open")
    page.screenshot(path=str(SHOTS / "21-ar-phone-menu.png"), full_page=False)
    page.set_viewport_size({"width": 1280, "height": 900})

    # Back to English.
    page.goto(base + "vocabulary.html")
    settle(page)
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'en'")
    settle(page)
    record("switching back to English", page_language(page) == ["en", "ltr", "en"]
           and page.locator("#site-nav a").all_inner_texts() == NAV_EN and page.url.endswith("vocabulary.html"))
    no_errors(page, "language switch back")
    context.close()

    # Storage blocked (for example, strict privacy settings): the site still works in English.
    context = browser.new_context()
    context.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } });")
    page = watch(context.new_page())
    page.goto(base + "summaries.html")
    settle(page)
    record("storage blocked: pages still load in English with the language button",
           page.locator(".empty-state h2").inner_text() == "No summaries added yet" and page.locator(".lang-toggle").is_visible())
    page.errors.clear()
    context.close()


def arabic_interface(browser, base):
    """Arabic interface with placeholder content: the content itself must stay exactly as written."""
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    for name, body in PHASE2_DATA.items():
        context.route("**/" + name, serve_json(json.dumps(body)))
    page = watch(context.new_page())
    dialogs = []

    def on_dialog(dialog):
        dialogs.append(dialog.message)
        if getattr(page, "dismiss_next", False):
            page.dismiss_next = False
            dialog.dismiss()
        else:
            dialog.accept()

    page.on("dialog", on_dialog)
    use_arabic(page, base)

    page.goto(base + "index.html")
    settle(page)
    counts = [page.inner_text("[data-count='%s']" % k) for k in ["summaries", "questions", "passages", "vocabulary"]]
    record("Arabic home: counted words use Arabic plural forms", counts == ["ملخص واحد", "4 أسئلة", "قطعتان", "4 أسئلة"], str(counts))

    page.goto(base + "vocabulary.html")
    settle(page)
    options = page.locator("#vocabulary-unit option").all_inner_texts()
    record("Arabic vocabulary setup: labels translated, unit titles unchanged and left-to-right",
           options == ["كل الوحدات (4)", "Test vocabulary unit one (3)", "Test vocabulary unit two (1)"]
           and page.locator("h1").inner_text() == "المفردات"
           and page.locator("label[for='vocabulary-unit']").inner_text() == "الوحدة"
           and page.locator("#vocabulary-unit").evaluate("s => getComputedStyle(s).direction") == "ltr", str(options))
    audit(page, "Arabic vocabulary setup")
    page.select_option("#vocabulary-unit", "vu2")
    page.click("button:has-text('ابدأ التدريب')")
    expect(page.locator(".question-legend")).to_contain_text("Test prompt v5")
    record("Arabic vocabulary: the unit title and the question stay exactly as written, left-to-right",
           "Test vocabulary unit two" in page.locator(".vocabulary-unit").inner_text()
           and page.locator(".question-form fieldset").evaluate("f => getComputedStyle(f).direction") == "ltr")
    audit(page, "Arabic vocabulary question")
    page.screenshot(path=str(SHOTS / "22-ar-vocabulary.png"), full_page=True)

    page.goto(base + "practice.html")
    settle(page)
    options = page.locator("#practice-unit option").all_inner_texts()
    record("Arabic practice setup: labels translated, unit titles unchanged",
           options == ["كل الوحدات (4)", "Test unit one (3)", "Test unit two (لا أسئلة بعد)", "أسئلة بلا وحدة (1)"]
           and page.locator("label[for='practice-unit']").inner_text() == "الوحدة", str(options))

    page.goto(base + "practice.html?topic=l1")
    settle(page)
    page.click("button:has-text('ابدأ التدريب')")
    expect(page.locator(".question-legend")).to_contain_text("Test prompt q1")
    record("Arabic practice: question and answer choices shown exactly as written",
           [label.split("\n")[-1] for label in page.locator(".options label").all_inner_texts()] == ["Opt A", "Opt B", "Opt C"]
           and page.locator(".quiz-progress-text").inner_text() == "السؤال 1 من 1")
    record("Arabic practice: the question box follows the question's own direction (English, left-to-right)",
           page.locator(".question-form fieldset").evaluate("f => getComputedStyle(f).direction") == "ltr"
           and page.locator(".quiz-progress-text").evaluate("p => getComputedStyle(p).direction") == "rtl")
    page.click(".options label:has-text('Opt A')")
    page.click("button.btn:has-text('أرسل الإجابة')")
    expect(page.locator(".feedback")).to_contain_text("إجابتك تختلف عن الإجابة المقترحة.")
    record("Arabic feedback, with the answer options left exactly as written",
           "Opt A" in page.locator(".options").inner_text() and "Not correct" not in page.locator(".feedback").inner_text())
    audit(page, "Arabic practice feedback")
    page.screenshot(path=str(SHOTS / "23-ar-practice-feedback.png"), full_page=True)

    # Practice already answered: the language button asks first (Cancel keeps everything).
    page.dismiss_next = True
    page.click(".lang-toggle")
    page.wait_for_timeout(200)
    record("practice in progress: switching asks first; Cancel keeps the answers and the language",
           page_language(page)[0] == "ar" and page.locator(".feedback-title").count() == 1
           and len(dialogs) == 1 and "تغيير اللغة" in dialogs[-1], " | ".join(dialogs))
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'en'")
    record("practice: after confirming, the same question starts again in English without reloading",
           page.locator(".quiz-progress-text").inner_text() == "Question 1 of 1"
           and page.locator(".feedback-title").count() == 0
           and "Test prompt q1" in page.locator(".question-legend").inner_text()
           and [label.split("\n")[-1] for label in page.locator(".options label").all_inner_texts()] == ["Opt A", "Opt B", "Opt C"]
           and page.locator("button:has-text('Submit answer')").count() == 1)
    page.click(".lang-toggle")  # nothing answered now: no question
    page.wait_for_function("document.documentElement.lang === 'ar'")
    record("practice: with no answers yet, switching does not ask", len(dialogs) == 2 and page.locator(".quiz-progress-text").inner_text() == "السؤال 1 من 1")
    page.click("button.btn--link:has-text('تغيير إعدادات التدريب')")
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'en'")
    record("practice settings screen switches language and keeps the chosen topic",
           page.locator("#setup-heading").inner_text() == "Choose your practice" and page.input_value("#practice-topic") == "l1"
           and page.locator("label[for='practice-mode-one']").inner_text().startswith("One at a time"))
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'ar'")

    page.goto(base + "reading.html?passage=p1")
    settle(page)
    record("Arabic reading page: passage text unchanged",
           page.locator(".passage-paragraphs li").nth(1).evaluate("li => li.textContent") == "Para   two"
           and page.locator(".answered-count").inner_text() == "أُجيب عن 0 من 3")
    page.click("button:has-text('صحّح إجاباتي')")
    expect(page.locator(".worksheet-warning")).to_contain_text("لم تُجب عن 3 أسئلة:")
    page.click("button:has-text('صحّح على أي حال')")
    expect(page.locator(".score-breakdown")).to_contain_text("لم تتم الإجابة: 2")
    record("Arabic answer-all: unanswered questions are reported in Arabic and get no marks",
           page.locator(".worksheet-score .score-number").inner_text() == "0 / 2")
    page.dismiss_next = True
    page.click(".lang-toggle")
    page.wait_for_timeout(200)
    record("reading results shown: switching asks first; Cancel keeps the results",
           page_language(page)[0] == "ar" and page.locator(".worksheet-score").count() == 1 and len(dialogs) == 3)
    audit(page, "Arabic reading results")
    page.screenshot(path=str(SHOTS / "24-ar-reading.png"), full_page=True)

    # Content manager in Arabic: validation messages translated, content untouched.
    page.goto(base + "manage.html#lessons")
    settle(page)
    record("Arabic manager: content titles are shown as written",
           page.locator(".manager-row-title").all_inner_texts() == ["Test topic one", "Test topic without unit"])
    page.click("[aria-label='تعديل الدرس «Test topic one»']")
    page.fill("#f-title", "")
    page.click("#manager-view button:has-text('حفظ التغييرات')")
    expect(page.locator(".error-summary")).to_contain_text("اكتب عنوانًا.")
    record("Arabic manager: form validation messages are in Arabic", page.get_attribute("#f-title", "aria-invalid") == "true")
    audit(page, "Arabic lesson editor with an error")
    page.screenshot(path=str(SHOTS / "25-ar-manager-error.png"), full_page=True)

    # Unsaved form: the language button asks first; after confirming, the manager redraws in English.
    page.evaluate("window.__samePage = true")
    page.dismiss_next = True
    page.click(".lang-toggle")
    page.wait_for_timeout(200)
    record("manager: unsaved form → asks before switching; Cancel keeps the form",
           page_language(page)[0] == "ar" and page.input_value("#f-title") == "" and "غير محفوظة" in dialogs[-1], dialogs[-1])
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'en'")
    expect(page.locator("#manager-view h2")).to_have_text("Edit lesson: Test topic one")
    record("manager redraws in English without reloading (same form, saved content unchanged)",
           page.evaluate("window.__samePage === true") and page.input_value("#f-title") == "Test topic one"
           and page.locator(".manager-nav a").first.inner_text() == "Units (2)"
           and page.locator("#f-sec-0-text, #sec-0-text").first.input_value() == "Line one\nLine two")
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'ar'")
    page.goto(base + "manage.html#questions/new")
    settle(page)
    page.fill("#f-prompt", "Placeholder prompt")
    page.fill("#f-option-0", "X")
    page.fill("#f-option-1", "X")
    page.click("#manager-view button:has-text('حفظ السؤال')")
    summary = page.locator(".error-summary").inner_text()
    record("Arabic manager: answer-key checks are in Arabic",
           "الاختيار B مطابق لاختيار آخر." in summary and "حدّد الاختيار الذي يمثّل الإجابة الصحيحة." in summary, summary.replace("\n", " | "))
    page.goto(base + "manage.html#tools")
    settle(page)
    letter = DOWNLOADS / "letter-answer-ar.json"
    letter.write_text(json.dumps({"schemaVersion": 2, "questions": [fixture_question("q-950", answer="B")]}))
    page.set_input_files("#import-files", str(letter))
    page.click("#import-result >> xpath=.. >> button[type='submit']")
    expect(page.locator("#import-result")).to_contain_text("لم يُستورد أي شيء")
    expect(page.locator("#import-result")).to_contain_text("تبدو حرف اختيار")
    record("Arabic manager: import errors are in Arabic", True)
    audit(page, "Arabic import & export")
    page.screenshot(path=str(SHOTS / "26-ar-manager-tools.png"), full_page=True)
    no_errors(page, "Arabic interface with content")
    context.close()


# ---------------------------------------------------------------- 9. colour contrast

def contrast():
    def luminance(hex_color):
        channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    def ratio(a, b):
        la, lb = sorted([luminance(a), luminance(b)], reverse=True)
        return (la + 0.05) / (lb + 0.05)

    css = (PROJECT / "style.css").read_text()
    var = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", css))
    pairs = [
        ("text", "bg"), ("text", "surface"), ("muted", "surface"), ("muted", "bg"), ("primary", "surface"),
        ("primary", "primary-light"), ("primary", "bg"), ("success", "success-bg"), ("danger", "danger-bg"),
        ("danger", "surface"), ("warning", "warning-bg"), ("info", "info-bg"),
        # main buttons and the current menu item: deep blue text on pastel
        ("button-text", "button"), ("button-text", "button-end"), ("button-text", "button-hover"),
    ]
    failures = []
    for fg, bg in pairs:
        r = ratio(var["color-" + fg], var["color-" + bg])
        if r < 4.5:
            failures.append("%s on %s = %.2f" % (fg, bg, r))
    record("colour contrast of text colour pairs is at least 4.5:1 (WCAG AA)", not failures, "; ".join(failures))


# ---------------------------------------------------------------- main

# ---------------------------------------------------------------- 11. Sources & References page

SOURCE_LINKS = [
    "https://elearnningcontent.blob.core.windows.net/elearnningcontent/2026/Secondry/Secondry3/Term1/StudentBook/English_language_Sec3.pdf",
    "https://shbabbek.com/show/284137",
    "https://app.minhaji.net/printlesson/13439",
    "https://app.minhaji.net/printlesson/13440",
    "https://app.minhaji.net/printlesson/13441",
]


def sources_page(browser, base):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = watch(context.new_page())
    # Every page links to it from the footer (the header navigation is unchanged).
    pages = sorted(p.name for p in PROJECT.glob("*.html"))
    missing = []
    for path in pages:
        page.goto(base + path)
        # Let each page finish loading its questions, so leaving it doesn't cancel a request.
        page.wait_for_load_state("networkidle")
        if page.locator(".site-footer a[href='sources.html']").count() != 1:
            missing.append(path)
    record("every page has the Sources & References link in its footer", not missing, ", ".join(missing))
    record("the header navigation does not list the sources page", page.locator("#site-nav a[href='sources.html']").count() == 0)
    no_errors(page, "every page (footer check)")
    page.goto(base + "index.html")
    settle(page)
    page.click(".site-footer a[href='sources.html']")
    expect(page).to_have_url(re.compile(r"sources\.html$"))
    expect(page.locator("h1")).to_have_text("Sources & References")
    links = page.locator("main a.source-name")
    hrefs = links.evaluate_all("list => list.map(a => a.href)")
    record("sources page lists exactly the five sources, each a link to its page", hrefs == SOURCE_LINKS, str(hrefs))
    record("source links open in a new tab safely",
           links.evaluate_all("list => list.every(a => a.target === '_blank' && a.rel.includes('noopener'))"))
    record("sources are grouped: English vocabulary, chemistry chapter 1, the rest of the content",
           page.locator(".sources-group h2").all_inner_texts() == ["English — Vocabulary", "Chemistry — Chapter 1", "The rest of the content"],
           str(page.locator(".sources-group h2").all_inner_texts()))
    record("sources page tab title", page.title() == "Sources & References — Learn for Grade 12", page.title())
    audit(page, "sources page")
    page.screenshot(path=str(SHOTS / "30-sources.png"), full_page=True)
    page.set_viewport_size({"width": 375, "height": 800})
    page.reload()
    audit(page, "sources page at phone width")
    page.screenshot(path=str(SHOTS / "31-sources-phone.png"), full_page=True)
    page.set_viewport_size({"width": 1280, "height": 900})
    # Arabic interface: headings translated, source names and addresses kept
    page.click(".lang-toggle")
    page.wait_for_function("document.documentElement.lang === 'ar'")
    record("Arabic sources page: interface translated, links unchanged",
           page.locator("h1").inner_text() == "المصادر والمراجع"
           and page.title() == "المصادر والمراجع — Learn for Grade 12"
           and links.evaluate_all("list => list.map(a => a.href)") == SOURCE_LINKS
           and "شبابيك" in page.locator("main").inner_text() and "منهاجي" in page.locator("main").inner_text(), page.locator("h1").inner_text())
    audit(page, "Arabic sources page")
    page.screenshot(path=str(SHOTS / "32-sources-ar.png"), full_page=True)
    page.click(".lang-toggle")
    no_errors(page, "sources page")
    context.close()


# ---------------------------------------------------------------- 12. No review-status labels next to questions

def no_review_labels(browser, base):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = watch(context.new_page())
    for subject, file in [("physics.html", "physics-questions.json"), ("chemistry.html", "chemistry-questions.json")]:
        data = json.loads((PROJECT / file).read_text(encoding="utf-8"))
        for chapter in data["chapters"]:
            for section in chapter["sections"]:
                page.goto(base + "%s?chapter=%s&section=%s" % (subject, chapter["id"], section["id"]))
                page.wait_for_selector(".quiz .question-legend")
                labels = page.locator(".quiz .badges").all_inner_texts()
                record("no review label next to questions: %s / %s" % (subject, section["id"]),
                       page.locator(".quiz .badge--reviewed, .quiz .badge--unreviewed").count() == 0
                       and not any("reviewed" in label.lower() or "مراجع" in label for label in labels), str(labels))
    no_errors(page, "question pages without review labels")
    context.close()


# ---------------------------------------------------------------- 13. Biology question bank

def biology_bank(browser, base):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = watch(context.new_page())
    page.goto(base + "biology.html")
    page.wait_for_selector(".subject-cards .card")
    chapters = page.locator(".subject-cards .card h2").all_inner_texts()
    counts = page.locator(".subject-cards .card .card-count").all_inner_texts()
    record("biology: chapter 1 has 100 questions, chapter 2 has 200 (100 multiple choice + 50 essay + 50 on pictures)",
           chapters == ["الفصل الأول: الدعامة والحركة في الكائنات الحية", "الفصل الثاني: التنسيق الهرموني في الكائنات الحية"]
           and counts == ["100 questions", "200 questions"], str(chapters) + str(counts))
    for chapter in ["chapter-1", "chapter-2"]:
        page.goto(base + "biology.html?chapter=" + chapter)
        page.wait_for_selector(".subject-cards .card")
        titles = page.locator(".subject-cards .card h3").all_inner_texts()
        counts = page.locator(".subject-cards .card .card-count").all_inner_texts()
        extra_titles = ["الأسئلة المقالية – 50 سؤالًا", "أسئلة على الصور – 50 سؤالًا"] if chapter == "chapter-2" else []
        extra_counts = ["50 questions", "50 questions"] if chapter == "chapter-2" else []
        record("biology %s: easy 10, medium 40, very hard 50%s" % (chapter, ", essay 50, pictures 50" if extra_titles else ""),
               titles == ["أسئلة سهلة", "أسئلة متوسطة", "أسئلة صعبة جدًا"] + extra_titles
               and counts == ["10 questions", "40 questions", "50 questions"] + extra_counts,
               str(titles) + str(counts))
        page.goto(base + "biology.html?chapter=%s&section=%s-very-hard" % (chapter, chapter))
        page.wait_for_selector(".quiz .question-legend")
        labels = page.locator(".quiz .badges").all_inner_texts()
        record("biology %s very hard: the question is labelled 'very hard', with no review label" % chapter,
               any("very hard" in label for label in labels) and page.locator(".quiz .badge--reviewed, .quiz .badge--unreviewed").count() == 0,
               str(labels))
        audit(page, "biology %s very-hard section" % chapter)
    page.set_viewport_size({"width": 375, "height": 800})
    page.goto(base + "biology.html?chapter=chapter-2&section=chapter-2-medium")
    page.wait_for_selector(".quiz .question-legend")
    audit(page, "biology section at phone width")
    page.screenshot(path=str(SHOTS / "40-biology-phone.png"), full_page=True)
    no_errors(page, "biology pages")
    context.close()


def question_pdfs(browser, base):
    """The four PDFs of questions with answers: a panel with "View PDF" and
    "Download PDF" where they belong, on a computer and on a phone."""
    # (page name, address, PDF, which panel on the page, how many panels the page has)
    pages = [("English home", "index.html", "english-questions.pdf", 0, 1),
             ("Chemistry", "chemistry.html", "chemistry-questions.pdf", 0, 1),
             ("Biology chapter 1", "biology.html?chapter=chapter-1", "biology-ch1-questions.pdf", 0, 1),
             ("Biology chapter 2", "biology.html?chapter=chapter-2", "biology-ch2-questions.pdf", 0, 2),
             ("Biology chapter 2 essay and picture questions", "biology.html?chapter=chapter-2", "biology-ch2-essay-image-questions.pdf", 1, 2),
             ("Physics chapter 2", "physics.html?chapter=chapter-2", "physics-ch2-question-bank.pdf", 0, 1)]
    for device, options in [("computer", {"viewport": {"width": 1280, "height": 900}}),
                            ("phone", {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 3, "is_mobile": True, "has_touch": True,
                                       "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"})]:
        context = browser.new_context(accept_downloads=True, **options)
        page = watch(context.new_page())
        for name, url, pdf, which, how_many in pages:
            page.goto(base + url)
            page.wait_for_selector(".questions-pdf")
            panels = page.locator(".questions-pdf")
            panel = panels.nth(which)
            view = panel.locator("a[target=_blank]")
            download_link = panel.locator("a[download]")
            record("%s (%s): %s with View PDF and Download PDF" % (name, device, "one PDF panel" if how_many == 1 else "PDF panel %d of %d" % (which + 1, how_many)),
                   panels.count() == how_many and view.inner_text() == "View PDF" and download_link.inner_text() == "Download PDF"
                   and view.get_attribute("href") == pdf and download_link.get_attribute("href") == pdf,
                   "%d panels" % panels.count())
            response = page.request.get(base + pdf)
            record("%s (%s): the PDF opens (200, application/pdf, a real PDF)" % (name, device),
                   response.status == 200 and response.headers.get("content-type", "").startswith("application/pdf")
                   and response.body()[:5] == b"%PDF-", "%s %s" % (response.status, response.headers.get("content-type")))
            # (headless Chromium has no PDF viewer, so the new tab hands the file over as a download;
            # a normal browser shows it)
            with context.expect_event("request", lambda request: request.url == base + pdf) as asked:
                with page.expect_popup() as popup:
                    view.click()
            opened = popup.value
            record("%s (%s): View PDF opens a new tab that loads the file" % (name, device),
                   asked.value.frame.page == opened, asked.value.url)
            opened.close()
            with page.expect_download() as info:
                download_link.click()
            saved = info.value
            size = pathlib.Path(saved.path()).stat().st_size
            record("%s (%s): Download PDF saves %s" % (name, device, pdf),
                   saved.suggested_filename == pdf and size == (PROJECT / pdf).stat().st_size, "%s %d bytes" % (saved.suggested_filename, size))
            audit(page, "%s page with the PDF panel (%s)" % (name, device))
        page.goto(base + "physics.html?chapter=chapter-1")
        page.wait_for_selector(".subject-cards .card")
        record("Physics (%s): unchanged, no answers PDF panel" % device, page.locator(".questions-pdf").count() == 0)
        if device == "phone":
            page.goto(base + "biology.html?chapter=chapter-1")
            page.wait_for_selector(".questions-pdf")
            page.screenshot(path=str(SHOTS / "41-biology-pdf-panel-phone.png"), full_page=True)
        no_errors(page, "pages with question PDFs (%s)" % device)
        context.close()


def biology_written(browser, base):
    """Biology Chapter 2: the 50 essay questions and the 50 questions on pictures.
    On a computer and on a phone every question is opened, shows exactly the text of
    biology-questions.json (the file the PDF is made from), takes a written answer
    and then shows its model answer; every picture loads, is sharp (at least 1200
    pixels wide) and fits the screen. The chapter page shows both PDF panels with
    the right numbers of questions."""
    data = json.loads((PROJECT / "biology-questions.json").read_text(encoding="utf-8"))
    chapter = data["chapters"][1]
    sections = chapter["sections"][3:]
    record("biology written: 50 essay and 50 picture questions",
           [s["id"] for s in sections] == ["chapter-2-essay", "chapter-2-images"] and [len(s["questions"]) for s in sections] == [50, 50])
    phone = {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 3, "is_mobile": True, "has_touch": True}
    for device, options in [("computer", {"viewport": {"width": 1280, "height": 900}}), ("phone", phone)]:
        context = browser.new_context(**options)
        page = watch(context.new_page())
        page.goto(base + "biology.html")
        page.evaluate("() => localStorage.setItem('g12-lang', 'en')")
        page.goto(base + "biology.html?chapter=chapter-2")
        page.wait_for_selector(".questions-pdf")
        titles = page.locator(".questions-pdf .summary-pdf-title").all_inner_texts()
        hints = page.locator(".questions-pdf .hint").all_inner_texts()
        record("biology written (%s): the chapter page has the multiple-choice PDF (100 questions) and the new PDF (100 questions)" % device,
               titles == [chapter["pdfTitle"], chapter["morePdfs"][0]["title"]]
               and all(h.startswith("100 questions") for h in hints) and len(hints) == 2, str(titles) + str(hints))
        for section in sections:
            page.goto(base + "biology.html?chapter=chapter-2&section=" + section["id"])
            page.wait_for_selector(".quiz .prompt-text")
            heading = page.locator(".question-section-title").inner_text().strip()
            problems = []
            for n, q in enumerate(section["questions"], 1):
                shown = page.locator(".prompt-text").first.evaluate("e => e.textContent")
                if shown != q["prompt"]:
                    problems.append("%d: text differs" % n)
                img = page.locator(".quiz .question-figure img")
                if "image" in q:
                    if img.count() != 1:
                        problems.append("%d: no picture" % n)
                    else:
                        img.scroll_into_view_if_needed()
                        page.wait_for_function("() => { const i = document.querySelector('.quiz .question-figure img'); return i && i.complete && i.naturalWidth > 0; }")
                        info = img.evaluate("i => ({src: i.getAttribute('src'), w: i.naturalWidth, shown: i.getBoundingClientRect().width, right: i.getBoundingClientRect().right, alt: i.alt})")
                        if info["src"] != q["image"] or info["w"] < 1200 or info["alt"] != q["imageAlt"]:
                            problems.append("%d: picture %s" % (n, info))
                        if info["right"] > page.viewport_size["width"] + 1 or info["shown"] < (300 if device == "phone" else 600):
                            problems.append("%d: picture %d px wide on screen" % (n, info["shown"]))
                elif img.count() != 0:
                    problems.append("%d: an essay question shows a picture" % n)
                page.fill(".quiz textarea", "إجابتي")
                page.click("button:has-text('Submit answer')")
                model = page.locator(".feedback p[dir=auto]").first.evaluate("e => e.textContent")
                if model != q["modelAnswer"]:
                    problems.append("%d: model answer differs" % n)
                page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
            record("biology written (%s): %s — all %d questions show their text%s and their model answer" % (
                   device, section["title"], len(section["questions"]), " and picture" if section["id"].endswith("images") else ""),
                   heading == section["title"] and not problems, "; ".join(problems[:5]))
        page.goto(base + "biology.html?chapter=chapter-2&section=chapter-2-images")
        page.wait_for_selector(".quiz .question-figure img")
        page.wait_for_function("() => document.querySelector('.quiz .question-figure img').complete")
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("biology written (%s): no sideways scrolling on a picture question" % device, overflow <= 0, "overflow %d" % overflow)
        audit(page, "biology picture question (%s)" % device)
        if device == "phone":
            page.screenshot(path=str(SHOTS / "45-biology-picture-question-phone.png"), full_page=True)
            page.goto(base + "biology.html?chapter=chapter-2&section=chapter-2-essay")
            page.wait_for_selector(".quiz textarea")
            page.fill(".quiz textarea", "إجابتي")
            page.click("button:has-text('Submit answer')")
            page.screenshot(path=str(SHOTS / "46-biology-essay-answer-phone.png"), full_page=True)
        no_errors(page, "biology written questions (%s)" % device)
        context.close()


def chemistry_ch2(browser, base):
    """Chemistry Chapter 2: the 100 multiple-choice questions and the 50 essay questions.
    The Chemistry page shows the new chapter and its own PDF stays Chapter 1 only; the
    chapter page shows its three sections and three PDF panels (each PDF opens). On a
    computer every multiple-choice question is answered correctly (marked correct, score
    50 / 50); on a phone every one is answered wrongly (marked incorrect, the key shown,
    score 0 / 50). Every question, choice, explanation and model answer on the screen is
    exactly the text in chemistry-questions.json, the file the three PDFs are made from."""
    data = json.loads((PROJECT / "chemistry-questions.json").read_text(encoding="utf-8"))
    chapter = data["chapters"][1]
    built = json.loads((PROJECT / "tools" / "chem_ch2_bank" / "built.json").read_text(encoding="utf-8"))["files"]
    record("chemistry chapter 2: 50 hard + 50 very hard multiple choice + 50 essay questions",
           [(s["id"], len(s["questions"])) for s in chapter["sections"]] == [("chapter-2-hard", 50), ("chapter-2-very-hard", 50), ("chapter-2-essay", 50)])
    phone = {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 3, "is_mobile": True, "has_touch": True}
    for device, options, right in [("computer", {"viewport": {"width": 1280, "height": 900}}, True), ("phone", phone, False)]:
        context = browser.new_context(**options)
        page = watch(context.new_page())
        page.goto(base + "chemistry.html")
        page.evaluate("() => localStorage.setItem('g12-lang', 'en')")
        page.goto(base + "chemistry.html")
        page.wait_for_selector(".subject-cards .card")
        names = [c.strip() for c in page.locator(".subject-cards .card h2").all_inner_texts()]
        counts = page.locator(".subject-cards .card .card-count").all_inner_texts()
        title = page.locator(".questions-pdf .summary-pdf-title").all_inner_texts()
        hint = page.locator(".questions-pdf .hint").all_inner_texts()
        record("chemistry (%s): the page shows both chapters (102 and 150 questions); its PDF panel is Chapter 1's (102 questions)" % device,
               names == ["الفصل الأول", chapter["title"]] and counts == ["102 questions", "150 questions"]
               and title == [data["pdfTitle"]] and len(hint) == 1 and hint[0].startswith("102 questions"), str(names) + str(counts) + str(title) + str(hint))
        page.goto(base + "chemistry.html?chapter=chapter-2")
        page.wait_for_selector(".questions-pdf")
        cards = [c.strip() for c in page.locator(".subject-cards .card h3").all_inner_texts()]
        panels = page.locator(".questions-pdf")
        titles = page.locator(".questions-pdf .summary-pdf-title").all_inner_texts()
        hints = page.locator(".questions-pdf .hint").all_inner_texts()
        hrefs = [(panels.nth(i).locator("a[target=_blank]").get_attribute("href"), panels.nth(i).locator("a[download]").get_attribute("href"))
                 for i in range(panels.count())]
        files = [p["file"] for p in chapter["morePdfs"]]
        record("chemistry chapter 2 (%s): three sections and three PDF panels (100, 50 and 150 questions) with View and Download" % device,
               cards == [s["title"] for s in chapter["sections"]] and titles == [p["title"] for p in chapter["morePdfs"]]
               and [h.split(" · ")[0] for h in hints] == ["100 questions", "50 questions", "150 questions"]
               and all(p["note"] in h for p, h in zip(chapter["morePdfs"], hints)) and hrefs == [(f, f) for f in files],
               str(cards) + str(titles) + str(hints) + str(hrefs))
        for f, b in zip(files, built):
            response = page.request.get(base + f)
            record("chemistry chapter 2 (%s): %s opens (200, application/pdf, %d pages, made from the questions on the site)" % (device, f, b["pages"]),
                   response.status == 200 and "application/pdf" in response.headers.get("content-type", "")
                   and response.body()[:5] == b"%PDF-" and b["pdf"] == f, "%d %s" % (response.status, response.headers.get("content-type")))
        for section in chapter["sections"][:2]:
            page.goto(base + "chemistry.html?chapter=chapter-2&section=" + section["id"])
            page.wait_for_selector(".quiz .prompt-text")
            heading = page.locator(".question-section-title").inner_text().strip()
            problems = []
            for n, q in enumerate(section["questions"], 1):
                shown = page.locator(".prompt-text").first.evaluate("e => e.textContent")
                choices = page.locator(".options .option-text").evaluate_all("els => els.map(e => e.textContent)")
                if shown != q["prompt"] or choices != q["options"]:
                    problems.append("%d: text differs" % n)
                key = q["options"].index(q["answer"])
                page.check(".options input[data-index='%d']" % (key if right else (key + 1) % 4))
                page.click("button:has-text('Submit answer')")
                verdict = page.locator(".feedback-title").inner_text().strip()
                if right and verdict != "Correct!":
                    problems.append("%d: right answer marked '%s'" % (n, verdict))
                if not right:
                    if verdict != "Not correct.":
                        problems.append("%d: wrong answer marked '%s'" % (n, verdict))
                    page.click("button:has-text('Show correct answer')")
                    shown_key = page.locator(".feedback-title").evaluate("e => e.textContent")
                    if not shown_key.startswith("Correct answer:") or q["answer"] not in shown_key:
                        problems.append("%d: the key is not shown" % n)
                explanation = page.locator(".feedback .explanation-text")
                if explanation.count() != 1 or explanation.evaluate("e => e.textContent") != q["explanation"]:
                    problems.append("%d: explanation differs" % n)
                page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
            page.wait_for_selector(".score-number")
            score = page.locator(".score-number").first.inner_text().strip()
            record("chemistry chapter 2 (%s): %s — all 50 questions, choices and explanations as in the PDFs; %s; score %s" % (
                   device, section["title"], "every right answer marked correct" if right else "every wrong answer marked incorrect with the key shown", score),
                   heading == section["title"] and not problems and score == ("50 / 50" if right else "0 / 50"), "; ".join(problems[:5]))
        essay = chapter["sections"][2]
        page.goto(base + "chemistry.html?chapter=chapter-2&section=" + essay["id"])
        page.wait_for_selector(".quiz .prompt-text")
        problems = []
        for n, q in enumerate(essay["questions"], 1):
            if page.locator(".prompt-text").first.evaluate("e => e.textContent") != q["prompt"]:
                problems.append("%d: text differs" % n)
            page.fill(".quiz textarea", "إجابتي")
            page.click("button:has-text('Submit answer')")
            if page.locator(".feedback p[dir=auto]").first.evaluate("e => e.textContent") != q["modelAnswer"]:
                problems.append("%d: model answer differs" % n)
            page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
        record("chemistry chapter 2 (%s): %s — all 50 questions take a written answer and show the model answer of the PDF" % (device, essay["title"]),
               not problems, "; ".join(problems[:5]))
        page.goto(base + "chemistry.html?chapter=chapter-2&section=chapter-2-very-hard")
        page.wait_for_selector(".quiz .prompt-text")
        page.check(".options input[data-index='0']")
        page.click("button:has-text('Submit answer')")
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("chemistry chapter 2 (%s): no sideways scrolling, question and explanation right to left" % device,
               overflow <= 0 and page.locator(".prompt-text").first.evaluate("e => getComputedStyle(e).direction") == "rtl"
               and page.locator(".feedback .explanation-text").evaluate("e => getComputedStyle(e).direction") == "rtl", "overflow %d" % overflow)
        audit(page, "chemistry chapter 2 question (%s)" % device)
        if device == "phone":
            page.screenshot(path=str(SHOTS / "47-chemistry-ch2-question-phone.png"), full_page=True)
            page.goto(base + "chemistry.html?chapter=chapter-2")
            page.wait_for_selector(".questions-pdf")
            page.screenshot(path=str(SHOTS / "48-chemistry-ch2-chapter-phone.png"), full_page=True)
        no_errors(page, "chemistry chapter 2 (%s)" % device)
        context.close()


def arabic_unit3(browser, base):
    """The Arabic page: Unit 3 with its questions PDF and summary PDF, each with
    a "view" link and a clearly labelled "download" link, on a computer and a phone."""
    files = [("arabic-unit3-questions.pdf", "عرض الأسئلة", "تحميل 100 سؤال على الوحدة الثالثة"),
             ("arabic-unit3-summary.pdf", "عرض الملخص", "تحميل ملخص الوحدة الثالثة")]
    for device, options in [("computer", {"viewport": {"width": 1280, "height": 900}}),
                            ("phone", {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 3, "is_mobile": True, "has_touch": True,
                                       "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"})]:
        context = browser.new_context(accept_downloads=True, **options)
        page = watch(context.new_page())
        page.goto(base + "arabic.html")
        page.wait_for_selector(".subject-cards .card")
        record("Arabic page (%s): Unit 2 and Unit 3 cards to solve the questions" % device,
               [c.strip() for c in page.locator(".subject-cards .card h2").all_inner_texts()] == ["الوحدة الثانية – اللغة العربية: الأبنية", "الوحدة الثالثة: النواسخ"]
               and page.locator(".subject-cards .card .btn").all_inner_texts() == ["حلّ أسئلة الوحدة"] * 2)
        record("Arabic page (%s): PDF files heading" % device, page.locator("#arabic-unit-files").inner_text() == "ملفات الوحدة الثالثة: النواسخ")
        record("Arabic page (%s): no 'no content' message any more" % device, page.locator(".empty-state").count() == 0)
        for pdf, view_text, download_text in files:
            view = page.locator(".arabic-unit a[target=_blank][href='%s']" % pdf)
            download_link = page.locator(".arabic-unit a[download][href='%s']" % pdf)
            record("Arabic page (%s): %s has a view and a download link" % (device, pdf),
                   view.count() == 1 and download_link.count() == 1 and view.inner_text() == view_text
                   and download_link.inner_text() == download_text, "%d / %d" % (view.count(), download_link.count()))
            response = page.request.get(base + pdf)
            record("Arabic page (%s): %s opens (200, application/pdf, a real PDF)" % (device, pdf),
                   response.status == 200 and response.headers.get("content-type", "").startswith("application/pdf")
                   and response.body()[:5] == b"%PDF-")
            with context.expect_event("request", lambda request: request.url == base + pdf) as asked:
                with page.expect_popup() as popup:
                    view.click()
            opened = popup.value
            record("Arabic page (%s): «%s» opens %s in a new tab" % (device, view_text, pdf), asked.value.frame.page == opened)
            opened.close()
            with page.expect_download() as info:
                download_link.click()
            saved = info.value
            size = pathlib.Path(saved.path()).stat().st_size
            record("Arabic page (%s): «%s» saves %s" % (device, download_text, pdf),
                   saved.suggested_filename == pdf and size == (PROJECT / pdf).stat().st_size, "%s %d bytes" % (saved.suggested_filename, size))
        for lang in ("en", "ar"):  # the Unit 3 content stays Arabic whatever the interface language
            page.evaluate("lang => localStorage.setItem('g12-lang', lang)", lang)
            page.reload()
            record("Arabic page (%s, %s interface): download labels unchanged" % (device, lang),
                   page.locator("section[aria-labelledby=arabic-unit-files] a[download]").all_inner_texts() == [f[2] for f in files])
            audit(page, "Arabic page with Unit 3 (%s, %s)" % (device, lang))
        if device == "phone":
            page.screenshot(path=str(SHOTS / "42-arabic-unit3-phone.png"), full_page=True)
        no_errors(page, "Arabic page with Unit 3 (%s)" % device)
        context.close()


def arabic_quiz(browser, base):
    """All 100 Arabic Unit 3 questions solved on the site: on a computer every
    question is answered correctly and must be marked correct; on a phone every
    question is answered wrongly first, must be marked incorrect, and "show the
    correct answer" must show the key. Each question's text and choices must be
    exactly those in arabic-questions.json (the file the PDF is made from)."""
    data = json.loads((PROJECT / "arabic-questions.json").read_text(encoding="utf-8"))
    chapter = next(c for c in data["chapters"] if c["id"] == "unit-3")
    total = sum(len(s["questions"]) for s in chapter["sections"])
    record("Arabic quiz: 100 questions in 5 sections", total == 100 and len(chapter["sections"]) == 5, str(total))
    phone = {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 3, "is_mobile": True, "has_touch": True}
    for device, options, right in [("computer", {"viewport": {"width": 1280, "height": 900}}, True), ("phone", phone, False)]:
        context = browser.new_context(**options)
        page = watch(context.new_page())
        page.goto(base + "arabic.html")
        page.evaluate("() => localStorage.setItem('g12-lang', 'en')")
        page.goto(base + "arabic.html?chapter=" + chapter["id"])
        cards = page.locator(".subject-cards .card")
        record("Arabic quiz (%s): the unit shows its five sections" % device,
               cards.count() == 5 and [c.strip() for c in page.locator(".subject-cards .card h3").all_inner_texts()] == [s["title"] for s in chapter["sections"]])
        for section in chapter["sections"]:
            page.goto(base + "arabic.html?chapter=%s&section=%s" % (chapter["id"], section["id"]))
            page.wait_for_selector(".quiz .prompt-text")
            problems = []
            for n, q in enumerate(section["questions"], 1):
                shown = page.locator(".prompt-text").first.evaluate("e => e.textContent")
                choices = page.locator(".options .option-text").evaluate_all("els => els.map(e => e.textContent)")
                if shown != q["prompt"] or choices != q["options"]:
                    problems.append("%d: text differs" % n)
                key = q["options"].index(q["answer"])
                pick = key if right else (key + 1) % 4
                page.check(".options input[data-index='%d']" % pick)
                page.click("button:has-text('Submit answer')")
                title = page.locator(".feedback-title").inner_text().strip()
                if right and title != "Correct!":
                    problems.append("%d: right answer marked '%s'" % (n, title))
                if not right:
                    if title != "Not correct.":
                        problems.append("%d: wrong answer marked '%s'" % (n, title))
                    page.click("button:has-text('Show correct answer')")
                    shown_key = page.locator(".feedback-title").inner_text().strip()
                    if shown_key != "Correct answer: " + q["answer"]:
                        problems.append("%d: shows '%s'" % (n, shown_key))
                if page.locator(".feedback .explanation-text").count() != 1:
                    problems.append("%d: no explanation" % n)
                page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
            record("Arabic quiz (%s): %s — all %d questions %s" % (device, section["title"], len(section["questions"]),
                   "marked correct when right" if right else "marked incorrect when wrong, and show the key"),
                   not problems, "; ".join(problems[:5]))
        page.goto(base + "arabic.html?chapter=%s&section=%s" % (chapter["id"], chapter["sections"][2]["id"]))
        page.wait_for_selector(".quiz .prompt-text")
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("Arabic quiz (%s): no sideways scrolling, text right to left" % device,
               overflow <= 0 and page.locator(".prompt-text").first.evaluate("e => getComputedStyle(e).direction") == "rtl", "overflow %d" % overflow)
        audit(page, "Arabic quiz (%s)" % device)
        if device == "phone":
            page.screenshot(path=str(SHOTS / "43-arabic-quiz-phone.png"), full_page=True)
        no_errors(page, "Arabic quiz (%s)" % device)
        context.close()


PHONE = {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 3, "is_mobile": True, "has_touch": True,
         "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}


def arabic_unit2_page(browser, base):
    """The Arabic page, on a computer and a phone: Unit 2 «الأبنية» first, its
    heading «الوحدة الثانية – اللغة العربية», and for each part (multiple choice,
    written) a button to solve it on the site, a "view" link and a "download" link
    to its PDF; the chapter page lists the two parts and the two PDFs."""
    data = json.loads((PROJECT / "arabic-questions.json").read_text(encoding="utf-8"))
    chapter = data["chapters"][0]
    record("Arabic Unit 2: the first unit, 50 multiple-choice and 50 written questions",
           chapter["id"] == "unit-2" and [len(s["questions"]) for s in chapter["sections"]] == [50, 50])
    parts = [("arabic-unit2-mcq.pdf", "تحميل أسئلة الاختيار من متعدد", chapter["sections"][0]),
             ("arabic-unit2-essay.pdf", "تحميل الأسئلة المقالية", chapter["sections"][1])]
    for device, options in [("computer", {"viewport": {"width": 1280, "height": 900}}), ("phone", PHONE)]:
        context = browser.new_context(accept_downloads=True, **options)
        page = watch(context.new_page())
        page.goto(base + "arabic.html")
        page.wait_for_selector(".subject-cards .card")
        unit = page.locator("section[aria-labelledby=arabic-unit2-files]")
        record("Arabic page (%s): Unit 2 heading, above Unit 3's files" % device,
               unit.locator("h2").inner_text() == "الوحدة الثانية – اللغة العربية" and unit.is_visible()
               and page.evaluate("() => document.querySelector('#arabic-unit2-files').compareDocumentPosition(document.querySelector('#arabic-unit-files')) & 4") != 0)
        for pdf, label, section in parts:
            panel = unit.locator(".summary-pdf:has(a[href='%s'])" % pdf)
            solve = panel.locator("a.btn:not(.btn--secondary)")
            view = panel.locator("a[target=_blank]")
            download_link = panel.locator("a[download]")
            record("Arabic page (%s): %s — solve, view and download buttons" % (device, pdf),
                   panel.count() == 1 and solve.inner_text() == "حلّ الأسئلة على الموقع" and view.inner_text() == "عرض ملف PDF"
                   and download_link.inner_text() == label and view.get_attribute("href") == pdf)
            response = page.request.get(base + pdf)
            record("Arabic page (%s): %s opens (200, application/pdf, a real PDF)" % (device, pdf),
                   response.status == 200 and response.headers.get("content-type", "").startswith("application/pdf") and response.body()[:5] == b"%PDF-")
            with context.expect_event("request", lambda request: request.url == base + pdf) as asked:
                with page.expect_popup() as popup:
                    view.click()
            record("Arabic page (%s): «عرض ملف PDF» opens %s in a new tab" % (device, pdf), asked.value.frame.page == popup.value)
            popup.value.close()
            with page.expect_download() as info:
                download_link.click()
            saved = info.value
            size = pathlib.Path(saved.path()).stat().st_size
            record("Arabic page (%s): «%s» saves %s" % (device, label, pdf),
                   saved.suggested_filename == pdf and size == (PROJECT / pdf).stat().st_size, "%s %d bytes" % (saved.suggested_filename, size))
            solve.click()
            page.wait_for_selector(".quiz .prompt-text")
            record("Arabic page (%s): «حلّ الأسئلة على الموقع» opens %s" % (device, section["title"]),
                   page.url.endswith("chapter=unit-2&section=" + section["id"]) and page.locator(".question-section-title").inner_text() == section["title"])
            page.goto(base + "arabic.html")
            page.wait_for_selector(".subject-cards .card")
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("Arabic page (%s): no sideways scrolling with Unit 2" % device, overflow <= 0, "overflow %d" % overflow)
        audit(page, "Arabic page with Unit 2 (%s)" % device)
        if device == "phone":
            unit.screenshot(path=str(SHOTS / "45-arabic-unit2-files-phone.png"))
        # the unit's own page: its two parts, then its two PDFs
        page.goto(base + "arabic.html?chapter=unit-2")
        page.wait_for_selector(".subject-cards .card")
        record("Arabic Unit 2 page (%s): the two parts and the two PDFs" % device,
               [c.strip() for c in page.locator(".subject-cards .card h3").all_inner_texts()] == [s["title"] for s in chapter["sections"]]
               and page.locator(".subject-content .questions-pdf a[download]").evaluate_all("els => els.map(e => e.getAttribute('href'))") == [p[0] for p in parts]
               and page.locator("section[aria-labelledby=arabic-unit2-files]").is_hidden())
        no_errors(page, "Arabic page with Unit 2 (%s)" % device)
        context.close()


def arabic_unit2_quiz(browser, base):
    """All 100 Unit 2 questions on the site. Multiple choice: on a computer every
    fifth question is answered wrongly and the others rightly — each marked so, with
    an explanation — and the results must say 40 / 50 (80%); on a phone every
    question is answered wrongly, shows the key, and the results say 0 / 50 (0%).
    Written: each has a writing box; on a computer the model answer is shown without
    writing, on a phone after writing an answer; the results do not score them. The
    texts must be exactly those in arabic-questions.json (the PDFs' source)."""
    data = json.loads((PROJECT / "arabic-questions.json").read_text(encoding="utf-8"))
    mcq, essay = data["chapters"][0]["sections"]
    for device, options, every in [("computer", {"viewport": {"width": 1280, "height": 900}}, 5), ("phone", PHONE, 1)]:
        context = browser.new_context(**options)
        page = watch(context.new_page())
        page.goto(base + "arabic.html")
        page.evaluate("() => localStorage.setItem('g12-lang', 'en')")
        page.goto(base + "arabic.html?chapter=unit-2&section=" + mcq["id"])
        page.wait_for_selector(".quiz .prompt-text")
        problems, right_count = [], 0
        for n, q in enumerate(mcq["questions"], 1):
            shown = page.locator(".prompt-text").first.evaluate("e => e.textContent")
            choices = page.locator(".options .option-text").evaluate_all("els => els.map(e => e.textContent)")
            if shown != q["prompt"] or choices != q["options"]:
                problems.append("%d: text differs" % n)
            key = q["options"].index(q["answer"])
            right = n % every != 0
            right_count += right
            page.check(".options input[data-index='%d']" % (key if right else (key + 1) % 4))
            page.click("button:has-text('Submit answer')")
            title = page.locator(".feedback-title").inner_text().strip()
            if title != ("Correct!" if right else "Not correct."):
                problems.append("%d: marked '%s'" % (n, title))
            if not right:
                page.click("button:has-text('Show correct answer')")
                if page.locator(".feedback-title").inner_text().strip() != "Correct answer: " + q["answer"]:
                    problems.append("%d: key not shown" % n)
            if page.locator(".feedback .explanation-text").evaluate_all("els => els.map(e => e.textContent)") != [q["explanation"]]:
                problems.append("%d: explanation" % n)
            page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
        record("Arabic Unit 2 multiple choice (%s): all 50 questions as in the file, marked right or wrong, explanation after each" % device,
               not problems, "; ".join(problems[:5]))
        page.wait_for_selector(".score-number")
        score = page.locator(".score-number").inner_text().strip()
        percent = round(100 * right_count / 50)
        record("Arabic Unit 2 multiple choice (%s): score %d / 50 and %d%%" % (device, right_count, percent),
               score == "%d / 50" % right_count and ("(%d%%)" % percent) in page.locator(".quiz").inner_text(), score)
        if device == "phone":
            page.screenshot(path=str(SHOTS / "46-arabic-unit2-results-phone.png"), full_page=True)
        # the written questions
        page.goto(base + "arabic.html?chapter=unit-2&section=" + essay["id"])
        page.wait_for_selector(".quiz .prompt-text")
        problems = []
        for n, q in enumerate(essay["questions"], 1):
            if page.locator(".prompt-text").first.evaluate("e => e.textContent") != q["prompt"]:
                problems.append("%d: text differs" % n)
            box = page.locator(".quiz textarea")
            if box.count() != 1 or box.get_attribute("rows") != "9" or not box.is_visible():
                problems.append("%d: no writing box" % n)
            if device == "computer":
                page.click("button:has-text('Show the model answer')")
            else:
                box.fill("إجابتي: اسم مقصور")
                page.click("button:has-text('Submit answer')")
            shown = page.locator(".feedback p").evaluate_all("els => els.map(e => e.textContent)")
            if q["modelAnswer"] not in shown:
                problems.append("%d: model answer not shown" % n)
            if n == 1 and device == "phone":
                page.screenshot(path=str(SHOTS / "47-arabic-unit2-written-phone.png"), full_page=True)
            page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
        record("Arabic Unit 2 written (%s): all 50 questions as in the file, a writing box, the model answer %s" % (
            device, "shown on request without writing" if device == "computer" else "shown after writing an answer"), not problems, "; ".join(problems[:5]))
        record("Arabic Unit 2 written (%s): the results do not score written answers" % device,
               "50 written answers are not scored" in page.locator(".quiz").inner_text())
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("Arabic Unit 2 (%s): no sideways scrolling" % device, overflow <= 0, "overflow %d" % overflow)
        audit(page, "Arabic Unit 2 results (%s)" % device)
        no_errors(page, "Arabic Unit 2 questions (%s)" % device)
        context.close()


def physics_ch2(browser, base):
    """Physics Chapter 2 on a computer and a phone. The chapter page shows its 8 lessons
    (number, «الدرس …» and the lesson's name, a button for its MCQs and one for its
    essays, with their counts), the random-exam card and ONE PDF panel. Every one of the
    150 MCQs is answered (on a computer every fourth one wrongly, on a phone all
    wrongly): the text, choices, diagram and explanation are exactly those in
    physics-questions.json (the PDF's source), each answer is marked right or wrong, and
    each lesson ends with its score. Every one of the 50 essays has a writing box and
    its model answer (shown on request on a computer, after writing on a phone). The
    exam: Hard with 10 questions (hard and very hard only, no repeats, score and a review
    of the 10 answers with explanations), a new exam with the same settings, Easy with
    more questions than there are (a notice, then all of them), and Mixed with 20."""
    data = json.loads((PROJECT / "physics-questions.json").read_text(encoding="utf-8"))
    chapter = data["chapters"][1]
    sections = {s["id"]: s for s in chapter["sections"]}
    by_text = {}
    for s in chapter["sections"]:
        for q in s["questions"]:
            by_text[(q["prompt"], tuple(q.get("options") or []))] = q
    mcq_all = [q for s in chapter["sections"] for q in s["questions"] if q["type"] == "mcq"]
    for device, options, every in [("computer", {"viewport": {"width": 1280, "height": 900}}, 4), ("phone", PHONE, 1)]:
        context = browser.new_context(**options)
        page = watch(context.new_page())
        page.goto(base + "physics.html")
        page.evaluate("() => localStorage.setItem('g12-lang', 'en')")
        page.goto(base + "physics.html")
        page.wait_for_selector(".subject-cards .card")
        names = [c.strip() for c in page.locator(".subject-cards .card h2").all_inner_texts()]
        counts = page.locator(".subject-cards .card .card-count").all_inner_texts()
        record("physics (%s): both chapters (118 and 200 questions)" % device,
               names == ["الفصل الأول", chapter["title"]] and counts == ["118 questions", "200 questions"], str(names) + str(counts))
        page.goto(base + "physics.html?chapter=chapter-2")
        page.wait_for_selector(".lesson-card")
        cards = page.locator(".lesson-card")
        problems = []
        for i, lesson in enumerate(chapter["lessons"]):
            card = cards.nth(i)
            number = card.locator(".lesson-number").inner_text().strip()
            kicker = card.locator(".lesson-kicker").inner_text().strip()
            title = card.locator(".lesson-title").inner_text().strip()
            buttons = card.locator("a.btn")
            hrefs = buttons.evaluate_all("els => els.map(e => e.getAttribute('href'))")
            texts = [b.strip() for b in buttons.all_inner_texts()]
            want = ["%s (%d)" % (sections[sid]["label"], len(sections[sid]["questions"])) for sid in lesson["sections"]]
            if (number, kicker, title) != (str(i + 1), lesson["number"], lesson["title"]) or texts != want \
                    or hrefs != ["physics.html?chapter=chapter-2&section=" + sid for sid in lesson["sections"]]:
                problems.append("%d: %s %s %s %s %s" % (i + 1, number, kicker, title, texts, hrefs))
        exam_card = page.locator(".subject-cards .card:not(.lesson-card)")
        panels = page.locator(".questions-pdf")
        record("physics chapter 2 (%s): 8 lesson cards (number, «الدرس …», name, MCQ and essay buttons with counts)" % device,
               cards.count() == 8 and not problems, "; ".join(problems[:4]))
        record("physics chapter 2 (%s): the random-exam card (150 questions to choose from)" % device,
               exam_card.count() == 1 and exam_card.locator("h3").inner_text().strip() == chapter["exam"]["title"]
               and exam_card.locator(".card-count").inner_text().strip() == "150 questions to choose from"
               and exam_card.locator("a.btn").get_attribute("href") == "physics.html?chapter=chapter-2&exam=1")
        record("physics chapter 2 (%s): ONE PDF panel — 200 questions, View and Download %s" % (device, chapter["pdf"]),
               panels.count() == 1 and panels.locator(".summary-pdf-title").inner_text() == chapter["pdfTitle"]
               and panels.locator(".hint").inner_text().startswith("200 questions")
               and panels.locator("a[target=_blank]").get_attribute("href") == chapter["pdf"]
               and panels.locator("a[download]").get_attribute("href") == chapter["pdf"])
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("physics chapter 2 (%s): no sideways scrolling on the chapter page" % device, overflow <= 0, "overflow %d" % overflow)
        audit(page, "physics chapter 2 page (%s)" % device)
        if device == "phone":
            page.screenshot(path=str(SHOTS / "49-physics-ch2-lessons-phone.png"), full_page=True)
        # the 8 lessons: MCQs, then essays
        right_total = 0
        for n, lesson in enumerate(chapter["lessons"], 1):
            mcq, essay = sections[lesson["sections"][0]], sections[lesson["sections"][1]]
            page.goto(base + "physics.html?chapter=chapter-2&section=" + mcq["id"])
            page.wait_for_selector(".quiz .prompt-text")
            banner_ok = (page.locator(".lesson-banner .lesson-number").inner_text().strip() == str(n)
                         and page.locator(".lesson-banner .lesson-title").inner_text().strip() == lesson["title"]
                         and page.locator(".question-section-title").inner_text().strip() == mcq["label"])
            problems, right_count = [], 0
            for k, q in enumerate(mcq["questions"], 1):
                shown = page.locator(".prompt-text").first.evaluate("e => e.textContent")
                choices = page.locator(".options .option-text").evaluate_all("els => els.map(e => e.textContent)")
                if shown != q["prompt"] or choices != q["options"]:
                    problems.append("%d: text differs" % k)
                image = page.locator(".quiz figure img")
                if (image.count() == 1) != bool(q.get("image")) or (q.get("image") and image.get_attribute("src") != q["image"]):
                    problems.append("%d: diagram" % k)
                key = q["options"].index(q["answer"])
                right = k % every != 0
                right_count += right
                page.check(".options input[data-index='%d']" % (key if right else (key + 1) % 4))
                page.click("button:has-text('Submit answer')")
                verdict = page.locator(".feedback-title").inner_text().strip()
                if verdict != ("Correct!" if right else "Not correct."):
                    problems.append("%d: marked '%s'" % (k, verdict))
                if not right:
                    page.click("button:has-text('Show correct answer')")
                    if page.locator(".feedback-title").evaluate("e => e.textContent") != "Correct answer: " + q["answer"]:
                        problems.append("%d: key not shown" % k)
                if page.locator(".feedback .explanation-text").evaluate_all("els => els.map(e => e.textContent)") != [q["explanation"]]:
                    problems.append("%d: explanation" % k)
                page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
            page.wait_for_selector(".score-number")
            score = page.locator(".score-number").inner_text().strip()
            right_total += right_count
            record("physics chapter 2 (%s): lesson %d MCQs — %d questions as in the file and the PDF, marked right/wrong with explanations, score %s" % (
                   device, n, len(mcq["questions"]), score),
                   banner_ok and not problems and score == "%d / %d" % (right_count, len(mcq["questions"])), "; ".join(problems[:5]))
            page.goto(base + "physics.html?chapter=chapter-2&section=" + essay["id"])
            page.wait_for_selector(".quiz .prompt-text")
            problems = []
            for k, q in enumerate(essay["questions"], 1):
                if page.locator(".prompt-text").first.evaluate("e => e.textContent") != q["prompt"]:
                    problems.append("%d: text differs" % k)
                box = page.locator(".quiz textarea")
                if box.count() != 1 or box.get_attribute("rows") != "9" or not box.is_visible():
                    problems.append("%d: no writing box" % k)
                if device == "computer":
                    page.click("button:has-text('Show the model answer')")
                else:
                    box.fill("إجابتي")
                    page.click("button:has-text('Submit answer')")
                if q["modelAnswer"] not in page.locator(".feedback p").evaluate_all("els => els.map(e => e.textContent)"):
                    problems.append("%d: model answer not shown" % k)
                page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
            page.wait_for_selector(".review-list")
            record("physics chapter 2 (%s): lesson %d essays — %d questions as in the file, writing box, model answer %s" % (
                   device, n, len(essay["questions"]), "on request" if device == "computer" else "after writing"),
                   not problems and page.locator(".lesson-banner .lesson-title").inner_text().strip() == lesson["title"], "; ".join(problems[:5]))
        expected = sum(len(sections[l["sections"][0]]["questions"]) - len(sections[l["sections"][0]]["questions"]) // every for l in chapter["lessons"])
        record("physics chapter 2 (%s): all 150 MCQs answered (%d right)" % (device, right_total), right_total == expected, str(right_total))
        if device == "phone":
            page.screenshot(path=str(SHOTS / "50-physics-ch2-essay-results-phone.png"), full_page=True)

        # the random exam
        def solve_exam(level_label, count_choice=None, custom=None, wrong_every=0):
            page.goto(base + "physics.html?chapter=chapter-2&exam=1")
            page.wait_for_selector(".exam-form")
            page.check("#chapter-exam-level-" + level_label)
            if custom is not None:
                page.check("#chapter-exam-count-custom")
                page.fill("#chapter-exam-count-number", str(custom))
            else:
                page.check("#chapter-exam-count-" + str(count_choice))
            page.click(".exam-form button[type=submit]")
            page.wait_for_selector(".quiz .prompt-text")
            return run_exam(wrong_every)

        def run_exam(wrong_every=0):
            seen, problems, right = [], [], 0
            total = int(page.locator(".quiz .quiz-progress-text").first.inner_text().split(" of ")[-1].split()[0])
            for k in range(1, total + 1):
                shown = page.locator(".prompt-text").first.evaluate("e => e.textContent")
                choices = page.locator(".options .option-text").evaluate_all("els => els.map(e => e.textContent)")
                q = by_text.get((shown, tuple(choices)))
                if not q or q["type"] != "mcq":
                    problems.append("%d: not one of the chapter's MCQs" % k)
                    break
                seen.append(q)
                key = q["options"].index(q["answer"])
                ok = not (wrong_every and k % wrong_every == 0)
                right += ok
                page.check(".options input[data-index='%d']" % (key if ok else (key + 1) % 4))
                page.click("button:has-text('Submit answer')")
                if not ok:
                    page.click("button:has-text('Show correct answer')")
                if page.locator(".feedback .explanation-text").evaluate_all("els => els.map(e => e.textContent)") != [q["explanation"]]:
                    problems.append("%d: explanation" % k)
                page.click(".actions button:has-text('Next question'), .actions button:has-text('See results')")
            page.wait_for_selector(".score-number")
            return seen, problems, right, page.locator(".score-number").inner_text().strip()

        seen, problems, right, score = solve_exam("hard", 10, wrong_every=5)
        review = page.locator(".review-list > li")
        explained = page.locator(".review-list .explanation-text").count()
        record("physics exam (%s): Hard, 10 questions — only hard and very hard, no repeats, score %s, review of the 10 answers with explanations" % (device, score),
               len(seen) == 10 and len({q["id"] for q in seen}) == 10 and all(q["difficulty"] in ("hard", "very-hard") for q in seen)
               and not problems and score == "8 / 10" and review.count() == 10 and explained == 10,
               "%s %s %s review %d explained %d" % ([q["difficulty"] for q in seen], problems[:3], score, review.count(), explained))
        first = {q["id"] for q in seen}
        page.click("button:has-text('New exam with the same settings')")
        page.wait_for_selector(".quiz .prompt-text")
        seen2, problems, right, score = run_exam()
        record("physics exam (%s): «New exam with the same settings» — 10 new hard questions, score %s" % (device, score),
               len(seen2) == 10 and len({q["id"] for q in seen2}) == 10 and all(q["difficulty"] in ("hard", "very-hard") for q in seen2)
               and {q["id"] for q in seen2} != first and score == "10 / 10" and not problems)
        page.click("button:has-text('Change exam settings')")
        page.wait_for_selector(".exam-form")
        record("physics exam (%s): «Change exam settings» returns to the settings, Hard still chosen" % device,
               page.locator("#chapter-exam-level-hard").is_checked())
        easy = sum(1 for q in mcq_all if q["difficulty"] == "easy")
        seen, problems, right, score = solve_exam("easy", custom=40)
        notice = page.locator(".exam-notice")
        record("physics exam (%s): Easy with 40 asked — a notice, then all %d easy questions once" % (device, easy),
               notice.count() == 1 and len(seen) == easy and len({q["id"] for q in seen}) == easy
               and all(q["difficulty"] == "easy" for q in seen) and score == "%d / %d" % (easy, easy) and not problems)
        seen, problems, right, score = solve_exam("mixed", 20)
        levels = {q["difficulty"] for q in seen}
        record("physics exam (%s): Mixed, 20 questions from the four levels and several lessons, no repeats" % device,
               len(seen) == 20 and len({q["id"] for q in seen}) == 20 and levels == {"easy", "medium", "hard", "very-hard"}
               and len({q["id"].split("-")[2] for q in seen}) >= 4 and score == "20 / 20" and not problems, str(sorted(levels)))
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        record("physics exam (%s): no sideways scrolling" % device, overflow <= 0, "overflow %d" % overflow)
        audit(page, "physics exam results (%s)" % device)
        if device == "phone":
            page.screenshot(path=str(SHOTS / "51-physics-ch2-exam-results-phone.png"), full_page=True)
        # the exam page in the Arabic interface
        page.evaluate("() => localStorage.setItem('g12-lang', 'ar')")
        page.goto(base + "physics.html?chapter=chapter-2&exam=1")
        page.wait_for_selector(".exam-form")
        record("physics exam (%s): Arabic interface — levels with their counts and «ابدأ الامتحان»" % device,
               page.locator(".exam-form button[type=submit]").inner_text().strip() == "ابدأ الامتحان"
               and "صعب (%d)" % sum(1 for q in mcq_all if q["difficulty"] in ("hard", "very-hard")) in page.locator(".level-choice").inner_text()
               and "سهل (%d)" % easy in page.locator(".level-choice").inner_text() and "مختلط (150)" in page.locator(".level-choice").inner_text(),
               page.locator(".level-choice").inner_text())
        if device == "phone":
            page.screenshot(path=str(SHOTS / "52-physics-ch2-exam-form-ar-phone.png"), full_page=True)
        no_errors(page, "physics chapter 2 (%s)" % device)
        context.close()


def dhikr(browser, base):
    """The dhikr card: on every page a dhikr from the list appears when the page
    opens, stays about 3.5 seconds, then disappears; a refresh shows a different
    one; it lets clicks through and fits a phone screen."""
    pages = sorted(p.name for p in PROJECT.glob("*.html"))
    phone = {"viewport": {"width": 390, "height": 664}, "device_scale_factor": 2, "is_mobile": True, "has_touch": True}
    for device, options, which in [("computer", {"viewport": {"width": 1280, "height": 900}}, pages),
                                   ("phone", phone, ["index.html", "arabic.html?chapter=unit-3&section=unit-3-kana", "biology.html", "practice.html"])]:
        context = browser.new_context(**options)
        page = watch(context.new_page())
        for path in which:
            page.goto(base + path)
            page.wait_for_selector(".dhikr.is-shown", timeout=3000)
            shown_at = time.monotonic()
            card = page.evaluate("""() => { const c = document.querySelector('.dhikr'); const r = c.getBoundingClientRect();
                return { text: c.querySelector('.dhikr-text').textContent, source: c.querySelector('.dhikr-source').textContent,
                         listed: window.G12Dhikr.items.some(i => i.text === c.querySelector('.dhikr-text').textContent),
                         lang: c.lang, dir: c.dir, pointer: getComputedStyle(c).pointerEvents,
                         through: document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2) !== c && !c.contains(document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)),
                         inside: r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight,
                         overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth }; }""")
            if device == "phone" and path.startswith("arabic"):
                page.screenshot(path=str(SHOTS / "44-dhikr-phone.png"))
            page.wait_for_selector(".dhikr", state="detached", timeout=6000)
            visible = time.monotonic() - shown_at
            record("dhikr (%s, %s): a listed dhikr in Arabic, clicks pass through, on screen" % (device, path),
                   card["listed"] and card["source"] and card["lang"] == "ar" and card["dir"] == "rtl" and card["pointer"] == "none"
                   and card["through"] and card["inside"] and card["overflow"] <= 0, json.dumps(card, ensure_ascii=False))
            record("dhikr (%s, %s): disappears by itself after about 3–4 seconds" % (device, path), 3.0 <= visible <= 4.5, "%.2f s" % visible)
        no_errors(page, "dhikr (%s)" % device)
        context.close()
    # refreshing shows a different dhikr each time
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = watch(context.new_page())
    texts = []
    for _ in range(6):
        page.goto(base + "index.html") if not texts else page.reload()
        page.wait_for_selector(".dhikr")
        texts.append(page.locator(".dhikr-text").inner_text())
    record("dhikr: each refresh shows a different dhikr", all(a != b for a, b in zip(texts, texts[1:])), " | ".join(texts))
    context.close()


def main():
    real_data = {name: (PROJECT / name).read_bytes() for name, _ in DATA_FILES}
    server, base = start_server()
    print("Serving the site from a subfolder: " + base)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        run_section("empty site", empty_site, browser, base)
        context = browser.new_context(accept_downloads=True)
        page = None
        try:
            page = manager_flow(context, base)
        except Exception as error:  # noqa: BLE001
            record("content manager (section stopped)", False, "%s\n%s" % (error, traceback.format_exc(limit=3)))
        files = backup = None
        if page:
            run_section("student pages in preview", student_pages_in_preview, page, base)
            try:
                files, backup = export_files(page, base)
            except Exception as error:  # noqa: BLE001
                record("export (section stopped)", False, "%s\n%s" % (error, traceback.format_exc(limit=3)))
        context.close()
        if files:
            run_section("published site", published_site, browser, base, files)
            run_section("import", import_flow, browser, base, backup)
        run_section("missing files and states", missing_files_and_states, browser, base)
        run_section("navigation", navigation, browser, base)
        run_section("phase 2 student pages", phase2_pages, browser, base)
        run_section("phase 2 content manager", phase2_manager, browser, base)
        run_section("language switch", language_switch, browser, base)
        run_section("Arabic interface", arabic_interface, browser, base)
        run_section("sources page", sources_page, browser, base)
        run_section("no review labels", no_review_labels, browser, base)
        run_section("biology question bank", biology_bank, browser, base)
        run_section("question PDFs", question_pdfs, browser, base)
        run_section("biology essay and picture questions", biology_written, browser, base)
        run_section("chemistry chapter 2 questions", chemistry_ch2, browser, base)
        run_section("Arabic Unit 3 PDFs", arabic_unit3, browser, base)
        run_section("Arabic Unit 3 questions on the site", arabic_quiz, browser, base)
        run_section("Arabic Unit 2 page and PDFs", arabic_unit2_page, browser, base)
        run_section("Arabic Unit 2 questions on the site", arabic_unit2_quiz, browser, base)
        run_section("Physics Chapter 2 lessons, questions and exam", physics_ch2, browser, base)
        run_section("dhikr card", dhikr, browser, base)
        browser.close()
    server.shutdown()
    contrast()

    passed = sum(1 for _, ok, _ in results if ok)
    print("\n%d checks, %d passed, %d failed" % (len(results), passed, len(results) - passed))
    print("Screenshots: %s" % SHOTS)
    data_untouched = all((PROJECT / name).read_bytes() == real_data[name] for name in real_data)
    print("Project data files unchanged by the test: %s" % data_untouched)
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
