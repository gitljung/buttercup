// Vercel-funktion: Stickerbord Studio – DELAT BORD (färdiga stickers som alla besökare ser, klustret "NYTT FRÅN STUDION").
// Källa/dokumentation: ~/code/konstruktion/stickerbord-studio/proto/PROJEKT.md (avsnitt "Delat bord").
//
// GET    /api/sticker-studio-board/            -> { items: [{ id, png, thumb, w, h, credits, texts, prompt, createdAt, test? }] } nyast först (max SBS_BOARD_MAX = 200)
// POST   /api/sticker-studio-board/  JSON { token, png: dataURL (utskuren PNG ≤ ~1,8 MB, ≤ 1100 px), thumb: dataURL (png/webp ≤ 300 kB),
//          credits: [{ handle, role: 'motif'|'style', pct, share }], texts: [str], prompt }
//          token = sparbiljett som api/sticker-studio.js skickar i 'final'-raden för en lyckad 'finish' (HMAC, 48 h, en gång per generering)
//          -> 200 { ok, item } · 403 utan giltig biljett · 409 redan sparad · 400/413 fel bild
// DELETE /api/sticker-studio-board/?id=<id>  header x-sbs-admin = SBS_ADMIN_TOKEN -> { ok, deleted }
// Lagring: Vercel Blob (publik butik sbs-board, env BLOB_READ_WRITE_TOKEN), REST-API via fetch (buttercup har inga npm-beroenden).
//   sbs-board/<id>.png (full utskärning), sbs-board/<id>_t.<png|webp> (miniatyr för bordet), sbs-board/<id>.json (metadata).
const crypto = require('crypto');

const ORIGINS = new Set(['https://www.buttercup.nu', 'https://buttercup.nu', 'https://buttercup-omega.vercel.app']);
const API = 'https://vercel.com/api/blob';
const PREFIX = 'sbs-board/';
const MAX_BODY = 3.2e6, MAX_PNG = 2.0e6, MAX_THUMB = 3.0e5;
const env = (k, d) => (process.env[k] !== undefined && process.env[k] !== '' ? process.env[k] : d);
// samma hemlighet som api/sticker-studio.js (sparbiljetten signeras där)
const SECRET = () => env('SBS_SECRET', '') || crypto.createHmac('sha256', String(process.env.OPENAI_API_KEY || 'x')).update('sbs-cookie-v1').digest('hex');
const clean = (s, n) => String(s || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const eq = (a, b) => { const x = Buffer.from(String(a)), y = Buffer.from(String(b)); return x.length === y.length && crypto.timingSafeEqual(x, y); };

function checkToken(t) {
  const [p, s] = String(t || '').split('.');
  if (!p || !s) return null;
  const want = crypto.createHmac('sha256', SECRET()).update('save:' + p).digest('base64url');
  if (!eq(s, want)) return null;
  let o = null;
  try { o = JSON.parse(Buffer.from(p, 'base64url').toString()); } catch (e) { return null; }
  if (!o || o.k !== 'save' || !/^[0-9a-f]{8,24}$/.test(String(o.id)) || !(o.exp > Date.now())) return null;
  return o;
}

// ---------- Blob REST ----------
const tok = () => process.env.BLOB_READ_WRITE_TOKEN || '';
const storeId = () => tok().split('_')[3] || '';
function bh(extra = {}) { return { authorization: 'Bearer ' + tok(), 'x-api-version': '13', 'x-vercel-blob-store-id': storeId(), ...extra }; }
async function blobErr(r) { let m = ''; try { const j = await r.json(); m = (j.error && (j.error.code + ' ' + (j.error.message || ''))) || ''; } catch (e) { m = ''; } return new Error('blob ' + r.status + ' ' + m); }
async function put(pathname, buf, type) {
  const r = await fetch(API + '/?' + new URLSearchParams({ pathname }), { method: 'PUT', body: buf,
    headers: bh({ 'x-vercel-blob-access': 'public', 'x-content-type': type, 'x-add-random-suffix': '0', 'x-allow-overwrite': '0', 'x-cache-control-max-age': '31536000' }) });
  if (!r.ok) { const e = await blobErr(r); e.status = r.status; throw e; }
  return r.json();
}
async function list(prefix) {
  let out = [], cursor = '';
  for (let k = 0; k < 5; k++) {
    const q = new URLSearchParams({ prefix, limit: '1000' }); if (cursor) q.set('cursor', cursor);
    const r = await fetch(API + '?' + q, { headers: bh() });
    if (!r.ok) throw await blobErr(r);
    const j = await r.json(); out = out.concat(j.blobs || []);
    if (!j.hasMore || !j.cursor) break; cursor = j.cursor;
  }
  return out;
}
async function del(urls) {
  if (!urls.length) return;
  const r = await fetch(API + '/delete', { method: 'POST', headers: bh({ 'content-type': 'application/json' }), body: JSON.stringify({ urls }) });
  if (!r.ok) throw await blobErr(r);
}

// ---------- hjälpare ----------
function send(res, code, obj, cache) {
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', cache || 'no-store');
  res.end(JSON.stringify(obj));
}
async function body(req) {
  if (req.body !== undefined && req.body !== null && req.body !== '') return typeof req.body === 'string' ? JSON.parse(req.body) : Buffer.isBuffer(req.body) ? JSON.parse(req.body.toString()) : req.body;
  const ch = []; let n = 0;
  for await (const c of req) { n += c.length; if (n > MAX_BODY) throw Object.assign(new Error('för stor'), { code: 413 }); ch.push(c); }
  return ch.length ? JSON.parse(Buffer.concat(ch).toString()) : {};
}
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
function image(u, max, allowWebp) {
  const m = /^data:image\/(png|webp);base64,([A-Za-z0-9+/=]+)$/.exec(String(u || ''));
  if (!m || m[2].length > max * 1.37 + 8) return null;
  const buf = Buffer.from(m[2], 'base64');
  if (buf.length > max) return null;
  if (buf.subarray(0, 8).equals(PNG_SIG) && buf.subarray(12, 16).toString() === 'IHDR') {
    const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
    if (!w || !h || w > 1100 || h > 1100) return null;
    return { buf, type: 'image/png', ext: 'png', w, h };
  }
  if (allowWebp && buf.subarray(0, 4).toString() === 'RIFF' && buf.subarray(8, 12).toString() === 'WEBP') return { buf, type: 'image/webp', ext: 'webp' };
  return null;
}
const n01 = (x) => (Number.isFinite(+x) ? Math.max(0, Math.min(1, +x)) : 0);

// ---------- lista (cache per instans: JSON per id ändras aldrig) ----------
const META = new Map();
let LIST = { t: 0, items: null };
async function items(fresh) {
  if (!fresh && LIST.items && Date.now() - LIST.t < 15000) return LIST.items;
  const blobs = await list(PREFIX), by = {};
  for (const b of blobs) {
    const m = /^sbs-board\/([0-9a-f]+)(_t)?\.(png|webp|json)$/.exec(b.pathname); if (!m) continue;
    const o = by[m[1]] || (by[m[1]] = { id: m[1] });
    if (m[3] === 'json') o.json = b.url; else if (m[2]) o.thumb = b.url; else o.png = b.url;
    o.up = Math.max(o.up || 0, Date.parse(b.uploadedAt) || 0);
  }
  const ok = Object.values(by).filter((o) => o.json && o.png).sort((a, b) => b.up - a.up).slice(0, +env('SBS_BOARD_MAX', 200));
  const out = await Promise.all(ok.map(async (o) => {
    let meta = META.get(o.json);
    if (!meta) { try { const r = await fetch(o.json); if (r.ok) { meta = await r.json(); META.set(o.json, meta); } } catch (e) { meta = null; } }
    if (!meta) return null;
    return { ...meta, id: o.id, png: o.png, thumb: o.thumb || o.png };
  }));
  LIST = { t: Date.now(), items: out.filter(Boolean).sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt))) };
  return LIST.items;
}

// ---------- handler ----------
module.exports = async (req, res) => {
  const origin = req.headers.origin || '';
  const test = !!process.env.SBS_TEST_TOKEN && req.headers['x-sbs-test'] === process.env.SBS_TEST_TOKEN;
  const admin = !!process.env.SBS_ADMIN_TOKEN && eq(req.headers['x-sbs-admin'] || '', process.env.SBS_ADMIN_TOKEN);
  if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }
  if (!tok()) return send(res, 503, { fel: 'bordet saknar lagring (BLOB_READ_WRITE_TOKEN)' });
  const url = new URL(req.url, 'http://x');
  try {
    if (req.method === 'GET') {
      if (url.searchParams.has('admin')) return send(res, admin ? 200 : 403, { admin });
      const fresh = url.searchParams.has('fresh');
      const it = await items(fresh);
      return send(res, 200, { items: it, n: it.length }, fresh ? 'no-store' : 'public, max-age=0, s-maxage=15, stale-while-revalidate=120');
    }
    if (req.method === 'DELETE') {
      if (!admin) return send(res, 403, { fel: 'admin krävs' });
      const id = String(url.searchParams.get('id') || '');
      if (!/^[0-9a-f]{8,24}$/.test(id)) return send(res, 400, { fel: 'id saknas' });
      const urls = (await list(PREFIX + id)).filter((b) => new RegExp('^sbs-board/' + id + '(_t)?\\.').test(b.pathname)).map((b) => b.url);
      await del(urls);
      LIST.t = 0;
      console.log(JSON.stringify({ sbs: 'bord-radera', id, n: urls.length }));
      return send(res, 200, { ok: true, deleted: urls.length });
    }
    if (req.method !== 'POST') return send(res, 405, { fel: 'GET/POST/DELETE' });
    if (!ORIGINS.has(origin) && !test) return send(res, 403, { fel: 'fel ursprung' });
    if (+(req.headers['content-length'] || 0) > MAX_BODY) return send(res, 413, { fel: 'för stor förfrågan' });
    let b;
    try { b = await body(req); } catch (e) { return send(res, e.code === 413 ? 413 : 400, { fel: e.code === 413 ? 'för stor förfrågan' : 'ogiltig JSON' }); }
    const t = checkToken(b.token);
    if (!t) return send(res, 403, { fel: 'ogiltig eller utgången sparbiljett' });
    if (t.dry && !test) return send(res, 403, { fel: 'testbiljett' });
    const png = image(b.png, MAX_PNG, false), th = image(b.thumb, MAX_THUMB, true);
    if (!png) return send(res, 400, { fel: 'png saknas, är inte PNG eller är för stor (≤ 2 MB, ≤ 1100 px)' });
    if (!th) return send(res, 400, { fel: 'miniatyr saknas eller är för stor (png/webp ≤ 300 kB)' });
    const credits = (Array.isArray(b.credits) ? b.credits : []).slice(0, 8).map((c) => ({ handle: clean(c && c.handle, 40) || '@stickerapp', role: c && c.role === 'motif' ? 'motif' : 'style', pct: +n01(c && c.pct).toFixed(3), share: +n01(c && c.share).toFixed(3) }));
    const meta = { id: t.id, w: png.w, h: png.h, credits, texts: (Array.isArray(b.texts) ? b.texts : []).slice(0, 4).map((x) => clean(x, 40)).filter(Boolean),
      prompt: clean(b.prompt, 200), createdAt: new Date().toISOString(), ...(t.dry ? { test: true } : {}) };
    let rp;
    try { rp = await put(PREFIX + t.id + '.png', png.buf, png.type); } catch (e) { if (e.status === 400 || e.status === 409 || e.status === 412) return send(res, 409, { fel: 'redan sparad' }); throw e; }
    const rt = await put(PREFIX + t.id + '_t.' + th.ext, th.buf, th.type);
    await put(PREFIX + t.id + '.json', Buffer.from(JSON.stringify(meta)), 'application/json');
    LIST.t = 0;
    console.log(JSON.stringify({ sbs: 'bord-spara', id: t.id, bytes: png.buf.length, credits, test: !!t.dry }));
    return send(res, 200, { ok: true, item: { ...meta, png: rp.url, thumb: rt.url } });
  } catch (e) {
    console.error('sbs board', e);
    return send(res, 502, { fel: 'lagringsfel: ' + String(e.message || e).slice(0, 160) });
  }
};
module.exports.config = { maxDuration: 30 };
module.exports.checkToken = checkToken;
