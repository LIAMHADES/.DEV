// Vídeos de "Así se ve": solo se descargan y reproducen cuando entran en pantalla.
(function () {
  var vids = document.querySelectorAll('video[data-src]');
  if (!vids.length) return;
  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function cargar(v) {
    if (v.src) return;
    v.src = v.getAttribute('data-src');
    if (quieto) { v.controls = true; return; }
    var p = v.play();
    if (p && p.catch) p.catch(function () { v.controls = true; });
  }
  if (!('IntersectionObserver' in window)) { vids.forEach(cargar); return; }
  var io = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) { cargar(v); if (!quieto && v.paused) v.play().catch(function () {}); }
      else if (v.src && !v.paused) v.pause();
    });
  }, { rootMargin: '200px 0px' });
  vids.forEach(function (v) { io.observe(v); });
})();
