/* SW kill-switch — unregisters itself and wipes caches on every install.
   Keep this as /sw.js until all clients have self-unregistered (track via
   Umami "sw-killed" events), then restore normal SW from git. */
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => caches.delete(k)));
    await self.registration.unregister();
    const clients = await self.clients.matchAll({ type: 'window' });
    clients.forEach((c) => c.navigate(c.url));
  })());
});

self.addEventListener('fetch', () => {});
