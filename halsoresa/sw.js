// Hasses Hälsoresa: offline-cache sa sidan funkar pa gymmet utan tackning.
const C = 'halsoresa-a5feb843';
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./hasse.webp", "./ex/manifest.json", "./ex/hasse/atw_x2.webp", "./ex/hasse/axelkast.webp", "./ex/hasse/axelkast3_x2.webp", "./ex/hasse/bojdrodd_x2.webp", "./ex/hasse/chop_x2.webp", "./ex/hasse/crosslunge_x2.webp", "./ex/hasse/dans3_x2.webp", "./ex/hasse/dlhalo_x2.webp", "./ex/hasse/goblet_x2.webp", "./ex/hasse/gobletpress_x2.webp", "./ex/hasse/gobletutfall_x2.webp", "./ex/hasse/golvpress_x2.webp", "./ex/hasse/gorillaswing.webp", "./ex/hasse/gorillaswing4_x2.webp", "./ex/hasse/grave2_x2.webp", "./ex/hasse/gymbg.webp", "./ex/hasse/halo_x2.webp", "./ex/hasse/highpull.webp", "./ex/hasse/highpull2_x2.webp", "./ex/hasse/kneedrive_x2.webp", "./ex/hasse/kustbg.webp", "./ex/hasse/lungepress_x2.webp", "./ex/hasse/n_curlpress.webp", "./ex/hasse/n_hornpush.webp", "./ex/hasse/n_hpull.webp", "./ex/hasse/n_kchop.webp", "./ex/hasse/n_uprow.webp", "./ex/hasse/pullover.webp", "./ex/hasse/pullover4_x2.webp", "./ex/hasse/pullrot_x2.webp", "./ex/hasse/rdl.webp", "./ex/hasse/rdl2_x2.webp", "./ex/hasse/rotdrive_x2.webp", "./ex/hasse/rotthruster_x2.webp", "./ex/hasse/situp_x2.webp", "./ex/hasse/squatpressout.webp", "./ex/hasse/squatpressout5_x2.webp", "./ex/hasse/swing_x2.webp", "./ex/hasse/tahav_x2.webp", "./ex/hasse/tuck_x2.webp", "./ex/hasse/upover_x2.webp", "./ex/hasse/utfallhalo.webp", "./ex/hasse/utfallhalo3_x2.webp", "./ex/hasse/vattenbg.webp", "./hasse/gfunk.mp3", "./hasse/hej1.mp3", "./hasse/hej2.mp3", "./hasse/hej3.mp3", "./hasse/hej4.mp3", "./hasse/hej5.mp3", "./hasse/hej6.mp3", "./hasse/hej7.mp3", "./hasse/korvi.mp3", "./hasse/synth80.mp3", "./hasse/tempel1.mp3", "./hasse/tempel2.mp3", "./hasse/vibe.mp3"];
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
