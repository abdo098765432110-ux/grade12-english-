/* Revision sheet pages (physics-ch1-laws.html): the "Print" button prints
   the sheet (sheet.css lays it out on A4 pages). Opening the page with
   ?print=1 (the "Print" button on the chapter page) prints it straight away. */
(function () {
  'use strict';

  function printSheet() {
    var ready = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    ready.then(function () { window.print(); });
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-print-sheet]'), function (button) {
    button.addEventListener('click', printSheet);
  });

  if (window.G12 && G12.param && G12.param('print') === '1') {
    window.addEventListener('load', function () { setTimeout(printSheet, 300); });
  }
})();
