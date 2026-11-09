"""Image questions 1–12: plants, Starling, kinds of glands, the body map, the chemical
nature of hormones, the pituitary gland, growth."""
import math
from figlib import *


# ------------------------------------------------------------------ 1. Boysen-Jensen set-ups
def seedling(s, cx, kind):
    base = 470
    # pot
    s.poly([(cx - 58, base - 50), (cx + 58, base - 50), (cx + 44, base + 30), (cx - 44, base + 30)], fill="#e07a3f", stroke=INK)
    s.rect(cx - 64, base - 62, 128, 16, fill="#f4a261", stroke=INK, rx=4)
    s.ellipse(cx, base - 62, 60, 7, fill="#6b4226", stroke=INK, sw=2)
    top = 175
    # stem
    s.rect(cx - 10, top, 20, base - 62 - top, fill=LEAF, stroke=DARKLEAF, sw=2.5, rx=3)
    # two leaves
    s.path("M%s %s q-48 -30 -70 6 q36 18 70 -6 Z" % (cx - 9, 360), fill=LEAF, stroke=DARKLEAF)
    s.path("M%s %s q48 -30 70 6 q-36 18 -70 -6 Z" % (cx + 9, 330), fill=LEAF, stroke=DARKLEAF)
    tip = "M%s %s L%s %s Q%s %s %s %s Z" % (cx - 10, top + 2, cx - 10, top - 18, cx, top - 46, cx + 10, top - 18)
    tip = "M%s %s L%s %s Q%s %s %s %s Q%s %s %s %s L%s %s Z" % (cx - 10, top, cx - 10, top - 22, cx - 10, top - 44, cx, top - 46, cx + 10, top - 44, cx + 10, top - 22, cx + 10, top)
    if kind == "intact":
        s.path(tip, DARKLEAF, DARKLEAF, 2)
    elif kind == "cut":
        s.path(tip, "none", GREY, 2.5, 'stroke-dasharray="6 5"')
        s.line(cx - 16, top, cx + 16, top, stroke=INK, sw=3)
    elif kind == "barrier":
        s.path(tip, DARKLEAF, DARKLEAF, 2)
        s.rect(cx - 30, top - 2, 60, 9, fill="#2b2d42", stroke=INK, sw=1.5, rx=2)
    elif kind == "gel":
        s.path("M%s %s L%s %s Q%s %s %s %s Q%s %s %s %s L%s %s Z" % (cx - 10, top - 14, cx - 10, top - 34, cx - 10, top - 56, cx, top - 58, cx + 10, top - 56, cx + 10, top - 34, cx + 10, top - 14), DARKLEAF, DARKLEAF, 2)
        s.rect(cx - 28, top - 14, 56, 14, fill="#ffe066", stroke="#d4a017", sw=2, rx=3, extra='fill-opacity="0.9"')
    # light from the right
    for dy in (-20, 30, 80):
        s.arrow(cx + 92, top + dy, cx + 30, top + dy, color=ORANGE, sw=4)


def fig01():
    s = SVG(760, 670)
    s.circle(726, 52, 22, fill=YELLOW, stroke=ORANGE, sw=3)
    for a in range(0, 360, 45):
        r = math.radians(a)
        s.line(726 + 28 * math.cos(r), 52 + 28 * math.sin(r), 726 + 38 * math.cos(r), 52 + 38 * math.sin(r), stroke=ORANGE, sw=3)
    s.text(450, 52, "الضوء يسقط من جانب واحد فقط", size=24, weight=800)
    for cx, kind, letter in ((110, "intact", "أ"), (290, "cut", "ب"), (470, "barrier", "ج"), (650, "gel", "د")):
        seedling(s, cx, kind)
        s.panel(cx, 532, letter)
    s.key(700, 572, "حاجز رقيق لا تنفذ منه المواد الكيميائية", color="#2b2d42")
    s.key(700, 606, "طبقة رقيقة تنفذ منها المواد الكيميائية", color="#ffe066")
    s.key(700, 640, "(ب): أُزيلت قمتها النامية", color=WHITE, kind="none")
    return s


# ------------------------------------------------------------------ 2. parts of a flowering plant
def fig02():
    s = SVG(720, 640)
    cx = 360
    # pot and soil
    s.poly([(cx - 90, 560), (cx + 90, 560), (cx + 70, 625), (cx - 70, 625)], fill="#e07a3f", stroke=INK)
    s.rect(cx - 98, 548, 196, 18, fill="#f4a261", stroke=INK, rx=5)
    # main stem
    s.path("M%s 550 C %s 430 %s 300 %s 120" % (cx, cx - 6, cx + 6, cx), "none", DARKLEAF, 13)
    s.path("M%s 550 C %s 430 %s 300 %s 120" % (cx, cx - 6, cx + 6, cx), "none", LEAF, 8)
    # growing tip
    s.path("M%s 128 Q%s 92 %s 84 Q%s 92 %s 128 Z" % (cx - 9, cx - 8, cx, cx + 8, cx + 9), DARKLEAF, DARKLEAF, 2)
    s.path("M%s 116 q-30 -26 -44 -8 q22 14 44 8 Z" % (cx - 4), LEAF, DARKLEAF, 2)
    s.path("M%s 110 q30 -26 44 -8 q-22 14 -44 8 Z" % (cx + 4), LEAF, DARKLEAF, 2)
    # bending region bracket
    s.path("M%s 150 q-14 0 -14 14 v44 q0 14 14 14" % (cx - 26), "none", PURPLE, 3)
    # leaves with buds
    def leaf(x, y, side, size=1.0):
        k = -1 if side == "L" else 1
        s.path("M%s %s q%s -70 %s -26 q%s 46 %s 26 Z" % (x, y, k * 60 * size, k * 150 * size, k * -40 * size, k * -150 * size), LEAF, DARKLEAF, 2.5)
        s.path("M%s %s q%s -24 %s -14" % (x, y, k * 70 * size, k * 140 * size), "none", DARKLEAF, 2)
    leaf(cx - 6, 470, "L", 1.0)
    leaf(cx + 6, 400, "R", 0.95)
    # bud in the axil of the right leaf
    s.path("M%s 394 C %s 380 %s 352 %s 340 C %s 352 %s 378 %s 394 Z" % (cx + 8, cx + 4, cx + 10, cx + 20, cx + 32, cx + 34, cx + 26), "#95d5b2", DARKLEAF, 2.5)
    s.path("M%s 392 C %s 376 %s 360 %s 346" % (cx + 16, cx + 16, cx + 18, cx + 20), "none", DARKLEAF, 2)
    # branch with flower (left)
    s.path("M%s 330 Q %s 300 %s 250" % (cx - 2, cx - 70, cx - 120), "none", DARKLEAF, 7)
    fx, fy = cx - 128, 232
    for a in range(0, 360, 60):
        r = math.radians(a)
        s.ellipse(fx + 26 * math.cos(r), fy + 26 * math.sin(r), 22, 13, fill=PINK, stroke=MAGENTA, sw=2,
                  extra='transform="rotate(%s %s %s)"' % (a, f(fx + 26 * math.cos(r)), f(fy + 26 * math.sin(r))))
    s.circle(fx, fy, 13, fill=YELLOW, stroke=ORANGE, sw=2.5)
    # branch with fruit (right)
    s.path("M%s 270 Q %s 250 %s 215" % (cx + 2, cx + 70, cx + 110), "none", DARKLEAF, 7)
    s.circle(cx + 122, 228, 26, fill="#f77f00", stroke="#c1121f", sw=3)
    s.path("M%s 204 l-8 -10 m8 10 l8 -10 m-8 10 v-12" % (cx + 122), "none", DARKLEAF, 3)
    # labels
    s.callout(1, cx, 92, cx + 120, 70)
    s.callout(2, cx + 22, 366, cx + 150, 320)
    s.callout(3, cx - 40, 185, cx - 130, 120)
    s.callout(4, fx - 22, 248, fx - 80, 320)
    s.callout(5, cx + 140, 236, cx + 230, 210)
    s.callout(6, cx - 120, 448, cx - 230, 420)
    return s


# ------------------------------------------------------------------ 3. Starling's experiment
def fig03():
    s = SVG(760, 600)
    # stomach (J-shaped bag, upper left)
    s.path("M95 40 L150 40 C150 120 170 200 240 205 C280 208 305 200 330 195 L338 242 C260 300 150 330 80 270 C30 220 40 100 95 40 Z", ROSE, INK, 3)
    s.text(150, 260, "المعدة", size=22, weight=800)
    # duodenum C-loop
    duo = "M330 218 C 420 190 470 230 470 300 C 470 400 420 460 330 470 C 270 476 240 450 240 420"
    s.path(duo, "none", INK, 44)
    s.path(duo, "none", "#ffb4a2", 36)
    s.path(duo, "none", "#e5989b", 6, 'stroke-dasharray="2 9"')
    # pancreas inside the loop
    s.path("M300 420 C 320 380 380 370 420 340 C 440 330 450 345 440 365 C 420 400 360 420 330 440 C 305 450 290 440 300 420 Z", "#f6bd60", INK, 3)
    for x, y in ((330, 420), (360, 400), (395, 380), (420, 360)):
        s.circle(x, y, 7, fill="#f7d08a", stroke="#c98a12", sw=1.5)
    # pancreatic duct
    s.path("M335 425 C 360 430 400 425 438 392", "none", "#2a9d8f", 5)
    s.arrow(430, 398, 446, 384, color="#2a9d8f", sw=4)
    # nerve from the lower left, cut in the middle
    s.path("M40 560 C 90 540 140 520 165 505", "none", "#f4a300", 7)
    s.path("M200 488 C 240 470 270 450 300 432", "none", "#f4a300", 7)
    s.line(170, 492, 194, 516, stroke=DARKRED, sw=4)
    s.line(194, 492, 170, 516, stroke=DARKRED, sw=4)
    # blood route: out of the duodenum wall, round the body, back to the pancreas
    s.path("M470 290 C 560 270 600 210 620 165", "none", RED, 9)
    s.arrow(604, 196, 620, 166, color=RED, sw=5)
    s.rect(560, 100, 180, 58, fill="#ffe5e5", stroke=RED, sw=2.5, rx=12)
    s.text(650, 129, "الدورة الدموية", size=21, weight=800, fill=DARKRED)
    s.path("M705 160 C 720 320 600 420 470 400", "none", RED, 9)
    s.arrow(500, 404, 414, 368, color=RED, sw=5)
    # food arriving
    s.arrow(250, 120, 320, 190, color=BROWN, sw=5)
    s.text(236, 100, "الطعام", size=21, weight=800, fill=BROWN)
    # labels
    s.callout(1, 462, 300, 540, 340)
    s.callout(2, 698, 280, 735, 360)
    s.callout(3, 380, 395, 300, 530)
    s.callout(4, 112, 528, 60, 450)
    s.callout(5, 400, 420, 440, 530)
    s.callout(6, 90, 200, 50, 330)
    return s


# ------------------------------------------------------------------ 4. a student's summary of Starling
def box(s, x, y, w, h, rows, n=None, fill=LIGHT, size=21, stroke=INK):
    s.rect(x - w / 2, y - h / 2, w, h, fill=fill, stroke=stroke, sw=2.5, rx=14)
    for i, r in enumerate(rows):
        s.text(x, y - (len(rows) - 1) * size * 0.7 + i * size * 1.4, r, size=size, weight=700)
    if n is not None:
        s.num(x + w / 2 - 2, y - h / 2 + 2, n, r=16)


def fig04():
    s = SVG(760, 700)
    s.text(380, 34, "مخطط الطالب: اكتشاف ستارلنج للهرمونات", size=25, weight=800, fill=PURPLE)
    box(s, 380, 98, 560, 58, ["وصول الطعام من المعدة إلى الاثني عشر"], 1, fill="#e0f2fe")
    s.arrow(380, 128, 380, 160)
    box(s, 380, 192, 560, 58, ["البنكرياس يفرز عصارته رغم قطع الاتصال العصبي بينه وبين الأعضاء"], 2, fill="#e0f2fe", size=19)
    s.arrow(380, 222, 380, 254)
    box(s, 380, 286, 560, 58, ["الاستنتاج: يوجد تنبيه عصبي للبنكرياس"], 3, fill="#e0f2fe")
    s.arrow(380, 316, 380, 348)
    box(s, 380, 380, 560, 58, ["الغشاء المخاطي المبطن للاثني عشر يفرز موادَّ كيميائية"], 4, fill="#e0f2fe")
    s.arrow(380, 410, 380, 474)
    s.tag(560, 442, "تنتقل عبر الأعصاب", size=20, fill="#e0f2fe", w=230)
    s.num(682, 442, 5, r=16)
    box(s, 380, 506, 560, 58, ["تنبيه البنكرياس فيفرز عصارته الهاضمة"], 6, fill="#e0f2fe")
    s.arrow(380, 536, 380, 568)
    box(s, 380, 610, 600, 76, ["سمّى ستارلنج هذه الرسائل الكيميائية «الهرمونات»", "وهي كلمة يونانية معناها «المواد المهدئة»"], 7, fill="#e0f2fe")
    return s


# ------------------------------------------------------------------ 5. kinds of glands
def acini(s, cx, cy, n=5, r=24, fill="#f9c74f", seed=0):
    pts = []
    for i in range(n):
        a = math.pi * (0.15 + 0.7 * i / max(n - 1, 1))
        x, y = cx + 52 * math.cos(a), cy + 46 * math.sin(a)
        pts.append((x, y))
        cell_ring(s, x, y, r * 0.35, r, 7, fill, nucleus="#9c6644")
    return pts


def capillary(s, d, w=11):
    s.path(d, "none", DARKRED, w + 3)
    s.path(d, "none", RED, w)
    s.path(d, "none", "#ff8a8a", 3, 'stroke-dasharray="3 10"')


def fig05():
    s = SVG(760, 600)
    for x in (380,):
        s.line(x, 20, x, 560, stroke=GRID, sw=3)
    s.line(20, 300, 740, 300, stroke=GRID, sw=3)
    # (أ) to the body surface
    s.panel(720, 38, "أ")
    s.rect(420, 70, 300, 34, fill=SKIN, stroke=INK, sw=2.5)
    s.text(650, 52, "سطح الجسم", size=19, fill=SOFT, weight=800)
    s.path("M560 104 L560 70", "none", "#3a86ff", 7)
    s.path("M560 200 L560 104", "none", "#3a86ff", 7)
    s.path("M560 200 c-30 0 -30 30 0 30 c30 0 30 30 0 30 c-30 0 -30 30 0 30 c30 0 30 -30 0 -30", "none", "#3a86ff", 10)
    for x, y in ((540, 56), (528, 44), (518, 60)):
        s.circle(x, y, 5, fill=SKY, stroke=BLUE, sw=1.5)
    # (ب) into a cavity inside the body
    s.panel(340, 38, "ب")
    s.rect(50, 64, 300, 56, fill="#ffe5ec", stroke=INK, sw=2.5, rx=28)
    s.text(200, 92, "تجويف داخل الجسم", size=19, fill=SOFT, weight=800)
    s.path("M200 120 L200 214", "none", GREEN, 7)
    acini(s, 200, 200, fill="#f9c74f")
    # (ج) no duct, capillaries
    s.panel(720, 330, "ج")
    for i, (x, y) in enumerate([(530, 430), (580, 410), (630, 432), (555, 470), (610, 476), (585, 445)]):
        s.path(blob(x, y, 24, 0.1, 7, seed=i + 3), "#c8b6ff", INK, 2)
        s.circle(x, y, 6, fill=PURPLE, stroke="none")
    capillary(s, "M450 380 C 520 360 560 400 690 370")
    capillary(s, "M450 520 C 520 500 600 540 690 505")
    s.arrow(585, 420, 585, 386, color=PURPLE, sw=3)
    s.arrow(600, 478, 600, 506, color=PURPLE, sw=3)
    # (د) two parts
    s.panel(340, 330, "د")
    s.path(blob(200, 455, 125, 0.06, 12, seed=9), "#fff1e6", INK, 2.5)
    acini(s, 150, 420, n=4, r=20, fill="#f9c74f")
    s.path("M150 440 L150 350 L230 350", "none", GREEN, 6)
    s.arrow(222, 350, 258, 350, color=GREEN, sw=4)
    for i, (x, y) in enumerate([(250, 470), (282, 488), (252, 505), (226, 488)]):
        s.path(blob(x, y, 16, 0.1, 7, seed=i + 20), "#c8b6ff", INK, 2)
    capillary(s, "M210 540 C 240 520 280 545 320 520", w=8)
    s.arrow(254, 508, 254, 527, color=PURPLE, sw=3)
    s.text(380, 586, "الأسهم: اتجاه خروج الإفراز", size=18, fill=SOFT, weight=700)
    return s


# ------------------------------------------------------------------ 6. the body map
def body_outline(s, x0=300):
    d = ("M{a} 30 C {b} 30 {c} 70 {c} 112 C {c} 150 {d} 172 {e} 182 L {e} 205 C {f} 215 {g} 225 {g} 262 "
         "L {h} 420 L {i} 425 L {j} 300 C {k} 420 {k} 520 {l} 610 C {m} 660 {n} 700 {a} 712 C {o} 700 {p} 660 {q} 610 "
         "C {r} 520 {r} 420 {s_} 300 L {t} 425 L {u} 420 L {v} 262 C {v} 225 {w} 215 {x} 205 L {x} 182 C {y} 172 {z} 150 {z} 112 "
         "C {z} 70 {aa} 30 {a} 30 Z")
    k = dict(a=x0, b=x0 + 40, c=x0 + 52, d=x0 + 40, e=x0 + 26, f=x0 + 70, g=x0 + 150, h=x0 + 190, i=x0 + 160, j=x0 + 118,
             k=x0 + 130, l=x0 + 140, m=x0 + 110, n=x0 + 50, o=x0 - 50, p=x0 - 110, q=x0 - 140, r=x0 - 130, s_=x0 - 118,
             t=x0 - 160, u=x0 - 190, v=x0 - 150, w=x0 - 70, x=x0 - 26, y=x0 - 40, z=x0 - 52, aa=x0 - 40)
    s.path(d.format(**k), "#fdf0e3", "#c9a27e", 3)


def fig06(labels=True):
    s = SVG(620, 760)
    x0 = 300
    body_outline(s, x0)
    s.ellipse(x0, 100, 40, 32, fill="#fde2e4", stroke="#e5989b", sw=2)   # brain
    s.circle(x0, 136, 7, fill=MAGENTA, stroke=INK, sw=2)                  # pituitary
    s.path("M%s 196 c-22 -14 -30 6 -22 18 c8 10 18 4 22 -2 c4 6 14 12 22 2 c8 -12 0 -32 -22 -18 Z" % x0, "#e63946", INK, 2)  # thyroid
    s.path("M%s 238 c-26 -6 -30 34 -6 46 c4 2 6 -4 6 -10 c0 6 2 12 6 10 c24 -12 20 -52 -6 -46 Z" % x0, "#e9edc9", INK, 2)  # thymus
    # kidneys (lower back) with the adrenal glands on top
    s.path("M%s 430 c-24 -2 -30 40 -10 64 c12 14 30 10 30 -8 c0 -18 -10 -24 -6 -34 c4 -12 2 -20 -14 -22 Z" % (x0 - 78), "#bc4749", INK, 2)
    s.path("M%s 430 c24 -2 30 40 10 64 c-12 14 -30 10 -30 -8 c0 -18 10 -24 6 -34 c-4 -12 -2 -20 14 -22 Z" % (x0 + 78), "#bc4749", INK, 2)
    s.path("M%s 432 q12 -24 32 -6 q-12 12 -32 6 Z" % (x0 - 96), YELLOW, INK, 2)
    s.path("M%s 432 q-12 -24 -32 -6 q12 12 32 6 Z" % (x0 + 96), YELLOW, INK, 2)
    # stomach (on the body's left = picture's right)
    s.path("M%s 262 L%s 292" % (x0 + 46, x0 + 48), "none", INK, 9)
    s.path("M%s 262 L%s 292" % (x0 + 46, x0 + 48), "none", "#ffb4a2", 5)
    s.path("M%s 290 C %s 276 %s 280 %s 312 C %s 346 %s 360 %s 358 C %s 356 %s 362 %s 360 C %s 352 %s 342 %s 344 C %s 344 %s 336 %s 318 C %s 304 %s 296 %s 292 Z" % (
        x0 + 40, x0 + 70, x0 + 108, x0 + 112, x0 + 114, x0 + 96, x0 + 72, x0 + 50, x0 + 28, x0 + 14,
        x0 + 8, x0 + 10, x0 + 22, x0 + 44, x0 + 58, x0 + 60, x0 + 60, x0 + 56, x0 + 54), "#ffb4a2", INK, 2)
    # pancreas below the stomach
    s.path("M%s 384 C %s 370 %s 366 %s 372 C %s 380 %s 390 %s 394 C %s 398 %s 398 %s 384 Z" % (x0 - 50, x0 - 10, x0 + 50, x0 + 96, x0 + 108, x0 + 80, x0 + 40, x0, x0 - 44, x0 - 50), "#f6bd60", INK, 2)
    s.ellipse(x0 - 46, 600, 14, 9, fill=LILAC, stroke=INK, sw=2)
    s.ellipse(x0 + 46, 600, 14, 9, fill=LILAC, stroke=INK, sw=2)
    if not labels:
        return s
    s.callout(1, x0 + 6, 136, 470, 110)
    s.callout(2, x0 + 16, 200, 470, 190)
    s.callout(3, x0 - 10, 258, 130, 250)
    s.callout(4, x0 + 80, 422, 520, 420)
    s.callout(5, x0 - 82, 470, 110, 500)
    s.callout(6, x0 - 10, 384, 110, 380)
    s.callout(7, x0 + 90, 320, 520, 290)
    s.callout(8, x0 + 52, 604, 500, 640)
    return s


# ------------------------------------------------------------------ 7. chemical nature of hormones
def fig07():
    s = SVG(760, 640)
    s.panel(730, 40, "أ")
    r = 40
    def ring(cx, cy):
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        s.poly(pts, fill=WHITE, stroke=INK, sw=3)
        s.circle(cx, cy, r * 0.55, fill="none", stroke=INK, sw=2)
        return pts
    ya = 150
    A = ring(200, ya)
    B = ring(390, ya)
    # left vertex of A: OH
    s.line(A[3][0], A[3][1], A[3][0] - 34, A[3][1], sw=3)
    s.text(A[3][0] - 58, A[3][1], "HO", size=24, weight=800, rtl=False)
    # O bridge
    s.line(A[0][0], A[0][1], 286, ya, sw=3)
    s.line(305, ya, B[3][0], B[3][1], sw=3)
    s.text(295, ya, "O", size=26, weight=800, fill=RED, rtl=False)
    # iodines next to the O-side / OH-side vertices
    for P in (A, B):
        for idx, dy in ((4, -1), (2, 1)):
            x, y = P[idx]
            x2, y2 = x - 14, y + dy * 30
            s.line(x, y, x2, y2, sw=3)
            s.circle(x2 - 4, y2 + dy * 16, 17, fill="#e9d5ff", stroke=PURPLE, sw=2.5)
            s.text(x2 - 4, y2 + dy * 16 + 1, "I", size=24, weight=800, fill=PURPLE, rtl=False)
    # side chain
    x, y = B[0]
    s.line(x, y, x + 30, y - 18, sw=3)
    s.line(x + 30, y - 18, x + 60, y, sw=3)
    s.line(x + 60, y, x + 60, y + 30, sw=3)
    s.text(x + 60, y + 48, "NH₂", size=22, weight=800, rtl=False, fill=BLUE)
    s.line(x + 60, y, x + 92, y - 18, sw=3)
    s.text(x + 136, y - 18, "COOH", size=22, weight=800, rtl=False, fill=RED)
    s.text(380, 262, "جزيء يحتوي على أربع ذرات من عنصر (I)", size=20, fill=SOFT, weight=700)
    s.line(30, 296, 730, 296, stroke=GRID, sw=3)
    # (ب) steroid nucleus
    s.panel(730, 330, "ب")
    sd = 42
    c30 = math.cos(math.radians(30))
    def hexp(cx, cy):
        return [(cx + sd * math.cos(math.radians(a)), cy + sd * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
    ax, ay = 480, 520
    rings = [(ax, ay), (ax + 2 * sd * c30, ay), (ax + 3 * sd * c30, ay - 1.5 * sd)]
    fills = ["#ffe5ec", "#fff3b0", "#d8f3dc"]
    for (cx, cy), fl in zip(rings, fills):
        s.poly(hexp(cx, cy), fill=fl, stroke=INK, sw=3)
    cx, cy = rings[2]
    x1 = cx + sd * c30
    ytop, ybot = cy - sd / 2, cy + sd / 2
    R = sd / (2 * math.sin(math.radians(36)))
    ap = sd / (2 * math.tan(math.radians(36)))
    pc = (x1 + ap, cy)
    pent = [(pc[0] + R * math.cos(math.radians(a)), pc[1] + R * math.sin(math.radians(a))) for a in (216, 288, 0, 72, 144)]
    s.poly(pent, fill="#dbeafe", stroke=INK, sw=3)
    for (x, y), lab in zip(rings + [pc], "ABCD"):
        s.text(x, y, lab, size=20, weight=800, fill=SOFT, rtl=False)
    s.text(560, 600, "أربع حلقات متصلة", size=20, fill=SOFT, weight=700)
    s.line(380, 316, 380, 620, stroke=GRID, sw=3)
    # (ج) a long chain of amino acids
    s.panel(345, 330, "ج")
    cols = [RED, ORANGE, YELLOW, LIME, TEAL, BLUE, PURPLE, MAGENTA]
    pts = []
    for i in range(16):
        t = i / 15
        x = 60 + 270 * t
        y = 470 + 60 * math.sin(t * 3.2 * math.pi) * (0.5 + 0.5 * math.cos(t * 2))
        pts.append((x, y))
    s.path(smooth(pts), "none", INK, 3)
    for i, (x, y) in enumerate(pts):
        s.circle(x, y, 13, fill=cols[i % len(cols)], stroke=INK, sw=2)
    s.circle(70, 590, 13, fill=RED, stroke=INK, sw=2)
    s.text(96, 591, "= حمض أميني واحد", size=20, anchor="start", rtl=False, weight=700, extra='direction="rtl"')
    return s


# ------------------------------------------------------------------ 8–10. the pituitary gland
def pituitary(s, ox=0, oy=0, k=1.0, labels=True, neurons=True):
    def P(x, y):
        return ox + x * k, oy + y * k
    def d(path):
        out = []
        for tok in path.split():
            if "," in tok:
                x, y = tok.split(",")
                X, Y = P(float(x), float(y))
                out.append("%s,%s" % (f(X), f(Y)))
            else:
                out.append(tok)
        return " ".join(out)
    # base of the brain (hypothalamus)
    s.path(d("M 40,40 C 120,10 480,10 560,40 L 560,190 C 470,210 420,200 395,215 L 335,215 C 300,200 230,212 40,190 Z"), "#fde2c8", "#c9a27e", 3)
    # infundibulum (stalk)
    s.path(d("M 335,213 C 340,250 345,270 342,300 L 382,300 C 382,270 390,240 397,213 Z"), "#d9c2f0", INK, 2.5)
    # anterior lobe
    s.path(d("M 335,300 C 250,280 150,310 150,400 C 150,500 250,540 320,520 C 335,515 338,470 338,420 C 338,370 342,320 335,300 Z"), "#ffadc6", INK, 3)
    # middle lobe (thin band)
    s.path(d("M 335,300 C 342,320 338,370 338,420 C 338,470 335,515 320,520 C 335,524 352,518 356,505 C 360,470 358,370 352,312 C 350,304 344,300 335,300 Z"), "#ffd6a5", INK, 2.5)
    # posterior lobe
    s.path(d("M 352,300 C 420,290 520,330 520,410 C 520,490 440,525 356,505 C 360,470 358,370 352,312 Z"), "#e2d4f7", INK, 3)
    if neurons:
        for i, (x, y) in enumerate(((300, 110), (370, 90), (440, 120))):
            X, Y = P(x, y)
            s.path(d("M %s,%s C %s,%s %s,%s %s,%s C %s,%s %s,%s %s,%s" % (
                x, y + 14, x, y + 60, 360 + i * 8, 180, 362 + i * 8, 240, 362 + i * 8, 300, 400 + i * 30, 340, 410 + i * 30, 405)), "none", PURPLE, 3 * k + 0.5)
            s.circle(X, Y, 18 * k, fill="#b197fc", stroke=INK, sw=2)
            s.circle(X, Y, 7 * k, fill=PURPLE, stroke="none")
            ex, ey = P(410 + i * 30, 410)
            s.circle(ex, ey, 10 * k, fill="#9d4edd", stroke=INK, sw=1.5)
            for j in range(3):
                s.circle(ex - 3 * k + j * 3 * k, ey - 2 * k + (j % 2) * 4 * k, 2 * k, fill=YELLOW, stroke="none")
        # capillary in the posterior lobe
        s.path(d("M 380,470 C 420,440 470,470 505,440"), "none", DARKRED, 9 * k + 2)
        s.path(d("M 380,470 C 420,440 470,470 505,440"), "none", RED, 7 * k)
    return P


def fig08():
    s = SVG(720, 600)
    P = pituitary(s, ox=40, oy=20, k=1.0)
    s.text(110, 560, "الأمام", size=20, weight=800, fill=SOFT)
    s.arrow(70, 586, 30, 586, color=SOFT, sw=3)
    s.callout(1, *P(300, 110), *P(150, 80))
    s.callout(2, *P(366, 260), *P(520, 250))
    s.callout(3, *P(230, 420), *P(100, 450))
    s.callout(4, *P(346, 440), *P(250, 560))
    s.callout(5, *P(480, 360), *P(590, 330))
    s.callout(6, *P(470, 410), *P(600, 420))
    s.callout(7, *P(495, 446), *P(580, 520))
    return s


def fig09():
    s = SVG(840, 700)
    P = pituitary(s, ox=-10, oy=120, k=0.58, neurons=False)
    s.text(160, 100, "رسم الطالب", size=24, weight=800, fill=PURPLE)
    rows = [
        ("القمع (الساق العصبية): جزء من المخ", "يصل الغدة النخامية بتحت المهاد"),
        ("الجزء الغدي (الفص الأمامي والفص الأوسط):", "يفرز هرمون النمو والبرولاكتين"),
        ("الفص الأوسط:", "جزء من الجزء العصبي للغدة"),
        ("الفص الخلفي: تتكون فيه هرمونات", "الأوكسيتوسين والمضاد لإدرار البول"),
        ("TSH و ACTH:", "من هرمونات الجزء العصبي للغدة"),
    ]
    targets = [P(366, 255), P(220, 420), P(342, 500), P(470, 470), P(440, 500)]
    for i, ((a, b), (tx, ty)) in enumerate(zip(rows, targets)):
        y = 90 + i * 122
        s.rect(370, y - 46, 450, 96, fill="#f8f9ff", stroke=INK, sw=2.5, rx=14)
        s.text(595, y - 14, a, size=20, weight=800)
        s.text(595, y + 20, b, size=20, weight=700)
        s.num(820, y - 46, i + 1, r=17)
        s.line(370, y, tx, ty, stroke=GREY, sw=2, dash="5 5")
        s.circle(tx, ty, 4, fill=INK, stroke=INK, sw=1)
    return s


def fig10():
    s = SVG(780, 640)
    def node(x, y, w, h, text, n=None, fill=LIGHT, size=20):
        s.rect(x - w / 2, y - h / 2, w, h, fill=fill, stroke=INK, sw=2.5, rx=14)
        s.text(x, y + 1, text, size=size, weight=700)
        if n is not None:
            s.num(x + w / 2, y - h / 2 + 2, n, r=16)
    node(390, 46, 380, 56, "الغدة النخامية (سيدة الغدد)", fill="#ffd6e0", size=23)
    s.line(390, 74, 390, 100); s.line(200, 100, 580, 100)
    s.arrow(580, 100, 580, 126); s.arrow(200, 100, 200, 126)
    node(580, 160, 340, 64, "الجزء الغدي = ...(1)... + ...(2)...", fill="#fff1c1")
    node(200, 160, 340, 64, "الجزء العصبي = ...(3)... + القمع", fill="#e7dcff")
    ys = [250, 320, 390, 460, 530]
    texts = ["هرمون النمو ← نمو الجسم", "...(4)... ← ينشط الغدة الدرقية", "ACTH ← ينشط ...(5)...",
             "...(6)... و LH ← الغدد التناسلية", "...(7)... ← إنتاج اللبن"]
    nums = [None] * 5
    s.line(580, 192, 580, 530 + 0)
    for y, t, n in zip(ys, texts, nums):
        s.line(580, y, 600, y)
        node(600 + 0, y, 330, 54, t, n, fill="#fffbe6", size=20)
    s.line(200, 192, 200, 320)
    for y, t, n in zip((250, 320), ("...(8)... ← يقلل كمية البول", "الأوكسيتوسين ← انقباض الرحم"), (None, None)):
        node(200, y, 330, 54, t, n, fill="#f3edff", size=20)
    s.text(200, 600, "أكمل الفراغات المرقمة", size=21, fill=SOFT, weight=800)
    return s


# ------------------------------------------------------------------ 11. trophic hormones
def thyroid_icon(s, x, y, k=1.0):
    s.rect(x - 8 * k, y - 50 * k, 16 * k, 100 * k, fill="#e0e7ff", stroke=INK, sw=2, rx=6)
    for i in range(6):
        s.line(x - 8 * k, y - 40 * k + i * 16 * k, x + 8 * k, y - 40 * k + i * 16 * k, stroke=GREY, sw=1.5)
    s.path("M%s %s c-40 -30 -60 10 -50 40 c8 24 34 22 50 6 Z" % (f(x - 4 * k), f(y - 20 * k)), "#e63946", INK, 2)
    s.path("M%s %s c40 -30 60 10 50 40 c-8 24 -34 22 -50 6 Z" % (f(x + 4 * k), f(y - 20 * k)), "#e63946", INK, 2)
    s.rect(x - 14 * k, y + 2 * k, 28 * k, 12 * k, fill="#e63946", stroke=INK, sw=2, rx=5)


def adrenal_icon(s, x, y, k=1.0):
    s.path("M%s %s c-36 0 -46 60 -20 96 c16 22 44 18 46 -6 c2 -22 -12 -30 -8 -48 c4 -18 2 -42 -18 -42 Z" % (f(x), f(y)), "#bc4749", INK, 2.5)
    s.path("M%s %s c-30 -6 -42 -40 -6 -54 c30 -10 50 20 40 44 c-6 12 -18 14 -34 10 Z" % (f(x - 2), f(y + 4)), YELLOW, INK, 2.5)
    s.path("M%s %s c-14 -4 -20 -24 -2 -30 c16 -4 24 12 18 24 c-4 6 -8 8 -16 6 Z" % (f(x - 2), f(y - 8)), ORANGE, INK, 2)


def ovary_icon(s, x, y, kind):
    s.ellipse(x, y, 70, 46, fill="#ffe5ec", stroke=INK, sw=2.5)
    if kind == "follicles":
        for (dx, dy, r) in ((-40, -10, 8), (-22, 18, 10), (2, -20, 13)):
            s.circle(x + dx, y + dy, r, fill="#fff", stroke=PINK, sw=2)
            s.circle(x + dx, y + dy, r * 0.35, fill=MAGENTA, stroke="none")
        s.circle(x + 34, y + 6, 24, fill="#fff7d6", stroke=ORANGE, sw=3)
        s.circle(x + 26, y + 0, 6, fill=MAGENTA, stroke="none")
    else:
        s.circle(x + 18, y, 28, fill="#ffd60a", stroke="#c99700", sw=3)
        for i in range(10):
            a = 2 * math.pi * i / 10
            s.circle(x + 18 + 16 * math.cos(a), y + 16 * math.sin(a), 4, fill="#e0a800", stroke="none")
        s.circle(x - 36, y + 10, 9, fill="#fff", stroke=PINK, sw=2)


def fig11():
    s = SVG(820, 560)
    s.ellipse(410, 72, 58, 44, fill="#ffadc6", stroke=INK, sw=3)
    s.text(410, 140, "الجزء الغدي للغدة النخامية", size=21, weight=800)
    tx = [105, 310, 515, 715]
    labels = ["س", "ص", "ع", "ل"]
    cols = [RED, ORANGE, MAGENTA, "#c99700"]
    for x, lab, col in zip(tx, labels, cols):
        s.arrow(410 + (x - 410) * 0.12, 160, x, 285, color=col, sw=4.5)
        mx, my = 410 + (x - 410) * 0.56, 222
        s.circle(mx, my, 20, fill=WHITE, stroke=col, sw=3)
        s.text(mx, my + 1, lab, size=24, weight=800, fill=col)
    thyroid_icon(s, 105, 370)
    s.lines(105, 460, ["الغدة الدرقية"], size=18, weight=800)
    adrenal_icon(s, 318, 330)
    s.lines(310, 460, ["الغدة الكظرية"], size=18, weight=800)
    ovary_icon(s, 515, 360, "follicles")
    s.lines(515, 460, ["المبيض"], size=18, weight=800)
    ovary_icon(s, 715, 360, "luteum")
    s.lines(715, 460, ["المبيض"], size=18, weight=800)
    return s


# ------------------------------------------------------------------ 12. growth curves
def fig12():
    s = SVG(760, 560)
    ax = Axes(s, 120, 50, 560, 400, (0, 20), (40, 230), "العمر (بالسنوات)", "الطول (سم)",
              [(v, str(v)) for v in range(0, 21, 4)], [(v, str(v)) for v in range(40, 231, 30)])
    A = [(0, 50), (2, 87), (5, 110), (8, 128), (11, 145), (13, 156), (15, 168), (17, 174), (20, 175)]
    B = [(0, 50), (2, 76), (5, 88), (8, 97), (11, 105), (13, 110), (15, 115), (17, 117), (20, 118)]
    C = [(0, 50), (2, 92), (5, 122), (8, 146), (11, 168), (13, 183), (15, 199), (17, 212), (20, 218)]
    for pts, col, lab in ((A, BLUE, "أ"), (B, ORANGE, "ب"), (C, PURPLE, "ج")):
        ax.curve(pts, col, 5)
        ax.end_label(pts, "(" + lab + ")", col, dx=30)
    s.text(400, 30, "منحنيات توضيحية للنمو في الطول لثلاثة أشخاص", size=21, weight=800, fill=SOFT)
    return s


QUESTIONS = [
    dict(diff="very-hard", draw=fig01,
         alt="أربع سيقان نباتات صغيرة في أصص (أ، ب، ج، د) يسقط عليها الضوء من جانب واحد؛ الساق (ب) أُزيلت قمتها، و(ج) بها حاجز أسود أسفل القمة، و(د) بين قمتها وباقي الساق طبقة صفراء.",
         prompt="""يوضح الشكل أربع سيقان نباتات صغيرة متماثلة، أُضيئت كلها من جانب واحد. توقّع أيها ينحني نحو الضوء وأيها لا ينحني، مع تفسير كل حالة في ضوء تفسير بويسن جنسن، ثم حدّد في الساق (أ) منطقة الاستقبال ومنطقة الاستجابة.""",
         answer="""• (أ) تنحني نحو الضوء: القمة النامية تفرز مادة كيميائية (إندول حمض الخليك – الأوكسين) تنتقل إلى منطقة الانحناء فتنحني.
• (ب) لا تنحني: أُزيلت القمة النامية التي تفرز المادة الكيميائية.
• (ج) لا تنحني: الحاجز لا تنفذ منه المواد الكيميائية، فلا تصل المادة من القمة إلى منطقة الانحناء.
• (د) تنحني نحو الضوء: المادة الكيميائية تنفذ من الطبقة الرقيقة فتصل إلى منطقة الانحناء.
• في الساق (أ): منطقة الاستقبال = القمة النامية للساق، ومنطقة الاستجابة = منطقة الانحناء أسفلها."""),
    dict(diff="hard", draw=fig02,
         alt="نبات زهري في أصيص عليه أرقام: 1 قمة الساق، 2 تركيب صغير عند قاعدة ورقة، 3 قوس على الساق أسفل القمة، 4 زهرة، 5 ثمرة، 6 ورقة.",
         prompt="""حدّد رقمي الجزأين اللذين تُفرز منهما الأوكسينات وفقًا للكتاب، ثم اربط كلًّا من الأجزاء (3) و(4) و(5) بوظيفة للأوكسينات تظهر فيه. ثم علّل من الشكل: لا يحتاج النبات إلى غدد خاصة لإفراز الأوكسينات.""",
         answer="""• تُفرز الأوكسينات من الجزأين (1) القمة النامية و(2) البرعم؛ لأنها تفرزها خلايا حية في القمم النامية والبراعم.
• (3) منطقة الانحناء (منطقة الاستجابة): تنحني نحو الضوء، فالأوكسينات تنظم نمو الأنسجة.
• (4) الزهرة: تتحكم الأوكسينات في تفتح الأزهار.
• (5) الثمرة: تتحكم الأوكسينات في تكوين الثمار ونضجها.
• لا يحتاج النبات إلى غدد خاصة: لأن الأوكسينات تفرزها خلايا حية في القمة النامية (1) والبراعم (2)، ثم تنتقل منها إلى مناطق أخرى مثل منطقة الانحناء (3) فتؤثر فيها."""),
    dict(diff="very-hard", draw=fig03,
         alt="رسم للمعدة والاثني عشر والبنكرياس: عصب مقطوع متجه إلى البنكرياس، ووعاء دموي يخرج من جدار الاثني عشر إلى الدورة الدموية ثم يعود إلى البنكرياس، وقناة من البنكرياس إلى الاثني عشر؛ الأجزاء مرقمة من 1 إلى 6.",
         prompt="""يمثل الشكل فكرة تجربة ستارلنج. حدّد بالأرقام: الجزء الذي أفرز الرسائل الكيميائية، والطريق الذي انتقلت فيه، والعضو الذي استجاب لها، والطريق الذي تصل به العصارة الناتجة إلى الاثني عشر، ثم سمِّ الجزء (4) وعلّل قطع ستارلنج له. ثم توقّع ماذا كان سيحدث عند وصول الطعام إلى الاثني عشر لو رُبط الوعاء الدموي (2) مع بقاء الجزء (4) مقطوعًا، مع التعليل.""",
         answer="""• (1) الغشاء المخاطي المبطن للاثني عشر: أفرز الرسائل الكيميائية (الهرمونات).
• (2) الدم (الوعاء الدموي): الطريق الذي انتقلت فيه.
• (3) البنكرياس: العضو الذي استجاب فأفرز عصارته.
• (4) العصب (الاتصال العصبي بين البنكرياس والأعضاء الأخرى): قطعه ستارلنج ليستبعد التنبيه العصبي، فإذا أفرز البنكرياس رغم ذلك كان المنبه غير عصبي.
• (5) القناة البنكرياسية: تصل بها العصارة إلى الاثني عشر.
• التوقع: لن يفرز البنكرياس عصارته؛ لأن الطريق العصبي مقطوع، والطريق الكيميائي (الدم) مسدود، فلا تصل الرسائل الكيميائية إلى البنكرياس."""),
    dict(diff="hard", draw=fig04,
         alt="مخطط من سبعة مربعات مرقمة يلخص اكتشاف ستارلنج كما كتبه طالب، وبين المربعين 4 و6 سهم عليه عبارة مرقمة بالرقم 5.",
         prompt="""لخّص طالب اكتشاف ستارلنج في المخطط الموضح، فوقع في ثلاثة أخطاء علمية. حدّد أرقام المربعات التي بها خطأ، وصحّح كل خطأ مع التعليل.""",
         answer="""• (3) خطأ: الصواب «يوجد تنبيه غير عصبي للبنكرياس»؛ لأن البنكرياس أفرز عصارته رغم قطع الاتصال العصبي.
• (5) خطأ: الصواب «تنتقل مع الدم إلى البنكرياس»؛ فالأعصاب كانت مقطوعة.
• (7) خطأ: الصواب أن «الهرمونات» كلمة يونانية معناها «المواد المنشطة»؛ لأنها نشطت البنكرياس لإفراز عصارته."""),
    dict(diff="hard", draw=fig05,
         alt="أربعة رسوم لغدد: (أ) غدة لها قناة تفتح على سطح الجسم، (ب) غدة لها قناة تفتح في تجويف داخل الجسم، (ج) مجموعة خلايا بلا قنوات بين أوعية دموية، (د) غدة بها جزء له قناة وجزء من خلايا بجوار وعاء دموي.",
         prompt="""صنّف الغدد (أ) و(ب) و(ج) و(د) حسب طريقة صب إفرازها، واذكر مثالًا من الكتاب لكلٍّ منها، ثم حدّد الغدد التي تفرز هرمونات أو تحتوي على جزء يفرز هرمونات، مع التعليل من الشكل.""",
         answer="""• (أ) غدة قنوية تصب إفرازها خارج الجسم، مثل الغدد العرقية.
• (ب) غدة قنوية تصب إفرازها داخل الجسم، مثل الغدد اللعابية والهاضمة.
• (ج) غدة صماء (لاقنوية) تصب إفرازها في الدم مباشرة، مثل الغدة الدرقية والغدة الكظرية.
• (د) غدة مختلطة (مزدوجة): جزء قنوي وجزء لاقنوي، مثل البنكرياس.
• تفرز الهرمونات: (ج)، والجزء اللاقنوي من (د)؛ لأن الإفراز فيهما يخرج إلى الأوعية الدموية مباشرة دون قنوات."""),
    dict(diff="very-hard", draw=fig06,
         alt="شكل تخطيطي لجسم الإنسان عليه ثمانية أعضاء وغدد مرقمة من 1 إلى 8 في الرأس والعنق والصدر والبطن والحوض.",
         prompt="""يوضح الشكل مواضع بعض الغدد والأعضاء في جسم الإنسان. حدّد بالرقم والاسم: (أ) الغدة المختلطة، (ب) الغدة التي يلزم اليود لتكوين أحد هرمونيها، (ج) الغدة التي تنشط بهرموناتها الغدتين (2) و(8) والطبقة الخارجية للغدة (4)، (د) العضو الذي ليس غدة صماء لكن بطانته تفرز هرمونًا، مع ذكر اسم الهرمون، (هـ) العضو الذي يعمل فيه كلٌّ من الألدوستيرون والهرمون المضاد لإدرار البول.""",
         answer="""• (أ) رقم (6): البنكرياس.
• (ب) رقم (2): الغدة الدرقية (هرمون الثيروكسين).
• (ج) رقم (1): الغدة النخامية؛ تفرز TSH للدرقية، وFSH وLH للغدد التناسلية (8)، وACTH لقشرة الغدة الكظرية (4).
• (د) رقم (7): المعدة؛ تفرز خلايا لاقنوية في بطانتها هرمون الجاسترين.
• (هـ) رقم (5): الكلية."""),
    dict(diff="very-hard", draw=fig07,
         alt="ثلاثة نماذج كيميائية: (أ) جزيء من حلقتين بهما أربع ذرات من العنصر I، (ب) أربع حلقات متصلة، (ج) سلسلة طويلة من الكرات الملونة كل كرة تمثل حمضًا أمينيًّا.",
         prompt="""يمثل الشكل نماذج للتركيب الكيميائي لثلاث مواد هرمونية. (1) ما الهرمون الممثل في (أ)؟ وما الغدة التي تفرزه؟ وما الدليل في الشكل؟ وماذا يحدث لهذه الغدة إذا نقص هذا العنصر في الغذاء والماء والهواء؟ (2) يمثل (ب) الستيرويدات: ما الغدة التي تفرز «هرمونات كثيرة» من هذا النوع؟ واذكر هرمونًا واحدًا منها ووظيفته. (3) ما الطبيعة الكيميائية التي يمثلها (ج)؟ واذكر الأنواع الثلاثة للطبيعة الكيميائية للهرمونات كما وردت في الكتاب.""",
         answer="""(1)
• الثيروكسين، وتفرزه الغدة الدرقية.
• الدليل: احتواؤه على ذرات اليود (I)، واليود لازم لتكوين الثيروكسين.
• نقص اليود ← نقص الثيروكسين ← تضخم الغدة (الجويتر البسيط).
(2) قشرة الغدة الكظرية؛ مثال: الألدوستيرون ← يحافظ على التوازن المعدني (إعادة امتصاص الصوديوم والتخلص من البوتاسيوم الزائد). (ويُقبل: الكورتيزون ← تنظيم أيض الكربوهيدرات.)
(3) (ج) بروتين معقد (سلسلة طويلة من الأحماض الأمينية).
الأنواع الثلاثة: الهرمونات مواد كيميائية عضوية:
• بعضها بروتينات معقدة.
• وبعضها مركبات بسيطة مثل الأحماض الأمينية.
• وبعضها ستيرويدات (مواد دهنية)."""),
    dict(diff="hard", draw=fig08,
         alt="قطاع طولي في الغدة النخامية متصلة بقاعدة المخ؛ تظهر خلايا عصبية تمتد أليافها في الساق إلى الفص الخلفي، والأجزاء مرقمة من 1 إلى 7.",
         prompt="""يمثل الشكل قطاعًا طوليًّا في الغدة النخامية واتصالها بالمخ. حدّد رقم المكان الذي: يتكون فيه الأوكسيتوسين، ويمر فيه، ويُخزن فيه، ويدخل منه إلى الدم. ثم توقّع: إذا قُطع الجزء (2) فماذا يحدث لإطلاق الهرمون المضاد لإدرار البول ولكمية البول؟ ولماذا؟""",
         answer="""• يتكون الأوكسيتوسين في (1): الخلايا العصبية في تحت المهاد.
• يمر في (2): القمع (الساق العصبية)، إلى الفص الخلفي (5).
• يُخزن في (6): نهايات هذه الخلايا العصبية في الفص الخلفي.
• يدخل إلى الدم عن طريق (7): الشعيرات الدموية، عند الحاجة.
• قطع (2): لا يصل الهرمون المضاد لإدرار البول من تحت المهاد إلى الفص الخلفي، فيقل إطلاقه في الدم ← يقل إعادة امتصاص الماء في أنابيب النفرونات ← تزيد كمية البول."""),
    dict(diff="very-hard", draw=fig09,
         alt="رسم للغدة النخامية بجانبه خمس عبارات مرقمة كتبها طالب، يشير كل منها إلى جزء من الغدة.",
         prompt="""رسم طالب الغدة النخامية وكتب عليها خمس عبارات، ثلاث منها خاطئة علميًّا. حدّد أرقام العبارات الخاطئة، وصحّح كلًّا منها.""",
         answer="""• (3) خطأ: الفص الأوسط جزء من الجزء الغدي (مع الفص الأمامي)، أما الجزء العصبي فيتكون من الفص الخلفي والقمع.
• (4) خطأ: الأوكسيتوسين والهرمون المضاد لإدرار البول يتكونان في خلايا عصبية في تحت المهاد، ويُخزنان في نهاياتها في الفص الخلفي ثم يُطلقان منه.
• (5) خطأ: TSH وACTH من هرمونات الجزء الغدي (الهرمونات المنشطة للغدد).
• العبارتان (1) و(2) صحيحتان."""),
    dict(diff="hard", draw=fig10,
         alt="مخطط شجري للغدة النخامية وجزأيها وهرموناتها، به فراغات مرقمة من 1 إلى 8.",
         prompt="""أكمل المخطط بكتابة ما يدل عليه كل رقم من (1) إلى (8)، ثم اذكر الاسم الآخر للهرمون (8) وعلّل هذه التسمية، وتوقّع أثر نقص الهرمون (6) وحده في الخصية.""",
         answer="""• (1) الفص الأمامي، و(2) الفص الأوسط.
• (3) الفص الخلفي.
• (4) TSH (الهرمون المنشط للغدة الدرقية).
• (5) قشرة الغدة الكظرية.
• (6) FSH (الهرمون المنشط لتكوين الحويصلات).
• (7) البرولاكتين (الهرمون المنشط لإفراز اللبن).
• (8) الهرمون المضاد لإدرار البول.
الاسم الآخر: الهرمون القابض للأوعية الدموية (الفازوبريسين)؛ لأنه يرفع ضغط الدم.
• نقص (6) FSH في الخصية: يتأثر تكوين الأنابيب المنوية والحيوانات المنوية، لأنه يساعد على تكوينها."""),
    dict(diff="very-hard", draw=fig11,
         alt="رسم يوضح أربعة أسهم (س، ص، ع، ل) تخرج من الجزء الغدي للغدة النخامية إلى: الغدة الدرقية، والطبقة الخارجية للغدة الكظرية، ومبيض به حويصلات، ومبيض به تركيب أصفر كبير.",
         prompt="""يوضح الشكل أربعة هرمونات (س، ص، ع، ل) يفرزها الجزء الغدي للغدة النخامية، ورأس كل سهم عند التركيب الذي ينشطه. حدّد الهرمونات الأربعة مستدلًّا بالتركيب الذي يصل إليه كل سهم، ثم توقّع ما يحدث لهرمونات الغدة الكظرية إذا توقف إفراز الهرمون (ص)، مميزًا بين القشرة والنخاع.""",
         answer="""• (س) TSH: يصل إلى الغدة الدرقية.
• (ص) ACTH: يصل إلى قشرة الغدة الكظرية (الطبقة الخارجية).
• (ع) FSH: يصل إلى الحويصلات النامية فينميها ويحولها إلى حويصلات جراف.
• (ل) LH: يصل إلى الجسم الأصفر فينشط تكوينه.
• عند توقف (ص): يتوقف تنشيط قشرة الغدة الكظرية فيقل إفرازها لهرموناتها (الستيرويدات)؛ أما النخاع (الأدرينالين والنورأدرينالين) فلا يتأثر بذلك، لأن ACTH ينشط القشرة فقط."""),
    dict(diff="hard", draw=fig12,
         alt="رسم بياني للطول بالسنتيمتر مقابل العمر بالسنوات لثلاثة أشخاص (أ، ب، ج)؛ منحنى (ج) أعلاها و(ب) أدناها.",
         prompt="""يمثل الشكل منحنيات توضيحية للنمو في الطول لثلاثة أشخاص. أي المنحنيات يمثل نموًّا طبيعيًّا؟ وما حالة كلٍّ من الشخصين الآخرين؟ وما الهرمون المسؤول؟ وما الخلل في إفرازه؟ وفي أي مرحلة عمرية بدأ الخلل وفق الشكل؟ ثم فسّر كيف يتحكم هذا الهرمون في نمو الجسم.""",
         answer="""• (أ) نمو طبيعي.
• (ب) القزامة: نقص إفراز هرمون النمو في الصغر.
• (ج) العملقة: زيادة إفراز هرمون النمو في الصغر.
• بدأ الخلل في الطفولة؛ إذ يبتعد المنحنيان عن المنحنى الطبيعي منذ السنوات الأولى من العمر.
• هرمون النمو يُفرز من الجزء الغدي للغدة النخامية، ويتحكم في عمليات الأيض وخاصة تخليق البروتين؛ فيتحكم في نمو الجسم."""),
]
