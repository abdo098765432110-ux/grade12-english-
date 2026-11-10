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
   "download"; a chapter may also list PDFs of some of its sections ("morePdfs":
   { file, title, sections, note? }, with "pdfTitle" naming the chapter PDF), each
   shown as one more panel ("note" replaces the line under its title). Sections
   listed in "morePdfs" are not counted for the chapter PDF or for the PDF at the
   top of the file, which "pdfTitle" at the top of the file may name.
   A chapter may group its sections into lessons ("lessons": [{ id, number, title,
   sections: [ids] }], for example "الدرس الأول" and the lesson's name): the chapter
   page then shows one card per lesson with a button for each of its sections (the
   section's short "label"), and the questions page shows the lesson above them.
   A chapter may also have a random exam ("exam": { title, note, sections: [ids],
   presets }): a card on the chapter page opens physics.html?chapter=<id>&exam=1,
   where the student chooses the number of questions and the level (Easy, Medium,
   Hard — which includes the very hard questions — or Mixed); the questions are
   drawn at random from those sections, never twice, and the quiz ends with the
   score and a review of every answer.
   Optional, on the page: data-open-label on the content area
   (the chapter button's text) and data-subject-home on any part of the page
   that should show only on the first step (the Arabic page's PDFs).
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
  var examRun = null;       // the exam being solved: { chapter, settings, exam }
  var examSetup = null;     // the last exam settings chosen: { level, value, custom }

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
  function answersPdf(file, title, count, note) {
    var icon = titleBox ? titleBox.querySelector('img') : null;
    return el('div', { className: 'summary-pdf questions-pdf' + (tone ? ' ' + tone : '') }, [
      icon ? el('img', { className: 'summary-pdf-icon', src: icon.getAttribute('src'), alt: '', width: '56', height: '56' }) : null,
      el('div', { className: 'summary-pdf-text' }, [
        el('p', { className: 'summary-pdf-title', dir: 'auto', lang: langOf(title), text: title }),
        hasText(note)
          ? el('p', { className: 'hint', dir: 'auto', lang: langOf(note), text: G12.plural(count, 'question') + ' · ' + note })
          : el('p', { className: 'hint', text: t('{questions} · answer key at the end · PDF file, A4 pages', { questions: G12.plural(count, 'question') }) }),
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
      return card('h2', chapter.title, hrefFor(chapter), countOf(sectionsOf(chapter)), area.getAttribute('data-open-label') || t('Open the chapter'));
    })));
    if (hasText(data && data.pdf)) {
      // sections with a PDF of their own (a chapter's "morePdfs") are not in this one
      var total = chapters.reduce(function (sum, chapter) {
        var own = {};
        morePdfsOf(chapter).forEach(function (item) { item.sections.forEach(function (id) { own[id] = true; }); });
        return sum + countOf(sectionsOf(chapter).filter(function (section) { return !own[section.id]; }));
      }, 0);
      area.appendChild(answersPdf(data.pdf, hasText(data.pdfTitle) ? data.pdfTitle : t('All the questions with their answers'), total));
    }
  }

  /* The extra PDFs of a chapter ("morePdfs"), leaving out broken entries. */
  function morePdfsOf(chapter) {
    return list(chapter.morePdfs).filter(function (item) { return item && hasText(item.file) && hasText(item.title) && Array.isArray(item.sections); });
  }

  /* The lessons of a chapter ("lessons"), each with its usable sections in order. */
  function lessonsOf(chapter) {
    var sections = sectionsOf(chapter);
    return list(chapter && chapter.lessons).map(function (lesson) {
      if (!lesson || !hasText(lesson.title)) return null;
      var own = list(lesson.sections).map(function (id) { return find(sections, id); }).filter(Boolean);
      return own.length ? { id: lesson.id, number: lesson.number, title: lesson.title, sections: own } : null;
    }).filter(Boolean);
  }

  /* The lesson a section belongs to, with its place in the chapter (1, 2, …). */
  function lessonOf(chapter, section) {
    var lessons = lessonsOf(chapter);
    for (var i = 0; i < lessons.length; i++) {
      if (lessons[i].sections.indexOf(section) !== -1) return { lesson: lessons[i], position: i + 1 };
    }
    return null;
  }

  /* The lesson's name above its questions, or as the head of its card. */
  function lessonHead(lesson, position, headingTag) {
    return el('div', { className: 'lesson-head', lang: 'ar', dir: 'rtl' }, [
      el('span', { className: 'lesson-number', 'aria-hidden': 'true', text: String(position) }),
      el('div', { className: 'lesson-name' }, [
        hasText(lesson.number) ? el('span', { className: 'lesson-kicker', text: lesson.number }) : null,
        el(headingTag, { className: 'lesson-title', text: lesson.title })
      ])
    ]);
  }

  function lessonCard(chapter, lesson, position) {
    return el('li', { className: 'card lesson-card' + (tone ? ' ' + tone : '') }, [
      lessonHead(lesson, position, 'h3'),
      el('div', { className: 'card-actions lesson-actions' }, lesson.sections.map(function (section, i) {
        var label = hasText(section.label) ? section.label : section.title;
        return el('a', {
          className: 'btn' + (i ? ' btn--secondary' : ''), href: hrefFor(chapter, section), lang: langOf(label), dir: 'auto',
          text: t('{title} ({count})', { title: label, count: usable(section.questions).length })
        });
      }))
    ]);
  }

  /* The questions a chapter's exam draws from (multiple-choice questions of its sections). */
  function examOf(chapter) {
    var exam = chapter && chapter.exam;
    if (!exam || !hasText(exam.title)) return null;
    var sections = sectionsOf(chapter);
    var questions = [];
    list(exam.sections).forEach(function (id) {
      var section = find(sections, id);
      if (section) questions = questions.concat(usable(section.questions).filter(function (q) { return q.type === 'mcq'; }));
    });
    return questions.length ? { title: exam.title, note: exam.note, presets: list(exam.presets), questions: questions } : null;
  }

  function examHref(chapter) {
    return page + '?chapter=' + encodeURIComponent(chapter.id) + '&exam=1';
  }

  /* "Hard" in an exam takes the hard and the very hard questions. */
  function examLevel(question) {
    return question.difficulty === 'very-hard' ? 'hard' : question.difficulty;
  }

  /* Step 2: the sections of one chapter. */
  function drawChapter(chapter) {
    G12.setTitle(chapter.title + ' — ' + subjectName);
    area.appendChild(breadcrumb([{ label: subjectName, href: page }, { label: chapter.title }]));
    area.appendChild(el('h2', { className: 'subject-step-title', dir: 'auto', lang: langOf(chapter.title), text: chapter.title }));
    var lessons = lessonsOf(chapter);
    var inLesson = [];
    lessons.forEach(function (lesson) { inLesson = inLesson.concat(lesson.sections); });
    if (lessons.length) {
      area.appendChild(el('ol', { className: 'card-grid subject-cards lesson-list', 'aria-label': chapter.title }, lessons.map(function (lesson, i) {
        return lessonCard(chapter, lesson, i + 1);
      })));
    }
    var cards = sectionsOf(chapter).filter(function (section) { return inLesson.indexOf(section) === -1; }).map(function (section) {
      var extra = hasText(section.pdf) ? [downloadLink(section.pdf, t('Download Questions'))] : [];
      return card('h3', section.title, hrefFor(chapter, section), usable(section.questions).length, t('Start practising'), null, extra);
    });
    var exam = examOf(chapter);
    if (exam) {
      cards.push(card('h3', exam.title, examHref(chapter), 0, t('Set up the exam'),
        t('{questions} to choose from', { questions: G12.plural(exam.questions.length, 'question') })));
    }
    var sheet = chapter.revision;
    if (sheet && hasText(sheet.title) && hasText(sheet.page)) {
      var extra = [];
      if (hasText(sheet.pdf)) extra.push(downloadLink(sheet.pdf, t('Download Revision Sheet')));
      extra.push(el('a', { className: 'btn btn--secondary', href: sheet.page + '?print=1', text: t('Print Revision Sheet') }));
      cards.push(card('h3', sheet.title, sheet.page, 0, t('Open the revision sheet'), t('Laws and key ideas · A4'), extra));
    }
    if (cards.length) area.appendChild(el('ul', { className: 'card-grid subject-cards', 'aria-label': chapter.title }, cards));
    // More PDFs for some sections only ("morePdfs": [{ file, title, sections: [ids] }]);
    // the chapter PDF then counts the other sections, under its own title ("pdfTitle") if given.
    var more = morePdfsOf(chapter);
    var elsewhere = {};
    more.forEach(function (item) { item.sections.forEach(function (id) { elsewhere[id] = true; }); });
    if (hasText(chapter.pdf)) {
      area.appendChild(answersPdf(chapter.pdf, hasText(chapter.pdfTitle) ? chapter.pdfTitle : t('All the questions of this chapter with their answers'),
        countOf(sectionsOf(chapter).filter(function (section) { return !elsewhere[section.id]; }))));
    }
    more.forEach(function (item) {
      area.appendChild(answersPdf(item.file, item.title,
        countOf(sectionsOf(chapter).filter(function (section) { return item.sections.indexOf(section.id) !== -1; })), item.note));
    });
  }

  /* Step 3: the questions of one section. */
  function drawSection(chapter, section) {
    G12.setTitle(section.title + ' — ' + subjectName);
    area.appendChild(breadcrumb([
      { label: subjectName, href: page },
      { label: chapter.title, href: hrefFor(chapter) },
      { label: section.title }
    ]));
    var found = lessonOf(chapter, section);
    var headingId = 'questions-' + section.id;
    var quizArea = el('div', { className: 'section-quiz' });
    var heading = found && hasText(section.label) ? section.label : section.title;
    area.appendChild(el('section', { className: 'question-section', 'aria-labelledby': headingId }, [
      found ? el('div', { className: 'lesson-banner' + (tone ? ' ' + tone : '') }, [lessonHead(found.lesson, found.position, 'p')]) : null,
      el('h2', { id: headingId, className: 'question-section-title', dir: 'auto', lang: langOf(heading), text: heading }),
      hasText(section.pdf) ? el('div', { className: 'section-downloads' }, [
        downloadLink(section.pdf, t('Download Questions'), 'btn btn--secondary'),
        el('span', { className: 'hint', text: t('All the questions in one PDF file (A4), with numbers and diagrams.') })
      ]) : null,
      quizArea
    ]));
    // navigator: the panel of question numbers beside the question
    G12.renderQuiz(quizArea, usable(section.questions), { label: section.title, shuffle: false, navigator: true });
  }

  /* Step 2b: the chapter's random exam: choose the number of questions and the
     level, then solve them (score and review at the end). */
  function drawExam(chapter, exam) {
    G12.setTitle(exam.title + ' — ' + subjectName);
    area.appendChild(breadcrumb([
      { label: subjectName, href: page },
      { label: chapter.title, href: hrefFor(chapter) },
      { label: exam.title }
    ]));
    area.appendChild(el('h2', { className: 'subject-step-title', dir: 'auto', lang: langOf(exam.title), text: exam.title }));
    var setupArea = el('div', { className: 'exam-setup' });
    var quizArea = el('div', { className: 'section-quiz' });
    area.appendChild(setupArea);
    area.appendChild(quizArea);

    function showSetup(moveFocus) {
      examRun = null;
      G12.clear(quizArea);
      G12.clear(setupArea);
      setupArea.hidden = false;
      var settings = examSetup || { level: 'mixed', value: 10, custom: '' };
      var choice = G12.examSettings({
        id: 'chapter-exam',
        questions: exam.questions,
        levelOf: examLevel,
        presets: exam.presets.length ? exam.presets : [10, 20, 30],
        level: settings.level,
        value: settings.value,
        custom: settings.custom,
        hint: t('Questions are chosen at random from the level you choose, in a random order, and never twice in the same exam.'),
        onChange: function (state) { examSetup = state; }
      });
      var heading = el('h3', { id: 'exam-setup-heading', text: t('Exam settings'), tabindex: '-1' });
      var rows = [heading];
      if (hasText(exam.note)) rows.push(el('p', { className: 'hint', dir: 'auto', lang: langOf(exam.note), text: exam.note }));
      rows = rows.concat(choice.elements);
      rows.push(el('p', { className: 'hint exam-level-note', text: t('“Hard” includes the hard and the very hard questions.') }));
      rows.push(el('div', { className: 'actions' }, [el('button', { type: 'submit', className: 'btn', text: t('Start the exam') })]));
      var form = el('form', { className: 'panel exam-form', 'aria-labelledby': 'exam-setup-heading', novalidate: true }, rows);
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        var chosen = choice.read();
        if (chosen.error) return;
        examSetup = choice.state();
        start({ level: chosen.level, count: chosen.count });
      });
      setupArea.appendChild(form);
      if (moveFocus) G12.focus(heading);
    }

    function start(settings, built, quiet) {
      if (!built) {
        built = G12.QuizEngine.buildExam(exam.questions, { level: settings.level, count: settings.count, levelOf: examLevel });
        built.level = settings.level;
      }
      examRun = { chapter: chapter.id, settings: settings, exam: built };
      setupArea.hidden = true;
      G12.clear(quizArea);
      quizArea.appendChild(el('p', null, [
        el('button', { type: 'button', className: 'btn btn--link', text: t('← Change exam settings'), onclick: function () { showSetup(true); } })
      ]));
      var notice = G12.examNotice(built, built.level);
      if (notice) quizArea.appendChild(notice);
      var holder = el('div');
      quizArea.appendChild(holder);
      G12.renderQuiz(holder, built.questions, {
        label: exam.title, shuffle: false, navigator: true,
        resultActions: [
          { label: t('New exam with the same settings'), onClick: function () { start(settings); } },
          { label: t('Change exam settings'), onClick: function () { showSetup(true); } }
        ]
      });
      if (!quiet) G12.focus(holder.querySelector('h2'));
    }

    // after a language change, the exam being solved is drawn again (from its first question)
    if (examRun && examRun.chapter === chapter.id) start(examRun.settings, examRun.exam, true);
    else showSetup(false);
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
    // parts of the page marked data-subject-home show only on the first step
    Array.prototype.forEach.call(document.querySelectorAll('[data-subject-home]'), function (node) { node.hidden = !!chapterId; });
    if (!chapterId) {
      drawChapters(chapters, data);
      return;
    }
    var chapter = find(chapters, chapterId);
    if (!chapter) {
      notFound(null);
      return;
    }
    if (!sectionId && G12.param('exam')) {
      var exam = examOf(chapter);
      if (exam) drawExam(chapter, exam);
      else notFound(chapter);
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
