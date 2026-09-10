(function () {
  var pool = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZÁÉÍÓÚÜÊÈËÀÂÄÇ1234567890€$%&@#+*~^<>/\\[]{}|_-¡¿!?';
  var headlineReady = false;
  var headlineReadyCallbacks = [];
  var headlineParts = [];
  var animationStopped = false;
  var headlineFallbackTimer;

  function randomText(length) {
    var result = '';
    for (var i = 0; i < length; i += 1) {
      result += pool[Math.floor(Math.random() * pool.length)];
    }
    return result;
  }

  function notifyHeadlineReady() {
    if (headlineReady) return;
    if (headlineFallbackTimer) window.clearTimeout(headlineFallbackTimer);
    headlineReady = true;
    var callbacks = headlineReadyCallbacks;
    headlineReadyCallbacks = [];
    callbacks.forEach(function (callback) {
      callback();
    });
  }

  function whenHeadlinesReady(callback) {
    if (headlineReady) {
      callback();
      return;
    }
    headlineReadyCallbacks.push(callback);
  }

  function finishHeadlines() {
    animationStopped = true;
    headlineParts.forEach(function (part) {
      part.element.textContent = part.text;
    });
    notifyHeadlineReady();
  }

  function animateLine(element, text, done) {
    var locked = 0;
    var parts = [text];
    var mobileBreak = element.getAttribute('data-mobile-break');
    if (mobileBreak && window.matchMedia('(max-width: 680px)').matches) {
      parts = mobileBreak.split('|');
    }
    var targets = [];

    element.textContent = '';
    parts.forEach(function (part, index) {
      var target = document.createElement('span');
      target.className = 'onix-tw-part';
      element.appendChild(target);
      var targetPart = { element: target, text: part.trim() };
      targets.push(targetPart);
      headlineParts.push(targetPart);
      if (index < parts.length - 1) {
        var br = document.createElement('br');
        br.className = 'onix-mobile-break';
        element.appendChild(br);
      }
    });

    function animatePart(part, next) {
      var position = 0;

      function tickPart() {
        if (animationStopped) return;
        if (position === part.text.length) {
          part.element.textContent = part.text;
          next();
          return;
        }
        var display = '';
        for (var i = 0; i < part.text.length; i += 1) {
          display += i < position ? part.text[i] : pool[Math.floor(Math.random() * pool.length)];
        }
        part.element.textContent = display;
        position += 1;
        window.setTimeout(tickPart, position < part.text.length - 5 ? 25 : 40);
      }

      tickPart();
    }

    function tick() {
      if (animationStopped) return;
      if (locked === targets.length) {
        if (done) done();
        return;
      }
      animatePart(targets[locked], function () {
        locked += 1;
        tick();
      });
    }

    tick();
  }

  function animateHeadline(headline, done) {
    var lines = headline.querySelectorAll('.onix-tw-line');
    if (!lines.length) {
      done();
      return;
    }

    var reservedHeight = headline.getBoundingClientRect().height;
    if (reservedHeight) headline.style.minHeight = reservedHeight + 'px';

    var firstText = lines[0].textContent.trim();
    var secondText = lines.length > 1 ? lines[1].textContent.trim() : '';

    if (!secondText) {
      animateLine(lines[0], firstText, done);
      return;
    }

    var secondMobileBreak = lines[1].getAttribute('data-mobile-break');
    var secondCycle = window.setInterval(function () {
      if (animationStopped) return;
      if (secondMobileBreak && window.matchMedia('(max-width: 680px)').matches) {
        var mobileParts = secondMobileBreak.split('|');
        lines[1].textContent = '';
        mobileParts.forEach(function (part, index) {
          var scrambledPart = document.createElement('span');
          scrambledPart.className = 'onix-tw-part';
          scrambledPart.textContent = randomText(part.trim().length);
          lines[1].appendChild(scrambledPart);
          if (index < mobileParts.length - 1) {
            var mobileBreak = document.createElement('br');
            mobileBreak.className = 'onix-mobile-break';
            lines[1].appendChild(mobileBreak);
          }
        });
        return;
      }
      lines[1].textContent = randomText(secondText.length);
    }, 50);

    animateLine(lines[0], firstText, function () {
      window.clearInterval(secondCycle);
      window.setTimeout(function () {
        animateLine(lines[1], secondText, done);
      }, 150);
    });
  }

  function animateHeadlines() {
    var headlines = document.querySelectorAll('.onix-typewriter-title');
    if (!headlines.length) {
      notifyHeadlineReady();
      return;
    }

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      headlines.forEach(function (headline) {
        headline.querySelectorAll('.onix-tw-line').forEach(function (line) {
          line.textContent = line.textContent.trim();
        });
      });
      notifyHeadlineReady();
      return;
    }

    var remaining = headlines.length;
    headlines.forEach(function (headline, headlineIndex) {
      window.setTimeout(function () {
        animateHeadline(headline, function () {
          remaining -= 1;
          if (remaining === 0) notifyHeadlineReady();
        });
      }, headlineIndex * 80);
    });
  }

  function revealAllImmediately() {
    document.querySelectorAll('.reveal-title, .reveal-el, .reveal-card').forEach(function (element) {
      element.style.opacity = '1';
      element.style.transform = 'none';
    });
  }

  function revealPage() {
    var typewriterTitles = document.querySelectorAll('.onix-typewriter-title');
    var rest = document.querySelectorAll('.reveal-title:not(.onix-typewriter-title), .reveal-el, .reveal-card');
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function revealRest() {
      gsap.to(rest, {
        opacity: 1,
        y: 0,
        duration: 0.6,
        ease: 'power3.out',
        stagger: 0.05,
        delay: 0.02
      });
    }

    if (reduceMotion || typeof gsap === 'undefined' || typeof gsap.to !== 'function') {
      revealAllImmediately();
      return;
    }

    gsap.to(typewriterTitles, {
      opacity: 1,
      y: 0,
      duration: 0.55,
      ease: 'power3.out',
    });

    if (!typewriterTitles.length) {
      revealRest();
      return;
    }

    // Supporting content follows the start of the typewriter, not its end.
    window.setTimeout(revealRest, 500);
  }

  function revealInitialSections() {
    var visibleSections = [];
    document.querySelectorAll('.fi').forEach(function (section) {
      var rect = section.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        visibleSections.push(section);
      }
    });
    visibleSections.forEach(function (section) {
      section.classList.add('vis');
    });
  }

  function initLegacyRedNav() {
    if (!document.getElementById('calc-slider')) return;
    var button = document.getElementById('menu-toggle');
    var links = document.querySelector('.nav-links');
    var cta = document.querySelector('.nav-cta');
    if (!button || !links || button.dataset.onixNavReady === 'true') return;

    function close() {
      links.classList.remove('open');
      button.classList.remove('is-open');
      button.setAttribute('aria-expanded', 'false');
      if (cta) cta.classList.remove('menu-visible');
    }

    button.dataset.onixNavReady = 'true';
    button.addEventListener('click', function () {
      var isOpen = links.classList.toggle('open');
      button.classList.toggle('is-open', isOpen);
      button.setAttribute('aria-expanded', String(isOpen));
      if (cta) cta.classList.toggle('menu-visible', isOpen);
    });
    links.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', close);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') close();
    });
  }

  function initNavigationTransitions() {
    document.addEventListener('click', function (event) {
      var link = event.target.closest && event.target.closest('a[href]');
      if (!link || event.defaultPrevented || link.target === '_blank' || link.hasAttribute('download')) return;
      if (!link.closest('nav')) return;
      var href = link.getAttribute('href');
      if (!href || href.charAt(0) === '#' || /^(?:[a-z]+:|\/\/)/i.test(href)) return;
      try {
        sessionStorage.setItem('onix-nav-transition', '1');
      } catch (error) {
        // Private browsing can deny sessionStorage; navigation still works.
      }
    }, true);
  }

  function startPreloader(onReady) {
    var preloader = document.getElementById('preloader');
    var top = document.querySelector('#preloader .pl-half.top');
    var bottom = document.querySelector('#preloader .pl-half.bot');
    if (!preloader || !top || !bottom) {
      onReady();
      return;
    }

    var preloaderReady = false;
    var finished = false;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!document.documentElement.classList.contains('onix-nav-transition')) {
      preloader.style.display = 'none';
      preloader.style.opacity = '0';
      preloader.style.visibility = 'hidden';
      onReady();
      return;
    }

    preloader.style.display = 'flex';
    preloader.style.opacity = '1';
    preloader.style.visibility = 'visible';

    function beginPage() {
      if (onReady) onReady();
    }

    function finishIfReady() {
      if (finished || !preloaderReady) return;
      finished = true;

      if (typeof gsap === 'undefined' || typeof gsap.to !== 'function' || reduceMotion) {
        preloader.style.display = 'none';
        beginPage();
        return;
      }

      gsap.to(preloader, {
        opacity: 0,
        duration: 0.35,
        ease: 'power2.in',
        onComplete: function () {
          preloader.style.display = 'none';
          beginPage();
        }
      });
    }

    if (reduceMotion || typeof gsap === 'undefined' || typeof gsap.timeline !== 'function') {
      preloaderReady = true;
      finishIfReady();
      return;
    }

    var timeline = gsap.timeline({
      onComplete: function () {
        preloaderReady = true;
        finishIfReady();
      }
    });
    timeline.fromTo(top, { x: -560 }, { x: 0, duration: 1.6, ease: 'power4.out' }, 0);
    timeline.fromTo(bottom, { x: 560 }, { x: 0, duration: 1.6, ease: 'power4.out' }, 0);

    // Protect against a blocked remote GSAP request or a stalled animation.
    window.setTimeout(function () {
      if (finished) return;
      finishHeadlines();
      preloaderReady = true;
      finishIfReady();
    }, 3000);
  }

  function startMotionSequence() {
    document.documentElement.classList.add('onix-shared-motion');
    document.documentElement.classList.add('onix-motion-ready');
    animateHeadlines();
    headlineFallbackTimer = window.setTimeout(function () {
      if (!headlineReady) finishHeadlines();
    }, 3000);
    revealPage();
    // Local page observers may add .vis immediately; the shared gate keeps
    // those sections hidden until the same half-second reveal point.
    window.setTimeout(function () {
      document.documentElement.classList.add('onix-rest-ready');
      revealInitialSections();
    }, 500);
  }

  function boot() {
    initNavigationTransitions();
    try {
      if (!document.documentElement.classList.contains('onix-nav-transition') && sessionStorage.getItem('onix-nav-transition') === '1') {
        document.documentElement.classList.add('onix-nav-transition');
        sessionStorage.removeItem('onix-nav-transition');
      }
    } catch (error) {
      // Keep boot resilient when storage is unavailable.
    }
    var headlines = document.querySelectorAll('.onix-typewriter-title');
    if (!headlines.length) return;

    if (document.getElementById('calc-slider')) {
      document.documentElement.classList.add('onix-legacy-red');
      initLegacyRedNav();
    }

    startPreloader(startMotionSequence);
  }

  window.addEventListener('DOMContentLoaded', boot);
})();
