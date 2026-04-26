/* Prevozni mobile UX behaviours.
 *
 * Loaded only on viewports ≤767px via a `media` attribute on the <script>
 * tag in base.html (`media` actually has no effect on <script>; we instead
 * gate inside this file with a single matchMedia check on boot, so the
 * script downloads on every device but bails out cheaply on desktop).
 *
 * Modules:
 *   - Bottom sheets (open / close / backdrop / ESC / swipe-down)
 *   - Off-canvas nav drawer
 *   - Header frosted-on-scroll + hide-on-scroll-down
 *   - FAB hide-on-scroll-down + scroll-to-top intent
 *   - Sticky CTA show after first trip + per-session dismiss
 *
 * Everything is delegated to document for resilience against partial
 * hydration / late-rendered components. No external deps.
 */
(function () {
  'use strict';

  // Bail on desktop — the CSS overlay also scopes to ≤767px, but skipping
  // the JS work avoids touching DOM we won't style anyway.
  var MOBILE_MQ = '(max-width: 767px)';
  if (window.matchMedia && !window.matchMedia(MOBILE_MQ).matches) return;

  var body = document.body;
  var html = document.documentElement;

  /* ── Bottom sheets ──────────────────────────────────────────────── */
  function openSheet(id) {
    var sheet = document.getElementById(id);
    if (!sheet) return;
    var backdrop = document.querySelector('[data-sheet-backdrop="' + id + '"]');
    sheet.removeAttribute('hidden');
    if (backdrop) backdrop.removeAttribute('hidden');
    // Force reflow so the transition fires when we add the `--open` class.
    void sheet.offsetWidth;
    sheet.classList.add('m-sheet--open');
    if (backdrop) backdrop.classList.add('m-sheet-backdrop--open');
    body.classList.add('m-sheet-locked');
    var firstFocusable = sheet.querySelector('button, a, input, [tabindex]:not([tabindex="-1"])');
    if (firstFocusable) firstFocusable.focus();
    sheet.dataset.openedAt = String(Date.now());
  }
  function closeSheet(id) {
    var sheet = document.getElementById(id);
    if (!sheet) return;
    var backdrop = document.querySelector('[data-sheet-backdrop="' + id + '"]');
    sheet.classList.remove('m-sheet--open');
    if (backdrop) backdrop.classList.remove('m-sheet-backdrop--open');
    body.classList.remove('m-sheet-locked');
    // Hide after the transition so the offscreen sheet doesn't trap focus
    // or capture clicks.
    setTimeout(function () {
      // Only hide if it's still meant to be closed (user might have re-opened).
      if (!sheet.classList.contains('m-sheet--open')) {
        sheet.setAttribute('hidden', '');
        if (backdrop) backdrop.setAttribute('hidden', '');
      }
    }, 260);
  }
  // Click delegation: any element with data-sheet-open / data-sheet-close.
  document.addEventListener('click', function (ev) {
    var opener = ev.target.closest('[data-sheet-open]');
    if (opener) {
      ev.preventDefault();
      openSheet(opener.dataset.sheetOpen);
      return;
    }
    var closer = ev.target.closest('[data-sheet-close]');
    if (closer) {
      ev.preventDefault();
      closeSheet(closer.dataset.sheetClose);
      return;
    }
    // Tap outside the sheet (i.e. the backdrop itself) closes it.
    var bdrop = ev.target.closest('[data-sheet-backdrop]');
    if (bdrop && !bdrop.hasAttribute('hidden')) {
      closeSheet(bdrop.getAttribute('data-sheet-backdrop'));
    }
  });
  // ESC closes the topmost open sheet.
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape') return;
    var open = document.querySelector('.m-sheet--open');
    if (open) closeSheet(open.id);
  });
  // Swipe-down on the handle closes.
  document.addEventListener('touchstart', function (ev) {
    var handle = ev.target.closest('.m-sheet__handle');
    if (!handle) return;
    var sheet = handle.closest('.m-sheet');
    if (!sheet) return;
    var startY = ev.touches[0].clientY;
    function onMove(e) {
      var dy = e.touches[0].clientY - startY;
      if (dy > 60) {
        closeSheet(sheet.id);
        document.removeEventListener('touchmove', onMove);
      }
    }
    document.addEventListener('touchmove', onMove, { passive: true });
    document.addEventListener('touchend', function () {
      document.removeEventListener('touchmove', onMove);
    }, { once: true });
  }, { passive: true });
  // Expose for templates that want to call programmatically.
  window.PrevozniSheet = { open: openSheet, close: closeSheet };


  /* ── Off-canvas nav drawer ──────────────────────────────────────── */
  var navToggle = document.getElementById('navToggle');
  var navBackdrop = document.querySelector('[data-nav-backdrop]');
  var siteNav = document.getElementById('siteNav');
  var navIconSvg = navToggle && navToggle.querySelector('svg');
  var HAMBURGER_ICON = '<path d="M3 12h18M3 6h18M3 18h18"/>';
  var CLOSE_ICON = '<path d="M18 6L6 18M6 6l12 12"/>';
  function setNavIcon(open) {
    if (navIconSvg) navIconSvg.innerHTML = open ? CLOSE_ICON : HAMBURGER_ICON;
  }
  // Drawer is in the DOM at all times; mark it inert when closed so keyboard
  // users + screen readers skip it. Removed when open or on desktop.
  if (siteNav) siteNav.setAttribute('inert', '');
  function closeNav() {
    body.classList.remove('m-nav-open');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
    if (siteNav) siteNav.setAttribute('inert', '');
    setNavIcon(false);
    if (navBackdrop) {
      navBackdrop.classList.remove('m-sheet-backdrop--open');
      navBackdrop.setAttribute('hidden', '');
    }
  }
  function openNav() {
    body.classList.add('m-nav-open');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'true');
    if (siteNav) siteNav.removeAttribute('inert');
    setNavIcon(true);
    if (navBackdrop) {
      navBackdrop.removeAttribute('hidden');
      navBackdrop.classList.add('m-sheet-backdrop--open');
    }
  }
  if (navToggle) {
    navToggle.addEventListener('click', function (ev) {
      ev.stopPropagation();
      if (body.classList.contains('m-nav-open')) closeNav(); else openNav();
    });
    // Close on link click — natural pattern; user navigates and drawer closes.
    document.addEventListener('click', function (ev) {
      if (!body.classList.contains('m-nav-open')) return;
      var link = ev.target.closest('.site-nav__link');
      if (link) closeNav();
    });
    // Tap on backdrop closes drawer.
    if (navBackdrop) {
      navBackdrop.addEventListener('click', closeNav);
    }
    // ESC closes drawer too.
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && body.classList.contains('m-nav-open')) closeNav();
    });
  }

  // Bottom-nav "More" tab opens the same off-canvas drawer the hamburger
  // does — keeps a single source of truth for the overflow menu.
  document.addEventListener('click', function (ev) {
    var trigger = ev.target.closest('[data-action="open-nav"]');
    if (!trigger) return;
    ev.preventDefault();
    if (body.classList.contains('m-nav-open')) closeNav(); else openNav();
  });


  /* ── Header + FAB scroll behaviour ──────────────────────────────── */
  // One scroll listener drives:
  //   .is-scrolled on header  (after 80 px scrolled)
  //   .is-hidden  on header   (when scrolling down past 240 px)
  //   .m-fab--hidden          (mirrors header's hide rule)
  // Throttle by rAF to keep scroll smooth on mid-range Android.
  var header = document.querySelector('.site-header');
  var lastScrollY = window.pageYOffset || 0;
  var ticking = false;
  function onScroll() {
    var y = window.pageYOffset || 0;
    var scrolled = y > 80;
    var goingDown = y > lastScrollY && y > 240;
    if (header) {
      header.classList.toggle('is-scrolled', scrolled);
      header.classList.toggle('is-hidden', goingDown);
    }
    document.querySelectorAll('.m-fab').forEach(function (fab) {
      fab.classList.toggle('m-fab--hidden', goingDown);
    });
    var sticky = document.querySelector('[data-sticky-cta]');
    if (sticky && !sticky.dataset.dismissed) {
      // Show after user has scrolled past one trip (~600 px) and only
      // when the page is scrolling DOWN-or-paused — slide it back when
      // scrolling up so it's not a constant attention sink.
      var shouldShow = y > 600 && !goingDown;
      sticky.classList.toggle('m-sticky-cta--hidden', !shouldShow);
      if (shouldShow) sticky.removeAttribute('hidden');
    }
    lastScrollY = y;
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });


  /* ── FAB intents ────────────────────────────────────────────────── */
  document.addEventListener('click', function (ev) {
    var fab = ev.target.closest('.m-fab');
    if (!fab) return;
    var action = fab.dataset.action;
    if (action === 'scroll-top') {
      ev.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (action === 'open-sheet' && fab.dataset.sheetId) {
      ev.preventDefault();
      openSheet(fab.dataset.sheetId);
    } else if (action === 'search-sheet') {
      // Opens the global search sheet if present, else routes to /
      var globalSearchSheet = document.getElementById('searchSheet');
      if (globalSearchSheet) {
        ev.preventDefault();
        openSheet('searchSheet');
      }
      // else: let default <a href="/"> navigation happen.
    }
  });


  /* ── Sticky CTA dismiss + persistence ───────────────────────────── */
  // Per-session dismissal — cookie ttl 1 day so a return user the next
  // day sees it again (otherwise we'd permanently hide the strongest
  // CTA after one accidental tap).
  var STICKY_DISMISS_COOKIE = 'sticky_cta_dismissed';
  function readCookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
    return m ? decodeURIComponent(m[1]) : '';
  }
  if (readCookie(STICKY_DISMISS_COOKIE) === '1') {
    document.querySelectorAll('[data-sticky-cta]').forEach(function (el) {
      el.dataset.dismissed = '1';
      el.setAttribute('hidden', '');
    });
  }
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('[data-sticky-cta-dismiss]');
    if (!btn) return;
    var sticky = btn.closest('[data-sticky-cta]');
    if (!sticky) return;
    sticky.dataset.dismissed = '1';
    sticky.classList.add('m-sticky-cta--hidden');
    setTimeout(function () { sticky.setAttribute('hidden', ''); }, 250);
    document.cookie = STICKY_DISMISS_COOKIE +
      '=1; Path=/; Max-Age=86400; SameSite=Lax';
  });


  /* ── Web Share API ──────────────────────────────────────────────── */
  // Triggered by any element with [data-share-current]. Optional
  // attributes data-share-title / data-share-text override the page
  // <title> + meta description fallbacks. URL gets a utm_source=share
  // query so attribution surfaces in analytics. Falls back to clipboard
  // copy with a toast — the success path on iOS Safari (which has
  // navigator.share) doesn't show the toast since the OS sheet already
  // confirms the action.
  function readMeta(name) {
    var el = document.querySelector('meta[name="' + name + '"]');
    return el ? el.getAttribute('content') || '' : '';
  }
  function withShareUtm(url) {
    try {
      var u = new URL(url, window.location.origin);
      if (!u.searchParams.has('utm_source')) {
        u.searchParams.set('utm_source', 'share');
      }
      return u.toString();
    } catch (e) { return url; }
  }
  function notify(msg, type) {
    if (window.toast && typeof window.toast.show === 'function') {
      window.toast.show(msg, { type: type || 'info' });
    }
  }
  function shareCurrent(opts) {
    opts = opts || {};
    var title = opts.title || document.title || 'Prevozni';
    var text = opts.text || readMeta('description') || '';
    var url = withShareUtm(opts.url || window.location.href);

    if (navigator.share) {
      return navigator.share({ title: title, text: text, url: url })
        .catch(function (err) {
          // AbortError = user dismissed the sheet — silent. Anything
          // else falls through to clipboard.
          if (err && err.name === 'AbortError') return;
          return clipboardCopy(url);
        });
    }
    return clipboardCopy(url);
  }
  function clipboardCopy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () {
        notify('Link copied', 'success');
      }, function () {
        notify('Copy failed', 'error');
      });
    }
    // Last-ditch fallback for old WebViews — synchronous selection +
    // execCommand. Resolves immediately since there's no async path.
    try {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      notify('Link copied', 'success');
    } catch (e) {
      notify('Copy failed', 'error');
    }
    return Promise.resolve();
  }
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('[data-share-current]');
    if (!btn) return;
    ev.preventDefault();
    shareCurrent({
      title: btn.dataset.shareTitle,
      text: btn.dataset.shareText,
      url: btn.dataset.shareUrl,
    });
  });
  // Expose so other scripts can call it without re-importing.
  window.prevozniShareCurrent = shareCurrent;


  /* ── Connection-aware map opt-out ───────────────────────────────── */
  // Slow-2g / 2g effective type → flag the map containers as static so
  // the eager Leaflet loader bails out and the user gets a "Tap to
  // load map" CTA instead of 200KB of tile traffic. Honours the
  // operator-set preference via the `Save-Data: on` header where
  // available too.
  var conn = navigator.connection || navigator.mozConnection
    || navigator.webkitConnection;
  function isSlowConnection() {
    if (!conn) return false;
    if (conn.saveData) return true;
    var t = conn.effectiveType || '';
    return t === 'slow-2g' || t === '2g';
  }
  function flagSlowMaps() {
    if (!isSlowConnection()) return;
    var maps = document.querySelectorAll('.city-map, .stop-hero__map');
    maps.forEach(function (m) {
      if (m.dataset.staticMap === '1') return;
      m.dataset.staticMap = '1';
      // Replace the Leaflet target so its initialiser sees a non-empty
      // container and bails (or, if it runs anyway, our CSS hides it).
      var cta = document.createElement('button');
      cta.type = 'button';
      cta.className = 'static-map-cta';
      cta.textContent = '🗺  Tap to load map';
      cta.setAttribute('aria-label', 'Load interactive map');
      cta.addEventListener('click', function () {
        delete m.dataset.staticMap;
        // Surface the original Leaflet div so its lazy loader picks up.
        cta.remove();
        // Trigger a synthetic intersection observer to wake the loader.
        m.dispatchEvent(new Event('mobile-load-map', { bubbles: true }));
      });
      m.appendChild(cta);
    });
  }
  // Run after DOMContentLoaded so the map containers are in the tree.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', flagSlowMaps);
  } else {
    flagSlowMaps();
  }


  /* ── Tap-feedback haptics ───────────────────────────────────────── */
  // Tiny vibration on save / share success — Android Chrome supports
  // navigator.vibrate(); iOS Safari ignores. Other browsers throw, so
  // wrap in try.
  function haptic(ms) {
    try {
      if (navigator.vibrate) navigator.vibrate(ms || 10);
    } catch (e) { /* swallow */ }
  }
  window.prevozniHaptic = haptic;


  /* ── Prose collapse toggle (P28 mobile polish) ────────────────────
     The .seo-block__content[data-collapse="1"] starts clipped via CSS
     mask-gradient on mobile; tapping the .seo-block__more button (also
     hidden on desktop) flips data-collapse to "0" and updates the
     button copy + aria-expanded. Delegated so any future seo-block
     instance picks it up automatically. */
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('[data-collapse-toggle]');
    if (!btn) return;
    var block = btn.closest('.seo-block');
    if (!block) return;
    var content = block.querySelector('.seo-block__content');
    if (!content) return;
    var expanded = content.getAttribute('data-collapse') === '0';
    content.setAttribute('data-collapse', expanded ? '1' : '0');
    btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    // Localised copy comes from data-* attributes set by the template;
    // when missing we keep the original button text rather than guess
    // a translation client-side.
    var moreLabel = btn.dataset.moreLabel || btn.textContent.trim();
    var lessLabel = btn.dataset.lessLabel || moreLabel;
    btn.textContent = expanded ? moreLabel : lessLabel;
  });
})();
