/* ==========================================================================
   «الدكتور والمزارع» — close-ups for Chapter 1 (الدعامة والحركة).
   Each view is 480 × 320. With { labels: true } the parts are named, as in
   the book. Options are listed above each view.
   ========================================================================== */
(function () {
  'use strict';

  var A = window.G12.BioArt;
  var V = A.views;
  var FONT = "Segoe UI, Tahoma, 'Noto Sans Arabic', Arial, sans-serif";
  var INK = '#2b3654';
  var BONE = ['#fbf5e8', '#e9dcc0', '#c9b48b'];

  function open(label, bg) {
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 320" role="img" aria-label="' + label + '"><rect width="480" height="320" fill="' + (bg || '#f3f7fc') + '"/>';
  }

  function boneGrad() {
    var g = A.id('bone');
    return { id: g, def: '<linearGradient id="' + g + '" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="' + BONE[1] + '"/><stop offset="0.45" stop-color="' + BONE[0] + '"/><stop offset="1" stop-color="' + BONE[2] + '"/></linearGradient>' };
  }

  /* A long bone from (x1,y1) to (x2,y2): a shaft with rounded ends. */
  function bone(x1, y1, x2, y2, w, fill, extra) {
    var dx = x2 - x1, dy = y2 - y1;
    var len = Math.sqrt(dx * dx + dy * dy);
    var ang = Math.atan2(dy, dx) * 180 / Math.PI;
    var k = w * 0.62;
    return '<g transform="translate(' + x1 + ',' + y1 + ') rotate(' + ang.toFixed(2) + ')"' + (extra || '') + '>' +
      '<path d="M' + k + ',' + (-w / 2) + ' L' + (len - k) + ',' + (-w / 2) + ' L' + (len - k) + ',' + (w / 2) + ' L' + k + ',' + (w / 2) + ' Z" fill="' + fill + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>' +
      '<circle cx="' + k * 0.7 + '" cy="' + (-w * 0.38) + '" r="' + k + '" fill="' + fill + '" stroke="' + BONE[2] + '" stroke-width="1.5"/><circle cx="' + k * 0.7 + '" cy="' + (w * 0.38) + '" r="' + k + '" fill="' + fill + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>' +
      '<circle cx="' + (len - k * 0.7) + '" cy="' + (-w * 0.38) + '" r="' + k + '" fill="' + fill + '" stroke="' + BONE[2] + '" stroke-width="1.5"/><circle cx="' + (len - k * 0.7) + '" cy="' + (w * 0.38) + '" r="' + k + '" fill="' + fill + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>' +
      '<path d="M' + k + ',' + (-w / 2 + 1.5) + ' L' + (len - k) + ',' + (-w / 2 + 1.5) + ' L' + (len - k) + ',' + (w / 2 - 1.5) + ' L' + k + ',' + (w / 2 - 1.5) + ' Z" fill="' + fill + '"/>' +
      '</g>';
  }

  /* A name with a thin line to the part it names. */
  function label(x, y, lx, ly, text, color, dark) {
    var w = Math.max(40, text.length * 6.7 + 16);
    lx = Math.max(w / 2 + 4, Math.min(480 - w / 2 - 4, lx));
    ly = Math.max(14, Math.min(306, ly));
    color = color || '#2f63b0';
    return '<g font-family="' + FONT + '">' +
      '<path d="M' + x + ',' + y + ' L' + lx + ',' + ly + '" stroke="' + color + '" stroke-width="1.6"/>' +
      '<circle cx="' + x + '" cy="' + y + '" r="3.2" fill="' + color + '"/>' +
      '<rect x="' + (lx - w / 2) + '" y="' + (ly - 12) + '" width="' + w + '" height="24" rx="12" fill="' + (dark ? '#0f1726' : '#ffffff') + '" stroke="' + color + '" stroke-width="1.6" opacity="0.96"/>' +
      '<text x="' + lx + '" y="' + (ly + 5) + '" text-anchor="middle" direction="rtl" font-size="13" font-weight="700" fill="' + (dark ? '#e6efff' : INK) + '">' + text + '</text></g>';
  }

  function caption(text, dark) {
    return '<text x="240" y="308" text-anchor="middle" direction="rtl" font-family="' + FONT + '" font-size="12.5" font-weight="700" fill="' + (dark ? '#c9d7ee' : '#56617c') + '">' + text + '</text>';
  }

  /* ---------- 1. The lower leg and foot, from the side ----------
     opts: swelling, torn (Achilles), state: 'cramp' | 'fatigue', labels */
  V.leg = function (o) {
    var g = boneGrad();
    var skin = A.id('skin');
    var s = open('الساق والقدم من الجنب');
    s += '<defs>' + g.def + '<linearGradient id="' + skin + '" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c58a63"/><stop offset="0.5" stop-color="#e2ae84"/><stop offset="1" stop-color="#d49b72"/></linearGradient>' +
      '<radialGradient id="' + skin + 'r" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#e0453a" stop-opacity="0.75"/><stop offset="1" stop-color="#e0453a" stop-opacity="0"/></radialGradient></defs>';
    s += '<rect x="0" y="282" width="480" height="38" fill="#dfe8f2"/>';
    var leg = 'M196,0 C166,40 156,92 166,132 C176,170 196,196 200,214 C202,234 184,250 188,268 C192,284 214,290 236,288 L330,290 C360,290 384,292 400,288 C414,284 420,272 410,264 C390,256 356,250 322,240 C300,233 284,226 278,208 C272,180 266,90 264,0 Z';
    s += '<path d="' + leg + '" fill="url(#' + skin + ')" opacity="' + (o.labels ? 0.38 : 1) + '"/>';
    s += '<path d="' + leg + '" fill="none" stroke="#a06a49" stroke-width="2" opacity="0.6"/>';
    if (!o.labels) {
      s += '<ellipse cx="300" cy="300" rx="130" ry="8" fill="#000" opacity="0.08"/>';
      s += '<path d="M258,6 C260,80 264,160 268,206" stroke="#ffffff" stroke-width="8" opacity="0.16" fill="none" stroke-linecap="round"/>';
      s += '<path d="M176,60 C170,96 172,126 182,150" stroke="#a06a49" stroke-width="6" opacity="0.18" fill="none" stroke-linecap="round"/>';
      s += '<ellipse cx="254" cy="214" rx="11" ry="9" fill="#c58a63" opacity="0.55"/><path d="M246,210 Q254,204 262,210" stroke="#a06a49" stroke-width="1.5" fill="none" opacity="0.6"/>';
      s += '<path d="M370,262 Q376,276 372,288 M384,264 Q390,276 388,288 M396,266 Q402,276 400,286" stroke="#a06a49" stroke-width="1.4" fill="none" opacity="0.5"/>';
      s += '<path d="M400,266 Q410,266 414,274 Q408,278 402,276 Z" fill="#f4d3bf" opacity="0.9"/>';
      s += '<path d="M200,214 C204,232 196,244 192,256" stroke="#a06a49" stroke-width="2" fill="none" opacity="0.35"/>';
    }
    if (o.labels) {
      // bones: tibia (front), fibula (behind), heel bone and the foot bones
      s += bone(246, 4, 250, 222, 22, 'url(#' + g.id + ')');
      s += bone(222, 10, 232, 214, 10, 'url(#' + g.id + ')');
      s += '<path d="M206,232 C222,226 252,226 268,236 C276,250 262,268 236,270 C214,272 198,262 198,250 C198,242 200,236 206,232 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="1.5"/>';
      s += '<path d="M262,232 C284,238 330,248 380,262 L382,272 C330,266 290,260 262,256 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="1.5"/>';
      // the calf muscle and the Achilles tendon
      var musc = o.state === 'cramp' ? '#d2342a' : '#c9574b';
      s += '<path d="M200,22 C160,52 152,100 164,138 C172,160 186,174 200,182 C214,170 222,150 222,120 C222,80 214,44 200,22 Z" fill="' + musc + '" opacity="0.9"/>';
      s += '<path d="M176,60 C172,90 174,124 186,156 M192,40 C190,80 192,130 202,170 M208,50 C212,90 212,130 206,166" stroke="#ffffff" stroke-width="1.4" opacity="0.35" fill="none"/>';
      if (o.torn) {
        s += '<path d="M198,182 L202,204 M204,214 L206,236" stroke="#f2ead8" stroke-width="10" stroke-linecap="round"/>';
        s += '<path d="M194,206 L212,212" stroke="#e0453a" stroke-width="3" stroke-dasharray="3 3"/>';
      } else {
        s += '<path d="M198,182 C201,200 203,218 206,236" stroke="#f2ead8" stroke-width="10" stroke-linecap="round" fill="none"/>';
        s += '<path d="M198,182 C201,200 203,218 206,236" stroke="#d8ccb4" stroke-width="2" fill="none"/>';
      }
    }
    if (o.state === 'fatigue' && o.labels) {
      for (var i = 0; i < 16; i++) s += '<circle cx="' + (172 + (i * 37) % 44) + '" cy="' + (60 + (i * 53) % 110) + '" r="2.6" fill="#ffd166"/>';
    }
    if (o.state === 'cramp' && !o.labels) s += '<path d="M170,80 l8,-6 l4,8 l8,-6 M168,120 l8,-6 l4,8 l8,-6" stroke="#e0453a" stroke-width="3" fill="none"/>';
    if (o.swelling) s += '<ellipse cx="200" cy="226" rx="34" ry="30" fill="url(#' + skin + 'r)"/>';
    if (o.labels) {
      s += label(186, 110, 92, 70, 'العضلة التوأمية (بطن الساق)', '#c9574b');
      s += label(203, 214, 100, 200, o.torn ? 'وتر أكيليس (متمزق)' : 'وتر أكيليس', '#a8875a');
      s += label(214, 258, 110, 262, 'عظمة الكعب', '#b9a37c');
      s += label(250, 70, 360, 50, 'القصبة', '#b9a37c');
      s += label(226, 120, 340, 120, 'الشظية', '#b9a37c');
      if (o.state === 'fatigue') s += label(178, 100, 380, 170, 'حمض اللاكتيك', '#e0a100');
    }
    return s + '</svg>';
  };

  /* ---------- 2. The knee joint (opened, from the front) ----------
     opts: lowFluid, torn (a cruciate ligament), labels */
  V.knee = function (o) {
    var g = boneGrad();
    var s = open('مفصل الركبة من جوه');
    s += '<defs>' + g.def + '</defs>';
    // the capsule with the synovial fluid
    s += '<path d="M150,120 C150,96 330,96 330,120 L330,200 C330,226 150,226 150,200 Z" fill="' + (o.lowFluid ? '#eef3f8' : '#cfe8ff') + '" stroke="#7aa8f0" stroke-width="2.5" stroke-dasharray="' + (o.labels ? '0' : '6 4') + '"/>';
    // femur (thigh bone) with two knobs
    s += '<path d="M206,0 L274,0 L278,110 C300,112 316,124 312,146 C308,162 286,164 262,154 C252,150 228,150 218,154 C194,164 172,162 168,146 C164,124 180,112 202,110 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="2"/>';
    // tibia and fibula
    s += '<path d="M176,176 C196,170 284,170 304,176 C312,188 296,198 282,202 L276,320 L204,320 L198,202 C184,198 168,188 176,176 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M316,206 C326,206 330,214 326,224 L322,320 L308,320 L306,224 C302,214 306,206 316,206 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="2"/>';
    // the smooth cartilage on the ends of the bones
    s += '<path d="M170,146 C174,160 194,162 218,152 C228,148 252,148 262,152 C286,162 306,160 310,146 C306,156 286,158 262,148 C252,144 228,144 218,148 C194,158 174,156 170,146 Z" fill="#b9e3ff" stroke="#8cc6ef" stroke-width="2"/>';
    s += '<path d="M178,176 C198,171 282,171 302,176 L302,181 C282,176 198,176 178,181 Z" fill="#b9e3ff" stroke="#8cc6ef" stroke-width="2"/>';
    // cruciate ligaments (front and back) and the two side ligaments
    s += '<path d="M226,154 L262,176" stroke="#e9c46a" stroke-width="7" stroke-linecap="round"/>';
    if (o.torn) s += '<path d="M254,154 L240,164 M232,170 L218,176" stroke="#e05d5d" stroke-width="7" stroke-linecap="round"/>';
    else s += '<path d="M254,154 L218,176" stroke="#f2a65a" stroke-width="7" stroke-linecap="round"/>';
    s += '<path d="M166,134 C160,160 164,186 176,204" stroke="#e9c46a" stroke-width="6" fill="none" stroke-linecap="round"/>';
    s += '<path d="M314,134 C322,160 320,186 312,206" stroke="#e9c46a" stroke-width="6" fill="none" stroke-linecap="round"/>';
    // the knee cap, seen through
    s += '<ellipse cx="240" cy="118" rx="26" ry="30" fill="#f7efdc" opacity="0.55" stroke="' + BONE[2] + '" stroke-width="2" stroke-dasharray="4 3"/>';
    if (o.lowFluid) s += '<path d="M200,160 l6,6 m4,-6 l6,6 M262,160 l6,6 m4,-6 l6,6" stroke="#e0453a" stroke-width="2.5"/>';
    if (o.labels) {
      s += label(240, 40, 110, 34, 'الفخذ', '#b9a37c');
      s += label(240, 270, 110, 280, 'القصبة (داخلية)', '#b9a37c');
      s += label(316, 280, 400, 296, 'الشظية (خارجية)', '#b9a37c');
      s += label(240, 100, 370, 30, 'الرضفة (قدام الركبة)', '#b9a37c');
      s += label(296, 152, 404, 92, 'غضروف أملس', '#5fa8dc');
      s += label(200, 196, 76, 150, o.lowFluid ? 'سائل زلالي قليل' : 'سائل زلالي', '#5b8fd8');
      s += label(244, 166, 400, 176, o.torn ? 'رباط صليبي متمزق' : 'الرباط الصليبي', o.torn ? '#e05d5d' : '#d9902f');
      s += label(166, 180, 72, 216, 'رباط وسطي', '#c9a227');
      s += label(318, 186, 412, 236, 'رباط جانبي', '#c9a227');
    }
    return s + '</svg>';
  };

  /* ---------- 3. A chest X-ray ----------
     opts: highlight: 'floating' | 'sternum' | 'broken', labels */
  V['xray-chest'] = function (o) {
    var s = open('أشعة على الصدر', '#0b1220');
    s += '<path d="M120,320 C120,200 150,120 240,110 C330,120 360,200 360,320 Z" fill="#1a2436"/>';
    // spine
    for (var v = 0; v < 15; v++) s += '<rect x="230" y="' + (40 + v * 18) + '" width="20" height="14" rx="4" fill="#8193ad" opacity="0.8"/>';
    // clavicles
    s += '<path d="M236,62 C200,56 170,64 140,56 M244,62 C280,56 310,64 340,56" stroke="#c9d6ea" stroke-width="8" fill="none" stroke-linecap="round"/>';
    // sternum with its lower cartilage part
    var sh = o.highlight === 'sternum';
    s += '<path d="M232,80 L248,80 L250,170 L240,186 L230,170 Z" fill="' + (sh ? '#ffd166' : '#cfdaea') + '"/>';
    s += '<path d="M231,170 L249,170 L240,196 Z" fill="' + (sh ? '#ffe9a8' : '#7c8ea8') + '"/>';
    // ribs: 10 pairs reach the sternum (through cartilage), 2 short pairs float
    for (var i = 0; i < 12; i++) {
      var y = 72 + i * 15;
      var wdt = 70 + Math.min(i, 7) * 9 - (i > 8 ? (i - 8) * 6 : 0);
      var floating = i >= 10;
      var color = floating && (o.highlight === 'floating' || o.highlight === 'broken') ? '#ffd166' : '#d6e1f1';
      [-1, 1].forEach(function (side) {
        var x0 = 240 + side * 12;
        var xo = 240 + side * wdt;
        if (!floating) {
          var xe = 240 + side * 14;
          var ye = 88 + i * 9;
          s += '<path d="M' + x0 + ',' + y + ' C' + (xo + side * 6) + ',' + (y - 8) + ' ' + (xo + side * 4) + ',' + (y + 34) + ' ' + (240 + side * 46) + ',' + (y + 36) + '" stroke="' + color + '" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.92"/>';
          s += '<path d="M' + (240 + side * 46) + ',' + (y + 36) + ' Q' + (240 + side * 30) + ',' + (ye + 8) + ' ' + xe + ',' + ye + '" stroke="#6f8199" stroke-width="3.5" fill="none" opacity="0.8"/>';
        } else {
          s += '<path d="M' + x0 + ',' + y + ' C' + (xo - side * 2) + ',' + (y - 2) + ' ' + (xo - side * 8) + ',' + (y + 18) + ' ' + (240 + side * (wdt - 18)) + ',' + (y + 24) + '" stroke="' + color + '" stroke-width="5" fill="none" stroke-linecap="round"/>';
        }
      });
    }
    if (o.highlight === 'broken') s += '<path d="M148,240 l6,-8 l-4,-4 l7,-8" stroke="#ff5d5d" stroke-width="3" fill="none"/>';
    if (o.labels) {
      s += label(240, 120, 88, 96, 'عظمة القص (أمامية)', '#ffd166', true);
      s += label(240, 184, 96, 140, 'جزء القص السفلي غضروفي', '#9fb6d6', true);
      s += label(140, 250, 80, 290, 'ضلوع عائمة', '#ffd166', true);
      s += label(240, 250, 388, 296, 'الفقرات الصدرية', '#9fb6d6', true);
      s += label(300, 60, 400, 26, 'الترقوة', '#9fb6d6', true);
      s += label(306, 140, 408, 120, '10 أزواج متصلة بالقص', '#9fb6d6', true);
    }
    return s + '</svg>';
  };

  /* ---------- 4. A side X-ray of the spine ----------
     opts: highlight: 'cervical' | 'thoracic' | 'lumbar' | 'sacral' | 'coccyx', labels */
  V['xray-spine'] = function (o) {
    var s = open('أشعة جانبية على العمود الفقري', '#0b1220');
    var groups = [
      { id: 'cervical', n: 7, h: 7, w: 24, name: 'عنقية: 7 متمفصلة' },
      { id: 'thoracic', n: 12, h: 9, w: 30, name: 'صدرية: 12 متمفصلة' },
      { id: 'lumbar', n: 5, h: 12.5, w: 42, name: 'قطنية: 5 (أكبرها)' }
    ];
    var y = 8;
    var colors = { cervical: '#7cc6ff', thoracic: '#ffd166', lumbar: '#9be38a', sacral: '#f4a3c9', coccyx: '#c3a6ff' };
    var marks = {};
    groups.forEach(function (gr) {
      var start = y;
      for (var i = 0; i < gr.n; i++) {
        var x = 240 + Math.sin((y - 14) / 260 * Math.PI * 1.6) * 22;
        var on = o.highlight === gr.id || o.labels;
        s += '<rect x="' + (x - gr.w / 2) + '" y="' + y + '" width="' + gr.w + '" height="' + gr.h + '" rx="4" fill="' + (on ? colors[gr.id] : '#9fb0c8') + '" opacity="' + (on ? 0.95 : 0.75) + '"/>';
        s += '<path d="M' + (x + gr.w / 2) + ',' + (y + gr.h / 2) + ' l12,4" stroke="#7d8ca3" stroke-width="3"/>';
        y += gr.h + 2.2;
      }
      marks[gr.id] = { y: (start + y) / 2, x: 240 + Math.sin(((start + y) / 2 - 14) / 260 * Math.PI * 1.6) * 22 };
    });
    var sx = 240 + Math.sin((y - 14) / 260 * Math.PI * 1.6) * 22;
    var sacOn = o.highlight === 'sacral' || o.labels;
    s += '<path d="M' + (sx - 24) + ',' + y + ' L' + (sx + 26) + ',' + y + ' L' + (sx + 10) + ',' + (y + 30) + ' L' + (sx - 12) + ',' + (y + 27) + ' Z" fill="' + (sacOn ? colors.sacral : '#9fb0c8') + '"/>';
    s += '<path d="M' + (sx - 18) + ',' + (y + 8) + ' L' + (sx + 20) + ',' + (y + 8) + ' M' + (sx - 14) + ',' + (y + 16) + ' L' + (sx + 16) + ',' + (y + 16) + '" stroke="#0b1220" stroke-width="1" opacity="0.4"/>';
    marks.sacral = { x: sx, y: y + 14 };
    y -= 14;
    var cocOn = o.highlight === 'coccyx' || o.labels;
    s += '<path d="M' + (sx - 10) + ',' + (y + 44) + ' L' + (sx + 8) + ',' + (y + 46) + ' L' + (sx - 6) + ',' + (y + 62) + ' Z" fill="' + (cocOn ? colors.coccyx : '#9fb0c8') + '"/>';
    marks.coccyx = { x: sx - 2, y: y + 52 };
    if (o.labels) {
      s += label(marks.cervical.x - 14, marks.cervical.y, 100, marks.cervical.y, 'عنقية: 7 متمفصلة', colors.cervical, true);
      s += label(marks.thoracic.x - 16, marks.thoracic.y, 100, marks.thoracic.y, 'صدرية: 12 متمفصلة', colors.thoracic, true);
      s += label(marks.lumbar.x - 20, marks.lumbar.y, 100, marks.lumbar.y, 'قطنية: 5 (أكبرها)', colors.lumbar, true);
      s += label(marks.sacral.x + 22, marks.sacral.y, 380, marks.sacral.y - 10, 'عجزية: 5 ملتحمة', colors.sacral, true);
      s += label(marks.coccyx.x + 6, marks.coccyx.y, 380, marks.coccyx.y + 16, 'عصعصية: 4 ملتحمة', colors.coccyx, true);
    } else if (o.highlight) {
      var m = marks[o.highlight];
      s += '<circle cx="' + m.x + '" cy="' + m.y + '" r="30" fill="none" stroke="#ff7b7b" stroke-width="3" stroke-dasharray="6 4"/>';
    }
    return s + '</svg>';
  };

  /* ---------- 5. One vertebra from above ----------
     opts: rib (a rib joined to it), labels */
  V.vertebra = function (o) {
    var g = boneGrad();
    var s = open('فقرة من فوق');
    s += '<defs>' + g.def + '</defs>';
    // body (front), arch, processes
    s += '<ellipse cx="240" cy="96" rx="78" ry="56" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="2.5"/>';
    s += '<path d="M180,132 C176,170 196,206 222,214 L240,280 L258,214 C284,206 304,170 300,132 C290,150 270,156 240,156 C210,156 190,150 180,132 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="2.5"/>';
    s += '<path d="M184,152 L104,176 L102,196 L192,180 Z M296,152 L376,176 L378,196 L288,180 Z" fill="url(#' + g.id + ')" stroke="' + BONE[2] + '" stroke-width="2.5"/>';
    // the canal with the spinal cord
    s += '<ellipse cx="240" cy="182" rx="30" ry="24" fill="#f3f7fc" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<ellipse cx="240" cy="182" rx="17" ry="13" fill="#ffe08a" stroke="#e0b84a" stroke-width="2"/>';
    if (o.rib) {
      s += '<path d="M330,110 C380,110 430,140 470,190" stroke="' + BONE[2] + '" stroke-width="16" fill="none" stroke-linecap="round"/>';
      s += '<path d="M330,110 C380,110 430,140 470,190" stroke="' + BONE[0] + '" stroke-width="12" fill="none" stroke-linecap="round"/>';
      s += '<path d="M372,182 C400,180 430,178 470,196" stroke="' + BONE[0] + '" stroke-width="6" fill="none" opacity="0.8"/>';
    }
    if (o.labels) {
      s += label(240, 80, 240, 22, 'جسم الفقرة (الجزء الأمامي السميك)', '#b9a37c');
      s += label(110, 186, 70, 240, 'نتوء مستعرض', '#b9a37c');
      s += label(370, 186, 410, 240, 'نتوء مستعرض', '#b9a37c');
      s += label(214, 196, 110, 290, 'الحلقة العصبية', '#b9a37c');
      s += label(240, 268, 360, 292, 'النتوء الشوكي (خلفي مائل لتحت)', '#b9a37c');
      s += label(252, 182, 380, 134, 'القناة العصبية + الحبل الشوكي', '#e0b84a');
      if (o.rib) s += label(420, 150, 400, 60, 'ضلع (بجسم الفقرة والنتوء المستعرض)', '#b9a37c');
    }
    return s + '</svg>';
  };

  /* ---------- 6. The skull from the side ---------- opts: labels */
  /* A serrated (sutured) line through the points. */
  function zig(pts, amp) {
    var d = 'M' + pts[0][0] + ',' + pts[0][1];
    for (var i = 1; i < pts.length; i++) {
      var a = pts[i - 1], b = pts[i];
      var dx = b[0] - a[0], dy = b[1] - a[1];
      var len = Math.sqrt(dx * dx + dy * dy), n = Math.max(2, Math.round(len / 9));
      var nx = -dy / len, ny = dx / len;
      for (var k = 1; k <= n; k++) {
        var t = k / n, side = (k % 2 ? 1 : -1) * (k === n ? 0 : amp);
        d += ' L' + (a[0] + dx * t + nx * side).toFixed(1) + ',' + (a[1] + dy * t + ny * side).toFixed(1);
      }
    }
    return d;
  }

  V.skull = function (o) {
    var g = boneGrad();
    var s = open('الجمجمة من الجنب');
    s += '<defs>' + g.def + '</defs>';
    var L = o.labels;
    var cranium = 'M372,150 C380,120 372,82 340,58 C305,34 240,28 190,44 C140,60 112,104 116,148 C118,176 134,196 158,208 C190,218 230,214 252,206 C270,196 290,186 312,180 C318,164 326,150 340,144 C352,140 364,142 372,150 Z';
    var face = 'M252,206 C270,196 290,186 312,180 C318,164 326,150 340,144 C352,140 364,142 372,150 C378,162 386,172 392,186 L384,196 C390,208 388,218 382,226 C384,234 382,240 376,246 L320,246 C312,234 306,224 296,216 C282,214 266,214 252,206 Z';
    var jaw = 'M264,214 C258,236 262,264 280,282 C304,293 344,297 370,290 C382,286 386,276 382,262 L378,256 L320,256 L306,220 L298,212 L290,222 C286,216 280,210 272,208 Z';
    s += '<ellipse cx="250" cy="300" rx="150" ry="10" fill="#dbe3ee"/>';
    s += '<path d="' + cranium + '" fill="' + (L ? '#e2d8ff' : 'url(#' + g.id + ')') + '" stroke="' + BONE[2] + '" stroke-width="2.5"/>';
    s += '<path d="' + jaw + '" fill="' + (L ? '#ffd2bd' : 'url(#' + g.id + ')') + '" stroke="' + BONE[2] + '" stroke-width="2.5"/>';
    s += '<path d="' + face + '" fill="' + (L ? '#ffe0cf' : 'url(#' + g.id + ')') + '" stroke="' + BONE[2] + '" stroke-width="2.5"/>';
    // the vault's roundness
    s += '<path d="M150,90 C180,56 240,44 300,56" stroke="#fff" stroke-width="10" stroke-linecap="round" fill="none" opacity="0.35"/>';
    // cheekbone and its arch towards the ear
    s += '<path d="M262,202 C282,194 302,190 322,194 C330,198 334,206 330,212 C306,208 284,210 264,214 Z" fill="' + (L ? '#ffd2bd' : BONE[1]) + '" stroke="' + BONE[2] + '" stroke-width="1.8"/>';
    // eye socket, nose opening, ear hole
    s += '<ellipse cx="344" cy="172" rx="21" ry="20" fill="#4f4032"/><ellipse cx="348" cy="176" rx="12" ry="11" fill="#2f261d"/>';
    s += '<path d="M380,190 C391,197 391,214 381,221 C373,214 371,200 380,190 Z" fill="#3b3027"/>';
    s += '<ellipse cx="254" cy="202" rx="7" ry="8" fill="#3b3027"/>';
    // teeth
    for (var t = 0; t < 7; t++) {
      var tx = 326 + t * 7.6;
      s += '<rect x="' + tx + '" y="243" width="6.6" height="11" rx="2.5" fill="#fbf7ee" stroke="#b9a989" stroke-width="1"/>';
      s += '<rect x="' + tx + '" y="255" width="6.6" height="10" rx="2.5" fill="#fbf7ee" stroke="#b9a989" stroke-width="1"/>';
    }
    // the sutures: serrated edges joined firmly (fibrous joints)
    var su = 'stroke="#8b7a62" stroke-width="1.8" fill="none" stroke-linejoin="round"';
    s += '<path d="' + zig([[266, 34], [272, 90], [286, 140], [300, 184]], 3.2) + '" ' + su + '/>';
    s += '<path d="' + zig([[178, 48], [160, 110], [150, 166], [158, 206]], 3.2) + '" ' + su + '/>';
    s += '<path d="' + zig([[206, 208], [222, 168], [262, 150], [292, 166], [304, 184]], 2.6) + '" ' + su + '/>';
    // the big hole in the base (seen through the bone)
    s += '<ellipse cx="200" cy="214" rx="22" ry="6" fill="none" stroke="#4a3f33" stroke-width="2" stroke-dasharray="4 3"/>';
    if (L) {
      s += label(200, 110, 120, 28, 'الجزء المخي (خلفي): 8 عظام', '#8b6fd6');
      s += label(356, 234, 372, 304, 'الجزء الوجهي (أمامي): 14 عظمة', '#e07a4f');
      s += label(276, 92, 380, 26, 'اتصال مسنن متين (مفصل ليفي)', '#8b7a62');
      s += label(200, 214, 120, 270, 'ثقب كبير في القاع (المخ ↔ الحبل الشوكي)', '#4a3f33');
    }
    return s + '</svg>';
  };

  /* ---------- 7. The shoulder girdle and the upper limb ---------- opts: labels, highlight */
  V.arm = function (o) {
    var g = boneGrad();
    var f = 'url(#' + g.id + ')';
    var s = open('عظام الحزام الصدري والطرف العلوي');
    s += '<defs>' + g.def + '</defs>';
    // scapula (behind, a triangle) and clavicle (in front, thin)
    s += '<path d="M60,40 L170,36 L160,70 C150,110 120,150 90,160 C76,120 66,80 60,40 Z" fill="' + BONE[1] + '" opacity="0.85" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<circle cx="164" cy="64" r="13" fill="#d8c8a6" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M40,28 C80,18 120,34 172,40" stroke="' + BONE[2] + '" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M40,28 C80,18 120,34 172,40" stroke="' + BONE[0] + '" stroke-width="8" fill="none" stroke-linecap="round"/>';
    // humerus, ulna, radius
    s += bone(170, 64, 280, 150, 18, f);
    s += bone(282, 152, 376, 214, 11, f);
    s += bone(286, 140, 378, 196, 9, f);
    // wrist (8 small bones in two rows), palm (5), fingers
    for (var r = 0; r < 2; r++) for (var c = 0; c < 4; c++) s += '<rect x="' + (382 + r * 13) + '" y="' + (180 + c * 11 - r * 2) + '" width="11" height="9" rx="3" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="1"/>';
    for (var m = 0; m < 5; m++) {
      var y0 = 172 + m * 13;
      s += bone(410, 184 + m * 7, 436, y0, 5, f);
      var n = m === 0 ? 2 : 3;
      var x = 438;
      for (var p = 0; p < n; p++) { s += bone(x, y0, x + 11, y0 + (m - 2) * 1.5, 4, f); x += 12; }
    }
    if (o.labels) {
      s += label(100, 90, 60, 200, 'لوح الكتف (ظهرية مثلثة)', '#b9a37c');
      s += label(100, 26, 230, 20, 'الترقوة (بطنية رفيعة)', '#b9a37c');
      s += label(164, 64, 130, 150, 'التجويف الأروح ← المفصل الكتفي', '#d9902f');
      s += label(226, 106, 220, 200, 'العضد', '#b9a37c');
      s += label(334, 176, 300, 260, 'الزند (ثابت)', '#b9a37c');
      s += label(330, 166, 330, 106, 'الكعبرة (أصغر وبتتحرك)', '#b9a37c');
      s += label(394, 200, 420, 270, 'الرسغ: 8 في صفين', '#b9a37c');
      s += label(452, 196, 440, 140, 'راحة 5 + سلاميات 14', '#b9a37c');
    }
    return s + '</svg>';
  };

  /* ---------- 8. Half of the pelvis and the lower limb ---------- opts: labels */
  V.legbones = function (o) {
    var g = boneGrad();
    var f = 'url(#' + g.id + ')';
    var s = open('نصف الحوض والطرف السفلي');
    s += '<defs>' + g.def + '</defs>';
    // ilium, pubis, ischium around the acetabulum
    s += '<path d="M40,30 C90,10 150,30 160,74 C150,96 120,104 100,104 C76,90 54,64 40,30 Z" fill="' + (o.labels ? '#f1e3b8' : f) + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M150,90 C176,96 196,110 204,128 L188,136 C176,122 160,114 142,110 Z" fill="' + (o.labels ? '#f7d3b0' : f) + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M96,104 C104,130 120,146 142,148 L150,132 C134,126 122,116 116,100 Z" fill="' + (o.labels ? '#e6d2f4' : f) + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<circle cx="134" cy="104" r="17" fill="#d1bf9a" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<circle cx="138" cy="106" r="11" fill="' + BONE[0] + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>';
    // femur, patella, tibia, fibula
    s += bone(144, 110, 270, 186, 18, f);
    s += '<ellipse cx="278" cy="176" rx="11" ry="9" fill="' + BONE[0] + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += bone(276, 196, 380, 250, 15, f);
    s += bone(282, 210, 378, 264, 8, f);
    // ankle bones (7, the back one makes the heel), sole bones (5), toes
    s += '<path d="M382,248 C392,240 410,244 412,256 C414,270 398,276 386,272 C378,266 376,256 382,248 Z" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>';
    for (var t = 0; t < 6; t++) s += '<rect x="' + (402 + (t % 3) * 10) + '" y="' + (250 + Math.floor(t / 3) * 10) + '" width="9" height="8" rx="3" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="1"/>';
    for (var m = 0; m < 5; m++) {
      s += bone(432, 250 + m * 6, 456, 254 + m * 7, 4, f);
      s += bone(458, 254 + m * 7, 470, 256 + m * 7.4, 3, f);
    }
    if (o.labels) {
      s += label(90, 50, 70, 156, 'الحرقفة (ظهرية)', '#d4b25f');
      s += label(178, 118, 230, 80, 'العانة (أمامية بطنية)', '#e0975c');
      s += label(116, 130, 70, 210, 'الورك (خلفية بطنية)', '#a77fd0');
      s += label(134, 104, 230, 34, 'التجويف الحقي ← مفصل الفخذ', '#d9902f');
      s += label(206, 148, 190, 230, 'الفخذ', '#b9a37c');
      s += label(278, 176, 300, 120, 'الرضفة', '#b9a37c');
      s += label(326, 222, 300, 290, 'القصبة (داخلية)', '#b9a37c');
      s += label(342, 246, 420, 300, 'الشظية (خارجية)', '#b9a37c');
      s += label(394, 262, 420, 206, 'رسغ القدم: 7 (أكبرها الكعب)', '#b9a37c');
    }
    return s + '</svg>';
  };

  /* ---------- 9. The three kinds of joints ---------- opts: highlight: 0 | 1 | 2, labels */
  V.joints = function (o) {
    var g = boneGrad();
    var f = 'url(#' + g.id + ')';
    var s = open('أنواع المفاصل');
    s += '<defs>' + g.def + '</defs>';
    var panels = [
      { x: 80, title: 'ليفي', where: 'عظام الجمجمة' },
      { x: 240, title: 'غضروفي', where: 'بين أجسام الفقرات' },
      { x: 400, title: 'زلالي', where: 'الركبة والكوع والكتف' }
    ];
    panels.forEach(function (p, i) {
      var on = o.highlight === i;
      s += '<rect x="' + (p.x - 72) + '" y="20" width="144" height="250" rx="16" fill="' + (on ? '#fff3c4' : '#ffffff') + '" stroke="' + (on ? '#ffd25c' : '#dbe5f5') + '" stroke-width="2"/>';
    });
    // fibrous: two skull plates joined by a serrated line
    s += '<path d="M24,80 L136,80 L136,200 L24,200 Z" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M80,80 l8,10 l-10,10 l10,10 l-10,10 l10,10 l-10,10 l10,10 l-10,10 l10,10 l-10,10 l8,10 l-6,10" stroke="#8b7a62" stroke-width="3" fill="none"/>';
    // cartilaginous: two vertebral bodies with a cartilage disc between them
    s += '<rect x="196" y="70" width="88" height="54" rx="10" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<rect x="198" y="128" width="84" height="22" rx="10" fill="#b9e3ff" stroke="#8cc6ef" stroke-width="2"/>';
    s += '<rect x="196" y="154" width="88" height="54" rx="10" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    // synovial: two bone ends with smooth cartilage, fluid and a capsule
    s += '<path d="M346,60 L454,60 L454,200 L346,200 Z" fill="#cfe8ff" opacity="0.6"/>';
    s += '<path d="M346,60 C346,60 454,60 454,60" stroke="#7aa8f0"/>';
    s += '<path d="M372,40 L428,40 L428,110 C440,116 440,130 424,134 C410,138 390,138 376,134 C360,130 360,116 372,110 Z" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M374,134 C390,140 410,140 426,134 L426,138 C410,144 390,144 374,138 Z" fill="#b9e3ff"/>';
    s += '<path d="M372,230 L428,230 L428,160 C440,154 440,144 424,146 C410,144 390,144 376,146 C360,144 360,154 372,160 Z" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="2"/>';
    s += '<path d="M348,104 C340,130 340,154 348,176 M452,104 C460,130 460,154 452,176" stroke="#7aa8f0" stroke-width="3" fill="none"/>';
    panels.forEach(function (p) {
      s += '<text x="' + p.x + '" y="240" text-anchor="middle" font-family="' + FONT + '" font-size="18" font-weight="800" fill="' + INK + '">' + p.title + '</text>';
      s += '<text x="' + p.x + '" y="262" text-anchor="middle" font-family="' + FONT + '" font-size="12.5" font-weight="600" fill="#56617c">' + p.where + '</text>';
    });
    if (o.labels) {
      s += label(84, 140, 80, 46, 'معظمها لا يتحرك', '#8b7a62');
      s += label(240, 139, 240, 46, 'حركة محدودة جدًا', '#5fa8dc');
      s += label(400, 140, 400, 290, 'سائل زلالي + غضروف أملس', '#5b8fd8');
    }
    return s + '</svg>';
  };

  /* ---------- 10. Where cartilage is (ear, nose, windpipe) ---------- opts: labels */
  V.cartilage = function (o) {
    var s = open('أماكن الغضاريف');
    var skin = '#e2ae84';
    // a man's head and neck from the side
    s += '<path d="M206,36 C262,22 314,40 326,92 C328,104 330,112 334,120 C340,130 352,142 352,150 C352,156 344,158 338,158 C340,164 340,170 336,174 C340,178 340,184 334,188 C338,194 336,204 328,208 C320,212 310,212 304,214 C300,232 298,250 300,280 L190,280 C192,250 186,226 170,208 C150,186 146,150 150,116 C154,76 170,48 206,36 Z" fill="' + skin + '" opacity="' + (o.labels ? 0.45 : 1) + '"/>';
    if (!o.labels) s += '<path d="M314,112 Q322,108 328,112" stroke="#2a1d16" stroke-width="3" fill="none"/><path d="M316,124 q6,-4 12,0" stroke="#3b2a1f" stroke-width="2" fill="none"/><path d="M332,180 q-6,2 -10,0" stroke="#a06a49" stroke-width="2" fill="none"/>';
    s += '<path d="M200,40 C230,30 280,30 300,48 C270,46 230,54 210,70 C196,62 194,50 200,40 Z" fill="#2a1d16"/>';
    // the ear, the nose and the windpipe in blue (cartilage)
    s += '<path d="M206,110 C192,102 182,116 186,134 C190,152 202,160 212,150 C206,142 204,124 206,110 Z" fill="' + (o.labels ? '#8cc6ef' : '#c48b62') + '"/>';
    s += '<path d="M330,100 C336,118 346,134 350,146 C346,152 340,154 336,152 Z" fill="' + (o.labels ? '#8cc6ef' : '#c48b62') + '"/>';
    if (o.labels) for (var r = 0; r < 6; r++) s += '<rect x="262" y="' + (214 + r * 11) + '" width="30" height="7" rx="3" fill="#8cc6ef"/>';
    if (o.labels) {
      s += label(196, 132, 90, 120, 'الأذن الخارجية', '#5fa8dc');
      s += label(342, 132, 420, 100, 'الأنف', '#5fa8dc');
      s += label(276, 240, 400, 240, 'جدار القصبة الهوائية', '#5fa8dc');
      s += caption('مفيهوش أوعية دموية: غذاؤه بالانتشار من خلايا العظام');
    }
    return s + '</svg>';
  };

  /* ---------- 11. Inside a skeletal muscle (big → small) ---------- opts: labels */
  V.musclezoom = function (o) {
    var s = open('تركيب العضلة الهيكلية من الكبير للصغير');
    // muscle
    s += '<path d="M20,160 C40,110 90,100 110,160 C90,220 40,210 20,160 Z" fill="#c9574b"/><path d="M20,160 L6,160 M110,160 L124,160" stroke="#efe6d2" stroke-width="7" stroke-linecap="round"/>';
    // bundle
    s += '<rect x="150" y="120" width="70" height="80" rx="34" fill="#e07a6a" stroke="#b5483c" stroke-width="2"/>';
    for (var i = 0; i < 9; i++) s += '<circle cx="' + (165 + (i % 3) * 20) + '" cy="' + (138 + Math.floor(i / 3) * 22) + '" r="8" fill="#d0574b" stroke="#a63f35" stroke-width="1.2"/>';
    // fiber (cell) with stripes and many nuclei
    s += '<rect x="246" y="138" width="90" height="44" rx="20" fill="#e8958a" stroke="#b5483c" stroke-width="2"/>';
    for (var j = 0; j < 12; j++) s += '<path d="M' + (254 + j * 7) + ',142 L' + (254 + j * 7) + ',178" stroke="#b5483c" stroke-width="1.6" opacity="0.6"/>';
    s += '<ellipse cx="266" cy="146" rx="5" ry="3" fill="#5b2a7a"/><ellipse cx="302" cy="176" rx="5" ry="3" fill="#5b2a7a"/><ellipse cx="326" cy="146" rx="5" ry="3" fill="#5b2a7a"/>';
    // myofibril with light and dark bands
    for (var k = 0; k < 6; k++) {
      s += '<rect x="' + (362 + k * 18) + '" y="146" width="9" height="28" fill="#7c3b33"/><rect x="' + (371 + k * 18) + '" y="146" width="9" height="28" fill="#f2c4bd"/>';
    }
    s += '<rect x="362" y="146" width="108" height="28" rx="8" fill="none" stroke="#7c3b33" stroke-width="2"/>';
    [124, 232, 342].forEach(function (x) { s += '<path d="M' + (x + 4) + ',160 L' + (x + 16) + ',160 M' + (x + 10) + ',154 L' + (x + 16) + ',160 L' + (x + 10) + ',166" stroke="#56617c" stroke-width="2.4" fill="none"/>'; });
    if (o.labels) {
      s += label(64, 160, 64, 60, 'عضلة', '#b5483c');
      s += label(185, 120, 185, 60, 'حزمة (حواليها غشاء الحزمة)', '#b5483c');
      s += label(290, 182, 200, 220, 'ليفة = خلية فيها أنوية كتير', '#b5483c');
      s += label(416, 174, 400, 264, 'لييفة (1000–2000 في الليفة)', '#7c3b33');
      s += label(416, 146, 400, 60, 'أكتين (رفيع) + ميوسين (غليظ)', '#7c3b33');
      s += caption('الساركوليما: غشاء الليفة • الساركوبلازم: جوه الليفة');
    }
    return s + '</svg>';
  };

  /* ---------- 12. Sarcomeres: bands and filaments ----------
     opts: contracted, count (sarcomeres shown, default 2), labels */
  V.sarcomere = function (o) {
    var n = o.count || 2;
    var s = open(o.contracted ? 'قطع عضلية منقبضة' : 'قطع عضلية في الراحة');
    var x0 = 30, W = 420;
    var unit = W / n;
    var band = o.contracted ? 0.62 : 0.56;   // the dark band keeps its length
    var squeeze = o.contracted ? 0.78 : 1;
    var u = unit * squeeze;
    var start = 240 - (u * n) / 2;
    // the microscope look (top)
    s += '<rect x="' + start + '" y="40" width="' + u * n + '" height="54" fill="#f6dcd7" stroke="#b5483c" stroke-width="1.5"/>';
    for (var i = 0; i < n; i++) {
      var sx = start + i * u;
      var aw = unit * band * (o.contracted ? 0.9 : 1);
      var ax = sx + (u - aw) / 2;
      var hw = o.contracted ? aw * 0.12 : aw * 0.3;
      s += '<rect x="' + ax + '" y="40" width="' + aw + '" height="54" fill="#8a3d33"/>';
      s += '<rect x="' + (ax + (aw - hw) / 2) + '" y="40" width="' + hw + '" height="54" fill="#c4766b"/>';
    }
    for (var z = 0; z <= n; z++) s += '<path d="M' + (start + z * u) + ',36 L' + (start + z * u) + ',98" stroke="#3b1a16" stroke-width="3.5"/>';
    // the filaments (bottom)
    for (var j = 0; j < n; j++) {
      var bx = start + j * u;
      [150, 172, 194].forEach(function (y) {
        var aw2 = unit * band * (o.contracted ? 0.9 : 1);
        var mx = bx + (u - aw2) / 2;
        s += '<path d="M' + (mx + 4) + ',' + (y + 11) + ' L' + (mx + aw2 - 4) + ',' + (y + 11) + '" stroke="#5a2a8a" stroke-width="6" stroke-linecap="round"/>';
        for (var h = 0; h < 6; h++) s += '<path d="M' + (mx + 10 + h * (aw2 - 20) / 5) + ',' + (y + 11) + ' l4,-5" stroke="#5a2a8a" stroke-width="2"/>';
      });
      [140, 162, 184, 206].forEach(function (y) {
        var len = u * (o.contracted ? 0.42 : 0.34);
        s += '<path d="M' + bx + ',' + y + ' L' + (bx + len) + ',' + y + ' M' + (bx + u) + ',' + y + ' L' + (bx + u - len) + ',' + y + '" stroke="#e07a6a" stroke-width="3"/>';
      });
    }
    for (var z2 = 0; z2 <= n; z2++) s += '<path d="M' + (start + z2 * u) + ',130 L' + (start + z2 * u) + ',216" stroke="#3b1a16" stroke-width="3.5"/>';
    if (o.labels) {
      var sx0 = start, aw0 = unit * band * (o.contracted ? 0.9 : 1), ax0 = sx0 + (u - aw0) / 2;
      s += label(sx0 + 2, 50, 40, 118, 'خط Z', '#3b1a16');
      s += label(sx0 + (ax0 - sx0) / 2 + 2, 60, sx0 + 40, 18, 'I مضيئة (أكتين)', '#e07a6a');
      s += label(ax0 + 6, 60, ax0 + 150, 18, 'A داكنة', '#8a3d33');
      s += label(ax0 + aw0 / 2, 80, ax0 + aw0 / 2 + 150, 116, 'H شبه مضيئة (ميوسين)', '#c4766b');
      s += label(sx0 + 30, 140, 90, 250, 'أكتين (رفيع)', '#e07a6a');
      s += label(ax0 + aw0 / 2, 161, 260, 250, 'ميوسين (غليظ) + روابط مستعرضة', '#5a2a8a');
      s += '<path d="M' + start + ',230 L' + (start + u) + ',230" stroke="#2f63b0" stroke-width="2"/><path d="M' + start + ',224 L' + start + ',236 M' + (start + u) + ',224 L' + (start + u) + ',236" stroke="#2f63b0" stroke-width="2"/>';
      s += '<text x="' + (start + u / 2) + '" y="292" text-anchor="middle" font-family="' + FONT + '" font-size="13" font-weight="700" fill="#2f63b0" direction="rtl">القطعة العضلية: من خط Z لخط Z</text>';
    }
    s += caption(o.contracted ? 'منقبضة: خطوط Z قربت، والخيوط نفسها طولها ما اتغيرش' : (o.labels ? '' : 'لييفة عضلية تحت المجهر'));
    return s + '</svg>';
  };

  /* ---------- 13. The nerve–muscle junction ----------
     opts: stage: 'rest' | 'active' | 'enzyme', labels */
  V.nmj = function (o) {
    var active = o.stage === 'active';
    var s = open('الاتصال العصبي العضلي');
    // the motor neuron's end
    s += '<path d="M200,0 L280,0 L276,70 C320,80 330,120 300,140 L180,140 C150,120 160,80 204,70 Z" fill="#ffe2a8" stroke="#d9a441" stroke-width="2.5"/>';
    for (var i = 0; i < 9; i++) {
      var vx = 196 + (i % 5) * 22, vy = 92 + Math.floor(i / 5) * 24;
      s += '<circle cx="' + vx + '" cy="' + vy + '" r="9" fill="#fff6dd" stroke="#d9a441" stroke-width="1.6"/>';
      s += '<circle cx="' + (vx - 3) + '" cy="' + (vy - 2) + '" r="1.8" fill="#7a5bd6"/><circle cx="' + (vx + 3) + '" cy="' + (vy + 2) + '" r="1.8" fill="#7a5bd6"/>';
    }
    // the muscle fibre and its membrane charges
    s += '<rect x="20" y="170" width="440" height="140" rx="10" fill="#f2c4bd" stroke="#b5483c" stroke-width="2.5"/>';
    for (var k = 0; k < 14; k++) s += '<path d="M' + (40 + k * 30) + ',190 L' + (40 + k * 30) + ',300" stroke="#b5483c" stroke-width="2" opacity="0.25"/>';
    var out = active ? '−' : '+', inn = active ? '+' : '−';
    for (var c = 0; c < 8; c++) {
      s += '<text x="' + (40 + c * 56) + '" y="164" font-size="18" font-weight="800" fill="' + (active ? '#2f63b0' : '#d84a3a') + '" font-family="' + FONT + '">' + out + '</text>';
      s += '<text x="' + (40 + c * 56) + '" y="196" font-size="18" font-weight="800" fill="' + (active ? '#d84a3a' : '#2f63b0') + '" font-family="' + FONT + '">' + inn + '</text>';
    }
    if (active || o.stage === 'enzyme') {
      for (var d = 0; d < 10; d++) s += '<circle cx="' + (200 + d * 9) + '" cy="' + (150 + (d % 3) * 5) + '" r="2.4" fill="#7a5bd6"/>';
      s += '<text x="330" y="120" font-size="15" font-weight="800" fill="#2a9d8f" font-family="' + FONT + '">Ca²⁺</text>';
    }
    if (active) for (var n2 = 0; n2 < 4; n2++) s += '<path d="M' + (120 + n2 * 70) + ',150 L' + (120 + n2 * 70) + ',200 M' + (114 + n2 * 70) + ',192 L' + (120 + n2 * 70) + ',200 L' + (126 + n2 * 70) + ',192" stroke="#e76f51" stroke-width="2.5" fill="none"/><text x="' + (128 + n2 * 70) + '" y="182" font-size="13" font-weight="800" fill="#e76f51">Na⁺</text>';
    if (o.stage === 'enzyme') s += '<g transform="translate(250,152)"><circle r="12" fill="#2a9d8f"/><path d="M-6,-6 L6,6 M6,-6 L-6,6" stroke="#fff" stroke-width="3"/></g>';
    if (o.labels) {
      s += label(240, 40, 380, 30, 'نهاية العصبون الحركي', '#d9a441');
      s += label(218, 94, 90, 60, 'حويصلات فيها أسيتيل كولين', '#7a5bd6');
      s += label(240, 155, 90, 120, 'فراغ التشابك العصبي العضلي', '#56617c');
      s += label(380, 240, 380, 290, active ? 'لااستقطاب: جوه موجب وبرّه سالب' : 'راحة: برّه موجب وجوه سالب', '#b5483c');
      if (o.stage === 'enzyme') s += label(250, 152, 400, 100, 'كولين استيريز يحطّم الأسيتيل كولين', '#2a9d8f');
    }
    return s + '</svg>';
  };

  /* ---------- 14. Three kinds of muscle under the microscope ---------- opts: labels, highlight */
  V.muscletypes = function (o) {
    var s = open('أنواع العضلات تحت المجهر');
    var c = [{ x: 85, t: 'هيكلية', d: 'مخططة • إرادية' }, { x: 240, t: 'قلبية', d: 'مخططة • لا إرادية' }, { x: 395, t: 'ملساء', d: 'غير مخططة • لا إرادية' }];
    c.forEach(function (m, i) {
      var cl = A.id('mt');
      var on = o.highlight === i;
      s += '<clipPath id="' + cl + '"><circle cx="' + m.x + '" cy="130" r="70"/></clipPath>';
      s += '<circle cx="' + m.x + '" cy="130" r="74" fill="#fff" stroke="' + (on ? '#ffd25c' : '#c7d3e6') + '" stroke-width="' + (on ? 6 : 4) + '"/>';
      s += '<g clip-path="url(#' + cl + ')"><rect x="' + (m.x - 74) + '" y="56" width="148" height="148" fill="#fbe5e1"/>';
      if (i === 0) {
        for (var f = 0; f < 4; f++) {
          s += '<rect x="' + (m.x - 74) + '" y="' + (70 + f * 32) + '" width="148" height="26" fill="#e9a79d"/>';
          for (var st = 0; st < 22; st++) s += '<path d="M' + (m.x - 72 + st * 7) + ',' + (70 + f * 32) + ' l0,26" stroke="#b5483c" stroke-width="1.6" opacity="0.7"/>';
          s += '<ellipse cx="' + (m.x - 30 + f * 15) + '" cy="' + (72 + f * 32) + '" rx="7" ry="3" fill="#5b2a7a"/>';
        }
      } else if (i === 1) {
        s += '<path d="M' + (m.x - 74) + ',90 L' + (m.x - 10) + ',96 L' + (m.x + 20) + ',80 L' + (m.x + 74) + ',86 L' + (m.x + 74) + ',112 L' + (m.x + 24) + ',106 L' + (m.x - 6) + ',122 L' + (m.x - 74) + ',116 Z M' + (m.x - 74) + ',140 L' + (m.x + 10) + ',146 L' + (m.x + 40) + ',132 L' + (m.x + 74) + ',138 L' + (m.x + 74) + ',166 L' + (m.x + 40) + ',160 L' + (m.x + 6) + ',172 L' + (m.x - 74) + ',168 Z" fill="#e9a79d"/>';
        for (var st2 = 0; st2 < 22; st2++) s += '<path d="M' + (m.x - 72 + st2 * 7) + ',80 l0,96" stroke="#b5483c" stroke-width="1.4" opacity="0.55"/>';
        s += '<path d="M' + (m.x - 30) + ',90 l0,28 M' + (m.x + 34) + ',134 l0,30" stroke="#5b2a7a" stroke-width="3"/>';
        s += '<ellipse cx="' + (m.x - 50) + '" cy="104" rx="7" ry="4" fill="#5b2a7a"/><ellipse cx="' + (m.x + 10) + '" cy="154" rx="7" ry="4" fill="#5b2a7a"/>';
      } else {
        for (var sm = 0; sm < 7; sm++) {
          var yy = 74 + sm * 18, xx = m.x - 60 + (sm % 2) * 26;
          s += '<path d="M' + xx + ',' + yy + ' C' + (xx + 30) + ',' + (yy - 9) + ' ' + (xx + 70) + ',' + (yy - 9) + ' ' + (xx + 100) + ',' + yy + ' C' + (xx + 70) + ',' + (yy + 9) + ' ' + (xx + 30) + ',' + (yy + 9) + ' ' + xx + ',' + yy + ' Z" fill="#e9a79d" stroke="#c4766b" stroke-width="1.2"/>';
          s += '<ellipse cx="' + (xx + 50) + '" cy="' + yy + '" rx="8" ry="3" fill="#5b2a7a"/>';
        }
      }
      s += '</g>';
      s += '<text x="' + m.x + '" y="234" text-anchor="middle" font-family="' + FONT + '" font-size="18" font-weight="800" fill="' + INK + '">' + m.t + '</text>';
      if (o.labels) s += '<text x="' + m.x + '" y="258" text-anchor="middle" font-family="' + FONT + '" font-size="13" font-weight="700" fill="#56617c">' + m.d + '</text>';
    });
    if (o.labels) s += caption('الملساء في جدر الأوعية الدموية، والقلبية في القلب');
    return s + '</svg>';
  };

  /* ---------- 15. Three systems work together for movement ---------- opts: labels, off: 'nerve' */
  V.systems = function (o) {
    var g = boneGrad();
    var f = 'url(#' + g.id + ')';
    var mu = A.id('mus');
    var off = o.off === 'nerve';
    var s = open('حركة الدراع: عظم وعضلة وعصب');
    s += '<defs>' + g.def + '<linearGradient id="' + mu + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d8695b"/><stop offset="1" stop-color="#a8392f"/></linearGradient></defs>';
    // the spine with the spinal cord, where the motor neurons come from
    for (var v = 0; v < 10; v++) {
      var y = 14 + v * 27;
      s += '<rect x="24" y="' + y + '" width="32" height="21" rx="6" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="1.4"/>';
      s += '<path d="M56,' + (y + 3) + ' L82,' + (y + 3) + ' L82,' + (y + 18) + ' L56,' + (y + 18) + '" fill="none" stroke="' + BONE[2] + '" stroke-width="2"/>';
    }
    s += '<rect x="63" y="8" width="10" height="272" rx="5" fill="#ffd166" stroke="#e0a100" stroke-width="1"/>';
    // the arm: skin, bones, biceps and its tendons
    s += '<path d="M112,64 C160,44 240,58 302,102 C330,92 352,66 370,38 C378,26 396,18 414,22 C432,26 440,44 432,60 C424,74 412,80 404,84 C380,120 356,160 330,182 C306,196 270,180 220,160 C178,144 140,136 112,132 Z" fill="#f2cfb3" opacity="0.5" stroke="#d9a882" stroke-width="2"/>';
    s += '<path d="M106,78 C128,70 150,84 150,104 C150,124 126,134 108,126 Z" fill="' + f + '" stroke="' + BONE[2] + '" stroke-width="1.4"/>';
    s += bone(146, 104, 306, 154, 17, f);
    s += bone(314, 150, 398, 58, 10, f) + bone(322, 160, 410, 70, 8, f);
    s += '<circle cx="412" cy="46" r="20" fill="#e9bd98" stroke="#d9a882" stroke-width="2"/>';
    var belly = off ? 'M170,100 C214,84 270,94 300,118 C288,124 248,120 170,112 Z' : 'M168,98 C204,50 272,62 302,118 C290,126 248,120 168,112 Z';
    s += '<path d="' + belly + '" fill="url(#' + mu + ')" stroke="#8f2f27" stroke-width="1.5"/>';
    for (var st = 0; st < 6; st++) s += '<path d="M' + (186 + st * 18) + ',' + (off ? 98 : 80 + Math.abs(st - 2.5) * 5) + ' C' + (196 + st * 18) + ',100 ' + (200 + st * 18) + ',108 ' + (206 + st * 18) + ',114" stroke="#f3a99d" stroke-width="1.3" fill="none" opacity="0.7"/>';
    s += '<path d="M168,105 L148,98 M300,118 L324,134" stroke="#f2ead8" stroke-width="5" stroke-linecap="round"/>';
    // the motor nerve: from the spinal cord to the muscle
    var nerve = off ? '#b9c0cc' : '#f2b705';
    s += '<path d="M73,120 C110,118 130,128 160,120 C190,112 206,102 222,96" stroke="' + nerve + '" stroke-width="4" fill="none" stroke-linecap="round"' + (off ? ' stroke-dasharray="7 6"' : '') + '/>';
    [[234, 84], [240, 98], [232, 110]].forEach(function (e) {
      s += '<path d="M222,96 L' + e[0] + ',' + e[1] + '" stroke="' + nerve + '" stroke-width="2.4"/><circle cx="' + e[0] + '" cy="' + e[1] + '" r="3.6" fill="' + nerve + '"/>';
    });
    if (off) s += '<path d="M106,108 l18,18 m0,-18 l-18,18" stroke="#e05d5d" stroke-width="4.5" stroke-linecap="round"/>';
    else s += '<path d="M140,124 l10,-3 m-4,-4 l4,4 l-4,4" stroke="#e0a100" stroke-width="2" fill="none"/>';
    if (o.labels) {
      s += label(73, 200, 200, 256, 'الجهاز العصبي: بيدّي الأوامر (سيالات)', '#e0a100');
      s += label(236, 76, 250, 22, 'الجهاز العضلي: مسئول عن الحركة', '#c9574b');
      s += label(262, 140, 360, 220, 'الجهاز الهيكلي: مكان اتصال ودعامة', '#b9a37c');
      s += caption(off ? 'العصب الحركي اتقطع ← مفيش سيال ← العضلة ما تنقبضش' : 'السيال في العصب الحركي ← العضلة تنقبض ← العظمة تتحرك');
    }
    return s + '</svg>';
  };

  /* ---------- 16. The whole skeleton ---------- opts: highlight: 'axial' | 'appendicular', labels */
  V.skeleton = function (o) {
    var g = boneGrad();
    var f = 'url(#' + g.id + ')';
    var ax = o.highlight === 'axial' || o.labels ? '#cdbcff' : f;
    var ap = o.highlight === 'appendicular' || o.labels ? '#ffc9a8' : f;
    var s = open('الهيكل العظمي');
    s += '<defs>' + g.def + '</defs>';
    var cx = 240;
    // axial: skull, spine, rib cage
    s += '<ellipse cx="' + cx + '" cy="34" rx="22" ry="26" fill="' + ax + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>';
    s += '<path d="M' + (cx - 12) + ',54 L' + (cx + 12) + ',54 L' + (cx + 8) + ',66 L' + (cx - 8) + ',66 Z" fill="' + ax + '"/>';
    for (var v = 0; v < 16; v++) s += '<rect x="' + (cx - 5) + '" y="' + (66 + v * 9) + '" width="10" height="7" rx="2" fill="' + ax + '" stroke="' + BONE[2] + '" stroke-width="0.8"/>';
    for (var r = 0; r < 8; r++) s += '<path d="M' + (cx - 4) + ',' + (84 + r * 8) + ' C' + (cx - 46) + ',' + (80 + r * 8) + ' ' + (cx - 44) + ',' + (100 + r * 8) + ' ' + (cx - 8) + ',' + (104 + r * 8) + ' M' + (cx + 4) + ',' + (84 + r * 8) + ' C' + (cx + 46) + ',' + (80 + r * 8) + ' ' + (cx + 44) + ',' + (100 + r * 8) + ' ' + (cx + 8) + ',' + (104 + r * 8) + '" stroke="' + (ax === f ? BONE[2] : '#a48fe0') + '" stroke-width="3" fill="none"/>';
    // appendicular: girdles and limbs
    s += '<path d="M' + (cx - 46) + ',78 L' + (cx - 6) + ',74 M' + (cx + 46) + ',78 L' + (cx + 6) + ',74" stroke="' + (ap === f ? BONE[2] : '#f2a07b') + '" stroke-width="6" stroke-linecap="round"/>';
    s += bone(cx - 46, 80, cx - 62, 160, 10, ap) + bone(cx + 46, 80, cx + 62, 160, 10, ap);
    s += bone(cx - 62, 162, cx - 72, 226, 8, ap) + bone(cx + 62, 162, cx + 72, 226, 8, ap);
    s += '<path d="M' + (cx - 34) + ',214 C' + (cx - 40) + ',196 ' + (cx - 20) + ',194 ' + cx + ',204 C' + (cx + 20) + ',194 ' + (cx + 40) + ',196 ' + (cx + 34) + ',214 C' + (cx + 24) + ',228 ' + (cx - 24) + ',228 ' + (cx - 34) + ',214 Z" fill="' + ap + '" stroke="' + BONE[2] + '" stroke-width="1.5"/>';
    s += bone(cx - 20, 226, cx - 26, 268, 11, ap) + bone(cx + 20, 226, cx + 26, 268, 11, ap);
    s += bone(cx - 26, 270, cx - 28, 306, 9, ap) + bone(cx + 26, 270, cx + 28, 306, 9, ap);
    s += '<ellipse cx="' + (cx - 74) + '" cy="236" rx="7" ry="10" fill="' + ap + '"/><ellipse cx="' + (cx + 74) + '" cy="236" rx="7" ry="10" fill="' + ap + '"/>';
    s += '<ellipse cx="' + (cx - 32) + '" cy="312" rx="12" ry="5" fill="' + ap + '"/><ellipse cx="' + (cx + 32) + '" cy="312" rx="12" ry="5" fill="' + ap + '"/>';
    if (o.labels) {
      s += label(cx, 40, 90, 40, 'الهيكل المحوري: الجمجمة', '#8b6fd6');
      s += label(cx, 140, 90, 130, 'العمود الفقري (المحور)', '#8b6fd6');
      s += label(cx - 30, 100, 90, 86, 'القفص الصدري', '#8b6fd6');
      s += label(cx + 46, 78, 390, 60, 'الحزام الصدري', '#e07a4f');
      s += label(cx + 62, 140, 390, 140, 'الطرفان العلويان', '#e07a4f');
      s += label(cx + 30, 210, 390, 210, 'الحزام الحوضي', '#e07a4f');
      s += label(cx + 26, 280, 390, 280, 'الطرفان السفليان', '#e07a4f');
    }
    return s + '</svg>';
  };

  /* ---------- 17. Peristalsis: a local movement in the gut ---------- opts: labels */
  V.gut = function (o) {
    var s = open('الحركة الدودية في الأمعاء');
    s += '<path d="M20,140 C80,120 120,160 180,140 C220,126 240,104 270,110 C300,116 320,150 360,150 C400,150 430,130 460,140 L460,200 C430,190 400,210 360,210 C320,210 300,176 270,170 C240,164 220,186 180,200 C120,220 80,180 20,200 Z" fill="#f4b6a6" stroke="#c4766b" stroke-width="2.5"/>';
    s += '<ellipse cx="300" cy="160" rx="16" ry="12" fill="#a77b4f"/>';
    s += '<path d="M240,96 L250,120 M240,214 L250,186" stroke="#c4766b" stroke-width="5" stroke-linecap="round"/>';
    s += '<path d="M330,240 L420,240 M410,232 L420,240 L410,248" stroke="#2f63b0" stroke-width="3" fill="none"/>';
    if (o.labels) {
      s += label(246, 110, 160, 60, 'انقباض بيمشي على طول الأمعاء', '#c4766b');
      s += label(300, 160, 380, 70, 'الطعام بيتدفع لقدام', '#a77b4f');
      s += caption('حركة موضعية: لجزء من الكائن الحي بس');
    }
    return s + '</svg>';
  };
})();
