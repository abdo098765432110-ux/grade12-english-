/* A dhikr or dua for every visit.
 *
 * Each time any page opens (or is refreshed), one dhikr, Qur'anic verse or
 * authentic Prophetic dua is chosen at random (never the same one twice in a
 * row) and shown in a small floating card for about 3.5 seconds, then it fades
 * away and is removed. The card ignores the mouse and touch (pointer-events:
 * none), so it never blocks a button or an answer. Everything runs here in the
 * browser: no server, no API. The style is in style.css (".dhikr").
 *
 * The texts: Qur'anic verses as in the Mushaf, with sura and verse; Prophetic
 * duas only from al-Bukhari and Muslim, or graded sahih/hasan (Abu Dawud 1522,
 * al-Tirmidhi 2140 and 3513, Ibn Majah 251, Ibn Hibban — al-Silsila al-Sahiha
 * 2886). Check any new text and its source before adding it here.
 */
(function () {
  'use strict';

  var SHOW_MS = 3200;   // fully visible for this long…
  var FADE_MS = 500;    // …then fades out (about 3.7 seconds in all)
  var LAST_KEY = 'g12-dhikr-last';

  var ADHKAR = [
    // short adhkar
    { text: 'سُبْحَانَ اللهِ', source: 'ذِكْر' },
    { text: 'الْحَمْدُ لِلَّهِ', source: 'ذِكْر' },
    { text: 'اللهُ أَكْبَرُ', source: 'ذِكْر' },
    { text: 'لَا إِلَهَ إِلَّا اللهُ', source: 'ذِكْر' },
    { text: 'أَسْتَغْفِرُ اللهَ الْعَظِيمَ', source: 'ذِكْر' },
    { text: 'اللَّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا مُحَمَّدٍ', source: 'صلاة على النبي ﷺ' },
    // adhkar from the Sunnah
    { text: 'سُبْحَانَ اللهِ وَبِحَمْدِهِ', source: 'متفق عليه' },
    { text: 'سُبْحَانَ اللهِ وَبِحَمْدِهِ، سُبْحَانَ اللهِ الْعَظِيمِ', source: 'متفق عليه' },
    { text: 'لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللهِ', source: 'متفق عليه' },
    { text: 'لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ، وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ', source: 'متفق عليه' },
    { text: 'سُبْحَانَ اللهِ، وَالْحَمْدُ لِلَّهِ، وَلَا إِلَهَ إِلَّا اللهُ، وَاللهُ أَكْبَرُ', source: 'رواه مسلم' },
    { text: 'سُبْحَانَ اللهِ وَبِحَمْدِهِ، عَدَدَ خَلْقِهِ، وَرِضَا نَفْسِهِ، وَزِنَةَ عَرْشِهِ، وَمِدَادَ كَلِمَاتِهِ', source: 'رواه مسلم' },
    { text: 'أَسْتَغْفِرُ اللهَ وَأَتُوبُ إِلَيْهِ', source: 'رواه البخاري' },
    // Prophetic duas
    { text: 'اللَّهُمَّ انْفَعْنِي بِمَا عَلَّمْتَنِي، وَعَلِّمْنِي مَا يَنْفَعُنِي، وَزِدْنِي عِلْمًا', source: 'رواه ابن ماجه' },
    { text: 'اللَّهُمَّ لَا سَهْلَ إِلَّا مَا جَعَلْتَهُ سَهْلًا، وَأَنْتَ تَجْعَلُ الْحَزْنَ إِذَا شِئْتَ سَهْلًا', source: 'رواه ابن حبان' },
    { text: 'اللَّهُمَّ أَعِنِّي عَلَى ذِكْرِكَ، وَشُكْرِكَ، وَحُسْنِ عِبَادَتِكَ', source: 'رواه أبو داود' },
    { text: 'يَا مُقَلِّبَ الْقُلُوبِ، ثَبِّتْ قَلْبِي عَلَى دِينِكَ', source: 'رواه الترمذي' },
    { text: 'اللَّهُمَّ إِنَّكَ عَفُوٌّ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي', source: 'رواه الترمذي' },
    { text: 'اللَّهُمَّ اهْدِنِي وَسَدِّدْنِي', source: 'رواه مسلم' },
    { text: 'اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَى، وَالتُّقَى، وَالْعَفَافَ، وَالْغِنَى', source: 'رواه مسلم' },
    { text: 'اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ، وَالْعَجْزِ وَالْكَسَلِ، وَالْجُبْنِ وَالْبُخْلِ، وَضَلَعِ الدَّيْنِ، وَغَلَبَةِ الرِّجَالِ', source: 'رواه البخاري' },
    // from the Qur'an
    { text: '﴿وَقُلْ رَبِّ زِدْنِي عِلْمًا﴾', source: 'سورة طه: ١١٤' },
    { text: '﴿رَبِّ اشْرَحْ لِي صَدْرِي﴾ ﴿وَيَسِّرْ لِي أَمْرِي﴾', source: 'سورة طه: ٢٥–٢٦' },
    { text: '﴿رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ﴾', source: 'سورة البقرة: ٢٠١' },
    { text: '﴿حَسْبُنَا اللهُ وَنِعْمَ الْوَكِيلُ﴾', source: 'سورة آل عمران: ١٧٣' },
    { text: '﴿لَا إِلَهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ﴾', source: 'سورة الأنبياء: ٨٧' },
    { text: '﴿رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِنْ لَدُنْكَ رَحْمَةً إِنَّكَ أَنْتَ الْوَهَّابُ﴾', source: 'سورة آل عمران: ٨' },
    { text: '﴿رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ﴾', source: 'سورة إبراهيم: ٤١' },
    { text: '﴿فَاذْكُرُونِي أَذْكُرْكُمْ وَاشْكُرُوا لِي وَلَا تَكْفُرُونِ﴾', source: 'سورة البقرة: ١٥٢' },
    { text: '﴿أَلَا بِذِكْرِ اللهِ تَطْمَئِنُّ الْقُلُوبُ﴾', source: 'سورة الرعد: ٢٨' },
    { text: '﴿وَقُلْ رَبِّ اغْفِرْ وَارْحَمْ وَأَنْتَ خَيْرُ الرَّاحِمِينَ﴾', source: 'سورة المؤمنون: ١١٨' }
  ];

  function remembered() {
    try { return parseInt(window.localStorage.getItem(LAST_KEY), 10); } catch (e) { return NaN; }
  }

  function remember(index) {
    try { window.localStorage.setItem(LAST_KEY, String(index)); } catch (e) { /* private mode: still works, may repeat */ }
  }

  /* A random dhikr, different from the one shown last time. */
  function pick() {
    var last = remembered();
    var known = last >= 0 && last < ADHKAR.length;
    var index = Math.floor(Math.random() * (known ? ADHKAR.length - 1 : ADHKAR.length));
    if (known && index >= last) index += 1;      // skip the last one, keep the others equally likely
    remember(index);
    return index;
  }

  function build(item) {
    var card = document.createElement('aside');
    card.className = 'dhikr';
    card.setAttribute('role', 'status');
    card.setAttribute('aria-live', 'polite');
    card.setAttribute('lang', 'ar');
    card.setAttribute('dir', 'rtl');
    card.innerHTML = '<span class="dhikr-star" aria-hidden="true"></span>';
    var text = document.createElement('p');
    text.className = 'dhikr-text';
    text.textContent = item.text;
    var source = document.createElement('p');
    source.className = 'dhikr-source';
    source.textContent = item.source;
    card.appendChild(text);
    card.appendChild(source);
    return card;
  }

  function show() {
    var item = ADHKAR[pick()];
    var card = build(item);
    document.body.appendChild(card);
    // next frame: start the fade-in
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { card.classList.add('is-shown'); });
    });
    window.setTimeout(function () {
      card.classList.remove('is-shown');
      window.setTimeout(function () { if (card.parentNode) card.parentNode.removeChild(card); }, FADE_MS + 100);
    }, SHOW_MS);
  }

  /* Wait (briefly) for the Arabic font, so the text appears in it from the start. */
  function start() {
    var ready = document.fonts && document.fonts.load ? document.fonts.load('1em "Dhikr Amiri"', 'سبحان الله') : null;
    var shown = false;
    function once() { if (!shown) { shown = true; show(); } }
    if (ready) ready.then(once, once);
    window.setTimeout(once, 700);
  }

  // for the tests: the list, and how long a card stays
  window.G12Dhikr = { items: ADHKAR, visibleMs: SHOW_MS, fadeMs: FADE_MS };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
