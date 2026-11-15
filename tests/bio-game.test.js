/* Tests for «الدكتور والمزارع» (bio-game-engine.js, bio-game-art*.js and bio-game-ch*.json).
   Run with: node --test tests/bio-game.test.js */
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const E = require('../bio-game-engine.js');

const PROJECT = path.join(__dirname, '..');
const FILES = ['bio-game-ch1.json', 'bio-game-ch2.json'];

function readJSON(name) {
  return JSON.parse(fs.readFileSync(path.join(PROJECT, name), 'utf8'));
}

function realContent() {
  return E.build(FILES.map(readJSON));
}

/* The drawings run in a small sandbox with a "window", as in the browser. */
function loadArt() {
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  fs.readdirSync(PROJECT).filter((f) => /^bio-game-art.*\.js$/.test(f)).sort((a, b) => a.length - b.length).forEach((f) => {
    vm.runInContext(fs.readFileSync(path.join(PROJECT, f), 'utf8'), sandbox, { filename: f });
  });
  return sandbox.window.G12.BioArt;
}

/* A tiny made-up content: one track, 2 ideas, levels 1 and 2. */
function testContent() {
  const kase = (id, idea, level) => ({
    id, idea, level, type: 'lesson',
    stories: [{ who: 'murad', lines: ['Test line one'] }, { who: 'ziad', lines: ['Test line two'] }],
    question: 'Test question?', answer: 'Test answer',
    wrong: [{ text: 'Test wrong one', why: 'Test why' }, { text: 'Test wrong two', why: 'Test why' }, { text: 'Test wrong three', why: 'Test why' }, { text: 'Test wrong four', why: 'Test why' }],
    explain: ['Test step']
  });
  return E.build([{
    chapter: 1, title: 'Test chapter',
    tracks: [{ id: 't', place: 'hospital', name: 'Test track' }],
    ideas: [{ id: 'a', track: 't', name: 'Test idea A' }, { id: 'b', track: 't', name: 'Test idea B' }],
    cases: [kase('a1', 'a', 1), kase('a2', 'a', 1), kase('a3', 'a', 2), kase('b1', 'b', 1), kase('b2', 'b', 2), kase('b3', 'b', 2)]
  }]);
}

function memoryStore() {
  const data = {};
  return { getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = String(v); } };
}

/* ---------- The real content ---------- */

test('the content files load with no problems', () => {
  const content = realContent();
  assert.deepEqual(content.problems, []);
  assert.ok(content.cases.length > 0);
});

test('every idea has at least 3 cases, so 3 stars can always be won from different forms', () => {
  const content = realContent();
  content.ideas.forEach((idea) => {
    const n = content.cases.filter((c) => c.idea === idea.id).length;
    assert.ok(n >= 3, idea.id + ' has ' + n + ' cases');
  });
});

test('every case: 2 stories or more, 4 wrong choices or more, an explanation, no wrong choice equal to the answer', () => {
  realContent().cases.forEach((c) => {
    assert.ok(c.stories.length >= 2, c.id + ': stories');
    assert.ok(c.wrong.length >= 4, c.id + ': wrong choices');
    assert.ok(c.explain.length >= 2, c.id + ': explanation');
    const texts = c.wrong.map((w) => w.text.trim());
    assert.equal(new Set(texts).size, texts.length, c.id + ': repeated wrong choice');
    assert.ok(!texts.includes(c.answer.trim()), c.id + ': a wrong choice is the answer');
  });
});

test('every track has levels from 1 up, without gaps', () => {
  const content = realContent();
  const idx = E.index(content);
  content.tracks.forEach((t) => {
    const levels = idx.levels[t.id];
    if (!levels.length) return;
    levels.forEach((l, i) => assert.equal(l, i + 1, t.id + ': level ' + (i + 1) + ' is missing'));
  });
});

test('every person and every picture used by a case exists and draws', () => {
  const A = loadArt();
  realContent().cases.forEach((c) => {
    c.stories.forEach((s) => {
      assert.ok(A.CAST[s.who], c.id + ': unknown person ' + s.who);
      assert.ok(A.scene({ who: s.who, bg: s.bg || 'clinic', mood: s.mood || 'neutral' }).length > 500);
    });
    [c.exam, c.after].filter(Boolean).forEach((v) => {
      assert.ok(A.views[v.view], c.id + ': unknown picture ' + v.view);
      const svg = A.view(v.view, Object.assign({}, v.opts, { labels: true }));
      assert.match(svg, /^<svg [^>]*viewBox="0 0 480 320"/, c.id + ': ' + v.view);
      assert.doesNotMatch(svg, /<title>/, c.id + ': ' + v.view + ' has a <title> (an English tooltip)');
    });
  });
});

/* ---------- The rules ---------- */

test('a shift has up to 5 cases from the current level, each shown with 4 choices', () => {
  const content = testContent();
  const idx = E.index(content);
  const state = E.emptyState();
  E.startShift(state);
  const shift = E.newShift(idx, state, 't', 1);
  assert.equal(shift.level, 1);
  assert.ok(shift.items.length >= 2 && shift.items.length <= E.SHIFT_SIZE);
  shift.items.forEach((item) => {
    assert.equal(idx.cases[item.caseId].level, 1);
    assert.equal(item.choices.length, 4);
    assert.equal(item.choices.filter((ch) => ch.right).length, 1);
  });
});

test('at most one star per idea in a shift, and never twice in a row from the same case', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  assert.equal(E.answer(idx, state, { caseId: 'a1', story: 0 }, true).starsAfter, 1);
  assert.equal(E.answer(idx, state, { caseId: 'a2', story: 0 }, true).starsAfter, 1, 'second star in the same shift');
  E.startShift(state);
  assert.equal(E.answer(idx, state, { caseId: 'a1', story: 1 }, true).starsAfter, 1, 'same case gave the star last time');
  assert.equal(E.answer(idx, state, { caseId: 'a2', story: 1 }, true).starsAfter, 2);
});

test('a wrong answer takes a star away, marks the idea weak, and the star can be won back', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a1', story: 0 }, true);
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a2', story: 0 }, true);
  assert.equal(E.stars(state, 'a'), 2);
  E.startShift(state);
  const r = E.answer(idx, state, { caseId: 'a3', story: 0 }, false);
  assert.equal(r.starsAfter, 1);
  assert.equal(state.ideas.a.weak, true);
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a3', story: 1 }, true);
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a1', story: 1 }, true);
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a2', story: 1 }, true);
  assert.equal(E.stars(state, 'a'), 3, 'mastery is reachable again after a mistake');
  assert.equal(state.ideas.a.weak, false);
});

test('a level is passed when every idea of it was answered right at that level; then the next level opens', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  assert.equal(E.currentLevel(idx, state, 't'), 1);
  E.answer(idx, state, { caseId: 'a1', story: 0 }, true);
  assert.equal(E.currentLevel(idx, state, 't'), 1);
  E.answer(idx, state, { caseId: 'b1', story: 0 }, true);
  assert.equal(E.currentLevel(idx, state, 't'), 2);
  const shift = E.newShift(idx, state, 't', 2);
  assert.equal(shift.level, 2);
  assert.ok(shift.items.some((item) => idx.cases[item.caseId].level === 2));
  const p = E.trackProgress(idx, state, 't');
  assert.equal(p.passed, 1);
  assert.equal(p.rank, E.RANKS.hospital[1]);
});

test('every level is open: the student can start at any level, or a review', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  const shift = E.newShift(idx, state, 't', 4, 2);
  assert.equal(shift.level, 2, 'level 2 chosen before level 1 is passed');
  assert.ok(shift.items.some((item) => idx.cases[item.caseId].level === 2));
  const review = E.newShift(idx, state, 't', 4, 'review');
  assert.equal(review.level, null);
  assert.ok(review.items.length > 0);
  assert.equal(E.newShift(idx, state, 't', 4, 9).level, 1, 'a level that does not exist falls back to the first open one');
});

test('a wrong idea comes first in the next shift', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  E.answer(idx, state, { caseId: 'b1', story: 0 }, false);
  E.startShift(state);
  const shift = E.newShift(idx, state, 't', 7);
  assert.ok(shift.items.some((item) => idx.cases[item.caseId].idea === 'b'));
});

test('the same case is told with another story the next time', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a1', story: 0 }, false);
  for (let seed = 1; seed < 20; seed++) {
    assert.equal(E.present(idx.cases.a1, state, E.rng(seed)).story, 1);
  }
});

test('after the last level the shifts review the ideas with the fewest stars', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  ['a1', 'b1', 'a3', 'b2'].forEach((id) => E.answer(idx, state, { caseId: id, story: 0 }, true));
  assert.equal(E.currentLevel(idx, state, 't'), null);
  assert.equal(E.trackProgress(idx, state, 't').done, true);
  const shift = E.newShift(idx, state, 't', 3);
  assert.equal(shift.level, null);
  assert.ok(shift.items.length > 0);
});

test('progress is saved and loaded; broken or old saves start empty', () => {
  const idx = E.index(testContent());
  const store = memoryStore();
  const state = E.emptyState();
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a1', story: 0 }, true);
  assert.equal(E.save(state, store), true);
  assert.equal(E.stars(E.load(store), 'a'), 1);
  store.setItem(E.KEY, '{broken');
  assert.deepEqual(E.load(store), E.emptyState());
  store.setItem(E.KEY, JSON.stringify({ v: 99 }));
  assert.deepEqual(E.load(store), E.emptyState());
});

test('the saved progress has numbers about ideas and cases only, nothing about the student', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a1', story: 0 }, true);
  E.finishDaily(state, '2026-11-15', 4, 5);
  E.finishExam(state, 17, 20);
  assert.deepEqual(Object.keys(state).sort(), ['answers', 'cases', 'cleared', 'daily', 'done', 'exam', 'ideas', 'right', 'shift', 'v']);
  assert.deepEqual(Object.keys(state.daily).sort(), ['day', 'right', 'streak', 'total']);
  assert.deepEqual(Object.keys(state.exam).sort(), ['best', 'last', 'passed']);
});

test('the daily challenge: the same cases all day, from several places, one per idea; the streak counts days in a row', () => {
  const idx = E.index(realContent());
  const state = E.emptyState();
  const a = E.dailyShift(idx, state, '2026-11-15').items.map((i) => i.caseId);
  const b = E.dailyShift(idx, state, '2026-11-15').items.map((i) => i.caseId);
  const c = E.dailyShift(idx, state, '2026-11-16').items.map((i) => i.caseId);
  assert.deepEqual(a.slice().sort(), b.slice().sort());
  assert.notDeepEqual(a.slice().sort(), c.slice().sort());
  assert.equal(a.length, E.DAILY_SIZE);
  assert.equal(new Set(a.map((id) => idx.cases[id].idea)).size, a.length);
  assert.ok(new Set(a.map((id) => idx.cases[id].track)).size >= 2);
  assert.equal(E.finishDaily(state, '2026-11-15', 3, 5).streak, 1);
  assert.equal(E.finishDaily(state, '2026-11-15', 5, 5).streak, 1, 'again the same day');
  assert.equal(E.finishDaily(state, '2026-11-16', 4, 5).streak, 2);
  assert.equal(E.finishDaily(state, '2026-11-18', 4, 5).streak, 1, 'a day was missed');
});

test('the final exam: 20 cases of levels 3 to 6 from every place; 85% or more passes and is remembered', () => {
  const idx = E.index(realContent());
  const state = E.emptyState();
  const exam = E.examShift(idx, state, 7);
  assert.equal(exam.items.length, E.EXAM_SIZE);
  assert.ok(exam.items.every((i) => idx.cases[i.caseId].level >= 3));
  assert.equal(new Set(exam.items.map((i) => idx.cases[i.caseId].idea)).size, E.EXAM_SIZE);
  assert.equal(new Set(exam.items.map((i) => idx.cases[i.caseId].track)).size, idx.content.tracks.length);
  assert.deepEqual(E.finishExam(state, 16, 20), { percent: 80, passed: false, best: 80 });
  assert.deepEqual(E.finishExam(state, 18, 20), { percent: 90, passed: true, best: 90 });
  E.finishExam(state, 10, 20);
  assert.equal(state.exam.best, 90);
  assert.equal(state.exam.passed, true);
});

test('the album counts the people met in answered cases', () => {
  const idx = E.index(testContent());
  const state = E.emptyState();
  E.startShift(state);
  E.answer(idx, state, { caseId: 'a1', story: 1 }, true);
  E.answer(idx, state, { caseId: 'b1', story: 1 }, false);
  E.answer(idx, state, { caseId: 'a2', story: 0 }, true);
  assert.deepEqual(E.album(idx, state), { ziad: { cases: 2, right: 1 }, murad: { cases: 1, right: 1 } });
});

test('no female character in the cast', () => {
  const A = loadArt();
  const roles = Object.keys(A.CAST).map((k) => A.CAST[k].name + ' ' + A.CAST[k].role);
  roles.forEach((r) => assert.doesNotMatch(r, /(دكتورة|مدرسة|ممرضة|ست |بنت|طالبة|مزارعة|أم |أخت)/, r));
});

test('broken content is reported, not used', () => {
  const content = E.build([{ chapter: 1, title: 'Test', tracks: [{ id: 't', place: 'hospital', name: 'Test' }], ideas: [{ id: 'a', track: 't', name: 'Test' }],
    cases: [{ id: 'x', idea: 'a', level: 9, stories: [], question: '', answer: 'Test', wrong: [{ text: 'Test', why: 'Test' }], explain: [] }] }]);
  assert.equal(content.cases.length, 0);
  assert.ok(content.problems.length >= 4);
});
