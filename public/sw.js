/* Lettura offline: le pagine visitate e le immagini restano disponibili.
   Cambia VERSION quando pubblichi contenuti nuovi. */
const VERSION = 'v2';
const CACHE = 'pensieri-muti-' + VERSION;
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(
  caches.keys().then((k) => Promise.all(k.filter((x) => x !== CACHE).map((x) => caches.delete(x)))).then(() => self.clients.claim())));
self.addEventListener('fetch', (e) => {
  const r = e.request, url = new URL(r.url);
  if (r.method !== 'GET' || url.origin !== location.origin) return;
  const stat = /\.(jpe?g|png|svg|webp|woff2?|css|js)$/i.test(url.pathname);
  e.respondWith(stat
    ? caches.match(r).then((h) => h || fetch(r).then((res) => { const c = res.clone(); caches.open(CACHE).then((x) => x.put(r, c)); return res; }))
    : fetch(r).then((res) => { const c = res.clone(); caches.open(CACHE).then((x) => x.put(r, c)); return res; }).catch(() => caches.match(r)));
});
