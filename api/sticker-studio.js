// Vercel-funktion: Stickerbord Studio (buttercup.nu/stickerbord_studio/) – gpt-image-2 via /v1/images/edits, strömmat.
// Källa/dokumentation: ~/code/konstruktion/stickerbord-studio/proto/PROJEKT.md (avsnitt "AI v1").
//
// GET  /api/sticker-studio/            -> { quota } (+ sätter besökscookie)
// POST /api/sticker-studio/  JSON { kind: 'gen'|'edit'|'finish', image: dataURL (jpeg/png/webp),
//        prompt?, texts?: [str], note?, styles?: [{ i: atlasindex, key, w }],
//        motifs?: [{ i, key, handle, w, pos: { x, y, s, z } }] }   (motivzonen/mashup: w = andel av stickern inne i rutan 0..1 = motivvikt;
//        x,y 0..1 = tyngdpunkt av delen i rutan, y nedåt, s = storlek/zonbredd, z = lager)
//   bilder till OpenAI: 1 = papper/version, 2.. = motiv (max 4), sedan stilar (max 4) -> högst 9 (gpt-image tar upp till 16)
//   gen    = low, image = pappersbild (ritning + text + uppladdad bild)
//   edit   = low, image = aktuell version med användarens markeringar ritade ovanpå, note = kort instruktion
//   finish = high, image = vald version (ren) -> slutlig tryckfil
//   -> 429/400/403/502 JSON { fel, quota } ELLER 200 application/x-ndjson, en rad per händelse:
//      {t:'start', id, quota} · {t:'partial', i, b64} · {t:'final', b64, fmt, usage, usd} · {t:'error', fel}
//
// Gränser (per besökare och dygn, Europe/Stockholm): SBS_LOW (10) utkast, SBS_HIGH (3) färdiga; per IP-hash 3× det;
// globalt tak SBS_GLOW (200) / SBS_GHIGH (30). Räknare i Vercel KV/Upstash om KV_REST_API_URL+KV_REST_API_TOKEN finns,
// annars i minnet per instans + i en HMAC-signerad cookie (se svagheter i PROJEKT.md).
// Test: header x-sbs-test = SBS_TEST_TOKEN -> body.dry (inget OpenAI-anrop, räknas ändå) och body.limits {low,high,glow,ghigh}.
// Nyckeln (OPENAI_API_KEY) lämnar aldrig servern. Varje generering loggas (console, + KV-lista om KV finns) för royalty.
const crypto = require('crypto');

const ORIGINS = new Set(['https://www.buttercup.nu', 'https://buttercup.nu', 'https://buttercup-omega.vercel.app']);
const REF_BASE = 'https://www.buttercup.nu/stickerbord_studio/stickers/ref/';
const NREF = 71;
const MAXMOT = 4, MOTW = 2;   // motivzonen: max 4 motiv, royaltyvikt MOTW × motiv-% (andel i rutan)
const MAX_BODY = 3.5e6, MAX_IMG = 2.4e6;
const RATE = { text: 5, imgIn: 8, out: 30 };   // USD per Mtok (gpt-image-2 listpris nov 2026)
const COOKIE = 'sbs_q';

const env = (k, d) => (process.env[k] !== undefined && process.env[k] !== '' ? process.env[k] : d);
const SECRET = () => env('SBS_SECRET', '') || crypto.createHmac('sha256', String(process.env.OPENAI_API_KEY || 'x')).update('sbs-cookie-v1').digest('hex');
const sign = (s) => crypto.createHmac('sha256', SECRET()).update(s).digest('base64url').slice(0, 32);
const dag = () => new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Stockholm' });
const b64u = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');

function readCookie(req) {
  const m = new RegExp('(?:^|;\\s*)' + COOKIE + '=([^;]+)').exec(req.headers.cookie || '');
  if (!m) return null;
  const [p, s] = m[1].split('.');
  if (!p || !s || sign(p) !== s) return null;
  try { const o = JSON.parse(Buffer.from(p, 'base64url').toString()); return o && typeof o.v === 'string' ? o : null; } catch (e) { return null; }
}
function cookieFor(o) {
  const p = b64u(o);
  return `${COOKIE}=${p}.${sign(p)}; Path=/api/sticker-studio; Max-Age=31536000; HttpOnly; Secure; SameSite=Lax`;
}
function ipHash(req) {
  const ip = String(req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '').split(',')[0].trim();
  return crypto.createHmac('sha256', SECRET()).update('ip:' + ip).digest('hex').slice(0, 16);
}

// ---------- räknare: KV (Upstash REST) eller minne ----------
const MEM = { dag: '', m: new Map() };
const kvOn = () => !!(process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN);
async function kv(cmd) {
  const r = await fetch(process.env.KV_REST_API_URL, { method: 'POST', headers: { Authorization: `Bearer ${process.env.KV_REST_API_TOKEN}` }, body: JSON.stringify(cmd) });
  return (await r.json()).result;
}
async function getCounts(keys) {
  if (kvOn()) { try { const v = await kv(['MGET', ...keys]); return v.map((x) => parseInt(x || 0, 10)); } catch (e) { console.error('kv get', e); } }
  if (MEM.dag !== dag()) { MEM.dag = dag(); MEM.m.clear(); }
  return keys.map((k) => MEM.m.get(k) || 0);
}
async function incr(keys) {
  if (kvOn()) { try { for (const k of keys) { await kv(['INCR', k]); await kv(['EXPIRE', k, 172800]); } return; } catch (e) { console.error('kv incr', e); } }
  if (MEM.dag !== dag()) { MEM.dag = dag(); MEM.m.clear(); }
  for (const k of keys) MEM.m.set(k, (MEM.m.get(k) || 0) + 1);
}

function limits(test, b) {
  const L = { low: +env('SBS_LOW', 10), high: +env('SBS_HIGH', 3), glow: +env('SBS_GLOW', 200), ghigh: +env('SBS_GHIGH', 30) };
  if (test && b && b.limits && typeof b.limits === 'object') for (const k of Object.keys(L)) if (Number.isFinite(+b.limits[k])) L[k] = +b.limits[k];
  return L;
}
async function quota(vis, ip, L) {
  const d = dag();
  const K = { vl: `sbs:${d}:v:${vis.v}:low`, vh: `sbs:${d}:v:${vis.v}:high`, il: `sbs:${d}:ip:${ip}:low`, ih: `sbs:${d}:ip:${ip}:high`, gl: `sbs:${d}:g:low`, gh: `sbs:${d}:g:high` };
  const [vl, vh, il, ih, gl, gh] = await getCounts(Object.values(K));
  const cl = vis.d === d ? vis.l || 0 : 0, ch = vis.d === d ? vis.h || 0 : 0;
  const ul = Math.max(vl, cl), uh = Math.max(vh, ch);
  const q = {
    low_left: Math.max(0, Math.min(L.low - ul, 3 * L.low - il, L.glow - gl)),
    high_left: Math.max(0, Math.min(L.high - uh, 3 * L.high - ih, L.ghigh - gh)),
    low: L.low, high: L.high,
  };
  q.why = { low: gl >= L.glow ? 'global' : il >= 3 * L.low ? 'ip' : ul >= L.low ? 'visitor' : null, high: gh >= L.ghigh ? 'global' : ih >= 3 * L.high ? 'ip' : uh >= L.high ? 'visitor' : null };
  return { q, K, ul, uh };
}

// ---------- hjälpare ----------
function send(res, code, obj, extra = {}) {
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  for (const [k, v] of Object.entries(extra)) res.setHeader(k, v);
  res.end(JSON.stringify(obj));
}
async function body(req) {
  if (req.body !== undefined && req.body !== null && req.body !== '') return typeof req.body === 'string' ? JSON.parse(req.body) : Buffer.isBuffer(req.body) ? JSON.parse(req.body.toString()) : req.body;
  const ch = []; let n = 0;
  for await (const c of req) { n += c.length; if (n > MAX_BODY) throw Object.assign(new Error('för stor'), { code: 413 }); ch.push(c); }
  return ch.length ? JSON.parse(Buffer.concat(ch).toString()) : {};
}
function dataUrl(u) {
  const m = /^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)$/.exec(String(u || ''));
  if (!m || m[2].length > MAX_IMG) return null;
  return { type: 'image/' + m[1], buf: Buffer.from(m[2], 'base64'), ext: m[1] === 'jpeg' ? 'jpg' : m[1] };
}
const clean = (s, n) => String(s || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const REFS = new Map();
async function ref(i) {
  if (REFS.has(i)) return REFS.get(i);
  const r = await fetch(REF_BASE + String(i).padStart(3, '0') + '.jpg');
  if (!r.ok) throw new Error('stilbild ' + i + ' saknas (' + r.status + ')');
  const buf = Buffer.from(await r.arrayBuffer()); REFS.set(i, buf); return buf;
}

const RULES = `STICKER RULES: one single flat printable die-cut sticker, seen straight from above as a FLAT PRINT FILE – no perspective, no skew, no curl, no mockup, no shadow, no paper texture.
A clean continuous WHITE die-cut border (even width) around the whole design. The sticker is isolated on a plain solid BLACK background,
centred with generous black margin – nothing touches or crosses the image edges. Full colour, crisp print-ready artwork.`;

// grov placering i motivzonen -> ord ("top-left, large")
function where(p) {
  const h = p.x < 0.36 ? 'left' : p.x > 0.64 ? 'right' : 'centre', v = p.y < 0.36 ? 'top' : p.y > 0.64 ? 'bottom' : 'middle';
  const pos = v === 'middle' ? (h === 'centre' ? 'centre' : h) : h === 'centre' ? v : `${v}-${h}`;
  return pos;
}
// motivvikt -> roll/storlek i kompositionen (rel = andel av motivens totala vikt, abs = andel i rutan)
function prominence(rel, abs, many) {
  if (!many) return abs >= 0.6 ? 'the main subject – large and dominant' : abs >= 0.3 ? 'a clearly visible but not dominant element (about a third to half of the design)' : 'a SMALL accent/supporting element – keep it small';
  return rel >= 0.5 ? 'DOMINANT main character – the largest and most prominent' : rel >= 0.3 ? 'secondary character – clearly visible but noticeably smaller' : 'small supporting element – much smaller, a side detail';
}
// bilder: 1 = papper/version, 2.. = motiv (mashup), sedan stilar
function buildPrompt(kind, b, sty, mot = []) {
  const texts = (Array.isArray(b.texts) ? b.texts : []).slice(0, 4).map((t) => clean(t, 40)).filter(Boolean);
  const user = clean(b.prompt, 300), note = clean(b.note, 200);
  const tot = sty.reduce((a, s) => a + s.w, 0) || 1, s0 = 2 + mot.length;
  const sw = sty.map((s, k) => `image ${k + s0} (${s.handle}) ${Math.round((s.w / tot) * 100)}%`).join(', ');
  const mi = mot.map((m, k) => `image ${k + 2}`), mr = mot.length > 1 ? `Images 2–${1 + mot.length}` : 'Image 2', many = mot.length > 1;
  const order = mot.map((m, k) => [m.pos.z, k]).sort((a, c) => a[0] - c[0]).map(([, k]) => mi[k]);
  let motifLine = '';
  if (mot.length && kind === 'gen') {
    const mt = mot.reduce((a, m) => a + m.mw, 0) || 1;
    const mw = mot.map((m, k) => `${mi[k]} (${m.handle}) ${Math.round((many ? m.mw / mt : m.mw) * 100)}% – ${prominence(m.mw / mt, m.mw, many)}, ${where(m.pos)}`).join('; ');
    motifLine = `${mr} ${many ? 'are MOTIF references' : 'is a MOTIF reference'}: INCLUDE ${many ? 'these characters/objects' : 'this character/object'} in the design – recognisable (same creature/character/object, key features, colours, outfit) – `
      + `combined with the customer's sketch and text into ONE cohesive sticker${many ? ' (a mashup: they share one composition, interacting or overlapping naturally – not separate stickers side by side)' : ''}. `
      + `Motif reference${many ? 's' : ''} weighted: ${mw}. ${many ? 'Relative size and prominence MUST follow these weights (higher % = bigger and more central). ' : ''}`
      + `Positions follow roughly where the customer placed them${many ? ` (back to front: ${order.join(', ')})` : ''}. `
      + `Redraw ${many ? 'them' : 'it'} in ONE unified style${sty.length ? ' (from the style references)' : ''}; do not paste ${many ? 'them' : 'it'} in, and do not copy ${many ? 'their' : 'its'} die-cut borders, backgrounds or any words/lettering.`;
  } else if (mot.length) {
    motifLine = `${mr} ${many ? 'are the MOTIF references' : 'is the MOTIF reference'} already combined in this design – keep ${many ? 'those characters/objects' : 'that character/object'} recognisable and in the same unified style; never add ${many ? 'their' : 'its'} original lettering.`;
  }
  const sr = sty.length > 1 ? `images ${s0}–${s0 + sty.length - 1}` : `image ${s0}`;
  const styleLine = sty.length ? `Style references weighted: ${sw}. Blend their drawing style, linework, colour palette and lettering approach in those proportions – borrow STYLE only, never copy their motifs or their text.`
      + (mot.length ? ` IMPORTANT: ${sr} ${sty.length > 1 ? 'are' : 'is'} STYLE-ONLY – do NOT draw any figure, creature, skull, face or object from ${sty.length > 1 ? 'them' : 'it'}; the only characters/objects in the sticker are the MOTIF reference${many ? 's' : ''} (${mi.join(', ')}) plus what the customer drew or wrote – exactly ${mot.length} referenced character${many ? 's' : ''}, no extra creatures, skulls or faces.` : '')
    : kind !== 'gen' ? 'Keep the design\'s current drawing style.' : mot.length ? 'No separate style references: draw everything in one bold, friendly, hand-drawn sticker style that suits the motifs.' : 'No style references: use a bold, friendly, hand-drawn sticker style.';
  const textLine = texts.length ? `Text on the sticker, spelled EXACTLY letter for letter (keep case and spelling, no extra words): ${texts.map((t) => `"${t}"`).join(', ')}.` : 'Do not add any text or letters that are not in image 1.';
  let task;
  if (kind === 'gen' && b.empty) task = user || !mot.length ? `Image 1 is an empty sheet of paper – ignore it. Design a new sticker from the customer's description: "${user}".` : 'Image 1 is an empty sheet of paper – ignore it. Design a new sticker that is a mashup of the motif references.';
  else if (kind === 'gen') task = `Image 1 is the customer's own sketch/layout on paper (drawing, typed text and/or an uploaded picture). Turn it into a finished sticker design: keep its motif, composition and idea, redraw it cleanly.${user ? ` Customer's description: "${user}".` : ''}`;
  else if (kind === 'edit') task = `Image 1 is the current sticker design with the customer's corrections drawn ON TOP in red and/or black marker${note ? ` and this note: "${note}"` : ''}. Apply what the marks and the note ask for (circled = change/fix this, arrows = move, scribbles = remove, drawn shapes = add this), then remove every marker annotation. Keep everything else in the design exactly as it is.${user ? ` Original description: "${user}".` : ''}`;
  else task = `Image 1 is the approved draft of a sticker. It is the ONLY image – everything (characters, mashup, style, lettering) is already in it. Re-render THIS EXACT design as the final high-quality print file: same motif, composition, colours, lettering and border – only sharper, cleaner and more polished. Do not redesign.`;
  return [task, motifLine, styleLine, textLine, RULES].filter(Boolean).join('\n');
}
const usd = (u) => u ? ((u.input_tokens_details?.text_tokens || 0) * RATE.text + (u.input_tokens_details?.image_tokens || 0) * RATE.imgIn + (u.output_tokens || 0) * RATE.out) / 1e6 : null;

// ---------- handler ----------
module.exports = async (req, res) => {
  const origin = req.headers.origin || '';
  const test = !!process.env.SBS_TEST_TOKEN && req.headers['x-sbs-test'] === process.env.SBS_TEST_TOKEN;
  if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }
  const vis0 = readCookie(req);
  const vis = vis0 || { v: crypto.randomBytes(12).toString('base64url'), d: dag(), l: 0, h: 0 };
  const ip = ipHash(req);
  if (req.method === 'GET') {
    const { q } = await quota(vis, ip, limits(test, null));
    return send(res, 200, { quota: q, store: kvOn() ? 'kv' : 'minne+cookie' }, vis0 ? {} : { 'Set-Cookie': cookieFor(vis) });
  }
  if (req.method !== 'POST') return send(res, 405, { fel: 'POST' });
  if (!ORIGINS.has(origin) && !test) return send(res, 403, { fel: 'fel ursprung' });
  if (+(req.headers['content-length'] || 0) > MAX_BODY) return send(res, 413, { fel: 'för stor förfrågan' });
  let b;
  try { b = await body(req); } catch (e) { return send(res, e.code === 413 ? 413 : 400, { fel: e.code === 413 ? 'för stor förfrågan' : 'ogiltig JSON' }); }
  const kind = ['gen', 'edit', 'finish'].includes(b.kind) ? b.kind : null;
  if (!kind) return send(res, 400, { fel: 'kind saknas' });
  const mode = kind === 'finish' ? 'high' : 'low';
  const img = dataUrl(b.image);
  if (!img) return send(res, 400, { fel: 'bild saknas eller är för stor' });
  const seen = new Set(), n01 = (x, d) => (Number.isFinite(+x) ? Math.max(0, Math.min(1, +x)) : d);
  const mot = (Array.isArray(b.motifs) ? b.motifs : []).slice(0, MAXMOT).map((m, k) => {
    const p = m && typeof m.pos === 'object' && m.pos ? m.pos : {};
    const mw = Number.isFinite(+m.w) && +m.w > 0 ? Math.max(0.01, Math.min(1, +m.w)) : 1;   // motiv-% (andel i rutan); saknas = 100 %
    return { i: Math.floor(+m.i), key: clean(m.key, 60), handle: clean(m.handle, 40) || '@stickerapp', mw, w: MOTW * mw,
      pos: { x: n01(p.x, 0.5), y: n01(p.y, 0.5), s: n01(p.s, 0.4), z: Number.isFinite(+p.z) ? +p.z : k } };
  }).filter((m) => m.i >= 0 && m.i < NREF && !seen.has(m.i) && seen.add(m.i));
  const sty = (Array.isArray(b.styles) ? b.styles : []).slice(0, 4).map((s) => ({ i: Math.floor(+s.i), key: clean(s.key, 60), handle: clean(s.handle, 40) || '@stickerapp', w: Math.max(0, Math.min(1, +s.w || 0)) }))
    .filter((s) => s.i >= 0 && s.i < NREF && s.w > 0 && !seen.has(s.i) && seen.add(s.i));
  const L = limits(test, b);
  const { q, K, ul, uh } = await quota(vis, ip, L);
  if ((mode === 'low' ? q.low_left : q.high_left) <= 0) {
    const why = q.why[mode];
    const fel = why === 'global' ? 'Studion har nått dagens tak för alla besökare – försök igen i morgon.'
      : mode === 'low' ? `Du har använt dina ${L.low} utkast för i dag. Nya i morgon!` : `Du har gjort dina ${L.high} färdiga stickers för i dag. Nya i morgon!`;
    return send(res, 429, { fel, quota: q, why }, vis0 ? {} : { 'Set-Cookie': cookieFor(vis) });
  }
  const id = crypto.randomBytes(6).toString('hex');
  const prompt = kind === 'gen' ? buildPrompt(kind, b, sty, mot) : buildPrompt(kind, b, [], []);
  const dry = (test && b.dry) || process.env.SBS_FAKE === '1';
  let upstream = null;
  const t0 = Date.now();
  if (!dry) {
    if (!process.env.OPENAI_API_KEY) return send(res, 503, { fel: 'AI är inte konfigurerad på servern' });
    let refs; // gen: motiv+stilar; edit/finish: bara utkastet (annars kopierar high ett av motiven)
    try { refs = kind === 'gen' ? await Promise.all([...mot, ...sty].map((s) => ref(s.i))) : []; } catch (e) { return send(res, 502, { fel: String(e.message || e) }); }
    const fd = new FormData();
    fd.append('model', env('SBS_MODEL', 'gpt-image-2'));
    fd.append('prompt', prompt);
    fd.append('image[]', new Blob([img.buf], { type: img.type }), 'image1.' + img.ext);
    refs.forEach((buf, k) => fd.append('image[]', new Blob([buf], { type: 'image/jpeg' }), `${k < mot.length ? 'motif' : 'style'}${k + 2}.jpg`));
    fd.append('quality', mode);
    fd.append('size', '1024x1024');
    fd.append('output_format', mode === 'high' ? 'png' : 'jpeg');
    if (mode === 'low') fd.append('output_compression', '88');
    fd.append('stream', 'true');
    fd.append('partial_images', '2');
    upstream = await fetch('https://api.openai.com/v1/images/edits', { method: 'POST', headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` }, body: fd });
    if (!upstream.ok) {
      let msg = 'AI-fel ' + upstream.status;
      try { const j = await upstream.json(); msg = (j.error && j.error.message) || msg; } catch (e) { /* */ }
      console.error('sbs openai', upstream.status, msg);
      const safety = /safety|moderation|rejected/i.test(msg);
      return send(res, 502, { fel: safety ? 'Bilden stoppades av säkerhetsfiltret – prova en annan formulering eller skiss.' : 'Genereringen misslyckades: ' + msg.slice(0, 200), quota: q });
    }
  }
  // räkna först när OpenAI har accepterat (avvisade anrop kostar inget och räknas inte)
  await incr(mode === 'low' ? [K.vl, K.il, K.gl] : [K.vh, K.ih, K.gh]);
  const nvis = { v: vis.v, d: dag(), l: (mode === 'low' ? ul + 1 : ul), h: (mode === 'high' ? uh + 1 : uh) };
  if (mode === 'low') q.low_left--; else q.high_left--;
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/x-ndjson; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, no-transform');
  res.setHeader('X-Accel-Buffering', 'no');
  res.setHeader('Set-Cookie', cookieFor(nvis));
  const line = (o) => res.write(JSON.stringify(o) + '\n');
  line({ t: 'start', id, kind, mode, quota: q, refs: { motifs: mot.length, styles: sty.length }, ...(test ? { prompt } : {}) });
  let usage = null, ok = false;
  try {
    if (dry) {
      const fake = process.env.SBS_FAKE_IMG ? require('fs').readFileSync(process.env.SBS_FAKE_IMG) : null;   // bara lokalt test
      const b64 = (fake || img.buf).toString('base64'), fmt = fake ? 'jpg' : img.ext;
      for (let i = 0; i < 2; i++) { await new Promise((r) => setTimeout(r, +env('SBS_FAKE_MS', 700))); line({ t: 'partial', i, b64, fmt }); }
      await new Promise((r) => setTimeout(r, +env('SBS_FAKE_MS', 700)));
      usage = { dry: true }; ok = true;
      line({ t: 'final', b64, fmt, usage, usd: 0, ms: Date.now() - t0 });
    } else {
      const dec = new TextDecoder(); let buf = '';
      for await (const chunk of upstream.body) {
        buf += dec.decode(chunk, { stream: true });
        let k;
        while ((k = buf.indexOf('\n\n')) >= 0) {
          const ev = buf.slice(0, k); buf = buf.slice(k + 2);
          const data = ev.split('\n').filter((l) => l.startsWith('data:')).map((l) => l.slice(5).trim()).join('');
          if (!data || data === '[DONE]') continue;
          let j; try { j = JSON.parse(data); } catch (e) { continue; }
          if (/partial_image$/.test(j.type)) line({ t: 'partial', i: j.partial_image_index, b64: j.b64_json, fmt: mode === 'high' ? 'png' : 'jpeg' });
          else if (/completed$/.test(j.type)) { usage = j.usage || null; ok = true; line({ t: 'final', b64: j.b64_json, fmt: mode === 'high' ? 'png' : 'jpeg', usage, usd: usd(usage), ms: Date.now() - t0 }); }
          else if (j.type === 'error' || j.error) line({ t: 'error', fel: 'AI-fel: ' + String((j.error && j.error.message) || 'okänt').slice(0, 200) });
        }
      }
      if (!ok) line({ t: 'error', fel: 'Svaret bröts – försök igen.' });
    }
  } catch (e) {
    console.error('sbs stream', e);
    line({ t: 'error', fel: 'Svaret bröts – försök igen.' });
  }
  // royalty-/creditlogg
  const logg = { sbs: 'generering', id, t: new Date().toISOString(), kind, mode, ok, dry: !!dry, visitor: crypto.createHash('sha256').update(vis.v).digest('hex').slice(0, 12), ip,
    // royaltyandel: motiv väger MOTW × motiv-% (pct = andel i rutan) mot stilarnas andel innanför linjen; role = motif|style
    refs: [...mot.map((m) => ({ ...m, role: 'motif' })), ...sty.map((s) => ({ ...s, role: 'style' }))].map((r, k, A) => ({ role: r.role, key: r.key, i: r.i, handle: r.handle, pct: +(r.role === 'motif' ? r.mw : r.w).toFixed(3), w: +r.w.toFixed(3),
      share: +(r.w / (A.reduce((a, x) => a + x.w, 0) || 1)).toFixed(3), ...(r.pos ? { pos: r.pos } : {}) })),
    usage, usd: usd(usage), ms: Date.now() - t0 };
  console.log(JSON.stringify(logg));
  if (kvOn()) { try { await kv(['RPUSH', `sbs:logg:${dag().slice(0, 7)}`, JSON.stringify(logg)]); } catch (e) { console.error('kv logg', e); } }
  res.end();
};
module.exports.config = { maxDuration: 300 };
module.exports.buildPrompt = buildPrompt;   // lokalt test
