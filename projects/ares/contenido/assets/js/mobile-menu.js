/* ============================================
   ARES GPS — Menu hamburguesa compartido (paginas de contenido)
   Mismo patron que el IIFE "HAMBURGER MENU" de landing/index.html:
   - toggle .nav-toggle / overlay fullscreen .nav-overlay
   - 36 ticks diagonales de scroll interno (#ovTicks / .ov-t)
   - dropdown movil "Recursos" (.ndrop-trigger / .ndrop-sub)
   - bloqueo del scroll de fondo al abrir el overlay

   Diferencia vs index.html: estas 4 paginas NO usan Lenis (scroll nativo,
   confirmado via grep — solo index.html trae Lenis). Por eso el bloqueo de
   scroll de fondo se hace unicamente con document.body.style.overflow, sin
   lenis.stop()/start(). El overlay usa overflow-y:auto nativo, así que su
   scroll interno funciona solo sin necesitar ningun "prevent" adicional
   (data-lenis-prevent no aplica aqui porque Lenis no intercepta el scroll
   nativo en estas paginas).
   ============================================ */
(function(){
    const btn = document.getElementById('navToggle');
  const ov = document.getElementById('navOverlay');
  const tc = document.getElementById('ovTicks');
  if (!btn || !ov) return;

  btn.type = 'button';
  btn.setAttribute('aria-label', 'Abrir menú');
  btn.setAttribute('aria-controls', 'navOverlay');
  btn.setAttribute('aria-expanded', 'false');
  ov.setAttribute('role', 'dialog');
  ov.setAttribute('aria-modal', 'true');
  ov.setAttribute('aria-label', 'Menú principal');
  ov.setAttribute('tabindex', '-1');
  let lastFocus = null;

  if (tc) {
    for (let i = 0; i < 36; i++) {
      const t = document.createElement('div');
      t.className = 'ov-t';
      tc.appendChild(t);
    }
  }

  const drop = document.getElementById('navDrop');
  const dropTrigger = drop && drop.querySelector('.ndrop-trigger');
  if (drop && dropTrigger) {
    const isTouch = window.matchMedia('(hover: none)').matches;
    const closeDrop = () => drop.classList.remove('open');
    dropTrigger.addEventListener('click', (e) => {
      e.preventDefault();
      drop.classList.toggle('open');
    });
    if (!isTouch) {
      drop.addEventListener('mouseenter', () => drop.classList.add('open'));
      drop.addEventListener('mouseleave', closeDrop);
    }
    document.addEventListener('click', (e) => {
      if (!drop.contains(e.target)) closeDrop();
    });
  }

  function setState(open){
    btn.classList.toggle('active', open);
    ov.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    document.documentElement.classList.toggle('menu-open', open);
    document.body.classList.toggle('menu-open', open);
    document.body.classList.toggle('nav-open', open);
  }

  function close(){
    setState(false);
    if(lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  btn.addEventListener('click', () => {
    const open = ov.classList.contains('open');
    if(!open) lastFocus = document.activeElement;
    setState(!open);
    if (!open) {
      ov.querySelectorAll('.nl-item a').forEach(a => {
        a.style.animation = 'none';
        void a.offsetWidth;
        a.style.animation = '';
      });
      requestAnimationFrame(() => ov.focus({ preventScroll: true }));
    }
  });

  ov.addEventListener('click', e => { if(e.target === ov) close(); });
  document.addEventListener('keydown', e => { if(e.key === 'Escape' && ov.classList.contains('open')) close(); });

  // Cierra el overlay al navegar (anclas internas o links a otras paginas).
  // IMPORTANTE: excluye .ndrop-trigger — es un <a> sin href usado solo para
  // desplegar el submenu "Recursos", no debe cerrar el overlay al pulsarlo
  // (mismo criterio que el navDropMob de index.html).
  ov.querySelectorAll('a:not(.ndrop-trigger)').forEach(a => a.addEventListener('click', close));

  // Dropdown "Recursos" en el menu full-screen (tap para expandir/colapsar)
  const dm = document.getElementById('navDropMob');
  if (dm) {
    const trigger = dm.querySelector('.ndrop-trigger');
    const sub = dm.querySelector('.ndrop-sub');
    if (trigger && sub) {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        sub.classList.toggle('open');
      });
    }
  }

  // Indicador de scroll interno del overlay (36 ticks verticales, derecha)
  if (tc) {
    ov.addEventListener('scroll', () => {
      const p = Math.min(ov.scrollTop / (ov.scrollHeight - ov.clientHeight || 1), 1);
      const ticks = tc.querySelectorAll('.ov-t');
      const n = Math.round(p * ticks.length);
      ticks.forEach((t, i) => t.classList.toggle('on', i <= n));
    });
  }
})();

/* === SELECTS — blur al cambiar para que la flecha vuelva abajo === */
document.querySelectorAll('select').forEach(s=>{s.addEventListener('change',()=>s.blur())});

/* === NUMBER INPUTS — botones +/- personalizados naranjas === */
document.querySelectorAll('input[type=number]').forEach(inp=>{
  inp.style.MozAppearance='textfield';
  const wrap=document.createElement('div');wrap.className='num-wrap';
  inp.parentNode.insertBefore(wrap,inp);wrap.appendChild(inp);
  const dec=document.createElement('button');dec.type='button';dec.className='num-btn num-dec';dec.textContent='−';
  const inc=document.createElement('button');inc.type='button';inc.className='num-btn num-inc';inc.textContent='+';
  wrap.appendChild(dec);wrap.appendChild(inc);
  dec.addEventListener('click',()=>{const v=parseFloat(inp.value)||0;const s=parseFloat(inp.step)||1;const mn=inp.min!==''?parseFloat(inp.min):null;if(mn===null||v-s>=mn)inp.value=v-s});
  inc.addEventListener('click',()=>{const v=parseFloat(inp.value)||0;const s=parseFloat(inp.step)||1;const mx=inp.max!==''?parseFloat(inp.max):null;if(mx===null||v+s<=mx)inp.value=v+s});
  inp.addEventListener('change',()=>{let v=parseFloat(inp.value);if(isNaN(v))v='';const mn=inp.min!==''?parseFloat(inp.min):null,mx=inp.max!==''?parseFloat(inp.max):null;if(mn!==null&&v<mn)v=mn;if(mx!==null&&v>mx)v=mx;inp.value=v});
});
