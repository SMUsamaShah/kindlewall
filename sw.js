const CACHE   = 'kw-v2'; // bumped from v1 — clears old cache on update
const PENDING = 'kw-pending-v1';

const PRECACHE = [
  './',
  './manifest.json',
  './icon.svg',
  'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js',
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => keys.filter(k => k !== CACHE && k !== PENDING))
      .then(old  => Promise.all(old.map(k => caches.delete(k))))
      .then(()   => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  // Share target: store file in cache, redirect to app
  if (event.request.method === 'POST') {
    const url = new URL(event.request.url);
    if (url.pathname.endsWith('/share-target')) {
      event.respondWith(handleShare(event.request, url));
    }
    return;
  }

  // Cache-first for everything else (makes app work offline)
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});

async function handleShare(request, url) {
  try {
    const formData = await request.formData();
    const file = formData.get('image');
    if (file) {
      const cache = await caches.open(PENDING);
      await cache.put('/pending-image', new Response(file, {
        headers: { 'Content-Type': file.type || 'image/jpeg' }
      }));
    }
  } catch (err) {
    console.error('[SW] Share handler error:', err);
  }

  const base = url.pathname.replace(/\/share-target$/, '/');
  return Response.redirect(url.origin + base + '?shared=1', 303);
}
