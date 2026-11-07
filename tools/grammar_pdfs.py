"""Builds the downloadable grammar-summary PDFs (development tool — the website
itself only links to the finished files):

  present-perfect-summary.pdf   from tools/present-perfect-summary.html:
                                Present Perfect & Present Perfect Continuous,
                                two A4 pages (Grammar Summaries).

Run it again whenever the source page changes:
    python3 tools/grammar_pdfs.py
Needs Python with Playwright and Chromium (the same as tests/e2e_test.py) and
the Inter font. With fontTools installed, Inter is converted to TrueType first,
so the PDF embeds ordinary TrueType fonts (crisp in every PDF viewer).
It stops with an error if any page's content does not fit on its A4 page."""
import pathlib
import sys
import tempfile

from playwright.sync_api import sync_playwright

SITE = pathlib.Path(__file__).resolve().parent.parent
DOCUMENTS = [
    (SITE / "tools" / "present-perfect-summary.html", SITE / "present-perfect-summary.pdf", 2),
]
INTER = pathlib.Path("/usr/share/fonts/opentype/inter")
FACES = [  # (family, file, weight, style)
    ("Inter", "Inter-Regular.otf", 400, "normal"), ("Inter", "Inter-Italic.otf", 400, "italic"),
    ("Inter", "Inter-Medium.otf", 500, "normal"), ("Inter", "Inter-SemiBold.otf", 600, "normal"),
    ("Inter", "Inter-SemiBoldItalic.otf", 600, "italic"), ("Inter", "Inter-Bold.otf", 700, "normal"),
    ("Inter", "Inter-BoldItalic.otf", 700, "italic"), ("Inter", "Inter-ExtraBold.otf", 800, "normal"),
    ("Inter Display", "InterDisplay-Medium.otf", 500, "normal"), ("Inter Display", "InterDisplay-Bold.otf", 700, "normal"),
    ("Inter Display", "InterDisplay-ExtraBold.otf", 800, "normal"),
]


def otf_to_ttf(source, target):
    """CFF (.otf) → TrueType (.ttf) outlines, after fontTools' otf2ttf example."""
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont, newTable
    font = TTFont(str(source))
    order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()
    glyphs = {}
    for name in order:
        pen = TTGlyphPen(glyph_set)
        glyph_set[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glyphs[name] = pen.glyph()
    font["loca"] = newTable("loca")
    font["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = order
    glyf.glyphs = glyphs
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    glyf.compile(font)
    hmtx = font["hmtx"]
    for name, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[name] = (hmtx[name][0], glyph.xMin)
    font["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    for field in ("maxZones",):
        setattr(maxp, field, 1)
    for field in ("maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
                  "maxStackElements", "maxSizeOfInstructions"):
        setattr(maxp, field, 0)
    maxp.maxComponentElements = max((len(getattr(g, "components", []) or []) for g in glyf.glyphs.values()), default=0)
    maxp.compile(font)
    post = font["post"]
    post.formatType, post.extraNames, post.mapping, post.glyphOrder = 2.0, [], {}, order
    font.sfntVersion = "\000\001\000\000"
    font.save(str(target))


def truetype_faces(folder):
    """@font-face rules for TrueType copies of Inter, or "" when that is not possible."""
    try:
        import fontTools  # noqa: F401
    except ImportError:
        return ""
    rules = []
    for family, name, weight, style in FACES:
        source = INTER / name
        if not source.exists():
            return ""
        target = pathlib.Path(folder) / (source.stem + ".ttf")
        otf_to_ttf(source, target)
        rules.append('@font-face { font-family: "%s"; src: url("%s") format("truetype"); font-weight: %d; font-style: %s; }'
                     % (family, target.as_uri(), weight, style))
    return "\n".join(rules)


def main():
    with tempfile.TemporaryDirectory() as fonts, sync_playwright() as p:
        faces = truetype_faces(fonts)
        browser = p.chromium.launch()
        page = browser.new_page()
        for source, target, pages in DOCUMENTS:
            page.goto(source.as_uri(), wait_until="load")
            if faces:
                page.add_style_tag(content=faces)
            page.evaluate("document.fonts.ready")
            overflow = page.evaluate("""() => [...document.querySelectorAll('.page')].map(p =>
                ({ id: p.id, over: p.scrollHeight - p.clientHeight }))""")
            if len(overflow) != pages or any(o["over"] > 0 for o in overflow):
                browser.close()
                sys.exit("%s: expected %d pages that fit, got %s" % (source.name, pages, overflow))
            page.pdf(path=str(target), prefer_css_page_size=True, print_background=True)
            print("written:", target.name, "(TrueType fonts)" if faces else "(system fonts)")
        browser.close()


if __name__ == "__main__":
    main()
