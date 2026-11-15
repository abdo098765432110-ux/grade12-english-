/* ==========================================================================
   «الدكتور والمزارع» — the game page (bio-game.html).

   Screens: the entrance (المدخل) → a shift (وردية) of 5 cases → the end of
   the shift; and the mastery map (خريطة الإتقان).
   A case: the person talks (upper body), the student examines (the camera
   moves to the part: a foot, an X-ray, a plant …), answers, then sees the
   explanation from the book with the part drawn and labelled.

   The rules are in bio-game-engine.js, the drawings in bio-game-art*.js,
   the cases in bio-game-ch1.json and bio-game-ch2.json.
   ========================================================================== */
(function () {
  'use strict';

  var G12 = window.G12;
  var E = G12.BioGame;
  var A = G12.BioArt;
  var el = G12.el;
  var root = document.getElementById('bio-game');
  var FILES = ['bio-game-ch1.json', 'bio-game-ch2.json'];
  var LETTERS = 'أبجد';
  var PLACE = {
    hospital: { name: 'المستشفى', icon: '🏥', bg: 'clinic', host: 'murad', you: 'الدكتور' },
    farm: { name: 'المزرعة', icon: '🌾', bg: 'farm', host: 'abdelrahman', you: 'المزارع' }
  };
  var TYPES = {
    clinic: { name: 'العيادة', bg: 'clinic' },
    emergency: { name: 'الطوارئ', bg: 'er' },
    xray: { name: 'الأشعة', bg: 'xray' },
    lab: { name: 'معمل التحاليل', bg: 'lab' },
    followup: { name: 'متابعة مريض', bg: 'clinic' },
    why: { name: 'المريض بيسأل', bg: 'clinic' },
    lesson: { name: 'محاضرة رئيس القسم', bg: 'clinic' },
    plant: { name: 'مشكلة في نبات', bg: 'farm' },
    decision: { name: 'قرار المزارع', bg: 'farm' },
    trap: { name: 'النبات عيّان؟', bg: 'farm' },
    microscope: { name: 'الميكروسكوب', bg: 'lab' },
    experiment: { name: 'تجربة بإيدك', bg: 'lab' },
    compare: { name: 'قارن', bg: 'farm' },
    ask: { name: 'سؤال من الغيط', bg: 'farm' },
    farmlesson: { name: 'درس المهندس', bg: 'farm' }
  };

  var idx = null;
  var state = null;
  var shift = null;     // { track, level, items, at, results }
  var chapter = 1;
  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  /* ---------- Helpers ---------- */

  function html(node, markup) {
    // drawings come only from bio-game-art*.js (never from the content files)
    node.innerHTML = markup;
    return node;
  }

  function art(markup, className) {
    return html(el('div', { className: className || 'bg-art' }), markup);
  }

  function save() {
    E.save(state);
  }

  function starsText(n) {
    var s = '';
    for (var i = 0; i < E.MAX_STARS; i++) s += i < n ? '★' : '☆';
    return s;
  }

  function starsNode(n, label) {
    return el('span', { className: 'bg-stars', 'aria-label': label || (n + ' من ' + E.MAX_STARS + ' نجوم'), text: starsText(n) });
  }

  function meter(percent, label) {
    var bar = el('span', { className: 'bg-meter-fill' });
    bar.style.width = Math.max(0, Math.min(100, percent)) + '%';
    return el('div', { className: 'bg-meter', role: 'img', 'aria-label': label }, [bar]);
  }

  function tracksOf(ch) {
    return idx.content.tracks.filter(function (t) { return t.chapter === ch; });
  }

  function chapterTitle(ch) {
    var found = idx.content.chapters.filter(function (c) { return c.chapter === ch; })[0];
    return found ? found.title : 'الفصل ' + ch;
  }

  function scrollTop() {
    try { window.scrollTo({ top: Math.max(0, root.getBoundingClientRect().top + window.pageYOffset - 70), behavior: reduceMotion ? 'auto' : 'smooth' }); } catch (e) { /* old browsers */ }
  }

  /* ---------- The entrance ---------- */

  function showLobby() {
    shift = null;
    G12.clear(root);
    G12.setTitle('الدكتور والمزارع');
    var all = E.overall(idx, state);

    root.appendChild(el('section', { className: 'bg-hero' }, [
      el('div', { className: 'bg-hero-text' }, [
        el('p', { className: 'bg-kicker', text: 'لعبة أحياء — تالتة ثانوي' }),
        el('h1', { text: 'الدكتور والمزارع' }),
        el('p', { className: 'bg-lead', text: 'اشتغل دكتور في المستشفى ومزارع في المزرعة. كل حالة بتسألك في فكرة من الكتاب، ومع كل ليفل الحالات بتصعب، لحد ما كل أفكار الفصلين تتفرم عندك.' }),
        meter(all.percent, 'نسبة الإتقان ' + all.percent + '%'),
        el('p', { className: 'bg-meter-text', text: 'اتفرم ' + all.percent + '% من أفكار الفصلين — ' + all.mastered + ' من ' + all.ideas + ' فكرة خدت 3 نجوم.' }),
        el('div', { className: 'bg-hero-actions' }, [
          el('button', { type: 'button', className: 'btn btn--secondary', text: '🗺️ خريطة الإتقان', onclick: showMap })
        ])
      ]),
      art(A.scene({ who: 'murad', bg: 'clinic', mood: 'happy' }) + A.scene({ who: 'abdelrahman', bg: 'farm', mood: 'happy' }), 'bg-art bg-hero-art bg-hero-pair')
    ]));

    var tabs = el('div', { className: 'bg-tabs', role: 'tablist', 'aria-label': 'الفصول' });
    [1, 2].forEach(function (ch) {
      var has = tracksOf(ch).some(function (t) { return (idx.levels[t.id] || []).length; });
      var tab = el('button', { type: 'button', role: 'tab', className: 'bg-tab', 'aria-selected': String(chapter === ch), text: chapterTitle(ch) + (has ? '' : ' (قريبًا)') });
      tab.addEventListener('click', function () { chapter = ch; showLobby(); });
      tabs.appendChild(tab);
    });
    root.appendChild(tabs);

    var places = el('div', { className: 'bg-places', role: 'tabpanel' });
    var list = tracksOf(chapter).filter(function (t) { return (idx.levels[t.id] || []).length; });
    if (!list.length) {
      places.appendChild(el('p', { className: 'bg-soon', text: 'حالات الفصل ده لسه بتتجهز، وهتظهر هنا قريب.' }));
    }
    list.forEach(function (t) { places.appendChild(trackCard(t)); });
    root.appendChild(places);
    root.appendChild(extras());

    root.appendChild(el('details', { className: 'bg-help' }, [
      el('summary', { text: 'إزاي تلعب؟' }),
      el('ol', null, [
        el('li', { text: 'اختار المكان: المستشفى (جسم الإنسان) أو المزرعة (النبات).' }),
        el('li', { text: 'كل وردية فيها 5 حالات. اسمع الحكاية، وافحص لو فيه فحص، وبعدين جاوب.' }),
        el('li', { text: 'بعد كل إجابة هتشوف الشرح من الكتاب، والجزء مرسوم ومتوضح عليه.' }),
        el('li', { text: 'كل فكرة ليها 3 نجوم. النجمة بتيجي لما تجاوب صح على شكل جديد من الفكرة، ونجمة واحدة بس لكل فكرة في الوردية، فالنجمة التالتة دايمًا في وردية تانية.' }),
        el('li', { text: 'الإجابة الغلط بتشيل نجمة، والفكرة بترجعلك تاني بحكاية مختلفة لحد ما تتقنها.' }),
        el('li', { text: 'كل الليفلات مفتوحة: اختار الليفل اللي تحبه (من 1 السهل لـ 6 الصعب) أو «مراجعة». الليفل بيخلص لما تجاوب صح على كل أفكاره، وكل ما تخلّص ليفلات رتبتك بتعلى.' })
      ])
    ]));

    var reset = el('div', { className: 'bg-reset' });
    reset.appendChild(el('button', { type: 'button', className: 'bg-link-button', text: 'ابدأ اللعبة من الأول', onclick: function () {
      G12.clear(reset);
      reset.appendChild(el('p', { text: 'كل النجوم والليفلات اللي على الجهاز ده هتتمسح. متأكد؟' }));
      reset.appendChild(el('div', { className: 'actions' }, [
        el('button', { type: 'button', className: 'btn btn--danger', text: 'أيوه، امسح وابدأ من الأول', onclick: function () { state = E.emptyState(); save(); showLobby(); } }),
        el('button', { type: 'button', className: 'btn btn--secondary', text: 'لأ، رجوع', onclick: showLobby })
      ]));
    } }));
    root.appendChild(reset);
  }

  /* The daily challenge, the final exam and the album. */
  function extras() {
    var today = E.dayOf();
    var d = state.daily || {};
    var doneToday = d.day === today;
    var ex = state.exam || {};
    var met = E.album(idx, state);
    var metCount = Object.keys(A.CAST).filter(function (k) { return met[k]; }).length;
    function card(icon, title, text, button, onclick, extra) {
      return el('article', { className: 'bg-extra' + (extra ? ' ' + extra : '') }, [
        el('h2', null, [el('span', { 'aria-hidden': 'true', text: icon + ' ' }), title]),
        el('p', { text: text }),
        el('button', { type: 'button', className: 'btn btn--secondary', text: button, onclick: onclick })
      ]);
    }
    return el('section', { className: 'bg-extras', 'aria-label': 'تحديات وإضافات' }, [
      card('📅', 'تحدي اليوم', doneToday
        ? 'اتعمل النهارده: ' + d.right + ' من ' + d.total + (d.streak > 1 ? ' — سلسلة ' + d.streak + ' أيام ورا بعض 🔥' : '') + '. التحدي الجاي بكرة.'
        : E.DAILY_SIZE + ' حالات من كل الأماكن، بتتغير كل يوم.' + (d.streak ? ' سلسلتك: ' + d.streak + (d.streak === 1 ? ' يوم' : ' أيام') + '.' : ''),
        doneToday ? 'اعمله تاني' : 'ابدأ تحدي اليوم', function () { startMixed('daily'); }, 'bg-extra--daily'),
      card('🎓', 'الامتحان النهائي', E.EXAM_SIZE + ' حالة صعبة (ليفل 3 لـ 6) من الفصلين. ' + E.PASS + '% أو أكتر = شهادة.' + (ex.best !== undefined ? ' أحسن نتيجة ليك: ' + ex.best + '%.' : ''),
        ex.passed ? 'امتحن تاني' : 'ادخل الامتحان', function () { startMixed('exam'); }, 'bg-extra--exam'),
      card('📒', 'ألبوم الحالات', 'قابلت ' + metCount + ' من ' + Object.keys(A.CAST).length + ' شخصية في الحالات.', 'افتح الألبوم', showAlbum, 'bg-extra--album')
    ]);
  }

  /* A simple description of every level, shown when the student picks it. */
  var LEVEL_INFO = {
    1: 'أسئلة سهلة: اسم الجزء أو المادة ومكانها وأول المعلومة. ابدأ منه لو أول مرة تذاكر الفكرة.',
    2: 'الجزء ده بيعمل إيه ولازمته إيه؟ أسئلة على الوظايف.',
    3: 'قدامك مريض أو زرعة بأعراض، وانت تشخّص من الكتاب.',
    4: 'حاجتين شبه بعض وبيتلخبطوا: تعرف الفرق بينهم.',
    5: 'لو حاجة اتشالت أو زادت أو قلّت: تتوقع اللي هيحصل وتعلّل.',
    6: 'أسئلة بتجمع أكتر من فكرة، زي الأسئلة الصعبة في الامتحان.'
  };
  var picked = {};   // the level each place is set to (this visit only)

  function trackCard(t) {
    var place = PLACE[t.place];
    var pr = E.trackProgress(idx, state, t.id);
    var sel = picked[t.id] !== undefined ? picked[t.id] : (pr.done ? 'review' : pr.level);
    var card;
    function pick(level) {
      picked[t.id] = level;
      var fresh = trackCard(t);
      card.parentNode.replaceChild(fresh, card);
      var again = fresh.querySelector('[data-level="' + level + '"]');
      if (again) again.focus();
    }
    var path = el('div', { className: 'bg-path', role: 'group', 'aria-label': 'اختار الليفل اللي تحبه' });
    pr.levels.forEach(function (level) {
      var done = E.levelCleared(idx, state, t.id, level);
      var on = sel === level;
      path.appendChild(el('button', { type: 'button', className: 'bg-path-step' + (done ? ' is-done' : '') + (on ? ' is-now' : ''),
        'aria-pressed': String(on), 'data-level': String(level), title: 'الليفل ' + level + ': ' + E.LEVEL_NAMES[level] + ' — ' + E.LEVEL_HINTS[level],
        onclick: function () { pick(level); } }, [
        el('span', { className: 'bg-path-dot', 'aria-hidden': 'true', text: done ? '✓' : String(level) }),
        el('span', { className: 'bg-path-name', text: E.LEVEL_NAMES[level] })
      ]));
    });
    var onReview = sel === 'review';
    path.appendChild(el('button', { type: 'button', className: 'bg-path-step bg-path-review' + (onReview ? ' is-now' : ''),
      'aria-pressed': String(onReview), 'data-level': 'review', title: 'مراجعة: الأفكار اللي نجومها أقل', onclick: function () { pick('review'); } }, [
      el('span', { className: 'bg-path-dot', 'aria-hidden': 'true', text: '🔁' }),
      el('span', { className: 'bg-path-name', text: 'مراجعة' })
    ]));
    var info;
    if (onReview) {
      info = el('div', { className: 'bg-level-info', role: 'status' }, [
        el('p', { className: 'bg-level-title', text: '🔁 مراجعة' }),
        el('p', { text: 'أفكار من كل الليفلات، واللي نجومها أقل بتيجي الأول. مناسبة قبل الامتحان.' })
      ]);
    } else {
      var all = E.levelIdeas(idx, t.id, sel);
      var cleared = all.filter(function (id) { return E.isCleared(state, t.id, sel, id); }).length;
      info = el('div', { className: 'bg-level-info', role: 'status' }, [
        el('p', { className: 'bg-level-title', text: 'الليفل ' + sel + ': ' + E.LEVEL_NAMES[sel] + (cleared === all.length && all.length ? ' ✓' : '') }),
        el('p', { text: LEVEL_INFO[sel] || E.LEVEL_HINTS[sel] }),
        el('p', { className: 'bg-level-count', text: 'جاوبت صح على ' + cleared + ' من ' + all.length + ' أفكار في الليفل ده.' })
      ]);
    }
    var host = t.host || place.host;
    card = el('article', { className: 'bg-place bg-place--' + t.place, 'data-track': t.id }, [
      art(A.scene({ who: host, bg: t.bg || place.bg, mood: 'happy' }), 'bg-art bg-place-art'),
      el('div', { className: 'bg-place-body' }, [
        el('h2', null, [el('span', { 'aria-hidden': 'true', text: place.icon + ' ' }), t.name]),
        el('p', { className: 'bg-place-desc', text: t.description || '' }),
        el('p', { className: 'bg-rank' }, ['رتبتك: ', el('strong', { text: pr.rank })]),
        el('p', { className: 'bg-path-hint', text: 'اختار أي ليفل تحبه (مش لازم بالترتيب):' }),
        path,
        info,
        meter(pr.percent, 'إتقان ' + pr.percent + '%'),
        el('p', { className: 'bg-meter-text', text: 'الإتقان: ' + pr.percent + '% (' + pr.mastered + ' من ' + pr.ideas + ' فكرة بـ 3 نجوم)' }),
        el('button', { type: 'button', className: 'btn bg-start', text: onReview ? 'ابدأ وردية مراجعة' : 'ابدأ وردية الليفل ' + sel + ' (' + E.LEVEL_NAMES[sel] + ')', onclick: function () { startShift(t.id, sel); } })
      ])
    ]);
    return card;
  }

  /* ---------- A shift ---------- */

  function clearedLevels(trackId) {
    return (idx.levels[trackId] || []).filter(function (l) { return E.levelCleared(idx, state, trackId, l); });
  }

  function startShift(trackId, chosen) {
    E.startShift(state);
    var made = E.newShift(idx, state, trackId, undefined, chosen);
    if (!made.items.length) { showLobby(); return; }
    shift = { mode: 'track', track: trackId, level: made.level, chosen: chosen, items: made.items, at: 0, results: [],
      clearedBefore: clearedLevels(trackId) };
    save();
    showCase();
    scrollTop();
  }

  function startMixed(kind) {
    E.startShift(state);
    var made = kind === 'daily' ? E.dailyShift(idx, state, E.dayOf()) : E.examShift(idx, state);
    if (!made.items.length) { showLobby(); return; }
    shift = { mode: kind, track: null, level: null, items: made.items, at: 0, results: [] };
    save();
    showCase();
    scrollTop();
  }

  function topBar() {
    var t = shift.track ? idx.tracks[shift.track] : null;
    var dots = el('ol', { className: 'bg-dots', 'aria-hidden': 'true' });
    shift.items.forEach(function (_, i) {
      var r = shift.results[i];
      dots.appendChild(el('li', { className: 'bg-dot' + (i === shift.at ? ' is-now' : '') + (r ? (r.right ? ' is-right' : ' is-wrong') : '') }));
    });
    return el('div', { className: 'bg-top' }, [
      el('button', { type: 'button', className: 'bg-exit', text: '✕ خروج', 'aria-label': 'اخرج من الوردية', onclick: showLobby }),
      el('div', { className: 'bg-top-text' }, [
        el('p', { className: 'bg-top-title' }, t ? [
          PLACE[t.place].icon + ' ',
          el('span', { className: 'bg-top-track', text: t.name + ' — ' }),
          shift.level ? 'الليفل ' + shift.level + ': ' + E.LEVEL_NAMES[shift.level] : 'مراجعة'
        ] : [shift.mode === 'daily' ? '📅 تحدي اليوم' : '🎓 الامتحان النهائي']),
        el('p', { className: 'bg-top-count', text: 'حالة ' + (shift.at + 1) + ' من ' + shift.items.length })
      ]),
      dots
    ]);
  }

  function showCase() {
    var item = shift.items[shift.at];
    var c = idx.cases[item.caseId];
    var story = c.stories[item.story] || c.stories[0];
    var person = A.CAST[story.who] || null;
    var type = TYPES[c.type] || TYPES.clinic;
    var answered = false;

    G12.clear(root);
    G12.setTitle('الدكتور والمزارع — حالة ' + (shift.at + 1));
    root.appendChild(topBar());

    var stage = el('div', { className: 'bg-stage' });
    var wide = art(person ? A.scene({ who: story.who, bg: story.bg || type.bg, mood: story.mood || 'neutral', signs: story.signs })
      : (story.view ? A.view(story.view, story.opts || {}) : A.scene({ who: 'murad', bg: type.bg })), 'bg-shot is-on');
    stage.appendChild(wide);
    stage.appendChild(el('span', { className: 'bg-chip', text: type.name }));

    var talk = el('div', { className: 'bg-talk' });
    if (person) talk.appendChild(el('p', { className: 'bg-who' }, [el('strong', { text: person.name }), ' · ' + person.role]));
    if (story.context) talk.appendChild(el('p', { className: 'bg-context', text: story.context }));
    talk.appendChild(el('ul', { className: 'bg-lines' }, story.lines.map(function (line) {
      return el('li', { className: 'bg-bubble', text: line });
    })));

    var actions = el('div', { className: 'bg-actions' });
    var question = el('section', { className: 'bg-question', 'aria-labelledby': 'bg-q-title' });
    question.hidden = true;
    var feedback = el('div', { className: 'bg-feedback', tabindex: '-1' });
    feedback.hidden = true;

    var card = el('article', { className: 'bg-case bg-case--' + idx.tracks[c.track].place }, [stage, talk, actions, question, feedback]);
    root.appendChild(card);

    // the question and its four choices
    var choices = item.choices.map(function (choice) {
      return choice.right ? { text: c.answer, right: true } : { text: c.wrong[choice.wrong].text, why: c.wrong[choice.wrong].why, right: false };
    });
    question.appendChild(el('h2', { id: 'bg-q-title', className: 'bg-q-title', text: 'السؤال' }));
    question.appendChild(el('p', { className: 'bg-q-text', text: c.question }));
    var options = el('div', { className: 'bg-options' });
    choices.forEach(function (choice, i) {
      var button = el('button', { type: 'button', className: 'bg-option' }, [
        el('span', { className: 'bg-option-letter', 'aria-hidden': 'true', text: LETTERS.charAt(i) }),
        el('span', { className: 'bg-option-text', text: choice.text })
      ]);
      button.addEventListener('click', function () { choose(i); });
      options.appendChild(button);
    });
    question.appendChild(options);

    function showQuestion(focus) {
      question.hidden = false;
      if (focus) G12.focus(question.querySelector('.bg-q-title'));
    }

    function camera(viewName, opts, kind) {
      var markup = A.view(viewName, opts || {});
      if (!markup) return;
      var next = art(markup, 'bg-shot bg-shot--' + (kind || 'close'));
      stage.appendChild(next);
      var old = stage.querySelectorAll('.bg-shot.is-on');
      // the camera moves down to the part (or a flash for an X-ray)
      requestAnimationFrame(function () {
        Array.prototype.forEach.call(old, function (o) { o.classList.remove('is-on'); o.classList.add('is-off'); });
        next.classList.add('is-on');
        setTimeout(function () { Array.prototype.forEach.call(old, function (o) { if (o.parentNode) o.parentNode.removeChild(o); }); }, reduceMotion ? 0 : 700);
      });
    }

    if (c.exam) {
      var examButton = el('button', { type: 'button', className: 'btn bg-exam', text: '🔍 ' + c.exam.label });
      examButton.addEventListener('click', function () {
        examButton.disabled = true;
        camera(c.exam.view, c.exam.opts, c.exam.kind);
        if (c.exam.finding) actions.appendChild(el('p', { className: 'bg-finding', role: 'status' }, [el('strong', { text: 'النتيجة: ' }), c.exam.finding]));
        showQuestion(true);
      });
      actions.appendChild(examButton);
    } else {
      showQuestion(false);
    }

    function choose(i) {
      if (answered) return;
      answered = true;
      var choice = choices[i];
      var result = E.answer(idx, state, item, choice.right);
      shift.results[shift.at] = result;
      save();
      Array.prototype.forEach.call(options.children, function (button, j) {
        button.disabled = true;
        if (choices[j].right) button.classList.add('is-right');
        else if (j === i) button.classList.add('is-wrong');
        if (choices[j].right) button.appendChild(el('span', { className: 'bg-option-mark', text: '✓ الإجابة الصح' }));
        else if (j === i) button.appendChild(el('span', { className: 'bg-option-mark', text: '✗ اختيارك' }));
      });
      var after = c.after || (c.exam ? { view: c.exam.view, opts: c.exam.opts } : null);
      if (after && after.view) camera(after.view, Object.assign({}, after.opts || {}, { labels: true }), 'labels');
      showFeedback(c, choice, result);
    }

    function showFeedback(c, choice, result) {
      feedback.hidden = false;
      feedback.className = 'bg-feedback ' + (choice.right ? 'is-right' : 'is-wrong');
      var idea = idx.ideas[c.idea];
      var starLine;
      if (choice.right && result.starsAfter > result.starsBefore) starLine = '⭐ نجمة جديدة لفكرة «' + idea.name + '» — بقى معاك ' + result.starsAfter + ' من 3.';
      else if (choice.right && result.starsAfter >= E.MAX_STARS) starLine = 'الفكرة دي متفرمة عندك (3 نجوم).';
      else if (choice.right) starLine = 'صح! النجمة الجاية لفكرة «' + idea.name + '» هتيجي في وردية تانية بشكل جديد من الفكرة.';
      else starLine = 'الفكرة دي («' + idea.name + '») هترجعلك تاني بحكاية مختلفة.' + (result.starsBefore > result.starsAfter ? ' ونقصت نجمة: بقى معاك ' + result.starsAfter + ' من 3.' : '');
      var parts = [
        el('h2', { className: 'bg-fb-title', text: choice.right ? '✓ برافو، إجابة صح!' : '✗ مش دي الإجابة' }),
        el('p', { className: 'bg-fb-stars', text: starLine })
      ];
      if (!choice.right) {
        parts.push(el('p', { className: 'bg-fb-why' }, [el('strong', { text: 'ليه اختيارك غلط؟ ' }), choice.why]));
        parts.push(el('p', { className: 'bg-fb-answer' }, [el('strong', { text: 'الإجابة الصح: ' }), c.answer]));
      }
      parts.push(el('div', { className: 'bg-explain' }, [
        el('p', null, [el('strong', { text: 'الشرح خطوة بخطوة (من الكتاب):' })]),
        el('ol', null, c.explain.map(function (step) { return el('li', { text: step }); }))
      ]));
      var last = shift.at === shift.items.length - 1;
      parts.push(el('div', { className: 'actions bg-next' }, [
        el('button', { type: 'button', className: 'btn', text: last ? 'خلّص الوردية' : 'الحالة الجاية ←', onclick: function () {
          if (last) showSummary(); else { shift.at += 1; showCase(); scrollTop(); }
        } })
      ]));
      parts.forEach(function (p) { feedback.appendChild(p); });
      G12.focus(feedback);
    }
  }

  /* ---------- End of the shift ---------- */

  function showSummary() {
    if (shift.mode !== 'track') { showMixedSummary(); return; }
    var shift0 = shift;
    var t = idx.tracks[shift.track];
    var right = shift.results.filter(function (r) { return r && r.right; }).length;
    var gained = shift.results.filter(function (r) { return r && r.starsAfter > r.starsBefore; }).length;
    var after = E.trackProgress(idx, state, shift.track);
    var newly = clearedLevels(shift.track).filter(function (l) { return shift.clearedBefore.indexOf(l) === -1; });
    var weak = [];
    shift.results.forEach(function (r) { if (r && !r.right && weak.indexOf(r.idea) === -1) weak.push(r.idea); });

    G12.clear(root);
    G12.setTitle('الدكتور والمزارع — نهاية الوردية');
    var heading = el('h1', { tabindex: '-1', text: 'خلصت الوردية!' });
    var box = el('section', { className: 'bg-summary' }, [
      art(A.scene({ who: t.host || PLACE[t.place].host, bg: PLACE[t.place].bg, mood: right >= 4 ? 'happy' : 'neutral' }), 'bg-art bg-summary-art'),
      el('div', { className: 'bg-summary-body' }, [
        heading,
        el('p', { className: 'bg-score' }, [el('bdi', { dir: 'ltr', text: right + ' / ' + shift.results.length }), ' إجابات صح']),
        el('p', { text: gained ? '⭐ كسبت ' + gained + (gained === 1 ? ' نجمة' : gained === 2 ? ' نجمتين' : ' نجوم') + ' في الوردية دي.' : 'مكسبتش نجوم جديدة المرة دي، والأفكار اللي غلطت فيها هترجعلك.' })
      ])
    ]);
    root.appendChild(box);
    var body = box.querySelector('.bg-summary-body');

    if (newly.length) {
      body.appendChild(el('div', { className: 'bg-levelup', role: 'status' }, [
        el('p', { className: 'bg-levelup-title', text: '🎉 خلّصت ' + newly.map(function (l) { return 'الليفل ' + l + ' (' + E.LEVEL_NAMES[l] + ')'; }).join(' و') + '!' }),
        el('p', { text: after.done ? 'وخلّصت كل ليفلات ' + t.name + '! رتبتك دلوقتي: ' + after.rank + '.' : 'رتبتك دلوقتي: ' + after.rank + '. اختار الليفل اللي تحبه من المدخل.' })
      ]));
    } else if (shift.level) {
      var lv = E.levelIdeas(idx, shift.track, shift.level);
      var cl = lv.filter(function (id) { return E.isCleared(state, shift.track, shift.level, id); }).length;
      body.appendChild(el('p', { className: 'bg-status', text: 'الليفل ' + shift.level + ' (' + E.LEVEL_NAMES[shift.level] + '): جاوبت صح على ' + cl + ' من ' + lv.length + ' أفكار.' }));
    }
    if (weak.length) {
      body.appendChild(el('div', { className: 'bg-weak' }, [
        el('p', null, [el('strong', { text: 'أفكار محتاجة مراجعة (هترجعلك):' })]),
        el('ul', null, weak.map(function (id) {
          var idea = idx.ideas[id];
          return el('li', null, [el('strong', { text: idea.name + ': ' }), idea.note || '']);
        }))
      ]));
    }
    body.appendChild(el('div', { className: 'actions' }, [
      el('button', { type: 'button', className: 'btn', text: 'وردية تانية في نفس الليفل', onclick: function () { startShift(t.id, shift0.chosen); } }),
      el('button', { type: 'button', className: 'btn btn--secondary', text: 'ارجع للمدخل', onclick: showLobby }),
      el('button', { type: 'button', className: 'btn btn--secondary', text: '🗺️ خريطة الإتقان', onclick: showMap })
    ]));
    shift = null;
    G12.focus(heading);
  }

  function showMixedSummary() {
    var right = shift.results.filter(function (r) { return r && r.right; }).length;
    var total = shift.results.length;
    var exam = shift.mode === 'exam';
    var result = exam ? E.finishExam(state, right, total) : E.finishDaily(state, E.dayOf(), right, total);
    save();
    var weak = [];
    shift.results.forEach(function (r) { if (r && !r.right && weak.indexOf(r.idea) === -1) weak.push(r.idea); });
    G12.clear(root);
    G12.setTitle('الدكتور والمزارع — ' + (exam ? 'نتيجة الامتحان' : 'نتيجة تحدي اليوم'));
    var heading = el('h1', { tabindex: '-1', text: exam ? 'نتيجة الامتحان النهائي' : 'خلصت تحدي اليوم!' });
    var lines = [heading, el('p', { className: 'bg-score' }, [el('bdi', { dir: 'ltr', text: right + ' / ' + total }), ' إجابات صح' + (exam ? ' — ' + result.percent + '%' : '')])];
    if (exam) {
      lines.push(el('p', { text: result.passed ? '🎉 مبروك! عديت الامتحان، وتقدر تطلع شهادتك.' : 'محتاج ' + E.PASS + '% علشان الشهادة. راجع الأفكار اللي تحت وارجع امتحن تاني. أحسن نتيجة ليك: ' + result.best + '%.' }));
    } else {
      lines.push(el('p', { text: result.streak > 1 ? '🔥 سلسلة ' + result.streak + ' أيام ورا بعض! ارجع بكرة علشان تكمّلها.' : 'ارجع بكرة لتحدي جديد وابدأ سلسلة أيام.' }));
    }
    var host = exam ? 'murad' : 'hassan';
    var box = el('section', { className: 'bg-summary' }, [
      art(A.scene({ who: host, bg: exam ? 'clinic' : 'farm', mood: right / Math.max(1, total) >= 0.6 ? 'happy' : 'neutral' }), 'bg-art bg-summary-art'),
      el('div', { className: 'bg-summary-body' }, lines)
    ]);
    root.appendChild(box);
    var body = box.querySelector('.bg-summary-body');
    if (weak.length) {
      body.appendChild(el('div', { className: 'bg-weak' }, [
        el('p', null, [el('strong', { text: 'أفكار محتاجة مراجعة:' })]),
        el('ul', null, weak.map(function (id) {
          var idea = idx.ideas[id];
          return el('li', null, [el('strong', { text: idea.name + ': ' }), idea.note || '']);
        }))
      ]));
    }
    var actions = [];
    if (exam && result.passed) actions.push(el('button', { type: 'button', className: 'btn', text: '🎓 اطلع الشهادة', onclick: function () { showCertificate(result.percent); } }));
    actions.push(el('button', { type: 'button', className: 'btn btn--secondary', text: 'ارجع للمدخل', onclick: showLobby }));
    actions.push(el('button', { type: 'button', className: 'btn btn--secondary', text: '🗺️ خريطة الإتقان', onclick: showMap }));
    body.appendChild(el('div', { className: 'actions' }, actions));
    shift = null;
    G12.focus(heading);
  }

  /* ---------- The certificate (the name is typed for printing only; it is not saved) ---------- */

  function showCertificate(percent) {
    G12.clear(root);
    G12.setTitle('الدكتور والمزارع — الشهادة');
    var all = E.overall(idx, state);
    var nameOut = el('p', { className: 'bg-cert-name', text: '..................' });
    var input = el('input', { type: 'text', id: 'bg-cert-input', maxlength: '40', autocomplete: 'off', placeholder: 'اكتب اسمك هنا' });
    input.addEventListener('input', function () { nameOut.textContent = input.value.trim() || '..................'; });
    var heading = el('h1', { tabindex: '-1', className: 'bg-cert-title', text: 'شهادة إتقان' });
    var d = new Date();
    root.appendChild(el('div', { className: 'bg-cert-tools' }, [
      el('label', { for: 'bg-cert-input', text: 'اسمك على الشهادة (مش بيتحفظ في أي مكان):' }),
      input,
      el('div', { className: 'actions' }, [
        el('button', { type: 'button', className: 'btn', text: '🖨️ اطبع الشهادة', onclick: function () { window.print(); } }),
        el('button', { type: 'button', className: 'btn btn--secondary', text: 'ارجع للمدخل', onclick: showLobby })
      ])
    ]));
    root.appendChild(el('section', { className: 'bg-cert' }, [
      art(A.scene({ who: 'murad', bg: 'clinic', mood: 'happy' }) + A.scene({ who: 'abdelrahman', bg: 'farm', mood: 'happy' }), 'bg-art bg-hero-pair bg-cert-art'),
      heading,
      el('p', { text: 'لعبة «الدكتور والمزارع» — أحياء تالتة ثانوي' }),
      el('p', { text: 'بنشهد إن' }),
      nameOut,
      el('p', { text: 'عدّى الامتحان النهائي بنسبة ' + percent + '%، في الدعامة والحركة والتنسيق الهرموني، واتفرم عنده ' + all.mastered + ' فكرة من ' + all.ideas + '.' }),
      el('p', { className: 'bg-cert-date', text: 'التاريخ: ' + d.getDate() + ' / ' + (d.getMonth() + 1) + ' / ' + d.getFullYear() }),
      el('p', { className: 'bg-cert-sign', text: 'د. مراد (رئيس القسم) — الحاج عبد الرحمن (شيخ المزارعين)' })
    ]));
    G12.focus(heading);
  }

  /* ---------- The album of the people met ---------- */

  function showAlbum() {
    shift = null;
    G12.clear(root);
    G12.setTitle('الدكتور والمزارع — ألبوم الحالات');
    var met = E.album(idx, state);
    var heading = el('h1', { tabindex: '-1', text: '📒 ألبوم الحالات' });
    root.appendChild(el('div', { className: 'bg-map-head' }, [
      heading,
      el('p', { text: 'كل الناس اللي قابلتهم في الحالات. اللي لسه رمادي ما قابلتوش؛ كمّل الورديات وهتقابلهم.' }),
      el('button', { type: 'button', className: 'btn btn--secondary', text: '← ارجع للمدخل', onclick: showLobby })
    ]));
    var bgs = { abdelrahman: 'farm', hassan: 'farm', ramadan: 'farm', mahmoud: 'lab' };
    root.appendChild(el('ul', { className: 'bg-album' }, Object.keys(A.CAST).map(function (k) {
      var p = A.CAST[k];
      var m = met[k];
      return el('li', { className: 'bg-album-card' + (m ? '' : ' is-locked') }, [
        art(A.scene({ who: k, bg: bgs[k] || 'clinic', mood: m ? 'happy' : 'neutral' }), 'bg-art'),
        el('p', { className: 'bg-album-name' }, [el('strong', { text: m ? p.name : '؟؟؟' }), m ? ' · ' + p.role : '']),
        el('p', { className: 'bg-album-count', text: m ? 'حليت معاه ' + m.right + ' من ' + m.cases + (m.cases === 1 ? ' حالة' : ' حالات') : 'لسه ما قابلتوش' })
      ]);
    })));
    G12.focus(heading);
  }

  /* ---------- The mastery map ---------- */

  function showMap() {
    shift = null;
    G12.clear(root);
    G12.setTitle('الدكتور والمزارع — خريطة الإتقان');
    var heading = el('h1', { tabindex: '-1', text: '🗺️ خريطة الإتقان' });
    root.appendChild(el('div', { className: 'bg-map-head' }, [
      heading,
      el('p', { text: 'كل فكرة من الفصلين ونجومها: ★★★ يعني اتفرمت، وأقل من كده يعني لسه محتاجة شغل. دوس على الفكرة تشوف ملخصها.' }),
      el('ul', { className: 'bg-legend' }, [
        el('li', { className: 'is-0', text: 'لسه' }), el('li', { className: 'is-1', text: 'بدأت' }), el('li', { className: 'is-2', text: 'قربت' }), el('li', { className: 'is-3', text: 'اتفرمت' })
      ]),
      el('button', { type: 'button', className: 'btn btn--secondary', text: '← ارجع للمدخل', onclick: showLobby })
    ]));
    [1, 2].forEach(function (ch) {
      var tracks = tracksOf(ch).filter(function (t) { return idx.content.ideas.some(function (i) { return i.track === t.id; }); });
      if (!tracks.length) return;
      var section = el('section', { className: 'bg-map-chapter' }, [el('h2', { text: chapterTitle(ch) })]);
      tracks.forEach(function (t) {
        var pr = E.trackProgress(idx, state, t.id);
        var ideas = idx.content.ideas.filter(function (i) { return i.track === t.id; });
        section.appendChild(el('h3', null, [PLACE[t.place].icon + ' ' + t.name + ' — ', el('span', { className: 'bg-map-percent', text: pr.percent + '%' })]));
        section.appendChild(el('ul', { className: 'bg-map-list' }, ideas.map(function (idea) {
          var n = E.stars(state, idea.id);
          var weak = state.ideas[idea.id] && state.ideas[idea.id].weak;
          return el('li', { className: 'bg-map-idea is-' + n + (weak ? ' is-weak' : '') }, [
            el('details', null, [
              el('summary', null, [starsNode(n), ' ', el('span', { text: idea.name }), weak ? el('span', { className: 'bg-map-flag', text: 'غلطت فيها آخر مرة' }) : null]),
              el('p', { text: idea.note || '' })
            ])
          ]);
        })));
      });
      root.appendChild(section);
    });
    G12.focus(heading);
  }

  /* ---------- Start ---------- */

  function start() {
    Promise.all(FILES.map(function (file) {
      return G12.loadJSON(file).catch(function (error) {
        if (window.console) console.warn('[bio-game] ' + file + ': ' + (error && error.message));
        return null;
      });
    })).then(function (files) {
      var loaded = files.filter(Boolean);
      if (!loaded.length) throw new Error('The game files could not be loaded.');
      var content = E.build(loaded);
      content.problems.forEach(function (p) { if (window.console) console.warn('[bio-game] ' + p); });
      idx = E.index(content);
      state = E.load();
      showLobby();
    }).catch(function (error) {
      G12.showError(root, error, { title: 'الدكتور والمزارع' });
    });
  }

  start();
})();
