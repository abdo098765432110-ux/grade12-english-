"""Small SVG drawing helpers for the Biology Chapter 2 diagrams.

The figures are written as SVG (with Arabic text in the Cairo font) and turned into
sharp PNG pictures by build.py; the PDF uses the same SVG directly."""
import math
from html import escape

INK = "#1f2a44"
SOFT = "#5b6478"
GRID = "#e3e8f0"
RED = "#e63946"
DARKRED = "#b5172b"
PINK = "#ff8fab"
ROSE = "#ffc2d1"
ORANGE = "#ff9f1c"
YELLOW = "#ffd166"
LEMON = "#fff3b0"
GREEN = "#2a9d8f"
LEAF = "#52b788"
DARKLEAF = "#2d6a4f"
LIME = "#8ac926"
TEAL = "#06b6d4"
SKY = "#bde0fe"
BLUE = "#3a86ff"
NAVY = "#1d3557"
PURPLE = "#8338ec"
LILAC = "#cdb4db"
MAGENTA = "#ff006e"
BROWN = "#a0522d"
TAN = "#e9c46a"
SKIN = "#ffd6b8"
BONE = "#f3e9d2"
BONELINE = "#b08d57"
GREY = "#94a3b8"
LIGHT = "#f1f5f9"
WHITE = "#ffffff"

FONT = "Cairo, 'Noto Naskh Arabic', sans-serif"


def f(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


class SVG:
    def __init__(self, w, h, bg=WHITE):
        self.w, self.h = w, h
        self.items = []
        self.defs = []
        self.markers = {}
        if bg:
            self.items.append('<rect width="%s" height="%s" fill="%s"/>' % (w, h, bg))

    def add(self, s):
        self.items.append(s)
        return self

    # ---- shapes
    def rect(self, x, y, w, h, fill=WHITE, stroke=INK, sw=2.5, rx=0, extra=""):
        return self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>'
                        % (f(x), f(y), f(w), f(h), f(rx), fill, stroke, sw, extra))

    def circle(self, cx, cy, r, fill=WHITE, stroke=INK, sw=2.5, extra=""):
        return self.add('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>'
                        % (f(cx), f(cy), f(r), fill, stroke, sw, extra))

    def ellipse(self, cx, cy, rx, ry, fill=WHITE, stroke=INK, sw=2.5, extra=""):
        return self.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>'
                        % (f(cx), f(cy), f(rx), f(ry), fill, stroke, sw, extra))

    def path(self, d, fill="none", stroke=INK, sw=2.5, extra=""):
        return self.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round" %s/>'
                        % (d, fill, stroke, sw, extra))

    def poly(self, pts, fill=WHITE, stroke=INK, sw=2.5, close=True, extra=""):
        d = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in pts) + (" Z" if close else "")
        return self.path(d, fill, stroke, sw, extra)

    def line(self, x1, y1, x2, y2, stroke=INK, sw=2.5, dash=None, extra=""):
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        return self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round"%s %s/>'
                        % (f(x1), f(y1), f(x2), f(y2), stroke, sw, da, extra))

    def marker(self, color):
        key = color.replace("#", "")
        if key not in self.markers:
            self.markers[key] = ('<marker id="ah%s" viewBox="0 0 10 10" refX="7.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                                 '<path d="M0 0 L10 5 L0 10 Z" fill="%s"/></marker>' % (key, color))
        return "url(#ah%s)" % key

    def arrow(self, x1, y1, x2, y2, color=INK, sw=3.5, both=False, curve=0, dash=None):
        m = self.marker(color)
        if curve:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            ln = math.hypot(dx, dy) or 1
            cx, cy = mx - dy / ln * curve, my + dx / ln * curve
            d = "M%s %s Q%s %s %s %s" % (f(x1), f(y1), f(cx), f(cy), f(x2), f(y2))
        else:
            d = "M%s %s L%s %s" % (f(x1), f(y1), f(x2), f(y2))
        extra = 'marker-end="%s"' % m
        if both:
            extra += ' marker-start="%s"' % m
        if dash:
            extra += ' stroke-dasharray="%s"' % dash
        return self.path(d, "none", color, sw, extra)

    def arrow_path(self, d, color=INK, sw=3.5, dash=None):
        extra = 'marker-end="%s"' % self.marker(color)
        if dash:
            extra += ' stroke-dasharray="%s"' % dash
        return self.path(d, "none", color, sw, extra)

    # ---- text
    def text(self, x, y, s, size=24, fill=INK, weight=600, anchor="middle", rtl=True, extra=""):
        direction = ' direction="rtl" unicode-bidi="embed"' if rtl else ' direction="ltr" unicode-bidi="embed"'
        return self.add('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s dominant-baseline="middle" %s>%s</text>'
                        % (f(x), f(y), FONT, size, weight, fill, anchor, direction, extra, escape(s)))

    def lines(self, x, y, rows, size=22, gap=1.35, **kw):
        for i, row in enumerate(rows):
            self.text(x, y + i * size * gap, row, size=size, **kw)
        return self

    def num(self, x, y, n, r=17, fill=YELLOW, color=INK, size=None):
        self.circle(x, y, r, fill=fill, stroke=INK, sw=2.5)
        return self.text(x, y + 1, str(n), size=size or int(r * 1.3), fill=color, weight=800, rtl=False)

    def callout(self, n, px, py, lx, ly, r=17, dot=True, fill=YELLOW):
        """A numbered label at (lx, ly) with a leader line to the point (px, py)."""
        ang = math.atan2(py - ly, px - lx)
        self.line(lx + r * math.cos(ang), ly + r * math.sin(ang), px, py, stroke=INK, sw=2)
        if dot:
            self.circle(px, py, 3.5, fill=INK, stroke=INK, sw=1)
        return self.num(lx, ly, n, r=r, fill=fill)

    def tag(self, x, y, s, size=22, fill=LEMON, stroke=INK, color=INK, pad=12, h=None, w=None, weight=700, rx=10):
        """Text in a rounded box, centred on (x, y)."""
        bw = w or (len(s) * size * 0.52 + 2 * pad)
        bh = h or size * 1.7
        self.rect(x - bw / 2, y - bh / 2, bw, bh, fill=fill, stroke=stroke, sw=2, rx=rx)
        return self.text(x, y + 1, s, size=size, fill=color, weight=weight)

    def key(self, x, y, text, size=20, swatch=None, color=None, kind="box"):
        """A legend row for right-to-left reading: the swatch at x (its right edge), the text to its left."""
        if kind == "box":
            self.rect(x - 26, y - 9, 26, 18, fill=color, stroke=INK, sw=2, rx=3)
        elif kind == "line":
            self.line(x - 34, y, x, y, stroke=color, sw=5)
        elif kind == "dash":
            self.line(x - 34, y, x, y, stroke=color, sw=5, dash="9 6")
        return self.text(x - 44, y + 1, text, size=size, anchor="start", weight=700)

    def panel(self, x, y, letter, size=26):
        """A panel letter such as (أ)."""
        return self.text(x, y, "(" + letter + ")", size=size, weight=800, fill=INK)

    def svg(self):
        defs = "".join(self.markers.values()) + "".join(self.defs)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
                '<defs>%s</defs>%s</svg>' % (self.w, self.h, self.w, self.h, defs, "".join(self.items)))


# ---------------------------------------------------------------- curves and graphs

def smooth(points, t=0.18):
    """A smooth path through the points (Catmull-Rom)."""
    if len(points) < 3:
        return "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in points)
    d = "M%s %s" % (f(points[0][0]), f(points[0][1]))
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t)
        c2 = (p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t)
        d += " C%s %s %s %s %s %s" % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p2[0]), f(p2[1]))
    return d


class Axes:
    """A graph area: data (x, y) → picture coordinates."""

    def __init__(self, s, x0, y0, w, h, xr, yr, xlabel="", ylabel="", xticks=(), yticks=(), grid=True,
                 xlabel_size=22, ylabel_size=22, tick_size=19):
        self.s, self.x0, self.y0, self.w, self.h, self.xr, self.yr = s, x0, y0, w, h, xr, yr
        if grid:
            for v, _ in yticks:
                s.line(x0, self.Y(v), x0 + w, self.Y(v), stroke=GRID, sw=1.5)
        s.line(x0, y0 + h, x0 + w + 8, y0 + h, stroke=INK, sw=3)
        s.line(x0, y0 + h, x0, y0 - 8, stroke=INK, sw=3)
        for v, lab in xticks:
            s.line(self.X(v), y0 + h, self.X(v), y0 + h + 7, stroke=INK, sw=2)
            if lab != "":
                s.text(self.X(v), y0 + h + 24, lab, size=tick_size, weight=600, fill=SOFT)
        for v, lab in yticks:
            s.line(x0 - 7, self.Y(v), x0, self.Y(v), stroke=INK, sw=2)
            if lab != "":
                s.text(x0 - 12, self.Y(v), lab, size=tick_size, weight=600, fill=SOFT, anchor="end", rtl=False)
        if xlabel:
            s.text(x0 + w / 2, y0 + h + 58, xlabel, size=xlabel_size, weight=700)
        if ylabel:
            cx, cy = x0 - 62, y0 + h / 2
            s.text(cx, cy, ylabel, size=ylabel_size, weight=700, extra='transform="rotate(-90 %s %s)"' % (f(cx), f(cy)))

    def X(self, v):
        return self.x0 + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y0 + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def P(self, pts):
        return [(self.X(x), self.Y(y)) for x, y in pts]

    def curve(self, pts, color, sw=4.5, dash=None, smooth_it=True, t=0.18):
        q = self.P(pts)
        d = smooth(q, t) if smooth_it else "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in q)
        extra = ' stroke-dasharray="%s"' % dash if dash else ""
        return self.s.path(d, "none", color, sw, extra)

    def band(self, lo, hi, color=LEMON, label=None, size=18):
        self.s.rect(self.x0, self.Y(hi), self.w, self.Y(lo) - self.Y(hi), fill=color, stroke="none", sw=0)
        if label:
            self.s.text(self.x0 + self.w - 8, (self.Y(hi) + self.Y(lo)) / 2, label, size=size, anchor="start", weight=700, fill=SOFT)

    def vmark(self, v, label=None, color=INK, size=20, top=None):
        X = self.X(v)
        self.s.line(X, self.y0, X, self.y0 + self.h, stroke=color, sw=2, dash="7 6")
        if label is not None:
            self.s.text(X, (top if top is not None else self.y0 - 18), label, size=size, weight=800, fill=color)

    def end_label(self, pts, text, color, dx=14, dy=0, size=22):
        X, Y = self.X(pts[-1][0]), self.Y(pts[-1][1])
        self.s.text(X + dx, Y + dy, text, size=size, weight=800, fill=color, anchor="start")


def bars(s, ax, groups, colors, width=0.7, value_labels=False):
    """groups: list of (x_center, [values...]) drawn side by side."""
    for xc, values in groups:
        n = len(values)
        span = width
        bw = span / n
        for i, v in enumerate(values):
            x = xc - span / 2 + i * bw
            X1, X2 = ax.X(x), ax.X(x + bw)
            Y0, Y1 = ax.Y(0 if ax.yr[0] <= 0 else ax.yr[0]), ax.Y(v)
            top, h = min(Y0, Y1), abs(Y1 - Y0)
            s.rect(X1 + 2, top, X2 - X1 - 4, max(h, 0.1), fill=colors[i % len(colors)], stroke=INK, sw=2, rx=3)


def legend(s, x, y, items, size=20, box=22, gap=34, anchor_right=True):
    """items: (color, text, kind) kind = 'line' | 'box' | 'dash'. Drawn right-to-left from x."""
    for i, it in enumerate(items):
        color, text = it[0], it[1]
        kind = it[2] if len(it) > 2 else "box"
        yy = y + i * gap
        if kind == "line":
            s.line(x - box - 14, yy, x, yy, stroke=color, sw=5)
        elif kind == "dash":
            s.line(x - box - 14, yy, x, yy, stroke=color, sw=5, dash="9 6")
        else:
            s.rect(x - box, yy - box / 2, box, box, fill=color, stroke=INK, sw=2, rx=4)
        s.text(x - box - 24, yy + 1, text, size=size, anchor="start" if not anchor_right else "end", weight=700)


def hexagon(cx, cy, r, rot=0):
    return [(cx + r * math.cos(math.radians(a + rot)), cy + r * math.sin(math.radians(a + rot))) for a in range(0, 360, 60)]


def cell_ring(s, cx, cy, r_in, r_out, n, fill, stroke=INK, nucleus=None, sw=2):
    """A ring of wedge-shaped cells around a centre (a follicle, an acinus, a tubule)."""
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p = [(cx + r_in * math.cos(a0), cy + r_in * math.sin(a0)), (cx + r_out * math.cos(a0), cy + r_out * math.sin(a0)),
             (cx + r_out * math.cos(a1), cy + r_out * math.sin(a1)), (cx + r_in * math.cos(a1), cy + r_in * math.sin(a1))]
        d = "M%s %s L%s %s A%s %s 0 0 1 %s %s L%s %s A%s %s 0 0 0 %s %s Z" % (
            f(p[0][0]), f(p[0][1]), f(p[1][0]), f(p[1][1]), f(r_out), f(r_out), f(p[2][0]), f(p[2][1]),
            f(p[3][0]), f(p[3][1]), f(r_in), f(r_in), f(p[0][0]), f(p[0][1]))
        s.path(d, fill, stroke, sw)
        if nucleus:
            am = (a0 + a1) / 2
            rm = (r_in + r_out) / 2 + (r_out - r_in) * 0.12
            s.circle(cx + rm * math.cos(am), cy + rm * math.sin(am), max(2.5, (r_out - r_in) * 0.2), fill=nucleus, stroke="none", sw=0)


def blob(cx, cy, r, wob=0.12, n=10, seed=1):
    """A slightly irregular round outline (cells, organs)."""
    import random
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + rnd.uniform(-wob, wob))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pts.append(pts[0])
    pts = pts + [pts[1]]
    d = smooth(pts[:-1] + [pts[0]], 0.2)
    return d + " Z"
