/* Turns SVG shapes with class "sk" into hand-drawn (double, slightly wobbly) strokes.
   Deterministic: the same page always gives the same drawing. */
window.runSketch = function () {
  var seed = 11;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
  function j(a) { return (rnd() * 2 - 1) * a; }
  var NS = 'http://www.w3.org/2000/svg';

  function line(x1, y1, x2, y2, a) {
    var len = Math.hypot(x2 - x1, y2 - y1), off = Math.min(a, len * 0.025 + 0.5);
    var mx = (x1 + x2) / 2 + j(off), my = (y1 + y2) / 2 + j(off);
    return 'M' + (x1 + j(0.5)) + ',' + (y1 + j(0.5)) + ' Q' + mx + ',' + my + ' ' + (x2 + j(0.5)) + ',' + (y2 + j(0.5));
  }
  function rect(x, y, w, h, a, r) {
    if (r > 0) {   // rounded: draw as a wobbly closed curve
      var k = Math.min(r, w / 2, h / 2);
      var p = [[x + k, y], [x + w - k, y], [x + w, y + k], [x + w, y + h - k], [x + w - k, y + h], [x + k, y + h], [x, y + h - k], [x, y + k]];
      var d = 'M' + (p[0][0] + j(a)) + ',' + (p[0][1] + j(a));
      d += ' L' + (p[1][0] + j(a)) + ',' + (p[1][1] + j(a)) + ' Q' + (x + w + j(a)) + ',' + (y + j(a)) + ' ' + (p[2][0] + j(a)) + ',' + (p[2][1] + j(a));
      d += ' L' + (p[3][0] + j(a)) + ',' + (p[3][1] + j(a)) + ' Q' + (x + w + j(a)) + ',' + (y + h + j(a)) + ' ' + (p[4][0] + j(a)) + ',' + (p[4][1] + j(a));
      d += ' L' + (p[5][0] + j(a)) + ',' + (p[5][1] + j(a)) + ' Q' + (x + j(a)) + ',' + (y + h + j(a)) + ' ' + (p[6][0] + j(a)) + ',' + (p[6][1] + j(a));
      d += ' L' + (p[7][0] + j(a)) + ',' + (p[7][1] + j(a)) + ' Q' + (x + j(a)) + ',' + (y + j(a)) + ' ' + (p[0][0] + 2 + j(a)) + ',' + (p[0][1] + j(a));
      return d;
    }
    var o = 1.5;
    return line(x - j(o), y, x + w + o, y + j(0.4), a) + ' ' + line(x + w, y - o, x + w + j(0.4), y + h + o, a) + ' ' +
      line(x + w + o, y + h, x - o, y + h + j(0.4), a) + ' ' + line(x, y + h + o, x + j(0.4), y - o, a);
  }
  function ellipse(cx, cy, rx, ry, a) {
    var n = 16, start = rnd() * Math.PI * 2, pts = [];
    for (var i = 0; i <= n + 1; i++) {
      var t = start + i * (Math.PI * 2 / n), f = 1 + j(a / Math.max(rx, ry));
      pts.push([cx + Math.cos(t) * rx * f, cy + Math.sin(t) * ry * f]);
    }
    var d = 'M' + pts[0][0] + ',' + pts[0][1];
    for (var k = 1; k < pts.length - 1; k++) {
      var mx = (pts[k][0] + pts[k + 1][0]) / 2, my = (pts[k][1] + pts[k + 1][1]) / 2;
      d += ' Q' + pts[k][0] + ',' + pts[k][1] + ' ' + mx + ',' + my;
    }
    return d;
  }
  function num(el, a) { return parseFloat(el.getAttribute(a) || 0); }

  function shapeD(el) {
    var t = el.tagName.toLowerCase();
    if (t === 'rect') return function (a) { return rect(num(el, 'x'), num(el, 'y'), num(el, 'width'), num(el, 'height'), a, num(el, 'rx')); };
    if (t === 'line') return function (a) { return line(num(el, 'x1'), num(el, 'y1'), num(el, 'x2'), num(el, 'y2'), a); };
    if (t === 'circle') return function (a) { return ellipse(num(el, 'cx'), num(el, 'cy'), num(el, 'r'), num(el, 'r'), a); };
    if (t === 'ellipse') return function (a) { return ellipse(num(el, 'cx'), num(el, 'cy'), num(el, 'rx'), num(el, 'ry'), a); };
    return null;
  }

  function sketch(el) {
    var cs = getComputedStyle(el);
    var stroke = cs.stroke !== 'none' ? cs.stroke : '#26355f';
    var sw = parseFloat(cs.strokeWidth) || 1.4;
    var fill = cs.fill, fillOp = cs.fillOpacity;
    var make = shapeD(el), parent = el.parentNode, a = parseFloat(el.getAttribute('data-wob') || 1.3);
    var g = document.createElementNS(NS, 'g');
    if (el.getAttribute('transform')) g.setAttribute('transform', el.getAttribute('transform'));
    if (make) {
      if (fill && fill !== 'none' && fill !== 'rgba(0, 0, 0, 0)') {
        var f = document.createElementNS(NS, 'path');
        f.setAttribute('d', make(a * 0.6));
        f.setAttribute('style', 'fill:' + fill + ';fill-opacity:' + fillOp + ';stroke:none');
        g.appendChild(f);
      }
      [[1, 1], [0.55, 0.65]].forEach(function (v) {
        var p = document.createElementNS(NS, 'path');
        p.setAttribute('d', make(a));
        p.setAttribute('style', 'fill:none;stroke:' + stroke + ';stroke-width:' + (sw * v[1]) + ';stroke-opacity:' + v[0] + ';stroke-linecap:round;stroke-linejoin:round');
        g.appendChild(p);
      });
      parent.replaceChild(g, el);
    } else {   // path / polyline / polygon: keep it and add a second, offset stroke
      var c = el.cloneNode(true);
      c.removeAttribute('class');
      c.setAttribute('style', 'fill:none;stroke:' + stroke + ';stroke-width:' + (sw * 0.6) + ';stroke-opacity:.5;stroke-linecap:round;stroke-linejoin:round');
      var dx = j(0.9), dy = j(0.9);
      c.setAttribute('transform', (el.getAttribute('transform') || '') + ' translate(' + dx + ',' + dy + ')');
      el.style.strokeLinecap = 'round'; el.style.strokeLinejoin = 'round';
      parent.insertBefore(c, el.nextSibling);
    }
  }
  document.querySelectorAll('svg .sk').forEach(sketch);
};
