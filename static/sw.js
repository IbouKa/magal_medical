/* ============================================================
   Service Worker — Magal Medical
   Cache network-first + fallback offline
   ============================================================ */
'use strict';

var CACHE_NAME = 'magal-v1';

var PRECACHE_URLS = [
  '/static/css/style.css',
  '/static/js/saisie.js',
  '/static/js/offline-saisie.js'
];

/* ---- Install : pre-cache static assets ---- */
self.addEventListener('install', function (e) {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return Promise.allSettled(
        PRECACHE_URLS.map(function (url) { return cache.add(url); })
      );
    })
  );
});

/* ---- Activate : purge old caches ---- */
self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE_NAME; })
            .map(function (k) { return caches.delete(k); })
      );
    }).then(function () { return self.clients.claim(); })
  );
});

/* ---- Fetch : network-first (same-origin), stale-while-revalidate (CDN) ---- */
self.addEventListener('fetch', function (e) {
  /* Only intercept GET */
  if (e.request.method !== 'GET') return;

  var url = new URL(e.request.url);

  /* ---- CDN / cross-origin : cache-first, then network ---- */
  if (url.origin !== self.location.origin) {
    e.respondWith(
      caches.open(CACHE_NAME).then(function (cache) {
        return cache.match(e.request).then(function (cached) {
          var networkFetch = fetch(e.request).then(function (resp) {
            if (resp && resp.status === 200) {
              cache.put(e.request, resp.clone());
            }
            return resp;
          }).catch(function () { return cached; });
          return cached || networkFetch;
        });
      })
    );
    return;
  }

  /* ---- Same-origin : network-first, cache fallback ---- */
  e.respondWith(
    fetch(e.request)
      .then(function (resp) {
        if (resp && resp.status === 200) {
          var clone = resp.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(e.request, clone);
          });
        }
        return resp;
      })
      .catch(function () {
        return caches.match(e.request);
      })
  );
});