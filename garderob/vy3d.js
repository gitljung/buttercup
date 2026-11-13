// 3D-vy för garderobskonfiguratorn. Bygger skivorna som lådor ur konfig + genererade delar.
// Koordinater (mm): x = bredd från vänster, y = djup från front, z = höjd från golv. three: Y upp.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const el = document.querySelector('#vy3d');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
el.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xf3ecdb);
const cam = new THREE.PerspectiveCamera(32, 1, 0.05, 100);
const ctl = new OrbitControls(cam, renderer.domElement); ctl.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x9a8a70, 1.2));
const sol = new THREE.DirectionalLight(0xffffff, 2.0); sol.position.set(-2.5, 4, 4); sol.castShadow = true;
sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -5, right: 5, top: 5, bottom: -2 }); sol.shadow.bias = -0.0005;
scene.add(sol);
const fyll = new THREE.DirectionalLight(0xfff4e0, 0.9); fyll.position.set(1.5, 1.6, 5); scene.add(fyll);
const golv = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.MeshStandardMaterial({ color: 0xd9cfbd, roughness: 1 }));
golv.rotation.x = -Math.PI / 2; golv.receiveShadow = true; scene.add(golv);
const V = new THREE.Group(); V.rotation.x = -Math.PI / 2; V.scale.setScalar(0.001); scene.add(V);
// V: (x, y, z)mm -> three (x, z, -y)  => fronten (y=0) vänd mot kameran

const M = {
  stomme: new THREE.MeshStandardMaterial({ color: 0xe8cf9f, roughness: 0.75 }),
  hylla: new THREE.MeshStandardMaterial({ color: 0xf0dcb2, roughness: 0.75 }),
  lada: new THREE.MeshStandardMaterial({ color: 0xbdb5a6, roughness: 0.8 }),
  dorr: new THREE.MeshStandardMaterial({ color: 0xa8774a, roughness: 0.6, transparent: true, opacity: 1 }),
  rygg: new THREE.MeshStandardMaterial({ color: 0xc9a46c, roughness: 0.9 }),
  regel: new THREE.MeshStandardMaterial({ color: 0xa9a49a, roughness: 0.8 }),
  stang: new THREE.MeshStandardMaterial({ color: 0x9a9a9a, metalness: 0.8, roughness: 0.3 }),
  klots: new THREE.MeshStandardMaterial({ color: 0x8fa3b8, roughness: 0.8 }),
  sockel: new THREE.MeshStandardMaterial({ color: 0xc8c2b6, roughness: 0.9 }),
  galler: new THREE.MeshStandardMaterial({ color: 0x777777, roughness: 0.6, wireframe: true }),
  vagg: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, transparent: true, opacity: 0.35, side: THREE.DoubleSide }),
  skiva: new THREE.MeshStandardMaterial({ color: 0x8a7f6e, roughness: 0.5 }),
  maskin: new THREE.MeshStandardMaterial({ color: 0x2b2b2b, roughness: 0.4, metalness: 0.3 }),
  hal8: new THREE.MeshBasicMaterial({ color: 0x1f4e8c }),
  hal5: new THREE.MeshBasicMaterial({ color: 0xc8321a }),
  kopp: new THREE.MeshBasicMaterial({ color: 0x2f7d32 }),
};
const kant = new THREE.LineBasicMaterial({ color: 0x5a4630, transparent: true, opacity: 0.45 });

function box(g, x0, x1, y0, y1, z0, z1, mat, namn) {
  const geo = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
  const m = new THREE.Mesh(geo, mat); m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  m.castShadow = m.receiveShadow = true; m.userData.namn = namn;
  m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), kant));
  g.add(m); return m;
}
// hål som små skivor på en yta. axel: 'x' | 'y' | 'z' (ytans normal)
const cyl = new THREE.CylinderGeometry(1, 1, 1, 16);
function hal(g, x, y, z, d, axel, mat) {
  const m = new THREE.Mesh(cyl, mat); m.scale.set(d / 2, 1.2, d / 2); m.position.set(x, y, z);
  if (axel === 'x') m.rotation.z = Math.PI / 2; else if (axel === 'z') m.rotation.x = Math.PI / 2;
  g.add(m);
}

let rot = null, dorrGrupp = [], frontGrupp = [], lage = { dorrar: 'oppna', hal: true }, forstaGang = true;

function bygg(ut) {
  if (rot) { V.remove(rot); rot.traverse(o => o.geometry && o.geometry !== cyl && o.geometry.dispose()); }
  rot = new THREE.Group(); V.add(rot); dorrGrupp = []; frontGrupp = [];
  if (ut.kok) return byggKok(ut);
  const sys = ut.moduler ? ut.sys : ut.konfig;
  const mods = ut.moduler ? ut.moduler.map(m => ({ ut: m.ut, x0: m.x0, nr: m.nr }))
    : [{ ut, x0: ut.konfig.nisch ? (ut.konfig.nisch.bredd - ut.konfig.bredd) / 2 : 0, nr: 1 }];
  const sock = sys.sockel || 0, gal = sys.galler || 0;
  const x0 = Math.min(...mods.map(m => m.x0)), x1 = Math.max(...mods.map(m => m.x0 + m.ut.konfig.bredd));
  const maxD = Math.max(...mods.flatMap(m => m.ut.konfig.skap.map(s => s.djup)));
  const hojd = Math.max(...mods.map(m => m.ut.konfig.hojd));
  if (sock) box(rot, x0, x1, 40, maxD, 0, sock, M.sockel, 'Sockel');
  modGrupper = mods.map(m => byggModul(m.ut, m.x0, sock, mods.length > 1 ? `M${m.nr} ` : '', m.nr, rot, 0));
  markera(window.__valdModul || valdModul);
  if (gal) box(rot, x0, x1, 0, maxD, sock + hojd, sock + hojd + gal, M.galler, 'Galler');
  if (sys.nisch && sys.nisch.bredd) {
    const nb = sys.nisch.bredd, nh = sys.nisch.hojd || sock + hojd + gal;
    box(rot, -60, 0, -30, maxD + 120, 0, nh, M.vagg, 'Nischvägg');
    box(rot, nb, nb + 60, -30, maxD + 120, 0, nh, M.vagg, 'Nischvägg');
  }
  satDorrar();
  const nyckel = mods.length + ':' + (x1 - x0);
  if (forstaGang || nyckel !== senast) { ram(x0, x1, sock + hojd + gal); forstaGang = false; senast = nyckel; }
}
let senast = '';

let modGrupper = [], valdModul = 0, markor = [];
const markMat = new THREE.MeshBasicMaterial({ color: 0xfbc021, transparent: true, opacity: 0.22, depthWrite: false });
function markera(nr) {
  valdModul = nr;
  markor.forEach(m => m.parent && m.parent.remove(m)); markor = [];
  if (!rot) return;
  modGrupper.filter(g => g.userData.nr === nr).forEach(g => {
    const k = g.userData.konfig, sock = g.userData.sock;
    const B = g.userData.bredd || k.bredd, D = k ? Math.max(...k.skap.map(s => s.djup)) : 580, Hh = k ? k.hojd : g.userData.hojd || 800;
    const geo = new THREE.BoxGeometry(B + 16, D + 40, Hh + 16);
    const mk = new THREE.Mesh(geo, markMat); mk.position.set(B / 2, D / 2 - 20, sock + Hh / 2);
    mk.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0xe0a000 })));
    mk.raycast = () => {};
    g.add(mk); markor.push(mk);
  });
}
// kök: rader i rummets plan (X, Y) -> V (x, y) = (X, Y); raden vriden rot grader, fronten ut = xdir vriden −90°
function byggKok(ut) {
  const T = Math.PI / 180;
  const grupper = ut.rader.map((r, ri) => {
    const a = r.rot * T, xd = [Math.cos(a), Math.sin(a)], n = [xd[1], -xd[0]];
    const g = new THREE.Group(); g.position.set(r.start[0] + r.yb * n[0], r.start[1] + r.yb * n[1], 0); g.rotation.z = a;
    rot.add(g); return g;
  });
  modGrupper = ut.moduler.map(m => {
    if (m.ut) return byggModul(m.ut, m.x0, m.z0, `${m.radId}-M${m.nr}${m.typ === 'vagg' ? 'V' : ''} `, m.nr, grupper[m.rad], m.y0);
    const g0 = new THREE.Group(); g0.position.set(m.x0, 0, 0); grupper[m.rad].add(g0);
    g0.userData = { nr: m.nr, konfig: null, sock: m.z0, bredd: m.bredd, hojd: 800 }; return g0;
  });
  (ut.extra3d || []).forEach(e => {
    const b = box(grupper[e.rad], e.x0, e.x1, e.y0, e.y1, e.z0, e.z1, M[e.mat] || M.stomme, e.namn);
    if (e.front) frontGrupp.push(b);
    if (e.mat === 'vagg') { b.castShadow = false; }
  });
  markera(window.__valdModul || valdModul);
  satDorrar();
  // kamera: över rummet snett uppifrån
  const pts = ut.rader.flatMap(r => { const a = r.rot * T; return [r.start, [r.start[0] + r.langd * Math.cos(a), r.start[1] + r.langd * Math.sin(a)]]; });
  const X0 = Math.min(...pts.map(p => p[0])), X1 = Math.max(...pts.map(p => p[0])), Y0 = Math.min(...pts.map(p => p[1])), Y1 = Math.max(...pts.map(p => p[1]));
  const nyckel = 'kok:' + ut.rader.length + ':' + X0 + ':' + X1 + ':' + Y0 + ':' + Y1;
  if (forstaGang || nyckel !== senast) {
    // från rummets öppna sida (min X), snett ovanifrån: ser fronterna på väggraderna
    const c = new THREE.Vector3((X0 + X1) / 2000 + 0.3, 0.7, -(Y0 + Y1) / 2000);
    ctl.target.copy(c);
    const R = Math.max(X1 - X0, Y1 - Y0) / 1000;
    cam.position.set(X0 / 1000 - R * 0.6, R * 1.0, c.z + R * 0.35); ctl.update();
    forstaGang = false; senast = nyckel;
  }
}
function byggModul(ut, ox, sock, pre, nr, foralder, oy) {
  const k = ut.konfig, T = k.T, W = k.bredd, med = !!k.dorrar;
  const g0 = new THREE.Group(); g0.position.x = ox; g0.position.y = oy || 0; foralder.add(g0);
  g0.userData = { nr, konfig: k, sock };
  let z = sock;
  k.skap.forEach(s => {
    const H = s.hojd, D = s.djup, rygg = s.bak === 'spar', ys = D - 25.5;
    const djHy = (rygg ? ys : D) - 2, g = g0, n = `${pre}Skåp ${s.nr}`;
    box(g, 0, T, 0, D, z, z + H, M.stomme, `${n} sida vänster`);
    box(g, W - T, W, 0, D, z, z + H, M.stomme, `${n} sida höger`);
    box(g, T, W - T, 2, D, z, z + T, M.stomme, `${n} botten`);
    box(g, T, W - T, 2, D, z + H - T, z + H, M.stomme, `${n} topp`);
    (s.fasta || (s.fast != null ? [s.fast] : [])).forEach(f => box(g, T, W - T, 0, rygg ? ys : D, z + f - T / 2, z + f + T / 2, M.stomme, `${pre}Fast hylla`));
    s.hyllor.forEach(m => box(g, T + 1, W - T - 1, 2, 2 + djHy, z + m + 4, z + m + 4 + T, M.hylla, `${pre}Ställbar hylla ${m}`));
    if (s.stang) {
      const st = new THREE.Mesh(new THREE.CylinderGeometry(12.5, 12.5, W - 2 * T, 20), M.stang);
      st.rotation.z = Math.PI / 2; st.position.set(W / 2, (rygg ? ys : D) / 2, z + s.stang); st.castShadow = true; st.userData.namn = `${pre}Klädstång`; g.add(st);
    }
    if (rygg) {
      box(g, T - 7, W - T + 7, ys, ys + 6.5, z + 13, z + H - 13, M.rygg, `${pre}Rygg 6,5`);
      [[T, T + 80], [H / 2 - 40, H / 2 + 40], [H - T - 80, H - T]].forEach(([a, b]) => box(g, T, W - T, D - 19, D, z + a, z + b, M.regel, `${pre}Regel bak`));
    }
    const inv = med ? 20 : 0;
    if (med && s.lador) {
      const KL = 200 + 260 * (s.lador - 1);
      box(g, T, T + 20, 10, 435, z + 75, z + 75 + KL, M.klots, `${pre}Distansklots`);
      box(g, W - T - 20, W - T, 10, 435, z + 75, z + 75 + KL, M.klots, `${pre}Distansklots`);
    }
    for (let i = 0; i < s.lador; i++) {
      const xa = T + 4 + inv, xb = W - T - 4 - inv, zb = z + T + 260 * i + 2, d0 = 4;
      box(g, xa, xb, d0, d0 + 15, zb, zb + 220, M.lada, `${pre}Låda ${i + 1} front`);
      box(g, xa + 2, xa + 17, d0 + 15, d0 + 15 + 410, zb + 15, zb + 215, M.lada, `${pre}Lådsida`);
      box(g, xb - 17, xb - 2, d0 + 15, d0 + 15 + 410, zb + 15, zb + 215, M.lada, `${pre}Lådsida`);
      box(g, xa + 17, xb - 17, d0 + 425 - 15, d0 + 425, zb + 35, zb + 215, M.lada, `${pre}Lådbak`);
      box(g, xa + 11, xb - 11, d0 + 15, d0 + 418, zb + 18, zb + 24, M.rygg, `${pre}Lådbotten`);
    }
    if (lage.hal) ut.delar.filter(d => d.skap === s.nr && /^SideLeft|^SideRight/.test(d.namn)).forEach(d => {
      const v = /^SideLeft/.test(d.namn), X = v ? T + 0.6 : W - T - 0.6;
      const Z = x => z + (v ? H - x : x);
      d.ops.forEach(o => {
        if (o.typ === 'hal') hal(g, X, o.y, Z(o.x), o.d, 'x', o.d >= 8 ? M.hal8 : M.hal5);
        if (o.typ === 'hylltapp') for (let i = 0; i < 3; i++) hal(g, X, o.y, Z(o.langd + Math.sign(o.steg) * 32 * i), 5, 'x', M.hal5);
      });
    });
    z += H;
  });
  if (med) {
    const d = k.dorrar, DB = d.bredd || (d.antal === 2 ? (W - 6) / 2 : W - 4);
    const xs = d.antal === 2 ? [[1, false], [W - 1 - DB, true]] : [[(W - DB) / 2, d.hand === 'h']];
    d.seg.forEach(sg => { const zb = sock + sg.zb, DH = sg.DH; xs.forEach(([x, hoger]) => {
      const px = hoger ? x + DB : x;
      // vrids kring dörrens yttre framkant (fullt anliggande gångjärn): dörren går inte utanför skåpkanten
      const piv = new THREE.Group(); piv.position.set(px, -19, 0); g0.add(piv);
      const dg = new THREE.Group(); dg.position.set(-px, 19, 0); piv.add(dg);
      box(dg, x, x + DB, -19, -2, zb, zb + DH, M.dorr, `${pre}Dörr ${hoger ? 'höger' : 'vänster'}`);
      sg.cups.forEach(c => hal(dg, hoger ? x + DB - 21.5 : x + 21.5, -1.4, zb + c, 35, 'y', M.kopp));
      piv.userData.hoger = hoger; dorrGrupp.push(piv);
    }); });
  }
  return g0;
}

function satDorrar() {
  frontGrupp.forEach(f => f.visible = lage.dorrar !== 'dolda');
  dorrGrupp.forEach(p => {
    p.visible = lage.dorrar !== 'dolda';
    p.rotation.z = lage.dorrar === 'oppna' ? (p.userData.hoger ? -1 : 1) * THREE.MathUtils.degToRad(-90) : 0;
  });
}

function ram(x0, x1, H) {
  const W = x1 - x0;
  const c = new THREE.Vector3((x0 + x1) / 2000, H / 2000, -0.25);
  ctl.target.copy(c);
  const avst = Math.max(H, W) / 1000 * 1.9;
  cam.position.set(c.x + avst * 0.55, c.y + avst * 0.15, c.z + avst);
  ctl.update();
}

function storlek() {
  const w = el.clientWidth, h = el.clientHeight;
  renderer.setSize(w, h); cam.aspect = w / h; cam.updateProjectionMatrix();
}
new ResizeObserver(storlek).observe(el); storlek();
(function loop() { requestAnimationFrame(loop); ctl.update(); renderer.render(scene, cam); })();

// klick: visa delnamn
const ray = new THREE.Raycaster(), mus = new THREE.Vector2(), etikett = document.querySelector('#vy3d-namn');
renderer.domElement.addEventListener('pointerdown', e => { mus.set(e.clientX, e.clientY); });
renderer.domElement.addEventListener('pointerup', e => {
  if (Math.hypot(e.clientX - mus.x, e.clientY - mus.y) > 4) return;
  const r = renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1), cam);
  const hit = ray.intersectObjects(rot ? rot.children : [], true).find(h => h.object.userData.namn && h.object.visible);
  if (etikett) etikett.textContent = hit ? hit.object.userData.namn : '';
  if (hit) { let o = hit.object; while (o && !(o.userData && o.userData.nr)) o = o.parent; if (o) window.dispatchEvent(new CustomEvent('modulklick', { detail: o.userData.nr })); }
});

window.Vy3d = {
  markera,
  bygg, ram: () => { forstaGang = true; window.__ut && bygg(window.__ut); },
  satt(o) { Object.assign(lage, o); if ('hal' in o && window.__ut) bygg(window.__ut); else satDorrar(); },
};
if (window.__ut) bygg(window.__ut);
window.addEventListener('garderob', e => bygg(e.detail));
