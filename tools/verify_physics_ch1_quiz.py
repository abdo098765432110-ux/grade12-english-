"""Checks the answers of the Physics Chapter 1 quiz (development tool).

Every question of the quiz "physics-ch1-quiz-1" in quizzes-physics.json is
solved here twice, by two different methods, and each wrong choice is worked
out from the student mistake it stands for. The script stops with an error if
the two methods disagree, if the answer in the file is not the one both
methods give, or if a wrong choice is not what its mistake gives.

Run from the website folder:  python3 tools/verify_physics_ch1_quiz.py
Needs Python 3 only (fractions for exact arithmetic)."""
import json
import math
import pathlib
import random
from fractions import Fraction as F

SITE = pathlib.Path(__file__).resolve().parent.parent
QUIZ = next(q for q in json.loads((SITE / "quizzes-physics.json").read_text(encoding="utf-8"))["quizzes"]
            if q["id"] == "physics-ch1-quiz-1")
E = F(16, 10) * F(1, 10 ** 19)          # charge of an electron, C
report = []


def check(number, method1, method2, expected_index, choices, note=""):
    """method1 == method2 == the choice at expected_index; the other choices differ."""
    question = QUIZ["questions"][number - 1]
    assert method1 == method2, "Q%d: the two methods disagree: %r / %r" % (number, method1, method2)
    assert question["correctIndex"] == expected_index, "Q%d: correctIndex in the file is %d, expected %d" % (
        number, question["correctIndex"], expected_index)
    assert choices[expected_index] == method1, "Q%d: the right choice is not the computed answer" % number
    others = [c for i, c in enumerate(choices) if i != expected_index]
    assert method1 not in others and len(set(map(str, choices))) == len(choices), "Q%d: two choices are the same" % number
    report.append("Q%-2d answer %s  (%s)  %s" % (number, "أبجد"[expected_index], method1, note))


def exact_sqrt(value):
    """√ of a fraction whose top and bottom are perfect squares."""
    top, bottom = math.isqrt(value.numerator), math.isqrt(value.denominator)
    assert top * top == value.numerator and bottom * bottom == value.denominator, value
    return F(top, bottom)


def parallel(*rs):
    return 1 / sum(1 / r for r in rs)


def solve(matrix, vector):
    """Exact Gaussian elimination with fractions."""
    n = len(vector)
    m = [[F(x) for x in row] + [F(v)] for row, v in zip(matrix, vector)]
    for c in range(n):
        p = next(r for r in range(c, n) if m[r][c] != 0)
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c and m[r][c] != 0:
                k = m[r][c] / m[c][c]
                m[r] = [a - k * b for a, b in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def equivalent_resistance(nodes, resistors, a, b):
    """Nodal analysis: 1 A into a, out of b (b at 0 V); R = V(a)."""
    unknown = [n for n in nodes if n != b]
    idx = {n: i for i, n in enumerate(unknown)}
    g = [[F(0)] * len(unknown) for _ in unknown]
    for x, y, r in resistors:
        for p, q in ((x, y), (y, x)):
            if p in idx:
                g[idx[p]][idx[p]] += 1 / F(r)
                if q in idx:
                    g[idx[p]][idx[q]] -= 1 / F(r)
    current = [F(1) if n == a else F(0) for n in unknown]
    return solve(g, current)[idx[a]]


# Q1 — electrons per second through any cross-section of X or Y (series: one current)
I = F(8, 10)
m1 = I / E                                    # n/t = I/e
m2 = (I * 1) / E / 1                          # charge in 1 s, then number of charges
check(1, ("same", m1, "opposite to current"), ("same", m2, "opposite to current"), 2,
      [("less in Y", m1, "-"), ("more in Y", None, "-"), ("same", m1, "opposite to current"), ("same", m1, "with the current")],
      "n/t = %.1e electrons per second" % float(m1))

# Q2 — cut 1 : 3, stretch the short part to the long part's length, then in parallel (answer in units of R)
R = F(1)
m1 = parallel(9 * (R / 4), 3 * R / 4)                                # n² rule
rho, L, A = F(1), F(4), F(1)                                         # method 2: real dimensions (R = 4)
short_A = A * (L / 4) / (3 * L / 4)                                  # same volume
m2 = parallel(rho * (3 * L / 4) / short_A, rho * (3 * L / 4) / A) / (rho * L / A)
check(2, m1, m2, 0, [m1, parallel(3 * R / 4, 3 * R / 4), parallel(9 * R, 3 * R / 4), 9 * R / 4 + 3 * R / 4], "R_eq = %s R" % m1)

# Q3 — I_X : I_Y for two wires in parallel
sx, sy = F(3 * 10 ** 7), F(6 * 10 ** 7)
m1 = 1 / ((F(3, 2)) * (sy / sx) * F(1, 9))                           # I_X/I_Y = R_Y/R_X
LY, dY = F(1), F(1, 1000)                                            # method 2: real wires, π cancels
RX = (F(3, 2) * LY) / (sx * (3 * dY) ** 2)
RY = LY / (sy * dY ** 2)
m2 = (1 / RX) / (1 / RY)                                             # same V on both
check(3, m1, m2, 3, [1 / (F(3, 2) * (sx / sy) * F(1, 9)), 1 / (F(3, 2) * (sy / sx) * F(1, 3)), 1 / m1, m1], "I_X : I_Y = %s : 1" % m1)

# Q4 — I (vertical) against V (horizontal): R = V / I; same material and length: d ∝ 1/√R
RX, RY = F(2) / F(8, 10), F(4) / F(4, 10)                         # from the points (2 V, 0.8 A) and (4 V, 0.4 A)
m1 = exact_sqrt(RY / RX)                                          # d_X/d_Y = √(R_Y/R_X)
dX = math.sqrt(4 / (math.pi * float(RX)))                         # method 2: R = ρL/(πd²/4) with ρL = 1
dY = math.sqrt(4 / (math.pi * float(RY)))
m2 = F(round(dX / dY * 10 ** 6), 10 ** 6)
sX, sY = F(8, 10) / 2, F(4, 10) / 4                               # the mistake: the slope I/V taken as R
check(4, m1, m2, 1, [exact_sqrt(sY / sX), m1, RY / RX, sY / sX], "R_X = %s Ω, R_Y = %s Ω, d_X : d_Y = %s : 1" % (RX, RY, m1))

# Q5 — R1 (A–C), R2 (C–D), R3 (D–B), wire A–D, wire C–B
m1 = parallel(F(4), F(6), F(12))
wire = F(1, 10 ** 9)
m2 = equivalent_resistance(["A", "C", "D", "B"], [("A", "C", 4), ("C", "D", 6), ("D", "B", 12), ("A", "D", wire), ("C", "B", wire)], "A", "B")
m2 = F(round(float(m2) * 10 ** 6), 10 ** 6)
check(5, m1, m2, 2, [F(22), F(12), m1, F(0)], "R_eq = %s Ω" % m1)

# Q6 — V = V_B − I r with (5 Ω, 10 V) and (2 Ω, 8 V)
I1, I2 = F(10, 5), F(8, 2)
r = (F(10) - F(8)) / (I2 - I1)
VB = 10 + I1 * r
m1 = (VB, VB / r)
VB2, r2 = solve([[1, -I1], [1, -I2]], [10, 8])                    # method 2: V_B − I r = V as a 2×2 system
m2 = (VB2, VB2 / r2)                                               # (open-circuit reading, short-circuit current)
assert VB == 12 and r == 1
check(6, m1, m2, 3, [(0, VB / r), (VB, "infinite"), (F(10), F(10) / ((F(10) - 8) / (I2 - I1))), m1], "V_B = %s V, r = %s Ω" % (VB, r))

# Q7 — closing S: A1, A2, V for many random circuits with r > 0 and R1 > 0
def readings(VB, r, R1, R2, R3, closed):
    group = parallel(R2, R3) if closed else R2
    I = VB / (r + R1 + group)
    V = VB - I * r
    return I, (V - I * R1) / R2, V


def trend(before, after):
    return tuple("up" if b > a else "down" if b < a else "same" for a, b in zip(before, after))


random.seed(1)
trends = set()
for _ in range(2000):
    values = [F(random.randint(1, 60), random.randint(1, 6)) for _ in range(5)]
    trends.add(trend(readings(*values, False), readings(*values, True)))
assert len(trends) == 1, trends
m1 = ("up", "down", "down")                                          # reasoning (A1 ↑, A2 ↓, V ↓)
m2 = trends.pop()
ideal = trend(readings(F(12), F(0), F(0), F(6), F(3), False), readings(F(12), F(0), F(0), F(6), F(3), True))
assert ideal == ("up", "same", "same")                               # choice ج: only if r = 0 and R1 = 0
check(7, m1, m2, 0, [m1, ("up", "up", "down"), ideal, ("down", "down", "up")], "A1 up, A2 down, V down")

# Q8 — junctions P and Q (assumed arrows: I1 from P to Q, I2 out of Q)
I1 = F(3) - F(7)                                                     # at P: 3 = 7 + I1
I2 = I1 + F(2)                                                       # at Q: I1 + 2 = I2
m1 = (abs(I1), "Q→P" if I1 < 0 else "P→Q", abs(I2), "into Q" if I2 < 0 else "out of Q")
I2_big = (F(3) + F(2)) - F(7)                                        # method 2: P and Q as one big junction
I1_big = F(3) - F(7)
m2 = (abs(I1_big), "Q→P" if I1_big < 0 else "P→Q", abs(I2_big), "into Q" if I2_big < 0 else "out of Q")
check(8, m1, m2, 1, [(F(4), "P→Q", F(6), "out of Q"), m1, (F(4), "Q→P", F(2), "out of Q"), (F(10), "P→Q", F(12), "out of Q")],
      "I1 = %s A (Q→P), I2 = %s A into Q" % (abs(I1), abs(I2)))

# Q9 — V_B1 = 12 V (+ up) with R1 = 2 Ω, R2 = 4 Ω, V_B2 = 6 V (+ up) with R3 = 2 Ω
# method 1: Kirchhoff (I1 up in branch 1, I2 down in R2, I3 down in branch 3)
I1, I2, I3 = solve([[1, -1, -1], [2, 4, 0], [0, 4, -2]], [0, 12, 6])
m1 = (I3, "charging" if I3 > 0 else "discharging")
# method 2: potential of the top wire (bottom wire 0 V); the three branches give the same value
V = solve([[F(1, 2) + F(1, 4) + F(1, 2)]], [F(12, 2) + F(6, 2)])[0]
assert V == I2 * 4 == 12 - I1 * 2 == 6 + I3 * 2
I3b = (V - 6) / 2
m2 = (I3b, "charging" if I3b > 0 else "discharging")
Vs = solve([[F(1, 2) + F(1, 4) + F(1, 2)]], [F(12, 2) - F(6, 2)])[0]  # the sign mistake (V_B2 taken the other way)
sign_mistake = ((Vs + 6) / 2, "discharging")
check(9, m1, m2, 3, [(I3, "discharging"), (F(12 - 6, 2 + 2), "charging"), sign_mistake, m1],
      "I1 = %s A, I2 = %s A, I3 = %s A, top wire %s V" % (I1, I2, I3, V))

# Q10 — lamps X (220 V, 100 W) and Y (220 V, 25 W) in series on 220 V
RX, RY = F(220 ** 2, 100), F(220 ** 2, 25)
I = F(220) / (RX + RY)
PX, PY = I ** 2 * RX, I ** 2 * RY
m1 = ("Y" if PY > PX else "X", PX + PY)
VX, VY = 220 * RX / (RX + RY), 220 * RY / (RX + RY)                  # method 2: voltage division, P = V²/R
m2 = ("Y" if VY ** 2 / RY > VX ** 2 / RX else "X", VX ** 2 / RX + VY ** 2 / RY)
assert F(220) ** 2 / (RX + RY) == m1[1]
check(10, m1, m2, 1, [("X", F(125)), m1, ("same", m1[1]), ("X", m1[1])], "P_X = %s W, P_Y = %s W" % (PX, PY))

# The skills are all different, and the right answers are spread over the four places.
skills = [q["skill"] for q in QUIZ["questions"]]
assert len(set(skills)) == len(skills) == 10
places = [q["correctIndex"] for q in QUIZ["questions"]]
assert all(places.count(i) >= 2 for i in range(4)), places
print("\n".join(report))
print("All 10 questions: both methods agree, one right choice each. Right choices: %s" % " ".join("أبجد"[i] for i in places))
