/* Unit tests for quiz-engine.js — run with: node --test tests/*.test.js
   Fixtures use placeholder text only; they are not educational content. */
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { Quiz, shuffle, gradeAll, unansweredNumbers, hasValidAnswerKey, pickSpread, parseCount } = require('../quiz-engine.js');

function mcq(id, reviewStatus) {
  return { id, type: 'mcq', prompt: 'Prompt ' + id, options: ['A', 'B', 'C'], answer: 'B', reviewStatus };
}

function short(id) {
  return { id, type: 'short', prompt: 'Prompt ' + id, modelAnswer: 'Model', reviewStatus: 'unreviewed' };
}

/* Deterministic random numbers for repeatable shuffles. */
function seeded(seed) {
  return function () {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };
}

test('a quiz needs at least one question', () => {
  assert.throws(() => new Quiz([]), /at least one question/);
});

test('unreviewed questions never report correct/incorrect', () => {
  const quiz = new Quiz([mcq('q1', 'unreviewed')], { shuffle: false });
  const wrong = quiz.submit('A');
  assert.equal(wrong.outcome, 'differs');
  assert.equal(wrong.reviewed, false);
  const right = quiz.submit('B');
  assert.equal(right.outcome, 'matches');
});

test('reviewed questions report correct/incorrect', () => {
  const quiz = new Quiz([mcq('q1', 'reviewed')], { shuffle: false });
  assert.equal(quiz.submit('C').outcome, 'incorrect');
  assert.equal(quiz.submit('B').outcome, 'correct');
});

test('only the first attempt counts towards the score', () => {
  const quiz = new Quiz([mcq('q1', 'reviewed'), mcq('q2', 'reviewed')], { shuffle: false });
  quiz.submit('A');           // wrong first try
  quiz.submit('B');           // right on retry
  quiz.next();
  quiz.submit('B');           // right first try
  quiz.next();
  const results = quiz.results();
  assert.equal(results.scoredCount, 2);
  assert.equal(results.firstTryMatches, 1);
  assert.equal(results.percent, 50);
  assert.equal(results.provisional, false);
  assert.equal(results.items[0].attempts, 2);
});

test('retry rules: no repeating a tried option; no retry once every wrong option is tried', () => {
  const quiz = new Quiz([mcq('q1', 'unreviewed')], { shuffle: false });
  quiz.submit('A');
  assert.equal(quiz.canRetry(), true);
  assert.throws(() => quiz.submit('A'), /already tried/);
  quiz.submit('C');
  // Only the answer is left untried, so a retry is still possible.
  assert.equal(quiz.canRetry(), true);
  quiz.submit('B');
  assert.equal(quiz.canRetry(), false, 'answered questions cannot be retried');
  assert.throws(() => quiz.submit('B'), /already been answered/);
});

test('invalid answers are rejected', () => {
  const quiz = new Quiz([mcq('q1', 'unreviewed')], { shuffle: false });
  assert.throws(() => quiz.submit('Z'), /choose one of the options/);
  assert.throws(() => quiz.submit(undefined), /choose one of the options/);
});

test('reveal needs an attempt; next needs a finished question', () => {
  const quiz = new Quiz([mcq('q1', 'unreviewed'), mcq('q2', 'unreviewed')], { shuffle: false });
  assert.throws(() => quiz.reveal(), /at least once/);
  assert.throws(() => quiz.next(), /Answer the question/);
  quiz.submit('A');
  quiz.reveal();
  quiz.next();
  assert.equal(quiz.index, 1);
  assert.equal(quiz.finished, false);
  quiz.submit('B');
  quiz.next();
  assert.equal(quiz.finished, true);
  assert.throws(() => quiz.next(), /already finished/);
});

test('scores are provisional when any scored question is unreviewed', () => {
  const quiz = new Quiz([mcq('q1', 'reviewed'), mcq('q2', 'unreviewed')], { shuffle: false });
  quiz.submit('B'); quiz.next();
  quiz.submit('B'); quiz.next();
  const results = quiz.results();
  assert.equal(results.provisional, true);
  assert.equal(results.unreviewedCount, 1);
});

test('short answers are recorded but never scored', () => {
  const quiz = new Quiz([short('s1'), mcq('q1', 'unreviewed')], { shuffle: false });
  assert.throws(() => quiz.submit('   '), /write an answer/);
  assert.equal(quiz.submit('  my answer  ').outcome, 'recorded');
  quiz.next();
  quiz.submit('A'); quiz.reveal(); quiz.next();
  const results = quiz.results();
  assert.equal(results.scoredCount, 1);
  assert.equal(results.shortAnswerCount, 1);
  assert.equal(results.items[0].response, 'my answer');
  assert.deepEqual(quiz.missedQuestions().map((q) => q.id), ['q1']);
});

test('retryMissed starts a round with only missed questions; restart brings all back', () => {
  const questions = [mcq('q1', 'unreviewed'), mcq('q2', 'unreviewed'), mcq('q3', 'unreviewed')];
  const quiz = new Quiz(questions, { shuffle: false });
  quiz.submit('B'); quiz.next();             // q1 matched
  quiz.submit('A'); quiz.reveal(); quiz.next(); // q2 missed
  quiz.submit('C'); quiz.submit('B'); quiz.next(); // q3 missed (first try wrong)
  quiz.retryMissed();
  assert.equal(quiz.roundType, 'missed');
  assert.deepEqual(quiz.items.map((item) => item.question.id), ['q2', 'q3']);
  quiz.submit('B'); quiz.next();
  quiz.submit('B'); quiz.next();
  assert.throws(() => quiz.retryMissed(), /no missed questions/);
  quiz.restart();
  assert.equal(quiz.roundType, 'full');
  assert.equal(quiz.total, 3);
  assert.equal(quiz.index, 0);
  assert.equal(quiz.items.every((item) => item.attempts.length === 0), true);
});

test('shuffle keeps every question exactly once; shuffle: false keeps order', () => {
  const list = Array.from({ length: 20 }, (_, i) => i);
  const mixed = shuffle(list, seeded(42));
  assert.deepEqual([...mixed].sort((a, b) => a - b), list);
  assert.notDeepEqual(mixed, list);
  assert.deepEqual(list, Array.from({ length: 20 }, (_, i) => i), 'input is not modified');
  const ordered = new Quiz([mcq('a'), mcq('b'), mcq('c')], { shuffle: false });
  assert.deepEqual(ordered.items.map((item) => item.question.id), ['a', 'b', 'c']);
});

/* ---------- Added in Phase 2: answer-all mode ---------- */

test('gradeAll: unanswered questions are never marked correct', () => {
  const questions = [mcq('q1', 'reviewed'), mcq('q2', 'reviewed'), mcq('q3', 'reviewed'), mcq('q4', 'reviewed')];
  const result = gradeAll(questions, { q1: 'B', q2: 'A', q3: '', q4: 'Not an option' });
  assert.deepEqual(result.items.map((item) => item.status), ['correct', 'incorrect', 'unanswered', 'unanswered']);
  assert.deepEqual(result.items.map((item) => item.correct), [true, false, false, false]);
  assert.equal(result.correctCount, 1);
  assert.equal(result.incorrectCount, 1);
  assert.equal(result.unansweredCount, 2);
  assert.equal(result.scoredCount, 4);
  assert.equal(result.percent, 25);
  assert.deepEqual(result.missed.map((q) => q.id), ['q2', 'q3', 'q4']);
});

test('gradeAll: nothing answered scores zero, never full marks', () => {
  const result = gradeAll([mcq('q1', 'reviewed'), mcq('q2', 'unreviewed')], {});
  assert.equal(result.correctCount, 0);
  assert.equal(result.unansweredCount, 2);
  assert.equal(result.percent, 0);
  // Even an (invalid) empty answer key cannot be "matched" by an empty answer.
  const broken = Object.assign(mcq('q3', 'reviewed'), { answer: '' });
  const brokenResult = gradeAll([broken], { q3: '' });
  assert.equal(brokenResult.items[0].status, 'no-key');
  assert.equal(brokenResult.items[0].correct, false);
  assert.equal(brokenResult.scoredCount, 0);
  assert.equal(brokenResult.noKeyCount, 1);
});

test('gradeAll: unreviewed wording, provisional score, written answers not scored', () => {
  const result = gradeAll([mcq('q1', 'unreviewed'), mcq('q2', 'unreviewed'), short('s1'), short('s2')],
    { q1: 'B', q2: 'C', s1: '  my words  ' });
  assert.deepEqual(result.items.map((item) => item.status), ['matches', 'differs', 'recorded', 'unanswered']);
  assert.equal(result.provisional, true);
  assert.equal(result.unreviewedCount, 2);
  assert.equal(result.scoredCount, 2);
  assert.equal(result.shortAnswerCount, 2);
  assert.equal(result.shortUnansweredCount, 1);
  assert.equal(result.items[2].response, 'my words');
  assert.equal(result.unansweredCount, 0, 'unanswered written answers are not counted as unanswered scored questions');
});

test('unansweredNumbers lists the questions still blank', () => {
  const questions = [mcq('q1'), short('s1'), mcq('q2'), mcq('q3')];
  assert.deepEqual(unansweredNumbers(questions, { q1: 'A', s1: '   ', q3: 'Wrong text' }), [2, 3, 4]);
  assert.deepEqual(unansweredNumbers(questions, { q1: 'A', s1: 'x', q2: 'B', q3: 'C' }), []);
});

test('answer keys are checked: a quiz refuses a question without a valid key', () => {
  assert.equal(hasValidAnswerKey(mcq('q1')), true);
  assert.equal(hasValidAnswerKey(short('s1')), true);
  assert.equal(hasValidAnswerKey(Object.assign(mcq('q2'), { answer: 'Z' })), false);
  assert.throws(() => new Quiz([Object.assign(mcq('q2'), { answer: 'Z' })]), /no valid answer key/);
});

test('Quiz results count questions never attempted as unanswered, not correct', () => {
  const quiz = new Quiz([mcq('q1', 'reviewed'), mcq('q2', 'reviewed')], { shuffle: false });
  quiz.submit('B');
  const results = quiz.results();
  assert.equal(results.firstTryMatches, 1);
  assert.equal(results.unansweredCount, 1);
  assert.equal(results.percent, 50);
});

/* ---------- Choosing how many questions ---------- */

function bank(n) {
  return Array.from({ length: n }, (_, i) => ({ id: 'q' + (i + 1) }));
}

test('pickSpread: exactly the number asked for, no question twice, in bank order', () => {
  const questions = bank(158);
  for (const count of [1, 5, 20, 30, 38, 50, 60, 80, 100, 120, 157]) {
    for (let run = 0; run < 50; run++) {
      const picked = pickSpread(questions, count);
      assert.equal(picked.length, count);
      assert.equal(new Set(picked.map((q) => q.id)).size, count, 'no duplicates');
      const positions = picked.map((q) => questions.indexOf(q));
      assert.deepEqual(positions, [...positions].sort((a, b) => a - b), 'kept in bank order');
    }
  }
});

test('pickSpread: all (no count, or a count of at least the bank size) gives every question once, in order', () => {
  const questions = bank(158);
  assert.deepEqual(pickSpread(questions, null), questions);
  assert.deepEqual(pickSpread(questions, 158), questions);
  assert.deepEqual(pickSpread(questions, 500), questions);
  assert.notEqual(pickSpread(questions, null), questions, 'a copy, not the same array');
});

test('pickSpread: questions come from every part of the bank, and every question can be chosen', () => {
  const questions = bank(158);
  // 50 of 158: each of the 50 equal parts gives exactly one question.
  const picked = pickSpread(questions, 50);
  for (let part = 0; part < 50; part++) {
    const start = Math.floor(part * 158 / 50);
    const end = Math.floor((part + 1) * 158 / 50);
    const inPart = picked.filter((q) => { const i = questions.indexOf(q); return i >= start && i < end; });
    assert.equal(inPart.length, 1, 'part ' + part);
  }
  // Both the first 38 and the later 120 appear in a 20-question quiz.
  const twenty = pickSpread(questions, 20).map((q) => questions.indexOf(q));
  assert.ok(twenty.some((i) => i < 38) && twenty.some((i) => i >= 38));
  // Lowest and highest random numbers still pick valid questions, and over
  // many runs every question gets chosen at least once.
  assert.equal(pickSpread(questions, 50, () => 0)[0], questions[0]);
  assert.equal(pickSpread(questions, 50, () => 0.9999999)[49], questions[157]);
  const seen = new Set();
  for (let run = 0; run < 2000; run++) pickSpread(questions, 20).forEach((q) => seen.add(q.id));
  assert.equal(seen.size, 158);
});

test('pickSpread: a broken count is refused', () => {
  for (const bad of [0, -1, 2.5, NaN, '20']) {
    assert.throws(() => pickSpread(bank(10), bad), /whole number/);
  }
});

test('parseCount: accepts whole numbers from 1 to the maximum only', () => {
  assert.deepEqual(parseCount('50', 158), { count: 50 });
  assert.deepEqual(parseCount(' 158 ', 158), { count: 158 });
  assert.deepEqual(parseCount('1', 158), { count: 1 });
  assert.deepEqual(parseCount('٥٠', 158), { count: 50 }, 'Arabic-Indic digits');
  assert.deepEqual(parseCount('۶۰', 158), { count: 60 }, 'Eastern Arabic-Indic digits');
  assert.deepEqual(parseCount('', 158), { error: 'empty' });
  assert.deepEqual(parseCount('   ', 158), { error: 'empty' });
  assert.deepEqual(parseCount(null, 158), { error: 'empty' });
  assert.deepEqual(parseCount('0', 158), { error: 'too-small' });
  assert.deepEqual(parseCount('-5', 158), { error: 'too-small' });
  assert.deepEqual(parseCount('159', 158), { error: 'too-big' });
  assert.deepEqual(parseCount('99999999999999999999', 158), { error: 'too-big' });
  for (const bad of ['2.5', 'abc', '1e2', '20 questions', '١٠x', '--3']) {
    assert.deepEqual(parseCount(bad, 158), { error: 'not-whole' }, bad);
  }
});

test('a submitted question cannot be submitted again (no double counting)', () => {
  const quiz = new Quiz([mcq('q1', 'reviewed')], { shuffle: false });
  quiz.submit('B');
  assert.throws(() => quiz.submit('B'), /already been answered/);
  assert.equal(quiz.results().firstTryMatches, 1);
});

/* ---------- Exams by difficulty ---------- */

const { buildExam } = require('../quiz-engine.js');

function levelled(easy, medium, hard, none = 0) {
  const list = [];
  const add = (n, level) => { for (let i = 0; i < n; i++) list.push({ id: (level || 'none') + i, difficulty: level }); };
  add(easy, 'easy'); add(medium, 'medium'); add(hard, 'hard'); add(none, undefined);
  return list;
}

test('buildExam: one level gives only that level, the number asked for, no repeats', () => {
  const bank = levelled(59, 96, 33);
  for (const level of ['easy', 'medium', 'hard']) {
    for (const count of [10, 15, 20, 30]) {
      const exam = buildExam(bank, { level, count });
      assert.equal(exam.questions.length, count);
      assert.ok(exam.questions.every((q) => q.difficulty === level));
      assert.equal(new Set(exam.questions.map((q) => q.id)).size, count);
      assert.equal(exam.adjusted, false);
    }
  }
});

test('buildExam: mixed takes questions from every level, in proportion', () => {
  const bank = levelled(59, 96, 33);
  for (const count of [3, 10, 15, 20, 30, 100]) {
    for (let run = 0; run < 30; run++) {
      const exam = buildExam(bank, { level: 'mixed', count });
      const levels = exam.questions.map((q) => q.difficulty);
      assert.equal(exam.questions.length, count);
      assert.equal(new Set(exam.questions.map((q) => q.id)).size, count, 'no repeats');
      for (const level of ['easy', 'medium', 'hard']) assert.ok(levels.includes(level), count + ' has ' + level);
    }
  }
  const twenty = buildExam(bank, { level: 'mixed', count: 20 }).questions;
  const counted = (level) => twenty.filter((q) => q.difficulty === level).length;
  assert.deepEqual([counted('easy'), counted('medium'), counted('hard')], [6, 10, 4], 'shares follow the bank: 59/96/33 of 188');
  // Fewer questions than levels: no level is forced in, still the right number.
  assert.equal(buildExam(bank, { level: 'mixed', count: 2 }).questions.length, 2);
  // A level with very few questions still gets one.
  const lopsided = buildExam(levelled(100, 100, 1), { level: 'mixed', count: 10 }).questions;
  assert.ok(lopsided.some((q) => q.difficulty === 'hard'));
  assert.equal(lopsided.length, 10);
  // Questions without a level are part of a mixed exam too.
  assert.equal(buildExam(levelled(3, 3, 3, 3), { level: 'mixed', count: null }).questions.length, 12);
});

test('buildExam: all questions, or more than there are, gives every question once (adjusted when too many)', () => {
  const bank = levelled(59, 96, 33);
  const all = buildExam(bank, { level: 'mixed', count: null });
  assert.equal(all.questions.length, 188);
  assert.deepEqual(all.questions.map((q) => q.id).sort(), bank.map((q) => q.id).sort());
  assert.equal(all.adjusted, false);
  const hard = buildExam(bank, { level: 'hard', count: 50 });
  assert.equal(hard.questions.length, 33);
  assert.ok(hard.questions.every((q) => q.difficulty === 'hard'));
  assert.deepEqual([hard.adjusted, hard.available, hard.requested], [true, 33, 50]);
  const allHard = buildExam(bank, { level: 'hard', count: null });
  assert.deepEqual([allHard.questions.length, allHard.adjusted], [33, false]);
  const none = buildExam(levelled(5, 0, 0), { level: 'hard', count: 10 });
  assert.deepEqual([none.questions.length, none.available, none.adjusted], [0, 0, true]);
});

test('buildExam: the order is random, so two exams of all questions differ', () => {
  const bank = levelled(59, 96, 33);
  const a = buildExam(bank, { level: 'mixed', count: null }).questions.map((q) => q.id);
  const b = buildExam(bank, { level: 'mixed', count: null }).questions.map((q) => q.id);
  assert.notDeepEqual(a, b);
  assert.notDeepEqual(a, bank.map((q) => q.id));
  assert.throws(() => buildExam(bank, { level: 'easy', count: 0 }), /whole number/);
});
