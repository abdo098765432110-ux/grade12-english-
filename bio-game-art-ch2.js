/* ==========================================================================
   «الدكتور والمزارع» — close-ups for Chapter 2 (التنسيق الهرموني).
   Each view is 480 × 320; { labels: true } names the parts as in the book.
   No female figure is drawn anywhere: the female hormones are taught with
   lab reports (the "report" view).
   ========================================================================== */
(function () {
  'use strict';

  var A = window.G12.BioArt;
  var V = A.views;
  var T = A.tools;
  var open = T.open;
  var label = T.label;
  var caption = T.caption;
  var FONT = T.FONT;
  var INK = T.INK;

  function n(v) { return Math.round(v * 10) / 10; }

  function cap(text) {
    return '<rect x="0" y="291" width="480" height="29" fill="#ffffff" opacity="0.85"/>' + caption(text);
  }

  function arrow(x1, y1, x2, y2, color, w, dash) {
    var a = Math.atan2(y2 - y1, x2 - x1);
    var h = 9;
    var p1 = [n(x2 - h * Math.cos(a - 0.45)), n(y2 - h * Math.sin(a - 0.45))];
    var p2 = [n(x2 - h * Math.cos(a + 0.45)), n(y2 - h * Math.sin(a + 0.45))];
    return '<path d="M' + x1 + ',' + y1 + ' L' + x2 + ',' + y2 + '" stroke="' + color + '" stroke-width="' + (w || 3) + '" fill="none" stroke-linecap="round"' + (dash ? ' stroke-dasharray="6 5"' : '') + '/>' +
      '<path d="M' + p1[0] + ',' + p1[1] + ' L' + x2 + ',' + y2 + ' L' + p2[0] + ',' + p2[1] + '" stroke="' + color + '" stroke-width="' + (w || 3) + '" fill="none" stroke-linecap="round" stroke-linejoin="round"/>';
  }

  function text(x, y, t, size, color, weight) {
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" direction="rtl" font-family="' + FONT + '" font-size="' + (size || 13) + '" font-weight="' + (weight || 700) + '" fill="' + (color || INK) + '">' + t + '</text>';
  }

  function cross(x, y, r) {
    return '<path d="M' + (x - r) + ',' + (y - r) + ' L' + (x + r) + ',' + (y + r) + ' M' + (x + r) + ',' + (y - r) + ' L' + (x - r) + ',' + (y + r) + '" stroke="#e05d5d" stroke-width="4.5" stroke-linecap="round"/>';
  }

  function glow(x, y, rx, ry, on) {
    return on ? '<ellipse cx="' + x + '" cy="' + y + '" rx="' + rx + '" ry="' + ry + '" fill="#ffd25c" opacity="0.45"/>' : '';
  }

  /* ---------- 1. Where the endocrine glands are (a man's body) ----------
     opts: highlight: 'pituitary' | 'thyroid' | 'parathyroid' | 'adrenal' | 'pancreas', labels */
  V.glands = function (o) {
    var h = o.highlight;
    var s = open('أماكن الغدد الصماء في جسم الإنسان', '#f3f7fc');
    s += '<path d="M240,8 C262,8 270,24 270,42 C270,60 260,70 252,74 L252,86 C300,90 330,98 336,120 L330,300 L150,300 L144,120 C150,98 180,90 228,86 L228,74 C220,70 210,60 210,42 C210,24 218,8 240,8 Z" fill="#f0d2b6" stroke="#d9a882" stroke-width="2"/>';
    s += '<ellipse cx="240" cy="34" rx="22" ry="15" fill="#f4c2cf" opacity="0.8"/>';
    // pituitary
    s += glow(240, 52, 12, 10, h === 'pituitary') + '<circle cx="240" cy="52" r="5" fill="#8b6fd6"/>';
    // thyroid and parathyroids
    s += glow(240, 82, 22, 14, h === 'thyroid' || h === 'parathyroid');
    s += '<ellipse cx="232" cy="82" rx="7" ry="10" fill="#d95c5c"/><ellipse cx="248" cy="82" rx="7" ry="10" fill="#d95c5c"/><rect x="232" y="82" width="16" height="6" fill="#d95c5c"/>';
    [[227, 76], [253, 76], [227, 89], [253, 89]].forEach(function (q) { s += '<circle cx="' + q[0] + '" cy="' + q[1] + '" r="2.6" fill="#f2a541" stroke="#b9741c"/>'; });
    // kidneys with the adrenals on top
    s += glow(205, 178, 20, 12, h === 'adrenal') + glow(275, 178, 20, 12, h === 'adrenal');
    s += '<path d="M190,190 C186,176 200,170 210,176 C220,182 218,196 214,206 C210,222 220,232 212,240 C198,250 186,232 188,214 Z" fill="#b5524a"/>';
    s += '<path d="M290,190 C294,176 280,170 270,176 C260,182 262,196 266,206 C270,222 260,232 268,240 C282,250 294,232 292,214 Z" fill="#b5524a"/>';
    s += '<path d="M192,180 L206,164 L218,178 Z" fill="#f2a541"/><path d="M288,180 L274,164 L262,178 Z" fill="#f2a541"/>';
    // pancreas
    s += glow(240, 196, 52, 14, h === 'pancreas');
    s += '<path d="M196,200 C210,188 250,186 284,190 C292,192 292,200 284,202 C254,206 220,210 200,210 C192,210 190,204 196,200 Z" fill="#f6c26b" stroke="#d9a043"/>';
    if (o.labels) {
      s += label(245, 52, 380, 30, 'النخامية: سيدة الغدد', '#8b6fd6');
      s += label(232, 82, 90, 60, 'الدرقية', '#d95c5c');
      s += label(253, 89, 400, 92, 'جارات الدرقية (4 أجزاء)', '#b9741c');
      s += label(206, 166, 86, 150, 'الكظرية فوق الكلية', '#c98a1c');
      s += label(270, 196, 400, 230, 'البنكرياس (غدة مشتركة)', '#c98a1c');
      s += cap('مواقع الغدد الصماء (رسم مبسّط)');
    }
    return s + '</svg>';
  };

  /* ---------- 2. The pituitary and the hypothalamus ----------
     opts: highlight: 'anterior' | 'posterior' | 'hypothalamus', removed: 'posterior', labels */
  V.pituitary = function (o) {
    var h = o.highlight;
    var s = open('الغدة النخامية وتحت المهاد', '#f7f4fb');
    s += '<path d="M0,0 L480,0 L480,96 C400,120 320,104 270,112 C240,118 200,118 160,110 C100,98 50,110 0,100 Z" fill="#f6d5df"/>';
    s += glow(214, 100, 50, 22, h === 'hypothalamus');
    s += '<ellipse cx="214" cy="100" rx="40" ry="16" fill="#efb5c6"/>';
    // the neurons of the hypothalamus and their long ends down the stalk
    [[196, 96], [214, 92], [232, 98]].forEach(function (q, i) {
      s += '<circle cx="' + q[0] + '" cy="' + q[1] + '" r="5" fill="#9a5bb0"/>';
      s += '<path d="M' + q[0] + ',' + (q[1] + 4) + ' C' + (q[0] + 4) + ',140 ' + (204 + i * 6) + ',170 ' + (196 + i * 10) + ',214" stroke="#9a5bb0" stroke-width="1.8" fill="none"/>';
      s += '<circle cx="' + (196 + i * 10) + '" cy="216" r="3.2" fill="#9a5bb0"/>';
    });
    // the stalk (infundibulum)
    s += '<path d="M200,112 C202,140 196,160 194,176 L226,176 C226,160 222,140 226,112 Z" fill="#f2c6a8" opacity="0.7"/>';
    // posterior (neural) lobe
    var post = o.removed === 'posterior';
    s += glow(208, 214, 50, 44, h === 'posterior');
    s += '<ellipse cx="208" cy="214" rx="38" ry="34" fill="' + (post ? 'none' : '#ffe0a3') + '" stroke="' + (post ? '#b9a37c' : '#d9a043') + '" stroke-width="2"' + (post ? ' stroke-dasharray="6 5"' : '') + '/>';
    if (post) s += cross(208, 214, 14);
    // anterior (glandular) lobe with the thin intermediate lobe
    s += glow(290, 210, 66, 54, h === 'anterior');
    s += '<path d="M246,190 C248,176 258,172 266,174" stroke="#e7d7ff" stroke-width="8" fill="none"/>';
    s += '<ellipse cx="292" cy="212" rx="52" ry="44" fill="#c9b6ff" stroke="#8b6fd6" stroke-width="2"/>';
    for (var k = 0; k < 14; k++) s += '<circle cx="' + (262 + (k * 23) % 60) + '" cy="' + (186 + Math.floor(k / 3) * 12) + '" r="3" fill="#a48be8"/>';
    if (o.labels) {
      s += label(214, 100, 90, 40, 'تحت المهاد: بيصنع ADH والأوكسيتوسين', '#9a5bb0');
      s += label(204, 150, 70, 160, 'القمع', '#b9741c');
      s += label(196, 232, 84, 262, 'الجزء العصبي: الفص الخلفي (تخزين وإفراز)', '#b9741c');
      s += label(300, 212, 392, 120, 'الجزء الغدي: الفص الأمامي والأوسط', '#6a4fc2');
      if (post) s += cap('الفص الخلفي اتشال: ADH والأوكسيتوسين مش هيتفرزوا');
      else s += label(330, 250, 340, 296, 'هرموناته: GH • TSH • ACTH • FSH • LH • البرولاكتين', '#6a4fc2');
    }
    return s + '</svg>';
  };

  /* ---------- 3. The thyroid and the parathyroids, front of the neck ----------
     opts: goiter, labels */
  V.thyroid = function (o) {
    var big = o.goiter ? 1.45 : 1;
    var s = open('الغدة الدرقية في الرقبة', '#f3f7fc');
    s += '<path d="M150,0 L330,0 L338,320 L142,320 Z" fill="#f0d2b6"/>';
    s += '<path d="M150,0 C146,120 144,220 142,320 M330,0 C334,120 336,220 338,320" stroke="#d9a882" stroke-width="2" fill="none"/>';
    // windpipe with its rings, the voice box on top
    s += '<rect x="222" y="40" width="36" height="290" rx="10" fill="#efe3d6" stroke="#c9b394"/>';
    for (var r = 0; r < 12; r++) s += '<path d="M222,' + (110 + r * 18) + ' C232,' + (116 + r * 18) + ' 248,' + (116 + r * 18) + ' 258,' + (110 + r * 18) + '" stroke="#c9b394" stroke-width="3" fill="none"/>';
    s += '<path d="M208,20 L272,20 L262,84 C252,96 228,96 218,84 Z" fill="#e8d8c6" stroke="#c9b394" stroke-width="2"/>';
    // the thyroid: two lobes and the isthmus
    s += '<g transform="translate(240,178) scale(' + big + ') translate(-240,-178)">';
    s += '<path d="M232,170 C224,140 206,124 196,136 C182,152 182,206 200,222 C212,232 226,220 232,196 Z" fill="#d95c5c" stroke="#a83a3a" stroke-width="2"/>';
    s += '<path d="M248,170 C256,140 274,124 284,136 C298,152 298,206 280,222 C268,232 254,220 248,196 Z" fill="#d95c5c" stroke="#a83a3a" stroke-width="2"/>';
    s += '<rect x="226" y="176" width="28" height="18" rx="5" fill="#cf5252"/>';
    s += '<path d="M200,150 C206,170 206,196 202,210 M280,150 C274,170 274,196 278,210" stroke="#f08a8a" stroke-width="3" fill="none" opacity="0.6"/>';
    s += '</g>';
    // parathyroids, behind the thyroid
    [[198, 146], [282, 146], [200, 208], [280, 208]].forEach(function (q) {
      s += '<ellipse cx="' + q[0] + '" cy="' + q[1] + '" rx="7" ry="5" fill="#f2b45a" stroke="#b9741c" stroke-width="1.5" stroke-dasharray="3 2"/>';
    });
    if (o.labels) {
      s += label(196, 176, 80, 120, o.goiter ? 'الدرقية متضخمة' : 'الدرقية: فصين بينهم برزخ', '#a83a3a');
      s += label(240, 185, 240, 268, 'البرزخ', '#a83a3a');
      s += label(282, 146, 400, 100, 'جارات الدرقية (4 أجزاء)', '#b9741c');
      s += label(258, 262, 396, 236, 'القصبة الهوائية', '#9a8462');
      s += cap('الدرقية: ثيروكسين + كالسيتونين • جارات الدرقية: باراثورمون');
    }
    return s + '</svg>';
  };

  /* ---------- 4. An adrenal gland on top of a kidney ----------
     opts: highlight: 'cortex' | 'medulla', removed: 'medulla', labels */
  V.adrenal = function (o) {
    var s = open('الغدة الكظرية فوق الكلية', '#f7f4fb');
    s += '<path d="M160,190 C150,140 210,120 250,140 C290,160 300,190 300,220 C300,280 220,300 180,270 C150,250 166,226 160,190 Z" fill="#b5524a" stroke="#8c3a33" stroke-width="2"/>';
    s += '<path d="M282,196 C266,206 262,224 272,236" stroke="#8c3a33" stroke-width="3" fill="none"/>';
    s += '<ellipse cx="216" cy="210" rx="34" ry="44" fill="#c4645b" opacity="0.6"/>';
    // the adrenal: cortex outside, medulla inside
    var hc = o.highlight === 'cortex', hm = o.highlight === 'medulla', rm = o.removed === 'medulla';
    s += '<path d="M150,150 C160,96 210,58 252,64 C300,70 316,112 302,150 C280,136 250,128 222,134 C196,138 170,150 150,150 Z" fill="' + (hc ? '#ffc65c' : '#f4c27a') + '" stroke="#c98a1c" stroke-width="' + (hc ? 4 : 2) + '"/>';
    s += '<path d="M184,136 C192,104 222,88 250,92 C276,96 286,116 278,132 C262,124 242,122 224,126 C208,128 196,132 184,136 Z" fill="' + (rm ? '#f7f4fb' : (hm ? '#b65a1f' : '#c97b3a')) + '" stroke="#8a4a1a" stroke-width="' + (hm ? 3.5 : 1.5) + '"' + (rm ? ' stroke-dasharray="5 4"' : '') + '/>';
    if (rm) s += cross(232, 112, 12);
    if (o.labels) {
      s += label(170, 136, 88, 70, 'القشرة (الخارجية): ستيرويدات', '#c98a1c');
      s += label(236, 112, 380, 40, 'النخاع (الداخلي): أدرينالين ونورأدرينالين', '#8a4a1a');
      s += label(250, 240, 380, 250, 'الكلية', '#8c3a33');
      s += label(150, 150, 96, 200, 'سكرية • معدنية • جنسية', '#c98a1c');
      s += cap(rm ? 'النخاع اتشال والقشرة سليمة' : 'كل غدة منطقتين: قشرة ونخاع، وهرموناتهم مختلفة');
    }
    return s + '</svg>';
  };

  /* ---------- 5. The pancreas and an islet of Langerhans ----------
     opts: blocked (the duct is blocked), betaDamaged, labels */
  V.pancreas = function (o) {
    var s = open('البنكرياس وجزر لانجرهانز', '#f6f9f2');
    // duodenum (a C) and the pancreas with its duct
    s += '<path d="M120,60 C40,60 30,190 110,210 L110,186 C60,174 66,84 120,84 Z" fill="#f2b8a8" stroke="#c4766b" stroke-width="2"/>';
    s += '<path d="M112,150 C150,120 210,118 250,128 C268,132 268,150 252,154 C214,160 170,168 128,176 Z" fill="#f6c26b" stroke="#d9a043" stroke-width="2"/>';
    s += '<path d="M244,140 C200,140 160,146 116,150" stroke="#e08a1e" stroke-width="3" fill="none"/>';
    if (o.blocked) s += cross(140, 148, 10);
    for (var a = 0; a < 6; a++) s += '<circle cx="' + (150 + a * 16) + '" cy="' + (156 - (a % 2) * 4) + '" r="5" fill="#f9d79a" stroke="#d9a043"/>';
    s += '<circle cx="196" cy="140" r="9" fill="#ffffff" stroke="#6fa8dc" stroke-width="2.5"/>';
    s += '<path d="M204,134 L300,70" stroke="#6fa8dc" stroke-width="1.5" stroke-dasharray="4 3"/><path d="M204,146 L300,250" stroke="#6fa8dc" stroke-width="1.5" stroke-dasharray="4 3"/>';
    // the islet, zoomed
    s += '<circle cx="368" cy="160" r="96" fill="#ffffff" stroke="#6fa8dc" stroke-width="3"/>';
    s += '<circle cx="368" cy="160" r="70" fill="#fff8ec" stroke="#f0d9a8"/>';
    var dmg = !!o.betaDamaged;
    for (var ring = 0; ring < 3; ring++) {
      var rr = ring * 22, cnt = ring === 0 ? 1 : ring * 7;
      for (var c = 0; c < cnt; c++) {
        var ang = (c / cnt) * Math.PI * 2 + ring * 0.3;
        var x = n(368 + rr * Math.cos(ang)), y = n(160 + rr * Math.sin(ang));
        var alpha = ring === 2 && c % 4 === 0;
        s += '<circle cx="' + x + '" cy="' + y + '" r="9.5" fill="' + (alpha ? '#e88aa0' : (dmg ? '#cfd6df' : '#6fa8dc')) + '" stroke="' + (alpha ? '#b8516b' : (dmg ? '#9aa6b5' : '#3f78b0')) + '" stroke-width="1.5"/>';
        if (dmg && !alpha) s += '<path d="M' + (x - 4) + ',' + (y - 4) + ' l8,8" stroke="#9aa6b5" stroke-width="2"/>';
      }
    }
    if (o.labels) {
      s += label(368, 160, 368, 22, dmg ? 'خلايا بيتا اتدمرت ← الإنسولين قلّ' : 'خلايا بيتا (الأغلبية) ← الإنسولين', '#3f78b0');
      s += label(412, 160, 410, 278, 'خلايا ألفا (قليلة) ← الجلوكاجون', '#b8516b');
      s += label(150, 156, 120, 236, 'خلايا حويصلية ← إنزيمات', '#d9a043');
      s += label(116, 150, 92, 32, o.blocked ? 'القناة اتسدت: الإنزيمات مش هتوصل' : 'القناة البنكرياسية ← الاثني عشر', '#e08a1e');
      s += label(196, 140, 230, 200, 'جزيرة لانجرهانز', '#6fa8dc');
      s += cap('البنكرياس غدة مشتركة: إنزيمات في قناة + هرمونات في الدم');
    }
    return s + '</svg>';
  };

  /* ---------- 6. Blood sugar after a meal: two people ----------
     opts: show: 'both' | 'normal' | 'diabetic', labels */
  V.sugar = function (o) {
    var show = o.show || 'both';
    var s = open('تركيز الجلوكوز في الدم بعد وجبة', '#ffffff');
    var X = function (h) { return n(70 + h * 90); }, Y = function (g) { return n(270 - g * 0.8); };
    s += '<rect x="70" y="' + Y(120) + '" width="370" height="' + n(Y(80) - Y(120)) + '" fill="#d3f4e4"/>';
    s += '<path d="M70,30 L70,270 L450,270" stroke="#56617c" stroke-width="2" fill="none"/>';
    [0, 100, 200, 300].forEach(function (g) { s += '<path d="M66,' + Y(g) + ' L70,' + Y(g) + '" stroke="#56617c"/>' + text(48, Y(g) + 4, String(g), 11, '#56617c', 600); });
    [0, 1, 2, 3, 4].forEach(function (h) { s += text(X(h), 288, String(h), 11, '#56617c', 600); });
    s += text(260, 306, 'الوقت بعد الوجبة (ساعات)', 12, '#56617c', 700);
    s += '<text x="22" y="150" transform="rotate(-90 22 150)" text-anchor="middle" font-family="' + FONT + '" font-size="11" font-weight="700" fill="#56617c">جلوكوز (ملليجرام/100 سم³)</text>';
    if (show !== 'diabetic') s += '<path d="M' + X(0) + ',' + Y(95) + ' C' + X(0.5) + ',' + Y(150) + ' ' + X(0.9) + ',' + Y(150) + ' ' + X(1.5) + ',' + Y(118) + ' C' + X(2) + ',' + Y(100) + ' ' + X(3) + ',' + Y(98) + ' ' + X(4) + ',' + Y(96) + '" stroke="#2f63b0" stroke-width="3.5" fill="none"/>' + text(X(4) - 6, Y(96) - 10, '(س)', 14, '#2f63b0', 800);
    if (show !== 'normal') s += '<path d="M' + X(0) + ',' + Y(160) + ' C' + X(0.6) + ',' + Y(270) + ' ' + X(1.2) + ',' + Y(270) + ' ' + X(2) + ',' + Y(240) + ' C' + X(2.8) + ',' + Y(225) + ' ' + X(3.4) + ',' + Y(222) + ' ' + X(4) + ',' + Y(220) + '" stroke="#e05d5d" stroke-width="3.5" fill="none"/>' + text(X(4) - 6, Y(220) - 10, '(ص)', 14, '#e05d5d', 800);
    if (o.labels) {
      s += label(400, Y(100), 360, 150, 'المعدل الطبيعي 80 – 120', '#1b6b49');
      if (show !== 'normal') s += label(X(2.6), Y(230), X(2.6), 40, '(ص): نقص إنسولين ← بول سكري', '#e05d5d');
      if (show !== 'diabetic') s += label(X(1.7), Y(112), 190, 236, '(س): الإنسولين رجّعه للطبيعي', '#2f63b0');
    }
    return s + '</svg>';
  };

  /* ---------- 7. Calcium between the bones and the blood ----------
     opts: state: 'pthHigh' | 'pthLow' | '' , labels */
  V.calcium = function (o) {
    var st = o.state || '';
    var s = open('الكالسيوم بين العظام والدم', '#f6f9fd');
    // bone
    s += '<path d="M40,150 C40,130 60,124 74,134 L156,134 C170,124 190,130 190,150 C190,170 170,176 156,166 L74,166 C60,176 40,170 40,150 Z" fill="#f3e7cf" stroke="#c9b48b" stroke-width="2"/>';
    if (st === 'pthHigh') s += '<path d="M100,134 l8,10 l-6,6 l8,10" stroke="#e05d5d" stroke-width="3" fill="none"/><path d="M130,136 l-4,8 l6,4 l-4,10" stroke="#e05d5d" stroke-width="2" fill="none"/>';
    for (var b = 0; b < 8; b++) s += '<circle cx="' + (70 + b * 14) + '" cy="' + (146 + (b % 2) * 8) + '" r="3" fill="#7aa6d6"/>';
    // blood vessel with calcium
    s += '<rect x="270" y="122" width="190" height="56" rx="28" fill="#f7c9c4" stroke="#d9827a" stroke-width="2"/>';
    var many = st === 'pthHigh' ? 14 : (st === 'pthLow' ? 3 : 8);
    for (var c = 0; c < many; c++) s += '<circle cx="' + (290 + (c * 37) % 160) + '" cy="' + (136 + (c * 13) % 28) + '" r="3.4" fill="#2f63b0"/>';
    s += text(365, 200, 'Ca²⁺ في الدم', 13, '#a83a3a', 800);
    // the two hormones
    s += '<rect x="200" y="20" width="80" height="40" rx="10" fill="#f2b45a"/>' + text(240, 46, 'باراثورمون', 13, '#5a3a06', 800);
    s += '<rect x="200" y="240" width="80" height="40" rx="10" fill="#d95c5c"/>' + text(240, 266, 'كالسيتونين', 13, '#ffffff', 800);
    s += arrow(186, 142, 266, 142, '#c98a1c', 4);
    s += arrow(240, 62, 230, 128, '#c98a1c', 2.4, true);
    s += arrow(266, 162, 194, 162, '#a83a3a', 4);
    s += arrow(240, 238, 230, 172, '#a83a3a', 2.4, true);
    if (st === 'pthLow') s += text(365, 106, 'تشنجات عضلية مؤلمة + سرعة انفعال', 12, '#e05d5d', 800);
    if (o.labels) {
      s += label(226, 142, 110, 92, 'الباراثورمون: يسحب الكالسيوم من العظام للدم', '#c98a1c');
      s += label(226, 162, 120, 216, 'الكالسيتونين: يقلل كالسيوم الدم ويمنع سحبه', '#a83a3a');
      if (st === 'pthHigh') s += label(108, 146, 120, 60, 'عظام هشة تنحني وتنكسر', '#e05d5d');
      s += cap('هرمونين متعاكسين بيحافظوا على كالسيوم الدم');
    }
    return s + '</svg>';
  };

  /* ---------- 8. The digestive hormones ----------
     opts: highlight: 'gastrin' | 'secretin' | 'cck', noGallbladder, labels */
  V.digest = function (o) {
    var h = o.highlight;
    var s = open('هرمونات القناة الهضمية', '#fbf8f3');
    // stomach
    s += '<path d="M70,40 C60,90 70,150 130,160 C190,168 214,130 206,96 C200,70 170,74 160,92 C150,110 120,104 116,80 C112,56 90,36 70,40 Z" fill="#f2b8a8" stroke="#c4766b" stroke-width="2"/>';
    // small intestine (duodenum) going down and right
    s += '<path d="M200,112 C240,120 250,170 230,200 C214,224 240,250 280,250 L300,250 L300,272 L276,272 C220,272 190,236 208,196 C222,168 220,138 196,132 Z" fill="#f4c7b6" stroke="#c4766b" stroke-width="2"/>';
    // pancreas
    s += '<path d="M244,206 C280,190 340,190 380,200 C392,204 390,216 378,218 C340,222 290,226 252,226 Z" fill="#f6c26b" stroke="#d9a043" stroke-width="2"/>';
    // gallbladder under the liver
    s += '<path d="M330,40 C380,30 450,40 460,80 C440,100 380,110 330,96 Z" fill="#b7684c" opacity="0.85"/>';
    if (!o.noGallbladder) s += '<path d="M372,100 C364,120 372,140 390,140 C404,138 404,118 394,104 Z" fill="#6aa043" stroke="#3f7a24" stroke-width="2"/><path d="M380,140 C360,170 300,170 246,176" stroke="#3f7a24" stroke-width="2.5" fill="none"/>';
    else s += '<path d="M372,100 C364,120 372,140 390,140 C404,138 404,118 394,104 Z" fill="none" stroke="#b9a37c" stroke-width="2" stroke-dasharray="5 4"/>' + cross(384, 122, 10);
    // a blood vessel carrying the hormones
    s += '<path d="M20,190 C120,200 140,290 240,296 C340,300 400,260 470,250" stroke="#e05d5d" stroke-width="7" fill="none" opacity="0.55"/>';
    var c = function (k, col) { return h && h !== k ? '#b8c2d0' : col; };
    s += arrow(110, 150, 70, 186, c('gastrin', '#d9534f'), 3) + arrow(60, 186, 92, 120, c('gastrin', '#d9534f'), 3, true);
    s += arrow(228, 214, 230, 280, c('secretin', '#2f63b0'), 3) + arrow(300, 284, 316, 224, c('secretin', '#2f63b0'), 3, true);
    s += arrow(218, 190, 330, 160, c('cck', '#6a4fc2'), 3, true) + arrow(330, 160, 372, 128, c('cck', '#6a4fc2'), 3, true);
    if (o.labels) {
      s += label(110, 120, 120, 26, 'الجاسترين: من بطانة المعدة ← العصارة المعدية', '#d9534f');
      s += label(230, 250, 108, 262, 'السكرتين: من الأمعاء ← العصارة البنكرياسية', '#2f63b0');
      s += label(330, 160, 380, 186, 'الكوليسيستوكينين: البنكرياس + الحويصلة', '#6a4fc2');
      s += cap('هرمونات بتتفرز من بطانة القناة الهضمية وتمشي في الدم');
    }
    return s + '</svg>';
  };

  /* ---------- 9. Starling's idea (1905) ---------- opts: labels */
  V.starling = function (o) {
    var s = open('فكرة تجربة ستارلنج', '#fbf8f3');
    s += '<path d="M40,40 C30,90 44,140 100,148 C150,154 170,122 164,92 C158,66 132,70 124,86 C114,104 90,96 86,72 C82,50 60,36 40,40 Z" fill="#f2b8a8" stroke="#c4766b" stroke-width="2"/>';
    s += '<path d="M160,104 C210,108 230,150 220,186 L196,186 C204,156 196,128 160,126 Z" fill="#f4c7b6" stroke="#c4766b" stroke-width="2"/>';
    for (var f = 0; f < 4; f++) s += '<circle cx="' + (176 + f * 9) + '" cy="' + (118 + f * 14) + '" r="5" fill="#c99a6a"/>';
    // pancreas on the right, secreting
    s += '<path d="M300,150 C340,130 410,130 450,144 C462,150 458,164 446,166 C400,172 344,176 306,174 Z" fill="#f6c26b" stroke="#d9a043" stroke-width="2"/>';
    for (var d = 0; d < 3; d++) s += '<path d="M' + (330 + d * 30) + ',180 c-3,5 -4,7 -4,9 a4,4 0 0 0 8,0 c0,-2 -1,-4 -4,-9 Z" fill="#ffd166"/>';
    // the nerves, cut
    s += '<path d="M200,60 C260,40 320,60 360,128" stroke="#9a5bb0" stroke-width="3" fill="none" stroke-dasharray="7 5"/>' + cross(282, 54, 10);
    // blood from the duodenum to the pancreas, with the "messages"
    s += '<path d="M214,190 C240,250 320,250 360,176" stroke="#e05d5d" stroke-width="8" fill="none" opacity="0.55"/>';
    [[246, 232], [290, 244], [334, 222]].forEach(function (q) { s += '<circle cx="' + q[0] + '" cy="' + q[1] + '" r="5" fill="#2f63b0"/>'; });
    if (o.labels) {
      s += label(282, 54, 400, 40, 'الاتصال العصبي مقطوع', '#9a5bb0');
      s += label(208, 160, 84, 196, 'الغذاء وصل للاثني عشر', '#c4766b');
      s += label(290, 244, 160, 262, 'غشاء الاثني عشر بيفرز مواد في الدم', '#2f63b0');
      s += label(400, 160, 380, 100, 'البنكرياس بيفرز عصارته', '#d9a043');
      s += cap('ستارلنج 1905: تنبيه غير عصبي = هرمونات (المواد المنشطة)');
    }
    return s + '</svg>';
  };

  /* ---------- 10. A lab report ----------
     opts: title, rows: [[name, value, flag]] (flag: 'up' | 'down' | 'ok' | ''), note (shown with labels) */
  V.report = function (o) {
    var rows = o.rows || [];
    var s = open('تقرير معمل التحاليل', '#eef2f8');
    s += '<rect x="56" y="14" width="368" height="292" rx="12" fill="#ffffff" stroke="#c7d3e6" stroke-width="2"/>';
    s += '<rect x="56" y="14" width="368" height="44" rx="12" fill="#e7ddff"/><rect x="56" y="44" width="368" height="14" fill="#e7ddff"/>';
    s += text(240, 42, '🧪 معمل التحاليل — ' + (o.title || 'تقرير'), 15, '#4b3a8a', 800);
    var y = 84;
    rows.forEach(function (r, i) {
      if (i) s += '<path d="M76,' + (y - 18) + ' L404,' + (y - 18) + '" stroke="#eef2f8" stroke-width="2"/>';
      s += '<text x="396" y="' + y + '" text-anchor="start" direction="rtl" font-family="' + FONT + '" font-size="14" font-weight="700" fill="' + INK + '">' + r[0] + '</text>';
      var col = r[2] === 'up' ? '#c0392b' : (r[2] === 'down' ? '#2f63b0' : '#1b6b49');
      var mark = r[2] === 'up' ? '▲ عالي' : (r[2] === 'down' ? '▼ قليل' : (r[2] === 'ok' ? '✓ طبيعي' : ''));
      s += '<text x="84" y="' + y + '" text-anchor="end" direction="rtl" font-family="' + FONT + '" font-size="13.5" font-weight="800" fill="' + col + '">' + (r[1] ? r[1] + '  ' : '') + mark + '</text>';
      y += 34;
    });
    if (o.labels && o.note) {
      s += '<rect x="72" y="' + Math.min(y - 8, 252) + '" width="336" height="40" rx="8" fill="#fff4d6" stroke="#f2c94c"/>';
      s += text(240, Math.min(y - 8, 252) + 25, o.note, 12.5, '#7a5a00', 800);
    }
    return s + '</svg>';
  };

  /* ---------- 11. A shoot bending to light: Boysen-Jensen's auxins ----------
     opts: barrier (a thin sheet stops the chemical), compare (both side by side), labels */
  function shoot(x, barrier, small) {
    var k = small ? 0.8 : 1;
    var s = '<g transform="translate(' + x + ',0) scale(' + k + ',1)">';
    s += '<rect x="-44" y="250" width="88" height="40" rx="6" fill="#c87a4a"/>';
    if (barrier) {
      s += '<path d="M0,252 L0,90" stroke="#5f9e3c" stroke-width="16" stroke-linecap="round"/>';
      s += '<path d="M-16,112 L16,108" stroke="#7d8ca3" stroke-width="5"/>';
      s += '<ellipse cx="0" cy="88" rx="8" ry="12" fill="#7cc35a"/>';
      [0, 1, 2].forEach(function (i) { s += '<circle cx="' + (i * 3 - 3) + '" cy="' + (96 + i * 5) + '" r="3" fill="#f2a541"/>'; });
    } else {
      s += '<path d="M0,252 L0,170 C0,130 16,100 44,80" stroke="#5f9e3c" stroke-width="16" fill="none" stroke-linecap="round"/>';
      s += '<ellipse cx="46" cy="78" rx="8" ry="12" fill="#7cc35a" transform="rotate(50 46 78)"/>';
      [[38, 92], [24, 112], [12, 136], [6, 160], [-2, 176]].forEach(function (q) { s += '<circle cx="' + (q[0] - 8) + '" cy="' + q[1] + '" r="3.2" fill="#f2a541"/>'; });
    }
    return s + '</g>';
  }

  V.auxin = function (o) {
    var s = open('انحناء الساق نحو الضوء', '#f3f8ff');
    s += '<circle cx="452" cy="60" r="18" fill="#ffd25c"/>';
    for (var r = 0; r < 4; r++) s += arrow(430, 52 + r * 22, 360, 52 + r * 22, '#f2c94c', 2.4);
    if (o.compare) {
      s += shoot(150, false, true) + shoot(300, true, true);
      s += text(150, 304, 'من غير حاجز: بتنحني', 13, '#1b6b49', 800) + text(300, 304, 'بحاجز: مش بتنحني', 13, '#c0392b', 800);
    } else {
      s += shoot(220, !!o.barrier);
    }
    if (o.labels && !o.compare) {
      if (o.barrier) {
        s += label(228, 110, 100, 80, 'حاجز ما بينفذش المواد', '#7d8ca3');
        s += label(220, 92, 380, 160, 'القمة بتفرز الأكسين بس مش بيوصل', '#c98a1c');
        s += cap('الحاجز منع إندول حمض الخليك يوصل ← مفيش انحناء');
      } else {
        s += label(266, 78, 360, 210, 'القمة النامية: منطقة الاستقبال', '#3f7a24');
        s += label(232, 112, 100, 90, 'إندول حمض الخليك (أكسين) نازل', '#c98a1c');
        s += label(220, 170, 100, 200, 'منطقة الاستجابة: الانحناء', '#5f9e3c');
        s += cap('بويسن جنسن 1913: أول من أشار للهرمونات النباتية (الأكسينات)');
      }
    }
    return s + '</svg>';
  };

  /* ---------- 12. Growth hormone: four men ----------
     opts: highlight: 'dwarf' | 'normal' | 'giant' | 'acro', labels */
  function man(x, h, color, big) {
    var top = 280 - h;
    var head = h * 0.13;
    var s = '<g>';
    s += '<circle cx="' + x + '" cy="' + n(top + head) + '" r="' + n(head) + '" fill="#e2ae84"/>';
    if (big) s += '<path d="M' + n(x - head * 0.8) + ',' + n(top + head * 1.4) + ' Q' + x + ',' + n(top + head * 2.5) + ' ' + n(x + head * 0.8) + ',' + n(top + head * 1.4) + '" fill="#d49b72"/>';
    s += '<path d="M' + n(x - head * 1.1) + ',' + n(top + head * 0.7) + ' Q' + x + ',' + n(top - head * 0.3) + ' ' + n(x + head * 1.1) + ',' + n(top + head * 0.7) + '" fill="#4b3621"/>';
    var bw = h * 0.16, by = top + head * 2.1, bh = h * 0.42;
    s += '<rect x="' + n(x - bw) + '" y="' + n(by) + '" width="' + n(bw * 2) + '" height="' + n(bh) + '" rx="' + n(bw * 0.5) + '" fill="' + color + '"/>';
    s += '<rect x="' + n(x - bw * 0.85) + '" y="' + n(by + bh - 4) + '" width="' + n(bw * 0.75) + '" height="' + n(280 - by - bh + 4) + '" fill="#4a5a78"/><rect x="' + n(x + bw * 0.1) + '" y="' + n(by + bh - 4) + '" width="' + n(bw * 0.75) + '" height="' + n(280 - by - bh + 4) + '" fill="#4a5a78"/>';
    var hand = big ? bw * 0.55 : bw * 0.3;
    s += '<rect x="' + n(x - bw * 1.45) + '" y="' + n(by + 4) + '" width="' + n(bw * 0.4) + '" height="' + n(bh * 0.8) + '" rx="4" fill="' + color + '"/><rect x="' + n(x + bw * 1.05) + '" y="' + n(by + 4) + '" width="' + n(bw * 0.4) + '" height="' + n(bh * 0.8) + '" rx="4" fill="' + color + '"/>';
    s += '<circle cx="' + n(x - bw * 1.25) + '" cy="' + n(by + bh * 0.85 + hand) + '" r="' + n(hand) + '" fill="#e2ae84"/><circle cx="' + n(x + bw * 1.25) + '" cy="' + n(by + bh * 0.85 + hand) + '" r="' + n(hand) + '" fill="#e2ae84"/>';
    if (big) s += '<ellipse cx="' + n(x - bw * 0.5) + '" cy="282" rx="' + n(bw * 0.7) + '" ry="5" fill="#2b3654"/><ellipse cx="' + n(x + bw * 0.5) + '" cy="282" rx="' + n(bw * 0.7) + '" ry="5" fill="#2b3654"/>';
    return s + '</g>';
  }

  V.growth = function (o) {
    var h = o.highlight;
    var s = open('هرمون النمو وأمراضه', '#f6f9fd');
    s += '<path d="M20,282 L460,282" stroke="#c7d3e6" stroke-width="3"/>';
    var people = [['dwarf', 70, 110, '#7cc6ff'], ['normal', 180, 180, '#9be38a'], ['giant', 290, 250, '#ffd166'], ['acro', 400, 180, '#f4a3c9']];
    people.forEach(function (p) {
      if (h === p[0]) s += '<rect x="' + (p[1] - 52) + '" y="' + (280 - p[2] - 10) + '" width="104" height="' + (p[2] + 16) + '" rx="12" fill="#ffd25c" opacity="0.3"/>';
      s += man(p[1], p[2], p[3], p[0] === 'acro');
    });
    if (o.labels) {
      s += label(70, 200, 80, 130, 'قزامة: نقص في الطفولة', '#2f63b0');
      s += label(180, 150, 180, 80, 'طبيعي', '#1b6b49');
      s += label(280, 120, 180, 30, 'عملقة: زيادة في الطفولة', '#c98a1c');
      s += label(400, 160, 410, 64, 'أكروميجالي: بالغين', '#b8516b');
      s += cap('الأكروميجالي: الإيدين والرجلين والصوابع وعظام الوش تكبر');
    }
    return s + '</svg>';
  };
})();
