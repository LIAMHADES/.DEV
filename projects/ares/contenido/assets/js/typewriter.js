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
  var i = 0;

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

  function type(el, done) {
    var t = el._tw;
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
        cursor.parentNode && cursor.parentNode.removeChild(cursor);
        el.removeChild(t.ghost);
        t.typed.style.position = 'static';
        t.typed.removeAttribute('aria-hidden');
        setTimeout(done, 260);
      }
    })();
  }

  function next() {
    if (i < els.length) {
      var el = els[i++];
      type(el, next);
    }
  }

  setTimeout(next, 650);
})();