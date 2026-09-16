/* ============================================
   ARES GPS — Footer: el mapa se estira al llegar al final de la pagina.
   Version unica compartida por todas las paginas de contenido (antes estaba
   duplicada, identica, en cada una).

   Al empujar hacia abajo en el final de la pagina:
   - Escritorio: el fondo sube y crece mas que la imagen, y la imagen mantiene
     un margen superior (HEADROOM) para no chocar con el corte diagonal del
     footer. Sin ese margen, al crecer se veia cortada por el angulo.
   - Movil: solo crece la imagen; el alto del mapa lo fija el CSS.
   ============================================ */
(function () {
  var footerMap = document.querySelector('.pf-footer-map');
  if (!footerMap) return;

  var MOBILE_MAX = 768;
  var HEADROOM = 28; /* escritorio: aire arriba, el corte diagonal come ~8px del mapa */
  var MOBILE_FILL = 0; /* movil: el mapa ya arranca por debajo del corte, la imagen lo llena */
  var REST_MAX = 0.1; /* movil: menos recorrido => la imagen ya sale grande en reposo */
  var DESK_MAX = 0.12;
  var MOBILE_BG = 0;
  var MOBILE_SVG = 1;
  var DESK_BG = 0.8; /* el fondo sube mas */
  var DESK_SVG = 0.5; /* la imagen crece menos que el fondo */

  var target = 0;
  var current = 0;
  var lastInput = 0;
  var lastTouchY = null;
  var frame = 0;
  var baseHeight = footerMap.offsetHeight;
  var baseScale = readBaseScale();

  function isMobile() {
    return window.innerWidth <= MOBILE_MAX;
  }
  function readBaseScale() {
    return parseFloat(getComputedStyle(footerMap).getPropertyValue('--footer-svg-base-scale')) || 1;
  }
  function maxStretch() {
    return isMobile() ? REST_MAX : DESK_MAX;
  }
  function bgFactor() {
    return isMobile() ? MOBILE_BG : DESK_BG;
  }
  function svgFactor() {
    return isMobile() ? MOBILE_SVG : DESK_SVG;
  }
  function atEnd() {
    return window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
  }

  function safeTop() {
    return isMobile() ? MOBILE_FILL : HEADROOM;
  }

  /* Altura base de la imagen.
     - Escritorio: el mapa crece con el scroll, asi que se compensa la escala
       frame a frame para que la imagen ocupe siempre (mapa - aire).
     - Movil: el mapa NO cambia de alto, asi que el tamano lo da la escala; la
       altura base es fija y se calcula para que en el pico llene el mapa justo. */
  function tileHeight() {
    var room = Math.max(0, footerMap.offsetHeight - safeTop());
    if (isMobile()) return room / (baseScale + maxStretch());
    return room / (baseScale + current * svgFactor());
  }

  function restTile() {
    footerMap.style.setProperty('--footer-tile-height', tileHeight().toFixed(2) + 'px');
  }

  function clearVars() {
    footerMap.style.removeProperty('--footer-bg-stretch');
    footerMap.style.removeProperty('--footer-svg-stretch');
    footerMap.style.removeProperty('--footer-rise');
  }

  function release() {
    target = 0;
    lastInput = 0;
    if (!frame) frame = requestAnimationFrame(tick);
  }

  function push(amount) {
    var max = maxStretch();
    target = Math.min(max, target + Math.min(max, amount));
    lastInput = performance.now();
    if (!frame) frame = requestAnimationFrame(tick);
  }

  function tick(now) {
    var elapsed = now - lastInput;
    if (elapsed > 90) target = Math.max(0, target - 0.12 * Math.min(1, (elapsed - 90) / 140));
    current += (target - current) * 0.22;

    var bg = bgFactor();
    var svg = svgFactor();
    footerMap.style.setProperty('--footer-bg-stretch', (current * bg).toFixed(4));
    footerMap.style.setProperty('--footer-svg-stretch', (current * svg).toFixed(4));
    footerMap.style.setProperty('--footer-rise', (current * bg * baseHeight).toFixed(2) + 'px');

    footerMap.style.setProperty('--footer-tile-height', tileHeight().toFixed(2) + 'px');

    if (Math.abs(current - target) > 0.0005 || target > 0.0005) {
      frame = requestAnimationFrame(tick);
    } else {
      current = 0;
      target = 0;
      clearVars();
      restTile();
      frame = 0;
    }
  }

  window.addEventListener('wheel', function (event) {
    if (event.deltaY > 0 && atEnd()) push(Math.abs(event.deltaY) * 0.0009);
    else if (event.deltaY < 0) release();
  }, { passive: true });

  window.addEventListener('touchstart', function (event) {
    lastTouchY = event.touches[0] ? event.touches[0].clientY : null;
  }, { passive: true });

  window.addEventListener('touchmove', function (event) {
    var y = event.touches[0] ? event.touches[0].clientY : lastTouchY;
    var delta = lastTouchY == null || y == null ? 0 : lastTouchY - y;
    lastTouchY = y;
    if (delta > 0 && atEnd()) push(delta * 0.002);
    else if (delta < 0) release();
  }, { passive: true });

  window.addEventListener('touchend', function () {
    lastTouchY = null;
    release();
  }, { passive: true });

  window.addEventListener('touchcancel', function () {
    lastTouchY = null;
    release();
  }, { passive: true });

  var resizeTimer = 0;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (frame) return;
      baseHeight = footerMap.offsetHeight;
      baseScale = readBaseScale();
      restTile();
    }, 200);
  }, { passive: true });

  restTile();
})();
