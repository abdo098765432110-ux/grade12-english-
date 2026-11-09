"""Biology Chapter 2 «التنسيق الهرموني في الكائنات الحية»: 50 essay questions and
50 questions on pictures, with model answers (development tool).

Makes, from essay.py and figs1.py–figs3.py:
  bio-ch2-img01.png … bio-ch2-img50.png   the 50 pictures (drawn as SVG, saved twice
                                           their size so they stay sharp on phones)
  biology-questions.json                  the two sections «الأسئلة المقالية» and
                                           «أسئلة على الصور» in Chapter 2 (the other
                                           sections are not touched)
  biology-ch2-essay-image-questions.pdf   all 100 questions, then the model answers
  tools/bio_ch2_bank/built.json           what the PDF was made from (checked by the tests)

Run from the website folder:
    python3 tools/bio_ch2_bank/build.py
Needs Playwright (Chromium), Pillow and pypdf."""
import hashlib
import io
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent
sys.path.insert(0, str(HERE))

from essay import ESSAY            # noqa: E402
from images import IMAGES          # noqa: E402
import render                      # noqa: E402

DATA = SITE / "biology-questions.json"
PDF = "biology-ch2-essay-image-questions.pdf"
IMG = "bio-ch2-img%02d.png"
ESSAY_ID, IMAGE_ID = "chapter-2-essay", "chapter-2-images"
ESSAY_TITLE = "الأسئلة المقالية – 50 سؤالًا"
IMAGE_TITLE = "أسئلة على الصور – 50 سؤالًا"
PDF_TITLE = "100 سؤال مقالي وعلى الصور مع الإجابات النموذجية"
OLD_PDF_TITLE = "أسئلة الاختيار من متعدد (سهلة – متوسطة – صعبة جدًا) مع إجاباتها"
LRI, PDI = "⁦", "⁩"


# ------------------------------------------------------------------ text
def isolate(text):
    """Latin letters and digits inside Arabic text are wrapped in direction marks
    (as in the rest of biology-questions.json), so «FSH وLH» or «80–120» keep their order."""
    text = text.replace(LRI, "").replace(PDI, "")
    run = r"[A-Za-z0-9][A-Za-z0-9.,/–\-+×₂³⁺]*(?: [A-Za-z0-9][A-Za-z0-9.,/–\-+×₂³⁺]*)*"
    return re.sub(run, lambda m: LRI + m.group(0) + PDI, text)


def questions():
    essay, image = [], []
    for i, (diff, prompt, answer) in enumerate(ESSAY, 1):
        essay.append({"id": "bio-ch2-es%02d" % i, "type": "short", "lang": "ar", "prompt": isolate(prompt.strip()),
                      "modelAnswer": isolate(answer.strip()), "difficulty": diff, "reviewStatus": "reviewed"})
    for i, q in enumerate(IMAGES, 1):
        image.append({"id": "bio-ch2-im%02d" % i, "type": "short", "lang": "ar", "prompt": isolate(q["prompt"].strip()),
                      "image": IMG % i, "imageAlt": isolate(q["alt"].strip()), "modelAnswer": isolate(q["answer"].strip()),
                      "difficulty": q["diff"], "reviewStatus": "reviewed"})
    return essay, image


# ------------------------------------------------------------------ the data file
def update_data(essay, image):
    raw = DATA.read_text(encoding="utf-8")
    data = json.loads(raw)
    chapter = next(c for c in data["chapters"] if c["id"] == "chapter-2")
    keep = [s for s in chapter["sections"] if s["id"] not in (ESSAY_ID, IMAGE_ID)]
    chapter["sections"] = keep + [
        {"id": ESSAY_ID, "title": ESSAY_TITLE, "questions": essay},
        {"id": IMAGE_ID, "title": IMAGE_TITLE, "questions": image},
    ]
    chapter["pdfTitle"] = OLD_PDF_TITLE
    chapter["morePdfs"] = [{"file": PDF, "title": PDF_TITLE, "sections": [ESSAY_ID, IMAGE_ID]}]
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: biology-questions.json (Chapter 2: %d + %d questions added)" % (len(essay), len(image)))


# ------------------------------------------------------------------ the pictures
def make_pictures():
    from PIL import Image
    figs = [("bio-ch2-img%02d" % i, q["draw"]().svg()) for i, q in enumerate(IMAGES, 1)]
    render.render(figs, SITE, scale=2)
    total = 0
    for name, _ in figs:
        path = SITE / (name + ".png")
        im = Image.open(path).convert("RGB")
        q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        pal = q.getpalette()[:768]
        # the colour nearest to white becomes exact white (the page background)
        best = min(range(256), key=lambda k: sum(255 - c for c in pal[3 * k:3 * k + 3]))
        pal[3 * best:3 * best + 3] = [255, 255, 255]
        q.putpalette(pal)
        q.save(path, optimize=True)
        total += path.stat().st_size
    print("written: %d pictures, %d KB in all" % (len(figs), total // 1024))
    return figs


# ------------------------------------------------------------------ the PDF
CSS = """
@font-face { font-family: "Cairo"; src: url("__BASE__tools/fonts/Cairo.ttf") format("truetype"); font-weight: 200 1000; font-style: oblique -11deg 11deg; }
@page { size: A4; margin: 17mm 15mm 19mm;
  @bottom-center { content: "صفحة " counter(page) " من " counter(pages); font-family: "Cairo"; font-size: 9pt; font-weight: 700; color: #7c3aed; }
  @bottom-right { content: "الأحياء • الفصل الثاني"; font-family: "Cairo"; font-size: 8.5pt; color: #94a3b8; }
  @bottom-left { content: "Learn for Grade 12"; font-family: "Cairo"; font-size: 8.5pt; color: #94a3b8; } }
@page cover { margin: 0; @bottom-center { content: none; } @bottom-right { content: none; } @bottom-left { content: none; } }
* { box-sizing: border-box; }
html { direction: rtl; }
body { margin: 0; font-family: "Cairo", sans-serif; color: #1f2a44; font-size: 11.2pt; line-height: 1.75; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slant { font-style: oblique 9deg; }
.cover { page: cover; width: 210mm; height: 297mm; position: relative; overflow: hidden; color: #fff;
  background: linear-gradient(140deg, #4c1d95 0%, #7c3aed 34%, #db2777 70%, #f97316 100%); }
.cover svg.deco { position: absolute; inset: 0; width: 210mm; height: 297mm; }
.cover .inner { position: absolute; inset: 26mm 20mm 22mm; display: flex; flex-direction: column; }
.cover .kicker { display: inline-block; align-self: flex-start; background: rgba(255,255,255,.18); border: 1.5px solid rgba(255,255,255,.55);
  border-radius: 99px; padding: 2mm 6mm; font-weight: 800; font-size: 12.5pt; }
.cover h1 { font-size: 44pt; line-height: 1.25; margin: 14mm 0 2mm; font-weight: 900; text-shadow: 0 2.5mm 6mm rgba(40,0,70,.45); }
.cover h2 { font-size: 21pt; line-height: 1.5; margin: 0 0 10mm; font-weight: 800; color: #fde68a; text-shadow: 0 1.5mm 4mm rgba(40,0,70,.35); }
.cover .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; margin-top: 4mm; }
.cover .stat { background: rgba(255,255,255,.95); color: #1f2a44; border-radius: 6mm; padding: 5mm 6mm; box-shadow: 0 3mm 8mm rgba(40,0,70,.25); }
.cover .stat b { display: block; font-size: 25pt; line-height: 1.2; font-weight: 900; }
.cover .stat span { font-weight: 700; font-size: 12pt; }
.cover .s1 b { color: #7c3aed; } .cover .s2 b { color: #0d9488; } .cover .s3 b { color: #db2777; } .cover .s4 b { color: #ea580c; }
.cover .art { margin: 9mm auto 0; width: 74mm; height: 88mm; background: rgba(255,255,255,.93); border-radius: 50% 50% 8mm 8mm; padding: 5mm 4mm 2mm; text-align: center;
  box-shadow: 0 3mm 9mm rgba(40,0,70,.3); }
.cover .art svg { width: 100%; height: 72mm; display: block; }
.cover .art p { margin: 1mm 0 0; color: #6d28d9; font-weight: 800; font-size: 10.5pt; }
.cover .foot { margin-top: auto; font-weight: 800; font-size: 13pt; display: flex; justify-content: space-between; }
.guide h2, .part-head h2 { margin: 0; }
.guide { page-break-before: always; }
.guide .box { border-radius: 6mm; padding: 6mm 7mm; margin-bottom: 6mm; }
.guide .contents { background: linear-gradient(135deg, #ede9fe, #fce7f3); border: 2px solid #c4b5fd; }
.guide .how { background: linear-gradient(135deg, #ccfbf1, #e0f2fe); border: 2px solid #5eead4; }
.guide h2 { font-size: 20pt; font-weight: 900; color: #6d28d9; margin-bottom: 3mm; text-shadow: 0 .8mm 1.6mm rgba(109,40,217,.18); }
.guide .how h2 { color: #0f766e; text-shadow: 0 .8mm 1.6mm rgba(15,118,110,.18); }
.guide table { width: 100%; border-collapse: collapse; font-size: 12pt; }
.guide td { padding: 2.2mm 2mm; border-bottom: 1.5px dashed rgba(109,40,217,.25); font-weight: 700; }
.guide td.n { text-align: left; color: #6d28d9; font-weight: 900; width: 26mm; }
.guide td .dot { display: inline-block; width: 4mm; height: 4mm; border-radius: 50%; margin-left: 2.5mm; vertical-align: middle; }
.guide ul { margin: 0; padding-right: 6mm; }
.guide li { margin: 1.2mm 0; }
.part { page-break-before: always; }
.part-head { border-radius: 6mm; padding: 6mm 8mm 5mm; color: #fff; margin-bottom: 6mm; position: relative; overflow: hidden; }
.part-head h2 { font-size: 23pt; font-weight: 900; line-height: 1.35; text-shadow: 0 1.2mm 2.5mm rgba(0,0,0,.28); }
.part-head p { margin: 1mm 0 0; font-weight: 700; font-size: 11.5pt; opacity: .95; }
.part-head .num { position: absolute; left: 7mm; top: 3mm; font-size: 46pt; font-weight: 900; opacity: .22; }
.essay .part-head { background: linear-gradient(120deg, #6d28d9, #db2777); }
.images .part-head { background: linear-gradient(120deg, #0f766e, #2563eb); }
.answers .part-head { background: linear-gradient(120deg, #ea580c, #db2777); }
.q { break-inside: avoid; border-radius: 4.5mm; padding: 3.6mm 5mm 3.6mm; margin: 0 0 4.2mm; background: #fff; position: relative; }
.essay .q { border: 1.6px solid #ddd6fe; border-right: 2.4mm solid #8b5cf6; background: linear-gradient(90deg, #fff 70%, #faf5ff); }
.essay .q:nth-child(even) { border-color: #fbcfe8; border-right-color: #ec4899; background: linear-gradient(90deg, #fff 70%, #fdf2f8); }
.images .q { border: 1.6px solid #99f6e4; border-right: 2.4mm solid #14b8a6; background: linear-gradient(90deg, #fff 70%, #f0fdfa); }
.images .q:nth-child(even) { border-color: #bfdbfe; border-right-color: #3b82f6; background: linear-gradient(90deg, #fff 70%, #eff6ff); }
.qhead { display: flex; align-items: center; gap: 3mm; margin-bottom: 1.4mm; }
.badge { flex: none; width: 10mm; height: 10mm; border-radius: 50%; color: #fff; font-weight: 900; font-size: 12.5pt; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #7c3aed, #db2777); box-shadow: 0 .8mm 1.6mm rgba(124,58,237,.35); }
.images .badge { background: linear-gradient(135deg, #0d9488, #2563eb); box-shadow: 0 .8mm 1.6mm rgba(13,148,136,.35); }
.pill { font-size: 9pt; font-weight: 800; border-radius: 99px; padding: .3mm 3.2mm; }
.pill.hard { background: #ffedd5; color: #c2410c; border: 1.2px solid #fdba74; }
.pill.very-hard { background: #fce7f3; color: #be185d; border: 1.2px solid #f9a8d4; }
.prompt { margin: 0; font-weight: 600; }
.lines { margin-top: 2.2mm; }
.lines div { height: 6.8mm; border-bottom: 1.3px dotted #c4b5fd; }
figure { margin: 2mm 0 0; text-align: center; background: #fff; border: 1.4px solid #e2e8f0; border-radius: 3.5mm; padding: 2.5mm; }
figure svg { width: 100%; height: auto; max-height: 128mm; display: block; margin: 0 auto; }
.images .q + .q { break-before: page; }
.images .lines div { height: 7.4mm; }
.answers .cols { columns: 2; column-gap: 5mm; }
.answers .q { display: flex; gap: 2.6mm; align-items: flex-start; border: 1.3px solid #fed7aa; border-right: 2mm solid #f97316; background: #fffaf5; padding: 2.4mm 3.4mm; margin-bottom: 3mm; font-size: 9.6pt; line-height: 1.62; }
.answers .q:nth-child(even) { border-color: #fbcfe8; border-right-color: #ec4899; background: #fff7fb; }
.answers .badge { width: 7.5mm; height: 7.5mm; font-size: 10pt; background: linear-gradient(135deg, #f97316, #db2777); }
.answers .ans { white-space: pre-line; margin: 0; }
.answers h3 { font-size: 15pt; font-weight: 900; margin: 5mm 0 3mm; color: #be185d; text-shadow: 0 .6mm 1.2mm rgba(190,24,93,.18); }
.answers h3.first { margin-top: 0; }
"""

DECO = """<svg class="deco" viewBox="0 0 210 297" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="190" cy="40" r="46" fill="#fff" fill-opacity=".09"/><circle cx="18" cy="250" r="60" fill="#fff" fill-opacity=".08"/>
<circle cx="170" cy="230" r="22" fill="#fde68a" fill-opacity=".25"/><circle cx="34" cy="70" r="9" fill="#fff" fill-opacity=".22"/>
<g fill="none" stroke="#fff" stroke-opacity=".35" stroke-width=".8">
<polygon points="150,120 163,112.5 176,120 176,135 163,142.5 150,135"/><polygon points="176,135 189,127.5 202,135 202,150 189,157.5 176,150"/>
<polygon points="163,142.5 176,150 176,165 163,172.5 150,165 150,150"/></g>
<g fill="#fff" fill-opacity=".9"><circle cx="163" cy="112.5" r="1.6"/><circle cx="202" cy="150" r="1.6"/><circle cx="150" cy="165" r="1.6"/></g>
<path d="M0 205 C 50 190 90 230 140 214 C 170 205 190 190 210 196 L210 297 L0 297 Z" fill="#fff" fill-opacity=".08"/>
</svg>"""


def html_text(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pill(diff):
    return '<span class="pill %s">%s</span>' % (diff, "صعب جدًّا" if diff == "very-hard" else "صعب")


def art():
    """The body with its endocrine glands (the picture of question 6 without its numbers)."""
    from figs1 import fig06
    return fig06(labels=False).svg().replace('<rect width="620" height="760" fill="#ffffff"/>', "")


def cover():
    return ('<section class="cover">' + DECO + '<div class="inner">'
            '<span class="kicker">الأحياء • الصف الثالث الثانوي</span>'
            '<h1 class="slant">بنك أسئلة<br>الفصل الثاني</h1>'
            '<h2 class="slant">التنسيق الهرموني في الكائنات الحية</h2>'
            '<div class="stats">'
            '<div class="stat s1"><b>50</b><span>سؤالًا مقاليًّا</span></div>'
            '<div class="stat s2"><b>50</b><span>سؤالًا على الصور والرسوم</span></div>'
            '<div class="stat s3"><b>100</b><span>إجابة نموذجية في آخر الملف</span></div>'
            '<div class="stat s4"><b>صعب</b><span>وصعب جدًّا فقط</span></div>'
            '</div>'
            '<div class="art">' + art() + '<p>الغدد الصماء في جسم الإنسان</p></div>'
            '<div class="foot"><span>وفق كتاب الوزارة</span><span dir="ltr">Learn for Grade 12</span></div>'
            '</div></section>')


def guide(pages):
    rows = [("#8b5cf6", "القسم الأول: الأسئلة المقالية (50 سؤالًا)", pages["essay"]),
            ("#14b8a6", "القسم الثاني: أسئلة على الصور (50 سؤالًا)", pages["images"]),
            ("#f97316", "الإجابات النموذجية للقسمين", pages["answers"])]
    body = "".join('<tr><td><span class="dot" style="background:%s"></span>%s</td><td class="n">صفحة %d</td></tr>' % r for r in rows)
    return ('<section class="guide"><div class="box contents"><h2 class="slant">محتويات الملف</h2><table>' + body + '</table></div>'
            '<div class="box how"><h2 class="slant">كيف تستفيد من هذا الملف؟</h2><ul>'
            '<li>كل الأسئلة من الفصل الثاني فقط، بمستوى «صعب» و«صعب جدًّا»، ومكتوبة بمصطلحات الكتاب.</li>'
            '<li>حاول الإجابة كتابةً أولًا في المساحة المخصصة، ثم قارن إجابتك بالإجابة النموذجية في آخر الملف.</li>'
            '<li>في أسئلة الصور: افحص الرسم جيدًا، فالأرقام والحروف عليه هي مفتاح الإجابة.</li>'
            '<li>الأسئلة نفسها موجودة على الموقع في قسمي «الأسئلة المقالية» و«أسئلة على الصور» داخل الفصل الثاني.</li>'
            '</ul></div></section>')


def part_essay():
    cards = []
    for i, (diff, prompt, _) in enumerate(ESSAY, 1):
        cards.append('<div class="q"><div class="qhead"><span class="badge">%d</span>%s</div><p class="prompt">%s</p>'
                     '<div class="lines"><div></div><div></div><div></div></div></div>' % (i, pill(diff), html_text(prompt.strip())))
    return ('<section class="part essay"><div class="part-head"><span class="num">1</span><h2 class="slant">القسم الأول: الأسئلة المقالية</h2>'
            '<p>50 سؤالًا: فسّر – علّل – قارن – ماذا يحدث لو – توقّع – ما العلاقة</p></div>' + "".join(cards) + "</section>")


def part_images(figs):
    cards = []
    for i, (q, (_, svg)) in enumerate(zip(IMAGES, figs), 1):
        cards.append('<div class="q"><div class="qhead"><span class="badge">%d</span>%s</div><p class="prompt">%s</p><figure>%s</figure>'
                     '<div class="lines"><div></div><div></div><div></div><div></div><div></div></div></div>'
                     % (i, pill(q["diff"]), html_text(q["prompt"].strip()), svg))
    return ('<section class="part images"><div class="part-head"><span class="num">2</span><h2 class="slant">القسم الثاني: أسئلة على الصور</h2>'
            '<p>50 سؤالًا: افحص الرسم، ثم أجب</p></div>' + "".join(cards) + "</section>")


def part_answers():
    def block(items, start_title, first):
        out = ['<h3 class="slant%s">%s</h3>' % (" first" if first else "", start_title)]
        for i, ans in enumerate(items, 1):
            out.append('<div class="q"><span class="badge">%d</span><p class="ans">%s</p></div>' % (i, html_text(ans.strip())))
        return out[0] + '<div class="cols">' + "".join(out[1:]) + "</div>"
    return ('<section class="part answers"><div class="part-head"><span class="num">✓</span><h2 class="slant">الإجابات النموذجية</h2>'
            '<p>قارن إجابتك بالنقاط الأساسية في كل إجابة</p></div>'
            + block([a for _, _, a in ESSAY], "إجابات القسم الأول: الأسئلة المقالية", True)
            + block([q["answer"] for q in IMAGES], "إجابات القسم الثاني: أسئلة على الصور", False) + "</section>")


def document(base, body):
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>' + CSS.replace("__BASE__", base)
            + '</style></head><body>' + body + "</body></html>")


def make_pdf(figs):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader
    server, base = render.serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            def pages_of(body):
                page.set_content(document(base, body), wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                return len(PdfReader(io.BytesIO(page.pdf(prefer_css_page_size=True, print_background=True))).pages)

            # each part starts on a new page, so its first page = the pages before it + 1
            essay, images, answers = part_essay(), part_images(figs), part_answers()
            n_front = pages_of(cover() + guide({"essay": 0, "images": 0, "answers": 0}))
            n_essay = pages_of(essay.replace('class="part essay"', 'class="essay"'))
            n_images = pages_of(images.replace('class="part images"', 'class="images"'))
            starts = {"essay": n_front + 1, "images": n_front + n_essay + 1, "answers": n_front + n_essay + n_images + 1}
            body = cover() + guide(starts) + essay + images + answers
            page.set_content(document(base, body), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(SITE / PDF), prefer_css_page_size=True, print_background=True)
            browser.close()
    finally:
        server.shutdown()
    total = len(PdfReader(str(SITE / PDF)).pages)
    print("written: %s (%d pages; parts start on pages %s)" % (PDF, total, starts))
    return total, starts


def fingerprint():
    """Changes when a question, an answer or a picture's source changes (tests/schema.test.js
    works it out the same way from biology-questions.json)."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    chapter = next(c for c in data["chapters"] if c["id"] == "chapter-2")
    digest = hashlib.sha256()
    for s in chapter["sections"]:
        if s["id"] in (ESSAY_ID, IMAGE_ID):
            for q in s["questions"]:
                digest.update(("\x1f".join([q["prompt"], q["modelAnswer"], q.get("image", "")]) + "\x1e").encode("utf-8"))
    return digest.hexdigest()[:16]


def main():
    essay, image = questions()
    figs = make_pictures()
    update_data(essay, image)
    total, starts = make_pdf(figs)
    sources = hashlib.sha256(b"".join((HERE / n).read_bytes() for n in ("essay.py", "figs1.py", "figs2.py", "figs3.py", "figlib.py"))).hexdigest()[:16]
    (HERE / "built.json").write_text(json.dumps({"pdf": PDF, "pages": total, "starts": starts, "questions": 100,
                                                 "fingerprint": fingerprint(), "sources": sources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: tools/bio_ch2_bank/built.json")


if __name__ == "__main__":
    main()
