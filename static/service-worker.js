// Service Worker to intercept CWA avatar requests
self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
  return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = event.request.url;
  
  // Intercept CWA avatar requests
  if (url.includes('null.jar') || url.includes('vhg.cmp.uea.ac.uk')) {
    console.log('Intercepting CWA request:', url);
    
    // Determine which avatar to load
    let avatarName = 'anna'; // default
    
    // Try to extract avatar name from URL or use stored preference
    if (url.includes('anna')) avatarName = 'anna';
    else if (url.includes('pablo')) avatarName = 'pablo';
    else if (url.includes('marc')) avatarName = 'marc';
    
    // Create new request to local file
    const newUrl = new URL(`/static/avatars/${avatarName}.jar`, self.location.origin);
    
    event.respondWith(
      fetch(newUrl).catch(error => {
        console.error('Failed to load avatar:', error);
        return new Response('', { status: 404 });
      })
    );
  }
});