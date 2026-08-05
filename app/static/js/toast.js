/* Prevozni toast notifications — minimal API, zero deps.
 *
 * Usage:
 *   toast.show('Saved');
 *   toast.show('Switched to EUR', {type: 'info', duration: 2500});
 *   toast.show('Network failed', {type: 'error'});
 *
 * Types map to a single brand-tinted accent — green=success, teal=info,
 * amber=warning, red=error. Same shape, different left border + icon
 * colour so a quick glance reads the severity without reading the text.
 *
 * Stacks: up to 3 visible; new ones push the oldest into a fade-out.
 *
 * Reduced-motion: respects prefers-reduced-motion — slide-in becomes a
 * fade-only, fade-out becomes a single instant remove.
 */
(function (global) {
  'use strict';

  var ROOT_ID = 'prevozni-toast-root';
  var MAX_VISIBLE = 3;
  var DEFAULT_DURATION = 3000;

  function ensureRoot() {
    var root = document.getElementById(ROOT_ID);
    if (root) return root;
    root = document.createElement('div');
    root.id = ROOT_ID;
    root.setAttribute('role', 'region');
    root.setAttribute('aria-label',
      document.body.dataset.i18nNotifications || 'Notifications');
    root.setAttribute('aria-live', 'polite');
    document.body.appendChild(root);
    return root;
  }

  function trim(root) {
    while (root.children.length > MAX_VISIBLE) {
      root.removeChild(root.firstElementChild);
    }
  }

  function show(message, opts) {
    if (!message) return null;
    opts = opts || {};
    var type = opts.type || 'success';
    if (['success', 'info', 'warning', 'error'].indexOf(type) === -1) {
      type = 'info';
    }
    var duration = typeof opts.duration === 'number'
      ? opts.duration : DEFAULT_DURATION;

    var root = ensureRoot();
    var el = document.createElement('div');
    el.className = 'toast toast--' + type;
    // role=status (polite) for non-error; alert (assertive) for error so
    // screen readers interrupt the current utterance only on real failures.
    el.setAttribute('role', type === 'error' ? 'alert' : 'status');
    el.textContent = String(message);

    root.appendChild(el);
    trim(root);

    // Trigger entry animation on next frame (so the .is-visible class
    // change actually transitions instead of being applied with the
    // initial layout).
    requestAnimationFrame(function () {
      el.classList.add('toast--visible');
    });

    if (duration > 0) {
      setTimeout(function () { dismiss(el); }, duration);
    }

    return el;
  }

  function dismiss(el) {
    if (!el || !el.parentNode) return;
    el.classList.remove('toast--visible');
    el.classList.add('toast--leaving');
    // Remove after the CSS transition (220ms) — or immediately if the
    // user prefers reduced motion (the CSS sets transition: none in
    // that case, so the fade-out already completed).
    setTimeout(function () {
      if (el && el.parentNode) el.parentNode.removeChild(el);
    }, 240);
  }

  // Click-to-dismiss anywhere on a toast — common pattern users expect.
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest('.toast');
    if (t) dismiss(t);
  });

  global.toast = { show: show, dismiss: dismiss };
})(window);
