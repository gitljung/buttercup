// Stark igen: offline-cache sa sidan funkar pa gymmet utan tackning.
const C = 'stark-igen-v60';
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './fighters/kent.webp', './fighters/bettan.webp', './fighters/pappa.webp', './fighters/sussie.webp', './hasse.webp', './ex/hasse/bojdrodd.webp', './ex/hasse/highpull.webp', './ex/hasse/highpull2.webp', './ex/hasse/gobletutfall.webp', './ex/hasse/strictpress.webp', './ex/hasse/gymbg.webp', './ex/hasse/tahav.webp', './ex/hasse/rdl.webp', './ex/hasse/golvpress.webp', './ex/hasse/situp.webp', './hasse/synth80.mp3', './ex/hasse/rotthruster.webp', './ex/hasse/dlhalo.webp', './ex/hasse/lungepress.webp', './ex/hasse/pullrot.webp', './ex/hasse/crosslunge.webp', './ex/hasse/gorillaswing4.webp', './ex/hasse/axelkast3.webp', './ex/hasse/pullover4.webp', './ex/hasse/squatpressout5.webp', './ex/hasse/utfallhalo3.webp', './ex/hasse/swing.webp', './ex/hasse/goblet.webp', './ex/hasse/gobletpress.webp', './ex/hasse/dans3.webp'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url);
  // sidan: natet forst (nya versioner), cache som reserv. Typsnitt m.m.: cache forst.
  if (u.origin === location.origin) {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); return res; }).catch(() => caches.match(r).then(m => m || caches.match('./'))));
  } else if (/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) {
    e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); return res; })));
  }
});
