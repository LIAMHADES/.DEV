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

  /* Desplegables del nav ("Descubre" y el cluster de secciones del resumen):
     en escritorio basta con el hover y el clic no cierra lo que ya esta
     abierto. El retardo evita que se cierre al cruzar el hueco hacia el menu. */
     const isTouch = window.matchMedia('(hover: none)').matches;
  document.querySelectorAll('#main-nav .ndrop').forEach(function(drop){
    const trigger = drop.querySelector('.ndrop-trigger');
    if (!trigger) return;
    let closeTimer = null;
    const openDrop = () => {
      clearTimeout(closeTimer);
      /* Solo un desplegable abierto a la vez: al pasar de "Descubre" a "Mas"
         (o al reves) el anterior se cierra en el acto. */
      document.querySelectorAll('#main-nav .ndrop.open').forEach(function(other){
        if (other !== drop) other.classList.remove('open');
      });
      drop.classList.add('open');
    };
    const closeDrop = (delay) => {
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => drop.classList.remove('open'), delay === undefined ? 170 : delay);
    };
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      if (isTouch) {
        drop.classList.toggle('open');
      } else {
        /* El clic no debe dejar :focus-within bloqueando el hover al salir. */
        trigger.blur();
      }
    });
     if (!isTouch) {
       drop.addEventListener('mouseenter', openDrop);
       drop.addEventListener('mouseleave', () => closeDrop());
       drop.addEventListener('focusin', openDrop);
       drop.addEventListener('focusout', (e) => { if (!drop.contains(e.relatedTarget)) closeDrop(); });
     }
    document.addEventListener('click', (e) => {
      if (!drop.contains(e.target)) closeDrop(0);
    });
    drop.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { closeDrop(0); trigger.focus(); }
    });
  });

  /* Logo del nav: centrado si cabe, y al lado del wordmark cuando los enlaces
     lo pisarian. Se remide en cada resize, asi que no depende de anchos fijos. */
  (function(){
    const nav = document.getElementById('main-nav');
    if (!nav) return;
    const logo = nav.querySelector('.nav-logo');
    const links = nav.querySelector('.inline-links');
    if (!logo || !links) return;
    const wordmark = nav.querySelector('.nl');
    function place(){
      nav.classList.remove('nav--logo-inline');
      const linksStyle = getComputedStyle(links);
      /* En movil/tablet con hamburguesa los enlaces estan ocultos: el logo
         debe permanecer centrado y no entrar en el fallback lateral. */
      if (linksStyle.display === 'none' || links.getBoundingClientRect().width === 0) return;
      const lw = logo.getBoundingClientRect().width;
      const half = window.innerWidth / 2;
      const linksLeft = links.getBoundingClientRect().left;
      const session = nav.querySelector('.nav-account-desktop');
      const leftEdge = Math.max(
        wordmark ? wordmark.getBoundingClientRect().right : 0,
        session ? session.getBoundingClientRect().right : 0
      );
      const margin = 14;
      if (linksLeft < half + lw / 2 + margin || leftEdge + margin > half - lw / 2) {
        nav.classList.add('nav--logo-inline');
      }
    }
    place();
    window.addEventListener('resize', place, {passive:true});
    window.addEventListener('load', place);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(place).catch(function(){});
  })();

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

   // Cierra el overlay al navegar, pero no al expandir el submenu movil.
   ov.querySelectorAll('a:not(.ndrop-trigger):not(.ndrop-trigger-static)').forEach(a => a.addEventListener('click', close));

  // Dropdown "Recursos" en el menu full-screen (tap para expandir/colapsar)
   const dm = ov.querySelector('.ndrop-trigger-static');
   if (dm) {
     const sub = dm.nextElementSibling;
     if (sub) {
       sub.id = sub.id || 'navDropMobSub';
       dm.tabIndex = 0;
       dm.setAttribute('role', 'button');
       dm.setAttribute('aria-controls', sub.id);
       dm.setAttribute('aria-expanded', String(sub.classList.contains('open')));
       const toggleDrop = () => {
         const open = sub.classList.toggle('open');
         dm.setAttribute('aria-expanded', String(open));
       };
       dm.addEventListener('click', (e) => {
         e.preventDefault();
         e.stopPropagation();
         toggleDrop();
       });
       dm.addEventListener('keydown', (e) => {
         if (e.key === 'Enter' || e.key === ' ') {
           e.preventDefault();
           toggleDrop();
         }
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
  if(inp.dataset.approxMode === 'range') wrap.classList.add('approx-hidden');
  const precision = () => {
    const step = String(inp.step || '1');
    return step.includes('.') ? step.split('.')[1].length : 0;
  };
  const clean = value => Number(value.toFixed(precision()));
  dec.addEventListener('click',()=>{const v=parseFloat(inp.value)||0;const s=parseFloat(inp.step)||1;const mn=inp.min!==''?parseFloat(inp.min):null;const next=clean(v-s);if(mn===null||next>=mn)inp.value=next});
  inc.addEventListener('click',()=>{const v=parseFloat(inp.value)||0;const s=parseFloat(inp.step)||1;const mx=inp.max!==''?parseFloat(inp.max):null;const next=clean(v+s);if(mx===null||next<=mx)inp.value=next});
  inp.addEventListener('change',()=>{let v=parseFloat(inp.value);if(isNaN(v)){inp.value='';return}const mn=inp.min!==''?parseFloat(inp.min):null,mx=inp.max!==''?parseFloat(inp.max):null;if(mn!==null&&v<mn)v=mn;if(mx!==null&&v>mx)v=mx;inp.value=clean(v)});
});
