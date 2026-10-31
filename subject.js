/* Subject pages (physics.html and, later, the other subjects).
   The content area names its data file in data-questions, for example
     <div class="subject-content" data-questions="physics-questions.json">
   The file holds sections of questions:
     { "schemaVersion": 2, "sections": [
         { "id": "chapter-1-questions", "title": "أسئلة على الفصل الأول", "questions": [ … ] } ] }
   Each section is shown with its title and the shared quiz (quiz-ui.js): one
   question at a time, with instant feedback, the correct answer and the
   explanation. Questions use the same format as the grammar questions; a
   broken question is skipped. Drawn again when the interface language changes. */
(function () {
  'use strict';

  var G12 = window.G12;
  var el = G12.el;
  var t = G12.t;
  var area = document.querySelector('[data-questions]');
  if (!area) return;

  var file = area.getAttribute('data-questions');
  var loaded = null;
  var failed = null;

  function usable(questions) {
    return (Array.isArray(questions) ? questions : []).filter(function (question, i) {
      return G12.Schema.validateItem('questions', question, i).errors.length === 0;
    });
  }

  function draw(data) {
    G12.clear(area);
    var sections = Array.isArray(data && data.sections) ? data.sections : [];
    sections.forEach(function (section, index) {
      var questions = usable(section && section.questions);
      if (!questions.length) return;
      var headingId = 'questions-' + (section.id || index + 1);
      var quizArea = el('div', { className: 'section-quiz' });
      area.appendChild(el('section', { className: 'question-section', 'aria-labelledby': headingId }, [
        el('h2', { id: headingId, className: 'question-section-title', dir: 'auto', lang: /[؀-ۿ]/.test(section.title) ? 'ar' : null, text: section.title }),
        quizArea
      ]));
      G12.renderQuiz(quizArea, questions, { label: section.title, shuffle: false });
    });
    if (!area.childNodes.length) {
      area.appendChild(el('div', { className: 'empty-state' }, [
        el('h2', { text: t('No content added yet') }),
        el('p', { text: t('Lessons for this subject will appear here when they are added.') })
      ]));
    }
  }

  function fail(error) {
    G12.clear(area);
    G12.showError(area, error);
  }

  G12.loadJSON(file).then(function (data) {
    loaded = data;
    draw(data);
  }).catch(function (error) {
    failed = error;
    fail(error);
  });

  if (G12.onLanguageChange) {
    G12.onLanguageChange(function () {
      if (loaded) draw(loaded);
      else if (failed) fail(failed);
    });
  }
})();
