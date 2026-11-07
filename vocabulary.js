/* Vocabulary page: questions on the words of each English unit, kept in
   their own file (vocabulary-questions.json), apart from the grammar questions:
     { "schemaVersion": 2, "units": [
         { "id": "unit-1", "title": "Unit 1: Inside the World of Care",
           "questions": [ … ] } ] }
   The questions use the same format as the grammar questions; a broken
   question is left out. Choose a unit, the level, how many questions and how
   to answer them, then practise.
     vocabulary.html?unit=<unit id>   preselects a unit */
(function () {
  'use strict';

  var G12 = window.G12;
  var Schema = G12.Schema;
  var el = G12.el;
  var t = G12.t;
  var root = document.getElementById('page-root');
  var FILE = 'vocabulary-questions.json';
  var COUNT_PRESETS = [10, 15, 20, 30];
  function modes() {
    return [
      { value: 'one', label: t('One at a time — feedback after each answer') },
      { value: 'all', label: t('All at once — answer everything, then check') }
    ];
  }

  var units = null;    // [{ id, title, questions }] with working questions only
  var skipped = 0;     // broken questions left out
  var loadError = null;
  /* level: 'easy', 'medium', 'hard' or 'mixed'; count: the choice on the settings screen;
     custom: the number typed for 'custom'; pick: how many questions to use (null: all). */
  var settings = { unit: '', level: 'mixed', count: null, custom: '', pick: null, mode: 'one' };
  var examChoice = null;
  var running = null;  // the exam in progress (null: settings screen)
  var setupArea = el('div');
  var quizArea = el('div', { id: 'quiz-area' });
  G12.ignoreDoubleClicks(setupArea);
  G12.ignoreDoubleClicks(quizArea);

  function list(value) { return Array.isArray(value) ? value : []; }

  /* Units with an id, a title and at least one working question. */
  function readUnits(data) {
    var used = {};
    return list(data && data.units).map(function (unit) {
      if (!unit || !Schema.hasText(unit.id) || !Schema.hasText(unit.title)) return null;
      var questions = list(unit.questions).filter(function (question, i) {
        var ok = Schema.validateItem('questions', question, i).errors.length === 0 && !used[question.id];
        if (ok) used[question.id] = true;
        else skipped += 1;
        return ok;
      });
      return questions.length ? { id: unit.id, title: unit.title, questions: questions } : null;
    }).filter(Boolean);
  }

  G12.loadJSON(FILE).then(function (data) {
    units = readUnits(data);
    var wanted = G12.param('unit');
    if (wanted && findUnit(wanted)) settings.unit = wanted;
    drawPage();
  }).catch(function (error) {
    loadError = error;
    G12.showError(root, error, { title: t('Vocabulary') });
  });

  /* The language button draws the page again in the other language. A
     practice in progress starts again with the same questions, so ask first
     if the student has already answered something. */
  G12.beforeLanguageChange(function () {
    return running && G12.hasAnswers(quizArea)
      ? t('Changing the language starts the questions on this page again, and your answers so far will be cleared. Change the language?')
      : null;
  });
  G12.onLanguageChange(function () {
    if (units) {
      rememberChoices();
      drawPage();
    } else if (loadError) {
      G12.showError(root, loadError, { title: t('Vocabulary') });
    }
  });

  function findUnit(id) {
    return units.filter(function (unit) { return unit.id === id; })[0] || null;
  }

  function pool(unitId) {
    var chosen = unitId ? findUnit(unitId) : null;
    return chosen ? chosen.questions : units.reduce(function (all, unit) { return all.concat(unit.questions); }, []);
  }

  /* Keep the choices made on the settings screen (not yet started). */
  function rememberChoices() {
    var form = setupArea.querySelector('form');
    if (!form || setupArea.hidden) return;
    var unit = form.querySelector('#vocabulary-unit');
    var mode = form.querySelector('input[name="mode"]:checked');
    if (unit) settings.unit = unit.value;
    if (examChoice) {
      var state = examChoice.state();
      settings.level = state.level;
      settings.count = state.value;
      settings.custom = state.custom;
    }
    if (mode) settings.mode = mode.value;
  }

  function drawPage() {
    G12.setTitle(t('Vocabulary'));
    G12.clear(root);
    root.appendChild(el('h1', { text: t('Vocabulary') }));
    root.appendChild(el('p', { className: 'lead', text: t('Practise the important words of each unit. Every answer comes with an explanation of why it is right and why the other choices are wrong.') }));
    var notice = G12.skippedNotice(skipped);
    if (notice) root.appendChild(notice);

    if (units.length === 0) {
      root.appendChild(G12.emptyState(
        t('No vocabulary questions yet'),
        t('Vocabulary questions will appear here as soon as they are added.')
      ));
      return;
    }

    var review = G12.listReviewNotice(pool(''));
    if (review) root.appendChild(review);
    root.appendChild(setupArea);
    root.appendChild(quizArea);
    if (running) startPractice(running, true);
    else showSetup(false);
  }

  /* ---------- Settings form ---------- */

  function showSetup(moveFocus) {
    running = null;
    examChoice = null;
    G12.clear(quizArea);
    G12.clear(setupArea);
    setupArea.hidden = false;

    // unit titles are English, so the list reads left to right (also on Arabic pages)
    var unitSelect = el('select', { id: 'vocabulary-unit', name: 'unit', lang: 'en', dir: 'ltr' });
    var countHolder = el('div');
    var startButton = el('button', { type: 'submit', className: 'btn', text: t('Start practice') });
    var heading = el('h2', { id: 'setup-heading', tabindex: '-1', text: t('Choose your practice') });

    var options = units.map(function (unit) {
      return { value: unit.id, label: t('{title} ({count})', { title: unit.title, count: unit.questions.length }) };
    });
    if (units.length > 1) options.unshift({ value: '', label: t('All units ({count})', { count: pool('').length }) });
    options.forEach(function (option) {
      unitSelect.appendChild(el('option', { value: option.value, text: option.label }));
    });
    unitSelect.value = options.some(function (option) { return option.value === settings.unit; }) ? settings.unit : options[0].value;

    var rows = [heading];
    rows.push(el('div', { className: 'form-row' }, [el('label', { for: 'vocabulary-unit', text: t('Unit') }), unitSelect]));
    rows.push(countHolder);
    rows.push(el('fieldset', { className: 'form-row' }, [
      el('legend', { text: t('How do you want to answer?') }),
      el('div', { className: 'inline-choices' }, modes().map(function (mode) {
        var id = 'vocabulary-mode-' + mode.value;
        return el('label', { for: id }, [
          el('input', { type: 'radio', id: id, name: 'mode', value: mode.value, checked: settings.mode === mode.value }),
          mode.label
        ]);
      }))
    ]));
    rows.push(el('div', { className: 'actions' }, [startButton]));
    var form = el('form', { className: 'panel', 'aria-labelledby': 'setup-heading', novalidate: true }, rows);

    function refresh() {
      var available = pool(unitSelect.value).length;
      var value = settings.count;
      if (typeof value === 'number' && !(value < available && COUNT_PRESETS.indexOf(value) !== -1)) value = null;
      if (value === null || value === undefined) value = available > 10 ? 10 : 'all';
      examChoice = G12.examSettings({
        id: 'vocabulary',
        questions: pool(unitSelect.value),
        presets: COUNT_PRESETS,
        level: settings.level,
        value: value,
        custom: settings.custom,
        hint: t('Questions are chosen at random from the level you choose, in a random order, and never twice in the same exam.'),
        onChange: function (state) {
          settings.level = state.level;
          settings.count = state.value;
          settings.custom = state.custom;
        }
      });
      G12.clear(countHolder);
      examChoice.elements.forEach(function (element) { countHolder.appendChild(element); });
    }

    unitSelect.addEventListener('change', function () {
      settings.unit = unitSelect.value;
      refresh();
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var mode = form.querySelector('input[name="mode"]:checked');
      settings.unit = unitSelect.value;
      settings.mode = mode ? mode.value : 'one';
      if (!pool(settings.unit).length || !examChoice) return;
      var chosen = examChoice.read();
      if (chosen.error) return;
      settings.level = chosen.level;
      settings.pick = chosen.count;
      startPractice();
    });

    setupArea.appendChild(form);
    refresh();
    if (moveFocus) G12.focus(heading);
  }

  /* ---------- Practice ---------- */

  /* exam: the same exam again (after a language change), or none to build a
     new one from the settings: the chosen level, no question twice, in a
     random order. */
  function startPractice(exam, quiet) {
    if (!exam) {
      exam = G12.QuizEngine.buildExam(pool(settings.unit), { level: settings.level, count: settings.pick });
      exam.level = settings.level;
      exam.unit = settings.unit;
    }
    running = exam;
    var unit = exam.unit ? findUnit(exam.unit) : null;

    setupArea.hidden = true;
    G12.clear(quizArea);
    quizArea.appendChild(el('p', null, [
      el('button', { type: 'button', className: 'btn btn--link', text: t('← Change practice settings'), onclick: function () { showSetup(true); } })
    ]));
    if (unit) {
      quizArea.appendChild(el('p', { className: 'vocabulary-unit' }, [
        el('strong', { text: t('Unit') + ': ' }),
        el('bdi', { lang: 'en', text: unit.title })
      ]));
    }
    var notice = G12.examNotice(exam, exam.level);
    if (notice) quizArea.appendChild(notice);
    var holder = el('div');
    quizArea.appendChild(holder);
    var back = [{ label: t('Change practice settings'), onClick: function () { showSetup(true); } }];
    if (settings.mode === 'all') {
      G12.renderWorksheet(holder, exam.questions, { label: t('Vocabulary questions'), title: t('Vocabulary questions'), resultActions: back });
    } else {
      G12.renderQuiz(holder, exam.questions, { label: t('Vocabulary questions'), shuffle: true, resultActions: back });
    }
    if (!quiet) G12.focus(holder.querySelector('h2'));
  }
})();
