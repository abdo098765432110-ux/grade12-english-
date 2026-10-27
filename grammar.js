/* Grammar Lessons page.
     grammar.html               all lessons, grouped by unit
     grammar.html?unit=<id>     the lessons of one unit
     grammar.html?topic=<id>    one lesson (topic). ?lesson=<id> also works. */
(function () {
  'use strict';

  var G12 = window.G12;
  var Schema = G12.Schema;
  var el = G12.el;
  var t = G12.t;
  var hasText = Schema.hasText;
  var root = document.getElementById('page-root');
  var PAGE = 'grammar.html';

  /* Exam settings for a lesson's questions (the same on every lesson and on
     Grammar Practice): difficulty level and number of questions. */
  var COUNT_PRESETS = [10, 15, 20, 30];
  function modes() {
    return [
      { value: 'one', label: t('One at a time — feedback after each answer') },
      { value: 'all', label: t('All at once — answer everything, then check') }
    ];
  }

  /* What the student chose for the lesson's exam. Kept in memory only (never
     saved or sent anywhere), so it survives a language change but not a
     page reload. stage: 'setup' or 'quiz'; level: 'easy', 'medium', 'hard'
     or 'mixed'; exam: the exam in progress (from buildExam). */
  function freshState(lessonId) {
    return { lessonId: lessonId, stage: 'setup', value: null, custom: '', level: 'mixed', mode: 'one', exam: null };
  }
  var quizState = freshState(null);

  G12.showPage(['units', 'lessons', 'summaries', 'questions'], function (content) {
    var topicId = G12.param('topic') || G12.param('lesson');
    if (topicId) renderLesson(content, topicId);
    else renderList(content, G12.param('unit'));
  }, function (error) {
    G12.showError(root, error, { title: t('Grammar Lessons') });
  });

  /* Switching language draws the lesson again, so answers already given to
     its questions would be cleared: ask first. */
  G12.beforeLanguageChange(function () {
    return quizState.stage === 'quiz' && G12.hasAnswers(root.querySelector('.lesson-quiz'))
      ? t('Changing the language starts the questions on this page again, and your answers so far will be cleared. Change the language?')
      : null;
  });

  function lessonHref(lesson) {
    return PAGE + '?topic=' + encodeURIComponent(lesson.id);
  }

  function questionCount(content, lessonId) {
    return content.questions.filter(function (q) { return q.topicId === lessonId; }).length;
  }

  function summaryFor(content, lessonId) {
    return content.summaries.filter(function (s) { return s.topicId === lessonId; })[0] || null;
  }

  /* ---------- Lesson list ---------- */

  function lessonCards(content, lessons, headingLevel) {
    return el('ul', { className: 'card-grid' }, lessons.map(function (lesson) {
      var count = questionCount(content, lesson.id);
      var href = lessonHref(lesson);
      return el('li', { className: 'card' }, [
        el(headingLevel, { dir: 'auto' }, [el('a', { href: href, text: lesson.title })]),
        hasText(lesson.description) ? el('p', { dir: 'auto', text: lesson.description }) : null,
        G12.badges(lesson),
        el('div', { className: 'card-actions' }, [
          el('a', { className: 'btn', href: href, text: t('Read lesson'), 'aria-label': t('Read lesson: {title}', { title: lesson.title }) }),
          count ? el('a', { href: 'practice.html?topic=' + encodeURIComponent(lesson.id), text: t('Practise ({questions})', { questions: G12.plural(count, 'question') }) }) : null
        ])
      ]);
    }));
  }

  /* One unit: heading, description, and its lessons or "no lessons yet". */
  function unitSection(content, group, headingLevel, linkHeading) {
    var unit = group.unit;
    var title = unit ? unit.title : t('Other topics');
    var headingId = 'unit-' + (unit ? unit.id : 'other');
    var heading = el(headingLevel, { id: headingId, dir: 'auto' },
      linkHeading && unit ? [el('a', { href: G12.unitHref(PAGE, unit.id), text: title })] : [title]);
    var section = el('section', { className: 'unit-section', 'aria-labelledby': headingId }, [heading]);
    if (unit && hasText(unit.description)) section.appendChild(el('p', { className: 'unit-description', dir: 'auto', text: unit.description }));
    if (group.items.length) {
      section.appendChild(lessonCards(content, group.items, headingLevel === 'h2' ? 'h3' : 'h2'));
    } else {
      section.appendChild(el('p', { className: 'unit-empty', text: t('No lessons in this unit yet.') }));
    }
    return section;
  }

  function renderList(content, unitId) {
    G12.setTitle(t('Grammar Lessons'));
    G12.clear(root);
    root.appendChild(el('h1', { text: t('Grammar Lessons') }));
    root.appendChild(el('p', { className: 'lead', text: t('Choose a lesson to read the explanation and examples.') }));
    var skipped = G12.skippedNotice(content, ['units', 'lessons']);
    if (skipped) root.appendChild(skipped);

    if (content.lessons.length === 0 && content.units.length === 0) {
      root.appendChild(G12.emptyState(
        t('No lessons added yet'),
        t('Grammar lessons will appear here once they are added in the content manager.'),
        [{ label: t('Add a lesson'), href: G12.MANAGER_PAGE + '#lessons/new' }]
      ));
      return;
    }

    var nav = G12.unitNav(content.units, unitId, PAGE, G12.countByUnit(content.lessons));
    if (nav) root.appendChild(nav);
    var groups = Schema.groupByUnit(content.lessons, content.units, content.lessons);

    if (unitId) {
      var group = groups.filter(function (g) { return g.unit && g.unit.id === unitId; })[0];
      if (!group) {
        G12.unitNotFound(root, PAGE, 'lessons');
        return;
      }
      G12.setTitle(group.unit.title + ' — ' + t('Grammar Lessons'));
      var notice = G12.listReviewNotice(group.items);
      if (notice) root.appendChild(notice);
      if (group.items.length === 0) {
        root.appendChild(el('h2', { dir: 'auto', text: group.unit.title }));
        root.appendChild(G12.emptyState(
          t('No lessons in this unit yet'),
          t('Lessons for this unit will appear here once they are added in the content manager.'),
          [{ label: t('Show all units'), href: PAGE }],
          'h3'
        ));
        return;
      }
      root.appendChild(unitSection(content, group, 'h2', false));
      return;
    }

    var allNotice = G12.listReviewNotice(content.lessons);
    if (allNotice) root.appendChild(allNotice);

    if (content.units.length === 0) {
      root.appendChild(lessonCards(content, content.lessons, 'h2'));
      return;
    }
    groups.forEach(function (g) {
      root.appendChild(unitSection(content, g, 'h2', true));
    });
  }

  /* ---------- One lesson ---------- */

  function renderLesson(content, id) {
    G12.clear(root);
    var ordered = Schema.orderByUnit(content.lessons, content.units, content.lessons);
    var index = -1;
    ordered.forEach(function (lesson, i) { if (lesson.id === id) index = i; });

    if (index === -1) {
      G12.setTitle(t('Lesson not found'));
      root.appendChild(el('h1', { text: t('Lesson not found') }));
      root.appendChild(el('p', { text: t('This lesson does not exist or has been removed.') }));
      root.appendChild(el('a', { className: 'btn', href: PAGE, text: t('Back to all lessons') }));
      return;
    }

    var lesson = ordered[index];
    var unit = Schema.findById(content.units, lesson.unitId);
    G12.setTitle(lesson.title);

    var crumbs = [el('li', null, [el('a', { href: PAGE, text: t('Grammar Lessons') })])];
    if (unit) crumbs.push(el('li', null, [el('a', { href: G12.unitHref(PAGE, unit.id), dir: 'auto', text: unit.title })]));
    crumbs.push(el('li', null, [el('span', { 'aria-current': 'page', dir: 'auto', text: lesson.title })]));
    root.appendChild(el('nav', { className: 'breadcrumb', 'aria-label': t('Breadcrumb') }, [el('ol', null, crumbs)]));

    root.appendChild(el('h1', { dir: 'auto', text: lesson.title }));
    if (hasText(lesson.description)) {
      root.appendChild(el('p', { className: 'lead', dir: 'auto', text: lesson.description }));
    }
    root.appendChild(G12.badges(lesson, [unit ? unit.title : null]));
    var notice = G12.reviewNotice(lesson, 'lesson');
    if (notice) root.appendChild(notice);

    var lessonQuestions = content.questions.filter(function (q) { return q.topicId === lesson.id; });
    var body = el('div', { className: 'lesson-body', dir: 'auto' });
    if (lesson.sections.length === 0 && lessonQuestions.length === 0) {
      body.appendChild(el('p', { text: t('This lesson has no content yet.') }));
    }
    lesson.sections.forEach(function (section, i) {
      body.appendChild(renderSection(section, i));
    });
    var toc = contents(lesson.sections);
    if (toc) root.appendChild(toc);
    if (body.childNodes.length) root.appendChild(body);

    /* The lesson's questions: first "How many questions?", then the quiz. */
    if (lessonQuestions.length) {
      if (quizState.lessonId !== lesson.id) {
        quizState = freshState(lesson.id);
      }
      var questionArea = el('section', { className: 'lesson-questions', 'aria-label': t('Questions about {title}', { title: lesson.title }) });
      G12.ignoreDoubleClicks(questionArea);
      root.appendChild(questionArea);
      if (quizState.stage === 'quiz' && quizState.exam) showLessonQuiz(questionArea, lesson, lessonQuestions, quizState.exam, false);
      else showLessonSetup(questionArea, lesson, lessonQuestions, false);
    }

    var summary = summaryFor(content, lesson.id);
    var count = questionCount(content, lesson.id);
    var links = [];
    if (summary) links.push(el('a', { className: 'btn btn--secondary', href: 'summaries.html?topic=' + encodeURIComponent(lesson.id), text: t('Read the summary') }));
    if (count) links.push(el('a', { className: 'btn', href: 'practice.html?topic=' + encodeURIComponent(lesson.id), text: t('Practise this topic ({questions})', { questions: G12.plural(count, 'question') }) }));
    if (links.length) {
      root.appendChild(el('section', { className: 'next-steps', 'aria-labelledby': 'next-steps-heading' }, [
        el('h2', { id: 'next-steps-heading', text: t('Next steps') }),
        el('div', { className: 'actions' }, links)
      ]));
    }

    var previous = ordered[index - 1];
    var next = ordered[index + 1];
    root.appendChild(el('nav', { className: 'pager', 'aria-label': t('Other lessons') }, [
      previous ? el('a', { href: lessonHref(previous), text: t('← {title}', { title: previous.title }) }) : el('span'),
      next ? el('a', { href: lessonHref(next), text: t('{title} →', { title: next.title }) }) : el('span')
    ]));
  }

  /* Exam settings: difficulty level, number of questions (a preset, all or a
     custom number) and how to answer. Nothing starts until the student
     presses Start quiz. */
  function showLessonSetup(area, lesson, questions, moveFocus) {
    quizState.stage = 'setup';
    quizState.exam = null;
    G12.clear(area);

    var heading = el('h2', { id: 'lesson-quiz-heading', tabindex: '-1', text: t('Quiz') });
    var settings = G12.examSettings({
      id: 'lesson',
      questions: questions,
      presets: COUNT_PRESETS,
      level: quizState.level,
      value: quizState.value,
      custom: quizState.custom,
      hint: t('Questions are chosen at random from the level you choose, in a random order, and never twice in the same exam.'),
      onChange: function (state) {
        quizState.level = state.level;
        quizState.value = state.value;
        quizState.custom = state.custom;
      }
    });
    var modeRow = el('fieldset', { className: 'form-row' }, [
      el('legend', { text: t('How do you want to answer?') }),
      el('div', { className: 'inline-choices' }, modes().map(function (mode) {
        var id = 'lesson-mode-' + mode.value;
        return el('label', { for: id }, [
          el('input', { type: 'radio', id: id, name: 'lesson-mode', value: mode.value, checked: quizState.mode === mode.value }),
          mode.label
        ]);
      }))
    ]);
    modeRow.addEventListener('change', function (event) { quizState.mode = event.target.value; });

    var form = el('form', { className: 'panel quiz-setup', 'aria-labelledby': 'lesson-quiz-heading', novalidate: true }, [
      heading,
      el('p', { text: t('This lesson has {questions}.', { questions: G12.plural(questions.length, 'question') }) })
    ].concat(settings.elements, [
      modeRow,
      el('div', { className: 'actions' }, [el('button', { type: 'submit', className: 'btn', text: t('Start quiz') })])
    ]));
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var chosen = settings.read();
      if (chosen.error) return;
      var exam = G12.QuizEngine.buildExam(questions, { level: chosen.level, count: chosen.count });
      exam.level = chosen.level;
      showLessonQuiz(area, lesson, questions, exam, true);
    });
    area.appendChild(form);
    if (moveFocus) G12.focus(heading);
  }

  /* The exam itself: the chosen questions in a random order, one at a time
     (feedback after each answer) or all at once. */
  function showLessonQuiz(area, lesson, questions, exam, moveFocus) {
    quizState.stage = 'quiz';
    quizState.exam = exam;
    G12.clear(area);
    function back() { showLessonSetup(area, lesson, questions, true); }

    area.appendChild(el('p', null, [
      el('button', { type: 'button', className: 'btn btn--link', text: t('← Change quiz settings'), onclick: back })
    ]));
    var notice = G12.examNotice(exam, exam.level);
    if (notice) area.appendChild(notice);
    var holder = el('div', { className: 'lesson-quiz' });
    area.appendChild(holder);
    var label = t('Questions about {title}', { title: lesson.title });
    var actions = [{ label: t('Change quiz settings'), onClick: back }];
    if (quizState.mode === 'all') {
      G12.renderWorksheet(holder, exam.questions, { label: label, title: t('Questions'), resultActions: actions });
    } else {
      G12.renderQuiz(holder, exam.questions, { label: label, shuffle: false, resultActions: actions });
    }
    if (moveFocus) G12.focus(holder.querySelector('h2'));
  }

  /* ---------- Lesson sections ---------- */

  /* A long lesson gets a contents list (folded until opened) with links to
     its main headings: the numbered ones ("1.1 …", "Part 2 …") when there
     are some, otherwise every heading. */
  function contents(sections) {
    var headed = [];
    sections.forEach(function (section, i) {
      if (hasText(section.heading)) headed.push({ index: i, text: section.heading });
    });
    if (headed.length < 8) return null;
    var numbered = headed.filter(function (h) { return /^(Part \d+|\d+\.\d+)\b/.test(h.text); });
    var list = numbered.length >= 4 ? numbered : headed;
    return el('details', { className: 'toc lesson-toc' }, [
      el('summary', { text: t('Contents of this lesson ({n})', { n: list.length }) }),
      el('ul', null, list.map(function (h) {
        return el('li', { className: /^Part \d+/.test(h.text) ? 'lesson-toc-part' : null }, [
          el('a', { href: '#lesson-part-' + (h.index + 1), dir: 'auto' }, mixedHeading(h.text))
        ]);
      }))
    ]);
  }

  /* Lesson text often mixes Arabic and English. Each stretch written in the
     other language is isolated (<bdi>) so it keeps its own reading order, for
     example an English sentence and its full stop inside an Arabic
     explanation. The text itself is not changed. */
  var FIRST_LETTER = /[A-Za-z\u0621-\u064A]/;
  var ARABIC_LETTER = /[\u0621-\u064A]/;

  function mixed(text) {
    text = String(text);
    var first = text.match(FIRST_LETTER);
    if (!first) return [text];
    var rtl = ARABIC_LETTER.test(first[0]);
    // a hyphen written straight before a Latin word ("-ing") belongs to that word
    var pattern = rtl ? /-?[A-Za-z0-9][^\u0600-\u06FF]*/g : /[\u0621-\u064A][^A-Za-z]*/g;
    var endOk = rtl ? /[A-Za-z0-9.?!'’”…%]/ : /[\u0621-\u0652\u0660-\u0669.؟!،…»]/;
    var out = [];
    var last = 0;
    var match;
    while ((match = pattern.exec(text))) {
      var run = match[0];
      // keep a closing bracket only when its opening bracket is inside the stretch
      while (run && !endOk.test(run.slice(-1)) && !(run.slice(-1) === ')' && run.split('(').length > run.slice(0, -1).split(')').length)) {
        run = run.slice(0, -1);
      }
      if (!run) continue;
      if (match.index > last) out.push(text.slice(last, match.index));
      out.push(el('bdi', { dir: rtl ? 'ltr' : 'rtl', text: run }));
      last = match.index + run.length;
      pattern.lastIndex = last;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
  }

  /* Headings are "English — Arabic": each part keeps its own direction. */
  function mixedHeading(text) {
    var parts = String(text).split(' — ');
    var out = [];
    parts.forEach(function (part, i) {
      if (i > 0) out.push(' — ');
      var first = part.match(FIRST_LETTER);
      out.push(first ? el('bdi', { dir: ARABIC_LETTER.test(first[0]) ? 'rtl' : 'ltr', text: part }) : part);
    });
    return out;
  }

  function heading(section) {
    return G12.Schema.hasText(section.heading) ? el('h2', { dir: 'auto' }, mixedHeading(section.heading)) : null;
  }

  function paragraphs(list) {
    return list.filter(G12.Schema.hasText).map(function (text) {
      return el('p', { dir: 'auto' }, mixed(text));
    });
  }

  function renderSection(section, index) {
    var wrapper = el('section', { className: 'lesson-section', id: 'lesson-part-' + (index + 1) });
    if (section.lang === 'ar') {
      wrapper.setAttribute('lang', 'ar');
      wrapper.setAttribute('dir', 'rtl');
    }

    switch (section.type) {
      case 'text':
        wrapper.appendChild(el('div', { className: 'prose' }, [heading(section), paragraphs(section.paragraphs)]));
        break;

      case 'note':
        wrapper.appendChild(el('div', { className: 'callout', role: 'note' }, [heading(section), paragraphs(section.paragraphs)]));
        break;

      case 'list':
        wrapper.appendChild(heading(section) || document.createTextNode(''));
        wrapper.appendChild(el('ul', { className: 'prose', dir: 'auto' }, section.items.filter(G12.Schema.hasText).map(function (item) {
          return el('li', { dir: 'auto' }, mixed(item));
        })));
        break;

      case 'examples':
        wrapper.appendChild(heading(section) || document.createTextNode(''));
        wrapper.appendChild(el('ul', { className: 'example-list', dir: 'auto' }, section.items.filter(G12.Schema.hasText).map(function (item) {
          return el('li', { dir: 'auto' }, mixed(item));
        })));
        break;

      case 'table':
        wrapper.appendChild(heading(section) || document.createTextNode(''));
        wrapper.appendChild(el('div', { className: 'table-wrap', dir: 'auto', tabindex: '0', role: 'region', 'aria-label': section.heading || t('Table') }, [
          el('table', null, [
            el('thead', null, [el('tr', null, section.columns.map(function (column) {
              return el('th', { scope: 'col', dir: 'auto', text: column });
            }))]),
            el('tbody', null, section.rows.map(function (row) {
              return el('tr', null, row.map(function (cell, i) {
                // the column name is shown above each cell when the table is stacked on phones
                return el('td', { dir: 'auto', 'data-label': section.columns[i] || '' }, mixed(cell));
              }));
            }))
          ])
        ]));
        break;

      case 'mistakes':
        wrapper.appendChild(heading(section) || document.createTextNode(''));
        wrapper.appendChild(el('ul', { className: 'mistake-list' }, section.items.map(function (item) {
          return el('li', null, [
            el('p', null, [el('span', { className: 'label-avoid', text: t('✗ Avoid:') + ' ' }), el('span', { className: 'text-avoid', dir: 'auto' }, mixed(item.avoid))]),
            el('p', null, [el('span', { className: 'label-use', text: t('✓ Use:') + ' ' }), el('span', { dir: 'auto' }, mixed(item.use))]),
            G12.Schema.hasText(item.note) ? el('p', { className: 'hint', dir: 'auto' }, mixed(item.note)) : null
          ]);
        })));
        break;
    }
    return wrapper;
  }
})();
