/* Tests for the quizzes (quizzes-data.js and the five quizzes-<subject>.json files).
   Run with: node --test tests/quizzes.test.js */
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const Quizzes = require('../quizzes-data.js');

const PROJECT = path.join(__dirname, '..');

function readJSON(name) {
  return JSON.parse(fs.readFileSync(path.join(PROJECT, name), 'utf8'));
}

function question(extra) {
  return Object.assign({
    id: 'q1', skill: 'Test skill', question: 'Test question?',
    options: ['Test one', 'Test two', 'Test three', 'Test four'], correctIndex: 1,
    explanation: ['Test step one', 'Test step two']
  }, extra);
}

function file(questions, quizExtra) {
  return { subject: 'chemistry', lang: 'ar', quizzes: [Object.assign({ id: 'test-quiz', title: 'Test quiz', chapter: 'Test chapter', difficulty: 'Hard', questions: questions }, quizExtra)] };
}

test('five subjects, in the order of the subject menu, each with its own file', () => {
  assert.deepEqual(Quizzes.SUBJECTS.map((s) => s.id), ['arabic', 'english', 'physics', 'chemistry', 'biology']);
  Quizzes.SUBJECTS.forEach((s) => {
    assert.equal(s.file, 'quizzes-' + s.id + '.json');
    assert.ok(fs.existsSync(path.join(PROJECT, s.file)), s.file + ' is missing');
    assert.ok(fs.existsSync(path.join(PROJECT, s.icon)), s.icon + ' is missing');
  });
});

test('every quiz file is valid: every quiz and question can be shown', () => {
  Quizzes.SUBJECTS.forEach((s) => {
    const data = readJSON(s.file);
    assert.equal(data.subject, s.id, s.file);
    assert.ok(data.lang === 'ar' || data.lang === 'en', s.file + ': lang');
    const result = Quizzes.readFile(data, s.id);
    assert.deepEqual(result.problems, [], s.file);
    assert.equal(result.skipped, 0, s.file);
    assert.equal(result.quizzes.length, data.quizzes.length, s.file);
  });
});

test('a correct question passes; a question with a mistake is left out with a reason', () => {
  assert.deepEqual(Quizzes.questionProblems(question()), []);
  assert.deepEqual(Quizzes.questionProblems(question({ explanation: 'One step\nAnother step' })), []);
  const cases = [
    [{ skill: '' }, /"skill" is missing/],
    [{ question: ' ' }, /"question" is missing/],
    [{ options: ['Only one'] }, /"options" must be a list/],
    [{ options: ['Same', 'Same', 'Other', 'Last'] }, /two choices are the same/],
    [{ correctIndex: 4 }, /"correctIndex"/],
    [{ correctIndex: '1' }, /"correctIndex"/],
    [{ correctIndex: 1.5 }, /"correctIndex"/],
    [{ explanation: [] }, /"explanation" is missing/],
    [{ whyWrong: ['a', 'b'] }, /"whyWrong"/],
    [{ svg: '<svg viewBox="0 0 10 10"></svg>' }, /"svgAlt"/],
    [{ svg: '<div></div>', svgAlt: 'Test' }, /whole <svg/]
  ];
  cases.forEach(([extra, pattern]) => {
    const problems = Quizzes.questionProblems(question(extra));
    assert.ok(problems.some((p) => pattern.test(p)), JSON.stringify(extra) + ' → ' + problems.join('; '));
  });
  const result = Quizzes.readFile(file([question(), question({ id: 'q2', correctIndex: 9 }), question()]), 'chemistry');
  assert.equal(result.quizzes.length, 1);
  assert.equal(result.quizzes[0].questions.length, 1, 'the bad question and the repeated id are left out');
  assert.equal(result.skipped, 2);
  assert.ok(result.problems.some((p) => /question 2: "correctIndex"/.test(p)));
  assert.ok(result.problems.some((p) => /question 3: another question in this quiz has the same "id"/.test(p)));
});

test('quiz fields are checked: id, title, difficulty, repeated quiz ids', () => {
  assert.equal(Quizzes.readFile(file([question()], { difficulty: 'Impossible' }), 'chemistry').quizzes.length, 0);
  assert.equal(Quizzes.readFile(file([question()], { id: 'has spaces' }), 'chemistry').quizzes.length, 0);
  assert.equal(Quizzes.readFile(file([question()], { title: '' }), 'chemistry').quizzes.length, 0);
  const two = file([question()]);
  two.quizzes.push(Object.assign({}, two.quizzes[0]));
  const result = Quizzes.readFile(two, 'chemistry');
  assert.equal(result.quizzes.length, 1);
  assert.ok(result.problems.some((p) => /same "id"/.test(p)));
  assert.ok(Quizzes.readFile({ quizzes: 'none' }, 'physics').problems.length > 0);
  assert.equal(Quizzes.readFile({ subject: 'physics', quizzes: [] }, 'physics').lang, 'ar');
  assert.equal(Quizzes.readFile({ subject: 'english', quizzes: [] }, 'english').lang, 'en');
});

test('grading: correct, wrong, unanswered and the percentage', () => {
  const questions = [question(), question({ correctIndex: 0 }), question({ correctIndex: 3 }), question({ correctIndex: 2 })];
  assert.deepEqual(Quizzes.grade(questions, [1, 2, null, 2]), { correct: 2, wrong: 1, unanswered: 1, total: 4, percent: 50 });
  assert.deepEqual(Quizzes.grade(questions, [null, null, null, null]), { correct: 0, wrong: 0, unanswered: 4, total: 4, percent: 0 });
  assert.equal(Quizzes.grade(questions.slice(0, 3), [1, 0, 0]).percent, 67);
});

test('the last score is saved per quiz, only the score and the date; blocked storage is harmless', () => {
  const store = { data: {}, getItem(k) { return k in this.data ? this.data[k] : null; }, setItem(k, v) { this.data[k] = String(v); } };
  assert.equal(Quizzes.lastScore('physics', 'a', store), null);
  assert.equal(Quizzes.saveScore('physics', 'a', 7, 10, store), true);
  assert.equal(Quizzes.saveScore('physics', 'b', 3, 4, store), true);
  const last = Quizzes.lastScore('physics', 'a', store);
  assert.equal(last.score, 7);
  assert.equal(last.total, 10);
  assert.equal(last.percent, 70);
  assert.deepEqual(Object.keys(JSON.parse(store.data[Quizzes.SCORES_KEY])['physics/a']).sort(), ['date', 'percent', 'score', 'total']);
  Quizzes.saveScore('physics', 'a', 9, 10, store);
  assert.equal(Quizzes.lastScore('physics', 'a', store).score, 9, 'a new score replaces the old one');
  assert.equal(Quizzes.lastScore('physics', 'b', store).score, 3, 'other quizzes keep theirs');
  store.data[Quizzes.SCORES_KEY] = 'not json';
  assert.equal(Quizzes.lastScore('physics', 'a', store), null);
  store.data[Quizzes.SCORES_KEY] = JSON.stringify({ 'physics/a': { score: 12, total: 10 } });
  assert.equal(Quizzes.lastScore('physics', 'a', store), null, 'impossible scores are ignored');
  const blocked = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } };
  assert.equal(Quizzes.saveScore('physics', 'a', 1, 2, blocked), false);
  assert.equal(Quizzes.lastScore('physics', 'a', blocked), null);
});

test('Physics Chapter 1 quiz: 10 very hard questions, 4 choices, 10 different skills, answers spread out', () => {
  const quiz = readJSON('quizzes-physics.json').quizzes.find((q) => q.id === 'physics-ch1-quiz-1');
  assert.ok(quiz, 'physics-ch1-quiz-1 is missing');
  assert.equal(quiz.difficulty, 'Very Hard');
  assert.equal(quiz.questions.length, 10);
  assert.equal(new Set(quiz.questions.map((q) => q.skill)).size, 10, 'every question measures a different skill');
  assert.equal(new Set(quiz.questions.map((q) => q.question)).size, 10);
  quiz.questions.forEach((q, i) => {
    assert.equal(q.options.length, 4, 'question ' + (i + 1));
    assert.ok(Array.isArray(q.explanation) && q.explanation.length >= 3, 'question ' + (i + 1) + ': step-by-step explanation');
    assert.equal(q.whyWrong.length, 4, 'question ' + (i + 1));
    q.whyWrong.forEach((text, j) => {
      if (j === q.correctIndex) assert.equal(text, '', 'question ' + (i + 1) + ': no "why wrong" for the right choice');
      else assert.ok(text.trim().length > 20, 'question ' + (i + 1) + ': every wrong choice is explained');
    });
    if (q.svg) {
      assert.ok(!/<script|\son\w+\s*=|href\s*=/i.test(q.svg), 'question ' + (i + 1) + ': the drawing has no script or link');
      assert.ok(/viewBox="/.test(q.svg), 'question ' + (i + 1) + ': the drawing scales');
    }
  });
  const places = quiz.questions.map((q) => q.correctIndex);
  [0, 1, 2, 3].forEach((place) => assert.ok(places.filter((p) => p === place).length >= 2, 'the right answers are spread over the four places: ' + places));
});

test('every page with the subject menu has the Quizzes link next to it', () => {
  fs.readdirSync(PROJECT).filter((name) => name.endsWith('.html')).forEach((name) => {
    const html = fs.readFileSync(path.join(PROJECT, name), 'utf8');
    if (!html.includes('class="subject-menu"')) return;
    assert.match(html, /<\/details>\s*<a class="quizzes-link" href="quizzes\.html"[^>]*><span data-i18n="Quizzes">Quizzes<\/span><\/a>/, name);
  });
});
