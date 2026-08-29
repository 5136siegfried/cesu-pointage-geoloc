// Network-first pour le HTML (toujours la version la plus fraîche),
// cache-first pour le reste. Le cache ne sert de secours qu'hors-ligne.

const CACHE_NAME = 'cesu-pointage-v7';
const APP_SHELL = ['/static/index.html', '/static/manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) return; // jamais de cache sur l'API

  const estDocumentHtml = event.request.mode === 'navigate' || event.request.destination === 'document';

  if (estDocumentHtml) {
    // Network-first : toujours la version la plus fraîche si le réseau répond.
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Cache-first pour le reste (manifest, icônes) : change rarement, priorité vitesse.
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
