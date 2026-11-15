/* ==========================================================================
   «الدكتور والمزارع» — the drawings (inline SVG, made in code: no images).

   G12.BioArt.scene({ bg, who, mood })      a person talking (upper body only)
   G12.BioArt.view(name, options)           a close-up (the camera moves to
                                            the part: a foot, a knee, an X-ray,
                                            a plant, a microscope slide …)
   G12.BioArt.CAST                          the people of the game (all men)

   Every drawing is an SVG string made only from this file's own data.
   ========================================================================== */
(function () {
  'use strict';

  var G12 = window.G12 = window.G12 || {};
  var uid = 0;
  function id(name) { uid += 1; return name + uid; }

  /* ---------- People ---------- */

  var SKIN = {
    light: ['#f1c7a3', '#d9a27d', '#b97e5c'],
    tan: ['#e2ae84', '#c58a63', '#a06a49'],
    brown: ['#c48b62', '#a46c48', '#7f5035'],
    dark: ['#9c6844', '#7d5134', '#5c3a25']
  };

  /* The cast. hair: short | side | curly | receding | buzz | none
     beard: none | stubble | moustache | short | full; headwear: cap | turban */
  var CAST = {
    karim: { name: 'كريم', role: 'لاعب كورة', age: 'young', skin: 'tan', hair: 'side', hairColor: '#2a1d16', beard: 'stubble', clothes: 'jersey', color: '#d84a3a', color2: '#ffffff', number: '10' },
    saber: { name: 'عم صابر', role: 'موظف على المعاش', age: 'old', skin: 'light', hair: 'receding', hairColor: '#b9b4ad', beard: 'moustache', beardColor: '#cfcac3', clothes: 'vest', color: '#7b8aa0', color2: '#eef1f5', glasses: true },
    youssef: { name: 'يوسف', role: 'عدّاء', age: 'young', skin: 'brown', hair: 'curly', hairColor: '#1d1410', beard: 'none', clothes: 'track', color: '#2f6fd1', color2: '#ffffff' },
    omar: { name: 'عمر', role: 'لاعب جمباز', age: 'young', skin: 'light', hair: 'short', hairColor: '#3a2618', beard: 'none', clothes: 'tshirt', color: '#2a9d8f', color2: '#ffffff' },
    sayed: { name: 'الأسطى سيد', role: 'عامل بناء', age: 'middle', skin: 'dark', hair: 'buzz', hairColor: '#1a1310', beard: 'short', beardColor: '#2b211b', clothes: 'work', color: '#c9a86a', color2: '#8a6d3b' },
    tamer: { name: 'كابتن تامر', role: 'مدرب جيم', age: 'middle', skin: 'tan', hair: 'buzz', hairColor: '#21170f', beard: 'short', beardColor: '#2a1f18', clothes: 'tshirt', color: '#333a48', color2: '#f2c14e' },
    ziad: { name: 'زياد', role: 'طالب في تالتة ثانوي', age: 'teen', skin: 'light', hair: 'short', hairColor: '#2d2019', beard: 'none', clothes: 'school', color: '#9fc5e8', color2: '#3d5a80' },
    adam: { name: 'آدم', role: 'تلميذ عنده 10 سنين', age: 'child', skin: 'tan', hair: 'short', hairColor: '#231811', beard: 'none', clothes: 'tshirt', color: '#f4a261', color2: '#ffffff' },
    abdelrahman: { name: 'الحاج عبد الرحمن', role: 'مزارع', age: 'old', skin: 'brown', hair: 'none', hairColor: '#d9d6d0', beard: 'full', beardColor: '#e4e1db', clothes: 'galabeya', color: '#7d8f7a', color2: '#5f6f5c', headwear: 'turban' },
    hassan: { name: 'حسن', role: 'مهندس زراعي', age: 'young', skin: 'tan', hair: 'side', hairColor: '#24180f', beard: 'short', beardColor: '#2b1d14', clothes: 'shirt', color: '#5b8c51', color2: '#e9f5e6', headwear: 'cap' },
    ramadan: { name: 'عم رمضان', role: 'صاحب مشتل', age: 'middle', skin: 'dark', hair: 'none', hairColor: '#2a2420', beard: 'moustache', beardColor: '#2c2520', clothes: 'galabeya', color: '#a68a64', color2: '#7d6748', headwear: 'cap' },
    mahmoud: { name: 'د. محمود', role: 'دكتور التحاليل', age: 'middle', skin: 'light', hair: 'side', hairColor: '#3b2c22', beard: 'short', beardColor: '#3a2b21', clothes: 'labcoat', color: '#ffffff', color2: '#6c8ebf', glasses: true },
    murad: { name: 'د. مراد', role: 'رئيس القسم', age: 'old', skin: 'tan', hair: 'receding', hairColor: '#8f8a84', beard: 'short', beardColor: '#a39e98', clothes: 'labcoat', color: '#ffffff', color2: '#8a5a44', glasses: true }
  };

  function shade(hex, amount) {
    var n = parseInt(hex.slice(1), 16);
    var r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    var f = function (c) { return Math.max(0, Math.min(255, Math.round(amount < 0 ? c * (1 + amount) : c + (255 - c) * amount))); };
    return '#' + ((1 << 24) + (f(r) << 16) + (f(g) << 8) + f(b)).toString(16).slice(1);
  }

  /* A head-and-shoulders portrait, drawn around (0,0) = middle of the face. */
  function person(p, mood) {
    mood = mood || 'neutral';
    var skin = SKIN[p.skin] || SKIN.tan;
    var g = { face: id('face'), neck: id('neck'), hair: id('hair'), cloth: id('cloth'), shadow: id('shd') };
    var child = p.age === 'child';
    var old = p.age === 'old';
    var s = [];

    s.push('<defs>' +
      '<radialGradient id="' + g.face + '" cx="42%" cy="34%" r="70%"><stop offset="0" stop-color="' + shade(skin[0], 0.12) + '"/><stop offset="0.55" stop-color="' + skin[0] + '"/><stop offset="1" stop-color="' + skin[1] + '"/></radialGradient>' +
      '<linearGradient id="' + g.neck + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="' + skin[2] + '"/><stop offset="0.45" stop-color="' + skin[1] + '"/><stop offset="1" stop-color="' + skin[0] + '"/></linearGradient>' +
      '<linearGradient id="' + g.hair + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="' + shade(p.hairColor, 0.25) + '"/><stop offset="1" stop-color="' + p.hairColor + '"/></linearGradient>' +
      '<linearGradient id="' + g.cloth + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="' + shade(p.color, 0.18) + '"/><stop offset="0.6" stop-color="' + p.color + '"/><stop offset="1" stop-color="' + shade(p.color, -0.2) + '"/></linearGradient>' +
      '<radialGradient id="' + g.shadow + '" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000" stop-opacity="0.22"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>' +
      '</defs>');

    var k = child ? 0.86 : 1;           // a child's head on a smaller body
    var wide = p.age === 'middle' || old ? 1.04 : 1;

    // shoulders and clothes
    s.push('<g transform="translate(0,' + (child ? 6 : 0) + ') scale(' + (child ? 0.82 : 1) + ',1)">' + clothes(p, g) + '</g>');
    // neck
    s.push('<path d="M-29,38 C-29,62 -31,78 -35,96 L35,96 C31,78 29,62 29,38 Z" fill="url(#' + g.neck + ')"/>');
    s.push('<path d="M-12,70 C-8,82 -6,90 -8,96 M12,70 C8,82 6,90 8,96" stroke="' + skin[2] + '" stroke-width="1.4" fill="none" opacity="0.15"/>');
    s.push('<path d="M-30,92 C-18,98 18,98 30,92 L32,100 L-32,100 Z" fill="' + skin[2] + '" opacity="0.35"/>');
    s.push('<path d="M-24,50 C-12,62 12,62 24,50 L24,62 C12,72 -12,72 -24,62 Z" fill="' + skin[2] + '" opacity="0.5"/>');
    s.push(collar(p));

    s.push('<g transform="scale(' + (k * wide) + ',' + k + ')">');
    // ears
    [-1, 1].forEach(function (side) {
      s.push('<ellipse cx="' + (side * 53) + '" cy="0" rx="9.5" ry="16" fill="' + skin[1] + '"/>');
      s.push('<path d="M' + (side * 53) + ',-10 q' + (side * 6) + ',6 0,18" stroke="' + skin[2] + '" stroke-width="2.4" fill="none" stroke-linecap="round"/>');
    });
    // back hair (behind the face)
    s.push(hairBack(p, g));
    // face
    var jaw = old ? 39 : child ? 33 : 37;
    s.push('<path d="M0,-70 C33,-70 55,-50 55,-16 C56,10 50,30 ' + jaw + ',47 C27,59 14,65 0,65 C-14,65 -27,59 -' + jaw + ',47 C-50,30 -56,10 -55,-16 C-55,-50 -33,-70 0,-70 Z" fill="url(#' + g.face + ')"/>');
    // soft shadow down the side of the face and under the cheekbones
    s.push('<path d="M38,-34 C50,-8 48,22 30,46 C42,24 44,0 38,-34 Z" fill="' + skin[1] + '" opacity="0.6"/>');
    s.push('<path d="M-38,-34 C-50,-8 -48,22 -30,46 C-42,24 -44,0 -38,-34 Z" fill="' + skin[1] + '" opacity="0.4"/>');
    // under the cheekbones, the jaw line and the chin
    s.push('<path d="M26,8 C34,16 36,28 30,38 C32,28 30,18 26,8 Z M-26,8 C-34,16 -36,28 -30,38 C-32,28 -30,18 -26,8 Z" fill="' + skin[2] + '" opacity="' + (p.age === 'old' ? 0.3 : 0.14) + '"/>');
    s.push('<path d="M-36,48 C-26,60 -12,66 0,66 C12,66 26,60 36,48 C26,62 12,68 0,68 C-12,68 -26,62 -36,48 Z" fill="' + skin[2] + '" opacity="0.5"/>');
    s.push('<ellipse cx="0" cy="56" rx="9" ry="5" fill="#ffffff" opacity="0.13"/>');
    // forehead light and the eye sockets
    s.push('<ellipse cx="-6" cy="-44" rx="26" ry="13" fill="#ffffff" opacity="0.12"/>');
    s.push('<path d="M-36,-12 Q-20,-22 -6,-13 Q-20,-17 -36,-12 Z M36,-12 Q20,-22 6,-13 Q20,-17 36,-12 Z" fill="' + skin[2] + '" opacity="0.35"/>');
    s.push('<ellipse cx="-24" cy="16" rx="12" ry="7" fill="#e07a6a" opacity="' + (mood === 'happy' ? 0.22 : 0.1) + '"/>');
    s.push('<ellipse cx="24" cy="16" rx="12" ry="7" fill="#e07a6a" opacity="' + (mood === 'happy' ? 0.22 : 0.1) + '"/>');
    if (old) {
      s.push('<path d="M-26,-40 Q0,-45 26,-40 M-22,-33 Q0,-37 22,-33" stroke="' + skin[2] + '" stroke-width="1.3" fill="none" opacity="0.6"/>');
      s.push('<path d="M-17,18 Q-23,30 -19,40 M17,18 Q23,30 19,40" stroke="' + skin[2] + '" stroke-width="1.6" fill="none" opacity="0.55"/>');
    }
    s.push(beardPath(p, mood, skin));
    s.push(eyes(p, mood, skin));
    s.push(nose(skin));
    s.push(mouth(p, mood, skin));
    s.push(moustache(p));
    s.push(hairFront(p, g));
    if (p.glasses) s.push(glasses());
    s.push(headwear(p));
    s.push('</g>');
    return s.join('');
  }

  function eyes(p, mood, skin) {
    var s = [];
    var squint = mood === 'pain' ? 3.2 : mood === 'happy' ? 1.6 : 0;
    var browLift = mood === 'pain' || mood === 'worried' ? -5 : mood === 'surprised' ? -7 : 0;
    var bulge = p.eyes === 'bulging';
    [-1, 1].forEach(function (side) {
      var x = side * 20;
      var top = -17 + squint + (bulge ? -3 : 0);
      var bottom = 2.5 - squint * 0.5 + (bulge ? 2.5 : 0);
      var clip = id('eye');
      // the white of the eye, the iris and the eyelids
      s.push('<clipPath id="' + clip + '"><path d="M' + (x - 12.5) + ',-6 Q' + x + ',' + top + ' ' + (x + 12.5) + ',-6 Q' + x + ',' + bottom + ' ' + (x - 12.5) + ',-6 Z"/></clipPath>');
      s.push('<path d="M' + (x - 13.5) + ',-5 Q' + x + ',' + (top - 3) + ' ' + (x + 13.5) + ',-5" fill="' + skin[1] + '" opacity="0.5"/>');
      s.push('<path d="M' + (x - 12) + ',' + (top + 0.5) + ' Q' + x + ',' + (top - 5.5) + ' ' + (x + 12) + ',' + (top + 0.5) + '" stroke="' + skin[2] + '" stroke-width="1.2" fill="none" opacity="0.6"/>');
      s.push('<path d="M' + (x - 12.5) + ',-6 Q' + x + ',' + top + ' ' + (x + 12.5) + ',-6 Q' + x + ',' + bottom + ' ' + (x - 12.5) + ',-6 Z" fill="#fbf7f2"/>');
      s.push('<g clip-path="url(#' + clip + ')"><circle cx="' + x + '" cy="-6" r="' + (bulge ? 5.3 : 5.8) + '" fill="#5a3a22"/><circle cx="' + x + '" cy="-6" r="' + (bulge ? 5.3 : 5.8) + '" fill="none" stroke="#2e1d10" stroke-width="1"/>' +
        '<circle cx="' + x + '" cy="-6" r="2.6" fill="#120b06"/><circle cx="' + (x - 1.8) + '" cy="-8" r="1.3" fill="#ffffff"/></g>');
      s.push('<path d="M' + (x - 13) + ',-5.5 Q' + x + ',' + (top - 0.5) + ' ' + (x + 13) + ',-5.5" stroke="#2a1a10" stroke-width="2.2" fill="none" stroke-linecap="round"/>');
      s.push('<path d="M' + (x - 10) + ',-3 Q' + x + ',' + (bottom + 1.5) + ' ' + (x + 10) + ',-3" stroke="' + skin[2] + '" stroke-width="1" fill="none" opacity="0.7"/>');
      // eyebrow
      var inner = side * 7;
      var outer = side * 34;
      var innerY = -21 + browLift + (mood === 'pain' ? -2 : 0);
      var outerY = -19 + (mood === 'pain' ? 3 : 0);
      var midY = -27 + browLift * 0.5;
      s.push('<path d="M' + inner + ',' + innerY + ' Q' + (side * 20) + ',' + midY + ' ' + outer + ',' + outerY + ' L' + (outer - side * 1) + ',' + (outerY + 3.5) + ' Q' + (side * 20) + ',' + (midY + 4.5) + ' ' + (inner + side * 0.5) + ',' + (innerY + 4.5) + ' Z" fill="' + (p.beardColor && p.age === 'old' ? p.beardColor : p.hairColor) + '"/>');
    });
    if (mood === 'pain') s.push('<path d="M-4,-24 L-2,-18 M4,-24 L2,-18" stroke="' + skin[2] + '" stroke-width="1.4" opacity="0.8"/>');
    return s.join('');
  }

  function nose(skin) {
    return '<path d="M-5,-6 C-6,4 -8,10 -10,16" stroke="' + skin[2] + '" stroke-width="2.2" fill="none" opacity="0.35" stroke-linecap="round"/>' +
      '<path d="M5,-6 C6,4 8,10 9,15" stroke="' + skin[2] + '" stroke-width="1.6" fill="none" opacity="0.22" stroke-linecap="round"/>' +
      '<path d="M-12,17 C-14,22 -11,26 -6,25 M12,17 C14,22 11,26 6,25" stroke="' + skin[2] + '" stroke-width="2.2" fill="none" stroke-linecap="round"/>' +
      '<path d="M-6,25 C-3,27 3,27 6,25" stroke="' + skin[2] + '" stroke-width="1.6" fill="none" opacity="0.7"/>' +
      '<ellipse cx="-5" cy="23" rx="2.8" ry="1.6" fill="' + shade(skin[2], -0.25) + '"/><ellipse cx="5" cy="23" rx="2.8" ry="1.6" fill="' + shade(skin[2], -0.25) + '"/>' +
      '<ellipse cx="0" cy="17" rx="5" ry="4.5" fill="#ffffff" opacity="0.2"/><path d="M0,-2 L0,12" stroke="#ffffff" stroke-width="3" opacity="0.12" stroke-linecap="round"/>';
  }

  function mouth(p, mood, skin) {
    var lip = shade(skin[2], -0.05);
    if (mood === 'happy') {
      return '<path d="M-17,34 Q0,48 17,34 Q0,41 -17,34 Z" fill="#7a3b31"/><path d="M-13,36.5 Q0,41 13,36.5 L12,38 Q0,42 -12,38 Z" fill="#fbf7f2"/>' +
        '<path d="M-17,34 Q0,48 17,34" stroke="' + lip + '" stroke-width="2" fill="none" stroke-linecap="round"/>';
    }
    if (mood === 'pain') {
      return '<path d="M-15,37 Q-8,32 0,33 Q8,32 15,37 Q8,43 0,43 Q-8,43 -15,37 Z" fill="#6e3027"/><path d="M-12,36.5 L12,36.5 L11,39 L-11,39 Z" fill="#fbf7f2"/>' +
        '<path d="M-15,37 Q-8,32 0,33 Q8,32 15,37" stroke="' + lip + '" stroke-width="2" fill="none"/>';
    }
    var corner = mood === 'worried' ? 2.5 : 0;
    return '<path d="M-16,' + (36 + corner) + ' Q-8,31.5 -2,33.5 Q0,33 2,33.5 Q8,31.5 16,' + (36 + corner) + ' Q8,37.5 0,37 Q-8,37.5 -16,' + (36 + corner) + ' Z" fill="' + shade(lip, -0.08) + '"/>' +
      '<path d="M-13,' + (37.5 + corner * 0.4) + ' Q0,' + (46.5 - corner) + ' 13,' + (37.5 + corner * 0.4) + ' Q0,39.5 -13,' + (37.5 + corner * 0.4) + ' Z" fill="' + shade(skin[2], 0.12) + '"/>' +
      '<path d="M-16,' + (36 + corner) + ' Q0,38.5 16,' + (36 + corner) + '" stroke="' + shade(lip, -0.35) + '" stroke-width="1.4" fill="none"/>' +
      '<ellipse cx="0" cy="' + (41.5 - corner * 0.3) + '" rx="5" ry="1.6" fill="#ffffff" opacity="0.22"/>' +
      '<path d="M-7,47.5 Q0,50 7,47.5" stroke="' + skin[2] + '" stroke-width="1.4" fill="none" opacity="0.45"/>';
  }

  function beardPath(p, mood, skin) {
    var color = p.beardColor || p.hairColor;
    if (p.beard === 'stubble') {
      return '<path d="M-50,10 C-46,34 -28,60 0,65 C28,60 46,34 50,10 C44,26 34,34 22,34 Q12,44 0,44 Q-12,44 -22,34 C-34,34 -44,26 -50,10 Z" fill="' + color + '" opacity="0.13"/>' +
        '<path d="M-17,29 C-10,26.5 10,26.5 17,29 L16,33 C10,30.5 -10,30.5 -16,33 Z" fill="' + color + '" opacity="0.1"/>';
    }
    if (p.beard === 'short' || p.beard === 'full') {
      var full = p.beard === 'full';
      var low = full ? 86 : 70;
      return '<path d="M-54,-4 C-52,30 -36,' + (low - 6) + ' 0,' + low + ' C36,' + (low - 6) + ' 52,30 54,-4 C50,14 40,24 26,28 Q12,30 0,29 Q-12,30 -26,28 C-40,24 -50,14 -54,-4 Z" fill="' + color + '"' + (full ? '' : ' opacity="0.92"') + '/>' +
        '<path d="M-14,40 Q0,52 14,40 Q0,46 -14,40 Z" fill="' + skin[1] + '"/>' +
        (full ? '<path d="M-30,50 Q-20,64 -8,72 M30,50 Q20,64 8,72 M-14,60 Q-6,74 0,80 M14,60 Q6,74 0,80" stroke="' + shade(color, -0.18) + '" stroke-width="1.2" fill="none" opacity="0.6"/>' : '');
    }
    return '';
  }

  function moustache(p) {
    if (p.beard !== 'moustache' && p.beard !== 'short' && p.beard !== 'full') return '';
    var color = p.beardColor || p.hairColor;
    var big = p.beard === 'moustache' ? 1.15 : 1;
    return '<path d="M0,28.5 C-6,26.5 -12,26.5 -18,30 C-20,32 -' + (21 * big) + ',35 -' + (22 * big) + ',38 C-17,35 -11,33.5 0,33 C11,33.5 17,35 ' + (22 * big) + ',38 C' + (21 * big) + ',35 20,32 18,30 C12,26.5 6,26.5 0,28.5 Z" fill="' + color + '"/>';
  }

  function hairBack(p, g) {
    if (p.hair === 'curly' || p.hair === 'side' || p.hair === 'short') {
      return '<path d="M-56,-10 C-62,-50 -36,-82 0,-82 C36,-82 62,-50 56,-10 C52,-30 46,-40 40,-44 L-40,-44 C-46,-40 -52,-30 -56,-10 Z" fill="' + shade(p.hairColor, -0.1) + '"/>';
    }
    return '';
  }

  function hairFront(p, g) {
    var c = 'url(#' + g.hair + ')';
    switch (p.hair) {
      case 'short':
        return '<path d="M-55,-4 C-60,-52 -34,-80 0,-80 C34,-80 60,-52 55,-4 L51,-6 C51,-26 47,-38 40,-46 C34,-50 26,-52 18,-52 C12,-56 6,-53 0,-54 C-8,-52 -14,-56 -22,-52 C-30,-51 -36,-49 -41,-45 C-48,-38 -51,-26 -51,-6 Z" fill="' + c + '"/>' +
          '<path d="M-30,-66 Q0,-74 30,-66 M-40,-56 Q-20,-66 0,-64" stroke="' + shade(p.hairColor, 0.35) + '" stroke-width="1.6" fill="none" opacity="0.45"/>';
      case 'side':
        return '<path d="M-55,-4 C-60,-54 -32,-82 4,-81 C38,-80 60,-52 55,-4 L51,-6 C51,-28 48,-40 40,-46 C30,-52 18,-50 8,-56 C0,-52 -10,-55 -18,-51 C-28,-52 -36,-49 -42,-44 C-48,-38 -51,-26 -51,-6 Z" fill="' + c + '"/>' +
          '<path d="M14,-80 C10,-70 9,-62 8,-56" stroke="' + shade(p.hairColor, -0.3) + '" stroke-width="1.6" fill="none"/>' +
          '<path d="M-36,-64 Q-10,-76 10,-70 M20,-72 Q40,-66 48,-50" stroke="' + shade(p.hairColor, 0.4) + '" stroke-width="2" fill="none" opacity="0.45"/>';
      case 'curly':
        var curls = [];
        for (var i = 0; i < 19; i++) {
          var a = Math.PI * (0.98 + i * 1.04 / 18);
          var r = 58 + (i % 2) * 4;
          curls.push('<circle cx="' + (Math.cos(a) * r * 0.98).toFixed(1) + '" cy="' + (-20 + Math.sin(a) * r * 1.02).toFixed(1) + '" r="' + (13 + (i % 3)) + '" fill="' + c + '"/>');
        }
        return '<path d="M-54,-14 C-58,-56 -32,-84 0,-84 C32,-84 58,-56 54,-14 C50,-34 40,-46 0,-50 C-40,-46 -50,-34 -54,-14 Z" fill="' + c + '"/>' + curls.join('') +
          '<path d="M-24,-74 q6,-6 12,0 M2,-80 q6,-6 12,0 M-44,-56 q6,-6 12,0 M30,-66 q6,-6 12,0" stroke="' + shade(p.hairColor, 0.4) + '" stroke-width="1.6" fill="none" opacity="0.5"/>';
      case 'receding':
        return '<path d="M-55,-10 C-58,-30 -54,-48 -44,-56 C-44,-44 -48,-30 -50,-10 Z M55,-10 C58,-30 54,-48 44,-56 C44,-44 48,-30 50,-10 Z" fill="' + c + '"/>' +
          '<path d="M-30,-66 Q0,-74 30,-66 Q0,-70 -30,-66 Z" fill="' + p.hairColor + '" opacity="0.5"/>';
      case 'buzz':
        return '<path d="M-55,-14 C-58,-52 -34,-78 0,-78 C34,-78 58,-52 55,-14 C52,-32 46,-42 38,-48 C26,-54 10,-55 0,-54 C-12,-55 -28,-53 -40,-46 C-48,-40 -52,-30 -55,-14 Z" fill="' + p.hairColor + '" opacity="0.78"/>';
      default:
        return '';
    }
  }

  function glasses() {
    return '<g fill="none" stroke="#3b3b3b" stroke-width="2.2"><rect x="-35" y="-17" width="28" height="21" rx="7"/><rect x="7" y="-17" width="28" height="21" rx="7"/><path d="M-7,-9 Q0,-13 7,-9 M-35,-10 L-53,-13 M35,-10 L53,-13"/></g>' +
      '<path d="M-30,-14 L-22,-2 M12,-14 L20,-2" stroke="#ffffff" stroke-width="2" opacity="0.35"/>';
  }

  function headwear(p) {
    if (p.headwear === 'cap') {
      // a knitted cap (طاقية)
      return '<path d="M-52,-34 C-52,-70 -26,-88 0,-88 C26,-88 52,-70 52,-34 C40,-42 22,-46 0,-46 C-22,-46 -40,-42 -52,-34 Z" fill="' + (p.clothes === 'shirt' ? '#e9e2d0' : '#f3efe6') + '"/>' +
        '<path d="M-50,-40 C-36,-48 36,-48 50,-40 M-46,-54 C-30,-60 30,-60 46,-54 M-38,-68 C-22,-74 22,-74 38,-68" stroke="#cfc6b2" stroke-width="2" fill="none"/>';
    }
    if (p.headwear === 'turban') {
      // a white turban (عِمّة) wrapped around a cap
      return '<path d="M-58,-30 C-62,-70 -30,-96 0,-96 C30,-96 62,-70 58,-30 C44,-44 24,-50 0,-50 C-24,-50 -44,-44 -58,-30 Z" fill="#f4f1ea"/>' +
        '<path d="M-58,-34 C-40,-56 40,-64 58,-40 M-54,-50 C-30,-72 34,-78 54,-56 M-44,-70 C-20,-88 24,-88 42,-74" stroke="#d8d2c4" stroke-width="3" fill="none"/>' +
        '<path d="M-58,-30 C-44,-44 -24,-50 0,-50 C24,-50 44,-44 58,-30" stroke="#cbc4b3" stroke-width="2" fill="none"/>';
    }
    return '';
  }

  /* Clothes, drawn on the shoulders (y from about 85 down to 190). */
  function clothes(p, g) {
    var body = 'M-136,200 C-136,140 -112,114 -64,100 C-46,95 -34,90 -25,86 L25,86 C34,90 46,95 64,100 C112,114 136,140 136,200 Z';
    var fill = 'url(#' + g.cloth + ')';
    var dark = shade(p.color, -0.28);
    switch (p.clothes) {
      case 'jersey':
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-128,190 C-128,150 -116,128 -96,116 L-84,190 Z M128,190 C128,150 116,128 96,116 L84,190 Z" fill="' + p.color2 + '" opacity="0.9"/>' +
          '<path d="M-26,94 L0,124 L26,94" stroke="' + p.color2 + '" stroke-width="7" fill="none" stroke-linejoin="round"/>' +
          '<text x="34" y="160" font-size="26" font-weight="800" font-family="Segoe UI, Arial, sans-serif" fill="' + p.color2 + '" opacity="0.92">' + (p.number || '') + '</text>';
      case 'track':
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-2,100 L-2,190 M2,100 L2,190" stroke="' + dark + '" stroke-width="1.5"/>' +
          '<path d="M-30,92 L-6,116 L-2,100 M30,92 L6,116 L2,100" fill="' + shade(p.color, -0.12) + '" stroke="' + dark + '" stroke-width="1.5"/>' +
          '<path d="M-118,150 L-104,124 M118,150 L104,124" stroke="' + p.color2 + '" stroke-width="5"/>' +
          '<rect x="-3" y="104" width="6" height="10" rx="2" fill="#d0d6de"/>';
      case 'vest':
        return '<path d="' + body + '" fill="' + p.color2 + '"/>' +
          '<path d="M-110,190 C-112,150 -98,124 -60,108 L-24,98 L-6,190 Z M110,190 C112,150 98,124 60,108 L24,98 L6,190 Z" fill="' + fill + '"/>' +
          '<circle cx="-12" cy="150" r="3" fill="' + dark + '"/><circle cx="-12" cy="174" r="3" fill="' + dark + '"/>';
      case 'galabeya':
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-24,96 C-14,110 14,110 24,96" stroke="' + dark + '" stroke-width="2.5" fill="none"/>' +
          '<path d="M0,106 L0,160" stroke="' + dark + '" stroke-width="2"/>' +
          '<circle cx="5" cy="120" r="2.4" fill="' + dark + '"/><circle cx="5" cy="136" r="2.4" fill="' + dark + '"/><circle cx="5" cy="152" r="2.4" fill="' + dark + '"/>' +
          '<path d="M-90,140 Q-80,170 -86,190 M90,140 Q80,170 86,190" stroke="' + dark + '" stroke-width="1.4" fill="none" opacity="0.5"/>';
      case 'shirt':
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-60,110 L-60,190 M-30,104 L-30,190 M30,104 L30,190 M60,110 L60,190 M-110,150 L110,150 M-120,176 L120,176" stroke="' + p.color2 + '" stroke-width="2" opacity="0.4"/>' +
          '<path d="M0,104 L0,190" stroke="' + dark + '" stroke-width="2"/><circle cx="-4" cy="124" r="2.4" fill="#f4f1e8"/><circle cx="-4" cy="148" r="2.4" fill="#f4f1e8"/><circle cx="-4" cy="172" r="2.4" fill="#f4f1e8"/>';
      case 'work':
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-60,108 L-46,190 M60,108 L46,190" stroke="' + p.color2 + '" stroke-width="10"/>' +
          '<rect x="-40" y="140" width="26" height="22" rx="3" fill="' + shade(p.color, -0.15) + '"/>';
      case 'labcoat':
        return '<path d="' + body + '" fill="#f7f9fb"/>' +
          '<path d="M-26,94 L0,190 L26,94 Z" fill="' + p.color2 + '"/>' +
          '<path d="M-5,104 L5,104 L8,160 L0,174 L-8,160 Z" fill="' + shade(p.color2, -0.3) + '"/>' +
          '<path d="M-26,94 L-46,130 L-30,138 L-6,190 M26,94 L46,130 L30,138 L6,190" stroke="#d5dbe3" stroke-width="2.5" fill="none"/>' +
          '<path d="M-40,104 C-50,140 -30,160 -10,150" stroke="#3e4a5c" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="-10" cy="150" r="7" fill="#9aa7b8" stroke="#3e4a5c" stroke-width="2"/>' +
          '<path d="M40,104 C48,120 46,130 40,136" stroke="#3e4a5c" stroke-width="4" fill="none" stroke-linecap="round"/>' +
          '<rect x="60" y="150" width="34" height="5" rx="2" fill="#c7d0dc"/>';
      case 'school':
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-26,94 L-40,118 L-8,110 Z M26,94 L40,118 L8,110 Z" fill="' + shade(p.color, 0.3) + '" stroke="' + dark + '" stroke-width="1.5"/>' +
          '<path d="M0,108 L0,190" stroke="' + dark + '" stroke-width="1.5"/><rect x="44" y="140" width="34" height="26" rx="3" fill="none" stroke="' + dark + '" stroke-width="1.5"/>' +
          '<path d="M50,150 L72,150" stroke="' + p.color2 + '" stroke-width="3"/>';
      default: // t-shirt
        return '<path d="' + body + '" fill="' + fill + '"/>' +
          '<path d="M-26,94 C-16,108 16,108 26,94" stroke="' + dark + '" stroke-width="5" fill="none"/>' +
          (p.color2 ? '<path d="M-118,150 C-112,138 -104,128 -96,122 M118,150 C112,138 104,128 96,122" stroke="' + p.color2 + '" stroke-width="4" fill="none" opacity="0.8"/>' : '');
    }
  }

  function collar(p) {
    if (p.clothes === 'shirt' || p.clothes === 'vest') {
      var c = p.clothes === 'vest' ? '#f6f7f9' : shade(p.color, 0.15);
      return '<path d="M-26,90 L-12,110 L0,98 L12,110 L26,90 L22,86 L0,96 L-22,86 Z" fill="' + c + '" stroke="#c5cbd3" stroke-width="1.2"/>';
    }
    if (p.clothes === 'labcoat') {
      return '<path d="M-24,88 L-10,108 L0,96 L10,108 L24,88 L20,84 L0,94 L-20,84 Z" fill="#eef2f6" stroke="#c5cbd3" stroke-width="1.2"/>';
    }
    return '';
  }

  /* ---------- Places (backgrounds) ---------- */

  function background(name) {
    switch (name) {
      case 'farm':
        return '<defs><linearGradient id="skyF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fd3f5"/><stop offset="1" stop-color="#e8f6ff"/></linearGradient></defs>' +
          '<rect width="480" height="320" fill="url(#skyF)"/><circle cx="400" cy="56" r="26" fill="#ffe28a"/><circle cx="400" cy="56" r="40" fill="#ffe28a" opacity="0.25"/>' +
          '<path d="M0,170 C80,160 160,176 240,168 C320,160 400,172 480,164 L480,320 L0,320 Z" fill="#9ccc7a"/>' +
          '<path d="M0,190 L480,182 L480,320 L0,320 Z" fill="#7fb85f"/>' +
          '<path d="M0,214 L480,206 M0,240 L480,232 M0,270 L480,262 M0,300 L480,292" stroke="#6aa34c" stroke-width="3" opacity="0.6"/>' +
          '<path d="M0,196 C100,192 200,200 300,194 C380,190 440,194 480,192" stroke="#7cc1e0" stroke-width="6" fill="none"/>' +
          palm(64, 176, 0.9) + palm(118, 172, 0.7) + palm(440, 170, 0.8) +
          '<rect x="330" y="130" width="70" height="44" fill="#c9a77c"/><rect x="330" y="122" width="70" height="10" fill="#b48d5f"/><rect x="352" y="148" width="14" height="26" fill="#7d5d3a"/><rect x="376" y="140" width="12" height="10" fill="#7d5d3a"/>';
      case 'lab':
        return '<rect width="480" height="320" fill="#eef1f8"/><path d="M0,0 L480,0 L480,200 L0,200 Z" fill="#e6ebf5"/>' +
          '<path d="M0,60 L480,60 M0,120 L480,120" stroke="#d3dae8" stroke-width="2"/>' +
          '<rect x="20" y="70" width="130" height="8" fill="#b8c2d6"/><rect x="330" y="70" width="130" height="8" fill="#b8c2d6"/>' +
          bottle(34, 70, '#7cc6a4') + bottle(62, 70, '#f2a65a') + bottle(92, 70, '#8fb3ef') + bottle(120, 70, '#d48fd0') +
          bottle(346, 70, '#f28b82') + bottle(378, 70, '#9ad0ec') + bottle(410, 70, '#c5e17a') + bottle(438, 70, '#f7d36b') +
          '<rect x="0" y="230" width="480" height="90" fill="#cfd8e8"/><rect x="0" y="226" width="480" height="8" fill="#b4c0d6"/>' +
          microscopeIcon(402, 228);
      case 'xray':
        return '<rect width="480" height="320" fill="#1d2433"/><rect x="300" y="40" width="150" height="120" rx="6" fill="#cfe2ff" opacity="0.25"/><rect x="308" y="48" width="134" height="104" rx="4" fill="#0d1320"/>' +
          '<path d="M350,64 Q375,58 400,64 M346,80 Q375,74 404,80 M344,96 Q375,90 406,96 M346,112 Q375,106 404,112" stroke="#9fb6d6" stroke-width="3" fill="none" opacity="0.7"/>';
      case 'er':
        return '<rect width="480" height="320" fill="#fdf1f0"/><rect x="0" y="0" width="480" height="40" fill="#f6d5d1"/>' +
          '<rect x="22" y="58" width="60" height="60" rx="8" fill="#ffffff"/><path d="M44,66 L60,66 L60,80 L74,80 L74,96 L60,96 L60,110 L44,110 L44,96 L30,96 L30,80 L44,80 Z" fill="#e05d5d"/>' +
          '<path d="M380,30 L380,260" stroke="#c9c2c0" stroke-width="3"/><path d="M380,40 C400,60 420,40 440,60 C460,40 470,60 480,50 L480,260 L380,260 Z" fill="#a9d6d0" opacity="0.8"/>' +
          '<rect x="0" y="250" width="480" height="70" fill="#f0dedb"/>';
      default: // clinic
        return '<rect width="480" height="320" fill="#eaf3fb"/><rect x="0" y="236" width="480" height="84" fill="#d6e4f0"/>' +
          '<rect x="24" y="40" width="110" height="130" rx="6" fill="#ffffff"/><rect x="30" y="46" width="98" height="118" fill="#cfe8fb"/><path d="M30,86 L128,86 M30,126 L128,126 M79,46 L79,164" stroke="#ffffff" stroke-width="4"/>' +
          '<rect x="370" y="36" width="80" height="120" rx="4" fill="#ffffff" stroke="#d3dde8" stroke-width="2"/>' + skeletonPoster(410, 46) +
          '<rect x="0" y="230" width="480" height="8" fill="#c5d6e6"/>';
    }
  }

  function palm(x, y, k) {
    return '<g transform="translate(' + x + ',' + y + ') scale(' + k + ')"><path d="M-3,0 C-2,-30 2,-60 0,-90 L5,-90 C7,-60 4,-30 5,0 Z" fill="#8a6a45"/>' +
      '<path d="M2,-90 C-20,-100 -40,-96 -52,-80 C-36,-92 -18,-92 2,-88 Z M2,-90 C24,-100 44,-96 56,-80 C40,-92 22,-92 2,-88 Z M2,-90 C-8,-112 -28,-118 -40,-112 C-24,-110 -12,-104 2,-90 Z M2,-90 C12,-112 32,-118 44,-112 C28,-110 16,-104 2,-90 Z" fill="#4f8f3a"/></g>';
  }

  function bottle(x, y, color) {
    return '<path d="M' + (x + 6) + ',' + (y - 30) + ' L' + (x + 14) + ',' + (y - 30) + ' L' + (x + 14) + ',' + (y - 20) + ' L' + (x + 20) + ',' + (y - 6) + ' L' + (x + 20) + ',' + y + ' L' + x + ',' + y + ' L' + x + ',' + (y - 6) + ' L' + (x + 6) + ',' + (y - 20) + ' Z" fill="#ffffff" stroke="#b8c2d6" stroke-width="1.5"/>' +
      '<path d="M' + (x + 1) + ',' + (y - 10) + ' L' + (x + 19) + ',' + (y - 10) + ' L' + (x + 19) + ',' + y + ' L' + (x + 1) + ',' + y + ' Z" fill="' + color + '" opacity="0.8"/>';
  }

  function microscopeIcon(x, y) {
    return '<g transform="translate(' + x + ',' + y + ')" fill="#5d6b84"><rect x="-26" y="-6" width="52" height="8" rx="3"/><rect x="8" y="-60" width="8" height="56" rx="3"/><rect x="-14" y="-74" width="12" height="34" rx="4" transform="rotate(-20 -8 -57)"/><rect x="-22" y="-30" width="34" height="5" rx="2"/></g>';
  }

  function skeletonPoster(x, y) {
    return '<g transform="translate(' + x + ',' + y + ')" stroke="#9fb0c6" stroke-width="2.5" fill="none" stroke-linecap="round"><circle cx="0" cy="12" r="9"/><path d="M0,21 L0,62 M-14,30 L14,30 M-12,36 Q0,40 12,36 M-11,42 Q0,46 11,42 M-10,48 Q0,52 10,48 M-14,30 L-22,58 M14,30 L22,58 M-8,64 L8,64 M-6,64 L-10,100 M6,64 L10,100"/></g>';
  }

  /* ---------- A person in a place ---------- */

  function scene(options) {
    var p = CAST[options.who] || CAST.karim;
    var s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 320" class="bg-art" role="img" aria-label="' + p.name + '، ' + p.role + '">';
    s += background(options.bg || 'clinic');
    s += '<ellipse cx="240" cy="318" rx="150" ry="18" fill="#000" opacity="0.08"/>';
    s += '<g transform="translate(240,' + (p.age === 'child' ? 140 : 126) + ') scale(' + (p.age === 'child' ? 0.92 : 0.98) + ')">' + person(p, options.mood) + '</g>';
    s += '</svg>';
    return s;
  }

  /* A close-up of one part ("the camera moves to it"). The drawings are in
     G12.BioArt.views, added by the chapter files of this script below. */
  var views = {};

  function view(name, options) {
    var draw = views[name];
    if (!draw) return '';
    return draw(options || {});
  }

  G12.BioArt = {
    CAST: CAST,
    SKIN: SKIN,
    shade: shade,
    person: person,
    scene: scene,
    background: background,
    view: view,
    views: views,
    id: id
  };
})();
