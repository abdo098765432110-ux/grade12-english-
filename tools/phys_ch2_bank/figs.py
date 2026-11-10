"""Draws the Physics Chapter 2 diagrams as SVG files at the top of the site
(physics-ch2-*.svg), in the same style as the Chapter 1 diagrams.

    python3 -B tools/phys_ch2_bank/figs.py          # writes all figures
Each figure matches the text description (imageAlt) of its question."""
import math
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent.parent

INK = "#2b3654"
AXIS = "#1f6f62"
LINE = "#e8692e"
GUIDE = "#9aa3b5"
WIRE = "#2b3654"
CUR = "#c43030"      # current arrows
FIELD = "#2f63b0"    # field lines / symbols
PURPLE = "#6a3d9a"
SOFT = "#6b7385"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, Tahoma, 'Noto Sans Arabic', sans-serif"


def n(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


class SVG:
    def __init__(self, w, h, note):
        self.w, self.h, self.note, self.items = w, h, note, []

    def add(self, s):
        self.items.append(s)

    def line(self, x1, y1, x2, y2, color=WIRE, width=3, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<path d="M%s %s L%s %s" stroke="%s" stroke-width="%s" fill="none" stroke-linecap="round"%s/>'
                 % (n(x1), n(y1), n(x2), n(y2), color, n(width), d))

    def poly(self, pts, color=WIRE, width=3, closed=False, fill="none", dash=None):
        d = "M" + " L".join("%s %s" % (n(x), n(y)) for x, y in pts) + (" z" if closed else "")
        extra = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<path d="%s" stroke="%s" stroke-width="%s" fill="%s" stroke-linejoin="round" stroke-linecap="round"%s/>'
                 % (d, color, n(width), fill, extra))

    def head(self, x, y, angle, color=CUR, size=13):
        """A filled arrowhead with its tip at (x, y) pointing at `angle` (radians, SVG y down)."""
        a, w = size, size * 0.38
        bx, by = x - a * math.cos(angle), y - a * math.sin(angle)
        px, py = -math.sin(angle) * w, math.cos(angle) * w
        self.add('<path d="M%s %s L%s %s L%s %s z" fill="%s"/>'
                 % (n(x), n(y), n(bx + px), n(by + py), n(bx - px), n(by - py), color))

    def arrow(self, x1, y1, x2, y2, color=CUR, width=3, size=13):
        ang = math.atan2(y2 - y1, x2 - x1)
        self.line(x1, y1, x2 - size * 0.6 * math.cos(ang), y2 - size * 0.6 * math.sin(ang), color, width)
        self.head(x2, y2, ang, color, size)

    def mid_head(self, x1, y1, x2, y2, t=0.55, color=CUR, size=14):
        """An arrowhead on the segment (x1,y1)→(x2,y2), pointing along it."""
        ang = math.atan2(y2 - y1, x2 - x1)
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        self.head(x + size / 2 * math.cos(ang), y + size / 2 * math.sin(ang), ang, color, size)

    def text(self, x, y, s, size=20, anchor="middle", color=INK, weight=700, italic=False):
        st = ' font-style="italic"' if italic else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.add('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" font-family="%s" fill="%s"%s>%s</text>'
                 % (n(x), n(y), anchor, size, weight, FONT, color, st, s))

    def tag(self, x, y, s, size=20, color=INK, italic=False, pad=6):
        """Centred text on a white box, so it stays readable over field symbols."""
        w = size * 0.62 * len(s) + 2 * pad
        self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="5" fill="#ffffff"/>'
                 % (n(x - w / 2), n(y - size * 0.95), n(w), n(size * 1.35)))
        self.text(x, y, s, size, "middle", color, italic=italic)

    def circle(self, cx, cy, r, color=WIRE, width=3, fill="none", dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<circle cx="%s" cy="%s" r="%s" stroke="%s" stroke-width="%s" fill="%s"%s/>'
                 % (n(cx), n(cy), n(r), color, n(width), fill, d))

    def dot(self, cx, cy, r=5, color=INK):
        self.add('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (n(cx), n(cy), n(r), color))

    def out_of_page(self, cx, cy, r=15, color=WIRE):
        self.circle(cx, cy, r, color, 3, "#ffffff")
        self.dot(cx, cy, r * 0.28, color)

    def into_page(self, cx, cy, r=15, color=WIRE):
        self.circle(cx, cy, r, color, 3, "#ffffff")
        k = r * 0.62
        self.line(cx - k, cy - k, cx + k, cy + k, color, 3)
        self.line(cx - k, cy + k, cx + k, cy - k, color, 3)

    def cross(self, cx, cy, k=6, color=FIELD, width=2.2):
        self.line(cx - k, cy - k, cx + k, cy + k, color, width)
        self.line(cx - k, cy + k, cx + k, cy - k, color, width)

    def arc_arrows(self, cx, cy, r, ccw=True, count=4, color=CUR, start=45):
        """Arrowheads on a circle showing the sense of the current (SVG: y down)."""
        for i in range(count):
            deg = start + i * 360 / count
            a = math.radians(deg)
            x, y = cx + r * math.cos(a), cy - r * math.sin(a)
            # counter-clockwise on screen = increasing math angle
            tang = math.atan2(-math.cos(a), -math.sin(a)) if ccw else math.atan2(math.cos(a), math.sin(a))
            self.head(x + 9 * math.cos(tang), y + 9 * math.sin(tang), tang, color, 20)

    def field_lines(self, x1, x2, ys, color=FIELD, label=None):
        for y in ys:
            self.line(x1, y, x2 - 6, y, color, 2)
            self.head(x2, y, 0, color, 12)
        if label:
            self.text(x2 + 16, ys[0] + 7, label, 22, "start", color, italic=True)

    def save(self, name):
        body = "\n  ".join(self.items)
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
               '  <!-- Physics, chapter 2: %s -->\n  <rect width="%d" height="%d" fill="#ffffff"/>\n  %s\n</svg>\n'
               % (self.w, self.h, self.w, self.h, self.note, self.w, self.h, body))
        (SITE / name).write_text(svg, encoding="utf-8")
        return name


# ---------------------------------------------------------------- graphs
def graph(name, note, xlabel, ylabel, xticks, yticks, xmax, ymax, lines, w=520, h=340):
    """lines: [(points, color, label or None)] in data units; ticks: list of (value, text)."""
    s = SVG(w, h, note)
    x0, y0, x1, y1 = 86, h - 56, w - 70, 40
    sx = lambda v: x0 + (x1 - x0) * v / xmax
    sy = lambda v: y0 - (y0 - y1) * v / ymax
    for v, _ in xticks:
        s.line(sx(v), y0, sx(v), y1 + 10, GUIDE, 1.3, "6 5")
    for v, _ in yticks:
        s.line(x0, sy(v), x1 - 10, sy(v), GUIDE, 1.3, "6 5")
    s.line(x0, y0, x0, y1 - 14, AXIS, 3.5)
    s.head(x0, y1 - 22, -math.pi / 2, AXIS, 18)
    s.line(x0, y0, x1 + 14, y0, AXIS, 3.5)
    s.head(x1 + 24, y0, 0, AXIS, 18)
    for v, t in xticks:
        s.text(sx(v), y0 + 30, t, 19)
    for v, t in yticks:
        s.text(x0 - 14, sy(v) + 7, t, 19, "end")
    s.text(x0 - 6, 18, ylabel, 19, "start")
    s.text(x1 + 30, y0 - 16, xlabel, 19, "end")
    s.text(x0 - 14, y0 + 30, "0", 19, "end")
    for pts, color, label in lines:
        s.poly([(sx(a), sy(b)) for a, b in pts], color, 4.5)
        for a, b in pts[1:]:
            s.dot(sx(a), sy(b), 5.5, color)
        if label:
            a, b = pts[-1]
            s.text(sx(a) + 12, sy(b) + 6, label, 21, "start", color)
    return s.save(name)


def wire_graph():
    return graph("physics-ch2-wire-graph.svg",
                 "B (x10^-5 T) against 1/d (1/m) for a long straight wire: a straight line through the origin and (5,2) (10,4) (15,6) (20,8).",
                 "1/d (m⁻¹)", "B (× 10⁻⁵ T)", [(5, "5"), (10, "10"), (15, "15"), (20, "20")],
                 [(2, "2"), (4, "4"), (6, "6"), (8, "8")], 22, 9,
                 [([(0, 0), (5, 2), (10, 4), (15, 6), (20, 8)], LINE, None)])


def loop_graph():
    return graph("physics-ch2-loop-graph.svg",
                 "B at the centre of a circular coil (pi x 10^-5 T) against I (A): a straight line through the origin and (1,2) (2,4) (3,6).",
                 "I (A)", "B (π × 10⁻⁵ T)", [(1, "1"), (2, "2"), (3, "3")],
                 [(2, "2"), (4, "4"), (6, "6")], 3.4, 6.9,
                 [([(0, 0), (1, 2), (2, 4), (3, 6)], LINE, None)])


def two_lines():
    return graph("physics-ch2-e-two-lines.svg",
                 "B (x10^-5 T) against I (A): line (1) at the centre of a one-turn loop through (10, 2 pi); line (2) near a long wire through (10, 1).",
                 "I (A)", "B (× 10⁻⁵ T)", [(2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")],
                 [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (2 * math.pi, "2π")], 12.6, 7.2,
                 [([(0, 0), (10, 2 * math.pi)], LINE, "(1)"), ([(0, 0), (10, 1)], FIELD, "(2)")])


def torque_curve():
    s = SVG(560, 340, "torque tau (N.m) against the angle theta between the coil's normal and B: sine curve, 0 at 0 deg, 0.5 N.m at 90 deg, 0 at 180 deg.")
    x0, y0, x1, y1 = 86, 284, 480, 50
    sx = lambda v: x0 + (x1 - x0) * v / 180
    sy = lambda v: y0 - (y0 - y1) * v / 0.6
    for v in (30, 60, 90, 120, 150, 180):
        s.line(sx(v), y0, sx(v), y1 + 10, GUIDE, 1.3, "6 5")
    for v in (0.25, 0.5):
        s.line(x0, sy(v), x1, sy(v), GUIDE, 1.3, "6 5")
    s.line(x0, y0, x0, y1 - 14, AXIS, 3.5)
    s.head(x0, y1 - 22, -math.pi / 2, AXIS, 18)
    s.line(x0, y0, x1 + 30, y0, AXIS, 3.5)
    s.head(x1 + 40, y0, 0, AXIS, 18)
    for v in (30, 60, 90, 120, 150, 180):
        s.text(sx(v), y0 + 30, "%d°" % v, 18)
    s.text(x0 - 14, sy(0.25) + 7, "0.25", 18, "end")
    s.text(x0 - 14, sy(0.5) + 7, "0.5", 18, "end")
    s.text(x0 - 14, y0 + 30, "0", 18, "end")
    s.text(x0 - 6, 22, "τ (N.m)", 19, "start")
    s.text(x1 + 46, y0 - 16, "θ", 21, "end", italic=True)
    pts = [(sx(a), sy(0.5 * math.sin(math.radians(a)))) for a in range(0, 181, 3)]
    s.poly(pts, LINE, 4.5)
    return s.save("physics-ch2-e-torque-curve.svg")


# ---------------------------------------------------------------- straight wires
def crossed(name, note, i_h, i_v, down=False):
    s = SVG(460, 400, note)
    cx, cy = 230, 205
    s.line(40, cy, 420, cy, WIRE, 4)
    s.line(cx, 30, cx, 380, WIRE, 4)
    s.arrow(330, cy, 395, cy, CUR, 4, 18)
    s.text(382, cy - 16, i_h, 21, "middle", CUR)
    if down:
        s.arrow(cx, 290, cx, 358, CUR, 4, 18)
        s.text(cx + 14, 352, i_v, 21, "start", CUR)
    else:
        s.arrow(cx, 120, cx, 52, CUR, 4, 18)
        s.text(cx + 14, 60, i_v, 21, "start", CUR)
    s.dot(cx, cy, 6)
    s.text(cx - 14, cy + 30, "O", 20, "end")
    s.text(330, 110, "الربع الأول", 20, "middle", PURPLE)
    s.text(118, 110, "الربع الثاني", 20, "middle", PURPLE)
    s.text(118, 310, "الربع الثالث", 20, "middle", PURPLE)
    s.text(330, 310, "الربع الرابع", 20, "middle", PURPLE)
    return s.save(name)


def crossed_wires():
    return crossed("physics-ch2-crossed-wires.svg",
                   "two insulated wires crossing at O in the page; horizontal current I to the right, vertical current I upward; quadrants numbered.",
                   "I", "I")


def crossed_unequal():
    return crossed("physics-ch2-e-crossed-unequal.svg",
                   "two insulated wires crossing at O in the page; horizontal 2 A to the right, vertical 6 A downward; quadrants numbered.",
                   "2 A", "6 A", down=True)


def right_triangle():
    s = SVG(460, 340, "right angle at P: PA = 3 cm, PB = 4 cm; wires perpendicular to the page at A (4.5 A) and B (8 A).")
    P, A, B = (90, 270), (90, 270 - 180), (90 + 240, 270)
    s.poly([P, A, B], INK, 2.5, True)
    s.poly([(P[0], P[1] - 22), (P[0] + 22, P[1] - 22), (P[0] + 22, P[1])], INK, 2)
    s.dot(*P, 6)
    s.text(P[0] - 14, P[1] + 26, "P", 22, "end")
    s.circle(A[0], A[1], 13, WIRE, 3, INK)
    s.circle(B[0], B[1], 13, WIRE, 3, INK)
    s.text(A[0] - 22, A[1] - 6, "A", 22, "end")
    s.text(A[0] + 22, A[1] - 10, "4.5 A", 21, "start", CUR)
    s.text(B[0] + 4, B[1] + 38, "B", 22)
    s.text(B[0] + 24, B[1] - 16, "8 A", 21, "start", CUR)
    s.text(P[0] - 16, (P[1] + A[1]) / 2 + 7, "3 cm", 20, "end", SOFT)
    s.text((P[0] + B[0]) / 2, P[1] + 32, "4 cm", 20, "middle", SOFT)
    return s.save("physics-ch2-right-triangle.svg")


def three_currents():
    s = SVG(520, 200, "three long parallel wires perpendicular to the page, equal spacing d on a horizontal line: Y (left, out of page), X (middle, out of page), Z (right, into page).")
    xs, y = (110, 260, 410), 96
    s.line(70, y, 450, y, GUIDE, 1.5, "6 5")
    s.out_of_page(xs[0], y, 20)
    s.out_of_page(xs[1], y, 20)
    s.into_page(xs[2], y, 20)
    for x, lab in zip(xs, "YXZ"):
        s.text(x, y - 34, lab, 23)
    for a, b in ((xs[0], xs[1]), (xs[1], xs[2])):
        s.line(a + 26, y + 44, b - 26, y + 44, SOFT, 2)
        s.head(a + 24, y + 44, math.pi, SOFT, 10)
        s.head(b - 24, y + 44, 0, SOFT, 10)
        s.text((a + b) / 2, y + 72, "d", 21, "middle", SOFT, italic=True)
    return s.save("physics-ch2-three-currents.svg")


def two_wires_points():
    s = SVG(560, 230, "wire 1 (3 A, out of page) and wire 2 (5 A, into page) 6 cm apart; P between them 2 cm from wire 1; Q to the left of wire 1, 2 cm from it.")
    k = 50  # px per cm
    y = 100
    x1 = 160
    x2 = x1 + 6 * k
    xp = x1 + 2 * k
    xq = x1 - 2 * k
    s.line(40, y, 520, y, GUIDE, 1.5, "6 5")
    s.out_of_page(x1, y, 19)
    s.into_page(x2, y, 19)
    s.text(x1, y - 32, "(1)  3 A", 20, "middle", CUR)
    s.text(x2, y - 32, "(2)  5 A", 20, "middle", CUR)
    s.dot(xp, y, 6, PURPLE)
    s.dot(xq, y, 6, PURPLE)
    s.text(xp, y - 18, "P", 21, "middle", PURPLE)
    s.text(xq, y - 18, "Q", 21, "middle", PURPLE)

    def dim(a, b, yy, label):
        s.line(a + 3, yy, b - 3, yy, SOFT, 2)
        s.head(a + 1, yy, math.pi, SOFT, 10)
        s.head(b - 1, yy, 0, SOFT, 10)
        s.text((a + b) / 2, yy + 26, label, 19, "middle", SOFT)

    dim(xq, x1, y + 44, "2 cm")
    dim(x1, xp, y + 44, "2 cm")
    dim(x1, x2, y + 94, "6 cm")
    return s.save("physics-ch2-e-two-wires-points.svg")


def three_wires():
    s = SVG(520, 330, "three long parallel vertical wires in one plane: A 10 A up, B 5 A up (10 cm from A), C 15 A up (20 cm from B).")
    k = 11  # px per cm
    xa = 110
    xb = xa + 10 * k
    xc = xb + 20 * k
    top, bot = 40, 250
    for x in (xa, xb, xc):
        s.line(x, top, x, bot, WIRE, 4)
    s.arrow(xa, 175, xa, 105, CUR, 4, 18)
    s.arrow(xb, 175, xb, 105, CUR, 4, 18)
    s.arrow(xc, 175, xc, 105, CUR, 4, 18)
    s.text(xa - 12, 145, "10 A", 20, "end", CUR)
    s.text(xb + 12, 145, "5 A", 20, "start", CUR)
    s.text(xc + 12, 145, "15 A", 20, "start", CUR)
    for x, lab in ((xa, "A"), (xb, "B"), (xc, "C")):
        s.text(x, top - 12, lab, 22)
    for a, b, lab in ((xa, xb, "10 cm"), (xb, xc, "20 cm")):
        s.line(a + 3, 282, b - 3, 282, SOFT, 2)
        s.head(a + 1, 282, math.pi, SOFT, 10)
        s.head(b - 1, 282, 0, SOFT, 10)
        s.text((a + b) / 2, 312, lab, 19, "middle", SOFT)
    return s.save("physics-ch2-e-three-wires.svg")


def wire_and_frame():
    s = SVG(400, 470, "long vertical wire (10 A up) on the left; rectangular loop to its right: near side 5 cm away (current up), far side 15 cm away (current down), sides 30 cm, loop current 5 A.")
    k = 10  # px per cm (drawn to scale)
    xw = 90
    xn, xf = xw + 5 * k, xw + 15 * k
    top, bot = 40, 40 + 30 * k
    s.line(xw, 15, xw, 355, WIRE, 4)
    s.arrow(xw, 230, xw, 150, CUR, 4, 18)
    s.text(xw - 12, 195, "10 A", 20, "end", CUR)
    s.poly([(xn, top), (xf, top), (xf, bot), (xn, bot)], WIRE, 4, True)
    s.mid_head(xn, bot, xn, top, 0.5, CUR, 18)
    s.mid_head(xn, top, xf, top, 0.5, CUR, 18)
    s.mid_head(xf, top, xf, bot, 0.5, CUR, 18)
    s.mid_head(xf, bot, xn, bot, 0.5, CUR, 18)
    s.text((xn + xf) / 2, (top + bot) / 2 + 8, "5 A", 21, "middle", CUR)
    s.text(xf + 14, (top + bot) / 2 + 8, "30 cm", 19, "start", SOFT)
    for a, b, yy, lab in ((xw, xn, bot + 40, "5 cm"), (xw, xf, bot + 90, "15 cm")):
        s.line(xw, bot + 22, xw, bot + 100, GUIDE, 1.3, "5 4") if a == xw and lab == "5 cm" else None
        s.line(b, bot + 6, b, yy + 8, GUIDE, 1.3, "5 4") if lab == "15 cm" else None
        s.line(a + 3, yy, b - 3, yy, SOFT, 2)
        s.head(a + 1, yy, math.pi, SOFT, 10)
        s.head(b - 1, yy, 0, SOFT, 10)
        s.text((a + b) / 2, yy + 26, lab, 19, "middle", SOFT)
    return s.save("physics-ch2-wire-and-frame.svg")


# ---------------------------------------------------------------- loops
def loop_ccw(s, cx, cy, r, label=None, start=45):
    s.circle(cx, cy, r, WIRE, 4)
    s.arc_arrows(cx, cy, r, True, 4, CUR, start)
    if label:
        s.text(cx + r * 0.72 + 8, cy - r * 0.72 - 10, label, 21, "start", CUR)


def loop_and_wire():
    s = SVG(460, 400, "circular coil, radius 10 cm, centre O, 2 A anticlockwise; long horizontal wire 20 cm below O with unknown current.")
    k = 7.5
    cx, cy, r = 230, 120, 10 * k
    loop_ccw(s, cx, cy, r, "2 A")
    s.dot(cx, cy, 5.5)
    s.text(cx - 10, cy - 10, "O", 20, "end")
    s.line(cx, cy, cx + r, cy, SOFT, 2)
    s.text(cx + r / 2, cy - 10, "10 cm", 17, "middle", SOFT)
    yw = cy + 20 * k
    s.line(40, yw, 420, yw, WIRE, 4)
    s.text(410, yw - 14, "I = ?", 21, "end", CUR)
    s.line(cx - 110, cy, cx - 110, yw - 4, SOFT, 2)
    s.head(cx - 110, cy - 1, -math.pi / 2, SOFT, 10)
    s.head(cx - 110, yw - 2, math.pi / 2, SOFT, 10)
    s.line(cx - 118, cy, cx - 6, cy, GUIDE, 1.3, "5 4")
    s.text(cx - 120, (cy + yw) / 2 + 6, "20 cm", 19, "end", SOFT)
    return s.save("physics-ch2-loop-and-wire.svg")


def loop_outside():
    s = SVG(420, 300, "circular coil in the page, anticlockwise current, field out of the page at the centre O; point Q just outside the loop on its right.")
    cx, cy, r = 190, 150, 100
    loop_ccw(s, cx, cy, r, "I")
    s.out_of_page(cx, cy, 14, FIELD)
    s.text(cx - 22, cy + 30, "O", 20, "end")
    s.dot(cx + r + 18, cy, 6, PURPLE)
    s.text(cx + r + 30, cy + 7, "Q", 22, "start", PURPLE)
    return s.save("physics-ch2-loop-outside.svg")


def loop_tangent():
    s = SVG(460, 330, "circular coil radius 5 cm, centre O, 2 A anticlockwise; a long straight insulated wire (3 A) touches the coil at its lowest point.")
    cx, cy, r = 230, 140, 105
    loop_ccw(s, cx, cy, r, "2 A", start=45)
    s.dot(cx, cy, 5.5)
    s.text(cx - 10, cy - 10, "O", 20, "end")
    s.line(cx, cy, cx + r * 0.7071, cy - r * 0.7071, SOFT, 2)
    s.text(cx + 30, cy - 40, "5 cm", 18, "end", SOFT)
    yw = cy + r
    s.line(30, yw, 430, yw, WIRE, 4)
    s.text(420, yw + 32, "3 A", 21, "end", CUR)
    return s.save("physics-ch2-e-loop-tangent.svg")


# ---------------------------------------------------------------- solenoid
def solenoid_compass():
    s = SVG(560, 340, "horizontal solenoid seen from the front, left end to the + terminal, right end to the - terminal; current in the front turns flows upward; small compass inside on the axis.")
    x0, x1, yt, yb = 120, 440, 70, 190
    turns = 8
    pitch = (x1 - x0) / turns
    # back halves (dashed) then front halves (solid, slanted) with upward arrows
    for i in range(turns):
        xa = x0 + i * pitch
        s.line(xa + pitch * 0.5, yt, xa + pitch, yb, GUIDE, 2.2, "5 4")
    for i in range(turns):
        xa = x0 + i * pitch
        s.line(xa, yb, xa + pitch * 0.5, yt, WIRE, 3.4)
        if i in (1, 3, 5, 7):
            s.mid_head(xa, yb, xa + pitch * 0.5, yt, 0.55, CUR, 15)
    s.line(x0 + 4, (yt + yb) / 2, x1 - 4, (yt + yb) / 2, GUIDE, 1.2, "3 5")
    # compass on the axis
    cxc, cyc = (x0 + x1) / 2 + pitch * 0.25, (yt + yb) / 2
    s.circle(cxc, cyc, 22, PURPLE, 2.5, "#ffffff")
    s.text(cxc, cyc + 8, "?", 22, "middle", PURPLE)
    # leads and battery
    yb2 = 285
    s.poly([(x0, yb), (x0 - 50, yb), (x0 - 50, yb2), (250, yb2)], WIRE, 3)
    s.poly([(x1, yb), (x1 + 50, yb), (x1 + 50, yb2), (310, yb2)], WIRE, 3)
    s.line(250, yb2 - 30, 250, yb2 + 30, WIRE, 4)   # long plate (+)
    s.line(310, yb2 - 16, 310, yb2 + 16, WIRE, 7)   # short plate (−)
    s.line(250, yb2, 250, yb2, WIRE, 1)
    s.text(232, yb2 - 22, "+", 26, "middle", CUR)
    s.text(330, yb2 - 22, "−", 26, "middle", INK)
    s.text(x0 - 60, (yt + yb) / 2 + 8, "الطرف الأيسر", 18, "end", SOFT) if False else None
    return s.save("physics-ch2-solenoid-compass.svg")


# ---------------------------------------------------------------- forces
def field_into(s, x0, y0, x1, y1, step=48):
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            s.cross(x, y)
            x += step
        y += step


def force_direction():
    s = SVG(460, 300, "a horizontal wire in the page with current I to the right inside a uniform magnetic field directed into the page (crosses).")
    field_into(s, 50, 60, 410, 260)
    s.line(30, 180, 430, 180, WIRE, 5)
    s.arrow(250, 180, 330, 180, CUR, 5, 20)
    s.text(314, 172, "I", 24, "middle", CUR)
    s.tag(404, 30, "B ⊗", 22, FIELD)
    return s.save("physics-ch2-force-direction.svg")


def bent_wire():
    s = SVG(500, 320, "uniform field B to the right; an L-shaped wire: 40 cm part parallel to B, then 30 cm part perpendicular to B; current 2 A.")
    s.field_lines(30, 470, [45, 115, 185, 300], FIELD)
    s.text(470, 33, "B", 22, "end", FIELD, italic=True)
    k = 7
    xa, y = 90, 250
    xb = xa + 40 * k
    yt = y - 30 * k
    s.poly([(xa, y), (xb, y), (xb, yt)], WIRE, 5)
    s.mid_head(xa, y, xb, y, 0.5, CUR, 18)
    s.mid_head(xb, y, xb, yt, 0.5, CUR, 18)
    s.text((xa + xb) / 2, y - 14, "40 cm", 19, "middle", INK)
    s.text(xb + 12, (y + yt) / 2 + 30, "30 cm", 19, "start", INK)
    s.text(xa, y - 14, "I = 2 A", 19, "start", CUR)
    return s.save("physics-ch2-bent-wire.svg")


def three_wires_field():
    s = SVG(560, 330, "uniform field B to the right; wire 1 vertical length L, wire 2 at 30 deg to B length 2L, wire 3 horizontal length 3L; equal currents I.")
    s.field_lines(20, 540, [30, 300], FIELD)
    s.text(536, 60, "B", 22, "end", FIELD, italic=True)
    u = 52
    # wire 1: vertical, length L
    s.line(70, 220, 70, 220 - u * 2, WIRE, 5)
    s.mid_head(70, 220, 70, 220 - u * 2, 0.5, CUR, 16)
    s.text(70, 250, "(1)  L", 19)
    # wire 2: 30 degrees, length 2L
    xs, ys = 140, 220
    L2 = u * 4
    xe, ye = xs + L2 * math.cos(math.radians(30)), ys - L2 * math.sin(math.radians(30))
    s.line(xs, ys, xe, ye, WIRE, 5)
    s.mid_head(xs, ys, xe, ye, 0.5, CUR, 16)
    s.line(xs, ys, xs + 90, ys, GUIDE, 1.5, "5 4")
    s.add('<path d="M%s %s A 56 56 0 0 0 %s %s" stroke="%s" stroke-width="2" fill="none"/>'
          % (n(xs + 56), n(ys), n(xs + 56 * math.cos(math.radians(30))), n(ys - 56 * math.sin(math.radians(30))), PURPLE))
    s.text(xs + 66, ys - 10, "30°", 18, "start", PURPLE)
    s.text((xs + xe) / 2 - 6, ys + 30, "(2)  2L", 19)
    # wire 3: horizontal, length 3L
    x3 = 230
    s.line(x3, 275, x3 + u * 6, 275, WIRE, 5)
    s.mid_head(x3, 275, x3 + u * 6, 275, 0.5, CUR, 16)
    s.text(x3 + u * 3, 262, "(3)  3L", 19)
    return s.save("physics-ch2-three-wires-field.svg")


def frame_in_field():
    s = SVG(500, 340, "rectangular loop abcd in the page (a top-left, b top-right, c bottom-right, d bottom-left), clockwise current, in a uniform field B to the right.")
    s.field_lines(20, 470, [40, 100, 160, 220, 280], FIELD)
    s.text(470, 28, "B", 22, "end", FIELD, italic=True)
    a, b, c, d = (130, 80), (370, 80), (370, 250), (130, 250)
    s.poly([a, b, c, d], WIRE, 5, True)
    s.mid_head(*a, *b, 0.5, CUR, 18)
    s.mid_head(*b, *c, 0.5, CUR, 18)
    s.mid_head(*c, *d, 0.5, CUR, 18)
    s.mid_head(*d, *a, 0.5, CUR, 18)
    for (x, y), lab, dx, dy in ((a, "a", -14, -10), (b, "b", 14, -10), (c, "c", 14, 18), (d, "d", -14, 18)):
        s.text(x + dx, y + dy, lab, 22, "end" if dx < 0 else "start", PURPLE)
    s.text(250, 140, "I", 22, "middle", CUR)
    return s.save("physics-ch2-e-frame-in-field.svg")


def four_segments():
    s = SVG(560, 330, "uniform field B to the right in the page; four equal wire segments: (a) current up, (b) current down, (c) current to the right, (d) current at 30 deg above B.")
    s.field_lines(20, 540, [36, 300], FIELD)
    s.text(536, 70, "B", 22, "end", FIELD, italic=True)
    L = 150
    segs = [((80, 245), (80, 245 - L), "(a)"), ((190, 95), (190, 95 + L), "(b)"), ((260, 250), (260 + L, 250), "(c)")]
    for (x1, y1), (x2, y2), lab in segs:
        s.line(x1, y1, x2, y2, WIRE, 5)
        s.mid_head(x1, y1, x2, y2, 0.55, CUR, 20)
    s.text(80, 278, "(a)", 20, "middle", PURPLE)
    s.text(190, 278, "(b)", 20, "middle", PURPLE)
    s.text(335, 232, "(c)", 20, "middle", PURPLE)
    xs, ys = 340, 190
    xe, ye = xs + L * math.cos(math.radians(30)), ys - L * math.sin(math.radians(30))
    s.line(xs, ys, xe, ye, WIRE, 5)
    s.mid_head(xs, ys, xe, ye, 0.55, CUR, 20)
    s.line(xs, ys, xs + 80, ys, GUIDE, 1.5, "5 4")
    s.add('<path d="M%s %s A 50 50 0 0 0 %s %s" stroke="%s" stroke-width="2" fill="none"/>'
          % (n(xs + 50), n(ys), n(xs + 50 * math.cos(math.radians(30))), n(ys - 50 * math.sin(math.radians(30))), PURPLE))
    s.text(xs + 58, ys - 8, "30°", 18, "start", PURPLE)
    s.text(xe + 6, ye - 8, "(d)", 20, "start", PURPLE)
    return s.save("physics-ch2-e-four-segments.svg")


# ---------------------------------------------------------------- circuit
def resistor(s, x1, x2, y, label, color=WIRE):
    """A zig-zag resistor between x1 and x2 on a horizontal wire at y."""
    s.line(x1, y, x1 + 14, y, color, 3)
    pts, k = [(x1 + 14, y)], (x2 - x1 - 28) / 8
    for i in range(1, 8):
        pts.append((x1 + 14 + i * k, y + (-12 if i % 2 else 12)))
    pts.append((x2 - 14, y))
    s.poly(pts, color, 3)
    s.line(x2 - 14, y, x2, y, color, 3)
    s.text((x1 + x2) / 2, y - 22, label, 19)


def voltmeter_loading():
    s = SVG(520, 330, "a 12 V battery with negligible internal resistance in series with two 10 kOhm resistors; a 10 kOhm voltmeter in parallel with the second resistor.")
    yt, yb = 90, 280
    xl, xr = 60, 460
    resistor(s, 100, 220, yt, "10 kΩ")
    resistor(s, 300, 420, yt, "10 kΩ")
    s.line(xl, yt, 100, yt, WIRE, 3)
    s.line(220, yt, 300, yt, WIRE, 3)
    s.line(420, yt, xr, yt, WIRE, 3)
    s.line(xl, yt, xl, yb, WIRE, 3)
    s.line(xr, yt, xr, yb, WIRE, 3)
    s.line(xl, yb, 235, yb, WIRE, 3)
    s.line(255, yb, xr, yb, WIRE, 3)
    s.line(235, yb - 28, 235, yb + 28, WIRE, 4)
    s.line(255, yb - 15, 255, yb + 15, WIRE, 7)
    s.text(245, yb - 40, "12 V", 19)
    # voltmeter across the second resistor
    s.dot(280, yt, 5)
    s.dot(440, yt, 5)
    s.poly([(280, yt), (280, 180), (335, 180)], WIRE, 3)
    s.poly([(385, 180), (440, 180), (440, yt)], WIRE, 3)
    s.circle(360, 180, 25, WIRE, 3, "#ffffff")
    s.text(360, 188, "V", 22, "middle", PURPLE)
    s.text(360, 232, "10 kΩ", 18, "middle", SOFT)
    return s.save("physics-ch2-voltmeter-loading.svg")


ALL = [wire_graph, crossed_wires, right_triangle, loop_and_wire, loop_outside, loop_graph, solenoid_compass,
       force_direction, bent_wire, three_wires_field, three_currents, wire_and_frame, voltmeter_loading,
       two_wires_points, crossed_unequal, two_lines, loop_tangent, frame_in_field, four_segments, three_wires,
       torque_curve]

if __name__ == "__main__":
    for fn in ALL:
        print(fn())
