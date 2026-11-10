/* ==========================================================================
   The founder's private dashboard (founder.html).

   1. The founder signs in with the email and password of his Supabase account
      (Supabase Auth). The session is kept in this tab only (sessionStorage)
      and ends with "تسجيل الخروج" or when the tab is closed.
   2. The register is read with the founder's token. The database's Row Level
      Security gives the rows only to an account listed in public.founders:
      any other account (or a student) gets nothing.
   3. The dashboard shows the number of registered students (one per record:
      a return visit never adds a record), new registrations, the most recent
      visitors, the visit history day by day and the full list, with search,
      sorting, a refresh button and an automatic refresh every 30 seconds.
   ========================================================================== */
(function () {
  'use strict';

  var V = window.G12Visitors;
  var root = document.getElementById('founder-root');
  var cfg = V && V.config();
  var SESSION_KEY = 'g12-founder-session';
  var AUTO_MS = 30000;
  var PAGE = 1000;          // rows per request (the API gives at most 1000 at once)
  var FIRST_ROWS = 50;      // rows shown before "عرض القائمة كاملة"
  var HISTORY_DAYS = 30;    // the visit history covers this many days
  var HISTORY_ROWS = 200;   // and shows at most this many visits

  var session = null;
  var data = null;          // { visitors: [], visits: [] }
  var known = null;         // ids seen at the previous refresh (to mark new ones)
  var fresh = {};           // ids that appeared at the last refresh
  var view = { query: '', sort: 'first-desc', all: false, auto: true };
  var updatedAt = null;
  var timer = null;
  var busy = false;

  var stamp = new Intl.DateTimeFormat('ar-EG-u-nu-latn', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Africa/Cairo' });
  var clock = new Intl.DateTimeFormat('ar-EG-u-nu-latn', { timeStyle: 'short', timeZone: 'Africa/Cairo' });
  var dayName = new Intl.DateTimeFormat('ar-EG-u-nu-latn', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Africa/Cairo' });
  var dayKeyFormat = new Intl.DateTimeFormat('en-CA', { year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'Africa/Cairo' });

  function dayKey(date) { return dayKeyFormat.format(date); }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (name) {
      var value = attrs[name];
      if (value === null || value === undefined || value === false) return;
      if (name === 'text') node.textContent = value;
      else if (name === 'className') node.className = value;
      else if (name.slice(0, 2) === 'on') node.addEventListener(name.slice(2), value);
      else node.setAttribute(name, value === true ? '' : value);
    });
    (children || []).forEach(function (child) {
      if (child === null || child === undefined || child === false) return;
      node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    });
    return node;
  }

  function clear() { while (root.firstChild) root.removeChild(root.firstChild); }

  function message(text, info) {
    return el('p', { className: 'founder-message' + (info ? ' is-info' : ''), role: info ? 'status' : 'alert', text: text });
  }

  /* ------------------------------------------------------------ not set up yet */
  if (!cfg) {
    clear();
    root.appendChild(el('section', { className: 'founder-panel' }, [
      el('h2', { text: 'قاعدة البيانات غير متصلة بعد' }),
      el('p', { text: 'املأ ملف visitor-config.js بعنوان مشروع Supabase والمفتاح العام (publishable key)، كما في خطوات الإعداد، ثم ارفعه إلى الموقع.' })
    ]));
    return;
  }

  /* ------------------------------------------------------------ the session */
  function loadSession() {
    try { return JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null'); } catch (error) { return null; }
  }

  function saveSession(value) {
    session = value;
    try {
      if (value) sessionStorage.setItem(SESSION_KEY, JSON.stringify(value));
      else sessionStorage.removeItem(SESSION_KEY);
    } catch (error) { /* the session lives in memory only */ }
  }

  function fromAuth(body) {
    return {
      access: body.access_token,
      refresh: body.refresh_token,
      expires: Date.now() + (Number(body.expires_in) || 3600) * 1000,
      email: (body.user && body.user.email) || (session && session.email) || ''
    };
  }

  function auth(grant, body) {
    return fetch(cfg.url + '/auth/v1/token?grant_type=' + grant, {
      method: 'POST', headers: { 'apikey': cfg.key, 'Content-Type': 'application/json' }, body: JSON.stringify(body), cache: 'no-store'
    }).then(function (response) {
      return response.json().catch(function () { return {}; }).then(function (json) {
        if (!response.ok || !json.access_token) {
          var error = new Error('auth ' + response.status);
          error.status = response.status;
          throw error;
        }
        return json;
      });
    });
  }

  function renew() {
    return auth('refresh_token', { refresh_token: session.refresh }).then(function (json) {
      saveSession(fromAuth(json));
    });
  }

  /* A request with the founder's token (renewed when it is about to end). */
  function api(path, options, retried) {
    var ready = session.expires - Date.now() < 60000 ? renew() : Promise.resolve();
    return ready.then(function () {
      return fetch(cfg.url + path, Object.assign({ headers: V.headers(cfg, session.access), cache: 'no-store' }, options || {}));
    }).then(function (response) {
      if (response.status === 401 && !retried) return renew().then(function () { return api(path, options, true); });
      if (!response.ok) {
        var error = new Error('api ' + response.status);
        error.status = response.status;
        throw error;
      }
      return response.json();
    });
  }

  function all(table, select, order, filter) {
    var rows = [];
    function next(offset) {
      return api('/rest/v1/' + table + '?select=' + select + (filter ? '&' + filter : '') + '&order=' + order + '&limit=' + PAGE + '&offset=' + offset)
        .then(function (page) {
          rows = rows.concat(page);
          return page.length === PAGE ? next(offset + PAGE) : rows;
        });
    }
    return next(0);
  }

  /* ------------------------------------------------------------ sign in */
  function showSignIn(note, info) {
    stopAuto();
    data = null;
    known = null;
    clear();
    var email = el('input', { id: 'founder-email', type: 'email', autocomplete: 'username', required: true, dir: 'ltr' });
    var password = el('input', { id: 'founder-password', type: 'password', autocomplete: 'current-password', required: true, dir: 'ltr' });
    var notice = note ? message(note, info) : null;
    var button = el('button', { type: 'submit', className: 'btn btn--big', text: 'تسجيل الدخول' });
    var form = el('form', { novalidate: true }, [
      el('label', { for: 'founder-email', text: 'البريد الإلكتروني لحساب المؤسس' }), email,
      el('label', { for: 'founder-password', text: 'كلمة المرور' }), password,
      notice,
      el('div', { className: 'actions' }, [button])
    ]);
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!email.value.trim() || !password.value) {
        replace(message('اكتب البريد الإلكتروني وكلمة المرور.'));
        return;
      }
      button.disabled = true;
      button.textContent = 'جارٍ تسجيل الدخول…';
      auth('password', { email: email.value.trim(), password: password.value }).then(function (json) {
        password.value = '';
        saveSession(fromAuth(json));
        return start();
      }).catch(function (error) {
        button.disabled = false;
        button.textContent = 'تسجيل الدخول';
        replace(message(error.status === 400 || error.status === 401
          ? 'البريد الإلكتروني أو كلمة المرور غير صحيحة.'
          : 'تعذّر الاتصال بقاعدة البيانات. تأكد من الإنترنت، ومن أن مشروع Supabase غير متوقف مؤقتًا (Paused).'));
      });
    });
    function replace(node) {
      var old = form.querySelector('.founder-message');
      if (old) form.replaceChild(node, old);
      else form.insertBefore(node, form.querySelector('.actions'));
    }
    root.appendChild(el('section', { className: 'founder-panel founder-login', 'aria-labelledby': 'founder-login-title' }, [
      el('h2', { id: 'founder-login-title', text: 'تسجيل دخول المؤسس' }),
      el('p', { text: 'هذه الصفحة خاصة بمؤسس الموقع فقط. السجل لا يظهر إلا لحساب المؤسس بعد تسجيل الدخول.' }),
      form
    ]));
    email.focus();
  }

  function signOut(note) {
    var token = session && session.access;
    saveSession(null);
    if (token) {
      fetch(cfg.url + '/auth/v1/logout', { method: 'POST', headers: V.headers(cfg, token) })
        .then(function (response) { return response.text(); })
        .catch(function () { /* the token ends by itself within the hour */ });
    }
    showSignIn(note || 'تم تسجيل الخروج.', true);
  }

  /* ------------------------------------------------------------ the register */
  function start() {
    clear();
    root.appendChild(el('p', { className: 'loading', role: 'status', text: 'جارٍ تحميل السجل…' }));
    return V.rpc(cfg, 'is_founder', {}, session.access).catch(function (error) {
      if (error.status === 401) return renew().then(function () { return V.rpc(cfg, 'is_founder', {}, session.access); });
      throw error;
    }).then(function (founder) {
      if (founder !== true) {
        signOut('هذا الحساب ليس حساب مؤسس الموقع، لذلك لا يمكنه رؤية السجل.');
        return;
      }
      return refresh().then(startAuto);
    }).catch(failed);
  }

  function failed(error) {
    if (error && (error.status === 400 || error.status === 401 || error.status === 403)) {
      signOut('انتهت جلسة الدخول. سجّل الدخول مرة أخرى.');
      return;
    }
    clear();
    root.appendChild(el('section', { className: 'founder-panel' }, [
      message('تعذّر تحميل السجل. تأكد من الإنترنت، ومن أن مشروع Supabase غير متوقف مؤقتًا (Paused)، ثم حاول مرة أخرى.'),
      el('div', { className: 'actions' }, [
        el('button', { type: 'button', className: 'btn', text: 'حاول مرة أخرى', onclick: function () { start(); } }),
        el('button', { type: 'button', className: 'btn btn--secondary', text: 'تسجيل الخروج', onclick: function () { signOut(); } })
      ])
    ]));
  }

  function refresh() {
    if (busy) return Promise.resolve();
    busy = true;
    var since = new Date(Date.now() - HISTORY_DAYS * 86400000).toISOString();
    return Promise.all([
      all('visitors', 'id,full_name,first_seen,last_seen,visits', 'first_seen.desc'),
      all('visits', 'visitor_id,visited_at,kind', 'visited_at.desc', 'visited_at=gte.' + encodeURIComponent(since))
    ]).then(function (result) {
      var ids = {};
      fresh = {};
      result[0].forEach(function (v) {
        ids[v.id] = true;
        if (known && !known[v.id]) fresh[v.id] = true;
      });
      known = ids;
      data = { visitors: result[0], visits: result[1] };
      updatedAt = new Date();
      busy = false;
      draw();
    }, function (error) {
      busy = false;
      throw error;
    });
  }

  function startAuto() {
    stopAuto();
    timer = setInterval(function () {
      if (view.auto && session && document.visibilityState === 'visible') refresh().catch(failed);
    }, AUTO_MS);
  }

  function stopAuto() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  /* ------------------------------------------------------------ drawing */
  // for searching: one form of alef, ta marbuta and alef maqsura
  function fold(text) {
    return V.cleanName(text).replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي');
  }

  function when(iso) { return stamp.format(new Date(iso)); }

  function sorted(list) {
    var by = {
      'first-desc': function (a, b) { return b.first_seen.localeCompare(a.first_seen); },
      'first-asc': function (a, b) { return a.first_seen.localeCompare(b.first_seen); },
      'last-desc': function (a, b) { return b.last_seen.localeCompare(a.last_seen); },
      'name': function (a, b) { return a.full_name.localeCompare(b.full_name, 'ar'); }
    }[view.sort];
    return list.slice().sort(by);
  }

  function draw() {
    var visitors = data.visitors;
    var focusId = document.activeElement && document.activeElement.id;
    var today = dayKey(new Date());
    var weekAgo = Date.now() - 7 * 86400000;
    var newToday = visitors.filter(function (v) { return dayKey(new Date(v.first_seen)) === today; }).length;
    var newWeek = visitors.filter(function (v) { return new Date(v.first_seen).getTime() >= weekAgo; }).length;
    var visitsToday = data.visits.filter(function (v) { return dayKey(new Date(v.visited_at)) === today; }).length;
    var totalVisits = visitors.reduce(function (sum, v) { return sum + (Number(v.visits) || 0); }, 0);
    var sameName = {};
    visitors.forEach(function (v) { var k = fold(v.full_name); sameName[k] = (sameName[k] || 0) + 1; });

    clear();
    // the top: who is signed in
    root.appendChild(el('section', { className: 'founder-panel founder-top', 'aria-label': 'الحساب' }, [
      el('p', { className: 'founder-updated' }, ['مسجّل الدخول بحساب المؤسس: ', el('bdi', { dir: 'ltr', text: session.email })]),
      el('div', { className: 'actions' }, [
        el('button', { type: 'button', className: 'btn', id: 'founder-refresh', text: 'تحديث السجل', onclick: function (event) {
          var button = event.currentTarget;
          button.disabled = true;
          refresh().catch(failed);
        } }),
        el('button', { type: 'button', className: 'btn btn--secondary', id: 'founder-signout', text: 'تسجيل الخروج', onclick: function () { signOut(); } })
      ])
    ]));

    // the numbers
    root.appendChild(el('section', { 'aria-labelledby': 'founder-stats-title' }, [
      el('h2', { id: 'founder-stats-title', text: 'إحصائيات الزوار' }),
      el('ul', { className: 'founder-stats' }, [
        stat('إجمالي الطلاب المسجلين', visitors.length, 'founder-total', true),
        stat('تسجيلات جديدة اليوم', newToday, 'founder-new-today'),
        stat('تسجيلات جديدة في آخر 7 أيام', newWeek, 'founder-new-week'),
        stat('زيارات اليوم', visitsToday, 'founder-visits-today'),
        stat('إجمالي الزيارات', totalVisits, 'founder-visits-total')
      ]),
      el('p', { className: 'founder-updated', id: 'founder-updated', role: 'status' }, [
        'آخر تحديث: ' + clock.format(updatedAt) + (view.auto ? ' — يتحدّث السجل تلقائيًا كل 30 ثانية.' : '')
      ])
    ]));

    // recent visitors and the history
    var recent = visitors.slice().sort(function (a, b) { return b.last_seen.localeCompare(a.last_seen); }).slice(0, 10);
    var names = {};
    visitors.forEach(function (v) { names[v.id] = v.full_name; });
    var days = [];
    var byDay = {};
    data.visits.slice(0, HISTORY_ROWS).forEach(function (visit) {
      var d = new Date(visit.visited_at);
      var key = dayKey(d);
      if (!byDay[key]) { byDay[key] = { label: dayName.format(d), items: [] }; days.push(byDay[key]); }
      byDay[key].items.push(visit);
    });
    root.appendChild(el('div', { className: 'founder-columns' }, [
      el('section', { className: 'founder-panel', 'aria-labelledby': 'founder-recent-title' }, [
        el('h2', { id: 'founder-recent-title', text: 'أحدث الزوار' }),
        recent.length ? el('ol', { className: 'founder-list', id: 'founder-recent' }, recent.map(function (v) {
          return el('li', null, [el('span', { text: v.full_name }), el('span', { className: 'when', text: when(v.last_seen) })]);
        })) : el('p', { text: 'لا يوجد زوار مسجلون بعد.' })
      ]),
      el('section', { className: 'founder-panel', 'aria-labelledby': 'founder-history-title' }, [
        el('h2', { id: 'founder-history-title', text: 'سجل الزيارات بالترتيب الزمني' }),
        el('p', { className: 'founder-updated', text: 'آخر ' + HISTORY_DAYS + ' يومًا، الأحدث أولًا' + (data.visits.length > HISTORY_ROWS ? ' (آخر ' + HISTORY_ROWS + ' زيارة)' : '') + '.' }),
        days.length ? el('div', { id: 'founder-history' }, [].concat.apply([], days.map(function (day) {
          return [
            el('h3', { className: 'founder-day', text: day.label }),
            el('ul', { className: 'founder-list' }, day.items.map(function (visit) {
              return el('li', null, [
                el('span', null, [names[visit.visitor_id] || '—', el('span', { className: 'founder-badge' + (visit.kind === 'register' ? '' : ' is-same'), text: visit.kind === 'register' ? 'تسجيل جديد' : 'زيارة' })]),
                el('time', { datetime: visit.visited_at, text: clock.format(new Date(visit.visited_at)) })
              ]);
            }))
          ];
        }))) : el('p', { text: 'لا توجد زيارات في هذه المدة.' })
      ])
    ]));

    // the full list
    var query = fold(view.query);
    var list = sorted(visitors.filter(function (v) { return !query || fold(v.full_name).indexOf(query) !== -1; }));
    var shown = view.all ? list : list.slice(0, FIRST_ROWS);
    var search = el('input', { type: 'search', id: 'founder-search', value: view.query, placeholder: 'اكتب جزءًا من الاسم', dir: 'rtl' });
    search.addEventListener('input', function () { view.query = search.value; draw(); });
    var sort = el('select', { id: 'founder-sort' }, [
      ['first-desc', 'الأحدث تسجيلًا أولًا'], ['first-asc', 'الأقدم تسجيلًا أولًا'], ['last-desc', 'آخر زيارة أولًا'], ['name', 'الاسم (أبجديًا)']
    ].map(function (o) { return el('option', { value: o[0], selected: o[0] === view.sort, text: o[1] }); }));
    sort.addEventListener('change', function () { view.sort = sort.value; draw(); });
    var auto = el('input', { type: 'checkbox', id: 'founder-auto', checked: view.auto });
    auto.addEventListener('change', function () { view.auto = auto.checked; draw(); });
    root.appendChild(el('section', { className: 'founder-panel', 'aria-labelledby': 'founder-list-title' }, [
      el('h2', { id: 'founder-list-title', text: 'قائمة الطلاب المسجلين (' + visitors.length + ')' }),
      el('div', { className: 'founder-tools' }, [
        el('label', { for: 'founder-search' }, ['بحث بالاسم', search]),
        el('label', { for: 'founder-sort' }, ['الترتيب', sort]),
        el('label', { for: 'founder-auto', className: 'founder-auto' }, [auto, 'تحديث تلقائي'])
      ]),
      el('p', { className: 'founder-updated', id: 'founder-count', role: 'status',
        text: query ? 'نتائج البحث: ' + list.length + ' من ' + visitors.length : 'يعرض ' + shown.length + ' من ' + list.length + ' طالب' }),
      el('div', { className: 'founder-table-wrap' }, [
        el('table', { className: 'founder-table', id: 'founder-table' }, [
          el('caption', { className: 'visually-hidden', text: 'الطلاب المسجلون في الموقع' }),
          el('thead', null, [el('tr', null, ['#', 'الاسم الثلاثي', 'أول تسجيل', 'آخر زيارة', 'عدد الزيارات'].map(function (h) { return el('th', { scope: 'col', text: h }); }))]),
          el('tbody', null, shown.map(function (v, i) {
            return el('tr', { 'data-id': v.id }, [
              el('td', { className: 'num', text: String(i + 1) }),
              el('td', null, [
                el('span', { className: 'founder-name', text: v.full_name }),
                fresh[v.id] ? el('span', { className: 'founder-badge', text: 'جديد' }) : null,
                sameName[fold(v.full_name)] > 1 ? el('span', { className: 'founder-badge is-same', title: 'الاسم نفسه مسجل من جهاز آخر', text: 'اسم مكرر' }) : null
              ]),
              el('td', null, [el('time', { datetime: v.first_seen, text: when(v.first_seen) })]),
              el('td', null, [el('time', { datetime: v.last_seen, text: when(v.last_seen) })]),
              el('td', { text: String(v.visits) })
            ]);
          }))
        ])
      ]),
      list.length > shown.length ? el('div', { className: 'actions' }, [
        el('button', { type: 'button', className: 'btn btn--secondary', id: 'founder-show-all', text: 'عرض القائمة كاملة (' + list.length + ')', onclick: function () { view.all = true; draw(); } })
      ]) : null
    ]));
    if (focusId && document.getElementById(focusId)) {
      var again = document.getElementById(focusId);
      again.focus();
      if (again.type === 'search') again.setSelectionRange(again.value.length, again.value.length);
    }
  }

  function stat(label, value, id, main) {
    return el('li', { className: 'founder-stat' + (main ? ' is-main' : '') }, [el('b', { id: id, text: String(value) }), label]);
  }

  /* ------------------------------------------------------------ open */
  session = loadSession();
  if (session && session.access) start();
  else showSignIn();
})();
