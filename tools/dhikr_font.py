"""Makes dhikr-amiri.woff: the Amiri font (tools/fonts, SIL Open Font License)
cut down to the letters and marks used in dhikr.js, so the dhikr card can show
its text in Amiri without loading the whole font (development tool).

Run it again after changing the texts in dhikr.js:
    python3 tools/dhikr_font.py
Needs fontTools (pip install fonttools)."""
import json
import pathlib
import re

from fontTools import subset

SITE = pathlib.Path(__file__).resolve().parent.parent
source = (SITE / "dhikr.js").read_text(encoding="utf-8")
texts = re.findall(r"text: '([^']*)'", source)
assert len(texts) >= 20, "could not read the texts from dhikr.js"
characters = sorted(set("".join(texts)) | set(" ،"))

options = subset.Options()
options.flavor = "woff"
options.layout_features = ["*"]       # keep Arabic joining, ligatures and mark placement
options.name_IDs = ["*"]
options.name_languages = ["*"]
options.notdef_outline = True
font = subset.load_font(str(SITE / "tools" / "fonts" / "Amiri-Regular.ttf"), options)
subsetter = subset.Subsetter(options)
subsetter.populate(text="".join(characters))
subsetter.subset(font)
subset.save_font(font, str(SITE / "dhikr-amiri.woff"), options)
# the characters in the font, for tests/schema.test.js (it fails if dhikr.js gains a character the font lacks)
(SITE / "tools" / "dhikr_font.json").write_text(json.dumps({"characters": "".join(characters)}, ensure_ascii=False) + "\n", encoding="utf-8")
print("written: dhikr-amiri.woff, %d characters, %d bytes" % (len(characters), (SITE / "dhikr-amiri.woff").stat().st_size))
