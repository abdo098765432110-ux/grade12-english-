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
    """Wait until the page has finished loading its content."""
    page.wait_for_function("!document.querySelector('.loading')")


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
