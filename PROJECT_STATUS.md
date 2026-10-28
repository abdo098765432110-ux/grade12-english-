# Project status — Learn English for Grade 12

_Last updated: 26 October 2026 (Phase 2 + the Arabic/English language switch, all website files at the top level)_

Target website (given by the owner): https://abdo098765432110-ux.github.io/grade12-english-/
Repository behind that address: https://github.com/abdo098765432110-ux/grade12-english-
(the repository name ends with a hyphen)

## Summary

| Work | Status |
|---|---|
| Phase 1 — student pages, quiz engine, content manager, empty content library | Done (19 Oct 2026) |
| Phase 1.5 — audit of the live site, fallback/loading/error states, navigation | Done (20 Oct 2026) |
| Phase 2 — data-driven content by unit and topic, answer checking, validation | Done in the project files (20 Oct 2026) |
| Arabic/English language switch | Done in the project files (26 Oct 2026) — now switches instantly, without reloading |

As the owner asked, the only addition to Phase 2 is the language switch. The
other Phase 3 work prepared earlier (home banner, new import/restore and
publishing workflow in the content manager) is **not** included.

The content library is still **empty**. No lessons, summaries, questions,
answers, explanations or reading passages have been written for the site.
All educational content will be supplied by the project owner.

## Why the language button did not work on the live site

Checked on 26 Oct 2026, repository `grade12-english-`, commit `df47d46`
(26 Oct, 15:06):
- The upload put every file at the **top level** of the repository. The
  pages looked for `js/i18n-ar.js`, `js/i18n.js`, `css/style.css` and
  `js/common.js` inside folders.
- The `js` and `css` folders still held the old Phase 1 files, and the two
  language files were not in `js` at all. So the pages showed the red
  “could not be loaded” message, and the button could not translate.
- `js/i18n-en.js` was not referenced by any file in the repository.

## The fix (26 Oct 2026)

**1. All website files at the top level** (the owner's choice)
- The pages now load `style.css`, `i18n-en.js`, `i18n-ar.js`, `i18n.js`,
  `common.js` and the other scripts, and the five data files, from the top
  level, next to `index.html`. There are no `css`, `js` or `data` folders.
- Selecting all the files and dragging them onto GitHub (what the owner
  did) now puts every file in the right place.
- The old `css`, `js` and `data` folders in the repository are no longer
  used and can be deleted later. They do no harm.
- The content manager's publishing steps, the “missing file” message and
  the site checker (`tools/check-site.js`) now describe the top-level
  layout.

**2. Language switch works immediately, without reloading**
- One click changes the whole interface:
  - the fixed text in the pages;
  - each page's content (lists, empty states, quizzes, results, errors);
  - the content manager with its forms and messages;
  - the browser tab title.
- `lang`/`dir` change at the same time: `en`/`ltr` and `ar`/`rtl`.
- English is the default. The choice is saved in the browser
  (`localStorage`, key `g12-lang`) and used again after reloading and on
  every page.
- If a student has already answered questions on the page, or a manager
  form has unsaved changes, the button asks first, because switching draws
  the page again. Answering “Cancel” keeps everything as it was.
- Educational content is never translated or changed.

**3. Translation files included in the project**
- `i18n-en.js` (English) and `i18n-ar.js` (Arabic): 610 interface texts
  each, plus the counted words (Arabic has six forms: 0, 1, 2, 3–10, 11–99,
  100+).
- `i18n.js` does the switching. The owner does not have to create or
  upload anything else.

## Test results (26 Oct 2026)

Linux, Node.js 22, Playwright with headless Chromium. The site was served
from a repository-style subfolder, as on GitHub Pages.

| Test | Result |
|---|---|
| `node --test tests/*.test.js` | **74 / 74 passed** |
| `python tests/e2e_test.py` (project) | **222 / 222 checks passed** on two runs |
| `node tools/check-site.js` | OK (all files at the top level) |
| `node tools/validate-content.js` | OK (empty library) |
| Upload simulated on a copy of `grade12-english-` (commit `df47d46`), every file dropped at the top level, served at `/grade12-english-/` | 221 / 222 checks passed. The one failure is a developer check that runs the repository's **old** `tools/validate-content.js` from Phase 1; it is not part of the website. |

New checks for the language switch:
- English → Arabic and back on the same page **without a reload** (a marker
  set in the page survives the switch);
- the page content changes too, not only the button;
- keyboard focus stays on the button;
- `rtl`/`ltr`, the choice kept after reloading and on every page;
- the “unsaved work” questions on the practice, reading and manager pages:
  “Cancel” keeps everything, and after confirming the page redraws in the
  other language;
- the practice settings keep the chosen topic;
- placeholder lessons, answer choices and passages stay exactly as written
  when switching back and forth;
- the “missing files” message names the top-level files, in both languages.

All Phase 2 checks (lessons, summaries, practice, reading, content manager,
navigation, error and loading states) still pass.

**Not tested:** the live site (nothing was uploaded from here), Firefox,
Safari, real phones, and screen readers. The Arabic interface text has not
been reviewed by a native speaker; it can be edited in `i18n-ar.js`.

## How to upload this version

1. On a **computer**, unzip `grade12-english-language-switch.zip` and open
   the `grade12-english` folder inside it.
2. Open https://github.com/abdo098765432110-ux/grade12-english- (with the
   hyphen at the end) and choose **Add file → Upload files**.
3. Select all the files (Ctrl+A, or Cmd+A on a Mac) and drag them onto the
   upload area. All the files go to the top level, next to `index.html`,
   which is exactly where the website looks for them.
4. Choose **Commit changes**. Files with the same names are replaced;
   nothing is deleted.
5. Wait 1–2 minutes. Open https://abdo098765432110-ux.github.io/grade12-english-/
   and reload with **Ctrl+F5** (Cmd+Shift+R on a Mac).
6. Click **العربية**: the page turns Arabic and right-to-left at once. Click
   **English** to switch back. Reload: the last choice is kept.
7. Optional: the old `css`, `js` and `data` folders are no longer used and
   can be deleted.

The five data files in the zip are empty, and so are the ones in the
repository today, so no content is lost. Later, once you have published
your own content, upload only the files that changed, not empty data files.

## Phase 2 report (20 Oct 2026) — implemented features

**1. Content by unit and topic**
- New file `data/units.json` (empty). Units group all content and appear in
  the order listed.
- A topic is a grammar lesson, and its `id` is the topic ID.
- Lessons, summaries, questions and passages can have `unitId`. Summaries and
  questions can have `topicId`, and then belong to that lesson’s unit
  automatically.
- **Grammar Lessons:** grouped by unit, with unit filter links. Pages work by
  address: `?unit=<id>` for one unit, `?topic=<id>` for one lesson (the old
  `?lesson=<id>` still works). The breadcrumb shows the unit, and the
  previous/next links follow unit order.
- **Grammar Summaries:** grouped by unit, with `?unit=<id>` and
  `?topic=<id>`. Lessons link to their own summary.
- **Grammar Practice:** choose a unit, then a topic (both with question
  counts), the number of questions, and how to answer. `?unit=` and `?topic=`
  preselect the choices.
- **Reading:** grouped by unit, with `?unit=<id>`.

**2. Grammar practice — answering and marking**
- Multiple-choice questions come only from `data/grammar-questions.json`.
- Two ways to answer:
  - *One at a time*: as before, with feedback, try again and show answer.
  - *All at once* (new): every question on one page, then “Check my answers”.
- Answers are checked against the answer key in the data. Only exact matches
  count.
- **Unanswered questions:**
  - Before checking, the page lists the blank question numbers and offers
    “Go to question N” or “Check anyway”.
  - Blank questions are marked “Not answered” and score 0. A blank answer is
    never counted as correct.
  - Any choice that is not one of the options counts as unanswered.
- **Score summary:** the score, the percentage, and separate counts for
  correct, not correct and not answered. Each question gets its own feedback
  and explanation. “Retry missed questions” includes the unanswered ones.
- The review-honesty rules from Phase 1 still apply: unreviewed answers are
  “suggested”, and scores that include them are “provisional”.

**3. Reading comprehension**
- Each passage is shown beside its questions. Questions appear **exactly in
  the stored order** in both modes and are never shuffled.
- “All questions” is the default mode, and “One at a time” is a button away.
- **Formatting is kept exactly:** paragraphs, line breaks, and spacing inside
  a paragraph. Paragraph numbers can be turned off per passage
  (`showParagraphNumbers: false`).
- On wide screens the passage stays in view while students scroll through
  the questions. A long passage scrolls inside its own box, which can also
  be scrolled with the keyboard.
- Line breaks are also kept in lesson text, summaries, question prompts,
  options and explanations.

**4. Safety and validation**
- Missing required fields, invalid IDs, and links to units or topics that
  don’t exist are all reported.
- **Answer keys get specific messages:**
  - a letter (`"B"`) or a number (`2`) instead of the option text, with the
    option it probably meant;
  - a difference only in spaces or capital letters;
  - a missing answer.
- Questions with an invalid key are never shown to students, and the quiz
  engine refuses to mark them as a second safeguard.
- A `unitId` that disagrees with its topic’s unit gets a warning, and the
  topic’s unit is used.
- Each page’s “N items could not be shown” notice now counts only the
  content that page shows.
- **Empty states:**
  - every unit with no content says so (“No lessons in this unit yet”);
  - a filtered empty unit or topic gets its own message;
  - Practice disables Start for an empty unit or topic;
  - unknown unit or topic addresses show “Unit not found” or “Topic not
    found”.
- **Older files keep working:** version 1 files are upgraded when loaded
  (`lessonId` → `topicId`, `topic` → `topicId`), with a validator reminder. If
  `data/units.json` is missing, the site behaves as if there are no units.

**5. Content manager**
- New **Units** tab: add, edit, reorder and delete units.
  - Renaming a unit’s ID updates everything linked to it.
  - Deleting a unit keeps its content and only removes the link.
- Every editor has a Unit field. Summaries and questions also have a Topic
  field, grouped by unit; choosing a topic selects its unit.
- Questions can be filtered by unit. The passage editor has a “Show
  paragraph numbers” option.
- Export, import and backup now include `units.json` (five data files).
  Imports of version 1 files are upgraded automatically.

### Data format

Version 2, documented in [docs/CONTENT_FORMAT.md](docs/CONTENT_FORMAT.md)
(units and topics, web addresses, answer-key rules, formatting, older files).

### Phase 2 test results (20 Oct 2026)

Environment: Linux, Node.js 22.22.0, Python 3.13, Playwright 1.56 with
headless Chromium 141. The site was served from a `/grade12-english/`
subfolder, the same path as on GitHub Pages. All test content is placeholder
text such as “Test prompt q1”, supplied by the tests and never written to
`data/`.

| Test | Result |
|---|---|
| `node --test tests/*.test.js` (unit tests) | **57 / 57 passed** (41 before + 16 new) |
| `python tests/e2e_test.py` (browser tests) | **161 / 161 checks passed**, on two runs in a row (115 before + 46 new) |
| `node tools/check-site.js` | OK: every referenced file exists with exact case; all paths are relative |
| `node tools/validate-content.js` | OK (empty library, version 2) |
| Project `data/` files after the tests | Still empty (verified) |

New tests in Phase 2:

- **Unit tests** cover:
  - unit validation;
  - `unitId`/`topicId` checks;
  - the version 1 → 2 upgrade (files, imports, drafts);
  - answer-key messages (letter, number, case, missing);
  - grouping and ordering by unit;
  - unit rename and delete cascades;
  - `gradeAll`: blank and invalid answers are never correct, nothing
    answered scores 0, unreviewed wording, written answers not scored;
  - blank-question numbers;
  - the quiz refusing a question without a valid key.
- **Browser tests (student pages)** cover:
  - unit links and grouping, including per-unit empty states;
  - `?unit=` / `?topic=` / `?lesson=` addresses, “Unit not found”, and the
    unit in the breadcrumb;
  - line breaks kept in lessons, and the old `lessonId` upgraded on the
    summaries page;
  - practice unit/topic counts, an empty unit disabling Start, a question
    with key `"B"` skipped with a notice, and `?topic=` preselecting the unit;
  - answer-all mode: blank questions listed, “Check anyway” scoring 0 with
    “Not answered” on each, retry missed, full score;
  - reading: spacing kept exactly, questions in stored order in both modes,
    sticky passage, matched/different/not answered counts, paragraph numbers
    off;
  - a missing `units.json`, and accessibility checks on the new screens.
- **Browser tests (content manager)** cover:
  - adding units, and a lesson in a unit;
  - choosing a topic selecting its unit, and a conflicting unit being
    refused;
  - what each question stores; the unit filter;
  - passage line breaks and the paragraph-number setting;
  - unit contents counts, unit ID rename and delete cascades;
  - the `units.json` download;
  - a version 1 import upgraded, and a letter answer key rejected with a
    hint.
- **Visual review** of screenshots found three layout issues, all fixed and
  re-tested: extra space above the question list, single cards stretching
  the full width, and extra space at the top of the practice panel.

### Phase 2 known limitations (still apply)

- Text formatting covers paragraphs, line breaks and spacing. Bold or
  italic text inside content is not supported.
- Only multiple-choice questions are scored; written answers are compared by
  the student.
- Drafts are per browser; publishing is a manual upload; there is no saved
  student progress; the wording has not been checked against the official
  syllabus.

## Next steps

1. Upload this version (see “How to upload this version” above) and check
   the live site with Ctrl+F5.
2. Add units first, then lessons (topics), summaries, questions and
   passages, with the content manager or JSON files that follow
   docs/CONTENT_FORMAT.md.
