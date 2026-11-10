"""Physics Chapter 2 «التأثير المغناطيسي للتيار الكهربي وأجهزة القياس الكهربي»:
150 multiple-choice questions and 50 essay questions in 8 lessons (development tool —
the website only reads the results).

Makes, from common.py (the lessons), mcq_fields.py, mcq_forces.py, mcq_devices.py and essay.py:
  physics-questions.json            Chapter 2: for each lesson a section of MCQs and a
                                    section of essay questions, the lessons (their names
                                    and sections) and the random-exam setting; Chapter 1
                                    is not touched
  physics-ch2-question-bank.pdf     ONE PDF: part 1 the 150 MCQs by lesson (no answers),
                                    part 2 the 50 essay questions by lesson with space to
                                    write, part 3 the answer key (every MCQ with the reason
                                    for each of its four choices, every essay model answer)
  tools/phys_ch2_bank/built.json    what the PDF was made from (checked by the tests)

The questions on the website and in the PDF are the same text (one source), with the
same numbers (each lesson starts at 1). Run from the website folder, after figs.py if
a diagram changed:
    python3 -B tools/phys_ch2_bank/figs.py
    python3 -B tools/phys_ch2_bank/build.py
Needs Playwright (Chromium) and pypdf."""
import hashlib
import html
import importlib.util
import io
import itertools
import json
import math
import pathlib
import random
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ folders in the site

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent
sys.path.insert(0, str(HERE))

from common import LESSONS, TOPICS              # noqa: E402
import mcq_fields                               # noqa: E402
import mcq_forces                               # noqa: E402
import mcq_devices                              # noqa: E402
from essay import ESSAY                         # noqa: E402

# the small local web server of the Biology bank (it serves the fonts to Chromium)
_spec = importlib.util.spec_from_file_location("bio_render", SITE / "tools" / "bio_ch2_bank" / "render.py")
render = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(render)


DATA = SITE / "physics-questions.json"
CHAPTER_ID = "chapter-2"
CHAPTER_TITLE = "الفصل الثاني: التأثير المغناطيسي للتيار الكهربي وأجهزة القياس الكهربي"
PDF = "physics-ch2-question-bank.pdf"
PDF_TITLE = "ملف الفصل الثاني كاملًا: 200 سؤال مقسمة على 8 دروس، مع مفتاح الإجابات"
MCQ_LABEL, ESSAY_LABEL = "أسئلة الاختيار من متعدد", "الأسئلة المقالية"
EXAM_TITLE = "امتحان عشوائي على الفصل الثاني"
EXAM_NOTE = "اختر عدد الأسئلة ومستوى الصعوبة، وتُسحب الأسئلة عشوائيًا من أسئلة الاختيار من متعدد الـ 150 في الدروس الثمانية، بدون تكرار."
EXAM_PRESETS = [10, 20, 30, 50]
LETTERS = "أبجد"
LEVELS = {"easy": "سهل", "medium": "متوسط", "hard": "صعب", "very-hard": "صعب جدًا"}
LRI, PDI, RLM = "⁦", "⁩", "‏"

LISTS = {"wire": mcq_fields.WIRE, "loop": mcq_fields.LOOP, "solenoid": mcq_forces.SOLENOID,
         "force": mcq_forces.FORCE, "parallel": mcq_forces.PARALLEL, "torque": mcq_devices.TORQUE,
         "galv": mcq_devices.GALV, "ammeter": mcq_devices.AMMETER, "voltmeter": mcq_devices.VOLTMETER,
         "ohmmeter": mcq_devices.OHMMETER}
TOPIC_TITLE = dict(TOPICS)

# ------------------------------------------------------------------ text
START = "A-Za-z0-9μπθτφΩΔ√⊙⊗ℓ∞|"
RUN = re.compile(r"[\(\[]*[+−\-]?[" + START + r"][A-Za-z0-9₀-₉⁰-⁹¹²³⁺⁻().,/+×÷=%°→\-−–:\[\] μπθτφΩΔ√≈∝′⊙⊗⊥ℓ∞|_½⟸]*")
ARABIC = re.compile(r"[؀-ۿ]")
STRONG = re.compile(r"[A-Za-z؀-ۿμπθτφΩΔℓ]")
UNIT_GAP = re.compile(r"(?<=[0-9⁰¹²³⁴-⁹]) (?=(?:k|M|m|μ|c)?(?:A|T|m|Ω|V|N|Wb|g|deg)(?![A-Za-z]))")
STEP = re.compile(r"^(\s*(?:\d+\)|\([؀-ۿ]+\))\s*)")


def unmatched(run):
    """Positions of the unmatched closing brackets, and of the unmatched opening ones."""
    closers, openers = [], []
    for i, ch in enumerate(run):
        if ch in "([":
            openers.append(i)
        elif ch in ")]":
            if openers:
                openers.pop()
            else:
                closers.append(i)
    return closers, openers


def trim(run):
    """Split a matched run into (text before, the left-to-right part, text after):
    end punctuation, a lone arrow and brackets that do not belong to it stay outside."""
    lead, tail = "", ""
    while True:
        changed = False
        if run and run[-1] in " .,:=⟸":
            tail = run[-1] + tail; run = run[:-1]; changed = True
        if run and run[0] in "= ⟸":
            lead += run[0]; run = run[1:]; changed = True
        closers, openers = unmatched(run)
        if closers:
            i = closers[0]
            if i == len(run) - 1:
                tail = run[-1] + tail; run = run[:-1]
            else:            # "1) B = …": the step number stays outside
                lead += run[:i + 1]; run = run[i + 1:]
            changed = True
        elif openers:
            j = openers[-1]
            if j == 0:
                lead += run[0]; run = run[1:]; changed = True
            else:            # "4a (a …": the bracket and what follows stay outside
                tail = run[j:] + tail; run = run[:j]; changed = True
        if not changed:
            return lead, run, tail


def isolate(text):
    """Formulas and numbers inside Arabic text are wrapped in left-to-right isolates, so
    «B = μNI / (2r)» keeps its order. Inside a formula «⟸» (written for right-to-left
    reading) becomes «⟹»; between Arabic words it stays as it is."""
    text = text.replace(LRI, "").replace(PDI, "").replace(RLM, "")

    def wrap(m):
        lead, run, tail = trim(m.group(0))
        if not re.search(r"[A-Za-z0-9μπθτφΩ√⊙⊗ℓ∞]", run):
            return m.group(0)
        run = UNIT_GAP.sub("\u00a0", run.replace("⟸", "⟹"))   # a number stays on the same line as its unit
        return lead + LRI + run + PDI + tail

    lines = []
    for line in text.split("\n"):
        step = STEP.match(line)
        head = step.group(1) if step else ""
        lines.append(head + RUN.sub(wrap, line[len(head):]))
    out = "\n".join(lines)
    # Arabic text whose first letter is Latin (it starts with a formula) gets a
    # right-to-left mark first, so the browser reads it as right-to-left text
    first = STRONG.search(out)
    if ARABIC.search(out) and first and not ARABIC.match(first.group(0)):
        out = RLM + out
    return out


SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")


def number(option):
    """The value of a number answer: «6.28 × 10⁻⁴ T» → 6.28e-4, «0 N.m» → 0."""
    o = option.strip()
    if o.startswith("صفر"):
        return 0.0
    m = re.match(r"([0-9]+(?:\.[0-9]+)?)(?:\s*×\s*10([⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+))?", o)
    if not m:
        return None
    value = float(m.group(1))
    if m.group(2):
        value *= 10 ** int(m.group(2).translate(SUPER))
    return value


def unit_of(option):
    unit = re.sub(r"^[0-9.]+(\s*×\s*10[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?\s*", "", option.strip())
    return {"لفات": "لفة"}.get(unit, unit)   # Arabic: 3–10 لفات, 11 and more لفة



# ------------------------------------------------------------------ the questions
def all_mcqs():
    """The 150 MCQs in the order of the lessons (and of the topics inside a lesson)."""
    out = []
    for key, _, _, topics in LESSONS:
        for topic in topics:
            for q in LISTS[topic]:
                assert q["topic"] == topic, (topic, q["prompt"][:40])
                out.append(dict(q, lesson=key))
    return out


def place(qs, seed=20261110):
    """The correct answer is written first in the sources. Number answers are shown in
    increasing order; for the others the place of the correct answer is chosen so that
    each letter is the answer about equally often and never three times in a row."""
    rnd = random.Random(seed)
    fixed = {}
    for i, q in enumerate(qs):
        if q["numeric"]:
            values = [number(o[0]) for o in q["options"]]
            assert None not in values, ("not a number", q["prompt"][:60], [o[0] for o in q["options"]])
            assert len(set(values)) == 4, ("two equal numbers", q["prompt"][:60])
            units = {unit_of(o[0]) for o in q["options"] if number(o[0]) != 0}
            assert len(units) == 1, ("mixed units", q["prompt"][:60], units)
            opts = sorted(q["options"], key=lambda o: number(o[0]))
            fixed[i] = (opts, opts.index(q["options"][0]))
    counts = [0, 0, 0, 0]
    for opts, pos in fixed.values():
        counts[pos] += 1
    placed = []
    for i, q in enumerate(qs):
        if i in fixed:
            placed.append(fixed[i])
            continue
        prev = [p for _, p in placed[-2:]]
        nxt = fixed.get(i + 1, (None, None))[1]
        ok = [k for k in range(4) if not (len(prev) == 2 and prev[0] == prev[1] == k) and not (prev[-1:] == [k] and nxt == k)]
        low = min(counts[k] for k in ok)
        pos = rnd.choice([k for k in ok if counts[k] == low])
        wrong = q["options"][1:]
        rnd.shuffle(wrong)
        opts = wrong[:pos] + [q["options"][0]] + wrong[pos:]
        placed.append((opts, pos))
        counts[pos] += 1
    seq = [p for _, p in placed]
    longest = max(len(list(run)) for _, run in itertools.groupby(seq))
    return placed, counts, longest


def build_questions():
    """Returns the lessons: [(key, ordinal, title, topics, mcq items, essay items, mcq sources)]."""
    qs = all_mcqs()
    assert len(qs) == 150, len(qs)
    assert len(ESSAY) == 50, len(ESSAY)
    placed, counts, longest = place(qs)
    print("MCQ answers by letter %s; longest run of one letter: %d" % (dict(zip(LETTERS, counts)), longest))
    assert longest <= 3, longest
    lessons = []
    for n, (key, ordinal, title, topics) in enumerate(LESSONS, 1):
        mcq, sources = [], []
        for q, (opts, pos) in zip(qs, placed):
            if q["lesson"] != key:
                continue
            review = ["نراجع الاختيارات:"]
            for k, (text, reason) in enumerate(opts):
                review.append("%s (%s) %s: %s" % ("✓" if k == pos else "✗", LETTERS[k], text, reason))
            options = [isolate(o[0]) for o in opts]
            item = {"id": "phys-ch2-l%d-mcq-%02d" % (n, len(mcq) + 1), "type": "mcq", "lang": "ar", "prompt": isolate(q["prompt"])}
            if q["image"]:
                item["image"] = q["image"]
                item["imageAlt"] = isolate(q["imageAlt"])
            item.update({"options": options, "answer": options[pos],
                         "explanation": isolate(q["solution"].strip() + "\n\n" + "\n".join(review)),
                         "difficulty": q["difficulty"], "reviewStatus": "reviewed"})
            mcq.append(item)
            sources.append(q)
        essays = []
        for e in ESSAY:
            if e["lesson"] != key:
                continue
            item = {"id": "phys-ch2-l%d-essay-%02d" % (n, len(essays) + 1), "type": "short", "lang": "ar", "prompt": isolate(e["prompt"])}
            if e["image"]:
                item["image"] = e["image"]
                item["imageAlt"] = isolate(e["imageAlt"])
            item.update({"modelAnswer": isolate(e["answer"].strip()), "revealAnytime": True,
                         "difficulty": e["difficulty"], "reviewStatus": "reviewed"})
            essays.append(dict(item, kind=e["kind"]))
        assert mcq and essays, key
        lessons.append((key, ordinal, title, topics, mcq, essays, sources))
    check(lessons)
    print("lessons: %s" % [(key, len(m), len(e)) for key, _, _, _, m, e, _ in lessons])
    return lessons


def plain(s):
    return re.sub(r"[‏⁦⁩\s]", "", s)


def check(lessons):
    """The checks the request asks for, before anything is written."""
    mcq = [q for lesson in lessons for q in lesson[4]]
    essays = [q for lesson in lessons for q in lesson[5]]
    assert len(mcq) == 150 and len(essays) == 50, (len(mcq), len(essays))
    for q in mcq:
        assert len(q["options"]) == 4 and len(set(map(plain, q["options"]))) == 4, q["id"]
        assert q["options"].count(q["answer"]) == 1, q["id"]
    for q in mcq + essays:
        if q.get("image"):
            assert (SITE / q["image"]).exists(), q["image"]
    keys = [plain(q["prompt"]) + "#" + "|".join(map(plain, q.get("options", []))) for q in mcq]
    assert len(set(keys)) == len(keys), "two MCQs are the same"
    keys = [plain(q["prompt"]) for q in essays]
    assert len(set(keys)) == len(keys), "two essays are the same"
    # every formula keeps its brackets balanced inside its isolate
    for q in mcq + essays:
        for text in [q["prompt"]] + q.get("options", []) + [q.get("explanation", ""), q.get("modelAnswer", "")]:
            for run in re.findall("⁦([^⁩]*)⁩", text):
                c, o = unmatched(run)
                assert not c and not o, (q["id"], run)
            assert text.count(LRI) == text.count(PDI), q["id"]


# ------------------------------------------------------------------ the data file
def section_id(n, kind):
    return "chapter-2-l%d-%s" % (n, kind)


def update_data(lessons):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    sections, groups = [], []
    for n, (key, ordinal, title, topics, mcq, essays, _) in enumerate(lessons, 1):
        clean = [{k: v for k, v in q.items() if k != "kind"} for q in essays]
        sections.append({"id": section_id(n, "mcq"), "title": "%s: %s – %s" % (ordinal, title, MCQ_LABEL), "label": MCQ_LABEL, "questions": mcq})
        sections.append({"id": section_id(n, "essay"), "title": "%s: %s – %s" % (ordinal, title, ESSAY_LABEL), "label": ESSAY_LABEL, "questions": clean})
        groups.append({"id": "chapter-2-l%d" % n, "number": ordinal, "title": title, "sections": [section_id(n, "mcq"), section_id(n, "essay")]})
    chapter = {"id": CHAPTER_ID, "title": CHAPTER_TITLE, "sections": sections, "lessons": groups,
               "exam": {"title": EXAM_TITLE, "note": EXAM_NOTE, "sections": [section_id(n, "mcq") for n in range(1, len(lessons) + 1)],
                        "presets": EXAM_PRESETS},
               "pdf": PDF, "pdfTitle": PDF_TITLE}
    others = [c for c in data["chapters"] if c["id"] != CHAPTER_ID]
    assert [c["id"] for c in others] == ["chapter-1"], [c["id"] for c in others]
    data["chapters"] = others + [chapter]
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: physics-questions.json (Chapter 2: %d lessons, %d sections)" % (len(groups), len(sections)))


# ------------------------------------------------------------------ the PDF
CSS = """
@font-face { font-family: "Cairo"; src: url("__BASE__tools/fonts/Cairo.ttf") format("truetype"); font-weight: 200 1000; font-style: oblique -11deg 11deg; }
@page { size: A4; margin: 15mm 13mm 17mm;
  @bottom-center { content: "صفحة " counter(page) " من " counter(pages); font-family: "Cairo"; font-size: 9pt; font-weight: 700; color: #3b2a7a; }
  @bottom-right { content: "الفيزياء • الفصل الثاني"; font-family: "Cairo"; font-size: 8pt; color: #94a3b8; }
  @bottom-left { content: "Learn for Grade 12"; font-family: "Cairo"; font-size: 8pt; color: #94a3b8; } }
@page cover { margin: 0; @bottom-center { content: none; } @bottom-right { content: none; } @bottom-left { content: none; } }
* { box-sizing: border-box; }
html { direction: rtl; }
body { margin: 0; font-family: "Cairo", "DejaVu Sans", sans-serif; color: #1e293b; font-size: 10.6pt; line-height: 1.72; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.m { font-family: "DejaVu Sans", "Cairo", sans-serif; font-size: .9em; direction: ltr; unicode-bidi: isolate; white-space: pre-wrap; }
.slant { font-style: oblique 9deg; }
.cover { page: cover; width: 210mm; height: 297mm; position: relative; overflow: hidden; color: #fff;
  background: linear-gradient(145deg, #1e1b4b 0%, #4338ca 38%, #6d28d9 68%, #db2777 100%); }
.cover svg.deco { position: absolute; inset: 0; width: 210mm; height: 297mm; }
.cover .inner { position: absolute; inset: 22mm 20mm 18mm; display: flex; flex-direction: column; }
.cover .kicker { display: inline-block; align-self: flex-start; background: rgba(255,255,255,.18); border: 1.5px solid rgba(255,255,255,.55);
  border-radius: 99px; padding: 2mm 6mm; font-weight: 800; font-size: 12.5pt; }
.cover h1 { font-size: 34pt; line-height: 1.3; margin: 10mm 0 2mm; font-weight: 900; text-shadow: 0 2.5mm 6mm rgba(0,10,40,.45); }
.cover h2 { font-size: 17pt; line-height: 1.55; margin: 0 0 7mm; font-weight: 800; color: #fde68a; text-shadow: 0 1.5mm 4mm rgba(0,10,40,.35); }
.cover .stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }
.cover .stat { background: rgba(255,255,255,.95); color: #1e293b; border-radius: 5mm; padding: 3.5mm 5mm; box-shadow: 0 3mm 8mm rgba(0,10,40,.25); }
.cover .stat b { display: block; font-size: 21pt; line-height: 1.2; font-weight: 900; }
.cover .stat span { font-weight: 700; font-size: 10.5pt; }
.cover .s1 b { color: #4338ca; } .cover .s2 b { color: #c2410c; } .cover .s3 b { color: #047857; }
.cover .art { margin: 8mm auto 0; width: 132mm; background: rgba(255,255,255,.95); border-radius: 8mm; padding: 4mm 5mm 3mm; text-align: center; box-shadow: 0 3mm 9mm rgba(0,10,40,.3); }
.cover .art svg { width: 100%; height: 64mm; display: block; }
.cover .art p { margin: 1mm 0 0; color: #4338ca; font-weight: 800; font-size: 10.5pt; }
.cover .foot { margin-top: auto; font-weight: 800; font-size: 12pt; display: flex; justify-content: space-between; }
.guide { page-break-before: always; }
.guide .box { border-radius: 5mm; padding: 4mm 6mm; margin-bottom: 4mm; }
.guide .contents { background: linear-gradient(135deg, #e0e7ff, #fce7f3); border: 2px solid #a5b4fc; }
.guide .how { background: linear-gradient(135deg, #fef3c7, #dcfce7); border: 2px solid #fcd34d; }
.guide h2 { font-size: 18pt; font-weight: 900; color: #4338ca; margin: 0 0 2.5mm; }
.guide .how h2 { color: #b45309; }
.guide table { width: 100%; border-collapse: collapse; font-size: 11pt; }
.guide td { padding: .9mm 2mm; border-bottom: 1.5px dashed rgba(67,56,202,.28); font-weight: 700; line-height: 1.5; }
.guide tr.sub td { font-weight: 600; font-size: 9.4pt; color: #475569; padding-top: .3mm; padding-bottom: .3mm; }
.guide tr.sub td:first-child { padding-right: 9mm; }
.guide td.n { text-align: left; color: #4338ca; font-weight: 900; width: 30mm; }
.guide td .dot { display: inline-block; width: 4mm; height: 4mm; border-radius: 50%; margin-left: 2.5mm; vertical-align: middle; }
.guide ul { margin: 0; padding-right: 6mm; }
.guide li { margin: .6mm 0; font-size: 10pt; line-height: 1.6; }
.part { page-break-before: always; }
.part-head { border-radius: 5mm; padding: 5mm 8mm 4.5mm; color: #fff; margin-bottom: 5mm; position: relative; overflow: hidden; }
.part-head h2 { margin: 0; font-size: 20pt; font-weight: 900; line-height: 1.35; text-shadow: 0 1.2mm 2.5mm rgba(0,0,0,.28); }
.part-head p { margin: 1mm 0 0; font-weight: 700; font-size: 10.8pt; opacity: .95; }
.part-head .num { position: absolute; left: 7mm; top: 1mm; font-size: 44pt; font-weight: 900; opacity: .22; }
.p1 .part-head { background: linear-gradient(120deg, #3730a3, #7c3aed); }
.p2 .part-head { background: linear-gradient(120deg, #9a3412, #ea580c); }
.p3 .part-head { background: linear-gradient(120deg, #065f46, #0d9488); }
.topic { break-after: avoid; margin: 5mm 0 3mm; padding: 2mm 4mm; border-radius: 3mm; background: #eef2ff; border-right: 2.2mm solid #6366f1;
  font-weight: 900; font-size: 12.5pt; color: #3730a3; }
.topic small { font-weight: 700; color: #64748b; font-size: 9.5pt; margin-right: 2mm; }
.q { break-inside: avoid; border-radius: 4mm; padding: 3mm 4.4mm; margin: 0 0 3.4mm; border: 1.4px solid #c7d2fe; border-right: 2.2mm solid #6366f1;
  background: linear-gradient(90deg, #fff 74%, #f5f3ff); }
.p2 .q { border-color: #fed7aa; border-right-color: #f97316; background: linear-gradient(90deg, #fff 74%, #fff7ed); }
.qhead { display: flex; align-items: center; gap: 2.4mm; margin-bottom: .8mm; }
.badge { flex: none; min-width: 9mm; height: 9mm; padding: 0 1.5mm; border-radius: 99px; color: #fff; font-weight: 900; font-size: 11pt;
  display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #4f46e5, #9333ea); }
.p2 .badge { background: linear-gradient(135deg, #ea580c, #be185d); }
.p3 .badge { background: linear-gradient(135deg, #059669, #0d9488); }
.pill { font-size: 8.4pt; font-weight: 800; border-radius: 99px; padding: .1mm 2.8mm; border: 1.2px solid; }
.pill.easy { background: #dcfce7; color: #166534; border-color: #86efac; }
.pill.medium { background: #e0f2fe; color: #075985; border-color: #7dd3fc; }
.pill.hard { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
.pill.very-hard { background: #fce7f3; color: #9d174d; border-color: #f9a8d4; }
.kind { font-size: 8.4pt; font-weight: 800; color: #9a3412; }
.prompt { margin: 0; font-weight: 600; white-space: pre-line; }
.fig { margin: 2mm 0 1mm; text-align: center; }
.fig svg { height: auto; max-width: 100%; }
.fig svg text { font-family: "Cairo", "DejaVu Sans", sans-serif; }
.opts { list-style: none; margin: 2mm 0 0; padding: 0; display: grid; grid-template-columns: 1fr; gap: 1.3mm; }
.opts.two { grid-template-columns: 1fr 1fr; column-gap: 4mm; }
.opts li { display: flex; gap: 2.2mm; align-items: flex-start; background: rgba(255,255,255,.9); border: 1.2px solid #e2e8f0; border-radius: 3mm; padding: .8mm 2.6mm; }
.opts .L { flex: none; width: 6.2mm; height: 6.2mm; margin-top: .7mm; border-radius: 50%; font-weight: 900; font-size: 9.8pt;
  display: flex; align-items: center; justify-content: center; color: #fff; background: #6366f1; }
.lines { margin-top: 1.5mm; }
.lines div { height: 7.2mm; border-bottom: 1.3px dotted #fdba74; }
.grid { width: 100%; border-collapse: separate; border-spacing: 1.2mm; margin: 0 0 4mm; }
.grid td { background: #ecfdf5; border: 1.3px solid #a7f3d0; border-radius: 2.2mm; text-align: center; padding: .6mm 0; font-weight: 800; font-size: 10.2pt; }
.grid td b { color: #94a3b8; font-weight: 700; margin-left: 1.2mm; font-size: 9pt; }
.p3 h3 { font-size: 14pt; font-weight: 900; margin: 5mm 0 2.5mm; color: #047857; }
.p3 h3.first { margin-top: 0; }
.k { break-inside: avoid; border-radius: 4mm; padding: 2.6mm 4.2mm; margin: 0 0 3mm; border: 1.4px solid #a7f3d0; border-right: 2.2mm solid #10b981;
  background: linear-gradient(90deg, #fff 76%, #ecfdf5); font-size: 9.6pt; line-height: 1.62; }
.k.e { border-color: #fed7aa; border-right-color: #f97316; background: linear-gradient(90deg, #fff 76%, #fff7ed); }
.k .khead { display: flex; align-items: center; gap: 2.2mm; margin-bottom: .6mm; }
.k .badge { min-width: 8mm; height: 8mm; font-size: 9.8pt; }
.k.e .badge { background: linear-gradient(135deg, #ea580c, #be185d); }
.k .right { font-weight: 900; color: #15803d; background: #dcfce7; border: 1.2px solid #86efac; border-radius: 99px; padding: 0 3mm; }
.k .kq { margin: 0 0 1mm; color: #475569; font-weight: 600; white-space: pre-line; }
.k .ke { margin: 0; white-space: pre-line; }
.k .lab { font-weight: 900; color: #047857; }
.k.e .lab { color: #c2410c; }
"""

DECO = """<svg class="deco" viewBox="0 0 210 297" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="186" cy="36" r="46" fill="#fff" fill-opacity=".08"/><circle cx="14" cy="256" r="60" fill="#fff" fill-opacity=".07"/>
<circle cx="174" cy="236" r="18" fill="#fde68a" fill-opacity=".2"/><circle cx="30" cy="70" r="7" fill="#fff" fill-opacity=".2"/>
<g fill="none" stroke="#fff" stroke-opacity=".25" stroke-width=".7">
<circle cx="168" cy="146" r="10"/><circle cx="168" cy="146" r="17"/><circle cx="168" cy="146" r="25"/><circle cx="168" cy="146" r="34"/></g>
<circle cx="168" cy="146" r="3" fill="#fff" fill-opacity=".7"/>
<path d="M0 210 C 50 192 92 234 140 216 C 170 206 190 192 210 198 L210 297 L0 297 Z" fill="#fff" fill-opacity=".07"/>
</svg>"""

# A solenoid with its field lines, and a moving-coil meter.
ART = """<svg viewBox="0 0 460 230" xmlns="http://www.w3.org/2000/svg">
<g fill="none" stroke="#6366f1" stroke-width="2" stroke-opacity=".75">
<path d="M70 92 C 70 30, 290 30, 290 92"/><path d="M70 92 C 70 2, 290 2, 290 92"/>
<path d="M70 148 C 70 210, 290 210, 290 148"/><path d="M70 148 C 70 238, 290 238, 290 148"/>
<line x1="56" y1="120" x2="304" y2="120"/><line x1="56" y1="104" x2="304" y2="104"/><line x1="56" y1="136" x2="304" y2="136"/></g>
<g fill="#6366f1"><path d="M182 23 l-10 -5 v10z"/><path d="M182 202 l-10 -5 v10z"/><path d="M226 120 l10 -5 v10z"/></g>
<g stroke="#334155" stroke-width="4" fill="none">""" + "".join(
    '<path d="M%d 150 L%d 90"/>' % (x, x + 14) for x in range(92, 280, 22)) + """</g>
<g stroke="#94a3b8" stroke-width="2.4" stroke-dasharray="4 3" fill="none">""" + "".join(
    '<path d="M%d 90 L%d 150"/>' % (x + 14, x + 22) for x in range(92, 258, 22)) + """</g>
<text x="58" y="126" font-family="Cairo" font-weight="900" font-size="20" fill="#be185d" text-anchor="end">N</text>
<text x="302" y="126" font-family="Cairo" font-weight="900" font-size="20" fill="#0f766e">S</text>
<rect x="326" y="58" width="120" height="120" rx="16" fill="#f8fafc" stroke="#334155" stroke-width="3"/>
<path d="M346 140 A 40 40 0 0 1 426 140" fill="none" stroke="#334155" stroke-width="2.5"/>""" + "".join(
    '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#334155" stroke-width="2"/>'
    % (386 + 40 * math.cos(math.radians(a)), 140 - 40 * math.sin(math.radians(a)),
       386 + 32 * math.cos(math.radians(a)), 140 - 32 * math.sin(math.radians(a))) for a in range(10, 171, 20)) + """
<line x1="386" y1="140" x2="408" y2="108" stroke="#db2777" stroke-width="4" stroke-linecap="round"/><circle cx="386" cy="140" r="6" fill="#334155"/>
<text x="386" y="168" font-family="Cairo" font-weight="900" font-size="18" fill="#4338ca" text-anchor="middle">G</text>
</svg>"""


def esc(s):
    return html.escape(s, quote=False)


def rich(text):
    """Escaped text, with each left-to-right isolate set in the formula font."""
    out = esc(text).replace(RLM, "")
    return re.sub("⁦([^⁩]*)⁩", lambda m: '<span class="m">%s</span>' % m.group(1), out)


def figure(name):
    svg = (SITE / name).read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    w = int(re.search(r'width="(\d+)"', svg).group(1))
    mm = min(100, w * 0.165)
    svg = re.sub(r'width="\d+" height="\d+"', 'style="width:%.1fmm"' % mm, svg, count=1)
    return '<div class="fig">%s</div>' % svg




CSS_LESSONS = """
.lesson + .lesson { page-break-before: always; }
.banner { break-after: avoid; display: flex; align-items: center; gap: 5mm; border-radius: 5mm; padding: 4mm 6mm; margin: 0 0 4mm; color: #fff; position: relative; overflow: hidden; }
.p1 .banner { background: linear-gradient(115deg, #312e81, #6d28d9 60%, #a21caf); }
.p2 .banner { background: linear-gradient(115deg, #7c2d12, #c2410c 60%, #e11d48); }
.banner .circle { flex: none; width: 17mm; height: 17mm; border-radius: 50%; background: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 22pt; font-weight: 900; box-shadow: 0 1.5mm 4mm rgba(0,0,0,.25); }
.p1 .banner .circle { color: #5b21b6; } .p2 .banner .circle { color: #c2410c; }
.banner .kick { display: inline-block; font-size: 10pt; font-weight: 800; background: rgba(255,255,255,.2); border: 1.2px solid rgba(255,255,255,.5); border-radius: 99px; padding: 0 3.5mm; }
.banner h3 { margin: 1mm 0 .5mm; font-size: 17pt; line-height: 1.35; font-weight: 900; text-shadow: 0 1mm 2mm rgba(0,0,0,.25); }
.banner p { margin: 0; font-size: 10pt; font-weight: 700; opacity: .95; }
.banner svg { position: absolute; left: -6mm; top: -8mm; width: 46mm; height: 46mm; opacity: .16; }
.sub { break-after: avoid; margin: 3.5mm 0 2.5mm; font-weight: 900; font-size: 11.5pt; color: #5b21b6; border-bottom: 1.5px dashed #c4b5fd; padding-bottom: .5mm; }
.mk { position: absolute; font-family: "DejaVu Sans", sans-serif; font-size: 6pt; line-height: 1; color: #ffffff; white-space: nowrap; }
.klesson { break-after: avoid; margin: 5mm 0 3mm; padding: 2.4mm 4.5mm; border-radius: 3.5mm; color: #fff; font-weight: 900; font-size: 12.5pt;
  background: linear-gradient(115deg, #065f46, #0d9488); }
.klesson.e { background: linear-gradient(115deg, #9a3412, #ea580c); }
.klesson small { font-weight: 700; font-size: 9.5pt; opacity: .92; margin-right: 2mm; }
.grid caption { caption-side: top; text-align: right; font-weight: 900; color: #047857; font-size: 10.5pt; padding: 0 1mm .5mm; }
"""

RINGS = ('<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="#fff" stroke-width="3">'
         '<circle cx="50" cy="50" r="12"/><circle cx="50" cy="50" r="24"/><circle cx="50" cy="50" r="36"/><circle cx="50" cy="50" r="48"/></g>'
         '<circle cx="50" cy="50" r="5" fill="#fff"/></svg>')


def pill(level):
    return '<span class="pill %s">%s</span>' % (level, LEVELS[level])


def marker(name):
    return '<div class="mk">QZMARK%sQZ</div>' % name


def mcq_card(n, q):
    short = all(len(plain(o)) <= 30 for o in q["options"])
    opts = "".join('<li><span class="L">%s</span><span>%s</span></li>' % (LETTERS[i], rich(o)) for i, o in enumerate(q["options"]))
    fig = figure(q["image"]) if q.get("image") else ""
    return ('<div class="q"><div class="qhead"><span class="badge">%d</span>%s</div><p class="prompt">%s</p>%s<ol class="opts%s">%s</ol></div>'
            % (n, pill(q["difficulty"]), rich(q["prompt"]), fig, " two" if short else "", opts))


def essay_card(n, q):
    lines = 9 if q["difficulty"] == "very-hard" else 7
    fig = figure(q["image"]) if q.get("image") else ""
    return ('<div class="q"><div class="qhead"><span class="badge">%d</span>%s<span class="kind">%s</span></div><p class="prompt">%s</p>%s<div class="lines">%s</div></div>'
            % (n, pill(q["difficulty"]), esc(q["kind"]), rich(q["prompt"]), fig, "<div></div>" * lines))


def part(cls, num, title, sub, body):
    return ('<section class="part %s"><div class="part-head"><span class="num">%s</span><h2 class="slant">%s</h2><p>%s</p></div>%s</section>'
            % (cls, num, title, sub, body))


def banner(n, ordinal, title, meta):
    return ('<div class="banner">%s<span class="circle">%d</span><div><span class="kick">%s</span><h3 class="slant">%s</h3><p>%s</p></div></div>'
            % (RINGS, n, ordinal, title, meta))


def part1(lessons):
    blocks = []
    for n, (key, ordinal, title, topics, mcq, essays, sources) in enumerate(lessons, 1):
        body = [banner(n, ordinal, title, "%d سؤالًا – اختر الإجابة الصحيحة (إجابة واحدة فقط صحيحة في كل سؤال)" % len(mcq)), marker("p1" + key)]
        for i, (q, src) in enumerate(zip(mcq, sources), 1):
            if len(topics) > 1 and (i == 1 or sources[i - 2]["topic"] != src["topic"]):
                body.append('<div class="sub">%s</div>' % TOPIC_TITLE[src["topic"]])
            body.append(mcq_card(i, q))
        blocks.append('<div class="lesson">%s</div>' % "".join(body))
    return part("p1", "1", "الجزء الأول: أسئلة الاختيار من متعدد",
                "150 سؤالًا مقسمة على 8 دروس بترتيب الكتاب – الأرقام تبدأ من 1 في كل درس كما على الموقع (الإجابات في الجزء الثالث)",
                "".join(blocks))


def part2(lessons):
    blocks = []
    for n, (key, ordinal, title, topics, mcq, essays, sources) in enumerate(lessons, 1):
        body = [banner(n, ordinal, title, "%d %s – اكتب إجابتك في المساحة بعد كل سؤال" % (len(essays), "أسئلة" if len(essays) <= 10 else "سؤالًا")), marker("p2" + key)]
        body.extend(essay_card(i, q) for i, q in enumerate(essays, 1))
        blocks.append('<div class="lesson">%s</div>' % "".join(body))
    return part("p2", "2", "الجزء الثاني: الأسئلة المقالية",
                "50 سؤالًا: اشرح – علّل – قارن – احسب بالخطوات – استنتج – فسّر الرسم – تنبأ – مسائل مركّبة (الإجابات النموذجية في الجزء الثالث)",
                "".join(blocks))


def part3_grid(lessons):
    tables = []
    for n, (key, ordinal, title, topics, mcq, essays, sources) in enumerate(lessons, 1):
        cells = ['<td><b>%d</b>%s</td>' % (i, LETTERS[q["options"].index(q["answer"])]) for i, q in enumerate(mcq, 1)]
        cells += ["<td style='visibility:hidden'></td>"] * (-len(cells) % 10)
        rows = "".join("<tr>%s</tr>" % "".join(cells[r:r + 10]) for r in range(0, len(cells), 10))
        tables.append('<table class="grid"><caption>%s: %s</caption>%s</table>' % (ordinal, title, rows))
    return part("p3", "3", "الجزء الثالث: مفتاح الإجابات",
                "المفتاح السريع لكل درس، ثم شرح كل سؤال اختيار من متعدد (لماذا الإجابة صحيحة ولماذا كل اختيار آخر خطأ)، ثم الإجابات النموذجية للأسئلة المقالية",
                marker("p3grid") + '<h3 class="slant first">المفتاح السريع لأسئلة الاختيار من متعدد (رقم السؤال وحرف الإجابة)</h3>' + "".join(tables))


def part3_mcq(lessons):
    body = [marker("p3mcq"), '<h3 class="slant first">شرح إجابات أسئلة الاختيار من متعدد</h3>']
    for n, (key, ordinal, title, topics, mcq, essays, sources) in enumerate(lessons, 1):
        body.append('<div class="klesson">%s: %s<small>(%d سؤالًا)</small></div>' % (ordinal, title, len(mcq)))
        for i, q in enumerate(mcq, 1):
            letter = LETTERS[q["options"].index(q["answer"])]
            body.append('<div class="k"><div class="khead"><span class="badge">%d</span><span class="right">الإجابة الصحيحة: (%s) %s</span>%s</div>'
                        '<p class="kq">%s</p><p class="ke"><span class="lab">الحل والشرح:</span>\n%s</p></div>'
                        % (i, letter, rich(q["answer"]), pill(q["difficulty"]), rich(q["prompt"]), rich(q["explanation"])))
    return '<section class="part p3">%s</section>' % "".join(body)


def part3_essay(lessons):
    body = [marker("p3essay"), '<h3 class="slant first">الإجابات النموذجية للأسئلة المقالية</h3>']
    for n, (key, ordinal, title, topics, mcq, essays, sources) in enumerate(lessons, 1):
        body.append('<div class="klesson e">%s: %s<small>(%d %s)</small></div>' % (ordinal, title, len(essays), "أسئلة" if len(essays) <= 10 else "سؤالًا"))
        for i, q in enumerate(essays, 1):
            body.append('<div class="k e"><div class="khead"><span class="badge">%d</span>%s</div><p class="kq">%s</p>'
                        '<p class="ke"><span class="lab">الإجابة النموذجية:</span>\n%s</p></div>' % (i, pill(q["difficulty"]), rich(q["prompt"]), rich(q["modelAnswer"])))
    return '<section class="part p3">%s</section>' % "".join(body)


def cover():
    stats = [("150", "سؤال اختيار من متعدد"), ("50", "سؤالًا مقاليًا"), ("8", "دروس بترتيب الكتاب")]
    stat_html = "".join('<div class="stat s%d"><b>%s</b><span>%s</span></div>' % (i, b, s) for i, (b, s) in enumerate(stats, 1))
    return ('<section class="cover">' + DECO + '<div class="inner">'
            '<span class="kicker">الفيزياء • الصف الثالث الثانوي</span>'
            '<h1 class="slant">بنك أسئلة الفصل الثاني</h1>'
            '<h2 class="slant">التأثير المغناطيسي للتيار الكهربي<br>وأجهزة القياس الكهربي</h2>'
            '<div class="stats">%s</div><div class="art">%s<p>المجال المغناطيسي لملف لولبي • الجلفانومتر ذو الملف المتحرك</p></div>'
            '<div class="foot"><span>وفق كتاب الوزارة 2026/2027 • مع مفتاح الإجابات الكامل</span><span dir="ltr">Learn for Grade 12</span></div>'
            '</div></section>') % (stat_html, ART)


def guide(lessons, pages):
    """The contents page; pages: marker name → page number (or "…" before they are known)."""
    rows = []

    def row(color, title, page):
        rows.append('<tr><td><span class="dot" style="background:%s"></span>%s</td><td class="n">صفحة %s</td></tr>' % (color, title, page))

    def sub(title, page):
        rows.append('<tr class="sub"><td>%s</td><td class="n">%s</td></tr>' % (title, page))

    row("#6366f1", "الجزء الأول: أسئلة الاختيار من متعدد (150 سؤالًا)", pages["p1l1"])
    for key, ordinal, title, topics, mcq, essays, sources in lessons:
        sub("%s: %s (%d سؤالًا)" % (ordinal, title, len(mcq)), pages["p1" + key])
    row("#f97316", "الجزء الثاني: الأسئلة المقالية (50 سؤالًا)", pages["p2l1"])
    for key, ordinal, title, topics, mcq, essays, sources in lessons:
        sub("%s: %s (%d %s)" % (ordinal, title, len(essays), "أسئلة" if len(essays) <= 10 else "سؤالًا"), pages["p2" + key])
    row("#10b981", "الجزء الثالث: مفتاح الإجابات – المفتاح السريع", pages["p3grid"])
    row("#10b981", "شرح إجابات أسئلة الاختيار من متعدد", pages["p3mcq"])
    row("#10b981", "الإجابات النموذجية للأسئلة المقالية", pages["p3essay"])
    return ('<section class="guide"><div class="box contents"><h2 class="slant">محتويات الملف</h2><table>' + "".join(rows) + '</table></div>'
            '<div class="box how"><h2 class="slant">كيف تستفيد من هذا الملف؟</h2><ul>' + "".join("<li>%s</li>" % t for t in TIPS) + '</ul></div></section>')


TIPS = [
    "كل الأسئلة من الفصل الثاني «التأثير المغناطيسي للتيار الكهربي وأجهزة القياس الكهربي» في كتاب الوزارة 2026/2027 فقط، ومقسمة على 8 دروس بترتيب الكتاب.",
    "حل أسئلة الدرس أولًا، ثم صحّح من الجزء الثالث (مفتاح الإجابات) الذي يبدأ في صفحة مستقلة؛ رقم السؤال في المفتاح هو رقمه في الدرس نفسه.",
    "في المسائل استخدم <span class=\"m\">μ = 4π × 10⁻⁷ Wb/A.m</span> للهواء ما لم يُذكر غير ذلك، وانتبه لتحويل الوحدات (cm إلى m، و mA و μA إلى A).",
    "مستوى كل سؤال مكتوب بجانب رقمه: سهل، متوسط، صعب، صعب جدًا.",
    "الأسئلة نفسها بالدروس والأرقام نفسها موجودة على الموقع تفاعليًا مع التصحيح الفوري والشرح، ومعها امتحان عشوائي تختار فيه عدد الأسئلة ومستواها.",
]


def make_pdf(lessons):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader
    body = part1(lessons) + part2(lessons) + part3_grid(lessons) + part3_mcq(lessons) + part3_essay(lessons)
    names = ["p1" + k for k, *_ in LESSONS] + ["p2" + k for k, *_ in LESSONS] + ["p3grid", "p3mcq", "p3essay"]

    def document(html_body):
        css = CSS.replace("__BASE__", base) + CSS_LESSONS
        return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>'
                % ("بنك أسئلة الفيزياء – الفصل الثاني", css, html_body))

    def find(path):
        found = {}
        for number, pg in enumerate(PdfReader(str(path)).pages, 1):
            for name in re.findall(r"QZMARK(\w+?)QZ", (pg.extract_text() or "").replace(" ", "").replace("\n", "")):
                found.setdefault(name, number)
        missing = [n for n in names if n not in found]
        assert not missing, missing
        return {n: found[n] for n in names}

    server, base = render.serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            def make(pages):
                page.set_content(document(cover() + guide(lessons, pages) + body), wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(SITE / PDF), prefer_css_page_size=True, print_background=True)
                return find(SITE / PDF)

            first = make({n: "000" for n in names})
            final = make(first)
            assert final == first, (first, final)   # the contents page did not move anything
            browser.close()
    finally:
        server.shutdown()
    total = len(PdfReader(str(SITE / PDF)).pages)
    print("written: %s (%d pages; starts %s)" % (PDF, total, final))
    return total, final


def fingerprint(questions):
    """Changes when a question, an option, an answer, an explanation or a model answer
    changes (tests/schema.test.js works it out the same way from physics-questions.json)."""
    digest = hashlib.sha256()
    for q in questions:
        fields = [q["prompt"]] + list(q.get("options") or []) + [q.get("answer", ""), q.get("explanation", ""), q.get("modelAnswer", "")]
        digest.update(("\x1f".join(fields) + "\x1e").encode("utf-8"))
    return digest.hexdigest()[:16]


def main():
    lessons = build_questions()
    update_data(lessons)
    total, starts = make_pdf(lessons)
    names = ("common.py", "mcq_fields.py", "mcq_forces.py", "mcq_devices.py", "essay.py", "figs.py", "build.py")
    questions = [q for lesson in lessons for q in lesson[4] + lesson[5]]
    built = {"pdf": PDF, "pages": total, "starts": starts,
             "lessons": [{"key": key, "mcq": len(m), "essay": len(e)} for key, _, _, _, m, e, _ in lessons],
             "fingerprint": fingerprint(questions),
             "sources": hashlib.sha256(b"".join((HERE / n).read_bytes() for n in names)).hexdigest()[:16]}
    (HERE / "built.json").write_text(json.dumps(built, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: tools/phys_ch2_bank/built.json")


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        build_questions()
    else:
        main()
