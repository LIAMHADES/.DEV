(function () {
  const el = document.getElementById('ticksWrapper');
  if (!el || el.dataset.initialized === 'true' || el.querySelector('.ti')) return;

  el.dataset.initialized = 'true';
  const inner = document.createElement('div');
  inner.className = 'ti';
  el.appendChild(inner);

  const count = 48;
  for (let i = 0; i < count; i += 1) {
    const tick = document.createElement('div');
    tick.className = 'tick-h';
    inner.appendChild(tick);
  }

  const ticks = inner.querySelectorAll('.tick-h');
  function updateTicks() {
    const root = document.documentElement;
    const limit = root.scrollHeight - root.clientHeight;
    const active = limit > 0 ? Math.round((root.scrollTop / limit) * (count - 1)) : 0;
    ticks.forEach((tick, index) => tick.classList.toggle('active', index <= active));
  }

  document.addEventListener('scroll', updateTicks, { passive: true });
  updateTicks();
}());
