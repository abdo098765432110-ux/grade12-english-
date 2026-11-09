"""Chemistry Chapter 2 «التحليل الكيميائي»: 100 multiple-choice questions (50 difficult,
50 very difficult) and 50 essay questions with model answers (development tool).

Makes, from mcq_hard.py, mcq_vhard.py and essay.py:
  chemistry-questions.json           Chapter 2 with three sections (the MCQs in two
                                     sections by difficulty, then the essay questions);
                                     Chapter 1 and its PDF are not touched
  chemistry-ch2-mcq.pdf              the 100 multiple-choice questions (no answers)
  chemistry-ch2-essay.pdf            the 50 essay questions with space to write
  chemistry-ch2-answer-key.pdf       every MCQ answer with its explanation, and every
                                     essay model answer
  tools/chem_ch2_bank/built.json     what each PDF was made from (checked by the tests)

The questions on the website and in the PDFs are the same text (one source).
Run from the website folder:
    python3 tools/chem_ch2_bank/build.py
Needs Playwright (Chromium) and pypdf."""
import hashlib
import html
import io
import json
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent
sys.path.insert(0, str(HERE))

from mcq_hard import HARD      # noqa: E402
from mcq_vhard import VHARD    # noqa: E402
from essay import ESSAY        # noqa: E402

# the small local web server of the Biology bank (it serves the fonts to Chromium)
import importlib.util          # noqa: E402
_spec = importlib.util.spec_from_file_location("bio_render", SITE / "tools" / "bio_ch2_bank" / "render.py")
render = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(render)

DATA = SITE / "chemistry-questions.json"
CHAPTER_ID = "chapter-2"
CHAPTER_TITLE = "الفصل الثاني: التحليل الكيميائي"
SECTIONS = [("chapter-2-hard", "اختيار من متعدد – أسئلة صعبة (50 سؤالًا)"),
            ("chapter-2-very-hard", "اختيار من متعدد – أسئلة صعبة جدًا (50 سؤالًا)"),
            ("chapter-2-essay", "الأسئلة المقالية – 50 سؤالًا")]
PDF_MCQ, PDF_ESSAY, PDF_KEY = "chemistry-ch2-mcq.pdf", "chemistry-ch2-essay.pdf", "chemistry-ch2-answer-key.pdf"
MORE_PDFS = [
    {"file": PDF_MCQ, "title": "ملف الـ 100 سؤال اختيار من متعدد (صعبة وصعبة جدًا)",
     "sections": ["chapter-2-hard", "chapter-2-very-hard"],
     "note": "الأسئلة فقط، والإجابات مع شرحها في ملف مفتاح الإجابات · ملف PDF بصفحات A4"},
    {"file": PDF_ESSAY, "title": "ملف الـ 50 سؤالًا مقاليًا",
     "sections": ["chapter-2-essay"],
     "note": "الأسئلة مع مساحة للإجابة، والإجابات النموذجية في ملف مفتاح الإجابات · ملف PDF بصفحات A4"},
    {"file": PDF_KEY, "title": "مفتاح الإجابات الكامل: شرح الاختيار من متعدد والإجابات النموذجية للمقالي",
     "sections": ["chapter-2-hard", "chapter-2-very-hard", "chapter-2-essay"],
     "note": "إجابة كل سؤال من الأسئلة الـ 150 مع الشرح التفصيلي · ملف PDF بصفحات A4"},
]
# The PDF on the Chemistry page has Chapter 1 only (Chapter 2 has its own three PDFs).
SUBJECT_PDF_TITLE = "أسئلة الفصل الأول مع مفتاح الإجابات"
LETTERS = "أبجد"
LRI, PDI, RLM = "⁦", "⁩", "‏"


# ------------------------------------------------------------------ text
RUN = re.compile(r"[\(\[]*[+−\-]?[A-Za-z0-9][A-Za-z0-9₀-₉⁰-⁹¹²³⁺⁻().,/+×=%°Δ→\-−–:\[\] ]*")
ARABIC = re.compile(r"[؀-ۿ]")
STRONG = re.compile(r"[A-Za-z؀-ۿ]")


def trim(run):
    """Keep brackets and end punctuation outside a left-to-right run unless they belong to it."""
    lead, tail = "", ""
    while True:
        changed = False
        if run and run[-1] in " .,:":
            tail = run[-1] + tail; run = run[:-1]; changed = True
        if run and run[-1] in ")]" and run.count(run[-1]) > run.count("(" if run[-1] == ")" else "["):
            tail = run[-1] + tail; run = run[:-1]; changed = True
        if run and run[0] in "([" and run.count(run[0]) > run.count(")" if run[0] == "(" else "]"):
            lead += run[0]; run = run[1:]; changed = True
        if run and run[-1] in "([":
            tail = run[-1] + tail; run = run[:-1]; changed = True
        if not changed:
            return lead, run, tail


def isolate(text):
    """Formulas, equations and numbers inside Arabic text are wrapped in left-to-right
    isolates (as in the rest of chemistry-questions.json), so «Na₂CO₃ + 2HCl → …» keeps its order."""
    text = text.replace(LRI, "").replace(PDI, "").replace(RLM, "")
    # the titration relation, written as in the book (Ma Va / na = Mb Vb / nb)
    for a, b in (("Mₐ", "Ma"), ("Vₐ", "Va"), ("nₐ", "na"), ("M_b", "Mb"), ("V_b", "Vb"), ("n_b", "nb")):
        text = text.replace(a, b)

    def wrap(m):
        lead, run, tail = trim(m.group(0))
        if not re.search(r"[A-Za-z0-9]", run):
            return m.group(0)
        return lead + LRI + run + PDI + tail
    out = "\n".join(RUN.sub(wrap, line) for line in text.split("\n"))
    # Arabic text whose first letter is Latin (it starts with a formula) gets a
    # right-to-left mark first, so the browser reads it as right-to-left text
    first = STRONG.search(out)
    if ARABIC.search(out) and first and not ARABIC.match(first.group(0)):
        out = RLM + out
    return out


def number(option):
    m = re.match(r"\s*([0-9.]+)", option)
    return float(m.group(1)) if m else None


def place(qs, seed):
    """The correct answer is written first in the sources. Number answers are sorted
    (smallest first); the others go to positions chosen so that each letter is the
    answer about equally often."""
    rnd = random.Random(seed)
    counts = [0, 0, 0, 0]
    placed = [None] * len(qs)
    for i, q in enumerate(qs):
        if q["sort"]:
            opts = sorted(q["options"], key=number)
            placed[i] = (opts, opts.index(q["options"][0]))
            counts[placed[i][1]] += 1
    order = [i for i, q in enumerate(qs) if not q["sort"]]
    rnd.shuffle(order)
    for i in order:
        low = min(counts)
        pos = rnd.choice([k for k in range(4) if counts[k] == low])
        wrong = qs[i]["options"][1:]
        rnd.shuffle(wrong)
        opts = wrong[:pos] + [qs[i]["options"][0]] + wrong[pos:]
        placed[i] = (opts, pos)
        counts[pos] += 1
    return placed, counts


def build_questions():
    sections = []
    for (sid, _), qs, tag, diff, seed in ((SECTIONS[0], HARD, "h", "hard", 2026), (SECTIONS[1], VHARD, "v", "very-hard", 2027)):
        placed, counts = place(qs, seed)
        items = []
        for i, (q, (opts, pos)) in enumerate(zip(qs, placed), 1):
            options = [isolate(o) for o in opts]
            items.append({"id": "chem-ch2-%s%02d" % (tag, i), "type": "mcq", "lang": "ar", "prompt": isolate(q["prompt"]),
                          "options": options, "answer": options[pos], "explanation": isolate(q["explanation"]),
                          "difficulty": diff, "reviewStatus": "reviewed"})
        print("%s: answers by letter %s" % (sid, dict(zip(LETTERS, counts))))
        sections.append(items)
    essays = []
    for i, e in enumerate(ESSAY, 1):
        essays.append({"id": "chem-ch2-e%02d" % i, "type": "short", "lang": "ar", "prompt": isolate(e["prompt"]),
                       "modelAnswer": isolate(e["answer"]), "difficulty": e["difficulty"], "reviewStatus": "reviewed"})
    sections.append(essays)
    return sections


# ------------------------------------------------------------------ the data file
def update_data(sections):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    chapter = {"id": CHAPTER_ID, "title": CHAPTER_TITLE,
               "sections": [{"id": sid, "title": title, "questions": qs} for (sid, title), qs in zip(SECTIONS, sections)],
               "morePdfs": MORE_PDFS}
    others = [c for c in data["chapters"] if c["id"] != CHAPTER_ID]
    data["chapters"] = others + [chapter]
    data["pdfTitle"] = SUBJECT_PDF_TITLE
    # keep the key order of the file: schemaVersion, pdf, pdfTitle, chapters
    ordered = {"schemaVersion": data["schemaVersion"], "pdf": data["pdf"], "pdfTitle": data["pdfTitle"], "chapters": data["chapters"]}
    DATA.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: chemistry-questions.json (Chapter 2: %s)" % [len(s) for s in sections])


# ------------------------------------------------------------------ the PDFs
CSS = """
@font-face { font-family: "Cairo"; src: url("__BASE__tools/fonts/Cairo.ttf") format("truetype"); font-weight: 200 1000; font-style: oblique -11deg 11deg; }
@page { size: A4; margin: 16mm 14mm 18mm;
  @bottom-center { content: "صفحة " counter(page) " من " counter(pages); font-family: "Cairo"; font-size: 9pt; font-weight: 700; color: var(--ink); }
  @bottom-right { content: "الكيمياء • الفصل الثاني: التحليل الكيميائي"; font-family: "Cairo"; font-size: 8.5pt; color: #94a3b8; }
  @bottom-left { content: "Learn for Grade 12"; font-family: "Cairo"; font-size: 8.5pt; color: #94a3b8; } }
@page cover { margin: 0; @bottom-center { content: none; } @bottom-right { content: none; } @bottom-left { content: none; } }
:root { --ink: __INK__; }
* { box-sizing: border-box; }
html { direction: rtl; }
body { margin: 0; font-family: "Cairo", "DejaVu Sans", sans-serif; color: #1e293b; font-size: 10.8pt; line-height: 1.7; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slant { font-style: oblique 9deg; }
.cover { page: cover; width: 210mm; height: 297mm; position: relative; overflow: hidden; color: #fff; background: __COVER__; }
.cover svg.deco { position: absolute; inset: 0; width: 210mm; height: 297mm; }
.cover .inner { position: absolute; inset: 24mm 20mm 20mm; display: flex; flex-direction: column; }
.cover .kicker { display: inline-block; align-self: flex-start; background: rgba(255,255,255,.18); border: 1.5px solid rgba(255,255,255,.55);
  border-radius: 99px; padding: 2mm 6mm; font-weight: 800; font-size: 12.5pt; }
.cover h1 { font-size: 40pt; line-height: 1.25; margin: 12mm 0 2mm; font-weight: 900; text-shadow: 0 2.5mm 6mm rgba(0,20,40,.45); }
.cover h2 { font-size: 20pt; line-height: 1.5; margin: 0 0 8mm; font-weight: 800; color: #fde68a; text-shadow: 0 1.5mm 4mm rgba(0,20,40,.35); }
.cover .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.cover .stat { background: rgba(255,255,255,.95); color: #1e293b; border-radius: 6mm; padding: 4.5mm 6mm; box-shadow: 0 3mm 8mm rgba(0,20,40,.25); }
.cover .stat b { display: block; font-size: 23pt; line-height: 1.2; font-weight: 900; }
.cover .stat span { font-weight: 700; font-size: 11.5pt; }
.cover .s1 b { color: #0f766e; } .cover .s2 b { color: #4338ca; } .cover .s3 b { color: #c2410c; } .cover .s4 b { color: #be185d; }
.cover .art { margin: 8mm auto 0; width: 120mm; background: rgba(255,255,255,.94); border-radius: 8mm; padding: 4mm 5mm 3mm; text-align: center; box-shadow: 0 3mm 9mm rgba(0,20,40,.3); }
.cover .art svg { width: 100%; height: 66mm; display: block; }
.cover .art p { margin: 1mm 0 0; color: #0f766e; font-weight: 800; font-size: 10.5pt; }
.cover .foot { margin-top: auto; font-weight: 800; font-size: 12.5pt; display: flex; justify-content: space-between; }
.guide { page-break-before: always; }
.guide .box { border-radius: 6mm; padding: 6mm 7mm; margin-bottom: 6mm; }
.guide .contents { background: linear-gradient(135deg, #ccfbf1, #e0e7ff); border: 2px solid #5eead4; }
.guide .how { background: linear-gradient(135deg, #fef3c7, #ffe4e6); border: 2px solid #fcd34d; }
.guide h2 { font-size: 19pt; font-weight: 900; color: #0f766e; margin: 0 0 3mm; }
.guide .how h2 { color: #b45309; }
.guide table { width: 100%; border-collapse: collapse; font-size: 11.5pt; }
.guide td { padding: 2mm 2mm; border-bottom: 1.5px dashed rgba(15,118,110,.3); font-weight: 700; }
.guide td.n { text-align: left; color: #0f766e; font-weight: 900; width: 26mm; }
.guide td .dot { display: inline-block; width: 4mm; height: 4mm; border-radius: 50%; margin-left: 2.5mm; vertical-align: middle; }
.guide ul { margin: 0; padding-right: 6mm; }
.guide li { margin: 1.2mm 0; }
.part { page-break-before: always; }
.part-head { border-radius: 6mm; padding: 5.5mm 8mm 5mm; color: #fff; margin-bottom: 5.5mm; position: relative; overflow: hidden; }
.part-head h2 { margin: 0; font-size: 21pt; font-weight: 900; line-height: 1.35; text-shadow: 0 1.2mm 2.5mm rgba(0,0,0,.28); }
.part-head p { margin: 1mm 0 0; font-weight: 700; font-size: 11pt; opacity: .95; }
.part-head .num { position: absolute; left: 7mm; top: 2mm; font-size: 44pt; font-weight: 900; opacity: .22; }
.hard .part-head { background: linear-gradient(120deg, #0f766e, #0284c7); }
.vhard .part-head { background: linear-gradient(120deg, #4338ca, #be185d); }
.essay .part-head { background: linear-gradient(120deg, #7c2d12, #d97706); }
.keyhead .part-head { background: linear-gradient(120deg, #b45309, #be185d); }
.q { break-inside: avoid; border-radius: 4.5mm; padding: 3.2mm 4.6mm; margin: 0 0 3.8mm; background: #fff; }
.hard .q { border: 1.5px solid #99f6e4; border-right: 2.4mm solid #14b8a6; background: linear-gradient(90deg, #fff 72%, #f0fdfa); }
.vhard .q { border: 1.5px solid #c7d2fe; border-right: 2.4mm solid #6366f1; background: linear-gradient(90deg, #fff 72%, #eef2ff); }
.essay .q { border: 1.5px solid #fed7aa; border-right: 2.4mm solid #f97316; background: linear-gradient(90deg, #fff 72%, #fff7ed); }
.essay .q:nth-child(even) { border-color: #fde68a; border-right-color: #d97706; }
.qhead { display: flex; align-items: center; gap: 2.6mm; margin-bottom: 1mm; }
.badge { flex: none; min-width: 9.5mm; height: 9.5mm; padding: 0 1.5mm; border-radius: 99px; color: #fff; font-weight: 900; font-size: 11.5pt; display: flex; align-items: center; justify-content: center; }
.hard .badge { background: linear-gradient(135deg, #0d9488, #0284c7); }
.vhard .badge { background: linear-gradient(135deg, #4f46e5, #db2777); }
.essay .badge, .keyhead .badge { background: linear-gradient(135deg, #ea580c, #be185d); }
.pill { font-size: 8.6pt; font-weight: 800; border-radius: 99px; padding: .2mm 3mm; }
.pill.hard { background: #ccfbf1; color: #0f766e; border: 1.2px solid #5eead4; }
.pill.very-hard { background: #fce7f3; color: #be185d; border: 1.2px solid #f9a8d4; }
.prompt { margin: 0; font-weight: 600; white-space: pre-line; }
.opts { list-style: none; margin: 2mm 0 0; padding: 0; display: grid; grid-template-columns: 1fr; gap: 1.4mm; }
.opts.two { grid-template-columns: 1fr 1fr; column-gap: 4mm; }
.opts li { display: flex; gap: 2.2mm; align-items: flex-start; background: rgba(255,255,255,.85); border: 1.2px solid #e2e8f0; border-radius: 3mm; padding: 1mm 2.6mm; }
.opts .L { flex: none; width: 6.4mm; height: 6.4mm; margin-top: .6mm; border-radius: 50%; font-weight: 900; font-size: 10pt; display: flex; align-items: center; justify-content: center; color: #fff; background: #64748b; }
.hard .opts .L { background: #0d9488; } .vhard .opts .L { background: #4f46e5; }
.lines { margin-top: 2mm; }
.lines div { height: 7mm; border-bottom: 1.3px dotted #fdba74; }
.grid { width: 100%; border-collapse: separate; border-spacing: 1.4mm; margin: 0 0 5mm; }
.grid td { background: #fff7ed; border: 1.3px solid #fed7aa; border-radius: 2.5mm; text-align: center; padding: 1mm 0; font-weight: 800; font-size: 10.5pt; }
.grid td b { color: #94a3b8; font-weight: 700; margin-left: 1.5mm; }
.grid.h td { background: #f0fdfa; border-color: #99f6e4; } .grid.v td { background: #eef2ff; border-color: #c7d2fe; }
.keyhead h3 { font-size: 14.5pt; font-weight: 900; margin: 4mm 0 2.5mm; color: #b45309; }
.keyhead h3.first { margin-top: 0; }
.k { break-inside: avoid; border-radius: 4mm; padding: 2.8mm 4.2mm; margin: 0 0 3.2mm; border: 1.4px solid #e2e8f0; border-right: 2.2mm solid #94a3b8; background: #fff; font-size: 9.7pt; line-height: 1.62; }
.k.h { border-color: #99f6e4; border-right-color: #14b8a6; background: linear-gradient(90deg, #fff 75%, #f0fdfa); }
.k.v { border-color: #c7d2fe; border-right-color: #6366f1; background: linear-gradient(90deg, #fff 75%, #eef2ff); }
.k.e { border-color: #fed7aa; border-right-color: #f97316; background: linear-gradient(90deg, #fff 75%, #fff7ed); }
.k .khead { display: flex; align-items: center; gap: 2.4mm; margin-bottom: .8mm; }
.k .badge { min-width: 8mm; height: 8mm; font-size: 10pt; }
.k.h .badge { background: linear-gradient(135deg, #0d9488, #0284c7); } .k.v .badge { background: linear-gradient(135deg, #4f46e5, #db2777); }
.k.e .badge { background: linear-gradient(135deg, #ea580c, #be185d); }
.k .right { font-weight: 900; color: #15803d; background: #dcfce7; border: 1.2px solid #86efac; border-radius: 99px; padding: 0 3mm; }
.k .kq { margin: 0 0 1mm; color: #475569; font-weight: 600; white-space: pre-line; }
.k .ka { margin: 0 0 1mm; font-weight: 800; color: #166534; white-space: pre-line; }
.k .ke { margin: 0; white-space: pre-line; }
.k .lab { font-weight: 900; color: #b45309; }
"""

COVERS = {
    "mcq": ("#0f766e", "linear-gradient(140deg, #134e4a 0%, #0f766e 32%, #0284c7 66%, #4338ca 100%)"),
    "essay": ("#c2410c", "linear-gradient(140deg, #7c2d12 0%, #c2410c 35%, #d97706 70%, #be185d 100%)"),
    "key": ("#b45309", "linear-gradient(140deg, #1e1b4b 0%, #4338ca 30%, #be185d 66%, #f59e0b 100%)"),
}

DECO = """<svg class="deco" viewBox="0 0 210 297" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="188" cy="38" r="44" fill="#fff" fill-opacity=".09"/><circle cx="16" cy="252" r="58" fill="#fff" fill-opacity=".08"/>
<circle cx="172" cy="232" r="20" fill="#fde68a" fill-opacity=".22"/><circle cx="34" cy="72" r="8" fill="#fff" fill-opacity=".2"/>
<g fill="none" stroke="#fff" stroke-opacity=".32" stroke-width=".8">
<polygon points="152,122 165,114.5 178,122 178,137 165,144.5 152,137"/><polygon points="178,137 191,129.5 204,137 204,152 191,159.5 178,152"/>
<polygon points="165,144.5 178,152 178,167 165,174.5 152,167 152,152"/></g>
<g fill="#fff" fill-opacity=".9"><circle cx="165" cy="114.5" r="1.6"/><circle cx="204" cy="152" r="1.6"/><circle cx="152" cy="167" r="1.6"/></g>
<path d="M0 206 C 50 190 90 232 140 214 C 170 205 190 190 210 196 L210 297 L0 297 Z" fill="#fff" fill-opacity=".08"/>
</svg>"""

# A titration set (burette over a conical flask) and a rack of test tubes with the
# colours of some precipitates from the chapter.
ART = """<svg viewBox="0 0 440 240" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="liq" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a7f3d0"/><stop offset="1" stop-color="#34d399"/></linearGradient>
<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e0f2fe"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="#e0f2fe"/></linearGradient></defs>
<rect x="18" y="222" width="190" height="8" rx="4" fill="#94a3b8"/>
<rect x="30" y="20" width="8" height="204" rx="3" fill="#64748b"/>
<rect x="36" y="64" width="64" height="7" rx="3" fill="#64748b"/>
<rect x="92" y="10" width="20" height="130" rx="6" fill="url(#gl)" stroke="#0f766e" stroke-width="2.5"/>
<rect x="94.5" y="40" width="15" height="98" rx="4" fill="#fecdd3"/>
<g stroke="#0f766e" stroke-width="1.4">""" + "".join('<line x1="92" y1="%d" x2="%d" y2="%d"/>' % (y, 100 if i % 2 else 104, y) for i, y in enumerate(range(24, 136, 10))) + """</g>
<path d="M96 140 L108 140 L104 158 L100 158 Z" fill="#0f766e"/><rect x="90" y="144" width="24" height="5" rx="2" fill="#f59e0b"/>
<circle cx="102" cy="170" r="3.2" fill="#fb7185"/>
<path d="M88 178 L116 178 L116 186 L150 216 Q154 222 146 222 L58 222 Q50 222 54 216 L88 186 Z" fill="url(#gl)" stroke="#0f766e" stroke-width="2.5"/>
<path d="M66 204 L138 204 L150 216 Q154 222 146 222 L58 222 Q50 222 54 216 Z" fill="#f9a8d4"/>
<rect x="232" y="150" width="190" height="12" rx="4" fill="#b45309"/><rect x="240" y="162" width="10" height="64" fill="#b45309"/><rect x="404" y="162" width="10" height="64" fill="#b45309"/>
<rect x="236" y="218" width="182" height="8" rx="4" fill="#92400e"/>""" + "".join(
    '<g><rect x="%d" y="70" width="26" height="128" rx="13" fill="url(#gl)" stroke="#334155" stroke-width="2.2"/>'
    '<path d="M%d 150 L%d 150 L%d 185 Q%d 196 %d 196 Q%d 196 %d 185 Z" fill="%s"/>'
    '<path d="M%d 170 L%d 170 L%d 185 Q%d 196 %d 196 Q%d 196 %d 185 Z" fill="%s"/></g>'
    % (x, x + 2.5, x + 23.5, x + 23.5, x + 23.5, x + 13, x + 2.5, x + 2.5, top, x + 2.5, x + 23.5, x + 23.5, x + 23.5, x + 13, x + 2.5, x + 2.5, ppt)
    for x, top, ppt in ((250, "#e0f2fe", "#ffffff"), (290, "#fef9c3", "#facc15"), (330, "#fee2e2", "#9a3412"), (370, "#e2e8f0", "#111827"))) + """
<text x="263" y="58" font-size="15" font-family="Cairo" font-weight="800" fill="#334155" text-anchor="middle">AgCl</text>
<text x="303" y="58" font-size="15" font-family="Cairo" font-weight="800" fill="#334155" text-anchor="middle">AgI</text>
<text x="343" y="40" font-size="15" font-family="Cairo" font-weight="800" fill="#334155" text-anchor="middle">Fe(OH)₃</text>
<text x="383" y="58" font-size="15" font-family="Cairo" font-weight="800" fill="#334155" text-anchor="middle">CuS</text>
<line x1="343" y1="44" x2="343" y2="66" stroke="#334155" stroke-width="1.2"/>
</svg>"""


def esc(s):
    return html.escape(s, quote=False)


def pill(diff):
    return '<span class="pill %s">%s</span>' % (diff, "صعب جدًا" if diff == "very-hard" else "صعب")


def cover(kind, kicker, title, sub, stats, art_note):
    stat_html = "".join('<div class="stat s%d"><b>%s</b><span>%s</span></div>' % (i, b, s) for i, (b, s) in enumerate(stats, 1))
    return ('<section class="cover">' + DECO + '<div class="inner">'
            '<span class="kicker">%s</span><h1 class="slant">%s</h1><h2 class="slant">%s</h2>'
            '<div class="stats">%s</div><div class="art">%s<p>%s</p></div>'
            '<div class="foot"><span>وفق كتاب الوزارة 2026/2027</span><span dir="ltr">Learn for Grade 12</span></div>'
            '</div></section>') % (kicker, title, sub, stat_html, ART, art_note)


def guide(rows, tips):
    body = "".join('<tr><td><span class="dot" style="background:%s"></span>%s</td><td class="n">صفحة %d</td></tr>' % r for r in rows)
    return ('<section class="guide"><div class="box contents"><h2 class="slant">محتويات الملف</h2><table>' + body + '</table></div>'
            '<div class="box how"><h2 class="slant">كيف تستفيد من هذا الملف؟</h2><ul>' + "".join("<li>%s</li>" % t for t in tips) + '</ul></div></section>')


def mcq_card(n, q):
    short = all(len(re.sub("[⁦⁩‏]", "", o)) <= 34 for o in q["options"])
    opts = "".join('<li><span class="L">%s</span><span>%s</span></li>' % (LETTERS[i], esc(o)) for i, o in enumerate(q["options"]))
    return ('<div class="q"><div class="qhead"><span class="badge">%d</span>%s</div><p class="prompt">%s</p><ol class="opts%s">%s</ol></div>'
            % (n, pill(q["difficulty"]), esc(q["prompt"]), " two" if short else "", opts))


def part(cls, num, title, sub, cards):
    return ('<section class="part %s"><div class="part-head"><span class="num">%s</span><h2 class="slant">%s</h2><p>%s</p></div>%s</section>'
            % (cls, num, title, sub, "".join(cards)))


def mcq_parts(sections):
    hard, vhard = sections[0], sections[1]
    return [part("hard", "1", "القسم الأول: أسئلة صعبة", "50 سؤالًا – اختر الإجابة الصحيحة (إجابة واحدة فقط صحيحة في كل سؤال)",
                 [mcq_card(i, q) for i, q in enumerate(hard, 1)]),
            part("vhard", "2", "القسم الثاني: أسئلة صعبة جدًا", "50 سؤالًا – تطبيقات وتحليل وحسابات وتمييز بين المتشابهات",
                 [mcq_card(i, q) for i, q in enumerate(vhard, 1)])]


def essay_parts(sections):
    cards = []
    for i, q in enumerate(sections[2], 1):
        lines = 6 if q["difficulty"] == "very-hard" else 5
        cards.append('<div class="q"><div class="qhead"><span class="badge">%d</span>%s</div><p class="prompt">%s</p><div class="lines">%s</div></div>'
                     % (i, pill(q["difficulty"]), esc(q["prompt"]), "<div></div>" * lines))
    return [part("essay", "✎", "الأسئلة المقالية", "50 سؤالًا: فسّر – علّل – قارن – تنبأ – اكتب المعادلات – احسب – صمم تجربة", cards)]


def key_parts(sections):
    hard, vhard, essay = sections
    out = []
    grid = []
    for cls, name, items in (("h", "القسم الأول (أسئلة صعبة)", hard), ("v", "القسم الثاني (أسئلة صعبة جدًا)", vhard)):
        rows = []
        for r in range(5):
            cells = "".join('<td><b>%d</b>%s</td>' % (r * 10 + c + 1, LETTERS[items[r * 10 + c]["options"].index(items[r * 10 + c]["answer"])]) for c in range(10))
            rows.append("<tr>%s</tr>" % cells)
        grid.append('<h3 class="slant%s">%s</h3><table class="grid %s">%s</table>' % (" first" if cls == "h" else "", name, cls, "".join(rows)))
    out.append(part("keyhead", "✓", "مفتاح الإجابات السريع", "رقم السؤال وحرف الإجابة الصحيحة، والشرح التفصيلي في الصفحات التالية", grid))

    def mcq_key(cls, items):
        cards = []
        for i, q in enumerate(items, 1):
            letter = LETTERS[q["options"].index(q["answer"])]
            cards.append('<div class="k %s"><div class="khead"><span class="badge">%d</span><span class="right">الإجابة الصحيحة: (%s)</span></div>'
                         '<p class="kq">%s</p><p class="ka">✓ %s</p><p class="ke"><span class="lab">الشرح: </span>%s</p></div>'
                         % (cls, i, letter, esc(q["prompt"]), esc(q["answer"]), esc(q["explanation"])))
        return cards
    out.append(part("keyhead", "1", "شرح إجابات القسم الأول: الأسئلة الصعبة", "50 سؤالًا – الإجابة الصحيحة وسببها، ولماذا الاختيارات الأخرى خطأ", mcq_key("h", hard)))
    out.append(part("keyhead", "2", "شرح إجابات القسم الثاني: الأسئلة الصعبة جدًا", "50 سؤالًا – الحل خطوة بخطوة", mcq_key("v", vhard)))
    cards = []
    for i, q in enumerate(essay, 1):
        cards.append('<div class="k e"><div class="khead"><span class="badge">%d</span>%s</div><p class="kq">%s</p>'
                     '<p class="ke"><span class="lab">الإجابة النموذجية:</span>\n%s</p></div>' % (i, pill(q["difficulty"]), esc(q["prompt"]), esc(q["modelAnswer"])))
    out.append(part("keyhead", "3", "الإجابات النموذجية للأسئلة المقالية", "50 سؤالًا – النقاط الأساسية التي تُقيَّم بها الإجابة", cards))
    return out


def document(base, ink, cover_bg, body):
    css = CSS.replace("__BASE__", base).replace("__INK__", ink).replace("__COVER__", cover_bg)
    return '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>' + css + '</style></head><body>' + body + "</body></html>"


def plans(sections):
    """(file, colours, cover, parts, contents rows (colour, title), tips)"""
    return [
        (PDF_MCQ, COVERS["mcq"],
         cover("mcq", "الكيمياء • الصف الثالث الثانوي", "100 سؤال اختيار<br>من متعدد", "الفصل الثاني: التحليل الكيميائي",
               [("50", "سؤالًا صعبًا"), ("50", "سؤالًا صعبًا جدًا"), ("4", "اختيارات لكل سؤال، واحد فقط صحيح"), ("150", "إجابة مشروحة في ملف المفتاح")],
               "المعايرة ورواسب بعض الشقوق"),
         mcq_parts(sections),
         [("#14b8a6", "القسم الأول: أسئلة صعبة (50 سؤالًا)"), ("#6366f1", "القسم الثاني: أسئلة صعبة جدًا (50 سؤالًا)")],
         ["كل الأسئلة من الباب الثاني «التحليل الكيميائي» في كتاب الوزارة 2026/2027 فقط.",
          "في كل سؤال إجابة واحدة فقط صحيحة؛ اكتب حرف إجابتك ثم راجع ملف «مفتاح الإجابات الكامل».",
          "الكتل الذرية المطلوبة للحسابات مكتوبة داخل السؤال نفسه، والحجم المولاري للغاز 22.4 L في الظروف القياسية (STP).",
          "الأسئلة نفسها موجودة على الموقع تفاعليًا مع التصحيح الفوري والدرجة في قسمي «أسئلة صعبة» و«أسئلة صعبة جدًا» داخل الفصل الثاني."]),
        (PDF_ESSAY, COVERS["essay"],
         cover("essay", "الكيمياء • الصف الثالث الثانوي", "50 سؤالًا<br>مقاليًا", "الفصل الثاني: التحليل الكيميائي",
               [("50", "سؤالًا مقاليًا"), ("صعب", "وصعب جدًا فقط"), ("✎", "مساحة للإجابة بعد كل سؤال"), ("50", "إجابة نموذجية في ملف المفتاح")],
               "المعايرة ورواسب بعض الشقوق"),
         essay_parts(sections),
         [("#f97316", "الأسئلة المقالية (50 سؤالًا)")],
         ["الأسئلة: فسّر وعلّل، قارن، تنبأ بما يحدث، اكتب المعادلات الموزونة، احسب، صمم خطة للتعرف على مادة.",
          "اكتب المعادلات كاملة بالحالات الفيزيائية متى أمكن، ووضح خطوات الحل في المسائل.",
          "قارن إجابتك بالإجابة النموذجية في ملف «مفتاح الإجابات الكامل».",
          "الأسئلة نفسها موجودة على الموقع في قسم «الأسئلة المقالية» داخل الفصل الثاني، وتظهر الإجابة النموذجية بعد كتابة إجابتك."]),
        (PDF_KEY, COVERS["key"],
         cover("key", "الكيمياء • الصف الثالث الثانوي", "مفتاح الإجابات<br>الكامل", "الفصل الثاني: التحليل الكيميائي",
               [("100", "إجابة اختيار من متعدد مع الشرح"), ("50", "إجابة نموذجية للمقالي"), ("✓", "لماذا الإجابة صحيحة والبقية خطأ"), ("150", "سؤالًا في المجموع")],
               "المعايرة ورواسب بعض الشقوق"),
         key_parts(sections),
         [("#f59e0b", "مفتاح الإجابات السريع (100 سؤال)"), ("#14b8a6", "شرح إجابات القسم الأول: الأسئلة الصعبة"),
          ("#6366f1", "شرح إجابات القسم الثاني: الأسئلة الصعبة جدًا"), ("#f97316", "الإجابات النموذجية للأسئلة المقالية")],
         ["الأقسام والأرقام هنا هي نفسها في ملف الـ 100 سؤال وملف الأسئلة المقالية وعلى الموقع.",
          "ابدأ بالمفتاح السريع لتصحيح إجاباتك، ثم اقرأ شرح كل سؤال أخطأت فيه.",
          "في المسائل، تابع خطوات الحل والمعادلة الموزونة التي تُبنى عليها النسبة المولية.",
          "في الأسئلة المقالية، الإجابة النموذجية تذكر النقاط الأساسية والمعادلات المطلوبة."]),
    ]


def make_pdfs(sections):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader
    server, base = render.serve()
    made = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            for name, (ink, bg), cov, parts, rows, tips in plans(sections):
                def pages_of(body):
                    page.set_content(document(base, ink, bg, body), wait_until="networkidle")
                    page.evaluate("document.fonts.ready")
                    return len(PdfReader(io.BytesIO(page.pdf(prefer_css_page_size=True, print_background=True))).pages)
                front = pages_of(cov + guide([(c, t, 0) for c, t in rows], tips))
                starts, at = [], front + 1
                for body in parts:
                    starts.append(at)
                    at += pages_of(body.replace('<section class="part ', '<section class="', 1))
                full = cov + guide([(c, t, s) for (c, t), s in zip(rows, starts)], tips) + "".join(parts)
                page.set_content(document(base, ink, bg, full), wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(SITE / name), prefer_css_page_size=True, print_background=True)
                total = len(PdfReader(str(SITE / name)).pages)
                print("written: %s (%d pages; parts start on pages %s)" % (name, total, starts))
                made.append((name, total, starts))
            browser.close()
    finally:
        server.shutdown()
    return made


def fingerprint(questions):
    """Changes when a question, an option, an answer, an explanation or a model answer
    changes (tests/schema.test.js works it out the same way from chemistry-questions.json)."""
    digest = hashlib.sha256()
    for q in questions:
        fields = [q["prompt"]] + list(q.get("options") or []) + [q.get("answer", ""), q.get("explanation", ""), q.get("modelAnswer", "")]
        digest.update(("\x1f".join(fields) + "\x1e").encode("utf-8"))
    return digest.hexdigest()[:16]


def main():
    sections = build_questions()
    update_data(sections)
    made = make_pdfs(sections)
    contents = {PDF_MCQ: sections[0] + sections[1], PDF_ESSAY: sections[2], PDF_KEY: sections[0] + sections[1] + sections[2]}
    files = [{"pdf": name, "pages": total, "starts": starts, "questions": len(contents[name]), "fingerprint": fingerprint(contents[name])}
             for name, total, starts in made]
    sources = hashlib.sha256(b"".join((HERE / n).read_bytes() for n in ("mcq_hard.py", "mcq_vhard.py", "essay.py", "build.py"))).hexdigest()[:16]
    (HERE / "built.json").write_text(json.dumps({"files": files, "sources": sources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("written: tools/chem_ch2_bank/built.json")


if __name__ == "__main__":
    main()
