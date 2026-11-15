/* ==========================================================================
   «الدكتور والمزارع» — close-ups for the Chapter 1 farm (الدعامة والحركة في
   النبات). Each view is 480 × 320; { labels: true } names the parts as in the
   book. Options are listed above each view.
   ========================================================================== */
(function () {
  'use strict';

  var A = window.G12.BioArt;
  var V = A.views;
  var T = A.tools;
  var open = T.open;
  var label = T.label;
  var caption = T.caption;

  var LEAF = '#5f9e3c';
  var LEAF_DARK = '#3f7a24';
  var STEM = '#5b8f3a';
  var SOIL = '#b98a5a';

  function n(v) { return Math.round(v * 10) / 10; }

  /* The caption on a light band, so it reads on soil and sky alike. */
  function cap(text) {
    return '<rect x="0" y="291" width="480" height="29" fill="#ffffff" opacity="0.85"/>' + caption(text);
  }

  /* A point on a circle, angle in degrees clockwise from the top. */
  function pt(cx, cy, r, deg) {
    var a = (deg - 90) * Math.PI / 180;
    return [n(cx + r * Math.cos(a)), n(cy + r * Math.sin(a))];
  }

  /* A point on a cubic curve. */
  function bez(p, t) {
    var u = 1 - t;
    return [
      n(u * u * u * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t * t * t * p[3][0]),
      n(u * u * u * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t * t * t * p[3][1])
    ];
  }

  function curve(p) {
    return 'M' + p[0][0] + ',' + p[0][1] + ' C' + p[1][0] + ',' + p[1][1] + ' ' + p[2][0] + ',' + p[2][1] + ' ' + p[3][0] + ',' + p[3][1];
  }

  /* A coiled (spring-like) line from a to b. */
  function coil(a, b, amp, wave) {
    var dx = b[0] - a[0], dy = b[1] - a[1];
    var len = Math.sqrt(dx * dx + dy * dy);
    var ux = dx / len, uy = dy / len;
    var d = 'M' + a[0] + ',' + a[1];
    for (var s = 2; s <= len; s += 2) {
      var k = Math.sin((s / wave) * Math.PI * 2) * amp * Math.min(1, s / 10, (len - s) / 10);
      d += ' L' + n(a[0] + ux * s - uy * k) + ',' + n(a[1] + uy * s + ux * k);
    }
    return d;
  }

  function arrow(x1, y1, x2, y2, color, w) {
    var a = Math.atan2(y2 - y1, x2 - x1);
    var h = 9;
    var p1 = [n(x2 - h * Math.cos(a - 0.45)), n(y2 - h * Math.sin(a - 0.45))];
    var p2 = [n(x2 - h * Math.cos(a + 0.45)), n(y2 - h * Math.sin(a + 0.45))];
    return '<path d="M' + x1 + ',' + y1 + ' L' + x2 + ',' + y2 + ' M' + p1[0] + ',' + p1[1] + ' L' + x2 + ',' + y2 + ' L' + p2[0] + ',' + p2[1] + '" stroke="' + color + '" stroke-width="' + (w || 3) + '" fill="none" stroke-linecap="round" stroke-linejoin="round"/>';
  }

  /* ---------- 1. A cross-section of a young dicot stem ----------
     opts: highlight: 'cutin' | 'suberin' | 'cellulose' | 'lignin', cork (a cork
     layer instead of the epidermis), noCutin (the cuticle is gone: water
     escapes), labels */
  V.stem = function (o) {
    var cx = 240, cy = 158;
    var hl = o.highlight;
    var s = open('قطاع عرضي في ساق نبات حديث ذي فلقتين', '#f4f8ef');
    s += '<circle cx="' + cx + '" cy="' + cy + '" r="125" fill="#eef7e4"/>';
    var a, i, p;
    // pith
    s += '<circle cx="' + cx + '" cy="' + cy + '" r="6.5" fill="#fbfdf7" stroke="#dfe9d5"/>';
    for (i = 0; i < 6; i++) { p = pt(cx, cy, 12, i * 60); s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="6" fill="#fbfdf7" stroke="#dfe9d5"/>'; }
    for (i = 0; i < 12; i++) { p = pt(cx, cy, 23, i * 30 + 15); s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="6" fill="#fbfdf7" stroke="#dfe9d5"/>'; }
    // cortex
    for (i = 0; i < 45; i++) { p = pt(cx, cy, 76, i * 8); s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="5.6" fill="#f5fbef" stroke="#c5ddb3"/>'; }
    for (i = 0; i < 52; i++) { p = pt(cx, cy, 87, i * (360 / 52) + 3); s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="5.4" fill="#f5fbef" stroke="#c5ddb3"/>'; }
    // collenchyma (cellulose)
    var cel = hl === 'cellulose';
    for (i = 0; i < 64; i++) {
      p = pt(cx, cy, 97, i * (360 / 64));
      s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4.2" fill="' + (cel ? '#d5f0c2' : '#e8f5dc') + '" stroke="' + (cel ? '#2f8f3a' : '#76ad55') + '" stroke-width="' + (cel ? 3.2 : 2.4) + '"/>';
      p = pt(cx, cy, 105, i * (360 / 64) + 2.8);
      s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4" fill="' + (cel ? '#d5f0c2' : '#e8f5dc') + '" stroke="' + (cel ? '#2f8f3a' : '#76ad55') + '" stroke-width="' + (cel ? 3.2 : 2.4) + '"/>';
    }
    // vascular bundles: sclerenchyma cap, phloem, xylem (lignin in the cap and the xylem)
    var lig = hl === 'lignin';
    var ligFill = lig ? '#f4a99b' : '#f9d9d2', ligStroke = lig ? '#8e1f14' : '#b23a2e', ligW = lig ? 3 : 2.3;
    for (a = 22.5; a < 360; a += 45) {
      s += '<g transform="rotate(' + a + ' ' + cx + ' ' + cy + ')">';
      [-12, -6, 0, 6, 12].forEach(function (dx) {
        s += '<circle cx="' + (cx + dx) + '" cy="' + n(cy - 66 + Math.abs(dx) * 0.18) + '" r="3.6" fill="' + ligFill + '" stroke="' + ligStroke + '" stroke-width="' + ligW + '"/>';
      });
      s += '<ellipse cx="' + cx + '" cy="' + (cy - 56) + '" rx="13" ry="5.2" fill="#d6e8ff" stroke="#7fa8d8" stroke-width="1.2"/>';
      s += '<path d="M' + (cx - 13) + ',' + (cy - 49.5) + ' L' + (cx + 13) + ',' + (cy - 49.5) + '" stroke="#a7c97a" stroke-width="1.6"/>';
      [[-7, -44], [7, -44], [0, -38], [-5, -31], [5, -31]].forEach(function (q) {
        s += '<circle cx="' + (cx + q[0]) + '" cy="' + (cy + q[1]) + '" r="' + (q[1] < -40 ? 4.4 : 3.4) + '" fill="#fde8e3" stroke="' + ligStroke + '" stroke-width="' + ligW + '"/>';
      });
      s += '</g>';
    }
    // the outside: cork (suberin) or epidermis with its cuticle (cutin)
    if (o.cork) {
      var sub = hl === 'suberin';
      for (i = 0; i < 72; i++) {
        var p1 = pt(cx, cy, 112, i * 5), p2 = pt(cx, cy, 112, i * 5 + 4.6), p3 = pt(cx, cy, 124, i * 5 + 4.6), p4 = pt(cx, cy, 124, i * 5);
        s += '<path d="M' + p1 + ' L' + p2 + ' L' + p3 + ' L' + p4 + ' Z" fill="' + (sub ? '#b07a45' : '#c99a6a') + '" stroke="#7a4b22" stroke-width="' + (sub ? 1.8 : 1.2) + '"/>';
      }
    } else {
      for (i = 0; i < 72; i++) {
        var e1 = pt(cx, cy, 112, i * 5), e2 = pt(cx, cy, 112, i * 5 + 4.6), e3 = pt(cx, cy, 120, i * 5 + 4.6), e4 = pt(cx, cy, 120, i * 5);
        s += '<path d="M' + e1 + ' L' + e2 + ' L' + e3 + ' L' + e4 + ' Z" fill="#eaf7de" stroke="#9cc47f" stroke-width="1"/>';
      }
      var cut = hl === 'cutin';
      var cutStyle = 'fill="none" stroke="' + (cut ? '#f2a900' : '#e3b52a') + '" stroke-width="' + (cut ? 5 : 3.2) + '"';
      if (o.noCutin) {
        s += '<path d="M' + pt(cx, cy, 121.5, 180) + ' A121.5,121.5 0 0 1 ' + pt(cx, cy, 121.5, 0) + '" ' + cutStyle + '/>';
        [55, 90, 125].forEach(function (d) {
          var q1 = pt(cx, cy, 126, d), q2 = pt(cx, cy, 150, d);
          s += arrow(q1[0], q1[1], q2[0], q2[1], '#3b8fd9', 2.4);
          s += '<path d="M' + q2[0] + ',' + (q2[1] + 4) + ' c-5,8 -8,12 -8,16 a8,8 0 0 0 16,0 c0,-4 -3,-8 -8,-16 Z" transform="translate(' + (d === 90 ? 12 : 4) + ',' + (d === 125 ? 4 : -2) + ')" fill="#7cc3f2" stroke="#3b8fd9"/>';
        });
      } else {
        s += '<circle cx="' + cx + '" cy="' + cy + '" r="121.5" ' + cutStyle + '/>';
      }
    }
    if (o.labels) {
      if (o.cork) s += label(pt(cx, cy, 118, -50)[0], pt(cx, cy, 118, -50)[1], 112, 22, 'فلين ← سوبرين (غير منفذ للماء)', '#7a4b22');
      else if (o.noCutin) s += label(pt(cx, cy, 124, 90)[0], pt(cx, cy, 124, 90)[1], 400, 300, 'من غير كيوتين ← الماء بيتفقد', '#3b8fd9');
      if (!o.cork) s += label(pt(cx, cy, 121, -50)[0], pt(cx, cy, 121, -50)[1], 112, 22, 'البشرة ← كيوتين (غير منفذ للماء)', '#b98900');
      s += label(pt(cx, cy, 101, 225)[0], pt(cx, cy, 101, 225)[1], 104, 294, 'كولنشيمي ← سليلوز (صلابة)', '#2f8f3a');
      s += label(pt(cx, cy, 66, 67.5)[0], pt(cx, cy, 66, 67.5)[1], 392, 26, 'إسكلرنشيمي ← لجنين', '#b23a2e');
      s += label(pt(cx, cy, 42, 112.5)[0], pt(cx, cy, 42, 112.5)[1], 412, 190, 'الخشب ← لجنين', '#b23a2e');
    } else {
      s += cap(o.cork ? 'ساق محاطة بطبقة فلين' : 'قطاع عرضي في ساق نبات حديث ذي فلقتين');
    }
    return s + '</svg>';
  };

  /* ---------- 2. The mimosa (المستحية) ----------
     opts: state: 'open' | 'touched' | 'night', labels */
  function pinna(len, folded, color) {
    var s = '<path d="M0,0 L' + len + ',0" stroke="#4f8a2c" stroke-width="1.8"/>';
    for (var t = 7; t <= len - 2; t += 6.4) {
      if (folded) {
        s += '<ellipse cx="' + n(t + 4) + '" cy="-1.5" rx="6" ry="1.9" fill="' + color + '" transform="rotate(-10 ' + n(t + 4) + ' -1.5)"/>';
        s += '<ellipse cx="' + n(t + 4) + '" cy="1.5" rx="6" ry="1.9" fill="' + color + '" transform="rotate(10 ' + n(t + 4) + ' 1.5)"/>';
      } else {
        s += '<ellipse cx="' + n(t) + '" cy="-7" rx="2.7" ry="6.6" fill="' + color + '" transform="rotate(-16 ' + n(t) + ' -7)"/>';
        s += '<ellipse cx="' + n(t) + '" cy="7" rx="2.7" ry="6.6" fill="' + color + '" transform="rotate(16 ' + n(t) + ' 7)"/>';
      }
    }
    return s;
  }

  function mimosaLeaf(x, y, angle, size, droop, folded, color) {
    var P = 64 * size;
    var s = '<g transform="translate(' + x + ',' + y + ') rotate(' + n(angle + droop) + ')">';
    s += '<path d="M0,0 L' + n(P) + ',0" stroke="#4f8a2c" stroke-width="2.6"/><ellipse cx="3" cy="0" rx="5" ry="3.4" fill="#6aa043"/>';
    [-26, -9, 9, 26].forEach(function (pa) {
      s += '<g transform="translate(' + n(P) + ',0) rotate(' + pa + ')">' + pinna(58 * size, folded, color) + '</g>';
    });
    return s + '</g>';
  }

  V.mimosa = function (o) {
    var night = o.state === 'night', touched = o.state === 'touched';
    var s = open('نبات المستحية', night ? '#1f2b4d' : '#eef7ff');
    if (night) {
      s += '<circle cx="410" cy="56" r="22" fill="#f4f1d0"/><circle cx="420" cy="50" r="20" fill="#1f2b4d"/>';
      [[60, 40], [120, 80], [330, 30], [450, 120], [40, 140], [300, 90]].forEach(function (st) { s += '<circle cx="' + st[0] + '" cy="' + st[1] + '" r="1.8" fill="#fff"/>'; });
    } else {
      s += '<circle cx="420" cy="52" r="20" fill="#ffe28a"/><circle cx="420" cy="52" r="32" fill="#ffe28a" opacity="0.3"/>';
    }
    s += '<path d="M150,300 L330,300 L316,262 L164,262 Z" fill="#c87a4a"/><rect x="156" y="252" width="168" height="14" rx="4" fill="#d98b5a"/>';
    s += '<path d="M240,256 C236,200 242,150 238,104 C236,80 240,60 244,44" stroke="' + STEM + '" stroke-width="6" fill="none" stroke-linecap="round"/>';
    var color = night ? '#4c8a35' : LEAF;
    var sleep = night ? 18 : 0;
    s += mimosaLeaf(238, 214, 200, 1, -sleep, night, color);
    s += mimosaLeaf(239, 168, -22, 1.05, touched ? 62 : sleep, night || touched, color);
    s += mimosaLeaf(238, 120, 205, 0.85, -sleep, night, color);
    s += mimosaLeaf(242, 76, -30, 0.7, sleep, night, color);
    // the pink flower head
    s += '<g transform="translate(250,40)">';
    for (var k = 0; k < 18; k++) s += '<path d="M0,0 L0,-15" stroke="#f08cc0" stroke-width="2" transform="rotate(' + k * 20 + ')"/>';
    s += '<circle r="6" fill="#e86aa8"/></g>';
    if (touched) {
      s += '<path d="M480,128 L392,128 C380,128 372,134 372,141 C372,148 380,154 392,154 L480,154 Z" fill="#e2ae84" stroke="#b9845c" stroke-width="2"/>';
      s += '<path d="M380,134 C376,136 376,146 380,148" stroke="#f3d3b8" stroke-width="3" fill="none"/>';
    }
    if (o.labels) {
      if (touched) {
        s += label(330, 196, 380, 230, 'اللمس ← الوريقات بتتدلى كأنها دبلانة', '#c4573a');
        s += cap('استجابة للمس: بتحصل على طول بعد اللمس');
      } else if (night) {
        s += label(300, 156, 360, 214, 'بالليل الوريقات بتتقارب (نوم)', '#f2c94c', true);
        s += cap('حركة النوم: بتتكرر مع تعاقب النور والظلام من غير لمس');
      } else {
        s += label(300, 150, 380, 214, 'الوريقات مفرودة (يقظة)', LEAF_DARK);
        s += cap('نبات المستحية بالنهار');
      }
    }
    return s + '</svg>';
  };

  /* ---------- 3. The pea tendril (حركة الشد) ----------
     opts: stage 1–5 (the 5 steps), noSupport (wilts and dies), growth (a
     close-up of why it coils), labels */
  V.tendril = function (o) {
    var stage = o.stage || 1;
    var none = !!o.noSupport;
    var s = open('محلاق البازلاء', '#eef7ff');
    s += '<rect x="0" y="286" width="480" height="34" fill="' + SOIL + '"/><path d="M0,286 L480,286" stroke="#8a6238" stroke-width="3"/>';
    var stickX = 330;
    if (!none) {
      s += '<rect x="' + (stickX - 6) + '" y="30" width="12" height="262" rx="4" fill="#d1ad72" stroke="#a5814a" stroke-width="1.5"/>';
      [80, 150, 220].forEach(function (y) { s += '<path d="M' + (stickX - 6) + ',' + y + ' L' + (stickX + 6) + ',' + y + '" stroke="#a5814a" stroke-width="2.5"/>'; });
    }
    var stem;
    if (none || stage <= 2) stem = [[200, 288], [196, 226], [176, 168], [148, 96]];
    else if (stage === 3) stem = [[200, 288], [206, 226], [222, 166], [236, 94]];
    else stem = [[200, 288], [236, 248], [300, 214], [306, 60]];
    var wilt = none;
    var stemColor = wilt ? '#9a8a4a' : STEM;
    s += '<path d="' + curve(stem) + '" stroke="' + stemColor + '" stroke-width="6" fill="none" stroke-linecap="round"/>';
    // leaves: pairs of round leaflets
    [0.3, 0.55, 0.82].forEach(function (t, i) {
      var p = bez(stem, t);
      var c = wilt ? '#b8a45a' : LEAF;
      var dr = wilt ? 40 : 0;
      s += '<ellipse cx="' + n(p[0] - 16) + '" cy="' + n(p[1] + dr / 4) + '" rx="15" ry="9" fill="' + c + '" transform="rotate(' + (-20 + dr) + ' ' + n(p[0] - 16) + ' ' + p[1] + ')"/>';
      s += '<ellipse cx="' + n(p[0] + 16) + '" cy="' + n(p[1] + dr / 4) + '" rx="15" ry="9" fill="' + c + '" transform="rotate(' + (20 - dr) + ' ' + n(p[0] + 16) + ' ' + p[1] + ')"/>';
      if (i === 2 && !wilt) s += '<path d="M' + p[0] + ',' + p[1] + ' l-4,-14 m4,14 l6,-12" stroke="' + STEM + '" stroke-width="2"/>';
    });
    var N = bez(stem, 0.62);
    var tw = stage >= 5 ? 5 : 2.4;
    var tc = wilt ? '#a08a4a' : (stage >= 5 ? LEAF_DARK : '#6aa043');
    var C = [stickX - 7, N[1] - 8];
    if (none) {
      s += '<path d="M' + N[0] + ',' + N[1] + ' C' + (N[0] + 40) + ',' + (N[1] - 10) + ' ' + (N[0] + 70) + ',' + (N[1] + 30) + ' ' + (N[0] + 64) + ',' + (N[1] + 60) + '" stroke="' + tc + '" stroke-width="2.4" fill="none"/>';
    } else if (stage === 1) {
      var tip = [N[0] + 92, N[1] - 34];
      s += '<path d="M' + N[0] + ',' + N[1] + ' C' + (N[0] + 30) + ',' + (N[1] - 4) + ' ' + (N[0] + 70) + ',' + (N[1] - 20) + ' ' + tip[0] + ',' + tip[1] + ' c6,-3 8,4 3,6" stroke="' + tc + '" stroke-width="2.4" fill="none" stroke-linecap="round"/>';
      s += '<ellipse cx="' + tip[0] + '" cy="' + tip[1] + '" rx="26" ry="11" fill="none" stroke="#2f63b0" stroke-width="2" stroke-dasharray="5 4"/>';
      s += arrow(tip[0] + 10, tip[1] + 11, tip[0] - 4, tip[1] + 11, '#2f63b0', 2);
    } else {
      if (stage === 2) {
        s += '<path d="M' + N[0] + ',' + N[1] + ' Q' + n((N[0] + C[0]) / 2) + ',' + n((N[1] + C[1]) / 2 + 22) + ' ' + C[0] + ',' + C[1] + '" stroke="' + tc + '" stroke-width="' + tw + '" fill="none"/>';
      } else {
        s += '<path d="' + coil(N, C, 7, 10) + '" stroke="' + tc + '" stroke-width="' + tw + '" fill="none" stroke-linejoin="round"/>';
      }
      for (var k = 0; k < 3; k++) {
        s += '<path d="M' + (stickX - 8) + ',' + (C[1] + k * 6) + ' C' + (stickX - 8) + ',' + (C[1] + k * 6 + 5) + ' ' + (stickX + 8) + ',' + (C[1] + k * 6 + 5) + ' ' + (stickX + 8) + ',' + (C[1] + k * 6) + '" stroke="' + tc + '" stroke-width="' + tw + '" fill="none"/>';
      }
      if (stage === 3) s += arrow(N[0] - 2, N[1] + 26, N[0] + 30, N[1] + 26, '#e07a4f', 3);
    }
    if (o.growth && !none) {
      s += '<circle cx="96" cy="88" r="70" fill="#fff" stroke="#2f63b0" stroke-width="2"/>';
      s += '<rect x="86" y="22" width="20" height="132" fill="#d1ad72"/>';
      s += '<path d="M40,60 C60,62 80,66 86,76 C92,88 110,92 118,84 C126,76 124,64 112,60" stroke="#6aa043" stroke-width="12" fill="none" stroke-linecap="round"/>';
      s += '<path d="M86,72 C90,82 104,86 112,80" stroke="#2f63b0" stroke-width="2" fill="none" stroke-dasharray="2 3"/>';
      s += '<path d="M46,50 C66,52 82,58 92,70 C104,82 120,82 126,74" stroke="#e07a4f" stroke-width="2" fill="none"/>';
    }
    if (o.labels) {
      var steps = { 1: 'المحلاق بيدور في الهوا', 2: 'لمس الدعامة ← لفّ حواليها', 3: 'الباقي بيتموّج لولبيًا ← طوله يقل', 4: 'الساق اتشد ناحية الدعامة واستقام', 5: 'المحلاق اتغلظ بأنسجة دعامية فقوي' };
      if (none) {
        s += label(N[0] + 60, N[1] + 56, 340, 210, 'ملقاش دعامة ← يذبل ويموت', '#9a6a2a');
        s += cap('محلاق من غير دعامة');
      } else {
        var at = stage === 1 ? [N[0] + 92, N[1] - 34] : (stage === 3 ? [n((N[0] + C[0]) / 2), n((N[1] + C[1]) / 2)] : (stage === 4 ? bez(stem, 0.9) : C));
        s += label(at[0], at[1], 400, stage === 4 ? 40 : 250, steps[stage], stage === 5 ? LEAF_DARK : '#2f63b0');
        if (o.growth) {
          s += label(100, 82, 150, 176, 'الجزء الملامس: نموه أبطأ', '#2f63b0');
          s += label(60, 52, 150, 206, 'الجزء البعيد: نموه أسرع ← يستطيل', '#e07a4f');
        }
        s += cap('حركة الشد في محلاق البازلاء — الخطوة ' + stage + ' من 5');
      }
    }
    return s + '</svg>';
  };

  /* ---------- 4. A bulb with contractile roots (النرجس) ----------
     opts: pulled (the bulb is down at the right depth), labels */
  V.bulb = function (o) {
    var y = o.pulled ? 222 : 168;
    var s = open('بصلة النرجس وجذورها الشادة', '#e8f4ff');
    s += '<rect x="0" y="120" width="480" height="200" fill="' + SOIL + '"/>';
    s += '<path d="M0,170 C120,166 240,176 480,168 M0,236 C140,230 300,242 480,232 M0,290 C160,286 320,296 480,288" stroke="#a87a4c" stroke-width="3" fill="none"/>';
    s += '<path d="M0,120 L480,120" stroke="#6aa34c" stroke-width="6"/>';
    for (var g = 6; g < 480; g += 14) s += '<path d="M' + g + ',118 l3,-9 m2,9 l4,-7" stroke="#6aa34c" stroke-width="2"/>';
    s += '<path d="M120,' + (o.pulled ? 222 : 222) + ' L360,222" stroke="#fff" stroke-width="2" stroke-dasharray="6 5" opacity="' + (o.pulled ? 0.9 : 0.75) + '"/>';
    // leaves and the flower above the ground
    s += '<path d="M240,' + (y - 44) + ' L240,120" stroke="#cfe3b5" stroke-width="10"/>';
    s += '<path d="M236,120 C230,80 214,50 200,22 M244,120 C250,84 266,56 286,30 M240,120 C240,90 240,60 238,40" stroke="' + LEAF + '" stroke-width="8" fill="none" stroke-linecap="round"/>';
    s += '<path d="M240,120 C242,90 252,60 262,40" stroke="#6aa043" stroke-width="3" fill="none"/>';
    s += '<g transform="translate(266,34)">';
    for (var p = 0; p < 6; p++) s += '<ellipse cx="0" cy="-11" rx="6" ry="11" fill="#fffdf2" stroke="#e7dcb5" transform="rotate(' + p * 60 + ')"/>';
    s += '<circle r="7" fill="#f6b73c" stroke="#e08a1e" stroke-width="2"/></g>';
    // roots: thin ones and the thick wrinkled contractile ones
    [[-30, -50], [-12, -22], [14, 20], [32, 54]].forEach(function (r) {
      s += '<path d="M' + (240 + r[0]) + ',' + (y + 36) + ' C' + (240 + r[0]) + ',' + (y + 60) + ' ' + (240 + r[1]) + ',' + (y + 66) + ' ' + (240 + r[1]) + ',' + Math.min(316, y + 92) + '" stroke="#efe6d2" stroke-width="2" fill="none"/>';
    });
    var cr = [[-6, -16], [6, 16]];
    cr.forEach(function (r) {
      var x0 = 240 + r[0], x1 = 240 + r[1];
      s += '<path d="M' + x0 + ',' + (y + 36) + ' L' + x1 + ',' + Math.min(312, y + 84) + '" stroke="#e8d7b0" stroke-width="7" stroke-linecap="round"/>';
      for (var w = 0; w < 6; w++) {
        var t = (w + 1) / 7;
        var wx = x0 + (x1 - x0) * t, wy = y + 36 + (Math.min(312, y + 84) - y - 36) * t;
        s += '<path d="M' + n(wx - 4) + ',' + n(wy) + ' l8,0" stroke="#b39a6a" stroke-width="1.6"/>';
      }
    });
    // the bulb
    s += '<path d="M240,' + (y - 46) + ' C262,' + (y - 20) + ' 284,' + (y - 6) + ' 280,' + (y + 18) + ' C276,' + (y + 40) + ' 204,' + (y + 40) + ' 200,' + (y + 18) + ' C196,' + (y - 6) + ' 218,' + (y - 20) + ' 240,' + (y - 46) + ' Z" fill="#efe2c4" stroke="#b89b63" stroke-width="2.5"/>';
    s += '<path d="M240,' + (y - 40) + ' C254,' + (y - 18) + ' 268,' + (y - 4) + ' 266,' + (y + 16) + ' M240,' + (y - 40) + ' C226,' + (y - 18) + ' 212,' + (y - 4) + ' 214,' + (y + 16) + '" stroke="#cdb688" stroke-width="2" fill="none"/>';
    s += '<rect x="214" y="' + (y + 30) + '" width="52" height="8" rx="3" fill="#a88a5a"/>';
    if (!o.pulled) {
      s += arrow(300, y - 6, 300, 212, '#e07a4f', 3);
      s += arrow(180, y - 6, 180, 212, '#e07a4f', 3);
    }
    if (o.labels) {
      s += label(240 + 12, y + 62, 372, 266, 'جذور شادة: بتتقلص وتشد البصلة لتحت', '#a5502a');
      s += label(130, 222, 92, 250, 'البعد الملائم من سطح الأرض', '#2f63b0');
      s += label(214, 40, 110, 40, 'الأجزاء الهوائية متأمّنة ضد الرياح', LEAF_DARK);
      s += cap(o.pulled ? 'البصلة نزلت للمستوى الملائم' : 'البصلة فوق أوي ← الجذور الشادة هتشدها لتحت');
    }
    return s + '</svg>';
  };

  /* ---------- 5. Two pulls compared: tendrils vs contractile roots ---------- opts: labels */
  V.pulls = function (o) {
    var s = open('المحاليق والجذور الشادة', '#f4f8ef');
    var inner = function (svg, x) { return '<g transform="translate(' + x + ',20) scale(0.49)">' + svg.replace(/^<svg[^>]*>/, '').replace(/<\/svg>$/, '') + '</g>'; };
    s += inner(V.tendril({ stage: 4 }), 2) + inner(V.bulb({ pulled: false }), 242);
    s += '<path d="M240,20 L240,300" stroke="#c7d3e6" stroke-width="2"/>';
    s += arrow(70, 214, 170, 214, '#e07a4f', 4);
    s += arrow(360, 196, 360, 262, '#e07a4f', 4);
    if (o.labels) {
      s += label(120, 214, 120, 252, 'المحاليق: تشد الساق ناحية الدعامة', '#2f63b0');
      s += label(360, 262, 360, 292, 'الجذور الشادة: تشد النبات لأسفل', '#a5502a');
    }
    return s + '</svg>';
  };

  /* ---------- 6. Tropisms ---------- opts: highlight: 'light' | 'gravity' | 'water', labels */
  V.tropism = function (o) {
    var hl = o.highlight;
    var s = open('الانتحاء', '#eef7ff');
    s += '<circle cx="430" cy="48" r="22" fill="#ffd25c"/>';
    for (var r = 0; r < 8; r++) { var q1 = pt(430, 48, 28, r * 45), q2 = pt(430, 48, 40, r * 45); s += '<path d="M' + q1 + ' L' + q2 + '" stroke="#ffd25c" stroke-width="3" stroke-linecap="round"/>'; }
    s += '<rect x="0" y="196" width="480" height="124" fill="' + SOIL + '"/><path d="M0,196 L480,196" stroke="#8a6238" stroke-width="3"/>';
    s += '<ellipse cx="86" cy="266" rx="58" ry="26" fill="#7cb7df" opacity="0.75"/>';
    for (var d = 0; d < 5; d++) s += '<path d="M' + (60 + d * 13) + ',' + (258 + (d % 2) * 8) + ' c-3,5 -4,7 -4,9 a4,4 0 0 0 8,0 c0,-2 -1,-4 -4,-9 Z" fill="#cfe9fb"/>';
    // the shoot bending to the light
    var shoot = [[220, 198], [222, 150], [252, 112], [312, 84]];
    s += '<path d="' + curve(shoot) + '" stroke="' + STEM + '" stroke-width="7" fill="none" stroke-linecap="round"/>';
    [0.45, 0.75].forEach(function (t) {
      var p = bez(shoot, t);
      s += '<ellipse cx="' + n(p[0] + 14) + '" cy="' + n(p[1] - 10) + '" rx="16" ry="8" fill="' + LEAF + '" transform="rotate(-30 ' + n(p[0] + 14) + ' ' + n(p[1] - 10) + ')"/>';
      s += '<ellipse cx="' + n(p[0] - 10) + '" cy="' + n(p[1] - 14) + '" rx="14" ry="7" fill="' + LEAF + '" transform="rotate(-70 ' + n(p[0] - 10) + ' ' + n(p[1] - 14) + ')"/>';
    });
    s += '<ellipse cx="320" cy="80" rx="12" ry="7" fill="' + LEAF + '" transform="rotate(-25 320 80)"/>';
    // roots: down (gravity) and towards the wet soil
    s += '<path d="M220,198 C220,236 218,270 216,312" stroke="#efe6d2" stroke-width="5" fill="none" stroke-linecap="round"/>';
    s += '<path d="M219,236 C196,244 164,256 132,262" stroke="#efe6d2" stroke-width="4" fill="none" stroke-linecap="round"/>';
    s += '<path d="M218,270 C200,276 180,282 150,284" stroke="#efe6d2" stroke-width="3" fill="none" stroke-linecap="round"/>';
    s += '<path d="M220,226 C236,232 250,240 262,248" stroke="#efe6d2" stroke-width="2.4" fill="none" stroke-linecap="round"/>';
    var c = function (k) { return hl === k ? '#e07a4f' : '#2f63b0'; };
    s += arrow(330, 76, 396, 54, c('light'), hl === 'light' ? 4 : 2.6);
    s += arrow(236, 262, 236, 306, c('gravity'), hl === 'gravity' ? 4 : 2.6);
    s += arrow(150, 246, 112, 246, c('water'), hl === 'water' ? 4 : 2.6);
    if (o.labels) {
      s += label(300, 88, 150, 60, 'الساق بتنحني ناحية الضوء', '#c98a00');
      s += label(236, 284, 360, 258, 'الجذر لتحت (الجاذبية)', '#8a6238', true);
      s += label(132, 262, 120, 214, 'الجذر ناحية الرطوبة', '#2f63b0');
      s += cap('الانتحاء في كل النباتات: للضوء والرطوبة والجاذبية');
    }
    return s + '</svg>';
  };

  /* ---------- 7. An Elodea leaf cell under the high power ----------
     opts: still (no moving chloroplasts), labels */
  V.elodea = function (o) {
    var clip = A.id('fld');
    var s = open('خلية من ورقة الإيلوديا تحت المجهر', '#1d2433');
    s += '<defs><clipPath id="' + clip + '"><circle cx="240" cy="158" r="146"/></clipPath></defs>';
    s += '<circle cx="240" cy="158" r="150" fill="#3a4357"/><g clip-path="url(#' + clip + ')"><rect x="0" y="0" width="480" height="320" fill="#eef7e6"/>';
    // neighbouring cells (a brick pattern)
    var cells = [[-108, 8], [66, 8], [240, 8], [414, 8], [-20, 104], [330, 104], [-108, 216], [66, 216], [240, 216], [414, 216]];
    cells.forEach(function (c) {
      s += '<rect x="' + c[0] + '" y="' + c[1] + '" width="170" height="92" rx="8" fill="#e3f2d6" stroke="#86b862" stroke-width="3"/>';
      for (var k = 0; k < 9; k++) {
        var cx = c[0] + 14 + (k * 19) % 150, cy = c[1] + (k % 2 ? 10 : 82);
        s += '<ellipse cx="' + cx + '" cy="' + cy + '" rx="5.5" ry="3.2" fill="#4f9a3f"/>';
      }
    });
    // the cell in the middle: wall, a thin layer of cytoplasm, the big vacuole
    var x0 = 154, y0 = 104, w = 172, h = 108;
    s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + w + '" height="' + h + '" rx="9" fill="#d3ecbd" stroke="#5f9a3c" stroke-width="4.5"/>';
    s += '<rect x="' + (x0 + 14) + '" y="' + (y0 + 14) + '" width="' + (w - 28) + '" height="' + (h - 28) + '" rx="6" fill="#f6fcf1" stroke="#b9dca1" stroke-width="1.2"/>';
    var path = 'M' + (x0 + 15) + ',' + (y0 + 7) + ' H' + (x0 + w - 15) + ' Q' + (x0 + w - 7) + ',' + (y0 + 7) + ' ' + (x0 + w - 7) + ',' + (y0 + 15) + ' V' + (y0 + h - 15) + ' Q' + (x0 + w - 7) + ',' + (y0 + h - 7) + ' ' + (x0 + w - 15) + ',' + (y0 + h - 7) + ' H' + (x0 + 15) + ' Q' + (x0 + 7) + ',' + (y0 + h - 7) + ' ' + (x0 + 7) + ',' + (y0 + h - 15) + ' V' + (y0 + 15) + ' Q' + (x0 + 7) + ',' + (y0 + 7) + ' ' + (x0 + 15) + ',' + (y0 + 7) + ' Z';
    var count = 16;
    var per = 2 * (w + h - 28);
    for (var k = 0; k < count; k++) {
      if (o.still) {
        var d = (k / count) * per, px, py, ang = 0;
        var top = w - 30, side = h - 30;
        if (d < top) { px = x0 + 15 + d; py = y0 + 7; }
        else if (d < top + side) { px = x0 + w - 7; py = y0 + 15 + (d - top); ang = 90; }
        else if (d < 2 * top + side) { px = x0 + w - 15 - (d - top - side); py = y0 + h - 7; }
        else { px = x0 + 7; py = y0 + h - 15 - (d - 2 * top - side); ang = 90; }
        s += '<ellipse cx="' + n(px) + '" cy="' + n(py) + '" rx="6" ry="3.4" fill="#2f8a2f" transform="rotate(' + ang + ' ' + n(px) + ' ' + n(py) + ')"/>';
      } else {
        s += '<ellipse rx="6" ry="3.4" fill="#2f8a2f"><animateMotion dur="24s" repeatCount="indefinite" rotate="auto" begin="' + n(-24 * k / count) + 's" path="' + path + '"/></ellipse>';
      }
    }
    // the direction of the stream (one way round)
    s += arrow(x0 + 60, y0 + 30, x0 + 110, y0 + 30, '#e07a4f', 2.6);
    s += arrow(x0 + 112, y0 + h - 30, x0 + 62, y0 + h - 30, '#e07a4f', 2.6);
    s += '</g>';
    if (o.labels) {
      s += label(x0 + w, y0 + 54, 412, 106, 'جدار الخلية', '#3f7a24');
      s += label(x0 + w - 7, y0 + 80, 408, 250, 'سيتوبلازم بيبطن الجدار', '#5f9a3c');
      s += label(x0 + 7, y0 + 40, 92, 52, 'بلاستيدات خضراء بتلف مع التيار', '#2f8a2f');
      s += label(x0 + 86, y0 + 30, 104, 268, 'دوران في اتجاه واحد', '#e07a4f');
      s += cap('خلية من ورقة الإيلوديا (القوة الكبرى للمجهر)');
    }
    return s + '</svg>';
  };
})();
