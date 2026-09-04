const CACHE = "halal-v1";
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(["/"])).then(()=>self.skipWaiting())
  );
});
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request)).catch(()=>caches.match("/"))
  );
});
