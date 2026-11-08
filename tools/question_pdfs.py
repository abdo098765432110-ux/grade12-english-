"""Builds the downloadable question PDFs, with the correct answer after every
question (development tool — the website itself only links to the finished files):

  english-questions.pdf      every English question on the website: Grammar
                             Practice (grammar-questions.json) and Vocabulary
                             (vocabulary-questions.json)
  chemistry-questions.pdf    every question in chemistry-questions.json
  biology-ch1-questions.pdf  every question of Biology Chapter 1
  biology-ch2-questions.pdf  every question of Biology Chapter 2
                             (biology-questions.json; the two chapters stay separate)

The questions are copied exactly as they are in the data files, in the same
order, numbered from 1 in each section (as on the website). The file names come
from the data: "pdf" at the top of chemistry-questions.json and on each Biology
chapter; the English file name is ENGLISH_PDF below (index.html links to it).

Run it again whenever the questions change:
    python3 tools/question_pdfs.py
Needs Python with Playwright and Chromium (the same as tests/e2e_test.py) and
the DejaVu Sans font (the same as tools/physics_pdfs.py). It also writes
question-pdfs.json: what each PDF was made from (checked by the tests)."""
import functools
import hashlib
import html
import http.server
import json
import pathlib
import re
import threading

from playwright.sync_api import sync_playwright

SITE = pathlib.Path(__file__).resolve().parent.parent
ENGLISH_PDF = "english-questions.pdf"
SITE_NAME = "Learn for Grade 12"

# Colours of each subject on the website (style.css: --sky, --sun, --mint).
TONES = {
    "english": {"ink": "#23559f", "soft": "#dcebff", "edge": "#a9cbff"},
    "chemistry": {"ink": "#744b00", "soft": "#fff0b3", "edge": "#ffd25c"},
    "biology": {"ink": "#1b6b49", "soft": "#d3f4e4", "edge": "#93dfbd"},
}

# Words that depend on the language of the document.
WORDS = {
    "ar": {"letters": "أبجد", "answer": "الإجابة الصحيحة:", "model": "الإجابة النموذجية:",
           "count": "%d سؤال", "contents": "محتوى الملف", "page": "صفحة", "of": "من"},
    "en": {"letters": "ABCD", "answer": "Correct answer:", "model": "Model answer:",
           "count": "%d questions", "contents": "In this file", "page": "Page", "of": "of"},
}


def serve(folder):
    handler = type("Quiet", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *args: None})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(handler, directory=str(folder)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/" % server.server_address[1]


def text(value):
    return html.escape(value, quote=False)


# A short run of Latin text inside Arabic (for example "A = Ti" or "FeO ،X"), kept
# on one line: if the line broke inside it, right-to-left order would scatter it.
LATIN_RUN = re.compile(r"(?=[A-Za-z0-9(])[A-Za-z0-9\u2080-\u2089\u00b0-\u00b9()+=:.\u2192\u0394-]+(?: [A-Za-z0-9\u2080-\u2089\u00b0-\u00b9()+=:.\u2192\u0394-]+)+")


def keep_together(value):
    return LATIN_RUN.sub(lambda m: m.group(0).replace(" ", "\u00a0") if len(m.group(0)) <= 24 else m.group(0), value)


def css(tone, lang, running_title):
    return """
@page {
  size: A4;
  margin: 16mm 14mm 16mm;
  @top-center { content: "%(running)s"; font-family: "DejaVu Sans", sans-serif; font-size: 8.5pt; color: #6b7590; }
  @bottom-center { content: "%(page)s " counter(page) " %(of)s " counter(pages); font-family: "DejaVu Sans", sans-serif; font-size: 9pt; color: #6b7590; }
}
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; background: #fff; }
body { font-family: "DejaVu Sans", sans-serif; font-size: %(size)s; line-height: 1.6; color: #23304d; }
.head { padding-bottom: 7pt; margin-bottom: 9pt; border-bottom: 2.5pt solid %(edge)s; }
.head h1 { margin: 0; font-size: 17pt; line-height: 1.35; color: %(ink)s; }
.head p { margin: 3pt 0 0; color: #56617c; font-size: 9.5pt; }
.contents { margin: 0 0 6pt; padding: 6pt 10pt; border: 0.8pt solid %(edge)s; border-radius: 5pt; background: #fbfcff; font-size: 9.5pt; }
.contents b { color: %(ink)s; }
.contents ol { margin: 3pt 0 0; padding-inline-start: 16pt; }
.part { break-before: auto; }
.part h2 { break-after: avoid; margin: 12pt 0 4pt; padding: 5pt 9pt; border-radius: 5pt; background: %(soft)s; border-inline-start: 4pt solid %(edge)s; color: %(ink)s; font-size: 12.5pt; line-height: 1.35; }
.q { break-inside: avoid; padding: 7pt 0 8pt; border-bottom: 0.7pt solid #e3e8f3; }
.q-head { display: flex; gap: 7pt; align-items: flex-start; }
.num { flex: none; min-width: 21pt; height: 19pt; padding: 0 4pt; border-radius: 5pt; background: %(soft)s; color: %(ink)s; font-weight: 700; font-size: 9.5pt; display: flex; align-items: center; justify-content: center; direction: ltr; }
.prompt { white-space: pre-line; font-weight: 700; padding-top: 1pt; min-width: 0; }
.fig { margin: 5pt 0 3pt; text-align: center; }
.fig img { max-width: 100%%; object-fit: contain; }
.opts { list-style: none; margin: 4pt 0 0; padding-block: 0; padding-inline: 28pt 0; display: grid; gap: 2pt 14pt; }
.opts.two { grid-template-columns: 1fr 1fr; }
.opts li { display: flex; gap: 5pt; align-items: baseline; break-inside: avoid; }
.opts .l { flex: none; font-weight: 700; color: %(ink)s; }
.opts .t { white-space: pre-line; unicode-bidi: plaintext; }
.ans { margin: 5pt 0 0; margin-inline-start: 28pt; padding: 3pt 8pt; border-radius: 4pt; background: #e9f7ef; border-inline-start: 3pt solid #2f9e5f; color: #17633a; font-size: 0.95em; }
.ans b { font-weight: 700; }
.ans .t { white-space: pre-line; unicode-bidi: plaintext; }
""" % {"running": running_title.replace('"', "'"), "size": "10pt" if lang == "ar" else "10.2pt",
       "page": WORDS[lang]["page"], "of": WORDS[lang]["of"],
       "ink": tone["ink"], "soft": tone["soft"], "edge": tone["edge"]}


def figure_size(path):
    """Width and height (mm) for a diagram on the page: as large as fits in
    140 mm x 62 mm, keeping its shape (the same rule as tools/physics_pdfs.py)."""
    source = path.read_text(encoding="utf-8")
    match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', source)
    width, height = (float(match.group(1)), float(match.group(2))) if match else (600.0, 300.0)
    scale = min(140 / width, 62 / height)
    return width * scale, height * scale


def question_block(number, question, words):
    letters = words["letters"]
    # the words of the question, exactly as in the data (in Arabic, short Latin runs kept on one line)
    show = (lambda value: text(keep_together(value))) if words is WORDS["ar"] else text
    figure = ""
    if question.get("image"):
        width, height = figure_size(SITE / question["image"])
        figure = '<div class="fig"><img src="%s" alt="%s" style="width:%.1fmm;height:%.1fmm"></div>' % (
            text(question["image"]), text(question.get("imageAlt", "")), width, height)
    options = question.get("options") or []
    if options:
        short = all(len(option) <= 30 and "\n" not in option for option in options)
        items = "".join('<li><span class="l">%s)</span><span class="t" dir="auto">%s</span></li>' % (letters[i], show(option))
                        for i, option in enumerate(options))
        body = '<ul class="opts%s">%s</ul>' % (" two" if short else "", items)
        k = options.index(question["answer"])
        answer = '<p class="ans"><b>%s</b> %s) <span class="t" dir="auto">%s</span></p>' % (words["answer"], letters[k], show(question["answer"]))
    else:  # a written-answer question: its model answer
        body = ""
        answer = '<p class="ans"><b>%s</b> <span class="t" dir="auto">%s</span></p>' % (words["model"], show(question["modelAnswer"]))
    return '<section class="q"><div class="q-head"><span class="num">%d</span><div class="prompt" dir="auto">%s</div></div>%s%s%s</section>' % (
        number, show(question["prompt"]), figure, body, answer)


def document(lang, tone, title, subtitle, parts, base_url):
    """parts: [(heading, [questions])]; numbering starts again at 1 in each part."""
    words = WORDS[lang]
    total = sum(len(questions) for _, questions in parts)
    contents = "".join("<li>%s — %s</li>" % (text(heading), words["count"] % len(questions)) for heading, questions in parts)
    sections = []
    for heading, questions in parts:
        blocks = "".join(question_block(n, q, words) for n, q in enumerate(questions, 1))
        sections.append('<section class="part"><h2>%s <span dir="ltr">(%d)</span></h2>%s</section>' % (text(heading), len(questions), blocks))
    return """<!DOCTYPE html>
<html lang="%s" dir="%s"><head><meta charset="utf-8"><base href="%s"><title>%s</title><style>%s</style></head>
<body>
<header class="head"><h1>%s</h1><p>%s · %s · <span dir="ltr">%s</span></p></header>
<div class="contents"><b>%s</b><ol>%s</ol></div>
%s
</body></html>""" % (lang, "rtl" if lang == "ar" else "ltr", base_url, text(title), css(tone, lang, title),
                    text(title), text(subtitle), words["count"] % total, SITE_NAME,
                    words["contents"], contents, "\n".join(sections))


def load(name):
    return json.loads((SITE / name).read_text(encoding="utf-8"))


def english_parts():
    lessons = {lesson["id"]: lesson["title"] for lesson in load("grammar-lessons.json")["lessons"]}
    grammar = load("grammar-questions.json")["questions"]
    parts = []
    topics = []
    for question in grammar:  # one part per grammar topic, in the order of the file
        if question.get("topicId") not in topics:
            topics.append(question.get("topicId"))
    for topic in topics:
        parts.append(("Grammar Practice: " + lessons.get(topic, "Other questions"),
                      [q for q in grammar if q.get("topicId") == topic]))
    for unit in load("vocabulary-questions.json")["units"]:
        parts.append(("Vocabulary: " + unit["title"], unit["questions"]))
    return parts


def jobs(base):
    """(file name, html, the questions in it) for each PDF."""
    grammar = load("grammar-questions.json")["questions"]
    vocabulary = [q for unit in load("vocabulary-questions.json")["units"] for q in unit["questions"]]
    out = [(ENGLISH_PDF, document("en", TONES["english"], "English — All Questions with Answers",
                                  "Grade 12 · Grammar Practice and Vocabulary", english_parts(), base),
            grammar + vocabulary)]
    chemistry = load("chemistry-questions.json")
    parts = [(chapter["title"] + " — " + section["title"], section["questions"])
             for chapter in chemistry["chapters"] for section in chapter["sections"]]
    out.append((chemistry["pdf"], document("ar", TONES["chemistry"], "الكيمياء — جميع الأسئلة بالإجابات",
                                           "الصف الثالث الثانوي", parts, base),
                [q for _, questions in parts for q in questions]))
    for chapter in load("biology-questions.json")["chapters"]:
        parts = [(section["title"], section["questions"]) for section in chapter["sections"]]
        out.append((chapter["pdf"], document("ar", TONES["biology"], "الأحياء — " + chapter["title"],
                                             "الصف الثالث الثانوي · جميع الأسئلة بالإجابات", parts, base),
                    [q for _, questions in parts for q in questions]))
    return out


def fingerprint(questions):
    """A short code that changes whenever a question, option, answer or diagram
    changes (tests/schema.test.js works it out the same way, so the tests fail
    when a PDF is older than its questions)."""
    digest = hashlib.sha256()
    for q in questions:
        fields = [q["prompt"]] + list(q.get("options") or []) + [q.get("answer", ""), q.get("modelAnswer", ""), q.get("image", "")]
        digest.update(("\x1f".join(fields) + "\x1e").encode("utf-8"))
    return digest.hexdigest()[:16]


def main():
    server, base = serve(SITE)
    made = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            for name, source, questions in jobs(base):
                page.set_content(source, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(SITE / name), prefer_css_page_size=True, print_background=True)
                made.append({"pdf": name, "questions": len(questions), "fingerprint": fingerprint(questions)})
                print("written:", name, len(questions), "questions")
            browser.close()
    finally:
        server.shutdown()
    # what each PDF was made from, for the tests
    (SITE / "question-pdfs.json").write_text(json.dumps({"files": made}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: question-pdfs.json")


if __name__ == "__main__":
    main()
