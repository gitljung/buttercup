// 3D-vy: modul-GLB:er (Fusion-export, glb_bygg.py) placerade enligt YamayKonfig.layout + genererade bänkskivor.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const el = document.querySelector('#vy3d');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
el.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xe9e4dc);
const cam = new THREE.PerspectiveCamera(35, 1, 0.05, 200);
const ctl = new OrbitControls(cam, renderer.domElement); ctl.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a7a66, 1.1));
const sol = new THREE.DirectionalLight(0xffffff, 2.2); sol.position.set(-4, 7, 6); sol.castShadow = true;
sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 }); scene.add(sol);
const mark = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: 0xcfc6b8, roughness: 1 }));
mark.rotation.x = -Math.PI / 2; mark.receiveShadow = true; scene.add(mark);
// världen i Fusion-koordinater (mm, Z upp) -> three (m, Y upp)
const W = new THREE.Group(); W.rotation.x = -Math.PI / 2; W.scale.setScalar(0.001); scene.add(W);

const loader = new GLTFLoader(), cache = {};
function glb(url) {
  if (!cache[url]) cache[url] = new Promise((ok, nej) => loader.load(url, g => {
    const z = new THREE.Group(); g.scene.rotation.x = Math.PI / 2;           // ångra GLB:ns Z->Y-rotation
    z.add(g.scene); z.scale.setScalar(1000);                                  // m -> mm
    z.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    z.updateMatrixWorld(true); ok(z);
  }, undefined, nej));
  return cache[url].then(z => z.clone(true));
}
const RF = new THREE.MeshStandardMaterial({ color: 0xc9ced4, metalness: 0.75, roughness: 0.3 });
const COR = new THREE.MeshStandardMaterial({ color: 0x6e381e, metalness: 0.2, roughness: 0.85 });
let gen = 0, forstaGang = true;

window.rita3d = async function (L, SV, KAT, SP) {
  const g = ++gen;
  const ny = new THREE.Group();
  const jobb = L.map(async p => {
    const mg = new THREE.Group();
    mg.position.set(p.c[0], p.c[1], 0); mg.rotation.z = p.rot * Math.PI / 180;
    const egen = p.blind && p.m['glb_' + p.blind] ? p.m['glb_' + p.blind] : null;
    let harEgen = false;
    if (egen) { try { mg.add(await glb(egen)); harEgen = true; } catch (e) { console.warn('saknar', egen); } }
    if (!harEgen) { try { mg.add(await glb(p.m.glb)); } catch (e) { console.warn('saknar', p.m.glb); } }
    if (p.m.horn && !harEgen) {   // blindpanel (koncept) på fronten
      const b = new THREE.Mesh(new THREE.BoxGeometry(p.m.blind, 3, 892 - 100), COR);
      const x = p.blind === 'slut' ? p.m.bredd / 2 - p.m.blind / 2 : -p.m.bredd / 2 + p.m.blind / 2;
      b.position.set(x, -300 + 1.5, 100 + (892 - 100) / 2); b.castShadow = true; mg.add(b);
    }
    if (p.m.grill && p.m.grill.glb) {
      try {
        const gr = await glb(p.m.grill.glb), bx = new THREE.Box3().setFromObject(gr), gg = p.m.grill;
        const lyft = KAT.gemensamt.skiva.pa_grill ? KAT.gemensamt.skiva.epdm + KAT.gemensamt.skiva.t : 0;   // grillen står på skivan
        gr.position.set(-(bx.min.x + bx.max.x) / 2, gg.glb_y_min - bx.min.y, gg.glb_z_min + lyft - bx.min.z);
        mg.add(gr);
      } catch (e) { console.warn('saknar', p.m.grill.glb); }
    }
    for (const t of p.tillval || []) {    // tillval (Yakitori 50) står löst på bänkskivan
      const tv = KAT.tillval[t];
      try {
        const gr = await glb(tv.glb), bx = new THREE.Box3().setFromObject(gr), S = KAT.gemensamt.skiva;
        gr.position.set(-(bx.min.x + bx.max.x) / 2, tv.y_fram - bx.min.y, p.m.stommehojd + S.epdm + S.t - bx.min.z);
        mg.add(gr);
      } catch (e) {
        const b = new THREE.Mesh(new THREE.BoxGeometry(tv.langd, tv.djup, tv.hojd), COR);
        b.position.set(0, tv.y_fram + tv.djup / 2, p.m.stommehojd + KAT.gemensamt.skiva.epdm + KAT.gemensamt.skiva.t + tv.hojd / 2); b.castShadow = true; mg.add(b);
      }
    }
    return mg;
  });
  const grupper = await Promise.all(jobb);
  if (g !== gen) return;
  grupper.forEach(x => ny.add(x));
  for (const s of SV) {          // bänkskivan genereras här: polygon ur skivgeneratorn, 6 mm, på modulens topplåt + EPDM
    const sh = new THREE.Shape(s.poly.map(q => new THREE.Vector2(q[0], q[1])));
    const m = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: 6, bevelEnabled: false }), RF);
    m.position.z = s.z; m.castShadow = true; m.receiveShadow = true; ny.add(m);
  }
  for (const q of SP || []) {    // sidopaneler i bänkmaterial: fri gavel, golvspel -> 900 (bänk) / topplåt (grill)
    const sh = new THREE.Shape(q.poly.map(c => new THREE.Vector2(c[0], c[1])));
    const m = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: q.hojd, bevelEnabled: false }), RF);
    m.position.z = q.z0; m.castShadow = true; m.receiveShadow = true; ny.add(m);
  }
  W.clear(); W.add(ny);
  if (forstaGang || window._centrera) {
    forstaGang = false; window._centrera = false;
    W.updateMatrixWorld(true);
    const bb = new THREE.Box3().setFromObject(W), c = bb.getCenter(new THREE.Vector3()), r = bb.getSize(new THREE.Vector3()).length();
    ctl.target.copy(c); cam.position.set(c.x - r * 0.55, c.y + r * 0.55, c.z + r * 0.9); ctl.update();
  }
};
window.centrera3d = () => { window._centrera = true; };
function storlek() { const w = el.clientWidth, h = el.clientHeight; renderer.setSize(w, h); cam.aspect = w / h; cam.updateProjectionMatrix(); }
new ResizeObserver(storlek).observe(el); storlek();
(function loop() { requestAnimationFrame(loop); ctl.update(); renderer.render(scene, cam); })();
if (window.YK_rita) window.YK_rita();
