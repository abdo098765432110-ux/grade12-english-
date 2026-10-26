/* ==========================================================================
   Interface language: English (default) or Arabic.

   - Only the website's own interface text is translated: menus, buttons,
     headings, labels, messages, forms. Educational content (lessons,
     summaries, questions, answer choices, answers, explanations, passages)
     is always shown exactly as written.
   - The texts are in two files:
       i18n-en.js  English interface text  (G12.I18N_EN)
       i18n-ar.js  Arabic interface text   (G12.I18N_AR)
     The English text is also the key used in the code:
       G12.t('Grammar Lessons')                       → "دروس القواعد" in Arabic
       G12.t('Question {n} of {total}', { n: 1, total: 5 })
   - The language button switches immediately, without reloading the page:
     the fixed text marked in the HTML (data-i18n="…") is translated again,
     the page direction changes (ltr / rtl), and every page redraws its own
     content through G12.onLanguageChange(…).
   - The choice is saved in this browser (localStorage, key "g12-lang") and
     used again on every page and after reloading. Nothing else is stored.
   ========================================================================== */
(function (global) {
  'use strict';

  var G12 = global.G12 || (global.G12 = {});
  var STORAGE_KEY = 'g12-lang';
  var LANGUAGES = ['en', 'ar'];
  var listeners = [];   // redraw functions, called after the language changes
  var guards = [];      // functions that may ask before the language changes

  function savedLanguage() {
    try {
      var value = global.localStorage.getItem(STORAGE_KEY);
      return LANGUAGES.indexOf(value) !== -1 ? value : null;
    } catch (error) {
      return null; // storage blocked (some private-browsing modes)
    }
  }

  function applyLanguage(lang) {
    G12.lang = lang;
    G12.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
    document.documentElement.dir = G12.dir;
  }

  G12.LANG_STORAGE_KEY = STORAGE_KEY;
  applyLanguage(savedLanguage() || 'en');

  function format(text, params) {
    if (!params) return text;
    return String(text).replace(/\{(\w+)\}/g, function (match, name) {
      return params[name] !== undefined && params[name] !== null ? String(params[name]) : match;
    });
  }
  G12.format = format;

  function dictionary() {
    return G12.lang === 'ar' ? G12.I18N_AR : G12.I18N_EN;
  }

  /* Translate interface text. Text missing from the dictionary is shown as
     written in the code (English), so the page never breaks. */
  G12.t = function (text, params) {
    var dict = dictionary();
    var translated = dict && dict.strings ? dict.strings[text] : undefined;
    if (dict && translated === undefined && global.console) {
      console.warn('[i18n] No ' + (G12.lang === 'ar' ? 'Arabic' : 'English') + ' text for: ' + text);
    }
    return format(translated !== undefined ? translated : text, params);
  };

  /**
   * Translate text that contains other elements, such as a link:
   *   G12.tNodes('Fix this in the {link}.', null, { link: someLinkElement })
   * Returns a list of strings and elements for G12.el(...) children.
   */
  G12.tNodes = function (text, params, nodes) {
    var translated = G12.t(text, params);
    var parts = [];
    var pattern = /\{(\w+)\}/g;
    var last = 0;
    var match;
    while ((match = pattern.exec(translated))) {
      if (nodes && nodes[match[1]]) {
        parts.push(translated.slice(last, match.index), nodes[match[1]]);
        last = pattern.lastIndex;
      }
    }
    parts.push(translated.slice(last));
    return parts.filter(function (part) { return part !== ''; });
  };

  /* Arabic plural categories (zero, one, two, few, many, other). */
  function arabicCategory(n) {
    n = Math.abs(n);
    if (n === 0) return 'zero';
    if (n === 1) return 'one';
    if (n === 2) return 'two';
    var rest = n % 100;
    if (rest >= 3 && rest <= 10) return 'few';
    if (rest >= 11 && rest <= 99) return 'many';
    return 'other';
  }
  G12.arabicCategory = arabicCategory;

  /**
   * A number with a counted word: G12.plural(3, 'question') → "3 questions",
   * or the correct Arabic form. pluralWord is the English plural when it is
   * not word + "s" (e.g. 'summary', 'summaries').
   */
  G12.plural = function (count, word, pluralWord) {
    if (G12.lang === 'ar') {
      var forms = G12.I18N_AR && G12.I18N_AR.nouns && G12.I18N_AR.nouns[word];
      if (forms) return format(forms[arabicCategory(count)] || forms.other, { n: count });
      if (G12.I18N_AR && global.console) console.warn('[i18n] No Arabic word for: ' + word);
    }
    var english = G12.I18N_EN && G12.I18N_EN.nouns && G12.I18N_EN.nouns[word];
    if (english) return format(count === 1 ? english.one : english.other, { n: count });
    return count + ' ' + (count === 1 ? word : (pluralWord || word + 's'));
  };

  /* Dates and times in the interface language (digits stay 0–9). */
  G12.formatDateTime = function (iso) {
    try {
      return new Date(iso).toLocaleString(G12.lang === 'ar' ? 'ar-EG-u-nu-latn' : 'en-GB', { dateStyle: 'medium', timeStyle: 'short' });
    } catch (error) {
      return iso;
    }
  };

  /* Translate the fixed text marked in the HTML. The English text stays in
     the data-i18n attribute, so this works again after every switch. */
  G12.translatePage = function (root) {
    root = root || document;
    Array.prototype.forEach.call(root.querySelectorAll('[data-i18n]'), function (node) {
      node.textContent = G12.t(node.getAttribute('data-i18n'));
    });
    Array.prototype.forEach.call(root.querySelectorAll('[data-i18n-aria]'), function (node) {
      node.setAttribute('aria-label', G12.t(node.getAttribute('data-i18n-aria')));
    });
    Array.prototype.forEach.call(root.querySelectorAll('[data-i18n-content]'), function (node) {
      node.setAttribute('content', G12.t(node.getAttribute('data-i18n-content')));
    });
  };

  /* A page registers how to draw itself again in the new language. */
  G12.onLanguageChange = function (redraw) {
    listeners.push(redraw);
  };

  /* A page that could lose unsaved work registers a check. It returns a
     question to ask (in the current language), or nothing when it is safe. */
  G12.beforeLanguageChange = function (check) {
    guards.push(check);
  };

  /**
   * Switch the interface language immediately (no page reload).
   * Returns true if the language was changed.
   */
  G12.setLanguage = function (lang) {
    if (LANGUAGES.indexOf(lang) === -1 || lang === G12.lang) return false;
    for (var i = 0; i < guards.length; i++) {
      var question = guards[i]();
      if (question && !global.confirm(question)) return false;
    }
    try {
      global.localStorage.setItem(STORAGE_KEY, lang);
    } catch (error) {
      // Storage blocked: the switch still works until the page is closed.
    }
    applyLanguage(lang);
    G12.translatePage(document);
    G12.setupLanguageToggle();
    listeners.slice().forEach(function (redraw) {
      try {
        redraw(lang);
      } catch (error) {
        if (global.console) console.error(error);
      }
    });
    return true;
  };

  /* The button in the header shows the language you can switch to. */
  G12.setupLanguageToggle = function () {
    Array.prototype.forEach.call(document.querySelectorAll('.lang-toggle'), function (button) {
      var other = G12.lang === 'ar' ? 'en' : 'ar';
      button.textContent = other === 'ar' ? 'العربية' : 'English';
      button.setAttribute('lang', other);
      button.setAttribute('aria-label', other === 'ar' ? 'العربية — عرض الموقع باللغة العربية' : 'English — show the website in English');
      button.hidden = false;
      if (!button.getAttribute('data-ready')) {
        button.setAttribute('data-ready', '1');
        button.addEventListener('click', function () {
          G12.setLanguage(G12.lang === 'ar' ? 'en' : 'ar');
        });
      }
    });
  };

  function ready() {
    G12.translatePage(document);
    G12.setupLanguageToggle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready);
  } else {
    ready();
  }
})(window);
