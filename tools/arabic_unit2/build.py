"""Builds Arabic Unit 2 «الأبنية» (development tool — the website only reads the results):

  arabic-questions.json   the chapter "unit-2" (before "unit-3"), with two sections:
                          50 multiple-choice questions (mcq.py) and 50 written
                          questions with model answers (essay.py)
  arabic-unit2-mcq.pdf    «الوحدة الثانية – أسئلة الاختيار من متعدد»: cover, contents,
                          the 50 questions in four sections, then the answer key and
                          the explanation of every answer in a separate section
  arabic-unit2-essay.pdf  «الوحدة الثانية – الأسئلة المقالية»: cover, contents, the 50
                          questions in seven sections with lines to write on, then the
                          model answers in a separate section
  built.json              what the PDFs were made from (tests/schema.test.js checks it)

Run it again after changing mcq.py or essay.py:
    python3 tools/arabic_unit2/build.py
Same needs as tools/arabic_unit3/build.py (Playwright with Chromium, pypdf); it uses
that file's fonts and design, so the two units' PDFs look alike."""
import hashlib
import importlib.util
import json
import pathlib
import random
import sys

sys.dont_write_bytecode = True  # no __pycache__ folders in the site

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


u3 = load("arabic_unit3_build", SITE / "tools" / "arabic_unit3" / "build.py")
MCQ = load("arabic_unit2_mcq", HERE / "mcq.py").MCQ
ESSAY = load("arabic_unit2_essay", HERE / "essay.py").ESSAY

DATA = SITE / "arabic-questions.json"
CHAPTER_ID = "unit-2"
CHAPTER_TITLE = "الوحدة الثانية – اللغة العربية: الأبنية"
MCQ_SECTION = ("unit-2-mcq", "القسم الأول: أسئلة الاختيار من متعدد")
ESSAY_SECTION = ("unit-2-essay", "القسم الثاني: الأسئلة المقالية")
MCQ_PDF = "arabic-unit2-mcq.pdf"
ESSAY_PDF = "arabic-unit2-essay.pdf"
MCQ_PDF_TITLE = "الوحدة الثانية – أسئلة الاختيار من متعدد (50 سؤالًا)"
ESSAY_PDF_TITLE = "الوحدة الثانية – الأسئلة المقالية (50 سؤالًا)"
LETTERS = "أبجد"
LEVEL = {"medium": ("متوسط", "teal"), "hard": ("صعب", "clay"), "very-hard": ("صعب جدًا", "deep")}

# The PDF groups the questions by topic; the numbers run 1–50 as on the website.
MCQ_GROUPS = [
    ("mushtaqqat", "القسم الأول", "المشتقات", 23,
     "اسم الفاعل، وصيغ المبالغة، واسم المفعول، واسم التفضيل، واسما الزمان والمكان: الصياغة والوزن والتمييز بينها."),
    ("masdar", "القسم الثاني", "المصدر واسم المرة واسم الهيئة", 12,
     "مصادر الأفعال الرباعية والخماسية والسداسية، وصياغة اسم المرة واسم الهيئة وإعرابهما."),
    ("tathniya", "القسم الثالث", "تثنية المقصور والممدود والمنقوص وجمعها", 12,
     "ما يحدث للألف والهمزة والياء عند التثنية والجمع، وحذف ياء المنقوص وبقاؤها."),
    ("majhool", "القسم الرابع", "الأفعال الملازمة للبناء للمجهول", 3,
     "إعراب ما بعد هذه الأفعال، والأفعال التي يخطئ الناس في بنائها."),
]
ESSAY_GROUPS = [
    ("أعرب", "القسم الأول", "الإعراب", "إعراب كلمات وجمل من نصوص الكتاب وأمثلته، مع بيان العلامة وسببها."),
    ("استخرج وحدّد", "القسم الثاني", "استخرج وحدّد", "استخراج المشتقات والمصادر والأسماء المقصورة والممدودة من نصوص الكتاب، وبيان أوزانها وأفعالها."),
    ("صوّب الخطأ", "القسم الثالث", "صوّب الخطأ", "تصحيح أخطاء شائعة في الضبط والتثنية والجمع والاشتقاق، مع التعليل."),
    ("علّل", "القسم الرابع", "علّل", "تعليل قواعد الوحدة: الحذف والقلب والرد، وإعراب ما بعد الأفعال الملازمة للبناء للمجهول."),
    ("أعد الصياغة", "القسم الخامس", "أعد الصياغة", "تحويل الجمل إلى المثنى والجمع، وصياغة المشتقات واسم المرة والهيئة وفق المطلوب."),
    ("أكمل وفق القاعدة", "القسم السادس", "أكمل وفق القاعدة", "إكمال الجمل بالمصدر أو المشتق أو الاسم المقصور أو الفعل المناسب."),
    ("تطبيق وتحليل", "القسم السابع", "تطبيقات وتحليل", "أسئلة تجمع أكثر من قاعدة وتحتاج إلى تحليل."),
]


# ---------------------------------------------------------------- the data

def answer_positions(count, seed=20261110):
    """Where the correct option goes in each question: each of the four places
    about equally often, and never the same place three times in a row."""
    base = [i % 4 for i in range(count)]
    rng = random.Random(seed)
    while True:
        rng.shuffle(base)
        if all(not (base[i] == base[i - 1] == base[i - 2]) for i in range(2, count)):
            return base


def chapter_data():
    assert len(MCQ) == 50 and len(ESSAY) == 50, (len(MCQ), len(ESSAY))
    assert sum(g[3] for g in MCQ_GROUPS) == 50
    kinds = [g[0] for g in ESSAY_GROUPS]
    assert [e["kind"] for e in ESSAY] == sorted((e["kind"] for e in ESSAY), key=kinds.index), "essays are grouped by kind, in this order"
    mcqs = []
    for n, (q, place) in enumerate(zip(MCQ, answer_positions(len(MCQ))), 1):
        right, *wrong = q["options"]
        assert len(wrong) == 3 and len(set(q["options"])) == 4, n
        options = wrong[:place] + [right] + wrong[place:]
        mcqs.append({"id": "ar-u2-mcq-%02d" % n, "type": "mcq", "lang": "ar", "prompt": q["prompt"], "options": options,
                     "answer": right, "difficulty": q["difficulty"], "explanation": q["explanation"], "reviewStatus": "reviewed"})
    essays = []
    for n, e in enumerate(ESSAY, 1):
        essays.append({"id": "ar-u2-essay-%02d" % n, "type": "short", "lang": "ar", "prompt": e["prompt"], "modelAnswer": e["answer"],
                       "difficulty": e["difficulty"], "revealAnytime": True, "reviewStatus": "reviewed"})
    return {
        "id": CHAPTER_ID,
        "title": CHAPTER_TITLE,
        "morePdfs": [
            {"file": MCQ_PDF, "title": MCQ_PDF_TITLE, "sections": [MCQ_SECTION[0]],
             "note": "مفتاح الإجابات وشرح كل إجابة في قسم مستقل آخر الملف · ملف PDF بمقاس A4"},
            {"file": ESSAY_PDF, "title": ESSAY_PDF_TITLE, "sections": [ESSAY_SECTION[0]],
             "note": "الإجابات النموذجية في قسم مستقل آخر الملف · ملف PDF بمقاس A4"},
        ],
        "sections": [
            {"id": MCQ_SECTION[0], "title": MCQ_SECTION[1], "questions": mcqs},
            {"id": ESSAY_SECTION[0], "title": ESSAY_SECTION[1], "questions": essays},
        ],
    }


def write_data(chapter):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    chapters = [c for c in data["chapters"] if c["id"] != CHAPTER_ID]
    at = next(i for i, c in enumerate(chapters) if c["id"] == "unit-3")  # Unit 2 comes before Unit 3
    chapters.insert(at, chapter)
    data["chapters"] = chapters
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fingerprint(questions):
    """Changes whenever a question's text, options, answer, explanation, model
    answer or level changes (tests/schema.test.js works it out the same way)."""
    digest = hashlib.sha256()
    for q in questions:
        fields = [q["prompt"]] + list(q.get("options") or []) + [q.get("answer", ""), q.get("explanation", ""), q.get("modelAnswer", ""), q["difficulty"]]
        digest.update(("\x1f".join(fields) + "\x1e").encode("utf-8"))
    return digest.hexdigest()[:16]


# ---------------------------------------------------------------- the PDFs

ar, text, body_text, how_many = u3.ar, u3.text, u3.body_text, u3.how_many

EXTRA_CSS = """
.chip.deep { background: var(--clay); color: #fff; }
.chip.kind { background: var(--gold-soft); color: #7d5f2c; }
.cover .kind-title { margin-top: 5mm; font-family: "Kufi", sans-serif; font-size: 13pt; font-weight: 700; color: var(--clay); }
.q .tags { flex: none; display: flex; flex-direction: column; align-items: flex-end; gap: 1mm; margin-top: 1mm; }
.lines { margin: 1.5mm 11.7mm 0 0; }
.lines div { height: 7.6mm; border-bottom: 0.6pt dotted #c9bba2; }
.model h3 { font-family: "Kufi", sans-serif; font-size: 10pt; color: var(--teal); margin: 4mm 0 1.5mm; break-after: avoid; }
.model ol { list-style: none; margin: 0; padding: 0; }
.model li { break-inside: avoid; display: flex; gap: 3mm; padding: 2mm 0 2.2mm; border-bottom: 0.5pt dotted #ddd3c2; font-size: 10pt; line-height: 1.8; }
.model li .num { width: 7mm; height: 7mm; font-size: 8.6pt; border-radius: 2mm; }
.model li .a { flex: 1 1 auto; min-width: 0; white-space: pre-line; }
.why li .ref, .model li .ref { color: #8d8577; font-size: 0.85em; white-space: nowrap; }
"""


def level_chip(q):
    name, tone = LEVEL[q["difficulty"]]
    return '<span class="chip %s">%s</span>' % (tone, name)


def level_counts(questions):
    present = [d for d in LEVEL if any(q["difficulty"] == d for q in questions)]
    return "".join('<span class="chip %s">%s: %s</span>' % (LEVEL[d][1], LEVEL[d][0], ar(sum(q["difficulty"] == d for q in questions))) for d in present)


def cover(kind_title, facts, foot):
    boxes = "".join('<div class="fact"><b>%s</b><span>%s</span></div>' % f for f in facts)
    return """
<section class="cover"><div class="frame"><div class="frame-in">
  <div class="top">اللغة العربية · الصف الثالث الثانوي</div>
  <div class="star"><span></span></div>
  <h1>الوحدة الثانية – اللغة العربية</h1>
  <div class="rule"></div>
  <div class="unit">الأبنية</div>
  <div class="parts">المشتقات · المصدر واسم المرة والهيئة · تثنية المقصور والممدود والمنقوص وجمعها · الأفعال الملازمة للبناء للمجهول</div>
  <div class="kind-title">%s</div>
  <div class="facts">%s</div>
  <div class="foot">وفق كتاب «اللغة العربية» للصف الثالث الثانوي — وزارة التربية والتعليم، العام الدراسي ٢٠٢٦/٢٠٢٧<br>
  %s<br><span class="site">%s</span></div>
</div></div></section>""" % (kind_title, boxes, foot, u3.SITE_NAME)


def intro(rows, last, pages, tips, legend):
    toc = "".join('<div class="row"><span class="no">%s</span><span class="name">%s</span><span class="count">%s</span><span class="pg">%s</span></div>'
                  % (no, name, how_many(count), ar(pages[key]) if pages.get(key) else "") for key, no, name, count in rows)
    toc += ('<div class="row"><span class="no">في الختام</span><span class="name">%s</span><span class="count"></span><span class="pg">%s</span></div>'
            % (last, ar(pages["answers"]) if pages.get("answers") else ""))
    return """
<section class="intro">
  <h2>محتوى الملف</h2>
  <div class="rule"></div>
  <div class="toc">%s</div>
  <div class="howto">
    <h3>قبل أن تبدأ</h3>
    <ul>%s</ul>
    <div class="legend">مستوى السؤال: %s</div>
  </div>
</section>""" % (toc, "".join("<li>%s</li>" % t for t in tips), legend)


def opener(no, name, desc, questions):
    chips = '<span class="chip gold">%s</span>%s' % (how_many(len(questions)), level_counts(questions))
    return '<header class="opener"><div class="no">%s</div><h2>%s</h2><p>%s</p><div class="chips">%s</div></header>' % (no, name, desc, chips)


def mcq_groups(questions):
    groups, at = [], 0
    for key, no, name, count, desc in MCQ_GROUPS:
        groups.append((key, no, name, desc, list(enumerate(questions[at:at + count], at + 1))))
        at += count
    return groups


def mcq_document(questions, pages=None):
    pages = pages or {}
    groups = mcq_groups(questions)
    legend = " ".join('<span class="chip %s">%s</span> %s' % (LEVEL[d][1], LEVEL[d][0], how_many(sum(q["difficulty"] == d for q in questions))) for d in LEVEL)
    parts = [("cover", cover("أسئلة الاختيار من متعدد",
                             [(ar(50), "سؤال اختيار من متعدد"), (ar(len(groups)), "أقسام منظّمة"), ("٣ مستويات", "متوسط · صعب · صعب جدًا")],
                             "مع مفتاح الإجابات وشرح كل إجابة في قسم مستقل في آخر الملف")),
             ("intro", intro([(k, no, name, len(qs)) for k, no, name, _, qs in groups], "مفتاح الإجابات وشرحها", pages, [
                 "الأسئلة كلها من الوحدة الثانية «الأبنية» في كتاب الوزارة: المشتقات، والمصدر واسم المرة والهيئة، وتثنية المقصور والممدود والمنقوص وجمعها، والأفعال الملازمة للبناء للمجهول.",
                 "انتبه للضبط بالشكل؛ فتغيير حركة واحدة قد يغيّر الإجابة (مثل: مُكْرِم ومُكْرَم، وجَلْسة وجِلْسة).",
                 "اختر إجابة واحدة لكل سؤال، ثم راجع إجاباتك من مفتاح الإجابات في آخر الملف، واقرأ شرح ما أخطأت فيه.",
                 "الأسئلة نفسها على الموقع لتحلّها وتعرف درجتك ونسبتك المئوية فورًا، بالترقيم نفسه.",
             ], legend))]
    for key, no, name, desc, numbered in groups:
        body = []
        for n, q in numbered:
            short = all(len(o) <= 28 for o in q["options"])
            items = "".join('<li><span class="l">%s</span><span class="t">%s</span></li>' % (LETTERS[i], body_text(o)) for i, o in enumerate(q["options"]))
            body.append('<article class="q"><div class="q-top"><span class="num">%s</span><div class="prompt">%s</div><div class="tags">%s</div></div>'
                        '<ul class="opts%s">%s</ul></article>' % (ar(n), body_text(q["prompt"]), level_chip(q), " two" if short else "", items))
        parts.append((key, '<section class="section">%s%s</section>' % (opener(no, name, desc, [q for _, q in numbered]), "".join(body))))
    # the answer key: the grid of letters, then the explanations
    cells = ['<td><span class="n">%s</span><span class="a">%s</span></td>' % (ar(n), LETTERS[q["options"].index(q["answer"])]) for n, q in enumerate(questions, 1)]
    table = "".join("<tr>%s</tr>" % "".join(cells[i:i + 10]) for i in range(0, len(cells), 10))
    reasons = []
    for key, no, name, desc, numbered in groups:
        items = "".join('<li><b>%s</b> <span class="ans">(%s) %s</span> — %s <span class="ref">(الكتاب: ص %s)</span></li>'
                        % (ar(n), LETTERS[q["options"].index(q["answer"])], body_text(q["answer"]), body_text(q["explanation"]), q["page"])
                        for n, q in numbered)
        reasons.append("<h3>%s: %s</h3><ol>%s</ol>" % (no, name, items))
    parts.append(("answers", '<section class="section key"><header class="opener"><div class="no">في الختام</div><h2>مفتاح الإجابات</h2>'
                             '<p>رقم السؤال وحرف الإجابة الصحيحة، ثم شرح كل إجابة في الصفحات التالية.</p></header>'
                             '<div class="grid-title">الأسئلة من ١ إلى ٥٠</div><table class="grid">%s</table></section>' % table))
    parts.append(("why", '<section class="section why"><header class="opener"><div class="no">مفتاح الإجابات</div><h2>شرح الإجابات</h2></header>%s</section>' % "".join(reasons)))
    return parts


def essay_groups(questions):
    groups = []
    for kind, no, name, desc in ESSAY_GROUPS:
        numbered = [(n, q) for n, q in enumerate(questions, 1) if q["kind"] == kind]
        groups.append((kind, no, name, desc, numbered))
    assert sum(len(g[4]) for g in groups) == len(questions)
    return groups


def essay_document(questions, pages=None):
    pages = pages or {}
    groups = essay_groups(questions)
    keys = {kind: "s%d" % i for i, (kind, *_rest) in enumerate(ESSAY_GROUPS, 1)}
    legend = " ".join('<span class="chip %s">%s</span> %s' % (LEVEL[d][1], LEVEL[d][0], how_many(sum(q["difficulty"] == d for q in questions)))
                      for d in LEVEL if any(q["difficulty"] == d for q in questions))
    parts = [("cover", cover("الأسئلة المقالية",
                             [(ar(50), "سؤالًا مقاليًّا"), (ar(len(groups)), "أنواع من الأسئلة"), ("صعب وصعب جدًا", "مستويات الأسئلة")],
                             "مع الإجابات النموذجية في قسم مستقل في آخر الملف")),
             ("intro", intro([(keys[k], no, name, len(qs)) for k, no, name, _, qs in groups], "الإجابات النموذجية", pages, [
                 "الأسئلة متنوعة: إعراب، واستخراج وتحديد، وتصويب الخطأ، وتعليل، وإعادة صياغة، وإكمال وفق القاعدة، وتطبيقات تحتاج إلى تحليل — وكلها من الوحدة الثانية «الأبنية» في كتاب الوزارة.",
                 "اكتب إجابتك في السطور تحت كل سؤال، واضبط الكلمات بالشكل حين يكون الضبط هو المطلوب.",
                 "الإجابات النموذجية في قسم مستقل في آخر الملف؛ قارن إجابتك بها بعد أن تنتهي من القسم.",
                 "الأسئلة نفسها على الموقع بالترقيم نفسه، ويمكنك كتابة إجابتك هناك وعرض الإجابة النموذجية متى شئت.",
             ], legend))]
    for kind, no, name, desc, numbered in groups:
        body = []
        for n, q in numbered:
            lines = min(9, max(3, q["answer"].count("\n") + 2))
            body.append('<article class="q"><div class="q-top"><span class="num">%s</span><div class="prompt">%s</div><div class="tags">%s</div></div>'
                        '<div class="lines">%s</div></article>' % (ar(n), body_text(q["prompt"]), level_chip(q), "<div></div>" * lines))
        parts.append((keys[kind], '<section class="section">%s%s</section>' % (opener(no, name, desc, [q for _, q in numbered]), "".join(body))))
    answers = []
    for kind, no, name, desc, numbered in groups:
        items = "".join('<li><span class="num">%s</span><div class="a">%s <span class="ref">(الكتاب: ص %s)</span></div></li>'
                        % (ar(n), body_text(q["answer"]), q["page"]) for n, q in numbered)
        answers.append("<h3>%s: %s</h3><ol>%s</ol>" % (no, name, items))
    parts.append(("answers", '<section class="section model"><header class="opener"><div class="no">في الختام</div><h2>الإجابات النموذجية</h2>'
                             '<p>إجابة نموذجية لكل سؤال بالترقيم نفسه، مع رقم الصفحة في كتاب الوزارة. تُقبل الإجابات الصحيحة الأخرى حين يسمح السؤال بأكثر من إجابة.</p></header>%s</section>'
                  % "".join(answers)))
    return parts


def document(title, running, parts, whole=True):
    return """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><base href="__BASE__"><title>%s</title>
<style>%s%s%s%s</style></head><body>%s</body></html>""" % (
        text(title), u3.BASE_CSS, u3.page_css(running, first_blank=whole), u3.QUESTIONS_CSS, EXTRA_CSS, "".join(h for _, h in parts))


def make_pdfs():
    from playwright.sync_api import sync_playwright
    mcqs = [dict(q, options=o["options"], answer=o["answer"]) for q, o in zip(MCQ, chapter_data()["sections"][0]["questions"])]
    jobs = [(MCQ_PDF, "الوحدة الثانية – اللغة العربية: أسئلة الاختيار من متعدد",
             "الوحدة الثانية «الأبنية» — أسئلة الاختيار من متعدد — اللغة العربية للصف الثالث الثانوي", lambda pages=None: mcq_document(mcqs, pages)),
            (ESSAY_PDF, "الوحدة الثانية – اللغة العربية: الأسئلة المقالية",
             "الوحدة الثانية «الأبنية» — الأسئلة المقالية — اللغة العربية للصف الثالث الثانوي", lambda pages=None: essay_document(ESSAY, pages))]
    server, base = u3.serve(SITE)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            def make(source, name):
                page.set_content(source.replace("__BASE__", base, 1), wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(SITE / name), prefer_css_page_size=True, print_background=True)

            for name, title, running, build in jobs:
                # every part starts on a new page: print the parts before each one to find
                # the page where it begins (for the contents page)
                parts = build()
                scratch = SITE / ".question-part.pdf"
                pages = {parts[0][0]: 1}
                for k in range(1, len(parts)):
                    make(document(title, running, parts[:k]), scratch.name)
                    pages[parts[k][0]] = u3.page_count(scratch) + 1
                scratch.unlink()
                assert pages["intro"] == 2 and pages[parts[2][0]] == 3, pages
                make(document(title, running, build(pages)), name)
                total = u3.page_count(SITE / name)
                assert total >= pages[parts[-1][0]], (name, total, pages)
                print("written:", name, total, "pages; parts start on", pages)
            browser.close()
    finally:
        server.shutdown()


def main():
    chapter = chapter_data()
    write_data(chapter)
    print("written:", DATA.name, "chapter", CHAPTER_ID, [(s["id"], len(s["questions"])) for s in chapter["sections"]])
    make_pdfs()
    mcqs, essays = (s["questions"] for s in chapter["sections"])
    (HERE / "built.json").write_text(json.dumps({"files": [
        {"pdf": MCQ_PDF, "questions": len(mcqs), "fingerprint": fingerprint(mcqs)},
        {"pdf": ESSAY_PDF, "questions": len(essays), "fingerprint": fingerprint(essays)},
    ]}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
