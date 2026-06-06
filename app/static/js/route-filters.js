/* route-filters.js — trip list controls on /rute/<slug>/ and /voznja/.
 *
 * All trip cards are server-rendered (good for SEO); this script only
 * shows/hides and reorders the existing DOM nodes. Three single-select
 * chip groups drive it:
 *   #timeFilter    — time-of-day window (data-from / data-to hours)
 *   #carrierFilter — single operator (data-carrier; empty = all)
 *   #sortChips     — sort key (data-sort: time | price | duration)
 *
 * Cards expose data-hour, data-price, data-duration, data-operator.
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

  var fromH = 0, toH = 24, carrier = '', sortKey = 'time';

  function num(c, attr) { return parseInt(c.dataset[attr], 10) || 0; }

  function inTime(c) {
    if (fromH === 0 && toH === 24) return true;
    var h = num(c, 'hour');
    return fromH > toH ? (h >= fromH || h < toH) : (h >= fromH && h < toH);
  }

  function apply() {
    var visible = 0;
    cards.forEach(function (c) {
      var show = inTime(c) && (!carrier || c.dataset.operator === carrier);
      c.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // Reorder the DOM. 'time' restores the server order (by departure).
    var order = original.slice();
    if (sortKey === 'price') {
      order.sort(function (a, b) { return num(a, 'price') - num(b, 'price'); });
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
  wire('carrierFilter', function (b) { carrier = b.dataset.carrier || ''; });
  wire('sortChips', function (b) { sortKey = b.dataset.sort; });
})();
