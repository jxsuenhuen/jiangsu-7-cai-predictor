const CACHE='jiangsu-seven-v10.1';
const CORE=['./','./index.html','./styles.css?v=10','./app.js?v=10','./manifest.webmanifest?v=10','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('lottery-predictor-')||k.startsWith('jiangsu-seven-')).filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;
 const url=new URL(e.request.url);url.search='';const key=url.href;
 e.respondWith(fetch(e.request,{cache:'no-store'}).then(async r=>{if(r.ok){const c=await caches.open(CACHE);await c.put(key,r.clone())}return r}).catch(async()=>await caches.match(key)||await caches.match(e.request)||new Response('离线且未缓存，请联网后重试',{status:503})));
});
