/* Review-prompt — show a sticky banner asking real customers to leave a
   review on their next visit, after they clicked Buy on a Bookaway link.
   The cookie `pending_review_route` is set in base.html's buy-click
   handler; this script reads it, gates on a 12h cooldown + per-route
   dismissal, and reveals the banner element from _review_prompt.html.

   Loaded with `defer` from base.html — runs once after DOM parsed,
   no work if the cookie isn't there. */
(function(){
  function readCookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  function writeCookie(name, value, maxAgeS) {
    document.cookie = name + '=' + encodeURIComponent(value)
      + '; path=/; max-age=' + maxAgeS + '; samesite=lax';
  }

  var raw = readCookie('pending_review_route');
  if (!raw) return;
  var data;
  try { data = JSON.parse(raw); } catch(e){ return; }
  if (!data || !data.slug) return;

  // Wait 12h after the click — don't ask DURING the trip.
  if ((Date.now() - (data.ts || 0)) / 3600000 < 12) return;
  if (readCookie('review_dismissed_' + data.slug) === '1') return;

  // Skip on the route's own page — form is already there.
  var path = location.pathname;
  if (path.indexOf('/rute/' + data.slug) !== -1) return;
  if (path.indexOf('/voznja/' + data.slug) !== -1) return;

  // Slug → "Beograd → Budva" — best-effort split, mostly cosmetic.
  function cap(p){ return p.charAt(0).toUpperCase() + p.slice(1); }
  var parts = data.slug.split('-');
  var fromTxt, toTxt;
  if (parts.length === 2) {
    fromTxt = cap(parts[0]); toTxt = cap(parts[1]);
  } else if (parts.length === 3) {
    fromTxt = cap(parts[0]); toTxt = cap(parts[1]) + ' ' + cap(parts[2]);
  } else {
    var mid = Math.floor(parts.length / 2);
    fromTxt = parts.slice(0, mid).map(cap).join(' ');
    toTxt   = parts.slice(mid).map(cap).join(' ');
  }

  var el = document.getElementById('reviewPrompt');
  if (!el) return;
  el.querySelector('[data-review-pair]').textContent = fromTxt + ' → ' + toTxt;
  el.querySelector('[data-review-cta]').setAttribute(
    'href', '/rute/' + data.slug + '/#reviews');
  el.removeAttribute('hidden');
  el.classList.remove('review-prompt--hidden');

  el.querySelector('[data-review-dismiss]').addEventListener('click', function(){
    writeCookie('review_dismissed_' + data.slug, '1', 60*60*24*90);
    el.classList.add('review-prompt--hidden');
    setTimeout(function(){ el.setAttribute('hidden', ''); }, 250);
  });
})();
