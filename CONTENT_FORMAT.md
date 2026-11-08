# Content format (version 2)

All educational content lives in five JSON files in the `data/` folder. The
website starts with all of them empty. The easiest way to fill them is the
**content manager** (`manage.html`), which writes these files for you. This
page is for preparing or checking the files by hand.

After editing by hand, check the files:

```
node tools/validate-content.js
```

| File | List inside it | Used by |
|---|---|---|
| `data/units.json` | `units` | All pages (grouping and filtering) |
| `data/grammar-lessons.json` | `lessons` | The grammar topics (titles used by summaries, practice and the content manager) |
| `data/grammar-summaries.json` | `summaries` | Grammar Summaries |
| `data/grammar-questions.json` | `questions` | Grammar Practice |
| `data/reading-passages.json` | `passages` | Reading Comprehension |

Every file has the same outer shape:

```json
{
  "schemaVersion": 2,
  "lessons": []
}
```

## How content is organised: units and topics

- A **unit** is a group of lessons, summaries, questions and passages
  (for example, one unit of the school book). Units are listed in
  `data/units.json` in the order they should appear.
- A **topic** is one grammar lesson. **The topic ID is the lesson’s `id`.**
- Any lesson, summary, question or passage can say which unit it belongs to
  with **`unitId`**.
- Summaries and practice questions can say which topic they belong to with
  **`topicId`**. They then belong to **that lesson’s unit automatically**, so
  they do not need a `unitId` as well. If both are given and they disagree,
  the topic’s unit is used and the validator shows a warning.
- Units and topics are optional. Content without a unit is shown under
  “Other”. If there are no units at all, each page shows one simple list.

Example: a unit, a topic (lesson) in it, and a question linked to the topic.

```json
{ "schemaVersion": 2, "units": [
  { "id": "unit-1", "title": "Unit 1 title", "description": "Optional short description" }
] }
```

```json
{ "schemaVersion": 2, "lessons": [
  { "id": "topic-id", "unitId": "unit-1", "title": "Lesson title", "reviewStatus": "unreviewed", "sections": [] }
] }
```

```json
{ "schemaVersion": 2, "questions": [
  { "id": "q-001", "type": "mcq", "topicId": "topic-id", "prompt": "…", "options": ["…", "…"], "answer": "…", "reviewStatus": "unreviewed" }
] }
```

## Web addresses by unit and topic

| Address | Shows |
|---|---|
| `summaries.html`, `summaries.html?unit=<unit id>` | All summaries / one unit’s summaries |
| `summaries.html?topic=<topic id>` | The summary of one topic |
| `practice.html?unit=<unit id>` | Practice with that unit chosen |
| `practice.html?topic=<topic id>` | Practice with that topic (and its unit) chosen |
| `reading.html`, `reading.html?unit=<unit id>` | All passages / one unit’s passages |
| `reading.html?passage=<passage id>` | One passage with its questions |
| `vocabulary.html?unit=<unit id>` | Vocabulary practice with that unit chosen |

## Rules for every item

- **`id`**: required, and unique within its list. Use lowercase English
  letters, numbers and single hyphens only (for example `unit-3` or
  `passive-voice`). IDs appear in web addresses, so avoid changing them after
  publishing. The content manager updates links automatically when you
  change an ID there.
- **`unitId`, `topicId`**: optional. When given, each must be a valid ID. A
  link to an ID that does not exist is a warning, not an error.
- **`reviewStatus`**: `"unreviewed"` or `"reviewed"` (units have none). Only
  `"reviewed"` items count as checked by a teacher. For anything else,
  students see “Not yet reviewed”, answers are called *suggested answers*
  (never “correct” or “incorrect”), and scores are marked *provisional*.
- **Text** is plain text. HTML is not interpreted; it is shown exactly as
  typed, so content can never break the page.
  - A line break inside a text value (`\n` in JSON, or Enter in the content
    manager) is shown as a line break.
  - In reading passages, spacing is also kept exactly as written.
  - Arabic and English can be mixed, and the text direction is detected
    automatically.

## Unit

| Field | Required | Notes |
|---|---|---|
| `id`, `title` | yes | |
| `description` | no | Shown under the unit title. |

## Lesson (topic)

| Field | Required | Notes |
|---|---|---|
| `id`, `title`, `reviewStatus` | yes | `id` is the topic ID. |
| `unitId` | no | The unit this lesson belongs to. |
| `description` | no | Shown in the lesson list. |
| `sections` | yes (may be empty) | Shown in order. Types below. |

Section types (each may also have an optional `heading`):

| `type` | Fields |
|---|---|
| `text` | `paragraphs`: list of text; optional `lang`: `"en"` or `"ar"` (Arabic shows right to left). With a `heading`, `paragraphs` may be empty: the heading alone is the title of a part. |
| `note` | same as `text`, shown in a highlighted box (for key rules) |
| `tip` | same as `note`, shown in a cream “exam tip” box |
| `list` | `items`: list of text (bullets) |
| `examples` | `items`: list of text (example boxes) |
| `table` | `columns`: list of headings; `rows`: list of rows, each a list with one cell per column |
| `mistakes` | `items`: list of `{ "avoid": "...", "use": "...", "note": "..." }` (`note` optional) |

## Summary

| Field | Required | Notes |
|---|---|---|
| `id`, `title`, `reviewStatus` | yes | |
| `topicId` | no | The topic (lesson) it summarises. Gives it that lesson’s unit. |
| `unitId` | no | Only needed when there is no `topicId`. |
| `points` | no | List of `{ "title": "...", "rule": "...", "example": "..." }`. Only `rule` is required. |
| `sections` | no | Sections written exactly like a lesson’s sections (types above), shown after the points table. A `text` section with a heading starts a new part; `tip` boxes that follow each other are shown side by side on wide screens; ✗ and ✓ are shown in red and green. |
| `remember` | no | List of short reminders. |

## Question (grammar practice)

| Field | Required | Notes |
|---|---|---|
| `id`, `prompt`, `reviewStatus` | yes | Write `___` (three underscores) in `prompt` to show a blank. |
| `type` | yes | `"mcq"` (multiple choice, scored) or `"short"` (written answer, never scored). |
| `topicId` | no | The topic (lesson). Gives the question that lesson’s unit. |
| `unitId` | no | Only needed when there is no `topicId`. |
| `options` | for `mcq` | 2 to 6 different, non-empty options, in the order they should appear. |
| `answer` | for `mcq` | **The full text of the correct option, exactly as written in `options`.** |
| `modelAnswer` | for `short` | Students compare their own answer with it. |
| `explanation` | no | Shown after answering. |
| `difficulty` | no | `"easy"`, `"medium"`, `"hard"` or `"very-hard"` (shown as "very hard"; used by the Biology bank). |
| `lang` | no | `"ar"` for a question written in Arabic: right to left, with the choices numbered أ) ب) ج) د). |
| `image`, `imageAlt` | no | A diagram shown under the question (a picture file next to `index.html`), and a text description of it for screen readers. |

### Vocabulary questions (`vocabulary-questions.json`)

The Vocabulary page (`vocabulary.html`) reads its own file, so vocabulary
questions are never mixed with the grammar practice questions. The questions
are grouped by English unit and use the same fields as the grammar questions
above. Students choose a unit, a level and how many questions, then answer
one at a time or all at once. Write each explanation as one line per choice:
`✓ …` for the answer, then `✗ …` for each wrong choice (line breaks are kept).

```json
{ "schemaVersion": 2, "units": [
  { "id": "unit-1", "title": "Unit 1: Inside the World of Care", "questions": [ … ] } ] }
```

These questions are edited in the file itself (not in the content manager).

### Subject questions (`physics-questions.json`)

The physics page reads `physics-questions.json`: chapters, each with
sections of questions. Students go step by step: the physics page shows the
chapters; a chapter shows its sections; a section shows its questions, one at
a time with instant feedback. Beside the question, a panel lists the question
numbers (1, 2, 3 …): a click opens that question straight away, and each
number shows whether it is the current question, answered, or not answered
yet. The panel is on the left on wide screens; on phones it sits above the
question and its numbers open with a button.

```json
{ "schemaVersion": 2, "chapters": [
  { "id": "chapter-1", "title": "الفصل الأول", "sections": [
    { "id": "chapter-1-questions", "title": "أسئلة على الفصل الأول", "questions": [ … ] } ] } ] }
```

A section can name a PDF of its questions (`"pdf": "physics-ch1-questions.pdf"`):
it gets a «تنزيل ملف الأسئلة» button. A chapter can have a revision sheet:
`"revision": { "id", "title", "page": "physics-ch1-laws.html", "pdf": "physics-ch1-laws.pdf" }`,
shown as a second card on the chapter page with «افتح المراجعة», «تحميل مراجعة القوانين»
and «طباعة المراجعة». After changing the questions or the revision sheet, make the
PDFs again with `python tools/physics_pdfs.py`.

A PDF of all the questions with their answers can be named at the top of the
file (`"pdf": "chemistry-questions.pdf"`, shown on the subject page) or on a
chapter (`"pdf": "biology-ch1-questions.pdf"`, shown on the chapter page), with
«عرض ملف PDF» and «تحميل ملف PDF». These PDFs (and `english-questions.pdf`,
linked from the English home page) are made by `python3 tools/question_pdfs.py`;
run it again after changing the English, Chemistry or Biology questions (the tests
fail until you do).

Addresses: `physics.html` (chapters), `physics.html?chapter=chapter-1`
(its sections), `physics.html?chapter=chapter-1&section=chapter-1-questions`
(the questions). The questions use the same fields as the grammar questions above.

### Answer key rules

The answer key is checked strictly, so a mistake can never mark a wrong
answer as right:

- `"answer"` must be **exactly** one of the options, with the same spelling,
  spaces and capital letters. `"B"`, `"2"` or `2` are **not** accepted. The
  validator explains the mistake and shows the option you probably meant.
- A question whose answer key is missing or does not match is **not shown to
  students**. A notice says that an item could not be shown, and the
  content manager’s *Check content* lists the reason.
- When students answer all questions at once, any question left blank is
  marked **“Not answered”** and scores **0**. A blank answer is never
  counted as correct.
- Only the student’s first attempt counts towards the score.

## Reading passage

| Field | Required | Notes |
|---|---|---|
| `id`, `title`, `reviewStatus` | yes | |
| `unitId` | no | The unit this passage belongs to. |
| `paragraphs` | yes | At least one. Each paragraph’s line breaks and spacing are kept exactly. |
| `showParagraphNumbers` | no | `true` (default) shows numbers beside paragraphs; `false` hides them. |
| `level` | no | For example “Grade 12”. |
| `source` | no | Credit for the text. Only publish texts you wrote or may use. |
| `questions` | yes (may be empty) | Same format as grammar questions (without `unitId`/`topicId`). **Always shown in this order.** Question IDs must be unique within the passage. |

## Older files (version 1)

Files saved before units existed (`"schemaVersion": 1`) still work. When they
are loaded:

- the summary field `lessonId` is read as `topicId`;
- the question field `topic` is read as `topicId`.

The validator shows a reminder. Exporting from the content manager saves the
files in version 2. If `data/units.json` is missing, the site works as if
there are no units.

## Errors and warnings

- **Errors** make an item unusable. On the student pages, an item with
  errors is skipped, and a short notice says how many were skipped; the rest
  of the page still works. The content manager never saves an item with
  errors and refuses imports that contain errors.
- **Warnings** do not stop anything. Examples: a lesson with no sections yet,
  a link to a unit or topic that does not exist, or a `unitId` that disagrees
  with its topic.
