/* Sources & References page (sources.html): the text is fixed in the page and
   translated like the rest of the interface; this only keeps the browser tab
   title in the chosen language. */
(function () {
  'use strict';

  var G12 = window.G12;
  function title() { G12.setTitle(G12.t('Sources & References')); }
  title();
  G12.onLanguageChange(title);
})();
