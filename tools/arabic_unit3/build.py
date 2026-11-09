"""Builds the two Arabic PDFs for Unit 3 «النواسخ» (development tool — the
website only links to the finished files):

  arabic-unit3-questions.pdf  «100 سؤال على الوحدة الثالثة – اللغة العربية»:
                              a cover, the questions in five sections, and the
                              answer key with a short reason for every answer
                              (from tools/arabic_unit3/questions.json)
  arabic-unit3-summary.pdf    the summary of the unit, in the same design
                              (from tools/arabic_unit3/summary.html)

Run it again after changing either source file (it also writes built.json,
which the tests use to check the PDFs are up to date):
    python3 tools/arabic_unit3/build.py
Needs Python with Playwright and Chromium (the same as tests/e2e_test.py), and
pypdf. The fonts are in tools/fonts (Noto Naskh Arabic, Noto Kufi Arabic and
Amiri, under the SIL Open Font License) and are embedded in the PDFs."""
import functools
import hashlib
import html
import http.server
import json
import pathlib
import re
import threading

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent
QUESTIONS_PDF = "arabic-unit3-questions.pdf"
SUMMARY_PDF = "arabic-unit3-summary.pdf"
TITLE = "100 سؤال على الوحدة الثالثة – اللغة العربية"
SITE_NAME = "Learn for Grade 12"
LETTERS = "أبجد"
SECTIONS = [
    ("kana", "القسم الأول", "كان وأخواتها", "الأفعال الناسخة: معانيها، وعملها، وأنواع خبرها، وتقدّمه، و«ليس» و«ما» والباء الزائدة، و«كان» التامة."),
    ("kada", "القسم الثاني", "أفعال المقاربة والرجاء والشروع", "كاد وكرب وأوشك، وعسى وحرى واخلولق، وأخذ وشرع وطفق: خبرها واقترانه بـ«أن»، والتام منها والناسخ."),
    ("inna", "القسم الثالث", "إنّ وأخواتها، وهمزة إنّ", "الحروف الناسخة ومعانيها، وتقدّم الخبر شبه الجملة، واللام المزحلقة، و«إنّما»، ومواضع كسر الهمزة وفتحها."),
    ("la", "القسم الرابع", "لا النافية للجنس", "شروط عملها، واسمها المبني والمعرب، وخبرها وحذفه، ومتى يبطل عملها."),
    ("mixed", "القسم الخامس", "تطبيقات شاملة على الوحدة", "أسئلة تجمع أكثر من ناسخ، وإعراب في سياق نصوص وأمثلة من الكتاب."),
]
LEVEL = {"medium": "متوسط", "hard": "صعب"}


def ar(n):
    """Arabic-Indic digits, as in Egyptian school books."""
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def text(value):
    return html.escape(value, quote=False)


QURAN = re.compile("﴿[^﴾]*﴾")


def body_text(value):
    """Question text for the page: escaped, with Arabic-Indic digits, and each
    Qur'an quotation ﴿…﴾ set in Amiri."""
    value = text(value).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))
    return QURAN.sub(lambda m: '<span class="quran">%s</span>' % m.group(0), value)


def how_many(n):
    """«١٠ أسئلة»، «٢٢ سؤالًا»، «١٠٠ سؤال» (Arabic number agreement)."""
    rest = n % 100
    word = "أسئلة" if 3 <= rest <= 10 else "سؤالًا" if 11 <= rest <= 99 else "سؤال"
    return "%s %s" % (ar(n), word)


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the site quietly; fonts are allowed to load into the generated page."""
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def serve(folder):
    handler = Handler
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(handler, directory=str(folder)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/" % server.server_address[1]


# ---------------------------------------------------------------- the shared design

BASE_CSS = """
@font-face { font-family: "Naskh"; src: url("tools/fonts/NotoNaskhArabic.ttf") format("truetype"); font-weight: 400 700; }
@font-face { font-family: "Kufi"; src: url("tools/fonts/NotoKufiArabic.ttf") format("truetype"); font-weight: 100 900; }
@font-face { font-family: "Amiri"; src: url("tools/fonts/Amiri-Regular.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Amiri"; src: url("tools/fonts/Amiri-Bold.ttf") format("truetype"); font-weight: 700; }
:root {
  --paper: #fbf8f2; --card: #fffdf9; --line: #e7dfd1; --ink: #28323d; --muted: #6c7480;
  --teal: #2d6a6e; --teal-soft: #e3eeec; --teal-line: #b9d3cf;
  --clay: #9b4f30; --clay-soft: #f6e6dc; --clay-line: #e7c3ad;
  --gold: #b38b4d; --gold-soft: #f3ead9;
}
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; background: transparent; }
body { font-family: "Naskh", serif; color: var(--ink); font-size: 11.2pt; line-height: 1.85; font-feature-settings: "kern"; }
h1, h2, h3, h4 { font-weight: 700; margin: 0; }
.kufi { font-family: "Kufi", sans-serif; }
.chip { display: inline-block; padding: 0.5pt 9pt 1.5pt; border-radius: 20pt; font-family: "Kufi", sans-serif; font-size: 8.4pt; font-weight: 600; line-height: 1.9; }
.chip.teal { background: var(--teal-soft); color: var(--teal); }
.chip.clay { background: var(--clay-soft); color: var(--clay); }
.chip.gold { background: var(--gold-soft); color: #7d5f2c; }
.rule { height: 0; border: 0; border-top: 1.2pt solid var(--gold); width: 46pt; margin: 8pt 0; }
.quran { font-family: "Amiri", serif; font-size: 1.08em; font-weight: 400; color: #1f4f53; }
"""


def page_css(running, first_blank=True):
    first = """
@page :first { margin: 0; @top-center { content: none; } @bottom-center { content: none; } }""" if first_blank else ""
    return """
@page {
  size: A4;
  margin: 19mm 17mm 18mm;
  background: #fbf8f2;
  @top-center { content: "%s"; font-family: "Kufi", sans-serif; font-size: 7.6pt; color: #8d8577; border-bottom: 0.6pt solid #e7dfd1; padding-bottom: 2pt; vertical-align: bottom; margin-bottom: 5mm; }
  @bottom-center { content: counter(page, arabic-indic); font-family: "Kufi", sans-serif; font-size: 8.5pt; color: #2d6a6e; }
}%s
""" % (running.replace('"', "'"), first)


# ---------------------------------------------------------------- the questions PDF

QUESTIONS_CSS = """
/* cover */
.cover { height: 297mm; padding: 15mm; position: relative; break-after: page; }
.frame { height: 100%; border: 1.3pt solid var(--gold); border-radius: 4pt; padding: 3.2mm; }
.frame-in { height: 100%; border: 0.5pt solid var(--gold); border-radius: 2pt; display: flex; flex-direction: column; align-items: center; text-align: center; padding: 22mm 16mm 14mm; background: linear-gradient(180deg, #fffdf9 0%, #fbf8f2 55%, #f5efe3 100%); }
.cover .top { font-family: "Kufi", sans-serif; font-size: 10.5pt; font-weight: 600; color: var(--teal); letter-spacing: 0.3pt; }
.star { width: 46pt; height: 46pt; position: relative; margin: 20mm 0 9mm; }
.star::before, .star::after { content: ""; position: absolute; inset: 7pt; border: 1.3pt solid var(--gold); }
.star::after { transform: rotate(45deg); }
.star span { position: absolute; inset: 19pt; background: var(--teal); border-radius: 50%; }
.cover h1 { font-family: "Amiri", serif; font-size: 34pt; line-height: 1.55; color: var(--ink); max-width: 140mm; }
.cover .unit { margin-top: 7mm; font-family: "Kufi", sans-serif; font-size: 15pt; font-weight: 700; color: var(--teal); }
.cover .parts { margin-top: 2.5mm; font-size: 11.5pt; color: var(--muted); }
.cover .facts { display: flex; gap: 5mm; margin-top: 15mm; }
.cover .fact { min-width: 36mm; padding: 4mm 5mm 3.5mm; border: 0.8pt solid var(--line); border-radius: 6pt; background: var(--card); }
.cover .fact b { display: block; font-family: "Kufi", sans-serif; font-size: 15pt; color: var(--teal); line-height: 1.5; }
.cover .fact span { font-size: 9.5pt; color: var(--muted); }
.cover .foot { margin-top: auto; font-size: 9.5pt; color: var(--muted); line-height: 1.8; }
.cover .foot .site { font-family: "Kufi", sans-serif; direction: ltr; unicode-bidi: isolate; color: #8d8577; font-size: 8.5pt; }

/* the page before the questions */
.intro { break-after: page; }
.intro h2 { font-family: "Amiri", serif; font-size: 23pt; color: var(--ink); line-height: 1.4; }
.toc { margin: 4mm 0 7mm; border-top: 0.8pt solid var(--line); }
.toc .row { display: flex; align-items: baseline; gap: 4mm; padding: 2.6mm 0; border-bottom: 0.8pt solid var(--line); }
.toc .no { flex: none; width: 22mm; font-family: "Kufi", sans-serif; font-size: 8.5pt; color: var(--teal); font-weight: 600; }
.toc .name { flex: 1 1 auto; font-weight: 700; }
.toc .count { flex: none; font-size: 9.5pt; color: var(--muted); }
.toc .pg { flex: none; width: 12mm; text-align: left; font-family: "Kufi", sans-serif; font-size: 10pt; color: var(--teal); font-weight: 700; }
.howto { padding: 5mm 6mm; border-radius: 7pt; background: var(--card); border: 0.8pt solid var(--line); }
.howto h3 { font-family: "Kufi", sans-serif; font-size: 10.5pt; color: var(--teal); margin-bottom: 1.5mm; }
.howto ul { margin: 0; padding-inline-start: 5mm; }
.howto li { margin: 0.6mm 0; }
.legend { display: flex; gap: 4mm; align-items: center; margin-top: 2.5mm; font-size: 9.5pt; color: var(--muted); }

/* a section of questions */
.section { break-before: page; }
.opener { padding: 0 0 4mm; margin-bottom: 5mm; border-bottom: 0.8pt solid var(--line); }
.opener .no { font-family: "Kufi", sans-serif; font-size: 9pt; font-weight: 600; color: var(--teal); }
.opener h2 { font-family: "Amiri", serif; font-size: 24pt; line-height: 1.45; color: var(--ink); margin-top: 1mm; }
.opener p { margin: 1mm 0 2.5mm; color: var(--muted); font-size: 10.2pt; line-height: 1.75; }
.opener .chips { display: flex; gap: 2mm; flex-wrap: wrap; }

/* one question */
.q { break-inside: avoid; padding: 3.2mm 0 3.6mm; border-bottom: 0.7pt dashed #ddd3c2; }
.q:last-child { border-bottom: 0; }
.q-top { display: flex; gap: 3.2mm; align-items: flex-start; }
.num { flex: none; width: 8.5mm; height: 8.5mm; border-radius: 2.4mm; background: var(--teal); color: #fff; font-family: "Kufi", sans-serif; font-weight: 700; font-size: 10pt; display: flex; align-items: center; justify-content: center; margin-top: 0.6mm; }
.prompt { flex: 1 1 auto; min-width: 0; white-space: pre-line; font-weight: 600; font-size: 11.6pt; }
.level { flex: none; margin-top: 1mm; }
.opts { list-style: none; margin: 2mm 0 0; padding: 0 11.7mm 0 0; display: grid; gap: 1.4mm 7mm; }
.opts.two { grid-template-columns: 1fr 1fr; }
.opts li { display: flex; gap: 2.4mm; align-items: baseline; break-inside: avoid; }
.opts .l { flex: none; width: 5.6mm; height: 5.6mm; border-radius: 50%; border: 0.9pt solid var(--teal-line); color: var(--teal); font-family: "Kufi", sans-serif; font-weight: 700; font-size: 8.4pt; display: inline-flex; align-items: center; justify-content: center; position: relative; top: 0.5mm; }
.opts .t { white-space: pre-line; }

/* the answer key */
.key .grid-title { font-family: "Kufi", sans-serif; font-size: 9.5pt; font-weight: 700; color: var(--teal); margin: 4mm 0 1.5mm; }
.grid { width: 100%; border-collapse: separate; border-spacing: 1.6mm; table-layout: fixed; margin: 0 -1.6mm; }
.grid td { padding: 1.1mm 0; border-radius: 3pt; background: var(--card); border: 0.7pt solid var(--line); text-align: center; white-space: nowrap; }
.grid td.empty { background: transparent; border-color: transparent; }
.grid .n { font-family: "Kufi", sans-serif; font-size: 8pt; color: #8d8577; }
.grid .a { font-family: "Kufi", sans-serif; font-size: 10pt; font-weight: 700; color: var(--teal); margin-inline-start: 1.4mm; }
.why h3 { font-family: "Kufi", sans-serif; font-size: 10pt; color: var(--teal); margin: 4mm 0 1.5mm; break-after: avoid; }
.why ol { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 8mm; column-rule: 0.6pt solid var(--line); }
.why li { break-inside: avoid; font-size: 9.4pt; line-height: 1.75; padding: 1.2mm 0; border-bottom: 0.5pt dotted #ddd3c2; }
.why li b { font-family: "Kufi", sans-serif; color: var(--teal); font-size: 8.6pt; }
.why li .ans { font-weight: 700; }
"""


def load_questions():
    items = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    by_section = {key: [q for q in items if q["section"] == key] for key, *_ in SECTIONS}
    assert sum(map(len, by_section.values())) == len(items) == 100, "need exactly 100 questions in the five sections"
    return by_section


def question_html(number, q):
    options = q["options"]
    short = all(len(o) <= 28 and "\n" not in o for o in options)
    items = "".join('<li><span class="l">%s</span><span class="t">%s</span></li>' % (LETTERS[i], body_text(o)) for i, o in enumerate(options))
    tag = '<span class="chip %s level">%s</span>' % ("clay" if q["difficulty"] == "hard" else "teal", LEVEL[q["difficulty"]])
    return ('<article class="q"><div class="q-top"><span class="num">%s</span><div class="prompt">%s</div>%s</div>'
            '<ul class="opts%s">%s</ul></article>') % (ar(number), body_text(q["prompt"]), tag, " two" if short else "", items)


def questions_document(by_section, pages=None):
    """The parts of the questions PDF, in order: [(name, html)]. pages: the first
    page of each section and of the key, once known (for the contents page)."""
    pages = pages or {}
    numbering = {}  # question id -> its number in the PDF (1..100, through the whole book)
    n = 0
    for key, *_ in SECTIONS:
        for q in by_section[key]:
            n += 1
            numbering[q["id"]] = n
    medium = sum(q["difficulty"] == "medium" for qs in by_section.values() for q in qs)
    cover = """
<section class="cover"><div class="frame"><div class="frame-in">
  <div class="top">اللغة العربية · الصف الثالث الثانوي</div>
  <div class="star"><span></span></div>
  <h1>%s</h1>
  <div class="rule"></div>
  <div class="unit">الوحدة الثالثة: النواسخ</div>
  <div class="parts">كان وأخواتها · أفعال المقاربة والرجاء والشروع · إنّ وأخواتها · لا النافية للجنس</div>
  <div class="facts">
    <div class="fact"><b>%s</b><span>سؤال اختيار من متعدد</span></div>
    <div class="fact"><b>%s</b><span>أقسام منظّمة</span></div>
    <div class="fact"><b>متوسط وصعب</b><span>مستويات الأسئلة</span></div>
  </div>
  <div class="foot">وفق كتاب «اللغة العربية» للصف الثالث الثانوي — وزارة التربية والتعليم، العام الدراسي ٢٠٢٦/٢٠٢٧<br>
  مع مفتاح إجابات كامل وتعليل مختصر لكل إجابة<br><span class="site">%s</span></div>
</div></div></section>""" % (text(TITLE).replace(" – ", "<br>– ", 1), ar(100), ar(len(SECTIONS)), SITE_NAME)
    rows = []
    for key, no, name, _ in SECTIONS:
        rows.append('<div class="row"><span class="no">%s</span><span class="name">%s</span><span class="count">%s</span><span class="pg">%s</span></div>'
                    % (no, name, how_many(len(by_section[key])), ar(pages[key]) if pages.get(key) else ""))
    rows.append('<div class="row"><span class="no">في الختام</span><span class="name">مفتاح الإجابات وتعليلها</span><span class="count"></span><span class="pg">%s</span></div>'
                % (ar(pages["key"]) if pages.get("key") else ""))
    intro = """
<section class="intro">
  <h2>محتوى الكراسة</h2>
  <div class="rule"></div>
  <div class="toc">%s</div>
  <div class="howto">
    <h3>قبل أن تبدأ</h3>
    <ul>
      <li>الأسئلة كلها من الوحدة الثالثة «النواسخ» في كتاب الوزارة، ومستواها متوسط وصعب.</li>
      <li>اقرأ الجملة كاملة قبل الاختيار، وحدّد الناسخ واسمه وخبره أولًا، ثم انظر إلى موقع الكلمة المسؤول عنها.</li>
      <li>اختر إجابة واحدة لكل سؤال، ثم راجع إجاباتك من مفتاح الإجابات في آخر الكراسة، واقرأ تعليل ما أخطأت فيه.</li>
    </ul>
    <div class="legend">مستوى السؤال: <span class="chip teal">متوسط</span> %s <span class="chip clay">صعب</span> %s</div>
  </div>
</section>""" % ("".join(rows), how_many(medium), how_many(100 - medium))
    sections = []
    for key, no, name, desc in SECTIONS:
        qs = by_section[key]
        m = sum(q["difficulty"] == "medium" for q in qs)
        chips = '<span class="chip gold">%s</span><span class="chip teal">متوسط: %s</span><span class="chip clay">صعب: %s</span>' % (
            how_many(len(qs)), ar(m), ar(len(qs) - m))
        body = "".join(question_html(numbering[q["id"]], q) for q in qs)
        sections.append('<section class="section"><header class="opener"><div class="no">%s</div><h2>%s</h2><p>%s</p><div class="chips">%s</div></header>%s</section>'
                        % (no, name, desc, chips, body))
    # answer key: the grid, then the reasons
    grids = []
    reasons = []
    for key, no, name, _ in SECTIONS:
        cells = []
        items = []
        for q in by_section[key]:
            k = numbering[q["id"]]
            letter = LETTERS[q["options"].index(q["answer"])]
            cells.append('<td><span class="n">%s</span><span class="a">%s</span></td>' % (ar(k), letter))
            items.append('<li><b>%s</b> <span class="ans">(%s) %s</span> — %s</li>' % (ar(k), letter, body_text(q["answer"]), body_text(q["explanation"])))
        cells += ['<td class="empty"></td>'] * (-len(cells) % 10)
        table = "".join("<tr>%s</tr>" % "".join(cells[i:i + 10]) for i in range(0, len(cells), 10))
        grids.append('<div class="grid-title">%s: %s</div><table class="grid">%s</table>' % (no, name, table))
        reasons.append('<h3>%s: %s</h3><ol>%s</ol>' % (no, name, "".join(items)))
    key_html = ('<section class="section key"><header class="opener"><div class="no">في الختام</div><h2>مفتاح الإجابات</h2>'
                '<p>رقم السؤال وحرف الإجابة الصحيحة، ثم تعليل مختصر لكل إجابة في الصفحات التالية.</p></header>%s</section>' % "".join(grids))
    why_html = ('<section class="section why"><header class="opener"><div class="no">مفتاح الإجابات</div><h2>تعليل الإجابات</h2></header>%s</section>'
                % "".join(reasons))
    return [("cover", cover), ("intro", intro)] + list(zip([key for key, *_ in SECTIONS], sections)) + [("key", key_html), ("why", why_html)]


def questions_html(parts, whole=True):
    """The HTML of the questions PDF from its parts (whole=False: some parts on
    their own, without the cover's page style, to count their pages)."""
    return """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><base href="__BASE__"><title>%s</title>
<style>%s%s%s</style></head><body>%s</body></html>""" % (
        text(TITLE), BASE_CSS, page_css("١٠٠ سؤال على الوحدة الثالثة «النواسخ» — اللغة العربية للصف الثالث الثانوي", first_blank=whole),
        QUESTIONS_CSS, "".join(html_part for _, html_part in parts))


# ---------------------------------------------------------------- the summary PDF

SUMMARY_CSS = """
@page { margin: 14mm 13mm 14mm; @top-center { content: none; } }
body { font-size: 9.7pt; line-height: 1.68; }
.s-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 6mm; padding-bottom: 2.4mm; margin-bottom: 3.4mm; border-bottom: 1.2pt solid var(--gold); }
.s-head .kicker { font-family: "Kufi", sans-serif; font-size: 8.5pt; font-weight: 600; color: var(--teal); }
.s-head h1 { font-family: "Amiri", serif; font-size: 23pt; line-height: 1.35; }
.s-head .meta { text-align: left; font-size: 8.2pt; color: var(--muted); line-height: 1.6; }
.s-head .meta .site { font-family: "Kufi", sans-serif; direction: ltr; unicode-bidi: isolate; }
.page + .page { break-before: page; }
.lead { margin: 0 0 2mm; }
.map { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2.4mm; margin-bottom: 3.6mm; }
.map div { padding: 2.2mm 3mm 2mm; border-radius: 6pt; background: var(--teal-soft); border: 0.8pt solid var(--teal-line); line-height: 1.55; }
.map b { display: block; font-family: "Kufi", sans-serif; font-size: 9pt; color: var(--teal); margin-bottom: 0.6mm; }
.map span { display: block; font-size: 8.8pt; }
.map i { display: block; font-style: normal; font-size: 8.4pt; color: var(--muted); margin-top: 0.6mm; }
.pcols { display: flex; gap: 4.5mm; align-items: flex-start; }
.pcol { flex: 1 1 0; min-width: 0; }
.box { break-inside: avoid; margin: 0 0 3.4mm; padding: 2.6mm 3.8mm 2.2mm; border-radius: 6pt; background: var(--card); border: 0.8pt solid var(--line); }
.box h2 { display: flex; align-items: center; gap: 2mm; font-family: "Kufi", sans-serif; font-size: 10.3pt; color: var(--teal); margin-bottom: 1.2mm; }
.box h2 .no { flex: none; width: 5.6mm; height: 5.6mm; border-radius: 1.8mm; background: var(--teal); color: #fff; font-size: 8pt; display: inline-flex; align-items: center; justify-content: center; }
.box p { margin: 0.8mm 0; }
.box ul { margin: 0.5mm 0; padding-inline-start: 4.5mm; }
.box li { margin: 0.35mm 0; }
.box b, .box strong { color: #1f4f53; }
.ex { color: #5b4a2c; }
.tbl { width: 100%; border-collapse: collapse; margin: 1mm 0 0.8mm; font-size: 9pt; line-height: 1.5; }
.tbl th { background: var(--teal-soft); color: var(--teal); font-family: "Kufi", sans-serif; font-weight: 700; font-size: 8.2pt; padding: 1.2mm 1.6mm; text-align: right; }
.tbl td { padding: 0.8mm 1.6mm; border-bottom: 0.6pt solid var(--line); vertical-align: top; }
.tbl tr:last-child td { border-bottom: 0; }
.note { margin-top: 1.4mm; padding: 1.6mm 2.6mm; border-radius: 4pt; background: var(--gold-soft); font-size: 9.2pt; }
.cmp td:first-child { font-family: "Kufi", sans-serif; font-size: 8.2pt; font-weight: 600; color: var(--teal); white-space: nowrap; }
.cmp th small { font-family: "Naskh", serif; font-weight: 400; color: var(--muted); font-size: 7.8pt; }

.traps { border-color: var(--clay-line); background: #fdf6f1; }
.traps h2 { color: var(--clay); }
.traps h2 .no { background: var(--clay); }
.traps li::marker { color: var(--clay); }
.s-foot { margin-top: 2mm; text-align: center; font-size: 8pt; color: #8d8577; }
"""


def summary_document():
    body = (HERE / "summary.html").read_text(encoding="utf-8")
    body = QURAN.sub(lambda m: '<span class="quran">%s</span>' % m.group(0), body)
    return """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><base href="__BASE__"><title>ملخص الوحدة الثالثة: النواسخ — اللغة العربية</title>
<style>%s%s%s</style></head><body>%s</body></html>""" % (BASE_CSS, page_css("", first_blank=False), SUMMARY_CSS, body)


# ---------------------------------------------------------------- printing

def page_count(path):
    return len(PdfReader(str(path)).pages)


def main():
    by_section = load_questions()
    server, base = serve(SITE)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            def make(source, name):
                page.set_content(source.replace("__BASE__", base, 1), wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(SITE / name), prefer_css_page_size=True, print_background=True)

            # Each section starts on a new page, so printing each part on its own gives
            # its number of pages, and from those the page where each section begins.
            parts = questions_document(by_section)
            scratch = SITE / ".question-part.pdf"
            counts = {}
            for name, part in parts:
                make(questions_html([(name, part)], whole=name == "cover"), scratch.name)
                counts[name] = page_count(scratch)
            scratch.unlink()
            assert counts["cover"] == 1 and counts["intro"] == 1, counts
            pages, at = {}, 1
            for name, _ in parts:
                pages[name] = at
                at += counts[name]
            make(questions_html(questions_document(by_section, pages)), QUESTIONS_PDF)
            total = page_count(SITE / QUESTIONS_PDF)
            assert total == at - 1, "the whole PDF has %d pages, the parts %d" % (total, at - 1)
            print("written:", QUESTIONS_PDF, total, "pages; parts start on", pages)
            make(summary_document(), SUMMARY_PDF)
            print("written:", SUMMARY_PDF, page_count(SITE / SUMMARY_PDF), "pages")
            browser.close()
    finally:
        server.shutdown()
    # what the PDFs were made from (tests/schema.test.js fails when they are older than their sources)
    source = (HERE / "questions.json").read_bytes() + b"\x00" + (HERE / "summary.html").read_bytes()
    (HERE / "built.json").write_text(json.dumps({"questions_pdf": QUESTIONS_PDF, "summary_pdf": SUMMARY_PDF,
                                                 "fingerprint": hashlib.sha256(source).hexdigest()[:16]}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
