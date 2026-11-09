# Learn for Grade 12

A free learning website for Egyptian Grade 12 students. The subject menu
(المواد الدراسية) at the top of every page leads to the five subjects:
اللغة العربية، اللغة الإنجليزية، الفيزياء، الكيمياء، الأحياء.

- **English** (the home page and the pages below): grammar lessons, grammar
  summaries, grammar practice with feedback and scoring, and reading
  comprehension.
- **Physics**: الفصل الأول → أسئلة على الفصل الأول: interactive questions,
  with the correct answer and an explanation after each answer.
- **Chemistry**: Chapter 1 questions (chemistry-questions.json).
- **Biology**: Chapters 1 and 2 question banks — each chapter has 10 easy,
  40 medium and 50 very hard questions (biology-questions.json).
- **Arabic**: Unit 3 «النواسخ»: two PDFs to view or download — 100 medium and hard
  questions with an answer key (`arabic-unit3-questions.pdf`) and a two-page summary
  (`arabic-unit3-summary.pdf`), made by `python3 tools/arabic_unit3/build.py` from
  `tools/arabic_unit3/questions.json` and `tools/arabic_unit3/summary.html` (fonts in
  `tools/fonts`, SIL Open Font License).

- Plain HTML, CSS, JavaScript and JSON. No build step, frameworks, packages,
  database, accounts, paid services or AI APIs.
- Works on GitHub Pages, including inside a repository subfolder
  (`https://<user>.github.io/<repository>/`). All paths are relative.
- **Starts with an empty content library.** All lessons, summaries, questions
  and passages are added by the teacher with the built-in content manager.

## Files

All website files are at the **top level**, next to `index.html` (there are
no `css`, `js` or `data` folders).

```
grade12-english/
├── index.html             Home
├── summaries.html         Grammar Summaries (?unit=<id>, ?topic=<id>)
├── practice.html          Grammar Practice  (?unit=<id>, ?topic=<id> preselect)
├── reading.html           Reading Comprehension (?unit=<id>, ?passage=<id>)
├── vocabulary.html        Vocabulary (?unit=<id> preselect); questions in vocabulary-questions.json, page script vocabulary.js
├── present-perfect-summary.pdf   The Present Perfect & Present Perfect Continuous summary (English + Arabic, four A4 pages; the owner's file, used as it is)
├── manage.html            Content manager (for teachers)
├── arabic.html, physics.html, chemistry.html, biology.html   The other four subjects
├── arabic-unit3-questions.pdf, arabic-unit3-summary.pdf   Arabic Unit 3: 100 questions with answer key, and the summary
├── subject.js             Subject pages: chapters → sections → questions, with the shared quiz
├── physics-questions.json Physics questions (الفصل الأول → حل أسئلة الفصل الأول, and the chapter's revision sheet)
├── chemistry-questions.json Chemistry questions (الفصل الأول)
├── biology-questions.json Biology questions (الفصل الأول والثاني: سهلة / متوسطة / صعبة جدًا)
├── physics-ch1-laws.html  Revision sheet «مراجعة أهم قوانين الفصل الأول» (A4, printable; styles in sheet.css, print button in sheet.js)
├── physics-ch1-laws.pdf, physics-ch1-questions.pdf   Downloadable PDFs: the revision sheet, and all chapter 1 questions (made by tools/physics_pdfs.py)
├── english-questions.pdf, chemistry-questions.pdf, biology-ch1-questions.pdf, biology-ch2-questions.pdf   All the questions, with an answer key on the last page (made by tools/question_pdfs.py; question-pdfs.json records what each was made from)
├── physics-ch1-p02.svg … physics-ch1-p118.svg   Diagrams for the physics questions taken from the review PDF (questions 1–118; only those that have a figure or table)
├── physics-ch1-q6.svg … physics-ch1-q11.svg   Diagrams for the earlier physics questions (no picture for q8)
├── .nojekyll              Empty file: tells GitHub Pages to serve files as they are
├── style.css              All styles
├── logo.svg               Logo (header, footer and browser tab)
├── home-hero.svg          Home page illustration
├── icon-summaries.svg, icon-practice.svg, icon-reading.svg, icon-vocabulary.svg   Home page section pictures
├── subject-arabic.svg, subject-english.svg, subject-physics.svg, subject-chemistry.svg, subject-biology.svg   Subject menu pictures
├── i18n.js                Interface language: the English/Arabic button, page direction, saved choice
├── i18n-en.js             English interface text
├── i18n-ar.js             Arabic interface text
├── content-schema.js      Data format, validation rules, units and topics
├── content-store.js       Add/edit/delete/move/import logic, browser drafts
├── common.js              Shared helpers: data loading, unit links, empty and error states, menu
├── quiz-engine.js         Quiz rules: answer keys, scoring, unanswered questions
├── quiz-ui.js             Quiz screens: one at a time, or all questions then check
├── dhikr.js, dhikr-amiri.woff   On every page: a random dhikr or dua in a small card for about 3.5 seconds (the font is Amiri, cut to the letters used; made by tools/dhikr_font.py)
├── home.js, grammar.js, summaries.js, practice.js, reading.js, manage.js   One script per page
├── units.json             The content (empty to start)
├── grammar-lessons.json
├── grammar-summaries.json
├── grammar-questions.json
├── reading-passages.json
├── docs/                  Data format reference and the first-upload diagnosis
├── tools/                 check-site.js, validate-content.js, physics_pdfs.py, question_pdfs.py, dhikr_font.py, arabic_unit3/, fonts/ (for developers)
├── tests/                 Automated tests (for developers, not used by the site)
├── README.md
└── PROJECT_STATUS.md
```

The website needs only the files at the top level. The `docs`, `tools` and
`tests` folders are for reference and development; they are not needed on
GitHub.

## Publish on GitHub Pages

1. Unzip the project on a computer and open the `grade12-english` folder, so
   you can see `index.html`, `style.css`, `i18n.js` and the other files.
2. On GitHub, open your repository and choose **Add file → Upload files**.
3. Select all the files in the folder (Ctrl+A on Windows, Cmd+A on Mac) and
   drag them onto the upload area (or use “choose your files” and select
   them all). Every file belongs at the top level of the repository, next to
   `index.html`.
4. Choose **Commit changes**. Files with the same name are replaced.
5. The first time only: open **Settings → Pages**, choose **Deploy from a
   branch**, then branch `main` and folder `/ (root)`, and save.
6. Wait 1–2 minutes and open `https://<user>.github.io/<repository>/`. If you
   still see the old page, force a reload: **Ctrl+F5** (Windows) or
   **Cmd+Shift+R** (Mac).

If a file is missing, every page shows a red message naming it.

## Interface language (English / العربية)

- Every page has a language button in the header: **العربية** on English
  pages, **English** on Arabic pages. A click switches the whole interface
  **immediately, without reloading the page**: menus, buttons, headings,
  labels, messages and forms, including the content manager. The page
  direction changes too: left-to-right for English, right-to-left for
  Arabic. English is the default.
- **Educational content is never translated.** Lessons, summaries,
  questions, answer choices, answers, explanations and passages always
  appear exactly as written, and each keeps its own text direction.
- The choice is saved in the browser (`localStorage`, key `g12-lang`), so it
  stays after reloading and on every page. If the browser blocks storage,
  the button still works until the page is closed.
- If a student has already answered questions on the page, or the content
  manager has a form with unsaved changes, the button asks first, because
  switching draws the page again.
- The interface text is in two files: `i18n-en.js` (English) and
  `i18n-ar.js` (Arabic). The text on the left is the key used in the code;
  the text on the right is what visitors see. To change wording, edit the
  right-hand side and keep any `{placeholders}`.

## Run it on your computer

Browsers block data files when a page is opened directly from disk
(`file://`), so use any local web server, for example with Python:

```
cd grade12-english
python -m http.server 8000
```

Then open <http://localhost:8000/>.

## Adding and managing content

Open `manage.html` (also linked at the bottom of every page).

1. **Add and edit** units, lessons (topics), summaries, grammar questions and
   reading passages (with their questions). Link each item to its unit, and
   summaries and questions to their topic. You can also delete items, reorder
   them, filter questions by unit and topic, and search question text.
2. Your work is **saved automatically as a draft in this browser** (on this
   device only). Nothing is sent anywhere.
3. Tick **“Preview my draft on the student pages”** to see the draft on the
   real pages in your browser. Students do not see it.
4. **Publish:** open *Import & export* and choose *Download all five files*.
   Then, in your GitHub repository (at the top level, next to `index.html`),
   choose **Add file → Upload files**, upload the five files (they replace
   the old ones) and commit.
5. **Back up** regularly with *Download backup file*. A backup (or any data
   file) can be **imported** on any computer. *Merge* adds new items and
   updates items with the same ID; *Replace* swaps the imported type
   completely. Files are checked before anything changes.

Notes:

- Anyone can open `manage.html` on the public site, but it only changes a
  draft in **their own** browser. Only people who can push to the GitHub
  repository can change the published website.
- The **“A teacher has reviewed this …”** tick decides how answers are shown.
  Until it is ticked, students see answers as *suggested answers*, never as
  definitely correct, and scores are marked *provisional*.
- Drafts live in the browser’s storage (usually about 5 MB). Clearing the
  browser’s site data deletes the draft, so download backups.

The data format is described in [docs/CONTENT_FORMAT.md](docs/CONTENT_FORMAT.md).

## Checks (need Node.js; no packages to install)

```
node tools/check-site.js        # before uploading: folders, files, letter case, relative paths
node tools/validate-content.js  # after editing the .json data files by hand
```

## Tests (for developers)

```
node --test tests/*.test.js     # unit tests (Node.js 18+), including a check that every interface text has Arabic
python tests/e2e_test.py        # browser tests; needs: pip install playwright && python -m playwright install chromium
```

The browser tests serve the site from a subfolder (like GitHub Pages), type
placeholder test text into the content manager, and never change the
project's data files. Run the checks and tests from the unzipped project
folder on a computer (they need the `tools` and `tests` folders).
