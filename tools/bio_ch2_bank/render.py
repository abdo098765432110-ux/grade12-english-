"""Turns the SVG figures into PNG pictures (twice their size, so they stay sharp on
phones and when zoomed), with the Cairo font loaded. Used by build.py, and on its own
to look at figures while drawing them:
    python3 tools/bio_ch2_bank/render.py OUT_FOLDER [figure numbers...]"""
import http.server
import pathlib
import socketserver
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent
FONTS = SITE / "tools" / "fonts"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(SITE), **k)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, *a):
        pass


def serve():
    server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/" % server.server_address[1]


FONT_CSS = """@font-face { font-family: "Cairo"; src: url("__BASE__tools/fonts/Cairo.ttf") format("truetype"); font-weight: 200 1000; }"""


def page(svg, base):
    return ("<!doctype html><html><head><meta charset='utf-8'><style>" + FONT_CSS.replace("__BASE__", base) +
            "html,body{margin:0;background:#fff} svg{display:block}</style></head><body>" + svg + "</body></html>")


def render(figures, out, scale=2):
    """figures: list of (name, svg_text). Writes out/name.png for each."""
    from playwright.sync_api import sync_playwright
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    server, base = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(device_scale_factor=scale, viewport={"width": 1000, "height": 1000})
            pg = ctx.new_page()
            for name, svg in figures:
                pg.set_content(page(svg, base), wait_until="networkidle")
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(50)
                pg.locator("svg").first.screenshot(path=str(out / (name + ".png")))
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    from images import IMAGES
    out = sys.argv[1]
    wanted = set(int(a) for a in sys.argv[2:])
    figs = [("i%02d" % (i + 1), q["draw"]().svg()) for i, q in enumerate(IMAGES) if not wanted or (i + 1) in wanted]
    render(figs, out, scale=1)
    print("rendered", len(figs))
