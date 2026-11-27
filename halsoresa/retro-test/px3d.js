// Kort #739: pixel-3D-Hasse för swing på retro-testsidan (live-appen orörd).
// 3D-Hasse v2.2 (../3d-test/hasse_v2.glb, samma rigg + swingklipp) renderas i låg upplösning med låst ortografisk
// kamera, 4 skuggsteg, gemensam palett (pixel-arkens 20 färger + gult + svart), lätt Bayer-dither och 1 px svart kontur.
// Alla rutor förrenderas EN gång (STEG per rep ≈ 12 fps vid takt 1,6 s) → identiska pixlar varje varv = inget flimmer.
// Rättningar ur översynen (kort #739): klockan grå med gult märke + större, huvudet 1,18× (2D-Hasses proportioner),
// marinblå väst/byxor dras mot 2D-Hassens mörka färger, svinga­ns botten med böjda knän (se KNA).
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const Q = new URLSearchParams(location.search);
export const RW = 84, RH = 96;            // ruta i spelpixlar (2D-arkets Hasse är 84 hög)
const STEG = 19;                           // rutor per rep (1,6 s takt → ~12 fps)
const PX = 1.80 / 84;                      // meter per spelpixel (Hasse ~1,75 m + hår ≈ 82 px)
const HUVUD = +(Q.get('huvud') || 1.18);
const KNA = Q.has('kna') ? +Q.get('kna') : 1; // 0 = mocapens raka ben, 1 = rättad knäböjning i botten
const KA = +(Q.get('ka') || 0.32), KH = +(Q.get('kh') || 0.12), KB = +(Q.get('kb') || 0.55), KW = +(Q.get('kw') || 0.12);   // knäböj (rad) och bålens uppresning (rad) i botten

function hex(h) { return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; }

export async function bygg(palettHex) {
  const PAL = palettHex.concat(['#ffd23f', '#0b0614']).map(hex);
  const R = new THREE.WebGLRenderer({ antialias: false, alpha: true, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(RW * 2, RH * 2, false);   // 2× översampling, sedan ruta-för-ruta-majoritet ned till 1×
  R.setClearColor(0x000000, 0);
  R.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  // låst kamera: ortografisk från Hasses vänstra sida (tittar +X → Hasse vänd åt höger som 2D-arken)
  const zc = 0.12, y0 = -0.05;
  const cam = new THREE.OrthographicCamera(-RW / 2 * PX, RW / 2 * PX, RH * PX + y0, y0, 0.1, 20);
  cam.position.set(-6, 0, zc); cam.lookAt(0, 0, zc); cam.position.y = 0; cam.updateMatrixWorld();
  const sol = new THREE.DirectionalLight(0xffffff, 2.6); sol.position.set(-3, 4, 3); scene.add(sol);
  scene.add(new THREE.AmbientLight(0xffffff, 0.75));
  const grad = new THREE.DataTexture(new Uint8Array([70, 70, 70, 255, 130, 130, 130, 255, 195, 195, 195, 255, 255, 255, 255, 255]), 4, 1);
  grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;

  const g = await new Promise((ok, fel) => { const L = new GLTFLoader(); L.setMeshoptDecoder(MeshoptDecoder); L.load('../3d-test/hasse_v2.glb', ok, undefined, fel); });
  const root = g.scene; scene.add(root);
  let kb = null, huvud = null, kropp = null; const ben = {};
  root.traverse(o => {
    if (o.name === 'Kettlebell') kb = o;
    if (o.isBone) ben[o.name] = o;
    if (!o.isMesh) return;
    o.frustumCulled = false;
    const src = o.material;
    if (o.isSkinnedMesh) {
      kropp = o;
      const m = new THREE.MeshToonMaterial({ map: src.map, gradientMap: grad });
      // marinblå väst/byxor → mörkt koksgrått som 2D-Hasse (bara mörka, mättade blå toner; ljusblå skjorta orörd)
      m.onBeforeCompile = s => { s.fragmentShader = s.fragmentShader.replace('#include <map_fragment>', `#include <map_fragment>
        { vec3 c = diffuseColor.rgb; float l = dot(c, vec3(.299,.587,.114)); float bl = c.b - max(c.r, c.g);
          float w = smoothstep(.02, .10, bl) * (1.0 - smoothstep(.16, .30, l));
          diffuseColor.rgb = mix(c, vec3(l * .95, l * .9, l * .9), w); }`); };
      o.material = m;
    } else if (o.name === 'Kettlebell' || (o.parent && o.parent.name === 'Kettlebell')) {
      o.material = new THREE.MeshToonMaterial({ color: 0x3a3c44, gradientMap: grad });
    } else o.material = new THREE.MeshToonMaterial({ color: src.color, map: src.map || null, gradientMap: grad });
  });
  huvud = ben.head;
  // klockan: större + gult märke på båda sidor (2D-Hasses klocka)
  if (kb) {
    const lab = new THREE.MeshBasicMaterial({ color: 0xffd23f });
    for (const sx of [1, -1]) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.045, 0.06), lab); m.position.set(sx * 0.094, -0.165, 0.0); kb.add(m); }
  }
  const mixer = new THREE.AnimationMixer(root);
  const clip = g.animations.find(a => a.name === 'swing') || g.animations[0];
  const act = mixer.clipAction(clip); act.play();
  // dölj andra klippets props (bänken) – de styrs av scale-spår i goblet-klippet
  root.traverse(o => { if (o.isMesh && /bank/i.test(o.name)) o.visible = false; });

  // ---- rätta swingens botten: böj knäna och skjut höften bakåt kring bottenläget (fötterna står kvar) ----
  const ABOT = 0.0;                     // klippfas för botten (klocka lägst)
  function knaKorr(c) {
    if (!KNA || !ben.thighL) return;
    const d = Math.min(Math.abs(c - ABOT), 1 - Math.abs(c - ABOT));
    const w = KNA * Math.exp(-Math.pow(d / KW, 2));          // 1 i botten, ~0 i toppen
    if (w < 1e-3) return;
    // klockan sitter som egen nod (inte i händerna): spara den relativt vänster hand och sätt tillbaka efteråt
    root.updateMatrixWorld(true);
    const kbRel = kb ? new THREE.Matrix4().copy(ben.handL.matrixWorld).invert().multiply(kb.matrixWorld) : null;
    const a = KA * w, h = KH * w;
    const X = new THREE.Vector3(1, 0, 0), q = (v) => new THREE.Quaternion().setFromAxisAngle(X, v);
    for (const s of ['L', 'R']) {
      ben['thigh' + s].quaternion.multiply(q(-a));
      ben['shin' + s].quaternion.multiply(q(2 * a));
      ben['foot' + s].quaternion.multiply(q(h - a));            // foten plant mot golvet
      if (ben['uarm' + s]) ben['uarm' + s].quaternion.premultiply(q(KB * w));   // armarna bakåt: klockan mellan benen
    }
    // bålen mer upprätt när knäna tar över (2D: höftfällning med knäböj)
    if (ben.hips) ben.hips.quaternion.premultiply(q(-h));
    root.updateMatrixWorld(true);
    if (kbRel) {
      const m = new THREE.Matrix4().copy(ben.handL.matrixWorld).multiply(kbRel);
      kb.matrix.copy(new THREE.Matrix4().copy(kb.parent.matrixWorld).invert().multiply(m));
      kb.matrix.decompose(kb.position, kb.quaternion, kb.scale); kb.updateMatrixWorld(true);
    }
  }

  // ---- en ruta: ställ klippet, rendera, kvantisera ----
  const off = document.createElement('canvas'); off.width = RW * 2; off.height = RH * 2;
  const ox = off.getContext('2d', { willReadFrequently: true });
  const B4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
  const fotY0 = {};
  function stall(c) {
    act.time = c * clip.duration; mixer.update(0);
    if (huvud) huvud.scale.setScalar(HUVUD);
    if (kb) kb.scale.setScalar(1.25);
    knaKorr(c);
    root.position.set(0, 0, 0); root.updateMatrixWorld(true);
    // håll fötterna i golvet (knäkorrigeringen lyfter dem annars)
    if (ben.footL) {
      const v = new THREE.Vector3(); ben.footL.getWorldPosition(v);
      if (fotY0.y === undefined) fotY0.y = v.y, fotY0.z = v.z;
      root.position.y = fotY0.y - v.y; root.position.z = fotY0.z - v.z; root.updateMatrixWorld(true);
    }
  }
  function ruta(c) {
    stall(c);
    R.render(scene, cam);
    ox.clearRect(0, 0, off.width, off.height); ox.drawImage(R.domElement, 0, 0);
    const src = ox.getImageData(0, 0, off.width, off.height).data;
    const ut = new ImageData(RW, RH), d = ut.data, A = new Uint8Array(RW * RH);
    for (let y = 0; y < RH; y++) for (let x = 0; x < RW; x++) {
      // 2×2 → 1: medel av täckta subpixlar, täckning ≥ 2 av 4 = pixel
      let r = 0, gg = 0, b = 0, n = 0;
      for (let j = 0; j < 2; j++) for (let i = 0; i < 2; i++) { const k = ((y * 2 + j) * off.width + x * 2 + i) * 4; if (src[k + 3] > 128) { r += src[k]; gg += src[k + 1]; b += src[k + 2]; n++; } }
      if (n < 2) continue;
      r /= n; gg /= n; b /= n;
      const t = (B4[(y & 3) * 4 + (x & 3)] / 16 - 0.5) * 14;     // lätt dither (±7)
      r += t; gg += t; b += t;
      let bi = 0, bd = 1e9;
      for (let p = 0; p < PAL.length - 1; p++) { const q = PAL[p]; const dr = r - q[0], dg = gg - q[1], db = b - q[2]; const dd = dr * dr * 0.3 + dg * dg * 0.59 + db * db * 0.11; if (dd < bd) { bd = dd; bi = p; } }
      const o = (y * RW + x) * 4, q = PAL[bi]; d[o] = q[0]; d[o + 1] = q[1]; d[o + 2] = q[2]; d[o + 3] = 255; A[y * RW + x] = 1;
    }
    // 1 px svart kontur runt silhuetten
    const K = PAL[PAL.length - 1];
    for (let y = 0; y < RH; y++) for (let x = 0; x < RW; x++) {
      if (A[y * RW + x]) continue;
      if ((x > 0 && A[y * RW + x - 1]) || (x < RW - 1 && A[y * RW + x + 1]) || (y > 0 && A[(y - 1) * RW + x]) || (y < RH - 1 && A[(y + 1) * RW + x])) {
        const o = (y * RW + x) * 4; d[o] = K[0]; d[o + 1] = K[1]; d[o + 2] = K[2]; d[o + 3] = 255;
      }
    }
    return ut;
  }
  // rutorna: index 0 = stående topp → ner → botten → upp (samma ordning som spelets repfas p)
  // spelets fas p: 0–0,5 = ▼ HÖFT BAK (topp → botten), 0,5–1 = HÖFT FRAM ▲ (botten → topp)
  const TOPP = 0.45;
  const fas2klipp = p => p < 0.5 ? (TOPP + (p / 0.5) * (1 - TOPP)) % 1 : ((p - 0.5) / 0.5) * TOPP;
  const RUTOR = [];
  for (let i = 0; i < STEG; i++) {
    const cv = document.createElement('canvas'); cv.width = RW; cv.height = RH;
    cv.getContext('2d').putImageData(ruta(fas2klipp(i / STEG)), 0, 0); RUTOR.push(cv);
  }
  window.__px3dStall = (c) => { stall(c); };
  return { RW, RH, STEG, RUTOR, ruta: p => RUTOR[Math.floor((((p % 1) + 1) % 1) * STEG) % STEG] };
}
