/* Site UI behaviour, bundled from base.html so it is fetched once and
   cached across navigations instead of inlined into every HTML response.
   Loaded with defer; each block is a self-contained IIFE that early-exits
   when its markup is absent. */
/* ── Cookie consent banner ───────────────────────────────────────────────
   Shows the banner until the user picks "all" or "essential". Choice
   persists in `cookie_consent` (1 year). On "all" we dynamically append
   the Umami script so analytics resume without a reload. The /politika-
   kolacica/ page exposes a `.js-consent-reset` button that clears the
   cookie so the banner returns on next navigation. */
(function(){
  var KEY = 'cookie_consent';
  function readConsent(){
    var m = document.cookie.match(/(?:^|; )cookie_consent=([^;]+)/);
    return m ? m[1] : '';
  }
  function writeConsent(v){
    var oneYear = 60 * 60 * 24 * 365;
    document.cookie = KEY + '=' + v + '; path=/; max-age=' + oneYear + '; samesite=lax';
  }
  function loadUmami(){
    if (document.querySelector('script[data-umami-loaded]')) return;
    var s = document.createElement('script');
    s.defer = true;
    s.src = 'https://cloud.umami.is/script.js';
    s.setAttribute('data-website-id', '6af0f7f1-e6d7-4d30-b3f0-f47265a83db8');
    s.setAttribute('data-umami-loaded', '1');
    document.head.appendChild(s);
  }
  var banner = document.getElementById('cookieBanner');
  if (banner && !readConsent()) {
    banner.setAttribute('data-visible', 'true');
    banner.addEventListener('click', function(ev){
      var btn = ev.target.closest('button[data-consent]');
      if (!btn) return;
      var choice = btn.getAttribute('data-consent');
      writeConsent(choice);
      banner.setAttribute('data-visible', 'false');
      if (choice === 'all') loadUmami();
    });
  }
  /* Reset button on /politika-kolacica/ */
  document.addEventListener('click', function(ev){
    var btn = ev.target.closest('.js-consent-reset');
    if (!btn) return;
    ev.preventDefault();
    document.cookie = KEY + '=; path=/; max-age=0; samesite=lax';
    location.reload();
  });
})();

/* Currency switcher — toggles <html class="ccy-eur"> and persists in cookie.
   CSS shows/hides .ccy-rsd vs .ccy-eur spans rendered by every trip card. */
(function(){
  function setCcy(c){
    document.documentElement.classList.toggle('ccy-eur', c === 'eur');
    try { document.cookie = 'ccy=' + c + '; path=/; max-age=31536000; samesite=lax'; } catch(e){}
    document.querySelectorAll('.js-ccy-btn').forEach(function(b){
      var active = b.dataset.ccy === c;
      b.classList.toggle('lang-pill__item--active', active);
      b.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }
  var initial = document.documentElement.classList.contains('ccy-eur') ? 'eur' : 'rsd';
  setCcy(initial);
  document.querySelectorAll('.js-ccy-btn').forEach(function(b){
    b.addEventListener('click', function(){
      setCcy(b.dataset.ccy);
      // User-confirmed feedback — the prices switch instantly, but a
      // toast confirms the choice "stuck" so the user doesn't keep
      // tapping. Skipped if toast.js hasn't loaded yet (early click).
      if (window.toast) {
        window.toast.show(
          b.dataset.ccy === 'eur' ? 'Switched to EUR' : 'Switched to RSD',
          { type: 'info', duration: 2000 }
        );
      }
    });
  });
})();

/* Saved routes (localStorage) — star toggle on route_detail + city_pair
   page titles. Write a small record so /omiljeno/ can render it. */
(function(){
  var KEY = 'prevozni.saved';
  function read(){ try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch(e){ return []; } }
  function write(arr){ try { localStorage.setItem(KEY, JSON.stringify(arr)); } catch(e){} }
  document.querySelectorAll('.js-fav-btn').forEach(function(btn){
    var key = btn.dataset.key;
    var saved = read().some(function(x){ return x.key === key; });
    btn.classList.toggle('fav-btn--on', saved);
    btn.setAttribute('aria-pressed', saved ? 'true' : 'false');
    btn.addEventListener('click', function(){
      var arr = read();
      var idx = arr.findIndex(function(x){ return x.key === key; });
      if (idx >= 0) {
        arr.splice(idx, 1);
      } else {
        arr.push({
          key: key,
          path: btn.dataset.path,
          from: btn.dataset.from,
          to: btn.dataset.to,
        });
      }
      write(arr);
      var on = idx < 0;
      btn.classList.toggle('fav-btn--on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      // Visual confirmation — added/removed message, plus a tiny
      // haptic on Android Chrome (no-op elsewhere). The toast doubles
      // as an action-undo affordance pattern that's easy to add later.
      if (window.toast) {
        window.toast.show(on ? 'Added to saved' : 'Removed from saved',
          { type: on ? 'success' : 'info', duration: 2200 });
      }
      if (window.prevozniHaptic) window.prevozniHaptic(8);
    });
  });
})();

/* Service worker temporarily disabled — kill-switch /sw.js unregisters
   previously-installed workers on visit. Existing SW registrations get
   cleared; no new ones are created. When the cleanup is complete for
   our user base (Umami: dropped "sw-killed" events), restore the real
   SW registration from git history (commit 42582d1) and bump CACHE. */
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(rs) {
    rs.forEach(function(r) { r.unregister(); });
  }).catch(function(){});
}

/* ── Date input: pre-fill today + block past dates ──────────────────────
   The journey-form has a date input (name="datum") that starts empty.
   We set it to today so the user sees a meaningful default without waiting
   for the backend. The min attr prevents picking past dates. */
(function(){
  var d = document.querySelector('.journey-form__date');
  if (!d) return;
  var today = new Date().toISOString().split('T')[0];
  d.setAttribute('min', today);
  if (!d.value) d.value = today;
})();

/* ── Scroll-reveal + stats counter ──────────────────────────────────────
   Adds .is-visible to .fade-in elements as they enter the viewport so
   CSS triggers the animation only when the element is actually seen.
   Also animates .home-stats__num with a count-up when the stats section
   scrolls into view — makes the numbers feel alive on the homepage. */
(function(){
  /* Immediate fallback: no IntersectionObserver or reduced-motion */
  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!('IntersectionObserver' in window) || prefersReduced) {
    document.querySelectorAll('.fade-in').forEach(function(el){ el.classList.add('is-visible'); });
    return;
  }

  /* Scroll-reveal observer */
  var revealObs = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if (!e.isIntersecting) return;
      e.target.classList.add('is-visible');
      revealObs.unobserve(e.target);
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

  document.querySelectorAll('.fade-in').forEach(function(el){
    /* Hero children animate via CSS keyframes already — skip observer */
    if (el.closest('.hero')) { el.classList.add('is-visible'); return; }
    revealObs.observe(el);
  });

  /* Stats count-up */
  var statsEl = document.querySelector('.home-stats');
  if (!statsEl) return;
  var counted = false;
  var statsObs = new IntersectionObserver(function(entries){
    if (counted || !entries[0].isIntersecting) return;
    counted = true;
    statsEl.querySelectorAll('.home-stats__num').forEach(function(num){
      var target = parseInt(num.textContent.replace(/\D/g, ''), 10);
      if (!target || target < 2) return;
      var start = performance.now();
      var dur = 900;
      (function tick(now){
        var p = Math.min((now - start) / dur, 1);
        var ease = 1 - Math.pow(1 - p, 3);
        num.textContent = Math.round(ease * target);
        if (p < 1) { requestAnimationFrame(tick); }
        else { num.textContent = target; num.classList.add('counted'); }
      })(start);
    });
    statsObs.unobserve(statsEl);
  }, { threshold: 0.3 });
  statsObs.observe(statsEl);
})();


/* ── Capped grids ────────────────────────────────────────────────────────
   Any grid carrying `data-visible-cap="N"` shows its first N children and
   hides the rest; a `[data-show-more-for="<gridId>"]` button reveals them
   all. The server renders the extras with `hidden` already, so this is
   only re-application and the expand control — nothing is injected, and
   with JS off the page degrades to "first N visible", never to a blank
   list.

   Capping is a display decision only: every child stays in the HTML, so
   crawlers still read the full set. This exists because route grids were
   shipping 100-120 cards at once — /destinacije/<country>/ was 14,398px
   tall on a 390px phone with 10,665px of it one grid.

   Grids that reorder themselves (the country hub sorts by price and
   distance in place) must dispatch `prevozni:reordered` on the grid after
   moving nodes: the visible N are the first N in the CURRENT order, so
   "cheapest 30" means the 30 cheapest, not whichever 30 were on screen
   before the sort. */
(function () {
  var grids = document.querySelectorAll('[data-visible-cap]');
  if (!grids.length) return;

  grids.forEach(function (grid) {
    var cap = parseInt(grid.dataset.visibleCap, 10);
    if (!cap || cap < 1) return;
    var expanded = false;

    function apply() {
      if (expanded) return;
      Array.prototype.forEach.call(grid.children, function (child, i) {
        child.hidden = i >= cap;
      });
    }

    grid.addEventListener('prevozni:reordered', apply);
    apply();

    var btn = document.querySelector('[data-show-more-for="' + grid.id + '"]');
    if (!btn) return;
    btn.addEventListener('click', function () {
      expanded = true;
      Array.prototype.forEach.call(grid.children, function (child) {
        child.hidden = false;
      });
      var wrap = btn.closest('[data-show-more-wrap]') || btn;
      wrap.hidden = true;
    });
  });
})();
