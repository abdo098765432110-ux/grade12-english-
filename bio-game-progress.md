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
| `bio-game-art-ch1.js` | Chapter 1 hospital close-ups (leg, knee, X-rays, vertebra, skull, arm, leg bones, joints, cartilage, muscle, sarcomere, nerve–muscle junction, muscle types, three systems, skeleton, gut) |
| `bio-game-art-ch1-farm.js` | Chapter 1 farm close-ups (stem cross-section, mimosa, pea tendril, narcissus bulb, the two pulls, tropisms, Elodea cell) |
| `bio-game.js` | the screens: entrance, shift, case, summary, mastery map |
| `bio-game-ch1.json` | Chapter 1 content |
| `bio-game-art-ch2.js` | Chapter 2 close-ups (glands map, pituitary, thyroid, adrenal, pancreas, blood-sugar chart, calcium, digestive hormones, Starling, lab report, auxin, growth hormone) |
| `bio-game-ch2.json` | Chapter 2 content |
| `tests/bio-game.test.js` | content checks + rules (part of `npm test`) |

The content JSON files are generated from the Python files in
`tools/bio_game/` (one file per place, for example `ch1_hospital.py`):
edit those, then run `python3 tools/bio_game/build.py` and `npm test`.

## Stages

1. ✅ Engine (levels, stars, mastery map, saving) + page + screens.
2. ✅ Chapter 1 — hospital: 30 ideas, 90 cases (every idea 3 cases or more,
   2–3 stories each, 4–5 wrong choices with "why"), levels 1–6.
3. ✅ Chapter 1 — farm: 15 ideas, 54 cases (cuticle / suberin / cellulose /
   lignin, mimosa touch and sleep, tropisms, tendrils, contractile roots,
   Elodea), levels 1–6, with 7 farm drawings.
4. ✅ Chapter 2 — 3 places, 36 ideas, 108 cases: the endocrine clinic (22
   ideas), the lab (8 ideas: FSH/LH, prolactin, oxytocin, oestrogen,
   progesterone, relaxin, adrenal sex hormones, sources — lab reports only,
   no female character), the auxin farm (6 ideas); 12 drawings.
5. ✅ Extras on the entrance: the daily challenge (5 mixed cases, the same
   all day, with a streak of days), the final exam (20 cases of levels 3–6
   from every place; 85% → a printable certificate — the name is typed for
   printing only and never saved), and the album of the people met.
6. ⏳ Full check against the booklet, desktop + phone, publish, send the link.

## Where it stopped (15 Nov 2026, «وقف»)

Stage 6 was started:
- done: `npm test` (113 pass) and the site checks pass; the game was played
  in the browser on desktop and phone for every place (5 places) and for the
  daily challenge, the exam, the certificate (print) and the album — no
  console errors, no sideways scrolling;
- not finished: the page-wide browser checks (`tests/e2e_test.py` sections
  sources_page, dhikr, navigation, language_switch, arabic_interface,
  no_review_labels, visitor_register, quizzes) were stopped after 40 checks
  passed and none failed — run them again to the end;
- then check the live page after the GitHub Pages deploy and send the owner
  the direct link: https://abdo098765432110-ux.github.io/grade12-english-/bio-game.html

## Next step

Finish stage 6 (above). Do not add the game to the site menus until the
owner approves.
