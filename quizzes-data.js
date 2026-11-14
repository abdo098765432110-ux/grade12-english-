/* ==========================================================================
   Quizzes: the five subjects, reading and checking the quiz files, and the
   last score saved in this browser.

   One module, used in three places:
     - quizzes.js  (the Quizzes pages: quizzes.html and quiz.html)
     - home.js     (the number of quizzes on the home page card)
     - tests/quizzes.test.js (Node: checks every quiz file)

   The quizzes are in one JSON file per subject, at the top level next to
   index.html: quizzes-arabic.json, quizzes-english.json,
   quizzes-physics.json, quizzes-chemistry.json, quizzes-biology.json.
   The format is explained in README.md ("Quizzes").

   A question that is incomplete or has a mistake is not shown (the others
   still are); the reason is written to the browser console, so the person
   editing the file can find it.
   ========================================================================== */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.G12 = root.G12 || {};
    root.G12.Quizzes = api;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* Same order and colours as the subject menu in the header. Subject names
     are Arabic in both interface languages, like the rest of the website. */
  var SUBJECTS = [
    { id: 'arabic', name: 'اللغة العربية', icon: 'subject-arabic.svg', tone: 'tone-peach', file: 'quizzes-arabic.json', lang: 'ar' },
    { id: 'english', name: 'اللغة الإنجليزية', icon: 'subject-english.svg', tone: 'tone-sky', file: 'quizzes-english.json', lang: 'en' },
    { id: 'physics', name: 'الفيزياء', icon: 'subject-physics.svg', tone: 'tone-lavender', file: 'quizzes-physics.json', lang: 'ar' },
    { id: 'chemistry', name: 'الكيمياء', icon: 'subject-chemistry.svg', tone: 'tone-sun', file: 'quizzes-chemistry.json', lang: 'ar' },
    { id: 'biology', name: 'الأحياء', icon: 'subject-biology.svg', tone: 'tone-mint', file: 'quizzes-biology.json', lang: 'ar' }
  ];

  /* Values for "difficulty" (the interface translates them). */
  var DIFFICULTIES = ['Easy', 'Medium', 'Hard', 'Very Hard'];
  var MIN_OPTIONS = 2;
  var MAX_OPTIONS = 6;
  var SCORES_KEY = 'g12-quiz-scores';

  function hasText(value) {
    return typeof value === 'string' && value.trim() !== '';
  }

  function subject(id) {
    for (var i = 0; i < SUBJECTS.length; i++) if (SUBJECTS[i].id === id) return SUBJECTS[i];
    return null;
  }

  /* The steps of an explanation: a text (one step per line) or a list of texts. */
  function steps(explanation) {
    if (Array.isArray(explanation)) return explanation.filter(hasText);
    if (hasText(explanation)) return explanation.split('\n').filter(hasText);
    return [];
  }

  /* Problems with one question, as English sentences ([] when it is fine). */
  function questionProblems(question) {
    var problems = [];
    if (!question || typeof question !== 'object' || Array.isArray(question)) return ['it is not an object { … }'];
    if (!hasText(question.id)) problems.push('"id" is missing');
    if (!hasText(question.skill)) problems.push('"skill" is missing');
    if (!hasText(question.question)) problems.push('"question" is missing');
    var options = question.options;
    if (!Array.isArray(options) || options.length < MIN_OPTIONS || options.length > MAX_OPTIONS) {
      problems.push('"options" must be a list of ' + MIN_OPTIONS + ' to ' + MAX_OPTIONS + ' choices (usually 4)');
    } else {
      if (!options.every(hasText)) problems.push('every choice in "options" must be a text');
      var seen = {};
      options.forEach(function (option) {
        if (hasText(option)) {
          var key = option.trim();
          if (seen[key]) problems.push('two choices are the same: ' + key);
          seen[key] = true;
        }
      });
      if (typeof question.correctIndex !== 'number' || question.correctIndex % 1 !== 0 ||
          question.correctIndex < 0 || question.correctIndex >= options.length) {
        problems.push('"correctIndex" must be the number of the correct choice, counting from 0 (0 to ' + (options.length - 1) + ')');
      }
      if (question.whyWrong !== undefined) {
        if (!Array.isArray(question.whyWrong) || question.whyWrong.length !== options.length ||
            !question.whyWrong.every(function (text) { return typeof text === 'string'; })) {
          problems.push('"whyWrong" must be a list with one text for each choice (use "" for the correct choice)');
        }
      }
    }
    if (!steps(question.explanation).length) problems.push('"explanation" is missing');
    if (question.svg !== undefined) {
      if (!hasText(question.svg) || !/^\s*<svg[\s>]/i.test(question.svg) || !/<\/svg>\s*$/i.test(question.svg)) {
        problems.push('"svg" must be a whole <svg …>…</svg> drawing');
      }
      if (!hasText(question.svgAlt)) problems.push('"svgAlt" (a description of the drawing for screen readers) is missing');
    }
    return problems;
  }

  /* Problems with a quiz's own fields (not its questions). */
  function quizProblems(quiz) {
    var problems = [];
    if (!quiz || typeof quiz !== 'object' || Array.isArray(quiz)) return ['it is not an object { … }'];
    if (!hasText(quiz.id)) problems.push('"id" is missing');
    else if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(quiz.id)) problems.push('"id" may only use English letters, numbers, - and _');
    if (!hasText(quiz.title)) problems.push('"title" is missing');
    if (quiz.chapter !== undefined && typeof quiz.chapter !== 'string') problems.push('"chapter" must be a text');
    if (quiz.difficulty !== undefined && DIFFICULTIES.indexOf(quiz.difficulty) === -1) {
      problems.push('"difficulty" must be one of: ' + DIFFICULTIES.join(', '));
    }
    if (!Array.isArray(quiz.questions)) problems.push('"questions" must be a list [ … ]');
    return problems;
  }

  /**
   * Reads one subject's quiz file (already parsed from JSON).
   * Returns { lang, quizzes, problems, skipped }:
   *   quizzes   the quizzes that can be shown, each with only its usable questions;
   *   problems  English sentences saying what is wrong and where;
   *   skipped   how many questions or quizzes are not shown.
   */
  function readFile(data, subjectId) {
    var info = subject(subjectId);
    var file = info ? info.file : 'the quiz file';
    var result = { lang: info ? info.lang : 'ar', quizzes: [], problems: [], skipped: 0 };
    if (!data || typeof data !== 'object' || Array.isArray(data) || !Array.isArray(data.quizzes)) {
      result.problems.push(file + ': the file must look like { "subject": "…", "lang": "…", "quizzes": [ … ] }');
      return result;
    }
    if (data.subject !== undefined && data.subject !== subjectId) {
      result.problems.push(file + ': "subject" should be "' + subjectId + '"');
    }
    if (data.lang === 'ar' || data.lang === 'en') result.lang = data.lang;
    else if (data.lang !== undefined) result.problems.push(file + ': "lang" must be "ar" or "en"');

    var quizIds = {};
    data.quizzes.forEach(function (quiz, q) {
      var where = file + ', quiz ' + (q + 1) + (quiz && hasText(quiz.id) ? ' ("' + quiz.id + '")' : '');
      var problems = quizProblems(quiz);
      if (!problems.length && quizIds[quiz.id]) problems.push('another quiz in this file has the same "id"');
      if (problems.length) {
        problems.forEach(function (problem) { result.problems.push(where + ': ' + problem); });
        result.skipped += 1;
        return;
      }
      quizIds[quiz.id] = true;
      var questionIds = {};
      var questions = [];
      quiz.questions.forEach(function (question, n) {
        var found = questionProblems(question);
        if (!found.length && questionIds[question.id]) found.push('another question in this quiz has the same "id"');
        if (found.length) {
          found.forEach(function (problem) { result.problems.push(where + ', question ' + (n + 1) + ': ' + problem); });
          result.skipped += 1;
          return;
        }
        questionIds[question.id] = true;
        questions.push(question);
      });
      if (!questions.length) {
        result.problems.push(where + ': it has no questions that can be shown');
        return;
      }
      var copy = {};
      Object.keys(quiz).forEach(function (key) { copy[key] = quiz[key]; });
      copy.questions = questions;
      result.quizzes.push(copy);
    });
    return result;
  }

  /* ---------- Grading ---------- */

  /* answers: one entry per question, the index of the chosen choice or null. */
  function grade(questions, answers) {
    var correct = 0;
    var unanswered = 0;
    questions.forEach(function (question, i) {
      var answer = answers[i];
      if (answer === null || answer === undefined) unanswered += 1;
      else if (answer === question.correctIndex) correct += 1;
    });
    var total = questions.length;
    return {
      correct: correct,
      wrong: total - correct - unanswered,
      unanswered: unanswered,
      total: total,
      percent: total ? Math.round((correct / total) * 100) : 0
    };
  }

  /* ---------- Last score (this browser only) ----------
     Stored under "g12-quiz-scores" as { "physics/quiz-id": { score, total,
     percent, date } }. Only the score is kept: no name or other details.
     Storage can be blocked (some private-browsing modes): then nothing is
     saved and the pages work as usual. */

  function storage(store) {
    if (store) return store;
    try {
      return typeof localStorage !== 'undefined' ? localStorage : null;
    } catch (error) {
      return null;
    }
  }

  function readScores(store) {
    try {
      var raw = storage(store) && storage(store).getItem(SCORES_KEY);
      var data = raw ? JSON.parse(raw) : {};
      return data && typeof data === 'object' && !Array.isArray(data) ? data : {};
    } catch (error) {
      return {};
    }
  }

  function lastScore(subjectId, quizId, store) {
    var entry = readScores(store)[subjectId + '/' + quizId];
    if (!entry || typeof entry !== 'object') return null;
    if (typeof entry.score !== 'number' || typeof entry.total !== 'number' || entry.total <= 0 ||
        entry.score < 0 || entry.score > entry.total) return null;
    return {
      score: entry.score,
      total: entry.total,
      percent: Math.round((entry.score / entry.total) * 100),
      date: typeof entry.date === 'string' ? entry.date : null
    };
  }

  /* Returns true when the score was saved. */
  function saveScore(subjectId, quizId, score, total, store) {
    try {
      var target = storage(store);
      if (!target) return false;
      var data = readScores(store);
      data[subjectId + '/' + quizId] = {
        score: score,
        total: total,
        percent: total ? Math.round((score / total) * 100) : 0,
        date: new Date().toISOString()
      };
      target.setItem(SCORES_KEY, JSON.stringify(data));
      return true;
    } catch (error) {
      return false;
    }
  }

  return {
    SUBJECTS: SUBJECTS,
    DIFFICULTIES: DIFFICULTIES,
    SCORES_KEY: SCORES_KEY,
    hasText: hasText,
    subject: subject,
    steps: steps,
    questionProblems: questionProblems,
    quizProblems: quizProblems,
    readFile: readFile,
    grade: grade,
    lastScore: lastScore,
    saveScore: saveScore
  };
});
