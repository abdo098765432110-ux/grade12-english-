"""Builds the downloadable question PDFs: the questions first, then an answer
key on the last page (development tool — the website itself only links to the
finished files):

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

# Soft colours for each subject (calmer versions of the website's --sky, --sun, --mint).
TONES = {
    "english": {"ink": "#335c8a", "soft": "#e8f0fa", "edge": "#c6d8ee"},
    "chemistry": {"ink": "#7d5418", "soft": "#fbf1dc", "edge": "#ead3a1"},
    "biology": {"ink": "#2e6b52", "soft": "#e5f3eb", "edge": "#b9dbc8"},
}

# Words that depend on the language of the document.
WORDS = {
    "ar": {"letters": "أبجد", "contents": "محتوى الملف",
           "page": "صفحة", "of": "من", "key": "مفتاح الإجابات", "key_note": "مفتاح الإجابات في آخر الملف",
           "key_help": "رقم السؤال وبجانبه حرف الإجابة الصحيحة. الشرح الكامل لكل سؤال موجود على الموقع.",
           "written": "مقالي", "written_head": "إجابات الأسئلة المقالية", "question": "سؤال %d"},
    "en": {"letters": "ABCD", "contents": "In this file",
           "page": "Page", "of": "of", "key": "Answer Key", "key_note": "Answer key at the end",
           "key_help": "Question number and the letter of the correct answer. Each question is explained on the website.",
           "written": "written", "written_head": "Answers to the written questions", "question": "Question %d"},
}


def serve(folder):
    handler = type("Quiet", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *args: None})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(handler, directory=str(folder)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/" % server.server_address[1]


def text(value):
    return html.escape(value, quote=False)


def how_many(lang, n, noun):
    """"10 أسئلة", "40 سؤالًا", "100 سؤال" (Arabic number agreement) or "40 questions"."""
    if lang == "en":
        return "%d %s" % (n, noun + ("" if n == 1 else "s"))
    forms = {"question": ("سؤال واحد", "سؤالان", "أسئلة", "سؤالًا", "سؤال"),
             "section": ("قسم واحد", "قسمان", "أقسام", "قسمًا", "قسم")}[noun]
    if n == 1:
        return forms[0]
    if n == 2:
        return forms[1]
    rest = n % 100
    if 3 <= rest <= 10:
        return "%d %s" % (n, forms[2])
    if 11 <= rest <= 99:
        return "%d %s" % (n, forms[3])
    return "%d %s" % (n, forms[4])


# A short run of Latin text inside Arabic (for example "A = Ti" or "FeO ،X"), kept
# on one line: if the line broke inside it, right-to-left order would scatter it.
LATIN_RUN = re.compile(r"(?=[A-Za-z0-9(])[A-Za-z0-9\u2080-\u2089\u00b0-\u00b9()+=:.\u2192\u0394-]+(?: [A-Za-z0-9\u2080-\u2089\u00b0-\u00b9()+=:.\u2192\u0394-]+)+")


def keep_together(value):
    return LATIN_RUN.sub(lambda m: m.group(0).replace(" ", "\u00a0") if len(m.group(0)) <= 24 else m.group(0), value)


def css(tone, lang, running_title):
    return """
@page {
  size: A4;
  margin: 17mm 15mm 16mm;
  background: #f7f6f2;
  @top-center { content: "%(running)s"; font-family: "DejaVu Sans", sans-serif; font-size: 8pt; color: #8a8f9b; }
  @bottom-center { content: "%(page)s " counter(page) " %(of)s " counter(pages); font-family: "DejaVu Sans", sans-serif; font-size: 8.5pt; color: #8a8f9b; }
}
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; background: transparent; }
body { font-family: "DejaVu Sans", sans-serif; font-size: %(size)s; line-height: 1.7; color: #3a414e; }

/* the title block on page 1 */
.cover { padding: 15pt 17pt 13pt; border: 1pt solid %(edge)s; border-radius: 12pt; background: linear-gradient(135deg, %(soft)s 0%%, #ffffff 85%%); }
.cover .kicker { margin: 0; font-size: 9pt; font-weight: 700; color: %(ink)s; opacity: 0.85; }
.cover h1 { margin: 3pt 0 2pt; font-size: 19pt; line-height: 1.35; color: %(ink)s; }
.cover .sub { margin: 0; font-size: 10.5pt; color: #59606d; }
.chips { display: flex; flex-wrap: wrap; gap: 5pt; margin: 9pt 0 0; padding: 0; list-style: none; }
.chips li { padding: 1.5pt 9pt; border-radius: 20pt; background: #ffffff; border: 0.8pt solid %(edge)s; color: %(ink)s; font-size: 8.5pt; font-weight: 700; }
.chips li.site { background: transparent; border-color: transparent; color: #8a8f9b; font-weight: 400; }

/* contents */
.contents { margin: 10pt 0 4pt; padding: 9pt 13pt; border-radius: 10pt; background: #ffffff; border: 0.8pt solid #e4e1d8; }
.contents h2 { margin: 0 0 4pt; font-size: 10pt; color: %(ink)s; }
.contents ol { margin: 0; padding: 0; list-style: none; counter-reset: c; }
.contents li { counter-increment: c; display: flex; align-items: baseline; gap: 6pt; padding: 2.5pt 0; border-bottom: 0.6pt dashed #e4e1d8; font-size: 9.5pt; }
.contents li:last-child { border-bottom: 0; }
.contents li::before { content: counter(c); flex: none; width: 15pt; height: 15pt; border-radius: 50%%; background: %(soft)s; color: %(ink)s; font-size: 8pt; font-weight: 700; text-align: center; line-height: 15pt; }
.contents .name { flex: 1 1 auto; }
.contents .n { flex: none; color: #7a808c; font-size: 8.5pt; }

/* one part (a section of the website) */
.part + .part, .key { break-before: page; }
.part-head { break-after: avoid; display: flex; align-items: center; gap: 8pt; margin: 14pt 0 9pt; padding: 7pt 12pt; border-radius: 10pt; background: %(soft)s; border: 0.8pt solid %(edge)s; }
.part + .part .part-head, .key .part-head { margin-top: 0; }
.part-head h2 { flex: 1 1 auto; margin: 0; font-size: 12.5pt; line-height: 1.4; color: %(ink)s; }
.part-head .n { flex: none; padding: 1pt 8pt; border-radius: 20pt; background: #ffffff; color: %(ink)s; font-size: 8.5pt; font-weight: 700; }

/* one question */
.q { break-inside: avoid; margin: 0 0 7pt; padding: 9pt 11pt 8pt; border-radius: 9pt; background: #ffffff; border: 0.8pt solid #e6e3da; }
.q-head { display: flex; gap: 8pt; align-items: flex-start; }
.num { flex: none; min-width: 22pt; height: 20pt; padding: 0 5pt; border-radius: 7pt; background: %(soft)s; color: %(ink)s; font-weight: 700; font-size: 9.5pt; display: flex; align-items: center; justify-content: center; direction: ltr; }
.prompt { white-space: pre-line; font-weight: 700; color: #343b48; padding-top: 1pt; min-width: 0; }
.fig { margin: 7pt 0 3pt; padding: 5pt; text-align: center; border-radius: 7pt; background: #ffffff; border: 0.6pt solid #eeebe3; }
.fig img { max-width: 100%%; object-fit: contain; }
.opts { list-style: none; margin: 6pt 0 0; padding-block: 0; padding-inline: 30pt 0; display: grid; gap: 4pt 16pt; }
.opts.two { grid-template-columns: 1fr 1fr; }
.opts li { display: flex; gap: 6pt; align-items: baseline; break-inside: avoid; }
.opts .l { flex: none; width: 15pt; height: 15pt; border-radius: 50%%; background: %(soft)s; color: %(ink)s; font-weight: 700; font-size: 8.5pt; line-height: 15pt; text-align: center; }
.opts .t { white-space: pre-line; unicode-bidi: plaintext; }

/* the answer key */
.key-help { margin: -3pt 0 8pt; color: #6b7280; font-size: 8.5pt; }
.key h3 { break-after: avoid; margin: 9pt 0 4pt; font-size: 10pt; color: %(ink)s; }
.grid { width: 100%%; border-collapse: separate; border-spacing: 2pt; table-layout: fixed; }
.grid tr { break-inside: avoid; }
.grid td { padding: 2pt 0; border-radius: 5pt; background: #ffffff; border: 0.6pt solid #e6e3da; text-align: center; font-size: 9.5pt; line-height: 1.45; white-space: nowrap; }
.grid td.empty { background: transparent; border-color: transparent; }
.grid .qn { display: inline-block; min-width: 15pt; color: #8a8f9b; font-size: 8pt; direction: ltr; }
.grid .a { display: inline-block; min-width: 12pt; color: %(ink)s; font-weight: 700; }
.grid .w { color: %(ink)s; font-size: 7.5pt; font-weight: 700; }
.written { margin: 6pt 0 0; padding: 0; list-style: none; }
.written li { break-inside: avoid; margin: 0 0 5pt; padding: 7pt 10pt; border-radius: 8pt; background: #ffffff; border: 0.8pt solid #e6e3da; font-size: 9pt; }
.written b { color: %(ink)s; }
.written .t { white-space: pre-line; unicode-bidi: plaintext; }
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


def shower(words):
    """The words of a question, exactly as in the data (in Arabic, short Latin runs kept on one line)."""
    return (lambda value: text(keep_together(value))) if words is WORDS["ar"] else text


def question_block(number, question, words):
    letters = words["letters"]
    show = shower(words)
    figure = ""
    if question.get("image"):
        width, height = figure_size(SITE / question["image"])
        figure = '<div class="fig"><img src="%s" alt="%s" style="width:%.1fmm;height:%.1fmm"></div>' % (
            text(question["image"]), text(question.get("imageAlt", "")), width, height)
    options = question.get("options") or []
    body = ""
    if options:
        short = all(len(option) <= 30 and "\n" not in option for option in options)
        items = "".join('<li><span class="l">%s</span><span class="t" dir="auto">%s</span></li>' % (letters[i], show(option))
                        for i, option in enumerate(options))
        body = '<ul class="opts%s">%s</ul>' % (" two" if short else "", items)
    return '<section class="q"><div class="q-head"><span class="num">%d</span><div class="prompt" dir="auto">%s</div></div>%s%s</section>' % (
        number, show(question["prompt"]), figure, body)


def answer_key(parts, words):
    """The last page(s): for each part, a grid of question numbers with the
    letter of the correct answer, then the model answers of written questions."""
    letters = words["letters"]
    show = shower(words)
    blocks = []
    for heading, questions in parts:
        cells, written = [], []
        for number, question in enumerate(questions, 1):
            if question.get("options"):
                letter = letters[question["options"].index(question["answer"])]
                cells.append('<td><span class="qn">%d</span> <span class="a">%s</span></td>' % (number, letter))
            else:
                cells.append('<td><span class="qn">%d</span> <span class="w">%s</span></td>' % (number, words["written"]))
                written.append('<li><b>%s:</b> <span class="t" dir="auto">%s</span></li>' % (words["question"] % number, show(question["modelAnswer"])))
        cells += ['<td class="empty"></td>'] * (-len(cells) % 10)
        rows = "".join("<tr>%s</tr>" % "".join(cells[k:k + 10]) for k in range(0, len(cells), 10))
        block = '<h3>%s</h3><table class="grid">%s</table>' % (text(heading), rows)
        if written:
            block += '<h3>%s</h3><ul class="written">%s</ul>' % (words["written_head"], "".join(written))
        blocks.append(block)
    return ('<section class="key"><div class="part-head"><h2>%s</h2></div><p class="key-help">%s</p>%s</section>'
            % (words["key"], words["key_help"], "".join(blocks)))


def document(lang, tone, title, kicker, heading, subtitle, parts, base_url):
    """parts: [(heading, [questions])]; numbering starts again at 1 in each part,
    as on the website. The answers are all in the answer key at the end."""
    words = WORDS[lang]
    total = sum(len(questions) for _, questions in parts)
    contents = "".join('<li><span class="name">%s</span><span class="n">%s</span></li>' % (text(name), how_many(lang, len(questions), "question"))
                       for name, questions in parts)
    contents += '<li><span class="name">%s</span><span class="n"></span></li>' % words["key"]
    sections = []
    for name, questions in parts:
        blocks = "".join(question_block(n, q, words) for n, q in enumerate(questions, 1))
        sections.append('<section class="part"><div class="part-head"><h2>%s</h2><span class="n">%s</span></div>%s</section>'
                        % (text(name), how_many(lang, len(questions), "question"), blocks))
    chips = [how_many(lang, total, "question"), how_many(lang, len(parts), "section"), words["key_note"]]
    return """<!DOCTYPE html>
<html lang="%s" dir="%s"><head><meta charset="utf-8"><base href="%s"><title>%s</title><style>%s</style></head>
<body>
<header class="cover"><p class="kicker">%s</p><h1>%s</h1><p class="sub">%s</p>
<ul class="chips">%s<li class="site" dir="ltr">%s</li></ul></header>
<nav class="contents"><h2>%s</h2><ol>%s</ol></nav>
%s
%s
</body></html>""" % (lang, "rtl" if lang == "ar" else "ltr", base_url, text(title), css(tone, lang, title),
                    text(kicker), text(heading), text(subtitle), "".join("<li>%s</li>" % c for c in chips), SITE_NAME,
                    words["contents"], contents, "\n".join(sections), answer_key(parts, words))


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
    out = [(ENGLISH_PDF, document("en", TONES["english"], "English — Question Bank with Answer Key",
                                  "English · Grade 12", "English Question Bank", "Grammar Practice and Vocabulary",
                                  english_parts(), base),
            grammar + vocabulary)]
    chemistry = load("chemistry-questions.json")
    parts = [(chapter["title"] + " — " + section["title"], section["questions"])
             for chapter in chemistry["chapters"] for section in chapter["sections"]]
    chapters = "، ".join(chapter["title"] for chapter in chemistry["chapters"])
    out.append((chemistry["pdf"], document("ar", TONES["chemistry"], "الكيمياء — بنك الأسئلة ومفتاح الإجابات",
                                           "الكيمياء · الصف الثالث الثانوي", "بنك أسئلة الكيمياء", chapters, parts, base),
                [q for _, questions in parts for q in questions]))
    for chapter in load("biology-questions.json")["chapters"]:
        parts = [(section["title"], section["questions"]) for section in chapter["sections"]]
        out.append((chapter["pdf"], document("ar", TONES["biology"], "الأحياء — " + chapter["title"],
                                             "الأحياء · الصف الثالث الثانوي", "بنك أسئلة الأحياء", chapter["title"], parts, base),
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
