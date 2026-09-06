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
        apply();
      });
    });
  }

  wire('timeFilter', function (b) { fromH = parseInt(b.dataset.from, 10); toH = parseInt(b.dataset.to, 10); });
  wire('modeFilter', function (b) { mode = b.dataset.mode || ''; });
  wire('carrierFilter', function (b) { carrier = b.dataset.carrier || ''; });
  wire('sortChips', function (b) { sortKey = b.dataset.sort; });
})();
