# «الدكتور والمزارع» — Biology game progress

This file says where the work on the Biology game stopped, so it can be
continued later from the same point ("كمّل اللعبة").

Page: `bio-game.html` (not linked from the site menus yet — only by its
direct link, until the owner approves).

## What the game is

- Grade 12 Biology, Chapter 1 (الدعامة والحركة) and Chapter 2 (التنسيق
  الهرموني), every idea of the book, from the booklet content
  (`tools/bio_revision_booklet/content/ch1.html`, `ch2.html`).
- Two places: the **hospital** (orthopaedic doctor, lab analyses, X-rays,
  emergencies, follow-ups, patients asking "why") and the **farm** (plant
  problems, the farmer's decisions, "healthy plant" traps, the microscope,
  experiments, comparisons).
- Levels 1–6 in every place: تعرّف، وظيفة، حالة، فرّق، لو حصل…، اربط.
- Mastery: 3 stars per idea, at most one star per idea in a shift, never
  twice in a row from the same case; a wrong answer takes a star away and
  brings the idea back with another story. Mastery map (green / red).
- After every answer: why the choice is wrong, the right answer, and the
  explanation from the book step by step in Egyptian Arabic, with the part
  drawn and labelled.
- Drawings: real-looking people with faces, upper body only while talking;
  the "camera" moves to the part (leg, knee, X-ray, microscope); labelled
  drawing after the answer. **All characters are men — no female element at
  all.** The parts of Chapter 2 about female hormones (ovary, oestrogen,
  progesterone, relaxin, prolactin, oxytocin, placenta, pregnancy) are taught
  through **lab reports only**, with no female character.
- Progress is kept in the browser only (localStorage `g12-bio-game`):
  numbers about ideas and cases, nothing about the student.

## Files

| File | What it is |
|---|---|
| `bio-game.html` | the page |
| `bio-game.css` | the game's look (site pastel colours) |
| `bio-game-engine.js` | the rules: levels, stars, shifts, saving |
| `bio-game-art.js` | the people (cast of 13 men) and backgrounds |
| `bio-game-art-ch1.js` | Chapter 1 close-ups (leg, knee, X-rays, vertebra, skull, arm, leg bones, joints, cartilage, muscle, sarcomere, nerve–muscle junction, muscle types, three systems, skeleton, gut) |
| `bio-game.js` | the screens: entrance, shift, case, summary, mastery map |
| `bio-game-ch1.json` | Chapter 1 content |
| `bio-game-ch2.json` | Chapter 2 content (empty for now — shows «قريبًا») |
| `tests/bio-game.test.js` | content checks + rules (part of `npm test`) |

The content JSON files are generated from the Python files in
`tools/bio_game/` (one file per place, for example `ch1_hospital.py`):
edit those, then run `python3 tools/bio_game/build.py` and `npm test`.

## Stages

1. ✅ Engine (levels, stars, mastery map, saving) + page + screens.
2. ✅ Chapter 1 — hospital: 30 ideas, 90 cases (every idea 3 cases or more,
   2–3 stories each, 4–5 wrong choices with "why"), levels 1–6.
3. ⏳ Chapter 1 — farm: cuticle / suberin / cellulose / lignin; mimosa (touch
   and sleep movements); tropisms; tendrils (5 steps, why they coil, no
   support); contractile roots; tendrils vs roots; cytoplasmic streaming
   (Elodea). New farm drawings needed: stem section, mimosa, pea tendril,
   bulb roots, tropism, Elodea cell.
4. ⏳ Chapter 2 — hospital (pituitary, thyroid, parathyroid, adrenal,
   pancreas, testes, GI hormones), lab reports (incl. the female-hormone
   parts, no female character), farm (auxins, Boysen-Jensen), Starling,
   hormone properties, gland types; Chapter 2 drawings.
5. ⏳ Final exam, certificate, patient album, daily challenge.
6. ⏳ Full check against the booklet, desktop + phone, publish, send the link.

## Next step

Stage 3: write the Chapter 1 farm track (`ch1-farm`, host عبد الرحمن) and its
drawings.
