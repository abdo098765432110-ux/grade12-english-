# -*- coding: utf-8 -*-
"""Build bio-game-ch1.json / bio-game-ch2.json (at the top of the project) from the content modules in this folder.
Run: python3 tools/bio_game/build.py"""
import importlib, json, os, sys
sys.dont_write_bytecode = True
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CHAPTERS = {
    1: {"title": "الفصل الأول: الدعامة والحركة", "modules": ["ch1_hospital", "ch1_farm"]},
    2: {"title": "الفصل الثاني: التنسيق الهرموني", "modules": ["ch2_hospital", "ch2_lab", "ch2_farm"]},
}


def build(ch):
    spec = CHAPTERS[ch]
    out = {"chapter": ch, "title": spec["title"], "tracks": [], "ideas": [], "cases": []}
    for name in spec["modules"]:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        out["tracks"].append(m.TRACK)
        for iid, nm, note in m.IDEAS:
            out["ideas"].append({"id": iid, "track": m.TRACK["id"], "name": nm, "note": note})
        out["cases"].extend(m.CASES)
    return out


def check(data):
    probs = []
    ideas = {i["id"] for i in data["ideas"]}
    per = Counter(c["idea"] for c in data["cases"])
    for i in data["ideas"]:
        if per[i["id"]] == 0:
            probs.append("idea without cases: " + i["id"])
    ids = Counter(c["id"] for c in data["cases"])
    for k, v in ids.items():
        if v > 1:
            probs.append("repeated case id: " + k)
    for c in data["cases"]:
        if c["idea"] not in ideas:
            probs.append(c["id"] + ": unknown idea " + c["idea"])
        if len(c["wrong"]) < 3:
            probs.append(c["id"] + ": fewer than 3 wrong")
        for w in c["wrong"]:
            if w["text"].strip() == c["answer"].strip():
                probs.append(c["id"] + ": wrong == answer")
    return probs


if __name__ == "__main__":
    for ch in (1, 2):
        data = build(ch)
        probs = check(data)
        path = os.path.join(REPO, "bio-game-ch%d.json" % ch)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.write("\n")
        lv = Counter(c["level"] for c in data["cases"])
        print("ch%d: %d tracks, %d ideas, %d cases, levels %s" % (
            ch, len(data["tracks"]), len(data["ideas"]), len(data["cases"]), dict(sorted(lv.items()))))
        for p in probs:
            print("  !", p)
