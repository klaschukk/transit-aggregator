/* connection-timeline.js — plays the Rome2Rio-style draw-in the moment
 * each connection card's journey strip (dot–line–bus–dot–line–bus–dot)
 * scrolls into view. Purely an entrance effect: .connection-card__timeline
 * already renders fully drawn without this script (see its CSS — the
 * fill/bus default state IS the finished state), so a page that never
 * runs this JS, or a visitor with prefers-reduced-motion, still sees a
 * complete, correct timeline — just without the one-time animation.
 */
(function () {
  'use strict';

  var timelines = document.querySelectorAll('.connection-card__timeline');
  if (!timelines.length || !('IntersectionObserver' in window)) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('connection-card__timeline--animate');
      io.unobserve(entry.target);
    });
  }, { threshold: 0.4 });

  timelines.forEach(function (el) { io.observe(el); });
})();
