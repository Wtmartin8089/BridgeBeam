self.addEventListener('install', event => {
  console.log('BridgeBeam service worker installed.');
  self.skipWaiting();
});
self.addEventListener('activate', event => {
  console.log('BridgeBeam service worker activated.');
});
self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});