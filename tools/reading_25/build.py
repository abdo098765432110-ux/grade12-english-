# -*- coding: utf-8 -*-
"""Writes the «حل 25 قطعة» passages into reading-passages.json.

    python3 tools/reading_25/build.py

Each passage carries the teacher's name (shown above the passage title on the site).
Passages that are not part of this set are kept as they are.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import passages as source  # noqa: E402

LETTERS = "abcd"
ARABIC = re.compile(r"[؀-ۿ]")
FIRST_LETTER = re.compile(r"[A-Za-z؀-ۿ]")

# The PDF numbers its passages 1–25 but uses 10 twice, so those two are 10 (a) and 10 (b);
# every other number is the same as in the PDF.
NUMBERS = [str(n) for n in range(1, 10)] + ["10a", "10b"] + [str(n) for n in range(11, 26)]


def title_of(number):
    if number.startswith("10") and len(number) == 3:
        return "Passage 10 (%s)" % number[2]
    return "Passage %s" % number


PREFIX = "abqary-"


def id_of(number):
    return PREFIX + (number.zfill(2) if number.isdigit() else number)


def build_passage(number, data):
    pid = id_of(number)
    questions = []
    for index, (prompt, options, letter, explanation) in enumerate(data["questions"]):
        where = "%s question %d" % (pid, index + 1)
        assert 2 <= len(options) <= 4, where
        assert len(set(options)) == len(options), where + ": repeated option"
        assert letter in LETTERS[:len(options)], where
        first = FIRST_LETTER.search(explanation)
        # The explanation is in Arabic: it must start with an Arabic word so it is shown right to left.
        assert first and ARABIC.match(first.group()), where + ": explanation must start in Arabic"
        questions.append({
            "id": "%s-q%d" % (pid, index + 1),
            "type": "mcq",
            "prompt": prompt,
            "options": options,
            "answer": options[LETTERS.index(letter)],
            "explanation": explanation,
            "reviewStatus": "unreviewed",
        })
    return {
        "id": pid,
        "title": title_of(number),
        "teacher": source.TEACHER,
        "source": source.SOURCE,
        "reviewStatus": "unreviewed",
        "paragraphs": data["paragraphs"],
        "questions": questions,
    }


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as handle:
        return json.load(handle)


def save(name, data):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    assert len(source.P) == len(NUMBERS) == 26, len(source.P)
    built = [build_passage(number, data) for number, data in zip(NUMBERS, source.P)]

    reading = load("reading-passages.json")
    others = [p for p in reading.get("passages", []) if not str(p.get("id", "")).startswith(PREFIX)]
    reading["passages"] = others + built
    save("reading-passages.json", reading)

    count = sum(len(p["questions"]) for p in built)
    print("%d passages, %d questions written." % (len(built), count))


if __name__ == "__main__":
    main()
