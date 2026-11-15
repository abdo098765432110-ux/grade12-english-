/* ==========================================================================
   «الدكتور والمزارع» — the Biology game's rules (no drawing, no page code).

   Used by bio-game.js in the browser and by tests/bio-game.test.js in Node.

   The content (bio-game-ch1.json, bio-game-ch2.json):
     tracks  the places of a chapter (hospital, farm), each with levels 1–6
     ideas   one idea of the book each (for example "وتر أكيليس")
     cases   situations that test one idea at one level; a case has several
             stories (different people and events) and more wrong choices than
             are shown, so the same case does not look the same twice

   The levels go from easy to hard:
     1 تعرّف   2 وظيفة   3 حالة   4 فرّق   5 لو حصل…   6 اربط

   Mastery ("الفرم"):
     - every idea has up to 3 stars;
     - a right answer gives the idea a star, but at most one star per idea
       in one shift (so the stars come on different sittings) and never twice
       in a row from the same case (so they come from different forms of the
       idea: every idea has 3 cases or more, each with several stories);
     - a wrong answer takes a star away and brings the idea back soon; the
       star can be won back later from another case;
     - a level is passed when every idea of the level was answered right at
       that level.

   Progress is kept in this browser only (localStorage "g12-bio-game"):
   numbers about ideas and cases, nothing about the student.
   ========================================================================== */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.G12 = root.G12 || {};
    root.G12.BioGame = api;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var KEY = 'g12-bio-game';
  var SHIFT_SIZE = 5;
  var MAX_STARS = 3;
  var LEVEL_NAMES = { 1: 'تعرّف', 2: 'وظيفة', 3: 'حالة', 4: 'فرّق', 5: 'لو حصل…', 6: 'اربط' };
  var LEVEL_HINTS = {
    1: 'اعرف الجزء واسمه ومكانه',
    2: 'اعرف بيعمل إيه',
    3: 'شخّص الحالة',
    4: 'فرّق بين حاجتين شبه بعض',
    5: 'توقّع اللي هيحصل',
    6: 'اربط أكتر من فكرة'
  };
  var RANKS = {
    hospital: ['طبيب امتياز', 'طبيب مقيم', 'أخصائي', 'أخصائي أول', 'استشاري', 'استشاري أول', 'رئيس القسم'],
    farm: ['مزارع مبتدئ', 'مزارع', 'مزارع ماهر', 'مهندس زراعي', 'خبير زراعي', 'كبير الخبراء', 'شيخ المزارعين']
  };

  function hasText(value) {
    return typeof value === 'string' && value.trim() !== '';
  }

  /* ---------- Random numbers (a seed gives the same order again) ---------- */

  function rng(seed) {
    if (seed === undefined || seed === null) return Math.random;
    var a = 0;
    String(seed).split('').forEach(function (ch) { a = (a * 31 + ch.charCodeAt(0)) | 0; });
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function shuffle(list, random) {
    var copy = list.slice();
    for (var i = copy.length - 1; i > 0; i--) {
      var j = Math.floor(random() * (i + 1));
      var x = copy[i]; copy[i] = copy[j]; copy[j] = x;
    }
    return copy;
  }

  /* ---------- Checking the content ---------- */

  function caseProblems(item, ideas) {
    var problems = [];
    if (!hasText(item.id)) problems.push('"id" is missing');
    if (!ideas[item.idea]) problems.push('"idea" is not one of the ideas: ' + item.idea);
    if ([1, 2, 3, 4, 5, 6].indexOf(item.level) === -1) problems.push('"level" must be 1 to 6');
    if (!Array.isArray(item.stories) || !item.stories.length) problems.push('"stories" must have at least one story');
    else item.stories.forEach(function (story, i) {
      if (!story || !Array.isArray(story.lines) || !story.lines.length || !story.lines.every(hasText)) problems.push('story ' + (i + 1) + ' has no "lines"');
      if (story && story.who !== undefined && !hasText(story.who)) problems.push('story ' + (i + 1) + ': "who" is empty');
    });
    if (!hasText(item.question)) problems.push('"question" is missing');
    if (!hasText(item.answer)) problems.push('"answer" is missing');
    if (!Array.isArray(item.wrong) || item.wrong.length < 3) problems.push('"wrong" must have at least 3 wrong choices');
    else item.wrong.forEach(function (w, i) {
      if (!w || !hasText(w.text) || !hasText(w.why)) problems.push('wrong choice ' + (i + 1) + ' needs "text" and "why"');
      else if (w.text.trim() === String(item.answer).trim()) problems.push('wrong choice ' + (i + 1) + ' is the same as the answer');
    });
    if (!Array.isArray(item.explain) || !item.explain.length || !item.explain.every(hasText)) problems.push('"explain" must be a list of steps');
    return problems;
  }

  /* Merges the chapter files into one content object and leaves out what is
     broken. Returns { tracks, ideas, cases, problems }. */
  function build(files) {
    var content = { tracks: [], ideas: [], cases: [], problems: [], chapters: [] };
    var trackIds = {};
    var ideaIds = {};
    var caseIds = {};
    files.forEach(function (file, f) {
      if (!file || !Array.isArray(file.tracks) || !Array.isArray(file.ideas) || !Array.isArray(file.cases)) {
        content.problems.push('file ' + (f + 1) + ': it must have "tracks", "ideas" and "cases"');
        return;
      }
      content.chapters.push({ chapter: file.chapter, title: file.title });
      file.tracks.forEach(function (track) {
        if (!track || !hasText(track.id) || trackIds[track.id] || (track.place !== 'hospital' && track.place !== 'farm')) {
          content.problems.push('chapter ' + file.chapter + ': a track has no id, a repeated id or a wrong "place"');
          return;
        }
        var copy = {};
        Object.keys(track).forEach(function (k) { copy[k] = track[k]; });
        copy.chapter = file.chapter;
        trackIds[track.id] = copy;
        content.tracks.push(copy);
      });
      file.ideas.forEach(function (idea) {
        if (!idea || !hasText(idea.id) || ideaIds[idea.id] || !trackIds[idea.track] || !hasText(idea.name)) {
          content.problems.push('chapter ' + file.chapter + ': idea "' + (idea && idea.id) + '" has no name, a repeated id or an unknown track');
          return;
        }
        ideaIds[idea.id] = idea;
        content.ideas.push(idea);
      });
      file.cases.forEach(function (item) {
        var problems = item ? caseProblems(item, ideaIds) : ['it is empty'];
        if (item && caseIds[item.id]) problems.push('the "id" is repeated');
        if (problems.length) {
          problems.forEach(function (p) { content.problems.push('case "' + (item && item.id) + '": ' + p); });
          return;
        }
        caseIds[item.id] = true;
        var copy = {};
        Object.keys(item).forEach(function (k) { copy[k] = item[k]; });
        copy.track = ideaIds[item.idea].track;
        content.cases.push(copy);
      });
    });
    return content;
  }

  /* Look-ups used everywhere. */
  function index(content) {
    var idx = { content: content, tracks: {}, ideas: {}, cases: {}, levels: {}, ideasAt: {} };
    content.tracks.forEach(function (t) { idx.tracks[t.id] = t; idx.levels[t.id] = []; idx.ideasAt[t.id] = {}; });
    content.ideas.forEach(function (i) { idx.ideas[i.id] = i; });
    content.cases.forEach(function (c) {
      idx.cases[c.id] = c;
      var levels = idx.levels[c.track];
      if (levels.indexOf(c.level) === -1) levels.push(c.level);
      var at = idx.ideasAt[c.track];
      at[c.level] = at[c.level] || [];
      if (at[c.level].indexOf(c.idea) === -1) at[c.level].push(c.idea);
    });
    Object.keys(idx.levels).forEach(function (t) { idx.levels[t].sort(function (a, b) { return a - b; }); });
    return idx;
  }

  /* ---------- Progress ---------- */

  function emptyState() {
    return { v: 1, shift: 0, ideas: {}, cases: {}, cleared: {}, done: {}, answers: 0, right: 0, daily: {}, exam: {} };
  }

  function storage(store) {
    if (store) return store;
    try {
      return typeof localStorage !== 'undefined' ? localStorage : null;
    } catch (error) {
      return null;
    }
  }

  function load(store) {
    try {
      var target = storage(store);
      var raw = target && target.getItem(KEY);
      var data = raw ? JSON.parse(raw) : null;
      if (!data || typeof data !== 'object' || data.v !== 1) return emptyState();
      var state = emptyState();
      Object.keys(state).forEach(function (k) {
        if (data[k] !== undefined && typeof data[k] === typeof state[k]) state[k] = data[k];
      });
      return state;
    } catch (error) {
      return emptyState();
    }
  }

  function save(state, store) {
    try {
      var target = storage(store);
      if (!target) return false;
      target.setItem(KEY, JSON.stringify(state));
      return true;
    } catch (error) {
      return false;
    }
  }

  function ideaState(state, id) {
    if (!state.ideas[id]) state.ideas[id] = { stars: 0, weak: false, wrong: 0, seen: 0, starShift: -1, starCase: '', lastShift: -1 };
    return state.ideas[id];
  }

  function stars(state, id) {
    return state.ideas[id] ? state.ideas[id].stars : 0;
  }

  /* ---------- Levels ---------- */

  function levelIdeas(idx, trackId, level) {
    return (idx.ideasAt[trackId] && idx.ideasAt[trackId][level]) || [];
  }

  function isCleared(state, trackId, level, ideaId) {
    return !!(state.cleared[trackId] && state.cleared[trackId][level] && state.cleared[trackId][level][ideaId]);
  }

  function levelCleared(idx, state, trackId, level) {
    var ideas = levelIdeas(idx, trackId, level);
    return ideas.length > 0 && ideas.every(function (id) { return isCleared(state, trackId, level, id); });
  }

  /* The first level not passed yet, or null when all are passed. */
  function currentLevel(idx, state, trackId) {
    var levels = idx.levels[trackId] || [];
    for (var i = 0; i < levels.length; i++) {
      if (!levelCleared(idx, state, trackId, levels[i])) return levels[i];
    }
    return null;
  }

  function trackProgress(idx, state, trackId) {
    var levels = idx.levels[trackId] || [];
    var passed = levels.filter(function (l) { return levelCleared(idx, state, trackId, l); }).length;
    var level = currentLevel(idx, state, trackId);
    var ideas = level === null ? [] : levelIdeas(idx, trackId, level);
    var track = idx.tracks[trackId];
    var ranks = RANKS[track.place];
    var trackIdeas = idx.content.ideas.filter(function (i) { return i.track === trackId; });
    var starSum = trackIdeas.reduce(function (sum, i) { return sum + stars(state, i.id); }, 0);
    return {
      levels: levels,
      passed: passed,
      level: level,
      levelIdeas: ideas.length,
      levelCleared: ideas.filter(function (id) { return isCleared(state, trackId, level, id); }).length,
      rank: ranks[Math.min(passed, ranks.length - 1)],
      ideas: trackIdeas.length,
      mastered: trackIdeas.filter(function (i) { return stars(state, i.id) >= MAX_STARS; }).length,
      percent: trackIdeas.length ? Math.round((starSum / (trackIdeas.length * MAX_STARS)) * 100) : 0,
      done: level === null && levels.length > 0
    };
  }

  function overall(idx, state) {
    var ideas = idx.content.ideas;
    var starSum = ideas.reduce(function (sum, i) { return sum + stars(state, i.id); }, 0);
    return {
      ideas: ideas.length,
      mastered: ideas.filter(function (i) { return stars(state, i.id) >= MAX_STARS; }).length,
      percent: ideas.length ? Math.round((starSum / (ideas.length * MAX_STARS)) * 100) : 0
    };
  }

  /* ---------- Building a shift ---------- */

  function caseRank(state, c) {
    // cases never answered right come first, then the ones seen longest ago
    var s = state.cases[c.id];
    return (s && s.right ? 1000 : 0) + (s ? s.lastShift + 1 : 0);
  }

  function pickCase(cases, state, random) {
    if (!cases.length) return null;
    var ranked = shuffle(cases, random).sort(function (a, b) { return caseRank(state, a) - caseRank(state, b); });
    return ranked[0];
  }

  /* How one case is shown: which story, which wrong choices, in which order. */
  function present(c, state, random) {
    var s = state.cases[c.id];
    var stories = c.stories.map(function (_, i) { return i; });
    if (s && stories.length > 1) stories = stories.filter(function (i) { return i !== s.story; });
    var story = stories[Math.floor(random() * stories.length)];
    var wrong = shuffle(c.wrong.map(function (_, i) { return i; }), random).slice(0, 3);
    var choices = shuffle([{ right: true }].concat(wrong.map(function (i) { return { wrong: i }; })), random);
    return { caseId: c.id, story: story, choices: choices };
  }

  /* A shift: up to 5 cases from the current level (ideas not passed first,
     the ones answered wrong before all others) and one case for review from
     an earlier level when there is one. After the last level: review only. */
  function newShift(idx, state, trackId, seed) {
    var random = rng(seed);
    var level = currentLevel(idx, state, trackId);
    var all = idx.content.cases.filter(function (c) { return c.track === trackId; });
    var picked = [];
    var usedIdeas = {};

    function take(c) {
      if (!c) return;
      picked.push(c);
      usedIdeas[c.idea] = true;
    }

    if (level === null) {
      // every level passed: review the weakest ideas of the track
      var ideas = shuffle(Object.keys(all.reduce(function (m, c) { m[c.idea] = true; return m; }, {})), random)
        .sort(function (a, b) { return stars(state, a) - stars(state, b); });
      ideas.slice(0, SHIFT_SIZE).forEach(function (id) {
        take(pickCase(all.filter(function (c) { return c.idea === id; }), state, random));
      });
      return { track: trackId, level: null, items: shuffle(picked, random).map(function (c) { return present(c, state, random); }) };
    }

    var atLevel = all.filter(function (c) { return c.level === level; });
    var open = levelIdeas(idx, trackId, level).filter(function (id) { return !isCleared(state, trackId, level, id); });
    open = shuffle(open, random).sort(function (a, b) {
      var wa = state.ideas[a] && state.ideas[a].weak ? 0 : 1;
      var wb = state.ideas[b] && state.ideas[b].weak ? 0 : 1;
      return wa - wb;
    });

    // one place for review from the earlier levels
    var earlier = all.filter(function (c) { return c.level < level; });
    var reviewIdeas = shuffle(Object.keys(earlier.reduce(function (m, c) { m[c.idea] = true; return m; }, {})), random)
      .filter(function (id) { return stars(state, id) < MAX_STARS; })
      .sort(function (a, b) {
        var ia = state.ideas[a] || {};
        var ib = state.ideas[b] || {};
        return ((ia.weak ? 0 : 10) + (ia.stars || 0)) - ((ib.weak ? 0 : 10) + (ib.stars || 0));
      });
    var room = SHIFT_SIZE - (reviewIdeas.length ? 1 : 0);

    open.slice(0, room).forEach(function (id) {
      take(pickCase(atLevel.filter(function (c) { return c.idea === id; }), state, random));
    });
    if (reviewIdeas.length) {
      var rid = reviewIdeas[0];
      take(pickCase(earlier.filter(function (c) { return c.idea === rid && !usedIdeas[c.idea]; }), state, random));
    }
    // fill the shift with other cases of this level (ideas with fewer stars first)
    var rest = shuffle(atLevel.filter(function (c) { return picked.indexOf(c) === -1; }), random)
      .sort(function (a, b) {
        var ua = usedIdeas[a.idea] ? 1 : 0;
        var ub = usedIdeas[b.idea] ? 1 : 0;
        return (ua - ub) || (stars(state, a.idea) - stars(state, b.idea)) || (caseRank(state, a) - caseRank(state, b));
      });
    while (picked.length < SHIFT_SIZE && rest.length) take(rest.shift());

    return { track: trackId, level: level, items: shuffle(picked, random).map(function (c) { return present(c, state, random); }) };
  }

  /* ---------- Answering ---------- */

  function startShift(state) {
    state.shift += 1;
    return state.shift;
  }

  /* Records one answer. Returns what changed: { right, starsBefore, starsAfter,
     clearedNow } (clearedNow: the idea was just passed at this level). */
  function answer(idx, state, item, right) {
    var c = idx.cases[item.caseId];
    var idea = ideaState(state, c.idea);
    var record = state.cases[c.id] || { seen: 0, right: 0, wrong: 0, lastShift: -1, story: -1 };
    var before = idea.stars;
    var clearedNow = false;
    record.seen += 1;
    record.lastShift = state.shift;
    record.story = item.story;
    idea.seen += 1;
    idea.lastShift = state.shift;
    state.answers += 1;
    if (right) {
      state.right += 1;
      var onlyCase = Object.keys(idx.cases).filter(function (id) { return idx.cases[id].idea === c.idea; }).length < 2;
      if (idea.starShift !== state.shift && idea.stars < MAX_STARS && (idea.starCase !== c.id || onlyCase)) {
        idea.stars += 1;
        idea.starShift = state.shift;
        idea.starCase = c.id;
      }
      record.right += 1;
      idea.weak = false;
      state.cleared[c.track] = state.cleared[c.track] || {};
      state.cleared[c.track][c.level] = state.cleared[c.track][c.level] || {};
      if (!state.cleared[c.track][c.level][c.idea]) {
        state.cleared[c.track][c.level][c.idea] = true;
        clearedNow = true;
      }
    } else {
      record.wrong += 1;
      idea.wrong += 1;
      idea.weak = true;
      if (idea.stars > 0) idea.stars -= 1;
    }
    state.cases[c.id] = record;
    return { right: right, starsBefore: before, starsAfter: idea.stars, clearedNow: clearedNow, idea: c.idea };
  }

  /* ---------- The daily challenge, the final exam, the album ---------- */

  var DAILY_SIZE = 5;
  var EXAM_SIZE = 20;
  var PASS = 85;   // percent for the certificate

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function dayOf(date) {
    var d = date || new Date();
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }

  function seedOf(text) {
    var h = 2166136261;
    for (var i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }

  /* Cases from several places, one per idea, taking turns between the places. */
  function mixedShift(idx, state, cases, size, random, kind) {
    var byTrack = {};
    cases.forEach(function (c) { (byTrack[c.track] = byTrack[c.track] || []).push(c); });
    var tracks = shuffle(Object.keys(byTrack), random);
    tracks.forEach(function (t) { byTrack[t] = shuffle(byTrack[t], random); });
    var picked = [];
    var used = {};
    var moved = true;
    while (picked.length < size && moved) {
      moved = false;
      tracks.forEach(function (t) {
        if (picked.length >= size) return;
        var list = byTrack[t];
        while (list.length && used[list[0].idea]) list.shift();
        if (list.length) {
          var c = list.shift();
          used[c.idea] = true;
          picked.push(c);
          moved = true;
        }
      });
    }
    return { kind: kind, track: null, level: null, items: shuffle(picked, random).map(function (c) { return present(c, state, random); }) };
  }

  /* The same 5 cases all day: from the levels the student has reached in every place. */
  function dailyShift(idx, state, day) {
    var random = rng(seedOf('daily-' + (day || dayOf())));
    var cases = idx.content.cases.filter(function (c) {
      var level = currentLevel(idx, state, c.track);
      return level === null || c.level <= level;
    });
    return mixedShift(idx, state, cases, DAILY_SIZE, random, 'daily');
  }

  /* 20 harder cases (levels 3 to 6) from every place of both chapters. */
  function examShift(idx, state, seed) {
    var random = rng(seed === undefined ? Date.now() : seed);
    var cases = idx.content.cases.filter(function (c) { return c.level >= 3; });
    return mixedShift(idx, state, cases, EXAM_SIZE, random, 'exam');
  }

  function finishDaily(state, day, right, total) {
    day = day || dayOf();
    var before = state.daily || {};
    var yesterday = dayOf(new Date(new Date(day + 'T12:00:00').getTime() - 864e5));
    var streak = before.day === day ? (before.streak || 1) : (before.day === yesterday ? (before.streak || 0) + 1 : 1);
    state.daily = { day: day, right: right, total: total, streak: streak };
    return state.daily;
  }

  function finishExam(state, right, total) {
    var percent = total ? Math.round((right / total) * 100) : 0;
    var before = state.exam || {};
    state.exam = { last: percent, best: Math.max(before.best || 0, percent), passed: !!before.passed || percent >= PASS };
    return { percent: percent, passed: percent >= PASS, best: state.exam.best };
  }

  /* The people the student has met (in cases already answered) and how many cases with each. */
  function album(idx, state) {
    var met = {};
    Object.keys(state.cases).forEach(function (id) {
      var c = idx.cases[id];
      var r = state.cases[id];
      if (!c || !r || !r.seen) return;
      var story = c.stories[r.story] || c.stories[0];
      if (!story || !story.who) return;
      met[story.who] = met[story.who] || { cases: 0, right: 0 };
      met[story.who].cases += 1;
      if (r.right) met[story.who].right += 1;
    });
    return met;
  }

  return {
    KEY: KEY,
    DAILY_SIZE: DAILY_SIZE,
    EXAM_SIZE: EXAM_SIZE,
    PASS: PASS,
    dayOf: dayOf,
    dailyShift: dailyShift,
    examShift: examShift,
    finishDaily: finishDaily,
    finishExam: finishExam,
    album: album,
    SHIFT_SIZE: SHIFT_SIZE,
    MAX_STARS: MAX_STARS,
    LEVEL_NAMES: LEVEL_NAMES,
    LEVEL_HINTS: LEVEL_HINTS,
    RANKS: RANKS,
    rng: rng,
    shuffle: shuffle,
    caseProblems: caseProblems,
    build: build,
    index: index,
    emptyState: emptyState,
    load: load,
    save: save,
    stars: stars,
    levelIdeas: levelIdeas,
    isCleared: isCleared,
    levelCleared: levelCleared,
    currentLevel: currentLevel,
    trackProgress: trackProgress,
    overall: overall,
    newShift: newShift,
    present: present,
    startShift: startShift,
    answer: answer
  };
});
