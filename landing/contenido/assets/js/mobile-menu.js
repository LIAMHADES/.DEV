/* ============================================
   ARES GPS — Menu hamburguesa compartido (paginas de contenido)
   Mismo patron que el IIFE "HAMBURGER MENU" de landing/index.html:
   - toggle .nav-toggle / overlay fullscreen .nav-overlay
   - 36 ticks verticales de scroll interno (#ovTicks / .ov-t)
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

  if (tc) {
    for (let i = 0; i < 36; i++) {
      const t = document.createElement('div');
      t.className = 'ov-t';
      tc.appendChild(t);
    }
  }

  function close(){
    btn.classList.remove('active');
    ov.classList.remove('open');
    document.body.style.overflow = '';
  }

  btn.addEventListener('click', () => {
    const open = ov.classList.contains('open');
    btn.classList.toggle('active');
    ov.classList.toggle('open');
    document.body.style.overflow = open ? '' : 'hidden';
    if (!open) {
      ov.querySelectorAll('.nl-item a').forEach(a => {
        a.style.animation = 'none';
        void a.offsetWidth;
        a.style.animation = '';
      });
    }
  });

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
