// Hasses Hälsoresa: offline-cache sa sidan funkar pa gymmet utan tackning.
const C = 'halsoresa-633e8548';
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./hasse.webp", "./ex/manifest.json", "./ex/hasse/axelkast.webp", "./ex/hasse/axelkast3.webp", "./ex/hasse/bojdrodd.webp", "./ex/hasse/crosslunge.webp", "./ex/hasse/dans3.webp", "./ex/hasse/dlhalo.webp", "./ex/hasse/goblet.webp", "./ex/hasse/gobletpress.webp", "./ex/hasse/gobletutfall.webp", "./ex/hasse/gorillaswing.webp", "./ex/hasse/gorillaswing3.webp", "./ex/hasse/gorillaswing4.webp", "./ex/hasse/gymbg.webp", "./ex/hasse/highpull.webp", "./ex/hasse/highpull2.webp", "./ex/hasse/lungepress.webp", "./ex/hasse/pullover.webp", "./ex/hasse/pullover2.webp", "./ex/hasse/pullover3.webp", "./ex/hasse/pullover4.webp", "./ex/hasse/pullrot.webp", "./ex/hasse/rotthruster.webp", "./ex/hasse/squatpressout.webp", "./ex/hasse/squatpressout3.webp", "./ex/hasse/squatpressout4.webp", "./ex/hasse/squatpressout5.webp", "./ex/hasse/strictpress.webp", "./ex/hasse/swing.webp", "./ex/hasse/utfallhalo.webp", "./ex/hasse/utfallhalo3.webp", "./hasse/hej1.mp3", "./hasse/hej2.mp3", "./hasse/hej3.mp3", "./hasse/hej4.mp3", "./hasse/hej5.mp3", "./hasse/hej6.mp3", "./hasse/hej7.mp3", "./hasse/korvi.mp3", "./hasse/synth80.mp3", "./hasse/tempel1.mp3", "./hasse/tempel2.mp3", "./hasse/vibe.mp3"];
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
