/* route-filters.js — trip list controls on /rute/<slug>/ and /voznja/.
 *
 * All trip cards are server-rendered (good for SEO); this script only
 * shows/hides and reorders the existing DOM nodes. Four single-select
 * chip groups drive it:
 *   #timeFilter    — time-of-day window (data-from / data-to hours)
 *   #modeFilter    — bus/train (data-mode; empty = all). Only rendered
 *                    when a route actually mixes modes.
 *   #carrierFilter — single operator (data-carrier; empty = all)
 *   #sortChips     — sort key (data-sort: time | price | duration)
 *
 * Cards expose data-hour, data-price, data-duration, data-operator, data-type.
 */
(function () {
  'use strict';

  var list = document.getElementById('tripList');
  if (!list) return;
  var cards = Array.prototype.slice.call(list.querySelectorAll('.trip-card'));
  if (!cards.length) return;

  var total = cards.length;
  var original = cards.slice();              // server order = by departure time
  var countEl = document.getElementById('tripCount');
  var visibleEl = document.getElementById('tripVisible');

  var fromH = 0, toH = 24, mode = '', carrier = '', sortKey = 'time';

  function num(c, attr) { return parseInt(c.dataset[attr], 10) || 0; }

  function inTime(c) {
    if (fromH === 0 && toH === 24) return true;
    var h = num(c, 'hour');
    return fromH > toH ? (h >= fromH || h < toH) : (h >= fromH && h < toH);
  }

  function apply() {
    var visible = 0;
    cards.forEach(function (c) {
      var show = inTime(c) && (!mode || c.dataset.type === mode) && (!carrier || c.dataset.operator === carrier);
      c.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // Reorder the DOM. 'time' restores the server order (by departure).
    var order = original.slice();
    if (sortKey === 'price') {
      /* Departures with no fare in our data must sort LAST, not first.
         num() returns 0 for a missing price, so "cheapest" was putting
         every unpriced trip at the top — 44 of 74 on Beograd–Novi Sad.
         It is the one sort a buyer clicks to compare money, and it could
         never answer that. The duration branch below already guarded the
         same way; price did not, and neither did any test. */
      order.sort(function (a, b) {
        return (num(a, 'price') || Infinity) - (num(b, 'price') || Infinity);
      });
    } else if (sortKey === 'duration') {
      order.sort(function (a, b) {
        return (num(a, 'duration') || Infinity) - (num(b, 'duration') || Infinity);
      });
    }
    order.forEach(function (c) { list.appendChild(c); });

    if (countEl && visibleEl) {
      countEl.hidden = (visible === total);
      visibleEl.textContent = visible;
    }
    var emptyEl = document.getElementById('filterEmpty');
    if (emptyEl) emptyEl.hidden = (visible !== 0);
  }

  /* Animated re-apply (FLIP): cards that stay glide to their new place,
     cards that appear fade in. Only cards near the screen are animated, so a
     74-trip list stays cheap; reduced motion or no Web Animations = instant. */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function near(r) { return r.bottom > -innerHeight && r.top < innerHeight * 2; }
  function flip() {
    if (reduce || !Element.prototype.animate) { apply(); return; }
    var before = new Map();
    cards.forEach(function (c) { if (c.style.display !== 'none') before.set(c, c.getBoundingClientRect().top); });
    apply();
    cards.forEach(function (c) {
      if (c.style.display === 'none') return;
      var r = c.getBoundingClientRect();
      if (!near(r)) return;
      if (before.has(c)) {
        var dy = before.get(c) - r.top;
        if (Math.abs(dy) > 1 && Math.abs(dy) < innerHeight * 1.5) {
          c.animate([{ transform: 'translateY(' + dy + 'px)' }, { transform: 'none' }],
                    { duration: 380, easing: 'cubic-bezier(.2,.8,.2,1)' });
        }
      } else {
        c.animate([{ opacity: 0, transform: 'translateY(10px) scale(.98)' }, { opacity: 1, transform: 'none' }],
                  { duration: 260, easing: 'ease-out' });
      }
    });
  }

  // Single-select chip group: highlight clicked, run setter, re-apply.
  function wire(groupId, setter) {
    var g = document.getElementById(groupId);
    if (!g) return;
    g.querySelectorAll('.time-chip').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var act = g.querySelector('.time-chip--active');
        if (act) act.classList.remove('time-chip--active');
        btn.classList.add('time-chip--active');
        setter(btn);
        flip();
      });
    });
  }

  wire('timeFilter', function (b) { fromH = parseInt(b.dataset.from, 10); toH = parseInt(b.dataset.to, 10); });
  wire('modeFilter', function (b) { mode = b.dataset.mode || ''; });
  wire('carrierFilter', function (b) { carrier = b.dataset.carrier || ''; });
  wire('sortChips', function (b) { sortKey = b.dataset.sort; });

  /* ── Live "departs in Xh Ym" on the next upcoming card ──
   * Only rendered on the "today" tab (list.dataset.now set server-side from
   * Belgrade wall-clock time at render — see intercity.py's
   * _belgrade_now_hhmm()). Ticks forward from that ONE server reading using
   * elapsed real time (Date.now() diff), never the visitor's own clock/
   * timezone, so a visitor in another timezone still sees Serbia-local
   * countdown. Re-scans on every filter/sort change (apply() calls it) so
   * "next" always reflects what's actually visible, not the full list. */
  var nowAttr = list.dataset.now;
  if (nowAttr && /^\d{2}:\d{2}$/.test(nowAttr)) {
    var baseMin = parseInt(nowAttr.slice(0, 2), 10) * 60 + parseInt(nowAttr.slice(3, 5), 10);
    var baseTs = Date.now();
    var countdownEl = null;
    var label = list.dataset.departsLabel || '';
    var unitH = list.dataset.unitH || 'h';
    var unitMin = list.dataset.unitMin || 'min';

    function updateCountdown() {
      var nowMin = baseMin + Math.floor((Date.now() - baseTs) / 60000);
      var next = null, bestDelta = Infinity;
      cards.forEach(function (c) {
        if (c.style.display === 'none') return;
        var timeEl = c.querySelector('.trip-card__time--depart');
        var dep = timeEl && timeEl.firstChild ? timeEl.firstChild.textContent.trim() : '';
        if (!/^\d{2}:\d{2}$/.test(dep)) return;
        var depMin = parseInt(dep.slice(0, 2), 10) * 60 + parseInt(dep.slice(3, 5), 10);
        // Window capped at 3h — a countdown reading "in 14h" isn't urgency,
        // it's noise; the badge should only appear when it's actually useful.
        var delta = depMin - nowMin;
        if (delta > 0 && delta <= 180 && delta < bestDelta) { bestDelta = delta; next = timeEl; }
      });
      if (countdownEl && countdownEl.parentNode !== next) {
        countdownEl.remove();
        countdownEl = null;
      }
      if (next) {
        if (!countdownEl) {
          countdownEl = document.createElement('span');
          countdownEl.className = 'trip-card__countdown';
          next.appendChild(countdownEl);
        }
        var h = Math.floor(bestDelta / 60), m = bestDelta % 60;
        countdownEl.textContent = label + ' ' + (h ? h + unitH + ' ' : '') + m + unitMin;
      }
    }

    updateCountdown();
    setInterval(updateCountdown, 30000);
    // apply() already exists above; wrap it so every filter/sort change
    // re-evaluates which card is "next" among what's now visible.
    var _apply = apply;
    apply = function () { _apply(); updateCountdown(); };
  }
})();
