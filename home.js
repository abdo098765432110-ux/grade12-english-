/* Home page: shows how much content each section has.
   Drawn again in the other language when the language button is used. */
(function () {
  'use strict';

  var G12 = window.G12;
  var status = document.getElementById('home-status');
  var t = G12.t;
  var loaded = null;   // content, once loaded
  var failed = null;   // loading error, if any
  /* The vocabulary questions have their own file (see vocabulary.js):
     null while loading, then the number of working questions, or -1 if the
     file could not be loaded. */
  var vocabulary = null;

  /* [counted word, text when there is none, English plural] */
  function words() {
    return {
      summaries: ['summary', t('No summaries yet'), 'summaries'],
      questions: ['question', t('No questions yet')],
      passages: ['passage', t('No passages yet')]
    };
  }

  function setCount(key, text) {
    var target = document.querySelector('[data-count="' + key + '"]');
    if (target) target.textContent = text;
  }

  function draw(content) {
    var WORDS = words();
    G12.setTitle('');
    G12.clear(status);
    var total = 0;
    Object.keys(WORDS).forEach(function (key) {
      var count = content[key].length;
      total += count;
      setCount(key, count ? G12.plural(count, WORDS[key][0], WORDS[key][2]) : WORDS[key][1]);
    });

    if (total === 0) {
      status.appendChild(G12.emptyState(
        t('No content added yet'),
        t('Summaries, practice questions and reading passages will appear here as soon as a teacher adds them.'),
        [{ label: t('Open the content manager'), href: G12.MANAGER_PAGE }]
      ));
    }
    var skipped = G12.skippedNotice(content.skipped);
    if (skipped) status.appendChild(skipped);
  }

  function drawVocabulary() {
    if (vocabulary === null) return;
    setCount('vocabulary', vocabulary < 0 ? t('Could not load')
      : vocabulary ? G12.plural(vocabulary, 'question') : t('No questions yet'));
  }

  function drawError(error) {
    G12.setTitle('');
    Object.keys(words()).forEach(function (key) { setCount(key, t('Could not load')); });
    G12.showError(status, error, { homeLink: false });
  }

  G12.setTitle('');
  G12.loadContent(['summaries', 'questions', 'passages']).then(function (content) {
    loaded = content;
    draw(content);
  }).catch(function (error) {
    failed = error;
    drawError(error);
  });

  G12.loadJSON('vocabulary-questions.json').then(function (data) {
    vocabulary = (Array.isArray(data && data.units) ? data.units : []).reduce(function (sum, unit) {
      var questions = unit && Array.isArray(unit.questions) ? unit.questions : [];
      return sum + questions.filter(function (question, i) {
        return G12.Schema.validateItem('questions', question, i).errors.length === 0;
      }).length;
    }, 0);
    drawVocabulary();
  }).catch(function () {
    vocabulary = -1;
    drawVocabulary();
  });

  G12.onLanguageChange(function () {
    drawVocabulary();
    if (loaded) draw(loaded);
    else if (failed) drawError(failed);
    else G12.setTitle('');
  });
})();
