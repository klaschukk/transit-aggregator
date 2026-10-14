/* ── Centralised analytics tracker ──────────────────────────────────────
   All event wiring lives here so individual templates stay markup-only.
   Fires two sinks in parallel:
     1. Umami custom events  — umami.track(name, props).  Blocked by most
        ad-blockers, so we don't depend on it for revenue attribution.
     2. POST /api/ba-click    — server-side log for partner buy clicks.
        Uses navigator.sendBeacon when available (survives tab close).
   Selectors used:
     .trip-card__buy              per-trip partner CTA
     .buy-ticket__btn             whole-route partner CTA
     .xsell__buy / .js-xsell      city-page intercity cross-sell (buy / row link)
     .js-ccy-btn                  currency switcher
     .js-fav-btn                  save-route star
     form.search-form             homepage/search departure picker
*/
(function(){
  function u(name, props){
    try { if (window.umami && typeof umami.track === 'function') umami.track(name, props || {}); }
    catch(e){}
  }

  function logBaClick(payload){
    try {
      var body = JSON.stringify(payload);
      if (navigator.sendBeacon) {
        var blob = new Blob([body], {type: 'application/json'});
        navigator.sendBeacon('/api/ba-click', blob);
      } else {
        fetch('/api/ba-click', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: body, keepalive: true,
        }).catch(function(){});
      }
    } catch(e){}
  }

  function readDataset(el, keys){
    var out = {};
    keys.forEach(function(k){ out[k] = el.dataset[k] || ''; });
    return out;
  }

  function logAbConvert(experiment, event, variant, value){
    /* Same delivery semantics as logBaClick — beacon first, fetch keepalive
       fallback. Server endpoint /api/ab-convert is a 204 fire-and-forget
       that records one row in ab_events. */
    try {
      var body = JSON.stringify({
        experiment: experiment, event: event,
        variant: variant || undefined, value: value || 1,
      });
      if (navigator.sendBeacon) {
        var blob = new Blob([body], {type: 'application/json'});
        navigator.sendBeacon('/api/ab-convert', blob);
      } else {
        fetch('/api/ab-convert', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: body, keepalive: true,
        }).catch(function(){});
      }
    } catch(e){}
  }

  /* City-page cross-sell rows (.js-xsell, _city_xsell.html) — remember which
     route the visitor went to, and count the hop itself in Umami. */
  var XSELL_KEY = 'prevozni.xsell';
  document.addEventListener('click', function(ev){
    var a = ev.target.closest('.js-xsell');
    if (!a) return;
    try { sessionStorage.setItem(XSELL_KEY, a.dataset.routeSlug || ''); } catch(e){}
    u('xsell_click', {route: a.dataset.routeSlug || '', path: location.pathname});
  });

  /* Partner buy CTAs — log every outbound affiliate click (data-partner) */
  document.addEventListener('click', function(ev){
    var el = ev.target.closest('.trip-card__buy, .buy-ticket__btn, .partners-block__btn, .transfer-offer__btn, .loop-offer__btn, .xsell__buy');
    if (!el) return;
    if (!el.dataset.partner) return;  /* skip non-affiliate .buy-ticket__btn (city map CTAs) — no blank ba_clicks */
    var payload = {
      route_slug: el.dataset.routeSlug || document.body.dataset.routeSlug || '',
      surface:    el.dataset.surface   || document.body.dataset.surface   || '',
      operator:   el.dataset.op || '',
      trip_time:  el.dataset.time || '',
      partner:    el.dataset.partner || '',
    };
    /* A buy on /rute/<slug>/ reached through a city-page cross-sell row gets
       its own surface, so the /gradski/ → intercity funnel is measurable. */
    if (payload.surface.indexOf('route_') === 0 && payload.route_slug) {
      try {
        if (sessionStorage.getItem(XSELL_KEY) === payload.route_slug) payload.surface = 'city_xsell_route';
      } catch(e){}
    }
    u('ba_click', payload);
    logBaClick(payload);
    /* Review-prompt seed — drop a 7-day cookie naming the route the user
       just bought a ticket for. On their next visit (any page), a sticky
       banner asks "How was Beograd → Budva? Leave a review". Pure first-
       party signal, no fake reviews — we just nudge real customers to
       come back and write one. */
    if (payload.route_slug && payload.partner !== 'transfer' && payload.partner !== 'cars') {
      try {
        var prTrip = encodeURIComponent(JSON.stringify({
          slug: payload.route_slug,
          ts: Date.now(),
        }));
        document.cookie = 'pending_review_route=' + prTrip
          + '; path=/; max-age=' + (60*60*24*7)
          + '; samesite=lax';
      } catch(e){}
    }
    /* A/B Exp 1 + Exp 2: a buy-button click is a conversion for the CTA-copy
       and CTA-color experiments. We pass the variant the server rendered
       (read from data-attrs) so the conversion always lines up with the
       exposure even if config changed mid-flight. */
    if (el.dataset.abCta) {
      logAbConvert('cta_copy_v1', 'buy_click', el.dataset.abCta);
    }
    if (el.dataset.abColor) {
      logAbConvert('cta_color_v2', 'buy_click', el.dataset.abColor);
    }
    /* A/B Exp 4: tourist currency-default. We attribute the conversion
       to the variant the page was *rendered with* — read from
       body[data-ab-ccy], stamped server-side. Reading the live ccy-eur
       class would mis-attribute users who toggled currency after load. */
    var ccyVariant = document.body.dataset.abCcy;
    if (ccyVariant) {
      logAbConvert('currency_default_v1', 'buy_click', ccyVariant);
    }
    /* Don't preventDefault — the <a target="_blank"> navigates naturally
       while sendBeacon / fetch(keepalive) deliver the log. */
  });

  /* ── Generic A/B conversion handler — any element with data-ab-experiment
     fires logAbConvert on click. Used for review CTA + future surfaces. */
  document.addEventListener('click', function(ev){
    var el = ev.target.closest('[data-ab-experiment]');
    if (!el) return;
    var exp = el.dataset.abExperiment;
    var variant = el.dataset.abVariant || '';
    var event = el.dataset.abEvent || 'click';
    if (exp && event) logAbConvert(exp, event, variant);
  });

  /* ── Hero search form submit — A/B Exp 3 conversion on home page.
     _search_form.html's actual <form> class is "journey-form" — this
     selector looked for "search-form"/"[data-search-form]", which no
     template has ever used, so this handler has never once fired since
     hero_sub_v1 launched 2026-04-24 (confirmed: zero conv: rows in
     ab_events for it, despite 19K+ exposures). ── */
  document.addEventListener('submit', function(ev){
    var form = ev.target.closest('form.journey-form');
    if (!form) return;
    var heroSub = document.querySelector('[data-ab-hero-sub]');
    if (heroSub) {
      logAbConvert('hero_sub_v1', 'search_submit',
                   heroSub.dataset.abHeroSub);
    }
  }, true);

  /* ── Currency toggle ── */
  document.querySelectorAll('.js-ccy-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
      u('ccy_toggle', {to: btn.dataset.ccy || ''});
    });
  });

  /* ── Save-route star ── */
  document.addEventListener('click', function(ev){
    var btn = ev.target.closest('.js-fav-btn');
    if (!btn) return;
    /* Fire AFTER the existing handler flips the class; use rAF so we observe
       the new state regardless of listener order. */
    requestAnimationFrame(function(){
      u('fav_toggle', {
        on: btn.classList.contains('fav-btn--on') ? 1 : 0,
        key: btn.dataset.key || '',
        path: btn.dataset.path || '',
      });
    });
  });

  /* ── Search form submit (journey-form is rendered by _search_form macro) ── */
  document.addEventListener('submit', function(ev){
    var form = ev.target;
    if (!form || !form.classList || !form.classList.contains('journey-form')) return;
    var fromEl = form.querySelector('#fromCity, [name="od"]');
    var toEl   = form.querySelector('#toCity, [name="do"]');
    u('search_submit', {
      from: (fromEl && fromEl.value || '').trim().slice(0, 60),
      to:   (toEl   && toEl.value   || '').trim().slice(0, 60),
    });
  });

  /* ── Scroll depth (25 / 50 / 75 / 100) ── */
  var fired = {};
  function onScroll(){
    var h = document.documentElement;
    var max = Math.max(h.scrollHeight - h.clientHeight, 1);
    var pct = Math.round((window.pageYOffset || h.scrollTop) / max * 100);
    [25, 50, 75, 100].forEach(function(m){
      if (pct >= m && !fired[m]) {
        fired[m] = true;
        u('scroll_depth', {pct: m, path: location.pathname});
      }
    });
  }
  var scrollTimer = null;
  window.addEventListener('scroll', function(){
    if (scrollTimer) return;
    scrollTimer = setTimeout(function(){ scrollTimer = null; onScroll(); }, 200);
  }, {passive: true});
})();
