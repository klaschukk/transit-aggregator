/* Prevozni service worker — minimal offline fallback + static cache.
   Strategy:
     * Static assets (CSS, SVG, manifest, favicons) → cache-first, 7-day TTL.
     * HTML pages → network-first, fall back to cached last-seen page or
       the offline shell if both fail.
     * API + /health → network only (never cache — they are data).
   Bumped version invalidates ALL caches: change the CACHE number on
   every deploy to force cold refresh. */

const CACHE = 'prevozni-v2';
const OFFLINE_URL = '/offline.html';
const STATIC_SHELL = [
  OFFLINE_URL,
  '/static/site.webmanifest',
  '/static/favicon/favicon.svg',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(STATIC_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE).map((n) => caches.delete(n)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Never cache API calls or health checks
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') return;

  // Static assets: cache-first
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(req, clone));
          }
          return res;
        });
      })
    );
    return;
  }

  // HTML navigation: network-first, fall back to cache, then offline shell
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(req, clone));
          }
          return res;
        })
        .catch(() =>
          caches.match(req).then((cached) => cached || caches.match(OFFLINE_URL))
        )
    );
  }
});
