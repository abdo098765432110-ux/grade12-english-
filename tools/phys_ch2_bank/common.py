"""Shared helpers for the Physics Chapter 2 question bank (development tool).

Source: the Ministry book «الفيزياء» للصف الثالث الثانوي 2026/2027, Unit 1, Chapter 2
«التأثير المغناطيسي للتيار الكهربي وأجهزة القياس الكهربي» (book pages 25–53).

MCQ:   Q(level, topic, prompt, options, solution, fig=None, alt=None)
       options: [(text, reason), …] with the CORRECT option first; build.py places it.
       solution: the worked steps (formula, substitution, result with unit).
       numeric=True: the four options are numbers and are shown in increasing order.
Essay: E(level, kind, prompt, answer, fig=None, alt=None)

Levels: "easy", "medium", "hard", "very-hard".
Topics (the parts of the chapter, in the book's order): see TOPICS."""

E_, M_, H_, V_ = "easy", "medium", "hard", "very-hard"

TOPICS = [
    ("wire", "المجال المغناطيسي لسلك مستقيم والفيض المغناطيسي"),
    ("loop", "المجال المغناطيسي لملف دائري"),
    ("solenoid", "المجال المغناطيسي لملف لولبي"),
    ("force", "القوة المغناطيسية على سلك يمر به تيار"),
    ("parallel", "القوة المتبادلة بين سلكين متوازيين"),
    ("torque", "عزم الازدواج وعزم ثنائي القطب المغناطيسي"),
    ("galv", "الجلفانومتر ذو الملف المتحرك"),
    ("ammeter", "الأميتر ومجزئ التيار"),
    ("voltmeter", "الفولتميتر والمقاومة المضاعفة للجهد"),
    ("ohmmeter", "الأوميتر"),
]

# The lessons of the chapter (on the website and in the PDF the questions are grouped
# by lesson): key, ordinal, title, the topics of its MCQs.
LESSONS = [
    ("l1", "الدرس الأول", "المجال المغناطيسي لتيار يمر في سلك مستقيم", ["wire"]),
    ("l2", "الدرس الثاني", "المجال المغناطيسي لتيار يمر في ملف دائري", ["loop"]),
    ("l3", "الدرس الثالث", "المجال المغناطيسي لتيار يمر في ملف لولبي", ["solenoid"]),
    ("l4", "الدرس الرابع", "القوة المغناطيسية المؤثرة على سلك يمر به تيار", ["force"]),
    ("l5", "الدرس الخامس", "القوة المتبادلة بين سلكين متوازيين يمر بهما تيار", ["parallel"]),
    ("l6", "الدرس السادس", "عزم الازدواج والجلفانومتر ذو الملف المتحرك", ["torque", "galv"]),
    ("l7", "الدرس السابع", "الأميتر والفولتميتر", ["ammeter", "voltmeter"]),
    ("l8", "الدرس الثامن", "الأوميتر", ["ohmmeter"]),
]


def lesson(key, items):
    """Marks the essay questions of one lesson."""
    assert key in [k for k, *_ in LESSONS], key
    for item in items:
        item["lesson"] = key
    return items


def Q(level, topic, prompt, options, solution, fig=None, alt=None, numeric=False):
    assert level in (E_, M_, H_, V_), level
    assert topic in dict(TOPICS), topic
    assert len(options) == 4 and len({o[0] for o in options}) == 4, prompt
    assert (fig is None) == (alt is None), prompt
    return {"difficulty": level, "topic": topic, "prompt": prompt, "options": options,
            "solution": solution, "image": fig, "imageAlt": alt, "numeric": numeric}


def E(level, kind, prompt, answer, fig=None, alt=None):
    assert level in (H_, V_), level
    assert (fig is None) == (alt is None), prompt
    return {"difficulty": level, "kind": kind, "prompt": prompt, "answer": answer, "image": fig, "imageAlt": alt}
