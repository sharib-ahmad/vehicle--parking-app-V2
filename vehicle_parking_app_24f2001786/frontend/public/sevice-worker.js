// This is a basic service worker. Its main purpose is to make the app installable.
// It doesn't perform any caching, which keeps things simple.

self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
});

self.addEventListener('fetch', (event) => {
  // The service worker is not intercepting network requests.
  // It only exists to satisfy the PWA criteria for installability.
});
