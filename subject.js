/* Subject pages (physics.html and, later, the other subjects).
   The content area names its data file in data-questions, for example
     <div class="subject-content" data-questions="physics-questions.json">
   The file groups the questions into chapters, and each chapter into sections:
     { "schemaVersion": 2, "chapters": [
         { "id": "chapter-1", "title": "الفصل الأول", "sections": [
             { "id": "chapter-1-questions", "title": "أسئلة على الفصل الأول", "questions": [ … ] } ] } ] }

   The student goes one step at a time; the questions appear only at the end:
     physics.html                                        the chapters
     physics.html?chapter=chapter-1                      the sections of that chapter
     physics.html?chapter=chapter-1&section=<id>         the questions of that section
   A section may name a PDF of its questions ("pdf"); a chapter may have a
   revision sheet ("revision": { title, page, pdf }), shown as a second card
   on the chapter page with "open", "download" and "print". A PDF of all the
   questions with their answers ("pdf" at the top of the file, or on a chapter;
   made by tools/question_pdfs.py) is shown under the cards with "view" and
   "download".
   The questions use the shared quiz (quiz-ui.js): one question at a time, with
   instant feedback, the correct answer and the explanation, and a panel of
   question numbers to jump to any question. Questions use the
   same format as the grammar questions; a broken question is skipped. Drawn
   again when the interface language changes. */
(function () {
  'use strict';

  var G12 = window.G12;
  var el = G12.el;
  var t = G12.t;
  var area = document.querySelector('[data-questions]');
  if (!area) return;

  var file = area.getAttribute('data-questions');
  var page = window.location.pathname.split('/').pop() || 'index.html';
  var titleBox = document.querySelector('.subject-title');
  var subjectName = titleBox ? titleBox.querySelector('h1').textContent.trim() : '';
  var toneMatch = titleBox ? titleBox.className.match(/\btone-[a-z]+\b/) : null;
  var tone = toneMatch ? toneMatch[0] : '';
  var ARABIC = /[؀-ۿ]/;
  var loaded = null;
  var failed = null;

  function list(value) { return Array.isArray(value) ? value : []; }

  function langOf(text) { return ARABIC.test(text || '') ? 'ar' : null; }

  function usable(questions) {
    return list(questions).filter(function (question, i) {
      return G12.Schema.validateItem('questions', question, i).errors.length === 0;
    });
  }

  function find(items, id) {
    return list(items).filter(function (item) { return item && item.id === id; })[0] || null;
  }

  /* Only chapters and sections that have at least one working question are shown. */
  function sectionsOf(chapter) {
    return list(chapter && chapter.sections).filter(function (section) {
      return section && section.id && usable(section.questions).length > 0;
    });
  }

  function chaptersOf(data) {
    return list(data && data.chapters).filter(function (chapter) {
      return chapter && chapter.id && sectionsOf(chapter).length > 0;
    });
  }

  function countOf(sections) {
    return sections.reduce(function (sum, section) { return sum + usable(section.questions).length; }, 0);
  }

  function hrefFor(chapter, section) {
    var href = page + '?chapter=' + encodeURIComponent(chapter.id);
    if (section) href += '&section=' + encodeURIComponent(section.id);
    return href;
  }

  /* "الفيزياء / الفصل الأول / …": links back up, the last step is the current page. */
  function breadcrumb(steps) {
    return el('nav', { className: 'breadcrumb subject-breadcrumb', 'aria-label': t('Breadcrumb'), lang: 'ar', dir: 'rtl' }, [
      el('ol', null, steps.map(function (step, i) {
        var last = i === steps.length - 1;
        return el('li', null, [last
          ? el('span', { 'aria-current': 'page', text: step.label })
          : el('a', { href: step.href, text: step.label })]);
      }))
    ]);
  }

  /* One clickable card: the title is a link, with the number of questions and a button.
     badge: the text under the title (default: the number of questions); extra: more buttons. */
  function card(headingTag, title, href, count, buttonText, badge, extra) {
    return el('li', { className: 'card' + (tone ? ' ' + tone : '') }, [
      el(headingTag, { dir: 'auto', lang: langOf(title) }, [el('a', { href: href, text: title })]),
      el('p', { className: 'card-count', text: badge || G12.plural(count, 'question') }),
      el('div', { className: 'card-actions' }, [el('a', { className: 'btn', href: href, text: buttonText })].concat(extra || []))
    ]);
  }

  /* A link that downloads a PDF file (the browser saves it, or opens it on some phones). */
  function downloadLink(file, text, className) {
    return el('a', { className: className || 'btn btn--secondary', href: file, download: '', type: 'application/pdf', text: text });
  }

  function hasText(value) { return typeof value === 'string' && value.trim() !== ''; }

  /* A PDF of all the questions with their answers ("pdf" at the top of the data
     file, or on a chapter): view it in the browser or download it. */
  function answersPdf(file, title, count) {
    var icon = titleBox ? titleBox.querySelector('img') : null;
    return el('div', { className: 'summary-pdf questions-pdf' + (tone ? ' ' + tone : '') }, [
      icon ? el('img', { className: 'summary-pdf-icon', src: icon.getAttribute('src'), alt: '', width: '56', height: '56' }) : null,
      el('div', { className: 'summary-pdf-text' }, [
        el('p', { className: 'summary-pdf-title', text: title }),
        el('p', { className: 'hint', text: t('{questions} · the correct answer after each question · PDF file, A4 pages', { questions: G12.plural(count, 'question') }) }),
        el('div', { className: 'actions' }, [
          el('a', { className: 'btn', href: file, target: '_blank', rel: 'noopener', type: 'application/pdf', text: t('View PDF') }),
          el('a', { className: 'btn btn--secondary', href: file, download: '', type: 'application/pdf', text: t('Download PDF') })
        ])
      ])
    ]);
  }

  /* Step 1: the chapters. */
  function drawChapters(chapters, data) {
    G12.setTitle(subjectName);
    if (!chapters.length) {
      area.appendChild(el('div', { className: 'empty-state' }, [
        el('h2', { text: t('No content added yet') }),
        el('p', { text: t('Lessons for this subject will appear here when they are added.') })
      ]));
      return;
    }
    area.appendChild(el('ul', { className: 'card-grid subject-cards', 'aria-label': subjectName }, chapters.map(function (chapter) {
      return card('h2', chapter.title, hrefFor(chapter), countOf(sectionsOf(chapter)), t('Open the chapter'));
    })));
    if (hasText(data && data.pdf)) {
      var total = chapters.reduce(function (sum, chapter) { return sum + countOf(sectionsOf(chapter)); }, 0);
      area.appendChild(answersPdf(data.pdf, t('All the questions with their answers'), total));
    }
  }

  /* Step 2: the sections of one chapter. */
  function drawChapter(chapter) {
    G12.setTitle(chapter.title + ' — ' + subjectName);
    area.appendChild(breadcrumb([{ label: subjectName, href: page }, { label: chapter.title }]));
    area.appendChild(el('h2', { className: 'subject-step-title', dir: 'auto', lang: langOf(chapter.title), text: chapter.title }));
    var cards = sectionsOf(chapter).map(function (section) {
      var extra = hasText(section.pdf) ? [downloadLink(section.pdf, t('Download Questions'))] : [];
      return card('h3', section.title, hrefFor(chapter, section), usable(section.questions).length, t('Start practising'), null, extra);
    });
    var sheet = chapter.revision;
    if (sheet && hasText(sheet.title) && hasText(sheet.page)) {
      var extra = [];
      if (hasText(sheet.pdf)) extra.push(downloadLink(sheet.pdf, t('Download Revision Sheet')));
      extra.push(el('a', { className: 'btn btn--secondary', href: sheet.page + '?print=1', text: t('Print Revision Sheet') }));
      cards.push(card('h3', sheet.title, sheet.page, 0, t('Open the revision sheet'), t('Laws and key ideas · A4'), extra));
    }
    area.appendChild(el('ul', { className: 'card-grid subject-cards', 'aria-label': chapter.title }, cards));
    if (hasText(chapter.pdf)) {
      area.appendChild(answersPdf(chapter.pdf, t('All the questions of this chapter with their answers'), countOf(sectionsOf(chapter))));
    }
  }

  /* Step 3: the questions of one section. */
  function drawSection(chapter, section) {
    G12.setTitle(section.title + ' — ' + subjectName);
    area.appendChild(breadcrumb([
      { label: subjectName, href: page },
      { label: chapter.title, href: hrefFor(chapter) },
      { label: section.title }
    ]));
    var headingId = 'questions-' + section.id;
    var quizArea = el('div', { className: 'section-quiz' });
    area.appendChild(el('section', { className: 'question-section', 'aria-labelledby': headingId }, [
      el('h2', { id: headingId, className: 'question-section-title', dir: 'auto', lang: langOf(section.title), text: section.title }),
      hasText(section.pdf) ? el('div', { className: 'section-downloads' }, [
        downloadLink(section.pdf, t('Download Questions'), 'btn btn--secondary'),
        el('span', { className: 'hint', text: t('All the questions in one PDF file (A4), with numbers and diagrams.') })
      ]) : null,
      quizArea
    ]));
    // navigator: the panel of question numbers beside the question
    G12.renderQuiz(quizArea, usable(section.questions), { label: section.title, shuffle: false, navigator: true });
  }

  function notFound(chapter) {
    G12.setTitle(t('Topic not found'));
    var back = chapter ? { label: chapter.title, href: hrefFor(chapter) } : { label: subjectName, href: page };
    area.appendChild(G12.emptyState(
      t('Topic not found'),
      t('This topic does not exist or has been removed.'),
      [back]
    ));
  }

  function draw(data) {
    G12.clear(area);
    var chapters = chaptersOf(data);
    var chapterId = G12.param('chapter');
    var sectionId = G12.param('section');
    if (!chapterId) {
      drawChapters(chapters, data);
      return;
    }
    var chapter = find(chapters, chapterId);
    if (!chapter) {
      notFound(null);
      return;
    }
    if (!sectionId) {
      drawChapter(chapter);
      return;
    }
    var section = find(sectionsOf(chapter), sectionId);
    if (!section) notFound(chapter);
    else drawSection(chapter, section);
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
