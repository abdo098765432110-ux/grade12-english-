/* ==========================================================================
   Quizzes pages.
     quizzes.html                       the five subjects, each with how many
                                        quizzes it has (counted from its file)
     quizzes.html?subject=<id>          the quizzes of one subject
     quiz.html?subject=<id>&quiz=<id>   taking a quiz: one question at a time,
                                        "Previous" and "Next", "Submit" at the
                                        end, then the score and a review of
                                        every question
   The quizzes are read from quizzes-<subject>.json (see quizzes-data.js and
   the "Quizzes" part of README.md). Nothing is sent anywhere: the last score
   of each quiz is kept in this browser only.

   Quiz text may use three small marks (always shown as text, never as HTML):
     `R = V / I`   a formula, kept left to right inside Arabic text
     V_{B}         written below the line   (V with a small B)
     10^{-19}      written above the line   (10 to the power −19)
   A question may also have a circuit drawing: "svg" (the drawing) and
   "svgAlt" (what it shows, for screen readers).

   Changing the interface language draws the page again and keeps the
   answers already chosen.
   ========================================================================== */
(function () {
  'use strict';

  var G12 = window.G12;
  var Q = G12.Quizzes;
  var el = G12.el;
  var t = G12.t;
  var listRoot = document.getElementById('quizzes-root');
  var quizRoot = document.getElementById('quiz-root');
  var LETTERS = 'ABCDEF';
  var ARABIC_LETTERS = 'أبجدهو';
  var QUESTION_ICONS = ['✏️', '💡', '🤔', '🎯', '📝', '🌟', '📚', '🧠'];
  var cache = {};   // subject id → promise of the checked quiz file

  /* ---------- Loading ---------- */

  function load(subjectId) {
    if (!cache[subjectId]) {
      var info = Q.subject(subjectId);
      cache[subjectId] = G12.loadJSON(info.file).then(function (data) {
        var result = Q.readFile(data, subjectId);
        result.problems.forEach(function (problem) {
          if (window.console) console.warn('[quizzes] ' + problem);
        });
        return result;
      });
    }
    return cache[subjectId];
  }

  /* ---------- Small helpers ---------- */

  function difficultyText(level) {
    switch (level) {
      case 'Easy': return t('Easy');
      case 'Medium': return t('Medium');
      case 'Hard': return t('Hard');
      case 'Very Hard': return t('Very Hard');
      default: return level;
    }
  }

  /* Quiz text with its small marks: `formula`, _{below} and ^{above}. */
  function rich(text) {
    var fragment = document.createDocumentFragment();
    String(text).split('`').forEach(function (part, i) {
      if (!part) return;
      if (i % 2 === 1) {
        // a short formula ("20 W", "I₂ = 6 A") never breaks across two lines; a long one may
        var short = part.replace(/[_^]\{([^{}]*)\}/g, '$1').length <= 24;
        var math = el('bdi', { className: short ? 'math math--short' : 'math', dir: 'ltr' });
        addScripts(math, part);
        fragment.appendChild(math);
      } else {
        addScripts(fragment, part);
      }
    });
    return fragment;
  }

  function addScripts(parent, text) {
    var pattern = /([_^])\{([^{}]*)\}/g;
    var last = 0;
    var match;
    while ((match = pattern.exec(text))) {
      addLines(parent, text.slice(last, match.index));
      parent.appendChild(el(match[1] === '_' ? 'sub' : 'sup', { text: match[2] }));
      last = pattern.lastIndex;
    }
    addLines(parent, text.slice(last));
  }

  function addLines(parent, text) {
    text.split('\n').forEach(function (line, i) {
      if (i > 0) parent.appendChild(document.createElement('br'));
      if (line) parent.appendChild(document.createTextNode(line));
    });
  }

  /* Quiz content inside interface text keeps its own direction (<bdi>). */
  function content(text, lang) {
    return el('bdi', { lang: lang }, [rich(text)]);
  }

  /* "7 / 10" always reads left to right, also in the Arabic interface. */
  function scoreText(score, total) {
    return el('bdi', { dir: 'ltr', text: score + ' / ' + total });
  }

  function letter(lang, i) {
    return lang === 'ar' ? ARABIC_LETTERS.charAt(i) + ')' : LETTERS.charAt(i) + '.';
  }

  function quizHref(subjectId, quizId) {
    return 'quiz.html?subject=' + encodeURIComponent(subjectId) + '&quiz=' + encodeURIComponent(quizId);
  }

  function subjectHref(subjectId) {
    return 'quizzes.html?subject=' + encodeURIComponent(subjectId);
  }

  /* The circuit drawing of a question. The drawing comes from the quiz file;
     anything that could run code (scripts, event attributes, outside links)
     is removed before it is shown. */
  function figure(question) {
    if (!Q.hasText(question.svg) || typeof DOMParser !== 'function') return null;
    var parsed = new DOMParser().parseFromString(question.svg, 'image/svg+xml');
    var svg = parsed.documentElement;
    if (!svg || svg.nodeName.toLowerCase() !== 'svg' || parsed.getElementsByTagName('parsererror').length) {
      if (window.console) console.warn('[quizzes] question "' + question.id + '": the drawing ("svg") could not be read');
      return null;
    }
    Array.prototype.slice.call(svg.querySelectorAll('script, foreignObject, iframe, object, embed, use')).forEach(function (node) {
      node.parentNode.removeChild(node);
    });
    [svg].concat(Array.prototype.slice.call(svg.querySelectorAll('*'))).forEach(function (node) {
      Array.prototype.slice.call(node.attributes).forEach(function (attribute) {
        var name = attribute.name.toLowerCase();
        if (name.indexOf('on') === 0 || name === 'href' || name === 'xlink:href' || name === 'style' && /url\(|expression/i.test(attribute.value)) {
          node.removeAttribute(attribute.name);
        }
      });
    });
    var drawing = document.importNode(svg, true);
    drawing.setAttribute('role', 'img');
    drawing.setAttribute('aria-label', question.svgAlt || '');
    drawing.setAttribute('focusable', 'false');
    return el('figure', { className: 'quiz-figure' }, [drawing]);
  }

  function breadcrumb(steps) {
    return el('nav', { className: 'breadcrumb quiz-breadcrumb', 'aria-label': t('Breadcrumb') }, [
      el('ol', null, steps.map(function (step, i) {
        var label = step.lang ? content(step.label, step.lang) : step.label;
        var last = i === steps.length - 1;
        return el('li', null, [last
          ? el('span', { 'aria-current': 'page' }, [label])
          : el('a', { href: step.href }, [label])]);
      }))
    ]);
  }

  function notFound(root, title, text, links) {
    G12.setTitle(title);
    G12.clear(root);
    root.appendChild(el('h1', { text: title }));
    root.appendChild(el('div', { className: 'empty-state' }, [
      el('p', { text: text }),
      el('div', { className: 'actions' }, links.map(function (link, i) {
        return el('a', { className: i === 0 ? 'btn' : 'btn btn--secondary', href: link.href, text: link.label });
      }))
    ]));
  }

  /* Questions that are not shown because the file has a mistake. */
  function skippedNotice(result) {
    if (!result.skipped) return null;
    return el('div', { className: 'notice notice--demo', role: 'note' }, [
      el('p', { text: t('Some quizzes or questions in this subject could not be shown because they are incomplete or contain errors. The details are in the browser console.') })
    ]);
  }

  /* ==========================================================================
     quizzes.html — the subjects, or one subject's quizzes
     ========================================================================== */

  function drawList() {
    var info = Q.subject(G12.param('subject'));
    if (G12.param('subject') !== null && !info) {
      notFound(listRoot, t('Subject not found'), t('This subject does not exist. Choose a subject from the list of quizzes.'),
        [{ label: t('All subjects'), href: 'quizzes.html' }]);
      return;
    }
    if (info) subjectPage(info);
    else subjectsPage();
  }

  function subjectsPage() {
    G12.setTitle(t('Quizzes'));
    G12.clear(listRoot);
    listRoot.appendChild(el('h1', { text: t('Quizzes') }));
    listRoot.appendChild(el('p', {
      className: 'lead',
      text: t('Choose a subject to see its quizzes. You answer one question at a time, then you see your score and a step-by-step explanation of every question.')
    }));
    var grid = el('ul', { className: 'card-grid home-cards quiz-subjects', 'aria-label': t('Subjects') });
    Q.SUBJECTS.forEach(function (info) {
      var count = el('p', { className: 'card-count' }, [el('span', { text: t('Loading…') })]);
      grid.appendChild(el('li', { className: 'card ' + info.tone, 'data-subject': info.id }, [
        el('img', { className: 'card-icon', src: info.icon, alt: '', width: '64', height: '64' }),
        el('h2', { lang: 'ar', text: info.name }),
        count,
        el('div', { className: 'card-actions' }, [el('a', { className: 'btn', href: subjectHref(info.id), text: t('Open quizzes') })])
      ]));
      load(info.id).then(function (result) {
        count.textContent = result.quizzes.length ? G12.plural(result.quizzes.length, 'quiz', 'quizzes') : t('No quizzes yet');
      }, function () {
        count.textContent = t('Could not load');
      });
    });
    listRoot.appendChild(grid);
  }

  function subjectPage(info) {
    G12.setTitle(info.name + ' — ' + t('Quizzes'));
    G12.clear(listRoot);
    listRoot.appendChild(breadcrumb([{ label: t('Quizzes'), href: 'quizzes.html' }, { label: info.name, lang: 'ar' }]));
    listRoot.appendChild(el('div', { className: 'subject-title quiz-subject-title ' + info.tone }, [
      el('img', { src: info.icon, alt: '', width: '64', height: '64' }),
      el('div', { className: 'quiz-subject-name' }, [
        el('p', { className: 'quiz-kicker', text: t('Quizzes') }),
        el('h1', { lang: 'ar', text: info.name })
      ])
    ]));
    var area = el('div', { className: 'quiz-list-area' }, [el('p', { className: 'loading', role: 'status', text: t('Loading…') })]);
    listRoot.appendChild(area);
    load(info.id).then(function (result) {
      G12.clear(area);
      if (!result.quizzes.length) {
        area.appendChild(G12.emptyState(
          t('No quizzes available yet — coming soon.'),
          t('The quizzes for this subject will appear here as soon as they are added.'),
          [{ label: t('All subjects'), href: 'quizzes.html' }]
        ));
      } else {
        area.appendChild(el('h2', { className: 'quiz-list-title', text: t('Available quizzes') }));
        area.appendChild(el('ul', { className: 'quiz-list' }, result.quizzes.map(function (quiz) {
          return quizCard(info, result.lang, quiz);
        })));
      }
      var notice = skippedNotice(result);
      if (notice) area.appendChild(notice);
    }, function (error) {
      G12.showError(area, error, {});
    });
  }

  function quizCard(info, lang, quiz) {
    var last = Q.lastScore(info.id, quiz.id);
    var labels = [G12.plural(quiz.questions.length, 'question')];
    if (quiz.difficulty) labels.push(t('Difficulty: {level}', { level: difficultyText(quiz.difficulty) }));
    return el('li', { className: 'card quiz-card ' + info.tone, 'data-quiz': quiz.id }, [
      el('h3', null, [content(quiz.title, lang)]),
      Q.hasText(quiz.chapter) ? el('p', { className: 'quiz-chapter' }, [content(quiz.chapter, lang)]) : null,
      el('ul', { className: 'badges', 'aria-label': t('Labels') }, labels.map(function (text) {
        return el('li', { className: 'badge', text: text });
      })),
      el('p', { className: 'quiz-last-score' }, last
        ? G12.tNodes('Your last score: {score} ({percent}%)', { percent: last.percent }, { score: scoreText(last.score, last.total) })
        : [t('Not taken yet on this device')]),
      el('div', { className: 'card-actions' }, [el('a', { className: 'btn', href: quizHref(info.id, quiz.id), text: t('Start Quiz') })])
    ]);
  }

  /* ==========================================================================
     quiz.html — taking a quiz
     ========================================================================== */

  var state = null;   // { info, lang, quiz, answers, index, warning, submitted, result, previous, saved }

  function startQuiz() {
    var info = Q.subject(G12.param('subject'));
    var quizId = G12.param('quiz');
    if (!info || !quizId) {
      notFound(quizRoot, t('Quiz not found'), t('This link does not lead to a quiz. Choose a quiz from the list of quizzes.'),
        [{ label: t('All subjects'), href: 'quizzes.html' }]);
      return;
    }
    G12.setTitle(t('Quiz'));
    load(info.id).then(function (result) {
      var quiz = result.quizzes.filter(function (item) { return item.id === quizId; })[0];
      if (!quiz) {
        notFound(quizRoot, t('Quiz not found'), t('This quiz is not in the list of quizzes. It may have been renamed or removed.'),
          [{ label: t('Quizzes'), href: subjectHref(info.id) }, { label: t('All subjects'), href: 'quizzes.html' }]);
        return;
      }
      state = { info: info, lang: result.lang, quiz: quiz, index: 0, warning: false, submitted: false };
      state.answers = quiz.questions.map(function () { return null; });
      drawQuiz(false);
    }, function (error) {
      G12.showError(quizRoot, error, { title: t('Quiz') });
    });
  }

  /* The quiz title and its details, then the question (or the results). */
  function drawQuiz(moveFocus) {
    var quiz = state.quiz;
    var lang = state.lang;
    G12.setTitle(G12.Quizzes.hasText(quiz.title) ? quiz.title.replace(/[`]/g, '').replace(/[_^]\{([^{}]*)\}/g, '$1') : t('Quiz'));
    G12.clear(quizRoot);
    quizRoot.appendChild(breadcrumb([
      { label: t('Quizzes'), href: 'quizzes.html' },
      { label: state.info.name, lang: 'ar', href: subjectHref(state.info.id) },
      { label: quiz.title, lang: lang }
    ]));
    var labels = [G12.plural(quiz.questions.length, 'question')];
    if (quiz.difficulty) labels.push(t('Difficulty: {level}', { level: difficultyText(quiz.difficulty) }));
    quizRoot.appendChild(el('div', { className: 'quiz-intro ' + state.info.tone }, [
      el('h1', null, [content(quiz.title, lang)]),
      Q.hasText(quiz.chapter) ? el('p', { className: 'quiz-chapter' }, [content(quiz.chapter, lang)]) : null,
      el('ul', { className: 'badges', 'aria-label': t('Labels') }, labels.map(function (text) {
        return el('li', { className: 'badge', text: text });
      }))
    ]));
    state.view = el('section', { className: 'quiz quiz-take', 'aria-label': t('Quiz') });
    quizRoot.appendChild(state.view);
    if (state.submitted) showResults(moveFocus);
    else showQuestion(moveFocus);
  }

  function promptNodes(question, index) {
    return [el('span', { className: 'question-head' }, [
      el('span', { className: 'question-icon question-icon--' + (index % 4), 'aria-hidden': 'true', text: QUESTION_ICONS[index % QUESTION_ICONS.length] }),
      el('span', { className: 'question-main' }, [el('span', { className: 'prompt-text' }, [rich(question.question)])])
    ])];
  }

  function answeredCount() {
    return state.answers.filter(function (answer) { return answer !== null; }).length;
  }

  function unansweredNumbers() {
    var list = [];
    state.answers.forEach(function (answer, i) { if (answer === null) list.push(i + 1); });
    return list;
  }

  function goTo(index) {
    state.index = index;
    state.warning = false;
    showQuestion(true);
  }

  function showQuestion(moveFocus) {
    var view = state.view;
    var quiz = state.quiz;
    var lang = state.lang;
    var dir = lang === 'ar' ? 'rtl' : 'ltr';
    var question = quiz.questions[state.index];
    var total = quiz.questions.length;
    var number = state.index + 1;
    var isLast = state.index === total - 1;
    G12.clear(view);

    var heading = el('h2', { className: 'quiz-progress-text', tabindex: '-1', text: t('Question {n} of {total}', { n: number, total: total }) });
    var answered = el('p', { className: 'quiz-answered' });
    view.appendChild(el('div', { className: 'quiz-header' }, [heading, answered]));
    view.appendChild(el('progress', { max: String(total), value: String(number), 'aria-hidden': 'true' }));

    /* The numbers 1, 2, 3 …: jump to any question; answered ones are marked. */
    var jump = el('ol', { className: 'quiz-jump', dir: 'ltr' });
    for (var i = 0; i < total; i++) {
      jump.appendChild(el('li', null, [el('button', { type: 'button', className: 'quiz-nav-button', 'data-index': String(i), text: String(i + 1) })]));
    }
    jump.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-index]');
      if (button) goTo(Number(button.getAttribute('data-index')));
    });
    view.appendChild(el('nav', { className: 'quiz-jump-nav', 'aria-label': t('Question numbers') }, [jump]));

    var form = el('form', { className: 'question-form', novalidate: true });
    var name = 'quiz-q' + state.index;
    var list = el('ul', { className: 'options' });
    question.options.forEach(function (option, i) {
      var input = el('input', { type: 'radio', name: name, value: String(i) });
      if (state.answers[state.index] === i) input.checked = true;
      input.addEventListener('change', function () {
        state.answers[state.index] = i;
        if (state.warning && !unansweredNumbers().length) {
          state.warning = false;
          G12.clear(warning);
          warning.className = 'feedback';
        }
        paint();
      });
      list.appendChild(el('li', { className: 'option' }, [
        el('label', null, [
          input,
          el('span', { className: 'option-letter', 'aria-hidden': 'true', text: letter(lang, i) }),
          el('span', { className: 'option-text' + (lang === 'ar' ? ' option-text--ar' : '') }, [rich(option)])
        ])
      ]));
    });
    form.appendChild(el('fieldset', { dir: dir, lang: lang }, [
      el('legend', { className: 'question-legend' }, promptNodes(question, state.index)),
      figure(question),
      list
    ]));

    var warning = el('div', { className: 'feedback', tabindex: '-1' });
    form.appendChild(warning);

    var previous = el('button', { type: 'button', className: 'btn btn--secondary', text: t('Previous') });
    previous.disabled = state.index === 0;
    previous.addEventListener('click', function () { if (state.index > 0) goTo(state.index - 1); });
    var forward = el('button', { type: 'submit', className: 'btn quiz-forward', text: isLast ? t('Submit') : t('Next') });
    form.appendChild(el('div', { className: 'actions quiz-actions' }, [previous, forward]));
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!isLast) goTo(state.index + 1);
      else submit(warning, false);
    });
    view.appendChild(form);

    function paint() {
      answered.textContent = t('Answered: {n} of {total}', { n: answeredCount(), total: total });
      Array.prototype.forEach.call(jump.querySelectorAll('button[data-index]'), function (button, j) {
        var done = state.answers[j] !== null;
        button.className = 'quiz-nav-button ' + (done ? 'is-answered' : 'is-unanswered') + (j === state.index ? ' is-current' : '');
        button.setAttribute('aria-label', t(done ? 'Question {n}, answered' : 'Question {n}, not answered', { n: j + 1 }));
        if (j === state.index) button.setAttribute('aria-current', 'step');
        else button.removeAttribute('aria-current');
      });
    }
    paint();
    if (state.warning) submit(warning, true);
    if (moveFocus) G12.focus(heading);
  }

  /* "Submit": with unanswered questions, warn first (they count as wrong). */
  function submit(warning, redraw) {
    var missing = unansweredNumbers();
    if (!missing.length) {
      finish();
      return;
    }
    state.warning = true;
    G12.clear(warning);
    warning.className = 'feedback feedback--warning quiz-warning';
    warning.setAttribute('role', 'alert');
    warning.appendChild(el('p', { className: 'feedback-title', text: missing.length === 1
      ? t('{questions} has not been answered yet.', { questions: G12.plural(1, 'question') })
      : t('{questions} have not been answered yet.', { questions: G12.plural(missing.length, 'question') }) }));
    warning.appendChild(el('p', null, G12.tNodes('Unanswered: {numbers}. An unanswered question is counted as wrong.', null, {
      numbers: el('bdi', { dir: 'ltr', text: missing.join(', ') })
    })));
    warning.appendChild(el('div', { className: 'actions' }, [
      el('button', { type: 'button', className: 'btn', text: t('Go to question {n}', { n: missing[0] }), onclick: function () { goTo(missing[0] - 1); } }),
      el('button', { type: 'button', className: 'btn btn--secondary', text: t('Submit anyway'), onclick: finish })
    ]));
    if (!redraw) G12.focus(warning);
  }

  function finish() {
    var quiz = state.quiz;
    state.result = Q.grade(quiz.questions, state.answers);
    state.previous = Q.lastScore(state.info.id, quiz.id);
    state.saved = Q.saveScore(state.info.id, quiz.id, state.result.correct, state.result.total);
    state.submitted = true;
    state.warning = false;
    showResults(true);
  }

  function retake() {
    state.answers = state.quiz.questions.map(function () { return null; });
    state.index = 0;
    state.submitted = false;
    state.warning = false;
    state.result = null;
    showQuestion(true);
  }

  function resultMessage(percent) {
    if (percent >= 90) return t('Excellent work!');
    if (percent >= 75) return t('Very good!');
    if (percent >= 50) return t('Good. Read the explanations below to learn from your mistakes.');
    return t('Keep practising: read the explanations below, then retake the quiz.');
  }

  function resultButtons() {
    return el('div', { className: 'actions' }, [
      el('button', { type: 'button', className: 'btn', text: t('Retake Quiz'), onclick: retake }),
      el('a', { className: 'btn btn--secondary', href: subjectHref(state.info.id), text: t('Back to the quiz list') })
    ]);
  }

  function showResults(moveFocus) {
    var view = state.view;
    var result = state.result;
    G12.clear(view);
    var heading = el('h2', { tabindex: '-1', text: t('Your result') });
    view.appendChild(heading);
    view.appendChild(el('div', { className: 'score-box quiz-score' }, [
      el('p', { className: 'score-number' }, [scoreText(result.correct, result.total)]),
      el('p', { className: 'quiz-percent', text: t('{percent}% correct', { percent: result.percent }) }),
      el('p', { className: 'quiz-message', text: resultMessage(result.percent) }),
      el('ul', { className: 'score-breakdown' }, [
        el('li', { text: t('Correct: {n}', { n: result.correct }) }),
        el('li', { text: t('Not correct: {n}', { n: result.wrong }) }),
        result.unanswered ? el('li', { text: t('Not answered: {n}', { n: result.unanswered }) }) : null
      ])
    ]));
    var note;
    if (!state.saved) note = [t('Your score could not be saved, because this browser does not allow saving.')];
    else if (state.previous) note = G12.tNodes('Your score is saved on this device. Your score before this one: {score}.', null, { score: scoreText(state.previous.score, state.previous.total) });
    else note = [t('Your score is saved on this device.')];
    view.appendChild(el('p', { className: 'hint quiz-saved' }, note));
    view.appendChild(resultButtons());

    view.appendChild(el('h3', { className: 'quiz-review-title', text: t('Review your answers') }));
    var list = el('ol', { className: 'review-list quiz-review' });
    state.quiz.questions.forEach(function (question, i) {
      list.appendChild(reviewItem(question, i));
    });
    view.appendChild(list);
    view.appendChild(resultButtons());
    if (moveFocus) G12.focus(heading);
  }

  function reviewItem(question, i) {
    var lang = state.lang;
    var dir = lang === 'ar' ? 'rtl' : 'ltr';
    var chosen = state.answers[i];
    var outcome = chosen === null ? 'skipped' : chosen === question.correctIndex ? 'match' : 'differs';
    var outcomeText = outcome === 'skipped' ? '— ' + t('Not answered') : outcome === 'match' ? '✓ ' + t('Correct') : '✗ ' + t('Wrong');

    var options = el('ul', { className: 'options quiz-review-options', dir: dir, lang: lang });
    question.options.forEach(function (option, j) {
      var isCorrect = j === question.correctIndex;
      var isChosen = j === chosen;
      var status = '';
      if (isCorrect && isChosen) status = t('✓ Your answer is correct');
      else if (isCorrect) status = t('✓ Correct answer');
      else if (isChosen) status = t('✗ Your answer');
      options.appendChild(el('li', { className: 'option' + (isCorrect ? ' option--match' : isChosen ? ' option--tried' : '') }, [
        el('div', { className: 'option-row' }, [
          el('span', { className: 'option-letter', 'aria-hidden': 'true', text: letter(lang, j) }),
          el('span', { className: 'option-text' + (lang === 'ar' ? ' option-text--ar' : '') }, [rich(option)]),
          status ? el('span', { className: 'option-status', dir: G12.dir, lang: G12.lang, text: status }) : null
        ])
      ]));
    });

    var why = null;
    if (Array.isArray(question.whyWrong)) {
      var reasons = [];
      question.whyWrong.forEach(function (text, j) {
        if (j !== question.correctIndex && Q.hasText(text)) {
          reasons.push(el('li', null, [el('span', { className: 'option-letter', text: letter(lang, j) }), ' ', rich(text)]));
        }
      });
      if (reasons.length) {
        why = el('div', { className: 'quiz-why' }, [
          el('p', null, [el('strong', { text: t('Why the other choices are wrong:') })]),
          el('ul', { dir: dir, lang: lang }, reasons)
        ]);
      }
    }

    return el('li', { className: 'quiz-review-item quiz-review-item--' + outcome }, [
      el('p', { className: 'quiz-review-head' }, [
        el('span', { className: 'quiz-review-number', text: t('Question {n}', { n: i + 1 }) }),
        el('span', { className: 'review-outcome review-outcome--' + outcome, text: outcomeText })
      ]),
      el('div', { className: 'quiz-review-question', dir: dir, lang: lang }, [el('p', null, [el('strong', null, [rich(question.question)])])]),
      figure(question),
      options,
      el('p', { className: 'quiz-skill' }, [el('strong', { text: t('Skill:') }), ' ', content(question.skill, lang)]),
      el('div', { className: 'explanation-block quiz-explanation' }, [
        el('p', null, [el('strong', { text: t('Step-by-step explanation:') })]),
        el('ol', { className: 'quiz-steps', dir: dir, lang: lang }, Q.steps(question.explanation).map(function (step) {
          return el('li', null, [rich(step)]);
        }))
      ]),
      why
    ]);
  }

  /* ---------- Start ---------- */

  if (listRoot) drawList();
  if (quizRoot) startQuiz();

  G12.onLanguageChange(function () {
    if (listRoot) drawList();
    if (quizRoot) {
      if (state) drawQuiz(false);
      else startQuiz();
    }
  });
})();
