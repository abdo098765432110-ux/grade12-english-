/* Home page: shows how much content each section has.
   Drawn again in the other language when the language button is used. */
(function () {
  'use strict';

  var G12 = window.G12;
  var status = document.getElementById('home-status');
  var t = G12.t;
  var loaded = null;   // content, once loaded
  var failed = null;   // loading error, if any

  /* [counted word, text when there is none, English plural] */
  function words() {
    return {
      lessons: ['lesson', t('No lessons yet')],
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
        t('Lessons, summaries, practice questions and reading passages will appear here as soon as a teacher adds them.'),
        [{ label: t('Open the content manager'), href: G12.MANAGER_PAGE }]
      ));
    }
    var skipped = G12.skippedNotice(content.skipped);
    if (skipped) status.appendChild(skipped);
  }

  function drawError(error) {
    G12.setTitle('');
    Object.keys(words()).forEach(function (key) { setCount(key, t('Could not load')); });
    G12.showError(status, error, { homeLink: false });
  }

  G12.setTitle('');
  G12.loadContent(['lessons', 'summaries', 'questions', 'passages']).then(function (content) {
    loaded = content;
    draw(content);
  }).catch(function (error) {
    failed = error;
    drawError(error);
  });

  G12.onLanguageChange(function () {
    if (loaded) draw(loaded);
    else if (failed) drawError(failed);
    else G12.setTitle('');
  });
})();
