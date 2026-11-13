/* Flows the blocks of each chapter (.src) into A4 pages. A block never splits;
   a heading never stays alone at the bottom of a page; <hr class="pb"> forces a new page. */
window.runPaginate = function () {
  var CH = window.CHAPTERS || {};
  var n = 0, warnings = [];
  function newPage(ch) {
    n += 1;
    var sec = document.createElement('section');
    sec.className = 'page'; sec.id = 'p' + n;
    sec.innerHTML = '<div class="hdr"><span>' + CH[ch] + '</span><span class="tape"></span><span class="pg">' + n + '</span></div><div class="sheet"></div>';
    document.body.insertBefore(sec, document.getElementById('srcs'));
    return sec.querySelector('.sheet');
  }
  function over(sheet) { if (sheet.scrollHeight > sheet.clientHeight + 1) return true; var last = sheet.lastElementChild; if (!last) return false; return last.getBoundingClientRect().bottom > sheet.getBoundingClientRect().bottom - 3; }
  function isHeading(el) { return el && /^(H1|H2|H3)$/.test(el.tagName) || (el && el.classList && (el.classList.contains('sub') || el.classList.contains('keep'))); }

  /* a long table (rows, header repeated) or list (items) may continue on the next page */
  function split(b, sheet) {
    if (b.classList.contains('nosplit')) return null;
    var part, items, moved = 0, min = 2;
    if (b.tagName === 'TABLE' && b.classList.contains('t')) {
      var rows = Array.prototype.slice.call(b.rows);
      if (rows.length < 4) return null;
      part = b.cloneNode(false); part.classList.add('cut');
      var tb = document.createElement('tbody'); part.appendChild(tb); tb.appendChild(rows[0].cloneNode(true));
      sheet.appendChild(part);
      for (var i = 1; i < rows.length - 1; i++) {
        tb.appendChild(rows[i]);
        if (over(sheet)) { rows[i + 1].parentNode.insertBefore(rows[i], rows[i + 1]); break; }
        moved++;
      }
    } else if ((b.tagName === 'UL' || b.tagName === 'OL') && b.children.length >= 3) {
      var lis = Array.prototype.slice.call(b.children);
      part = b.cloneNode(false); sheet.appendChild(part);
      for (var k = 0; k < lis.length - 1; k++) {
        part.appendChild(lis[k]);
        if (over(sheet)) { b.insertBefore(lis[k], b.firstChild); break; }
        moved++;
      }
      if (moved >= min && b.tagName === 'OL') b.setAttribute('start', (parseInt(b.getAttribute('start') || '1', 10) + moved));
    } else return null;
    if (moved < min) {   // undo
      if (b.tagName === 'TABLE') { var back = Array.prototype.slice.call(part.rows).slice(1); var ref = b.rows[1] || null; back.forEach(function (r) { b.rows[0].parentNode.insertBefore(r, ref); }); }
      else { var ls = Array.prototype.slice.call(part.children).reverse(); ls.forEach(function (li) { b.insertBefore(li, b.firstChild); }); }
      sheet.removeChild(part); return null;
    }
    b.classList.add('cont');
    return b;
  }

  document.querySelectorAll('#srcs .src').forEach(function (src) {
    var ch = src.getAttribute('data-ch');
    var blocks = Array.prototype.slice.call(src.children);
    var prev = document.querySelectorAll('.page .sheet');
    var sheet = (src.getAttribute('data-continue') && prev.length) ? prev[prev.length - 1] : newPage(ch);
    blocks.forEach(function (b) {
      if (b.tagName === 'HR' && b.classList.contains('pb')) { if (sheet.children.length) sheet = newPage(ch); return; }
      sheet.appendChild(b);
      if (over(sheet)) {
        if (sheet.children.length === 1) { warnings.push('block too tall on page ' + n); return; }
        sheet.removeChild(b);
        var rest = split(b, sheet);
        if (rest) { sheet = newPage(ch); sheet.appendChild(rest); if (over(sheet)) warnings.push('block too tall on page ' + n); return; }
        var carry = [];
        while (sheet.lastElementChild && isHeading(sheet.lastElementChild)) carry.unshift(sheet.removeChild(sheet.lastElementChild));
        sheet = newPage(ch);
        carry.forEach(function (c) { sheet.appendChild(c); });
        sheet.appendChild(b);
        if (over(sheet)) warnings.push('block too tall on page ' + n);
      }
    });
  });
  document.getElementById('srcs').remove();
  window.PAGINATE = { pages: n, warnings: warnings };
};
Promise.all(['400 13px Pen','500 13px Pen','700 13px Pen','600 13px Pen','650 13px Pen','400 20px Ruqaa','700 20px Ruqaa','700 13px Marker','700 16px Hand'].map(function (f) { return document.fonts.load(f); }))
  .then(function () { return document.fonts.ready; })
  .then(function () { window.runPaginate(); if (window.runSketch) window.runSketch(); window.BOOK_DONE = true; });
