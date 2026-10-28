/* Service worker: il libro resta leggibile anche offline.
   Cambia VERSION ad ogni aggiornamento dei contenuti per svuotare la cache vecchia. */
const VERSION = 'v1';
const CACHE = 'pensieri-muti-' + VERSION;
const CORE = ['./', 'index.html', 'styles.css', 'app.js', 'data.js', 'favicon.svg', 'manifest.webmanifest'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return; // font Google ecc.: gestiti dal browser

  const isImage = /\.(jpe?g|png|svg|webp)$/i.test(url.pathname);
  if (isImage) {
    // immagini: prima la cache
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res;
    })));
  } else {
    // pagine, script, dati: prima la rete, cache come riserva offline
    e.respondWith(fetch(req).then((res) => {
      const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res;
    }).catch(() => caches.match(req).then((hit) => hit || caches.match('index.html'))));
  }
});
