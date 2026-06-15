const PENDING = 'kw-pending-v1';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

self.addEventListener('fetch', event => {
  if (event.request.method !== 'POST') return;
  const url = new URL(event.request.url);
  if (!url.pathname.endsWith('/share-target')) return;
  event.respondWith(handleShare(event.request, url));
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

  // Works for both root hosting and sub-path (e.g. GitHub Pages)
  const base = url.pathname.replace(/\/share-target$/, '/');
  return Response.redirect(url.origin + base + '?shared=1', 303);
}
