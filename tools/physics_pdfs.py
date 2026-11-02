"""Builds the two downloadable physics PDFs (development tool — the website
itself only links to the finished files):

  physics-ch1-questions.pdf  every question of "حل أسئلة الفصل الأول" from
                             physics-questions.json: numbered, with all four
                             choices and the diagrams, on A4 pages, and the
                             answer key on the last page.
  physics-ch1-laws.pdf       the revision sheet physics-ch1-laws.html, printed
                             the same way the browser prints it (sheet.css: A4).

Run it again whenever the questions or the revision sheet change:
    python tools/physics_pdfs.py
Needs Python with Playwright and Chromium (the same as tests/e2e_test.py)."""
import functools
import html
import http.server
import json
import pathlib
import re
import threading

from playwright.sync_api import sync_playwright

SITE = pathlib.Path(__file__).resolve().parent.parent
LETTERS = "أبجد"


def serve(folder):
    handler = type("Quiet", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *args: None})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(handler, directory=str(folder)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/" % server.server_address[1]


def text(value):
    return html.escape(value, quote=False)


QUESTIONS_CSS = """
@page {
  size: A4;
  margin: 15mm 13mm 15mm;
  @top-center { content: "حل أسئلة الفصل الأول — الفيزياء"; font-family: "DejaVu Sans", sans-serif; font-size: 8.5pt; color: #6b7590; }
  @bottom-center { content: counter(page) " / " counter(pages); font-family: "DejaVu Sans", sans-serif; font-size: 9pt; color: #6b7590; }
}
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; background: #fff; }
body { font-family: "DejaVu Sans", "Segoe UI", Tahoma, sans-serif; font-size: 10.3pt; line-height: 1.65; color: #23304d; }
.head { padding-bottom: 6pt; margin-bottom: 8pt; border-bottom: 2.5pt solid #c9b8f5; }
.head h1 { margin: 0; font-size: 18pt; color: #3e2c8c; }
.head p { margin: 2pt 0 0; color: #56617c; font-size: 9.5pt; }
.source { margin: 0 0 10pt; padding: 5pt 8pt; border: 0.8pt solid #f2cf6b; border-right-width: 3pt; border-radius: 4pt; background: #fff7e0; font-size: 9pt; }
.q { break-inside: avoid; padding: 7pt 0 8pt; border-bottom: 0.7pt solid #e3e8f3; }
.q-head { display: flex; gap: 7pt; align-items: flex-start; }
.num { flex: none; min-width: 20pt; height: 20pt; padding: 0 4pt; border-radius: 5pt; background: #ebe4ff; color: #3e2c8c; font-weight: 700; font-size: 10pt; display: flex; align-items: center; justify-content: center; direction: ltr; }
.prompt { white-space: pre-line; font-weight: 700; padding-top: 1pt; }
.fig { margin: 5pt 0 3pt; text-align: center; }
.fig img { max-width: 100%; object-fit: contain; }
.opts { list-style: none; margin: 4pt 0 0; padding: 0 27pt 0 0; display: grid; gap: 2pt 14pt; }
.opts.two { grid-template-columns: 1fr 1fr; }
.opts li { display: flex; gap: 5pt; align-items: baseline; break-inside: avoid; }
.opts .l { flex: none; font-weight: 700; color: #3e2c8c; }
.opts .t { white-space: pre-line; unicode-bidi: plaintext; }
.key { break-before: page; }
.key h2 { margin: 0 0 8pt; font-size: 14pt; color: #3e2c8c; }
.key p { margin: 0 0 8pt; color: #56617c; font-size: 9pt; }
.key table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
.key td { border: 0.7pt solid #dbe3f2; padding: 3pt 0; text-align: center; width: 10%; }
.key td b { display: inline-block; min-width: 18pt; color: #3e2c8c; direction: ltr; }
.key td:nth-child(odd) { background: #fbfaff; }
"""


def figure_size(path):
    """Width and height (mm) for a diagram on the page: as large as fits in
    140 mm × 62 mm, keeping its shape, so small and large drawings look alike."""
    source = path.read_text(encoding="utf-8")
    match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', source)
    width, height = (float(match.group(1)), float(match.group(2))) if match else (600.0, 300.0)
    scale = min(140 / width, 62 / height)
    return width * scale, height * scale


def option_list(question):
    options = question["options"]
    short = all(len(option) <= 30 and "\n" not in option for option in options)
    items = "".join(
        '<li><span class="l">%s)</span><span class="t" dir="auto">%s</span></li>' % (LETTERS[i], text(option))
        for i, option in enumerate(options))
    return '<ul class="opts%s">%s</ul>' % (" two" if short else "", items)


def questions_document(section, base_url):
    questions = section["questions"]
    blocks = []
    for number, question in enumerate(questions, 1):
        figure = ""
        if question.get("image"):
            width, height = figure_size(SITE / question["image"])
            figure = '<div class="fig"><img src="%s" alt="%s" style="width:%.1fmm;height:%.1fmm"></div>' % (
                text(question["image"]), text(question.get("imageAlt", "")), width, height)
        blocks.append('<section class="q"><div class="q-head"><span class="num">%d</span><div class="prompt">%s</div></div>%s%s</section>'
                      % (number, text(question["prompt"]), figure, option_list(question)))
    cells = []
    for number, question in enumerate(questions, 1):
        letter = LETTERS[question["options"].index(question["answer"])]
        cells.append("<td><b>%d</b> %s</td>" % (number, letter))
    rows = "".join("<tr>%s</tr>" % "".join(cells[k:k + 10]) for k in range(0, len(cells), 10))
    return """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><base href="%s"><title>%s</title><style>%s</style></head>
<body>
<header class="head"><h1>%s — الفيزياء</h1><p>الصف الثالث الثانوي · الفصل الأول · %d سؤال اختيار من متعدد · <span dir="ltr">Learn for Grade 12</span></p></header>
<p class="source">الأسئلة منقولة من المحتوى التعليمي المنشور على قنوات مستر حسام خليل (HKh Physics) ومستر سعد الدين طارق (الشارح) على YouTube.</p>
%s
<section class="key"><h2>مفتاح الإجابات</h2><p>رقم السؤال ثم حرف الإجابة الصحيحة. الشرح الكامل لكل سؤال موجود على الموقع.</p><table>%s</table></section>
</body></html>""" % (base_url, text(section["title"]), QUESTIONS_CSS, text(section["title"]), len(questions), "\n".join(blocks), rows)


def main():
    data = json.loads((SITE / "physics-questions.json").read_text(encoding="utf-8"))
    chapter = data["chapters"][0]
    section = chapter["sections"][0]
    server, base = serve(SITE)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # 1. the questions
            page.set_content(questions_document(section, base), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(SITE / section["pdf"]), prefer_css_page_size=True, print_background=True)
            # 2. the revision sheet, printed the way a browser prints it
            page.goto(base + chapter["revision"]["page"], wait_until="networkidle")
            # Arabic in DejaVu Sans with its real bold face (the font installed where the PDF is made)
            page.add_style_tag(content='.sheet { font-family: "DejaVu Sans", sans-serif !important; }')
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(SITE / chapter["revision"]["pdf"]), prefer_css_page_size=True, print_background=True)
            browser.close()
    finally:
        server.shutdown()
    print("written:", section["pdf"], chapter["revision"]["pdf"])


if __name__ == "__main__":
    main()
