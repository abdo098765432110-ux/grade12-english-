/* ==========================================================================
   The welcome and registration screen (every page of the website).

   A student who opens the website for the first time on a device sees a
   welcome screen and writes his full three-part Arabic name (الاسم الثلاثي)
   before he can use the website. The name is saved in the visitor register
   (Supabase — see visitor-config.js and tools/visitors/supabase-setup.sql)
   with an id made on this device, so:
     - the same device is recognised on every page, after a refresh and after
       the browser is closed (the id and name stay in this browser's storage);
     - a return visit (a new browser session) only updates the last visit time
       and the number of visits of the same record: no second record, and the
       number of students does not grow;
     - "تسجيل طالب آخر" (in the footer) lets another student use a shared device.
   If the register can not be reached (no internet, or the free project is
   paused), the student still enters; his name is sent the next time a page
   opens. The browser storage only remembers who uses this device: the
   register itself is the database.

   Nothing happens while visitor-config.js has no url or key, or when the
   browser does not allow storage (the student could not be remembered).

   Used also by the founder's dashboard (founder.js): window.G12Visitors.
   On founder.html the script tag has data-no-gate: no welcome screen there.
   ========================================================================== */
(function () {
  'use strict';

  var STORE_KEY = 'g12-visitor-v1';        // { id, name, at, synced } — who uses this device
  var SESSION_KEY = 'g12-visitor-seen';    // this browser session was already counted
  var script = document.currentScript;
  var noGate = !!(script && script.hasAttribute('data-no-gate'));

  /* ---------------------------------------------------------------- the register's address */
  function config() {
    var c = window.G12_VISITORS || {};
    var url = String(c.url || '').trim().replace(/\/+$/, '');
    var key = String(c.key || '').trim();
    if (!url || !key) return null;
    if (!safeKey(key)) {
      if (window.console) console.error('[visitors] visitor-config.js holds a secret key. Use the publishable (or anon) key only.');
      return null;
    }
    return { url: url, key: key };
  }

  /* The website may only use the publishable key or the legacy anon key. */
  function safeKey(key) {
    if (/^sb_secret_/i.test(key)) return false;
    if (/^eyJ/.test(key)) {
      try {
        var payload = JSON.parse(atob(key.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
        return payload.role === 'anon';
      } catch (error) {
        return false;
      }
    }
    return true;
  }

  /* Request headers: the publishable key goes in "apikey"; a signed-in user's
     token (the founder) in "Authorization". A legacy anon key is a token too. */
  function headers(cfg, token) {
    var h = { 'apikey': cfg.key, 'Content-Type': 'application/json' };
    if (token) h.Authorization = 'Bearer ' + token;
    else if (/^eyJ/.test(cfg.key)) h.Authorization = 'Bearer ' + cfg.key;
    return h;
  }

  function rpc(cfg, name, body, token) {
    return fetch(cfg.url + '/rest/v1/rpc/' + name, {
      method: 'POST', headers: headers(cfg, token), body: JSON.stringify(body || {}), cache: 'no-store'
    }).then(function (response) {
      if (!response.ok) {
        var error = new Error('register error ' + response.status);
        error.status = response.status;
        throw error;
      }
      return response.json();
    });
  }

  /* ---------------------------------------------------------------- the name */
  // the same rules as clean_visitor_name() in the database
  function cleanName(raw) {
    return String(raw || '')
      .replace(/[ـً-ٰٟ]/g, '')   // tatweel and short vowels
      .replace(/\s+/g, ' ')
      .trim();
  }

  /* An Arabic message saying what is wrong with the name, or '' when it is right. */
  function nameProblem(name) {
    if (!name) return 'اكتب اسمك الثلاثي أولًا.';
    if (/[A-Za-z]/.test(name)) return 'اكتب الاسم بالحروف العربية.';
    if (/[0-9٠-٩۰-۹]/.test(name)) return 'الاسم لا يحتوي على أرقام.';
    if (!/^[ء-ي ]+$/.test(name)) return 'اكتب الاسم بالحروف العربية فقط، بدون رموز.';
    var parts = name.split(' ');
    if (parts.length < 3) return 'اكتب الاسم الثلاثي كاملًا: اسمك ثم اسم والدك ثم اسم جدك (ثلاثة أسماء على الأقل).';
    if (parts.some(function (part) { return part.length < 2; })) return 'كل اسم لازم يكون حرفين على الأقل.';
    if (name.length > 80) return 'الاسم أطول من اللازم.';
    return '';
  }

  function newId() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    var b = new Uint8Array(16);
    crypto.getRandomValues(b);
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    var h = [].map.call(b, function (x) { return (x + 0x100).toString(16).slice(1); }).join('');
    return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20);
  }

  window.G12Visitors = { config: config, headers: headers, rpc: rpc, cleanName: cleanName, nameProblem: nameProblem };
  if (noGate) return;

  /* ---------------------------------------------------------------- this device */
  var cfg = config();
  if (!cfg) return;
  var storage;
  try {
    storage = window.localStorage;
    storage.setItem('g12-visitor-test', '1');
    storage.removeItem('g12-visitor-test');
  } catch (error) {
    return;   // storage blocked: the student could not be remembered, so no screen
  }

  function load() {
    try {
      var saved = JSON.parse(storage.getItem(STORE_KEY) || 'null');
      if (saved && typeof saved.id === 'string' && /^[0-9a-f-]{36}$/i.test(saved.id) && !nameProblem(saved.name)) return saved;
    } catch (error) { /* a broken record: register again */ }
    return null;
  }

  function save(record) {
    try { storage.setItem(STORE_KEY, JSON.stringify(record)); } catch (error) { /* full storage */ }
  }

  function sessionCounted() {
    try { return sessionStorage.getItem(SESSION_KEY) === '1'; } catch (error) { return false; }
  }

  function markSession() {
    try { sessionStorage.setItem(SESSION_KEY, '1'); } catch (error) { /* ignore */ }
  }

  /* Sends the record (a new one, or one not sent yet), or counts a return visit. */
  function sync(record) {
    if (!record.synced) {
      return rpc(cfg, 'register_visitor', { p_id: record.id, p_name: record.name }).then(function () {
        record.synced = true;
        save(record);
        markSession();
      }, function (error) {
        // a name the register refuses (should not happen): ask again on the next page
        if (error.status === 400) { try { storage.removeItem(STORE_KEY); } catch (e) { /* ignore */ } }
      });
    }
    if (sessionCounted()) return Promise.resolve();
    return rpc(cfg, 'touch_visitor', { p_id: record.id }).then(function (known) {
      if (known === false) {          // not in the register (for example removed): register again
        record.synced = false;
        save(record);
        return sync(record);
      }
      markSession();
    }, function () { /* try again on the next page */ });
  }

  /* ---------------------------------------------------------------- the welcome screen */
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (name) {
      if (name === 'text') node.textContent = attrs[name];
      else if (name === 'className') node.className = attrs[name];
      else node.setAttribute(name, attrs[name]);
    });
    (children || []).forEach(function (child) { if (child) node.appendChild(child); });
    return node;
  }

  var gate = null;

  function lockPage(on) {
    document.documentElement.classList.toggle('visitor-locked', on);
    [].forEach.call(document.body.children, function (node) {
      if (node === gate) return;
      if (on) node.setAttribute('inert', '');
      else node.removeAttribute('inert');
    });
  }

  /* current: the student registered on this device (when another student
     registers on a shared device), or null for the first registration. */
  function openGate(current) {
    if (gate) return;
    var input = el('input', {
      id: 'visitor-name', name: 'name', type: 'text', autocomplete: 'name', required: '', 'aria-required': 'true',
      maxlength: '80', dir: 'rtl', lang: 'ar', placeholder: 'مثال: أحمد محمد علي',
      'aria-describedby': 'visitor-name-hint visitor-name-error'
    });
    var error = el('p', { id: 'visitor-name-error', className: 'visitor-error', role: 'alert' });
    error.hidden = true;
    var actions = el('div', { className: 'visitor-actions' }, [
      el('button', { type: 'submit', className: 'btn btn--big visitor-enter', text: 'دخول الموقع' }),
      current ? el('button', { type: 'button', className: 'btn btn--secondary visitor-cancel', text: 'رجوع (' + current.name + ')' }) : null
    ]);
    var form = el('form', { className: 'visitor-form', novalidate: '' }, [
      el('label', { for: 'visitor-name', className: 'visitor-label', text: 'الاسم الثلاثي' }),
      input,
      el('p', { id: 'visitor-name-hint', className: 'visitor-hint', text: 'اكتب اسمك ثم اسم والدك ثم اسم جدك، بالحروف العربية.' }),
      error,
      actions
    ]);
    gate = el('div', { className: 'visitor-gate', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'visitor-title', lang: 'ar', dir: 'rtl' }, [
      el('div', { className: 'visitor-card' }, [
        el('div', { className: 'visitor-brand' }, [
          el('img', { src: 'logo.svg', alt: '', width: '56', height: '56' }),
          el('span', { lang: 'en', dir: 'ltr', text: 'Learn for Grade 12' })
        ]),
        el('h2', { id: 'visitor-title', className: 'visitor-title', text: current ? 'تسجيل طالب آخر على هذا الجهاز' : 'أهلًا بك في موقع طلاب الثانوية العامة' }),
        el('p', { className: 'visitor-lead', text: current
          ? 'اكتب الاسم الثلاثي للطالب الجديد. سيبقى تسجيل «' + current.name + '» محفوظًا في السجل.'
          : 'ملخصات وأسئلة بالتصحيح الفوري وامتحانات لكل المواد، مجانًا. قبل أن تبدأ، عرّفنا باسمك.' }),
        form,
        el('p', { className: 'visitor-privacy', text: 'خصوصيتك: سيُسجَّل اسمك الثلاثي ووقت دخولك في سجل زوار الموقع، ولا يطّلع عليه إلا مؤسس الموقع. لا نطلب أي بيانات أخرى.' })
      ])
    ]);
    document.body.insertBefore(gate, document.body.firstChild);
    lockPage(true);
    // the page is still loading under the screen: keep new parts locked too
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { if (gate) lockPage(true); });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var name = cleanName(input.value);
      var problem = nameProblem(name);
      if (problem) {
        error.textContent = problem;
        error.hidden = false;
        input.setAttribute('aria-invalid', 'true');
        input.focus();
        return;
      }
      var record = { id: newId(), name: name, at: new Date().toISOString(), synced: false };
      save(record);
      try { sessionStorage.removeItem(SESSION_KEY); } catch (e) { /* ignore */ }
      closeGate();
      showWho(record);
      sync(record);
    });
    input.addEventListener('input', function () {
      if (!error.hidden) { error.hidden = true; input.removeAttribute('aria-invalid'); }
    });
    var cancel = gate.querySelector('.visitor-cancel');
    if (cancel) {
      cancel.addEventListener('click', closeGate);
      gate.addEventListener('keydown', function (event) { if (event.key === 'Escape') closeGate(); });
    }
    // keep the keyboard inside the screen
    gate.addEventListener('keydown', function (event) {
      if (event.key !== 'Tab') return;
      var items = [].filter.call(gate.querySelectorAll('input, button'), function (n) { return !n.disabled; });
      var first = items[0];
      var last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    setTimeout(function () { input.focus(); }, 0);
  }

  function closeGate() {
    if (!gate) return;
    gate.parentNode.removeChild(gate);
    gate = null;
    lockPage(false);
  }

  /* "مسجّل باسم … · تسجيل طالب آخر" in the footer. */
  function showWho(record) {
    function draw() {
      var place = document.querySelector('.site-footer .footer-text');
      if (!place) return;
      var line = document.getElementById('visitor-who');
      if (line) line.parentNode.removeChild(line);
      var change = el('button', { type: 'button', className: 'visitor-switch', text: 'تسجيل طالب آخر' });
      change.addEventListener('click', function () { openGate(load()); });
      line = el('p', { id: 'visitor-who', className: 'visitor-who', lang: 'ar', dir: 'rtl' }, [
        document.createTextNode('مسجّل باسم: '),
        el('strong', { text: record.name }),
        document.createTextNode(' · '),
        change
      ]);
      place.appendChild(line);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', draw);
    else draw();
  }

  var record = load();
  if (record) {
    showWho(record);
    sync(record);
  } else {
    openGate(null);
  }
})();
