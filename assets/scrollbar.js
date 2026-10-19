/* Barra de scroll propia: fondo transparente, barra larga y semitransparente que invierte su color
   según lo que tiene detrás (mix-blend-mode: difference, como el cursor). Se puede arrastrar con el ratón;
   en pantallas táctiles aparece al hacer scroll y se esconde sola. */
(function () {
  var estilo = document.createElement('style');
  estilo.textContent =
    'html{scrollbar-width:none}html::-webkit-scrollbar,body::-webkit-scrollbar{width:0;height:0;display:none}' +
    '.sb{position:fixed;top:6px;bottom:6px;right:4px;width:12px;z-index:99990;pointer-events:none;mix-blend-mode:difference}' +
    '.sb-t{position:absolute;top:0;right:2px;width:6px;border-radius:99px;background:#fff;opacity:.9;pointer-events:auto;' +
    'transform-origin:right center;will-change:transform;transition:opacity .3s ease,scale .25s ease;touch-action:none}' +
    '.sb-t:hover,.sb.arrastrando .sb-t{opacity:1;scale:1.6 1}' +
    '.sb.oculta .sb-t{opacity:0}' +
    '@media (hover:none),(pointer:coarse){.sb-t{width:5px;pointer-events:none}}';
  document.head.appendChild(estilo);

  var barra = document.createElement('div');
  barra.className = 'sb';
  barra.setAttribute('aria-hidden', 'true');
  var pulgar = document.createElement('div');
  pulgar.className = 'sb-t';
  barra.appendChild(pulgar);
  document.body.appendChild(barra);

  var tactil = matchMedia('(hover:none),(pointer:coarse)').matches;
  var alto = 0, recorrido = 0, maxScroll = 0, pendiente = false, temporizador;

  function medir() {
    var vista = barra.clientHeight;
    maxScroll = Math.max(0, document.documentElement.scrollHeight - innerHeight);
    alto = maxScroll ? Math.max(vista * vista / document.documentElement.scrollHeight, vista * 0.2) : 0;
    recorrido = vista - alto;
    pulgar.style.height = alto + 'px';
    barra.style.display = maxScroll ? '' : 'none';
    pintar();
  }
  function pintar() {
    pendiente = false;
    var y = maxScroll ? (scrollY / maxScroll) * recorrido : 0;
    pulgar.style.transform = 'translate3d(0,' + y.toFixed(1) + 'px,0)';
  }
  addEventListener('scroll', function () {
    if (!pendiente) { pendiente = true; requestAnimationFrame(pintar); }
    if (tactil) {
      barra.classList.remove('oculta');
      clearTimeout(temporizador);
      temporizador = setTimeout(function () { barra.classList.add('oculta'); }, 1200);
    }
  }, { passive: true });
  addEventListener('resize', medir);
  addEventListener('load', medir);
  if ('ResizeObserver' in window) new ResizeObserver(medir).observe(document.body);
  if (tactil) barra.classList.add('oculta');

  var inicioY = 0, inicioScroll = 0;
  pulgar.addEventListener('pointerdown', function (e) {
    inicioY = e.clientY; inicioScroll = scrollY;
    barra.classList.add('arrastrando');
    pulgar.setPointerCapture(e.pointerId);
    document.documentElement.style.scrollBehavior = 'auto';
    e.preventDefault();
  });
  pulgar.addEventListener('pointermove', function (e) {
    if (!barra.classList.contains('arrastrando') || !recorrido) return;
    scrollTo(0, inicioScroll + (e.clientY - inicioY) * maxScroll / recorrido);
  });
  function soltar() { barra.classList.remove('arrastrando'); document.documentElement.style.scrollBehavior = ''; }
  pulgar.addEventListener('pointerup', soltar);
  pulgar.addEventListener('pointercancel', soltar);
  medir();
})();
