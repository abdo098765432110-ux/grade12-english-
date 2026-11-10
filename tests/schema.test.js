/* Unit tests for content-schema.js — run with: node --test tests/*.test.js
   Fixtures use placeholder text only; they are not educational content. */
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const Schema = require('../content-schema.js');

function lesson(overrides) {
  return Object.assign({
    id: 'test-lesson',
    title: 'Test lesson',
    reviewStatus: 'unreviewed',
    sections: [{ type: 'text', paragraphs: ['Placeholder paragraph.'] }]
  }, overrides);
}

function mcq(overrides) {
  return Object.assign({
    id: 'q-001',
    type: 'mcq',
    prompt: 'Test prompt ___ 1',
    options: ['Option A', 'Option B', 'Option C'],
    answer: 'Option B',
    reviewStatus: 'unreviewed'
  }, overrides);
}

function errorsOf(key, item) {
  return Schema.validateItem(key, item, 0).errors;
}

test('an empty library is valid', () => {
  const report = Schema.validateLibrary(Schema.emptyLibrary());
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.warnings, []);
});

test('a complete lesson with every section type is valid', () => {
  const item = lesson({
    sections: [
      { type: 'text', heading: 'H', paragraphs: ['P1', 'P2'] },
      { type: 'note', paragraphs: ['ملاحظة'], lang: 'ar' },
      { type: 'tip', heading: 'Tip', paragraphs: ['T1'] },
      { type: 'text', heading: 'Part title only', paragraphs: [] },
      { type: 'list', items: ['a', 'b'] },
      { type: 'examples', items: ['e1'] },
      { type: 'table', columns: ['C1', 'C2'], rows: [['1', '2'], ['3', '']] },
      { type: 'mistakes', items: [{ avoid: 'x', use: 'y' }, { avoid: 'x2', use: 'y2', note: 'n' }] }
    ]
  });
  assert.deepEqual(errorsOf('lessons', item), []);
});

test('lesson errors: missing title, bad id, unknown section type, bad table row', () => {
  assert.match(errorsOf('lessons', lesson({ title: ' ' })).join(), /title is required/);
  assert.match(errorsOf('lessons', lesson({ id: 'Bad ID' })).join(), /may only contain lowercase/);
  assert.match(errorsOf('lessons', lesson({ sections: [{ type: 'video' }] })).join(), /type must be one of/);
  const table = lesson({ sections: [{ type: 'table', columns: ['A', 'B'], rows: [['only one']] }] });
  assert.match(errorsOf('lessons', table).join(), /row 1 has 1 cell, but the table has 2 columns/);
  assert.match(errorsOf('lessons', lesson({ reviewStatus: 'maybe' })).join(), /reviewStatus/);
});

test('a lesson without sections is a warning, not an error', () => {
  const report = Schema.validateItem('lessons', lesson({ sections: [] }), 0);
  assert.equal(report.errors.length, 0);
  assert.match(report.warnings.join(), /no sections yet/);
});

test('missing reviewStatus is a warning and is treated as unreviewed', () => {
  const item = lesson();
  delete item.reviewStatus;
  const report = Schema.validateItem('lessons', item, 0);
  assert.equal(report.errors.length, 0);
  assert.match(report.warnings.join(), /treated as "unreviewed"/);
});

test('multiple-choice rules: answer must match an option exactly', () => {
  assert.deepEqual(errorsOf('questions', mcq()), []);
  assert.match(errorsOf('questions', mcq({ answer: 'option b' })).join(), /only in spaces or capital letters/);
  assert.match(errorsOf('questions', mcq({ answer: 'Something else' })).join(), /does not exactly match any option/);
  assert.match(errorsOf('questions', mcq({ answer: '' })).join(), /answer is missing/);
  assert.match(errorsOf('questions', mcq({ options: ['Only one'], answer: 'Only one' })).join(), /between 2 and 6 options/);
  assert.match(errorsOf('questions', mcq({ options: ['A', 'A', 'B'], answer: 'B' })).join(), /appears more than once/);
  assert.match(errorsOf('questions', mcq({ options: ['A', '', 'B'], answer: 'B' })).join(), /every option must contain text/);
  assert.match(errorsOf('questions', mcq({ type: undefined })).join(), /type must be "mcq"/);
  assert.match(errorsOf('questions', mcq({ difficulty: 'impossible' })).join(), /difficulty/);
});

test('short-answer questions need a model answer', () => {
  const short = { id: 'q-002', type: 'short', prompt: 'Test prompt 2', reviewStatus: 'unreviewed' };
  assert.match(errorsOf('questions', short).join(), /modelAnswer is required/);
  assert.deepEqual(errorsOf('questions', Object.assign({ modelAnswer: 'Placeholder answer' }, short)), []);
});

test('passages: need paragraphs; questions are validated; duplicate question ids are errors', () => {
  const passage = { id: 'p1', title: 'Test passage', reviewStatus: 'unreviewed', paragraphs: ['Text.'], questions: [mcq()] };
  assert.deepEqual(errorsOf('passages', passage), []);
  assert.match(errorsOf('passages', Object.assign({}, passage, { paragraphs: [] })).join(), /paragraphs needs at least 1/);
  assert.match(errorsOf('passages', Object.assign({}, passage, { questions: [mcq(), mcq()] })).join(), /already used/);
  const noQuestions = Schema.validateItem('passages', Object.assign({}, passage, { questions: [] }), 0);
  assert.equal(noQuestions.errors.length, 0);
  assert.match(noQuestions.warnings.join(), /no questions yet/);
});

test('summaries: rule is required for each point; empty summary is a warning', () => {
  const summary = { id: 's1', title: 'Test summary', reviewStatus: 'unreviewed', points: [{ title: 'T', rule: 'R' }] };
  assert.deepEqual(errorsOf('summaries', summary), []);
  assert.match(errorsOf('summaries', Object.assign({}, summary, { points: [{ title: 'T' }] })).join(), /rule is required/);
  const empty = Schema.validateItem('summaries', { id: 's2', title: 'Empty', reviewStatus: 'unreviewed' }, 0);
  assert.equal(empty.errors.length, 0);
  assert.match(empty.warnings.join(), /will look empty/);
});

test('summaries: an optional PDF file name; a summary with only a PDF is not "empty"', () => {
  const ok = Schema.validateItem('summaries', { id: 's1', title: 'T', reviewStatus: 'reviewed', pdf: 'present-perfect-summary.pdf' }, 0);
  assert.deepEqual(ok.errors, []);
  assert.deepEqual(ok.warnings, []);
  ['', 'summary.docx', '/summary.pdf', 'https://example.com/a.pdf', 'files/summary.pdf', 42].forEach((pdf) => {
    const bad = Schema.validateItem('summaries', { id: 's1', title: 'T', reviewStatus: 'reviewed', pdf: pdf }, 0);
    assert.equal(bad.errors.length, 1, JSON.stringify(pdf));
  });
});

test('Grammar Summaries: Present Perfect / Present Perfect Continuous is the uploaded four-page bilingual PDF', () => {
  const fs = require('fs');
  const path = require('path');
  const summaries = require('../grammar-summaries.json').summaries;
  const pp = summaries.find((s) => s.id === 'present-perfect-vs-present-perfect-continuous');
  assert.ok(pp, 'summary kept');
  assert.equal(pp.title, 'Present Perfect vs Present Perfect Continuous');
  assert.equal(pp.pdf, 'present-perfect-summary.pdf');
  assert.equal(pp.sections, undefined, 'old content removed');
  assert.equal(pp.remember, undefined, 'old content removed');
  assert.deepEqual(Schema.validateItem('summaries', pp, 0).errors, []);
  const pdf = fs.readFileSync(path.join(__dirname, '..', pp.pdf));
  assert.equal(pdf.subarray(0, 5).toString(), '%PDF-');
  assert.equal((pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length, 4, 'four pages');
  // exactly the owner's uploaded file (English + Arabic), unchanged
  const sha = require('crypto').createHash('sha256').update(pdf).digest('hex');
  assert.equal(sha, '17c877a138b2f64834be09fb485996fccd728aff7c1ec70f63d3d15f9494ee5d', 'the uploaded file, byte for byte');
  // the old summary's source page and its PDF builder are gone, so the old version cannot come back
  assert.ok(!fs.existsSync(path.join(__dirname, '..', 'tools', 'present-perfect-summary.html')), 'old source removed');
  assert.ok(!fs.existsSync(path.join(__dirname, '..', 'tools', 'grammar_pdfs.py')), 'old builder removed');
});

test('summaries: optional sections are checked like lesson sections', () => {
  const summary = { id: 's1', title: 'Test summary', reviewStatus: 'unreviewed', sections: [
    { type: 'text', heading: 'Part 1', paragraphs: [] },
    { type: 'tip', heading: 'Tip', paragraphs: ['T1'] },
    { type: 'table', columns: ['A', 'B'], rows: [['1', '2']] }
  ] };
  const report = Schema.validateItem('summaries', summary, 0);
  assert.deepEqual(report.errors, []);
  assert.equal(report.warnings.length, 0, 'sections alone are enough, so no "will look empty" warning');
  assert.match(errorsOf('summaries', Object.assign({}, summary, { sections: 'x' })).join(), /sections must be a list/);
  assert.match(errorsOf('summaries', Object.assign({}, summary, { sections: [{ type: 'table', columns: ['A', 'B'], rows: [['1']] }] })).join(), /section 1.*row 1 has 1 cell/);
  // a heading alone is allowed for text only; a note or tip box still needs text
  assert.match(errorsOf('summaries', Object.assign({}, summary, { sections: [{ type: 'tip', heading: 'T', paragraphs: [] }] })).join(), /paragraphs needs at least 1/);
  assert.match(errorsOf('lessons', lesson({ sections: [{ type: 'text', paragraphs: [] }] })).join(), /paragraphs needs at least 1/);
});

test('duplicate ids in a collection are errors', () => {
  const report = Schema.validateCollection('lessons', [lesson(), lesson()]);
  assert.match(report.errors.join(), /already used by Lesson 1/);
});

test('links to missing topics and units are warnings', () => {
  const library = Schema.emptyLibrary();
  library.questions = [mcq({ topicId: 'missing-lesson' })];
  library.summaries = [{ id: 's1', title: 'S', topicId: 'missing-lesson', reviewStatus: 'unreviewed', remember: ['r'] }];
  library.passages = [{ id: 'p1', title: 'P', unitId: 'missing-unit', reviewStatus: 'unreviewed', paragraphs: ['x'], questions: [mcq()] }];
  library.lessons = [lesson({ unitId: 'missing-unit' })];
  const report = Schema.validateLibrary(library);
  assert.equal(report.errors.length, 0);
  assert.equal(report.warnings.length, 4);
  assert.match(report.warnings.join(), /no lesson has that id/);
  assert.match(report.warnings.join(), /no unit has that id/);
});

test('a unitId that disagrees with the topic’s unit is a warning, and the topic’s unit wins', () => {
  const library = Schema.emptyLibrary();
  library.units = [{ id: 'u1', title: 'U1' }, { id: 'u2', title: 'U2' }];
  library.lessons = [lesson({ id: 'l1', unitId: 'u1' })];
  library.questions = [mcq({ topicId: 'l1', unitId: 'u2' })];
  const report = Schema.validateLibrary(library);
  assert.match(report.warnings.join(), /its topic “l1” is in the unit “u1”/);
  assert.equal(Schema.unitIdOf(library.questions[0], library.lessons), 'u1');
});

test('file shape and schema version are checked', () => {
  assert.equal(Schema.validateFile('lessons', { schemaVersion: 1, lessons: [] }).errors.length, 0);
  assert.match(Schema.validateFile('lessons', [] ).errors.join(), /must contain a JSON object/);
  assert.match(Schema.validateFile('lessons', { schemaVersion: 1 }).errors.join(), /must contain a "lessons" list/);
  assert.match(Schema.validateFile('lessons', { schemaVersion: 99, lessons: [] }).errors.join(), /not supported/);
  assert.match(Schema.validateFile('lessons', { lessons: [] }).warnings.join(), /schemaVersion is missing/);
});

test('readImport accepts single files and backups, rejects other shapes', () => {
  const single = Schema.readImport({ schemaVersion: 1, questions: [mcq()] }, 'q.json');
  assert.deepEqual(Object.keys(single.collections), ['questions']);
  const backup = Schema.readImport({ schemaVersion: 1, type: 'grade12-english-backup', lessons: [], summaries: [], questions: [], passages: [] });
  assert.equal(Object.keys(backup.collections).length, 4);
  assert.match(Schema.readImport([1, 2]).report.errors.join(), /not a content file/);
  assert.match(Schema.readImport({ something: [] }).report.errors.join(), /does not contain units, lessons/);
  assert.match(Schema.readImport({ lessons: {} }).report.errors.join(), /must be a list/);
});

test('usableItems skips broken items but keeps a passage whose question is broken', () => {
  const lessons = Schema.usableItems('lessons', [lesson(), lesson({ id: 'x', title: '' }), lesson()]);
  assert.equal(lessons.items.length, 1);
  assert.equal(lessons.skipped, 2); // one broken, one duplicate id

  const passages = Schema.usableItems('passages', [{
    id: 'p1', title: 'T', reviewStatus: 'unreviewed', paragraphs: ['x'],
    questions: [mcq(), mcq({ id: 'q-002', answer: 'nope' })]
  }]);
  assert.equal(passages.items.length, 1);
  assert.equal(passages.items[0].questions.length, 1);
  assert.equal(passages.skippedQuestions, 1);
});

test('id and text helpers', () => {
  assert.equal(Schema.slugify('  Hello, World! Ünïcode  '), 'hello-world-unicode');
  assert.equal(Schema.slugify('نص عربي'), '');
  assert.equal(Schema.uniqueId('Test', ['test', 'test-2']), 'test-3');
  assert.equal(Schema.uniqueId('', []), 'item');
  assert.equal(Schema.nextNumberedId('q', ['q-001', 'q-009', 'other']), 'q-010');
  assert.equal(Schema.nextNumberedId('q', []), 'q-001');
  assert.deepEqual(Schema.splitParagraphs('a\nb\n\n\n  c  \r\n\r\nd'), ['a\nb', 'c', 'd']);
  assert.deepEqual(Schema.splitLines(' a \n\n b\r\n'), ['a', 'b']);
  assert.equal(Schema.toJSON(Schema.toFileData('lessons', [])), '{\n  "schemaVersion": 2,\n  "lessons": []\n}\n');
});

/* ---------- Added in Phase 2: units, topics, format upgrade, answer keys ---------- */

test('units: id and title are required; description is optional text', () => {
  assert.deepEqual(errorsOf('units', { id: 'unit-1', title: 'Unit title' }), []);
  assert.match(errorsOf('units', { id: 'unit-1', title: '' }).join(), /title is required/);
  assert.match(errorsOf('units', { id: 'Unit 1', title: 'T' }).join(), /may only contain lowercase/);
  assert.match(errorsOf('units', { id: 'u', title: 'T', description: 5 }).join(), /description must be text/);
  assert.match(Schema.validateCollection('units', [{ id: 'u', title: 'A' }, { id: 'u', title: 'B' }]).errors.join(), /already used/);
});

test('unitId and topicId must be valid ids when given', () => {
  assert.deepEqual(errorsOf('questions', mcq({ unitId: 'unit-1', topicId: 'topic-1' })), []);
  assert.match(errorsOf('questions', mcq({ unitId: 'Unit 1' })).join(), /unitId “Unit 1” is not a valid id/);
  assert.match(errorsOf('summaries', { id: 's', title: 'S', topicId: 'Bad Topic', remember: ['r'] }).join(), /topicId/);
  assert.match(errorsOf('lessons', lesson({ unitId: 7 })).join(), /unitId/);
  assert.match(errorsOf('passages', { id: 'p', title: 'P', paragraphs: ['x'], questions: [], unitId: 'x y' }).join(), /unitId/);
});

test('version 1 field names are upgraded (lessonId → topicId, topic → topicId)', () => {
  assert.deepEqual(Schema.upgradeItem('summaries', { id: 's', lessonId: 'l1' }), { id: 's', topicId: 'l1' });
  assert.deepEqual(Schema.upgradeItem('questions', { id: 'q', topic: 'l1' }), { id: 'q', topicId: 'l1' });
  assert.deepEqual(Schema.upgradeItem('questions', { id: 'q', topic: 'old', topicId: 'new' }), { id: 'q', topicId: 'new' });
  const original = { id: 'q', topic: 'l1' };
  Schema.upgradeItem('questions', original);
  assert.deepEqual(original, { id: 'q', topic: 'l1' }, 'the original is not changed');

  const file = Schema.validateFile('questions', { schemaVersion: 1, questions: [mcq({ topic: 'l1' })] });
  assert.equal(file.errors.length, 0);
  assert.match(file.warnings.join(), /old field name "topic"/);
  const imported = Schema.readImport({ schemaVersion: 1, summaries: [{ id: 's', title: 'S', lessonId: 'l1', remember: ['r'] }] });
  assert.equal(imported.collections.summaries[0].topicId, 'l1');
  assert.equal(Schema.usableItems('questions', [mcq({ topic: 'l1' })]).items[0].topicId, 'l1');
  assert.match(Schema.validateFile('lessons', { schemaVersion: 3, lessons: [] }).errors.join(), /not supported/);
});

test('answer-key mistakes get specific messages', () => {
  const problem = (answer) => Schema.answerKeyProblem(mcq({ answer }));
  assert.equal(problem('Option B'), null);
  assert.match(problem(''), /answer is missing/);
  assert.match(problem(undefined), /answer is missing/);
  assert.match(problem('B'), /looks like an option letter.*option B is “Option B”/);
  assert.match(problem('(c)'), /option letter.*option C is “Option C”/);
  assert.match(problem('2'), /looks like an option number.*option 2 is “Option B”/);
  assert.match(problem(3), /is the number 3.*“Option C”/);
  assert.match(problem(' option b '), /only in spaces or capital letters/);
  assert.match(problem({}), /must be the text/);
});

test('passage options: showParagraphNumbers must be true or false', () => {
  const passage = { id: 'p', title: 'P', paragraphs: ['x'], questions: [], reviewStatus: 'unreviewed' };
  assert.deepEqual(errorsOf('passages', Object.assign({}, passage, { showParagraphNumbers: false })), []);
  assert.match(errorsOf('passages', Object.assign({}, passage, { showParagraphNumbers: 'no' })).join(), /true or false/);
});

test('unitIdOf, groupByUnit and orderByUnit', () => {
  const units = [{ id: 'u1', title: 'U1' }, { id: 'u2', title: 'U2' }];
  const lessons = [lesson({ id: 'l1', unitId: 'u1' }), lesson({ id: 'l2' })];
  const items = [
    { id: 'a', topicId: 'l1' },            // unit from its topic
    { id: 'b', unitId: 'u2' },             // own unit
    { id: 'c', topicId: 'l2' },            // topic without a unit, no unit
    { id: 'd', unitId: 'gone' },           // unknown unit
    { id: 'e', topicId: 'l2', unitId: 'u1' } // topic has no unit, so own unit counts
  ];
  assert.equal(Schema.unitIdOf(items[0], lessons), 'u1');
  assert.equal(Schema.unitIdOf(items[2], lessons), '');
  assert.equal(Schema.unitIdOf(items[4], lessons), 'u1');
  const groups = Schema.groupByUnit(items, units, lessons);
  assert.deepEqual(groups.map((g) => (g.unit ? g.unit.id : null)), ['u1', 'u2', null]);
  assert.deepEqual(groups.map((g) => g.items.map((i) => i.id)), [['a', 'e'], ['b'], ['c', 'd']]);
  assert.deepEqual(Schema.groupByUnit([], units, lessons).map((g) => g.items.length), [0, 0], 'empty units are kept; no "other" group');
  assert.deepEqual(Schema.orderByUnit(items, units, lessons).map((i) => i.id), ['a', 'e', 'b', 'c', 'd']);
});

/* ---------- Automatic difficulty (estimate for questions without one) ---------- */

test('estimateDifficulty: rough rules give a valid level for any question', () => {
  const est = (prompt, options) => Schema.estimateDifficulty({ type: 'mcq', prompt, options, answer: options[0] });
  assert.equal(est('Seldom .......... such a talented student.', ['have I met', 'I have met', 'did I met', 'I met']), 'hard', 'inversion');
  assert.equal(est('Not once .......... a lesson.', ['has she missed', 'she has missed', 'did she missed', 'she missed']), 'hard');
  assert.equal(est('Having .......... the test, he left.', ['finished', 'finishing', 'finish', 'been finished']), 'hard', 'perfect participle');
  assert.equal(est('She .......... the report since 9, but she .......... half.', ['has been writing / has written', 'wrote / has', 'a / b', 'c / d']), 'hard', 'two blanks');
  assert.equal(est('She has lived here .......... 2015.', ['for', 'ago', 'since', 'yet']), 'easy', 'one short word');
  assert.equal(est('He .......... in Saudi Arabia since 2019.', ['works', 'is working', 'had worked', 'has been working']), 'easy', 'clear signal, one present perfect');
  assert.equal(est("It's three years .......... I last saw my cousin.", ['for', 'ago', 'since', 'when']), 'medium', "It's … since");
  assert.equal(est('They .......... each other for a long time.', ['have known', 'have been knowing', 'had been knowing', 'are knowing']), 'medium');
  for (const bad of [null, {}, { prompt: 5 }, { options: 'x' }]) {
    assert.ok(Schema.DIFFICULTIES.includes(Schema.estimateDifficulty(bad)));
  }
});

test('estimateDifficulty agrees with the stored levels for most Present Perfect questions', () => {
  const questions = require('../grammar-questions.json').questions;
  const agree = questions.filter((q) => Schema.estimateDifficulty(q) === q.difficulty).length;
  assert.ok(questions.every((q) => Schema.DIFFICULTIES.includes(q.difficulty)), 'every stored question has a level');
  assert.ok(agree / questions.length >= 0.7, 'agreement ' + agree + ' / ' + questions.length);
});

test('physics questions: every question is valid, has its diagram, and the answer is one of its choices', () => {
  const fs = require('fs');
  const path = require('path');
  const project = path.join(__dirname, '..');
  const data = JSON.parse(fs.readFileSync(path.join(project, 'physics-questions.json'), 'utf8'));
  assert.equal(data.chapters[0].title, 'الفصل الأول');
  assert.equal(data.chapters[0].sections[0].title, 'حل أسئلة الفصل الأول');
  // the downloadable questions PDF and the revision sheet (page + PDF) exist
  assert.ok(fs.existsSync(path.join(project, data.chapters[0].sections[0].pdf)), 'questions PDF');
  assert.equal(data.chapters[0].revision.title, 'مراجعة أهم قوانين الفصل الأول');
  assert.ok(fs.existsSync(path.join(project, data.chapters[0].revision.page)), 'revision page');
  assert.ok(fs.existsSync(path.join(project, data.chapters[0].revision.pdf)), 'revision PDF');
  const ids = new Set();
  data.chapters.forEach((chapter) => {
    chapter.sections.forEach((section) => {
      section.questions.forEach((question, i) => {
        assert.deepEqual(Schema.validateItem('questions', question, i).errors, [], question.id);
        assert.ok(question.options.includes(question.answer), question.id);
        assert.ok(!ids.has(question.id), 'duplicate id ' + question.id);
        ids.add(question.id);
        if (question.image) assert.ok(fs.existsSync(path.join(project, question.image)), question.image);
      });
    });
  });
  assert.equal(ids.size, 118);
  // the first five questions added earlier were removed, with their pictures
  for (let n = 1; n <= 5; n += 1) {
    assert.ok(!ids.has('phys-ch1-q' + n), 'phys-ch1-q' + n + ' should be gone');
    assert.ok(!fs.existsSync(path.join(project, 'physics-ch1-q' + n + '.svg')), 'physics-ch1-q' + n + '.svg should be gone');
  }
  // no question appears twice under another id
  const prompts = data.chapters[0].sections[0].questions.map((q) => q.prompt.replace(/[\u200f\u2066\u2069\s]/g, ''));
  assert.equal(new Set(prompts).size, prompts.length);
});

test('chemistry questions: chapter 1 has the review (50 + 2 written) and test A (50), all valid, with their diagrams', () => {
  const fs = require('fs');
  const path = require('path');
  const project = path.join(__dirname, '..');
  const data = JSON.parse(fs.readFileSync(path.join(project, 'chemistry-questions.json'), 'utf8'));
  assert.deepEqual(data.chapters.map((c) => c.id), ['chapter-1', 'chapter-2']);
  assert.equal(data.chapters[0].title, 'الفصل الأول');
  const sections = data.chapters[0].sections;
  assert.deepEqual(sections.map((s) => s.title), ['أسئلة المراجعة النهائية على الفصل الأول', 'اختبار (A) على الفصل الأول']);
  const expected = [
    Array.from({ length: 50 }, (_, i) => 'chem-ch1-r' + String(i + 1).padStart(2, '0')).concat(['chem-ch1-rw1', 'chem-ch1-rw2']),
    Array.from({ length: 50 }, (_, i) => 'chem-ch1-t' + String(i + 1).padStart(2, '0'))
  ];
  const ids = new Set();
  sections.forEach((section, s) => {
    assert.deepEqual(section.questions.map((q) => q.id), expected[s], section.title);
    section.questions.forEach((question, i) => {
      assert.deepEqual(Schema.validateItem('questions', question, i).errors, [], question.id);
      assert.equal(question.lang, 'ar', question.id);
      assert.equal(question.reviewStatus, 'reviewed', question.id);
      assert.ok(Schema.hasText(question.explanation), question.id + ' has an explanation');
      if (question.type === 'mcq') {
        assert.equal(question.options.length, 4, question.id);
        assert.ok(question.options.includes(question.answer), question.id);
      } else {
        assert.equal(question.type, 'short', question.id);
        assert.ok(Schema.hasText(question.modelAnswer), question.id);
      }
      assert.ok(!ids.has(question.id), 'duplicate id ' + question.id);
      ids.add(question.id);
      if (question.image) assert.ok(fs.existsSync(path.join(project, question.image)), question.image);
    });
    // no question appears twice in the same section (same text, diagram and choices)
    const keys = section.questions.map((q) => [q.prompt, q.image || '', (q.options || []).join('|')].join('#').replace(/[‏⁦⁩\s]/g, ''));
    assert.equal(new Set(keys).size, keys.length, section.title);
  });
  assert.equal(ids.size, 102);
});

test('chemistry chapter 2: 100 multiple-choice questions (50 hard, 50 very hard) and 50 essay questions, with their three PDFs', () => {
  const fs = require('fs');
  const path = require('path');
  const crypto = require('crypto');
  const root = path.join(__dirname, '..');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'chemistry-questions.json'), 'utf8'));
  const chapter = data.chapters[1];
  assert.equal(chapter.id, 'chapter-2');
  assert.equal(chapter.title, 'الفصل الثاني: التحليل الكيميائي');
  const [hard, veryHard, essay] = chapter.sections;
  assert.deepEqual(chapter.sections.map((s) => [s.id, s.questions.length]),
    [['chapter-2-hard', 50], ['chapter-2-very-hard', 50], ['chapter-2-essay', 50]]);
  const plain = (s) => s.replace(/[‏⁦⁩]/g, '');
  const letters = [0, 0, 0, 0];
  [[hard, 'hard', 'h'], [veryHard, 'very-hard', 'v']].forEach(([section, level, tag]) => {
    section.questions.forEach((q, i) => {
      assert.equal(q.id, 'chem-ch2-' + tag + String(i + 1).padStart(2, '0'));
      assert.deepEqual(Schema.validateItem('questions', q, i).errors, [], q.id + ': valid');
      assert.equal(q.type, 'mcq', q.id);
      assert.equal(q.lang, 'ar', q.id);
      assert.equal(q.difficulty, level, q.id);
      assert.equal(q.reviewStatus, 'reviewed', q.id);
      assert.equal(q.options.length, 4, q.id + ': four options');
      assert.equal(new Set(q.options.map(plain)).size, 4, q.id + ': four different options');
      assert.equal(q.options.filter((o) => o === q.answer).length, 1, q.id + ': the answer is exactly one of the options');
      assert.ok(plain(q.explanation).length > 120, q.id + ': a detailed explanation');
      letters[q.options.indexOf(q.answer)] += 1;
    });
  });
  // the correct answer is spread over the four letters
  letters.forEach((n) => assert.ok(n >= 20 && n <= 30, 'answers by letter: ' + letters));
  essay.questions.forEach((q, i) => {
    assert.equal(q.id, 'chem-ch2-e' + String(i + 1).padStart(2, '0'));
    assert.deepEqual(Schema.validateItem('questions', q, i).errors, [], q.id + ': valid');
    assert.equal(q.type, 'short', q.id + ': written answer');
    assert.ok(['hard', 'very-hard'].includes(q.difficulty), q.id + ': hard or very hard');
    assert.equal(q.reviewStatus, 'reviewed', q.id);
    assert.ok(plain(q.modelAnswer).length > 150, q.id + ': a detailed model answer');
  });
  const all = hard.questions.concat(veryHard.questions, essay.questions);
  assert.equal(new Set(all.map((q) => q.id)).size, 150, 'different ids');
  assert.equal(new Set(all.map((q) => plain(q.prompt))).size, 150, 'no question twice');
  assert.equal(new Set(chapter.sections.map((s) => s.id)).size, 3);
  // the three PDFs: one panel each on the chapter page, made from exactly these questions
  assert.deepEqual(chapter.morePdfs.map((p) => [p.file, p.sections]), [
    ['chemistry-ch2-mcq.pdf', ['chapter-2-hard', 'chapter-2-very-hard']],
    ['chemistry-ch2-essay.pdf', ['chapter-2-essay']],
    ['chemistry-ch2-answer-key.pdf', ['chapter-2-hard', 'chapter-2-very-hard', 'chapter-2-essay']]]);
  chapter.morePdfs.forEach((p) => assert.ok(p.title && p.note, p.file + ': title and note'));
  assert.equal(chapter.pdf, undefined, 'no chapter-wide PDF: the three PDFs cover Chapter 2');
  // the same code as fingerprint() in tools/chem_ch2_bank/build.py
  const fingerprint = (questions) => {
    const digest = crypto.createHash('sha256');
    questions.forEach((q) => {
      const fields = [q.prompt].concat(q.options || [], [q.answer || '', q.explanation || '', q.modelAnswer || '']);
      digest.update(fields.join('\x1f') + '\x1e', 'utf8');
    });
    return digest.digest('hex').slice(0, 16);
  };
  const built = JSON.parse(fs.readFileSync(path.join(root, 'tools', 'chem_ch2_bank', 'built.json'), 'utf8')).files;
  const expected = [['chemistry-ch2-mcq.pdf', hard.questions.concat(veryHard.questions)],
    ['chemistry-ch2-essay.pdf', essay.questions], ['chemistry-ch2-answer-key.pdf', all]];
  assert.deepEqual(built.map((b) => b.pdf), expected.map(([name]) => name));
  expected.forEach(([name, questions], i) => {
    assert.equal(fs.readFileSync(path.join(root, name)).subarray(0, 5).toString(), '%PDF-', name + ' is a PDF file');
    assert.equal(built[i].questions, questions.length, name + ': number of questions');
    assert.equal(built[i].fingerprint, fingerprint(questions), name + ' is older than the questions: run python3 tools/chem_ch2_bank/build.py');
  });
  // the PDF on the Chemistry page keeps Chapter 1 only, and says so
  assert.equal(data.pdf, 'chemistry-questions.pdf');
  assert.equal(data.pdfTitle, 'أسئلة الفصل الأول مع مفتاح الإجابات');
});

test('vocabulary: Unit 1 has exactly 100 valid questions, medium and hard only, in their own file', () => {
  const fs = require('fs');
  const path = require('path');
  const project = path.join(__dirname, '..');
  const data = JSON.parse(fs.readFileSync(path.join(project, 'vocabulary-questions.json'), 'utf8'));
  assert.equal(data.units.length, 1);
  assert.equal(data.units[0].id, 'unit-1');
  assert.equal(data.units[0].title, 'Unit 1: Inside the World of Care');
  const questions = data.units[0].questions;
  assert.equal(questions.length, 100);
  assert.deepEqual(questions.map((q) => q.id), Array.from({ length: 100 }, (_, i) => 'vocab-u1-' + String(i + 1).padStart(3, '0')));
  questions.forEach((question, i) => {
    assert.deepEqual(Schema.validateItem('questions', question, i).errors, [], question.id);
    assert.equal(question.type, 'mcq', question.id);
    assert.ok(['medium', 'hard'].includes(question.difficulty), question.id + ' is medium or hard');
    assert.equal(question.options.length, 4, question.id);
    assert.ok(question.options.includes(question.answer), question.id);
    // the explanation says why the answer is right (✓) and why each other choice is wrong (✗)
    const lines = question.explanation.split('\n');
    assert.ok(lines[0].startsWith('✓'), question.id + ' explains the answer');
    assert.ok(lines.slice(1).length >= 1 && lines.slice(1).every((line) => line.startsWith('✗')), question.id + ' explains the wrong choices');
  });
  // no question twice, and the answers are spread over A, B, C and D
  assert.equal(new Set(questions.map((q) => q.prompt)).size, 100);
  const letters = [0, 0, 0, 0];
  questions.forEach((q) => { letters[q.options.indexOf(q.answer)] += 1; });
  assert.ok(letters.every((n) => n >= 15), 'answer positions ' + letters);
  // kept apart from the grammar practice questions
  const grammar = require('../grammar-questions.json').questions;
  const ids = new Set(questions.map((q) => q.id));
  const prompts = new Set(questions.map((q) => q.prompt));
  assert.ok(grammar.every((q) => !ids.has(q.id) && !prompts.has(q.prompt)), 'no vocabulary question in grammar-questions.json');
});

test('biology: chapters 1 and 2 each have 100 multiple-choice questions — 10 easy, 40 medium, 50 very hard', () => {
  const fs = require('fs');
  const path = require('path');
  const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'biology-questions.json'), 'utf8'));
  assert.deepEqual(data.chapters.map((c) => c.id), ['chapter-1', 'chapter-2']);
  const levels = [['easy', 10], ['medium', 40], ['very-hard', 50]];
  const ids = new Set();
  data.chapters.forEach((chapter, c) => {
    // chapter 2 also has its essay and picture sections after these (checked in the next test)
    const extra = chapter.id === 'chapter-2' ? ['chapter-2-essay', 'chapter-2-images'] : [];
    assert.deepEqual(chapter.sections.map((s) => s.id), levels.map(([level]) => chapter.id + '-' + level).concat(extra), chapter.title);
    chapter.sections.slice(0, 3).forEach((section, s) => {
      const [level, count] = levels[s];
      assert.equal(section.questions.length, count, section.title);
      const letters = [0, 0, 0, 0];
      section.questions.forEach((question, i) => {
        assert.deepEqual(Schema.validateItem('questions', question, i).errors, [], question.id);
        assert.equal(question.type, 'mcq', question.id);
        assert.equal(question.lang, 'ar', question.id);
        assert.equal(question.difficulty, level, question.id);
        assert.equal(question.options.length, 4, question.id);
        assert.equal(new Set(question.options).size, 4, question.id + ' has four different options');
        assert.ok(question.options.includes(question.answer), question.id);
        letters[question.options.indexOf(question.answer)] += 1;
        // the explanation covers all four options: one ✓ and three ✗
        assert.equal((question.explanation.match(/✓/g) || []).length, 1, question.id + ' ✓');
        assert.equal((question.explanation.match(/✗/g) || []).length, 3, question.id + ' ✗');
        assert.ok(!ids.has(question.id), 'duplicate id ' + question.id);
        ids.add(question.id);
      });
      // the correct answers are spread over the four positions
      assert.ok(letters.every((n) => n >= Math.floor(count / 4) - 1), section.id + ' answer positions ' + letters);
      const prompts = section.questions.map((q) => q.prompt.replace(/\s+/g, ' '));
      assert.equal(new Set(prompts).size, prompts.length, section.id + ' has no repeated question');
    });
  });
  assert.equal(ids.size, 200);
});

test('biology chapter 2: 50 essay questions and 50 picture questions with model answers, their pictures and their PDF', () => {
  const fs = require('fs');
  const path = require('path');
  const crypto = require('crypto');
  const root = path.join(__dirname, '..');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'biology-questions.json'), 'utf8'));
  const chapter = data.chapters[1];
  const [essay, pictures] = chapter.sections.slice(3);
  assert.equal(essay.id, 'chapter-2-essay');
  assert.equal(essay.title, 'الأسئلة المقالية – 50 سؤالًا');
  assert.equal(pictures.id, 'chapter-2-images');
  assert.equal(pictures.title, 'أسئلة على الصور – 50 سؤالًا');
  assert.equal(essay.questions.length, 50);
  assert.equal(pictures.questions.length, 50);
  const all = essay.questions.concat(pictures.questions);
  all.forEach((q, i) => {
    assert.deepEqual(Schema.validateItem('questions', q, i).errors, [], q.id + ': valid');
    assert.equal(q.type, 'short', q.id + ': written answer');
    assert.equal(q.lang, 'ar', q.id);
    assert.equal(q.reviewStatus, 'reviewed', q.id);
    assert.ok(['hard', 'very-hard'].includes(q.difficulty), q.id + ': hard or very hard only');
    assert.ok(q.modelAnswer.trim().length > 40, q.id + ': model answer');
  });
  assert.equal(new Set(all.map((q) => q.id)).size, 100, 'different ids');
  assert.equal(new Set(all.map((q) => q.prompt)).size, 100, 'no question twice');
  essay.questions.forEach((q) => assert.ok(!q.image, q.id + ': essay questions have no picture'));
  // every picture question has its own picture, a real PNG next to index.html, with a description
  pictures.questions.forEach((q, i) => {
    assert.equal(q.image, 'bio-ch2-img' + String(i + 1).padStart(2, '0') + '.png', q.id);
    const png = fs.readFileSync(path.join(root, q.image));
    assert.equal(png.subarray(1, 4).toString(), 'PNG', q.image + ' is a PNG');
    assert.ok(png.readUInt32BE(16) >= 1200, q.image + ' is large (at least 1200 pixels wide)');
    assert.ok(q.imageAlt.trim().length > 20, q.id + ': picture description');
  });
  assert.equal(new Set(pictures.questions.map((q) => q.image)).size, 50, 'fifty different pictures');
  // the PDF: shown on the chapter page as its own panel; made from these questions
  assert.deepEqual(chapter.morePdfs, [{ file: 'biology-ch2-essay-image-questions.pdf', title: '100 سؤال مقالي وعلى الصور مع الإجابات النموذجية', sections: ['chapter-2-essay', 'chapter-2-images'] }]);
  const built = JSON.parse(fs.readFileSync(path.join(root, 'tools', 'bio_ch2_bank', 'built.json'), 'utf8'));
  assert.equal(built.pdf, chapter.morePdfs[0].file);
  assert.equal(fs.readFileSync(path.join(root, built.pdf)).subarray(0, 5).toString(), '%PDF-');
  const digest = crypto.createHash('sha256');
  all.forEach((q) => digest.update([q.prompt, q.modelAnswer, q.image || ''].join('\x1f') + '\x1e', 'utf8'));
  assert.equal(built.fingerprint, digest.digest('hex').slice(0, 16), 'the PDF is older than the questions: run python3 tools/bio_ch2_bank/build.py');
});

test('questions: optional lang, image and imageAlt are checked', () => {
  const question = mcq({ lang: 'ar', image: 'figure.svg', imageAlt: 'وصف الشكل' });
  assert.deepEqual(errorsOf('questions', question), []);
  assert.match(errorsOf('questions', mcq({ lang: 'fr' })).join(), /lang must be/);
  assert.match(errorsOf('questions', mcq({ image: 3 })).join(), /image must be text/);
});

test('question PDFs: English, Chemistry and Biology chapters 1 and 2 are linked, are PDFs, and match the questions', () => {
  const fs = require('fs');
  const path = require('path');
  const crypto = require('crypto');
  const root = path.join(__dirname, '..');
  const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
  // the same code as fingerprint() in tools/question_pdfs.py
  const fingerprint = (questions) => {
    const digest = crypto.createHash('sha256');
    questions.forEach((q) => {
      const fields = [q.prompt].concat(q.options || [], [q.answer || '', q.modelAnswer || '', q.image || '']);
      digest.update(fields.join('\x1f') + '\x1e', 'utf8');
    });
    return digest.digest('hex').slice(0, 16);
  };
  // (sections listed in a chapter's "morePdfs" have a PDF of their own)
  const all = (chapters) => chapters.reduce((list, c) => {
    const own = new Set([].concat(...(c.morePdfs || []).map((item) => item.sections)));
    return list.concat(...c.sections.filter((s) => !own.has(s.id)).map((s) => s.questions));
  }, []);
  const chemistry = read('chemistry-questions.json');
  const biology = read('biology-questions.json');
  const expected = [
    ['english-questions.pdf', read('grammar-questions.json').questions.concat(...read('vocabulary-questions.json').units.map((u) => u.questions))],
    [chemistry.pdf, all(chemistry.chapters)],
    [biology.chapters[0].pdf, all([biology.chapters[0]])],
    [biology.chapters[1].pdf, all([biology.chapters[1]])]
  ];
  assert.deepEqual(expected.map(([name]) => name), ['english-questions.pdf', 'chemistry-questions.pdf', 'biology-ch1-questions.pdf', 'biology-ch2-questions.pdf']);
  assert.match(fs.readFileSync(path.join(root, 'index.html'), 'utf8'), /href="english-questions\.pdf"[^>]*download/);
  const made = read('question-pdfs.json').files;
  assert.equal(made.length, 4);
  expected.forEach(([name, questions], i) => {
    assert.equal(fs.readFileSync(path.join(root, name)).subarray(0, 5).toString(), '%PDF-', name + ' is a PDF file');
    assert.equal(made[i].pdf, name);
    assert.equal(made[i].questions, questions.length, name + ': number of questions');
    assert.equal(made[i].fingerprint, fingerprint(questions), name + ' is older than its questions: run python3 tools/question_pdfs.py');
  });
});

test('Arabic Unit 3: 100 questions on the site (arabic-questions.json), the PDFs made from them, linked from the Arabic page', () => {
  const fs = require('fs');
  const path = require('path');
  const crypto = require('crypto');
  const root = path.join(__dirname, '..');
  const folder = path.join(root, 'tools', 'arabic_unit3');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'arabic-questions.json'), 'utf8'));
  assert.equal(data.schemaVersion, 2);
  assert.deepEqual(data.chapters.map((c) => c.id), ['unit-2', 'unit-3'], 'Unit 2, then Unit 3');
  const unit = data.chapters.find((c) => c.id === 'unit-3');
  assert.deepEqual(unit.sections.map((s) => [s.id, s.questions.length]),
    [['unit-3-kana', 22], ['unit-3-kada', 14], ['unit-3-inna', 30], ['unit-3-la', 14], ['unit-3-mixed', 20]]);
  const ids = [];
  unit.sections.forEach((section) => section.questions.forEach((q, i) => {
    ids.push(q.id);
    assert.equal(Schema.validateItem('questions', q, i).errors.length, 0, q.id + ': valid question');
    assert.equal(q.type, 'mcq');
    assert.equal(q.lang, 'ar');
    assert.equal(q.reviewStatus, 'reviewed');
    assert.ok(['medium', 'hard'].includes(q.difficulty), q.id + ': medium or hard only');
    assert.equal(q.options.length, 4, q.id + ': four options');
    assert.equal(new Set(q.options.map((o) => o.trim())).size, 4, q.id + ': different options');
    assert.equal(q.options.filter((o) => o === q.answer).length, 1, q.id + ': the answer is exactly one of the options');
    assert.ok(q.explanation.trim(), q.id + ': explanation');
    assert.ok(!/[A-Za-z0-9]/.test(q.prompt + q.options.join('') + q.explanation), q.id + ': no Latin letters or Western digits (as in the PDF)');
  }));
  assert.equal(new Set(ids).size, 100, 'unique ids');
  const built = JSON.parse(fs.readFileSync(path.join(folder, 'built.json'), 'utf8'));
  // the same as fingerprint() in tools/arabic_unit3/build.py: Unit 3 written compactly, then the summary
  const source = Buffer.concat([Buffer.from(JSON.stringify(unit), 'utf8'), Buffer.from([0]), fs.readFileSync(path.join(folder, 'summary.html'))]);
  assert.equal(built.fingerprint, crypto.createHash('sha256').update(source).digest('hex').slice(0, 16),
    'the Arabic PDFs are older than the questions or the summary: run python3 tools/arabic_unit3/build.py');
  const page = fs.readFileSync(path.join(root, 'arabic.html'), 'utf8');
  assert.ok(page.includes('data-questions="arabic-questions.json"'), 'the Arabic page shows the questions');
  [[built.questions_pdf, 'تحميل 100 سؤال على الوحدة الثالثة'], [built.summary_pdf, 'تحميل ملخص الوحدة الثالثة']].forEach(([pdf, label]) => {
    assert.equal(fs.readFileSync(path.join(root, pdf)).subarray(0, 5).toString(), '%PDF-', pdf + ' is a PDF file');
    assert.ok(page.includes('href="' + pdf + '" target="_blank"'), pdf + ' can be viewed');
    assert.ok(page.includes('href="' + pdf + '" download type="application/pdf">' + label + '</a>'), pdf + ' can be downloaded: ' + label);
  });
});

test('Arabic Unit 2: 50 multiple-choice and 50 written questions on the site, before Unit 3, and the two PDFs made from them', () => {
  const fs = require('fs');
  const path = require('path');
  const crypto = require('crypto');
  const root = path.join(__dirname, '..');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'arabic-questions.json'), 'utf8'));
  assert.equal(data.chapters[0].id, 'unit-2', 'Unit 2 comes first, before Unit 3');
  const unit = data.chapters[0];
  assert.equal(unit.title, 'الوحدة الثانية – اللغة العربية: الأبنية');
  assert.deepEqual(unit.sections.map((s) => [s.id, s.questions.length]), [['unit-2-mcq', 50], ['unit-2-essay', 50]]);
  const [mcq, essay] = unit.sections.map((s) => s.questions);
  const noLatin = (q, textOf) => assert.ok(!/[A-Za-z0-9]/.test(textOf), q.id + ': no Latin letters or Western digits (as in the PDF)');
  mcq.forEach((q, i) => {
    assert.equal(Schema.validateItem('questions', q, i).errors.length, 0, q.id + ': valid question');
    assert.equal(q.id, 'ar-u2-mcq-' + String(i + 1).padStart(2, '0'));
    assert.equal(q.type, 'mcq');
    assert.equal(q.lang, 'ar');
    assert.equal(q.reviewStatus, 'reviewed');
    assert.equal(q.options.length, 4, q.id + ': four options');
    assert.equal(new Set(q.options.map((o) => o.trim())).size, 4, q.id + ': different options');
    assert.equal(q.options.filter((o) => o === q.answer).length, 1, q.id + ': the answer is exactly one of the options');
    assert.ok(q.explanation.trim(), q.id + ': explanation');
    noLatin(q, q.prompt + q.options.join('') + q.explanation);
  });
  assert.deepEqual(['medium', 'hard', 'very-hard'].map((d) => mcq.some((q) => q.difficulty === d)), [true, true, true], 'medium, hard and very hard questions');
  const places = [0, 1, 2, 3].map((k) => mcq.filter((q) => q.options.indexOf(q.answer) === k).length);
  assert.ok(Math.min(...places) >= 12 && Math.max(...places) <= 13, 'the right answer is in each place about equally often: ' + places);
  essay.forEach((q, i) => {
    assert.equal(Schema.validateItem('questions', q, i).errors.length, 0, q.id + ': valid question');
    assert.equal(q.id, 'ar-u2-essay-' + String(i + 1).padStart(2, '0'));
    assert.equal(q.type, 'short');
    assert.equal(q.lang, 'ar');
    assert.equal(q.reviewStatus, 'reviewed');
    assert.equal(q.revealAnytime, true, q.id + ': the model answer can be shown at any time');
    assert.ok(['hard', 'very-hard'].includes(q.difficulty), q.id + ': hard or very hard');
    assert.ok(q.modelAnswer.trim().length > 40, q.id + ': a model answer');
    noLatin(q, q.prompt + q.modelAnswer);
  });
  const all = data.chapters.flatMap((c) => c.sections.flatMap((s) => s.questions));
  assert.equal(new Set(all.map((q) => q.id)).size, all.length, 'unique ids in the Arabic file');
  assert.equal(new Set(all.map((q) => q.prompt.trim())).size, all.length, 'no question twice in the Arabic file');
  // the PDFs: listed on the unit's page ("morePdfs"), made from these questions (tools/arabic_unit2/build.py)
  assert.deepEqual(unit.morePdfs.map((p) => [p.file, p.sections]), [['arabic-unit2-mcq.pdf', ['unit-2-mcq']], ['arabic-unit2-essay.pdf', ['unit-2-essay']]]);
  unit.morePdfs.forEach((p) => assert.ok(p.title && p.note, p.file + ': title and note'));
  // the same code as fingerprint() in tools/arabic_unit2/build.py
  const fingerprint = (questions) => {
    const digest = crypto.createHash('sha256');
    questions.forEach((q) => {
      const fields = [q.prompt].concat(q.options || [], [q.answer || '', q.explanation || '', q.modelAnswer || '', q.difficulty]);
      digest.update(fields.join('\x1f') + '\x1e', 'utf8');
    });
    return digest.digest('hex').slice(0, 16);
  };
  const built = JSON.parse(fs.readFileSync(path.join(root, 'tools', 'arabic_unit2', 'built.json'), 'utf8')).files;
  [['arabic-unit2-mcq.pdf', mcq], ['arabic-unit2-essay.pdf', essay]].forEach(([name, questions], i) => {
    assert.equal(built[i].pdf, name);
    assert.equal(fs.readFileSync(path.join(root, name)).subarray(0, 5).toString(), '%PDF-', name + ' is a PDF file');
    assert.equal(built[i].questions, 50, name + ': 50 questions');
    assert.equal(built[i].fingerprint, fingerprint(questions), name + ' is older than the questions: run python3 tools/arabic_unit2/build.py');
  });
  // and on the Arabic page itself, with the title the owner asked for
  const page = fs.readFileSync(path.join(root, 'arabic.html'), 'utf8');
  assert.ok(page.includes('>الوحدة الثانية – اللغة العربية</h2>'), 'the Unit 2 heading on the Arabic page');
  [['arabic-unit2-mcq.pdf', 'عرض ملف PDF', 'تحميل أسئلة الاختيار من متعدد'],
    ['arabic-unit2-essay.pdf', 'عرض ملف PDF', 'تحميل الأسئلة المقالية']].forEach(([pdf, view, label]) => {
    assert.ok(page.includes('href="' + pdf + '" target="_blank" rel="noopener" type="application/pdf">' + view + '</a>'), pdf + ' can be viewed: ' + view);
    assert.ok(page.includes('href="' + pdf + '" download type="application/pdf">' + label + '</a>'), pdf + ' can be downloaded: ' + label);
  });
  assert.ok(page.includes('href="arabic.html?chapter=unit-2&amp;section=unit-2-mcq"') && page.includes('href="arabic.html?chapter=unit-2&amp;section=unit-2-essay"'),
    'buttons to solve each part online');
});

test('dhikr: the list of adhkar, and the font has every character they use', () => {
  const fs = require('fs');
  const path = require('path');
  const root = path.join(__dirname, '..');
  const source = fs.readFileSync(path.join(root, 'dhikr.js'), 'utf8');
  const items = [...source.matchAll(/\{ text: '([^']*)', source: '([^']*)' \}/g)].map((m) => ({ text: m[1], source: m[2] }));
  assert.ok(items.length >= 30, 'at least 30 adhkar');
  assert.equal(new Set(items.map((i) => i.text)).size, items.length, 'no dhikr twice');
  items.forEach((item) => {
    assert.ok(/[؀-ۿ]/.test(item.text) && !/[A-Za-z0-9]/.test(item.text), 'Arabic text: ' + item.text);
    assert.ok(item.source.trim(), 'a source or label: ' + item.text);
    if (item.text.startsWith('﴿')) assert.match(item.source, /^سورة .+: [٠-٩–]+$/, 'a verse gives its sura and number: ' + item.text);
  });
  const fontCharacters = new Set(JSON.parse(fs.readFileSync(path.join(root, 'tools', 'dhikr_font.json'), 'utf8')).characters);
  const missing = [...new Set(items.map((i) => i.text).join(''))].filter((c) => !fontCharacters.has(c));
  assert.deepEqual(missing, [], 'dhikr-amiri.woff lacks some characters: run python3 tools/dhikr_font.py');
  assert.ok(fs.statSync(path.join(root, 'dhikr-amiri.woff')).size > 1000);
  fs.readdirSync(root).filter((f) => f.endsWith('.html')).forEach((page) => {
    assert.ok(fs.readFileSync(path.join(root, page), 'utf8').includes('<script src="dhikr.js"></script>'), page + ' loads dhikr.js');
  });
});
