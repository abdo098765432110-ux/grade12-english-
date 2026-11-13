"""Biology revision booklet, Chapters 1 and 2 (development tool).

Makes biology-ch1-ch2-revision-booklet.pdf: a colourful A4 revision notebook in a
handwriting style, at most 20 pages, from
  content/ch1.html   الفصل الأول: الدعامة والحركة في الكائنات الحية
  content/ch2.html   الفصل الثاني: التنسيق الهرموني في الكائنات الحية
  content/ch3.html   questions on the diagrams and questions linking the two chapters
  content/defs.svg   arrow heads used by the drawings
  style.css          the notebook look; sketch.js draws the outlines by hand;
                     paginate.js flows the blocks into A4 pages
The text follows the Ministry of Education's 2026 Grade 12 Biology book
(pages 7–20 and 25–36). The only note labels are «ركز هنا!», «خد بالك!» and
«فخ امتحان!»; every question has its answer under the heading "Answer".

Fonts (SIL Open Font License, in fonts/): Aref Ruqaa (headings), Playpen Sans
Arabic (text), Marhey (note labels), Caveat (Latin words). The variable fonts are
cut into fixed weights at build time, so the PDF embeds real fonts (small file,
searchable text) instead of drawn glyphs.

Run from the website folder:
    python3 tools/bio_revision_booklet/build.py [--previews DIR]
Needs Playwright (Chromium), fontTools and pypdf."""
import json
import pathlib
import shutil
import sys
import tempfile

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent
PDF = SITE / "biology-ch1-ch2-revision-booklet.pdf"
MAX_PAGES = 20
CHAPTERS = {
    "1": "الفصل الأول: الدعامة والحركة في الكائنات الحية",
    "2": "الفصل الثاني: التنسيق الهرموني في الكائنات الحية",
    "3": "أسئلة على الرسومات وأسئلة تربط الفصلين",
}
# (variable font, family used in style.css, weights)
INSTANCES = [("PlaypenSansArabic[wght].ttf", "Pen", [400, 500, 600, 650, 700]),
             ("Caveat[wght].ttf", "Hand", [700]),
             ("Marhey[wght].ttf", "Marker", [700])]


def fonts(into):
    into.mkdir()
    for name in ("ArefRuqaa-Regular.ttf", "ArefRuqaa-Bold.ttf"):
        shutil.copy(HERE / "fonts" / name, into / name)
    for source, family, weights in INSTANCES:
        for weight in weights:
            instancer.instantiateVariableFont(TTFont(HERE / "fonts" / source), {"wght": weight}).save(into / ("%s-%d.ttf" % (family, weight)))


def page_html():
    sources = []
    for ch in ("1", "2", "3"):
        text = (HERE / "content" / ("ch%s.html" % ch)).read_text(encoding="utf-8")
        cont = ' data-continue="1"' if ch == "3" else ""   # the last questions go on after Chapter 2
        sources.append('<div class="src" data-ch="%s"%s>%s</div>' % (ch, cont, text))
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<title>مذكرة مراجعة الأحياء – الفصلان الأول والثاني</title>'
            '<link rel="stylesheet" href="style.css"></head><body>'
            + (HERE / "content" / "defs.svg").read_text(encoding="utf-8")
            + '<div id="srcs">' + "\n".join(sources) + '</div>'
            + '<script>window.CHAPTERS = %s;</script>' % json.dumps(CHAPTERS, ensure_ascii=False)
            + '<script src="sketch.js"></script><script src="paginate.js"></script></body></html>')


def main():
    previews = None
    if "--previews" in sys.argv:
        previews = pathlib.Path(sys.argv[sys.argv.index("--previews") + 1])
        previews.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        fonts(work / "f")
        for name in ("style.css", "sketch.js", "paginate.js"):
            shutil.copy(HERE / name, work / name)
        (work / "booklet.html").write_text(page_html(), encoding="utf-8")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 820, "height": 1200})
            page.goto((work / "booklet.html").as_uri())
            page.wait_for_function("window.BOOK_DONE === true", timeout=60000)
            info = page.evaluate("window.PAGINATE")
            problems = list(info["warnings"])
            report = page.evaluate("""() => [...document.querySelectorAll('.page')].map((p, i) => {
                const s = p.querySelector('.sheet'), r = s.getBoundingClientRect();
                let bottom = 0, left = 1e9;
                s.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect(); if (b.height > 0) { bottom = Math.max(bottom, b.bottom); left = Math.min(left, b.left); } });
                return {page: i + 1, over: Math.round(bottom - r.bottom), left: Math.round(r.left - left)};
            })""")
            for r in report:
                if r["over"] > 0 or r["left"] > 2:
                    problems.append("page %d: content outside the page (%s)" % (r["page"], r))
            if previews:
                for i in range(1, info["pages"] + 1):
                    page.locator("#p%d" % i).screenshot(path=str(previews / ("p%02d.png" % i)))
            page.pdf(path=str(PDF), prefer_css_page_size=True, print_background=True)
            browser.close()
    pages = len(PdfReader(str(PDF)).pages)
    if pages > MAX_PAGES:
        problems.append("%d pages (at most %d)" % (pages, MAX_PAGES))
    for problem in problems:
        print("PROBLEM:", problem)
    print("written: %s (%d pages, %d KB)" % (PDF.name, pages, PDF.stat().st_size // 1024))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
