/* ==========================================================================
   Shared helpers used by every page.
   Everything lives on one global object, window.G12, so pages can share code
   without a build step or modules.
   All content from JSON is inserted with textContent (never innerHTML), so
   text in the data files can never inject HTML or scripts into the page.
   Interface text goes through G12.t() (i18n.js) so it can be shown in
   English or Arabic. Content from the data files is never translated.
   ========================================================================== */
(function (global) {
  'use strict';

  var G12 = global.G12 || (global.G12 = {});
  var t = G12.t;

  G12.SITE_NAME = 'Learn for Grade 12';
  G12.MANAGER_PAGE = 'manage.html';
  G12.SLOW_NOTICE_MS = 8000;   // show "still loading" after this long
  G12.LOAD_TIMEOUT_MS = 30000; // give up on a data file after this long

  /* ---------- Data loading ----------
     All paths are relative (no leading slash), so the site also works inside
     a GitHub Pages repository subfolder such as https://user.github.io/repo/ */

  /* An error whose message can be shown again in the other language. */
  function failure(key, params) {
    var error = new Error(t(key, params));
    error.i18n = { key: key, params: params };
    return error;
  }

  /* The message of an error, in the current interface language. */
  G12.errorText = function (error) {
    if (error && error.i18n) return t(error.i18n.key, error.i18n.params);
    return error && error.message ? error.message : String(error);
  };

  G12.loadJSON = function (path) {
    var controller = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = controller ? setTimeout(function () { controller.abort(); }, G12.LOAD_TIMEOUT_MS) : null;
    var options = { cache: 'no-cache' };
    if (controller) options.signal = controller.signal;

    return fetch(path, options).then(
      function (response) {
        clearTimeout(timer);
        if (!response.ok) {
          var problem = response.status === 404
            ? failure('The file "{path}" was not found (HTTP 404).', { path: path })
            : failure('Could not load "{path}" (HTTP {status}).', { path: path, status: response.status });
          problem.status = response.status;
          throw problem;
        }
        return response.json().catch(function (error) {
          if (error && error.name === 'SyntaxError') {
            throw failure('The file "{path}" contains invalid JSON. Check it with the content validator.', { path: path });
          }
          throw failure('The file "{path}" could not be downloaded completely. Check your internet connection and try again.', { path: path });
        });
      },
      function (error) {
        clearTimeout(timer);
        if (error && error.name === 'AbortError') {
          throw failure('Could not load "{path}". It took too long to load. Check your internet connection and try again.', { path: path });
        }
        if (global.location && global.location.protocol === 'file:') {
          throw failure('Could not load "{path}". Pages opened directly from your computer (file://) cannot load data files. Use GitHub Pages or a local web server instead (see README.md).', { path: path });
        }
        throw failure('Could not load "{path}". Check your internet connection and try again.', { path: path });
      }
    );
  };

  /**
   * Loads one data file and returns its list (old field names upgraded).
   * units.json is optional: if it is missing, there are simply no units
   * (so a site uploaded before units existed keeps working).
   */
  G12.loadCollection = function (key) {
    var Schema = G12.Schema;
    var path = Schema.COLLECTIONS[key].path;
    return G12.loadJSON(path).then(function (data) {
      if (!data || !Array.isArray(data[key])) {
        throw failure('The file "{path}" must contain a "{key}" list. Check it with the content validator.', { path: path, key: key });
      }
      return Schema.upgradeCollection(key, data[key]);
    }, function (error) {
      if (key === 'units' && error.status === 404) {
        console.warn('units.json was not found, so no units are shown.');
        return [];
      }
      throw error;
    });
  };

  /**
   * Loads the content collections a page needs, e.g. ['units', 'lessons'].
   * Resolves to { units: [...], lessons: [...], skipped: <number> }.
   * Broken items are left out and counted in "skipped".
   * In preview mode (switched on in the content manager) the browser draft
   * is used instead of the published files.
   */
  G12.loadContent = function (keys) {
    var Schema = G12.Schema;
    var Store = G12.Store;
    var storage = Store.browserStorage();
    var draft = Store.isPreviewOn(storage) ? Store.loadDraft(storage) : null;
    G12.previewing = Boolean(draft);
    if (draft) showPreviewBanner(storage);

    return Promise.all(keys.map(function (key) {
      return draft ? draft.library[key] : G12.loadCollection(key);
    })).then(function (lists) {
      var content = { skipped: 0, skippedBy: {} };
      keys.forEach(function (key, i) {
        var usable = Schema.usableItems(key, lists[i]);
        content[key] = usable.items;
        /* A grammar question without a difficulty (for example one added to
           the data file by hand) gets an estimated level, so Easy, Medium and
           Hard exams can use it straight away. Only in this page's memory. */
        if (key === 'questions') {
          usable.items.forEach(function (question) {
            if (Schema.DIFFICULTIES.indexOf(question.difficulty) === -1) {
              question.difficulty = Schema.estimateDifficulty(question);
              question.difficultyEstimated = true;
            }
          });
        }
        content.skippedBy[key] = usable.skipped + usable.skippedQuestions;
        content.skipped += usable.skipped + usable.skippedQuestions;
        if (usable.skipped || usable.skippedQuestions) {
          console.warn(key + ': skipped ' + usable.skipped + ' item(s) and ' + usable.skippedQuestions + ' passage question(s) with errors.');
        }
      });
      return content;
    });
  };

  if (G12.onLanguageChange) {
    G12.onLanguageChange(function () {
      var banner = document.getElementById('preview-banner');
      if (!banner) return;
      banner.remove();
      showPreviewBanner(G12.Store.browserStorage());
    });
  }

  /* True when the student has started answering questions inside container
     (a choice picked, something written, or an answer checked). */
  G12.hasAnswers = function (container) {
    if (!container) return false;
    if (container.querySelector('input[type="radio"]:checked, .feedback-title, .worksheet-score, .score-number')) return true;
    return Array.prototype.some.call(container.querySelectorAll('textarea'), function (box) {
      return box.value.trim() !== '';
    });
  };

  /**
   * Loads the content a page needs and draws it. When the language button is
   * used, the page is drawn again from the content already loaded (nothing is
   * downloaded again). draw(content) and fail(error) use the current language.
   */
  G12.showPage = function (keys, draw, fail) {
    var loaded = null;
    var failed = null;
    G12.loadContent(keys).then(function (content) {
      loaded = content;
      draw(content, false);
    }).catch(function (error) {
      failed = error;
      fail(error);
    });
    if (G12.onLanguageChange) {
      G12.onLanguageChange(function () {
        if (loaded) draw(loaded, true);
        else if (failed) fail(failed);
      });
    }
  };

  function showPreviewBanner(storage) {
    var main = document.getElementById('main');
    if (!main || document.getElementById('preview-banner')) return;
    var banner = G12.el('div', { id: 'preview-banner', className: 'notice notice--info', role: 'note' }, [
      G12.el('p', null, [
        G12.el('strong', { text: t('Preview mode.') + ' ' }),
        t('You are seeing the unpublished draft saved in this browser. Students do not see these changes until you export the files and upload them.')
      ]),
      G12.el('div', { className: 'actions' }, [
        G12.el('a', { className: 'btn btn--secondary', href: G12.MANAGER_PAGE, text: t('Open content manager') }),
        G12.el('button', {
          type: 'button',
          className: 'btn btn--secondary',
          text: t('Stop preview'),
          onclick: function () {
            G12.Store.setPreview(storage, false);
            global.location.reload();
          }
        })
      ])
    ]);
    main.insertBefore(banner, main.firstChild);
  }

  /* ---------- DOM helpers ---------- */

  function appendChildren(node, children) {
    if (children === undefined || children === null || children === false) return;
    if (!Array.isArray(children)) children = [children];
    children.forEach(function (child) {
      if (child === undefined || child === null || child === false) return;
      if (Array.isArray(child)) {
        appendChildren(node, child);
      } else if (typeof child === 'string' || typeof child === 'number') {
        node.appendChild(document.createTextNode(String(child)));
      } else {
        node.appendChild(child);
      }
    });
  }

  /**
   * Create an element.
   *   G12.el('a', { href: 'x.html', className: 'btn', text: 'Go' })
   *   G12.el('ul', null, [G12.el('li', { text: 'one' })])
   * Keys starting with "on" and holding a function become event listeners.
   */
  G12.el = function (tag, props, children) {
    var node = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (key) {
        var value = props[key];
        if (value === undefined || value === null || value === false) return;
        if (key === 'className') {
          node.className = value;
        } else if (key === 'text') {
          node.textContent = value;
        } else if (key.indexOf('on') === 0 && typeof value === 'function') {
          node.addEventListener(key.slice(2).toLowerCase(), value);
        } else if (value === true) {
          node.setAttribute(key, '');
        } else {
          node.setAttribute(key, String(value));
        }
      });
    }
    appendChildren(node, children);
    return node;
  };

  G12.clear = function (node) {
    while (node.firstChild) node.removeChild(node.firstChild);
    return node;
  };

  G12.param = function (name) {
    return new URLSearchParams(global.location.search).get(name);
  };

  /* Page title in the browser tab: "<text> — Learn for Grade 12" (the page name translated). */
  G12.setTitle = function (text) {
    var site = t(G12.SITE_NAME);
    document.title = text ? text + ' — ' + site : site;
  };

  /* Move keyboard and screen-reader focus to an element (e.g. a new heading). */
  G12.focus = function (node) {
    if (!node) return;
    if (!node.hasAttribute('tabindex')) node.setAttribute('tabindex', '-1');
    node.focus();
  };

  /**
   * Render prompt text, turning blanks written as "___" (3+ underscores)
   * into a visible line that screen readers announce as "blank".
   */
  G12.renderPrompt = function (text) {
    var fragment = document.createDocumentFragment();
    String(text).split(/_{3,}/).forEach(function (part, index) {
      if (index > 0) {
        fragment.appendChild(G12.el('span', { className: 'blank', 'aria-hidden': 'true' }));
        fragment.appendChild(G12.el('span', { className: 'visually-hidden', text: ' ' + t('blank') + ' ' }));
      }
      fragment.appendChild(document.createTextNode(part));
    });
    return fragment;
  };

  /* ---------- Review status ---------- */

  /* Only items explicitly marked "reviewed" are treated as checked by a teacher. */
  G12.isReviewed = function (item) {
    return Boolean(item) && item.reviewStatus === 'reviewed';
  };

  G12.badges = function (item, extra) {
    var list = G12.el('ul', { className: 'badges', 'aria-label': t('Labels') });
    (extra || []).forEach(function (label) {
      if (label) list.appendChild(G12.el('li', { className: 'badge', dir: 'auto', text: label }));
    });
    if (G12.isReviewed(item)) {
      list.appendChild(G12.el('li', { className: 'badge badge--reviewed', text: t('Teacher-reviewed') }));
    } else {
      list.appendChild(G12.el('li', { className: 'badge badge--unreviewed', text: t('Not yet reviewed') }));
    }
    return list;
  };

  /**
   * Returns a notice if any of the given items has not been reviewed by a
   * teacher, or null when all of them have been reviewed.
   * kind: 'lesson' or 'passage'.
   */
  G12.reviewNotice = function (items, kind) {
    items = Array.isArray(items) ? items : [items];
    var hasUnreviewed = items.some(function (item) { return !G12.isReviewed(item); });
    if (!hasUnreviewed) return null;
    var text = kind === 'passage'
      ? t('a teacher has not checked this passage and its questions yet, so treat any answers and explanations as suggestions, not final answers.')
      : t('a teacher has not checked this lesson yet, so treat any answers and explanations as suggestions, not final answers.');
    return G12.el('div', { className: 'notice notice--demo', role: 'note' }, [
      G12.el('p', null, [G12.el('strong', { text: t('Not yet reviewed:') + ' ' }), text])
    ]);
  };

  /* Notice for list pages where some items may not be reviewed yet. */
  G12.listReviewNotice = function (items) {
    var hasUnreviewed = (items || []).some(function (item) { return !G12.isReviewed(item); });
    if (!hasUnreviewed) return null;
    return G12.el('div', { className: 'notice notice--demo', role: 'note' }, [
      G12.el('p', null, [
        G12.el('strong', { text: t('Please note:') + ' ' }),
        t('items labelled “Not yet reviewed” have not been checked by a teacher yet, so treat their answers and explanations as suggestions, not final answers.')
      ])
    ]);
  };

  /* Notice shown when some items in a data file were broken and left out.
     Pass a number, or the loaded content plus the collections the page shows:
       G12.skippedNotice(content, ['units', 'lessons']) */
  G12.skippedNotice = function (count, keys) {
    if (count && typeof count === 'object') {
      var byKey = count.skippedBy || {};
      count = (keys || Object.keys(byKey)).reduce(function (sum, key) { return sum + (byKey[key] || 0); }, 0);
    }
    if (!count) return null;
    var link = G12.el('a', { href: G12.MANAGER_PAGE + '#tools', text: t('content manager') });
    return G12.el('div', { className: 'notice notice--demo', role: 'note' }, [
      G12.el('p', null, G12.tNodes(count === 1
        ? '{items} could not be shown because it is incomplete or contains errors. A teacher can fix this in the {link}.'
        : '{items} could not be shown because they are incomplete or contain errors. A teacher can fix this in the {link}.',
      { items: G12.plural(count, 'item') }, { link: link }))
    ]);
  };

  /**
   * Friendly message for a section with no content yet.
   *   G12.emptyState('No lessons added yet', 'Explain…', [{ label, href }])
   */
  G12.emptyState = function (title, text, links, headingLevel) {
    return G12.el('div', { className: 'empty-state' }, [
      G12.el(headingLevel || 'h2', { text: title }),
      G12.el('p', { text: text }),
      G12.el('div', { className: 'actions' }, (links || []).map(function (link, i) {
        return G12.el('a', { className: i === 0 ? 'btn' : 'btn btn--secondary', href: link.href, text: link.label });
      }))
    ]);
  };

  /* ---------- Status messages ----------
     Loading:  every page starts with <p class="loading" role="status">Loading…</p>
               in its HTML, so something is shown before any script runs.
     Slow:     after SLOW_NOTICE_MS the loading text says it is taking longer.
     Error:    G12.showError replaces the page content with a heading, the
               reason, and "Try again" / "Go to the home page" buttons.
     Missing CSS/JS files are handled by the small inline script in each
     page's <head>, because shared scripts cannot report their own absence. */

  G12.watchSlowLoading = function () {
    setTimeout(function () {
      var loading = document.querySelector('#page-root .loading, #home-status .loading');
      if (loading) {
        loading.textContent = t('Still loading… This is taking longer than usual. Please check your internet connection.');
      }
    }, G12.SLOW_NOTICE_MS);
  };

  /**
   * Show a page-level error.
   *   G12.showError(container, error, { title: 'Grammar Lessons', homeLink: true })
   */
  G12.showError = function (container, error, options) {
    options = options || {};
    var message = G12.errorText(error);
    var actions = [G12.el('button', {
      type: 'button',
      className: 'btn',
      text: t('Try again'),
      onclick: function () { global.location.reload(); }
    })];
    if (options.homeLink !== false) {
      actions.push(G12.el('a', { className: 'btn btn--secondary', href: 'index.html', text: t('Go to the home page') }));
    }
    G12.clear(container);
    if (options.title) container.appendChild(G12.el('h1', { text: options.title }));
    container.appendChild(G12.el('div', { className: 'notice notice--error error-state', role: 'alert' }, [
      G12.el('h2', { text: t('This content could not be loaded') }),
      G12.el('p', { text: message }),
      G12.el('div', { className: 'actions' }, actions)
    ]));
    if (global.console) console.error(error);
  };

  /* ---------- Mobile menu ----------
     The menu button is hidden in the HTML. It is shown only when this script
     runs, so without JavaScript the full navigation stays visible. */

  G12.setupMenu = function () {
    var toggle = document.querySelector('.nav-toggle');
    var header = document.querySelector('.site-header');
    var nav = toggle ? document.getElementById(toggle.getAttribute('aria-controls')) : null;
    if (!toggle || !header || !nav) return;

    header.classList.add('has-menu');
    toggle.hidden = false;

    function setOpen(open) {
      toggle.setAttribute('aria-expanded', String(open));
      header.classList.toggle('menu-open', open);
    }

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
  };

  /* Subject menu (المواد الدراسية): a <details> list in the header. It opens and
     closes by itself; this adds closing with Escape and with a click outside. */
  G12.setupSubjectMenu = function () {
    var menu = document.querySelector('.subject-menu');
    if (!menu) return;
    var button = menu.querySelector('summary');
    document.addEventListener('click', function (event) {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
    menu.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        button.focus();
      }
    });
  };

  G12.setupMenu();
  G12.setupSubjectMenu();
  G12.watchSlowLoading();
  if (G12.translatePage) G12.translatePage(document);

  /* ---------- Units ---------- */

  /* Link to a page filtered to one unit, e.g. grammar.html?unit=unit-1 */
  G12.unitHref = function (page, unitId) {
    return unitId ? page + '?unit=' + encodeURIComponent(unitId) : page;
  };

  /**
   * Row of links to filter a page by unit: "All units", then each unit.
   * counts (optional): { unitId: number } shown after each unit title.
   * Returns null when there are no units.
   */
  G12.unitNav = function (units, currentId, page, counts) {
    if (!units || !units.length) return null;
    var items = [G12.el('li', null, [G12.el('a', {
      href: page,
      'aria-current': currentId ? null : 'page',
      text: t('All units')
    })])];
    units.forEach(function (unit) {
      var count = counts && counts[unit.id] !== undefined ? counts[unit.id] : null;
      items.push(G12.el('li', null, [G12.el('a', {
        href: G12.unitHref(page, unit.id),
        'aria-current': currentId === unit.id ? 'page' : null,
        dir: 'auto'
      }, [unit.title, count === null ? null : G12.el('span', { className: 'unit-nav-count', text: ' (' + count + ')' })])]));
    });
    return G12.el('nav', { className: 'unit-nav', 'aria-label': t('Units') }, [G12.el('ul', null, items)]);
  };

  /* Count items per unit id (items without a unit are not counted). */
  G12.countByUnit = function (items, lessons) {
    var counts = {};
    (items || []).forEach(function (item) {
      var unitId = G12.Schema.unitIdOf(item, lessons);
      if (unitId) counts[unitId] = (counts[unitId] || 0) + 1;
    });
    return counts;
  };

  /* Message for a unit id in the address that does not exist.
     what: 'lessons', 'summaries' or 'passages'. */
  G12.unitNotFound = function (container, page, what) {
    var labels = {
      lessons: t('Show all lessons'),
      summaries: t('Show all summaries'),
      passages: t('Show all passages')
    };
    container.appendChild(G12.el('div', { className: 'empty-state' }, [
      G12.el('h2', { text: t('Unit not found') }),
      G12.el('p', { text: t('This unit does not exist or has been removed.') }),
      G12.el('div', { className: 'actions' }, [G12.el('a', { className: 'btn', href: page, text: labels[what] })])
    ]));
  };

  /* ---------- Lesson sections (lesson pages and summaries) ---------- */
  (function () {
    var el = G12.el;

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

    function headingOf(section, tag) {
      return G12.Schema.hasText(section.heading) ? el(tag || 'h2', { dir: 'auto' }, mixedHeading(section.heading)) : null;
    }

    function paragraphs(list, show) {
      return list.filter(G12.Schema.hasText).map(function (text) {
        return el('p', { dir: 'auto' }, show(text));
      });
    }

    /* The marks ✗ (wrong) and ✓ (right) in red and green. The text is unchanged. */
    function marked(parts) {
      var out = [];
      parts.forEach(function (part) {
        if (typeof part !== 'string') {
          out.push(part);
          return;
        }
        part.split(/([✗✓])/).forEach(function (bit) {
          if (bit === '✗') out.push(el('span', { className: 'mark-wrong', text: bit }));
          else if (bit === '✓') out.push(el('span', { className: 'mark-right', text: bit }));
          else if (bit) out.push(bit);
        });
      });
      return out;
    }

    /* One section of a lesson (or of a summary).
       opts: { id, headingTag (default 'h2'), className (extra classes),
               marks (true: colour the ✗ and ✓ marks) } */
    function renderSection(section, opts) {
      opts = opts || {};
      var show = opts.marks ? function (text) { return marked(mixed(text)); } : mixed;
      var wrapper = el('section', { className: 'lesson-section' + (opts.className ? ' ' + opts.className : ''), id: opts.id });
      var heading = function (s) { return headingOf(s, opts.headingTag); };
      if (section.lang === 'ar') {
        wrapper.setAttribute('lang', 'ar');
        wrapper.setAttribute('dir', 'rtl');
      }

      switch (section.type) {
        case 'text':
          wrapper.appendChild(el('div', { className: 'prose' }, [heading(section), paragraphs(section.paragraphs, show)]));
          break;

        case 'note':
          wrapper.appendChild(el('div', { className: 'callout', role: 'note' }, [heading(section), paragraphs(section.paragraphs, show)]));
          break;

        case 'tip':
          // an exam tip: same as a note, in its own colour
          wrapper.appendChild(el('div', { className: 'callout callout--tip', role: 'note' }, [heading(section), paragraphs(section.paragraphs, show)]));
          break;

        case 'list':
          wrapper.appendChild(heading(section) || document.createTextNode(''));
          wrapper.appendChild(el('ul', { className: 'prose', dir: 'auto' }, section.items.filter(G12.Schema.hasText).map(function (item) {
            return el('li', { dir: 'auto' }, show(item));
          })));
          break;

        case 'examples':
          wrapper.appendChild(heading(section) || document.createTextNode(''));
          wrapper.appendChild(el('ul', { className: 'example-list', dir: 'auto' }, section.items.filter(G12.Schema.hasText).map(function (item) {
            return el('li', { dir: 'auto' }, show(item));
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
                  return el('td', { dir: 'auto', 'data-label': section.columns[i] || '' }, show(cell));
                }));
              }))
            ])
          ]));
          break;

        case 'mistakes':
          wrapper.appendChild(heading(section) || document.createTextNode(''));
          wrapper.appendChild(el('ul', { className: 'mistake-list' }, section.items.map(function (item) {
            return el('li', null, [
              el('p', null, [el('span', { className: 'label-avoid', text: t('✗ Avoid:') + ' ' }), el('span', { className: 'text-avoid', dir: 'auto' }, show(item.avoid))]),
              el('p', null, [el('span', { className: 'label-use', text: t('✓ Use:') + ' ' }), el('span', { dir: 'auto' }, show(item.use))]),
              G12.Schema.hasText(item.note) ? el('p', { className: 'hint', dir: 'auto' }, show(item.note)) : null
            ]);
          })));
          break;
      }
      return wrapper;
    }

    G12.mixed = mixed;
    G12.mixedHeading = mixedHeading;
    G12.renderSection = renderSection;
  })();

  /* ---------- Small utilities ---------- */

  G12.wordCount = function (paragraphs) {
    return (paragraphs || []).join(' ').split(/\s+/).filter(Boolean).length;
  };

  G12.byId = function (list, id) {
    for (var i = 0; i < (list || []).length; i++) {
      if (list[i].id === id) return list[i];
    }
    return null;
  };
})(window);
