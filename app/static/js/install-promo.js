/* install-promo.js — PWA install nudge.
 *
 * Decision tree:
 *   already installed (display-mode: standalone)  → nothing
 *   user dismissed in last 30 days                → nothing
 *   visit_count < 3                               → nothing
 *   Chrome/Edge fires beforeinstallprompt         → show banner, on accept call prompt()
 *   iOS Safari (no API)                           → show banner with "Install" that opens
 *                                                   the Add-to-Home-Screen hint modal
 *   other browsers                                → nothing
 *
 * Storage keys (localStorage):
 *   prevozni.install.dismissed_at   ISO date or ''
 *   prevozni.install.visits         integer
 *   prevozni.install.installed      '1' when appinstalled fires
 */
(function () {
  'use strict';

  var VISITS_KEY = 'prevozni.install.visits';
  var DISMISS_KEY = 'prevozni.install.dismissed_at';
  var INSTALLED_KEY = 'prevozni.install.installed';
  var DISMISS_COOLDOWN_MS = 30 * 24 * 60 * 60 * 1000; // 30 days
  var VISIT_THRESHOLD = 3;

  function store() {
    try { return window.localStorage; } catch (e) { return null; }
  }
  function get(k) {
    var s = store(); return s ? s.getItem(k) : null;
  }
  function set(k, v) {
    var s = store(); if (s) try { s.setItem(k, v); } catch (e) {}
  }

  function bumpVisit() {
    var n = parseInt(get(VISITS_KEY) || '0', 10) || 0;
    set(VISITS_KEY, String(n + 1));
    return n + 1;
  }

  function recentlyDismissed() {
    var ts = get(DISMISS_KEY);
    if (!ts) return false;
    var d = Date.parse(ts);
    if (isNaN(d)) return false;
    return (Date.now() - d) < DISMISS_COOLDOWN_MS;
  }

  function isStandalone() {
    if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) return true;
    if (window.navigator && window.navigator.standalone === true) return true;   // iOS
    if (get(INSTALLED_KEY) === '1') return true;
    return false;
  }

  function isIOS() {
    var ua = window.navigator.userAgent || '';
    return /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
  }

  function show(banner) {
    banner.setAttribute('data-visible', 'true');
  }
  function hide(banner) {
    banner.setAttribute('data-visible', 'false');
  }

  function openIOSModal(modal) {
    if (!modal) return;
    modal.removeAttribute('hidden');
    var focusable = modal.querySelector('button');
    if (focusable) focusable.focus();
  }
  function closeIOSModal(modal) {
    if (modal) modal.setAttribute('hidden', '');
  }

  function init() {
    var banner = document.getElementById('installBanner');
    if (!banner) return;
    var modal = document.getElementById('installModal');
    var acceptBtn = document.getElementById('installAccept');
    var dismissBtn = document.getElementById('installDismiss');
    var modalClose = document.getElementById('installModalClose');

    if (isStandalone()) return;

    var visits = bumpVisit();
    if (visits < VISIT_THRESHOLD) return;
    if (recentlyDismissed()) return;

    var deferredPrompt = null;

    window.addEventListener('beforeinstallprompt', function (e) {
      e.preventDefault();
      deferredPrompt = e;
      show(banner);
    });

    window.addEventListener('appinstalled', function () {
      set(INSTALLED_KEY, '1');
      hide(banner);
      closeIOSModal(modal);
    });

    // iOS has no beforeinstallprompt; show the banner immediately so the
    // CTA can open the Add-to-Home-Screen instructions.
    if (isIOS()) show(banner);

    if (acceptBtn) acceptBtn.addEventListener('click', function () {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function (choice) {
          if (choice && choice.outcome === 'dismissed') {
            set(DISMISS_KEY, new Date().toISOString());
          }
          deferredPrompt = null;
          hide(banner);
        });
      } else if (isIOS()) {
        openIOSModal(modal);
      } else {
        hide(banner);
      }
    });

    if (dismissBtn) dismissBtn.addEventListener('click', function () {
      set(DISMISS_KEY, new Date().toISOString());
      hide(banner);
    });

    if (modalClose) modalClose.addEventListener('click', function () {
      closeIOSModal(modal);
    });
    if (modal) modal.addEventListener('click', function (e) {
      if (e.target === modal) closeIOSModal(modal);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
