// Service Worker for Claw Assistant PWA
const CACHE_NAME = 'claw-v1';
const urlsToCache = ['/', '/chat', '/dashboard', '/reminders'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};
  const options = {
    body: data.body || 'New message from your AI',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-192.png',
    vibrate: [200, 100, 200],
    tag: data.type || 'default',
    data: data,
    actions: [
      { action: 'open', title: 'Open' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };

  if (data.type === 'alarm') {
    options.vibrate = [500, 200, 500, 200, 500];
    options.requireInteraction = true;
    options.tag = 'alarm';
  }

  event.waitUntil(
    self.registration.showNotification(data.title || '🦞 Claw Assistant', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow('/chat'));
});
