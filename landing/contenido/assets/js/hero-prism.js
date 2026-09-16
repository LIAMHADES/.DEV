/* ============================================
   ARES GPS — Rejilla animada del hero (malla)
   Activa por si sola cualquier <div class="sec-prism" id="..."> que este
   dentro de una seccion posicionada. Es idempotente (si la rejilla ya existe
   no la vuelve a crear) y respeta prefers-reduced-motion.

   El mismo patron que ya usan comunidad/descanso/actividad en su script
   inline, extraido aqui para las paginas que no lo tenian.
   ============================================ */
(function () {
  var SIZE = 40;
  var MAX_TRAIL = 18;
  var LIGHT = '134,187,216';
  var ACCENT = '246,174,45';

  function build(id) {
    var wrap = document.getElementById(id);
    if (!wrap || wrap.querySelector('.prism-grid')) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var section = wrap.closest('section, header') || wrap.parentElement;
    if (!section) return;

    var cols = Math.ceil(section.offsetWidth / SIZE) + 4;
    var rows = Math.ceil(section.offsetHeight / SIZE) + 4;
    var grid = document.createElement('div');
    grid.className = 'prism-grid';
    var gw = cols * SIZE;
    var gh = rows * SIZE;
    grid.style.cssText =
      'width:' + gw + 'px;height:' + gh + 'px;margin-left:' + gw / -2 + 'px;margin-top:' + gh / -2 + 'px;' +
      'grid-template-columns:repeat(' + cols + ',' + SIZE + 'px);grid-template-rows:repeat(' + rows + ',' + SIZE + 'px)';

    var cells = [];
    for (var i = 0; i < rows * cols; i += 1) {
      var cell = document.createElement('div');
      cell.className = 'prism-cell';
      cell.style.cssText = 'width:' + SIZE + 'px;height:' + SIZE + 'px';
      grid.appendChild(cell);
      cells.push(cell);
    }
    wrap.appendChild(grid);

    var trail = [];
    var color = LIGHT;

    section.addEventListener('mousemove', function (event) {
      var rect = section.getBoundingClientRect();
      var left = section.offsetWidth / 2 - gw / 2;
      var top = section.offsetHeight / 2 - gh / 2;
      var col = Math.floor((event.clientX - rect.left - left) / SIZE);
      var row = Math.floor((event.clientY - rect.top - top) / SIZE);
      if (col >= 0 && col < cols && row >= 0 && row < rows) trail.push({ col: col, row: row, life: 1 });
      color = event.target.closest('a,button') ? ACCENT : LIGHT;
    });

    section.addEventListener('mouseleave', function () {
      trail.length = 0;
      cells.forEach(function (cell) {
        cell.style.background = 'rgba(134,187,216,0)';
        cell.classList.remove('lit');
      });
    });

    (function animate() {
      for (var i = trail.length - 1; i >= 0; i -= 1) {
        trail[i].life -= 0.04;
        if (trail[i].life <= 0) trail.splice(i, 1);
      }
      while (trail.length > MAX_TRAIL) trail.shift();
      var lit = {};
      trail.forEach(function (point) {
        var key = point.row * cols + point.col;
        if (!lit[key] || lit[key] < point.life) lit[key] = point.life;
      });
      cells.forEach(function (cell, index) {
        var life = lit[index] || 0;
        cell.style.background = life > 0.01 ? 'rgba(' + color + ',' + life * 0.3 + ')' : 'rgba(134,187,216,0)';
        cell.classList.toggle('lit', life > 0.01);
      });
      requestAnimationFrame(animate);
    })();
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.sec-prism[id]'), function (el) {
      build(el.id);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  window.addEventListener('load', init);
})();
