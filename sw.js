const CACHE   = 'kw-v2';
const PENDING = 'kw-pending-v1';

// Only CDN resources are precached — immutable versioned URLs, safe to cache forever.
// Own-origin files (index.html, manifest.json etc) use network-first so updates
// are picked up immediately without bumping a cache version constant.
const CDN_PRECACHE = [
  'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js',
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(CDN_PRECACHE)));
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
  // Share target POST — intercept, store file, redirect
  if (event.request.method === 'POST') {
    const url = new URL(event.request.url);
    if (url.pathname.endsWith('/share-target')) {
      event.respondWith(handleShare(event.request, url));
    }
    return;
  }

  const url = new URL(event.request.url);

  // CDN resources: cache-first (versioned URLs, never change)
  if (url.hostname !== self.location.hostname) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request))
    );
    return;
  }

  // Own origin: network-first, cache as offline fallback.
  // Any push to GitHub is picked up on the next page load without reinstalling the PWA.
  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (response.ok) {
          caches.open(CACHE).then(c => c.put(event.request, response.clone()));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
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
