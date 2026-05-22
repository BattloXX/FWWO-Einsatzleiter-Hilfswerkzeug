/* Service Worker – PWA Offline Cache */
const CACHE = 'fwwo-v1';
const PRECACHE = [
  '/',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/js/alpine.min.js',
  '/static/js/htmx.min.js',
  '/static/js/sortable.min.js',
  '/static/manifest.webmanifest',
  '/login',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // Never intercept WebSocket or API calls
  if (url.pathname.startsWith('/ws/') || url.pathname.startsWith('/api/')) return;
  // Network-first for HTML pages, cache-first for static assets
  if (e.request.destination === 'document' || url.pathname === '/') {
    e.respondWith(
      fetch(e.request).catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request))
    );
  }
});

// Push notification handler
self.addEventListener('push', e => {
  if (!e.data) return;
  let data;
  try { data = JSON.parse(e.data.text()); } catch { data = { title: 'FF Wolfurt', body: e.data.text() }; }
  e.waitUntil(
    self.registration.showNotification(data.title || 'FF Wolfurt', {
      body: data.body || '',
      icon: '/static/img/logo.png',
      badge: '/static/img/badge.png',
      data: { url: data.url || '/' },
      requireInteraction: true,
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = e.notification.data?.url || '/';
  e.waitUntil(clients.openWindow(url));
});
