/* ============================================
   TYPEWRITER — hero-tag + hero-sub (escribir una vez)
   Vanilla JS, sin dependencias. Respeta prefers-reduced-motion.
   - Antes de animar el texto es invisible pero ocupa su espacio
     (span fantasma), para no alterar el layout de la pagina.
   - Frases de >15 palabras se escriben al doble de rapido.
   - El cursor desaparece al terminar de escribir.
   ============================================ */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var els = Array.prototype.slice.call(document.querySelectorAll('#hero .hero-tag, #hero .hero-sub'));
  if (!els.length) return;

  els.forEach(function (el) {
    if (!el.getAttribute('data-type')) {
      el.setAttribute('data-type', el.textContent.replace(/\s+/g, ' ').trim());
    }
  });

  var style = document.createElement('style');
  style.textContent = '.tw-cursor{display:inline-block;width:2px;height:1em;margin-left:2px;vertical-align:-0.12em;background:currentColor;animation:tw-blink 0.9s steps(2,start) infinite}@keyframes tw-blink{0%,100%{opacity:1}50%{opacity:0}}.tw-ghost{visibility:hidden;display:block}.tw-typed{display:block;position:absolute;top:0;left:0;right:0}';
  document.head.appendChild(style);

  if (reduce) {
    els.forEach(function (el) { el.textContent = el.getAttribute('data-type'); });
    return;
  }

  var TICK = 18;

  els.forEach(function (el) {
    var full = el.getAttribute('data-type');
    var words = full.trim().split(/\s+/).length;
    el.style.position = 'relative';
    el.textContent = '';
    var ghost = document.createElement('span');
    ghost.className = 'tw-ghost';
    ghost.setAttribute('aria-hidden', 'true');
    ghost.textContent = full;
    var typed = document.createElement('span');
    typed.className = 'tw-typed';
    typed.setAttribute('aria-hidden', 'true');
    el.appendChild(ghost);
    el.appendChild(typed);
    el._tw = { ghost: ghost, typed: typed, full: full, tick: words > 15 ? TICK / 2 : TICK };
  });

  function finish(el) {
    var t = el._tw;
    if (!t || t.done) return;
    t.done = true;
    el.textContent = t.full;
  }

  function type(el, done) {
    var t = el._tw;
    if (t.started) return;
    t.started = true;
    var cursor = document.createElement('span');
    cursor.className = 'tw-cursor';
    cursor.setAttribute('aria-hidden', 'true');
    t.typed.appendChild(cursor);
    var pos = 0;
    (function step() {
      if (pos < t.full.length) {
        t.typed.insertBefore(document.createTextNode(t.full.charAt(pos)), cursor);
        pos++;
        setTimeout(step, t.tick);
      } else {
        finish(el);
        if (done) setTimeout(done, 260);
      }
    })();
  }

  function next() {
    els.forEach(function (el) { type(el); });
  }

  var intro = document.getElementById('intro-overlay');
  function start() { next(); }
  if (intro) {
    // Escribir cuando el intro se cierra: por click en el boton O al auto-cerrarse (hidden).
    var btn = document.getElementById('intro-btn');
    if (btn) btn.addEventListener('click', function () { start(); }, { once: true });
    if (intro.classList.contains('hidden')) {
      setTimeout(start, 650);
    } else {
      var mo = new MutationObserver(function () {
        if (intro.classList.contains('hidden')) { mo.disconnect(); setTimeout(start, 650); }
      });
      mo.observe(intro, { attributes: true, attributeFilter: ['class'] });
      // Fallback por si el observer no se dispara (p. ej. se desmonta el nodo).
      var iv = setInterval(function () {
        if (intro.classList.contains('hidden')) { clearInterval(iv); start(); }
      }, 300);
      setTimeout(function () { clearInterval(iv); if (mo) mo.disconnect(); }, 8000);
    }
  } else {
    setTimeout(start, 650);
  }
})();
