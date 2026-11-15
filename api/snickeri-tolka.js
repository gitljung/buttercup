// Vercel-funktion: AI-assisterad planinläsning för snickeri-granskningsvyn (buttercup.nu/snickeri/, k2/webb/ai_tolka.js).
// HYBRID: AI klassar (rum, rumstyp, dörrar, fönster, vitvaror, inritade snickerier, okända koder, öppna planlösningar och
// vilken måtttext som hör till vilken vägg/nisch). AI ger ALDRIG mått – siffrorna tas ur ritningen (vektorer/måtttext) i sidan.
//
// POST { token, filnamn, blad: [{ typ: 'plan'|'sektion'|'uppstallning', namn?, rutor: [{ id, bbox_px:[x0,y0,x1,y1], bild: dataURL }],
//        sammandrag?: { rum, texter, inritat, osakert, snitt } }], zon?: { blad, bbox_px }, logga_bilder?: bool }
//   (äldre form { rutor, sammandrag } = ett blad typ 'plan')
// -> { leverantor, modell, ms, usd, tokens, anrop_idag, tak, blad: [{ index, typ, ... }], strukna_matt }
//    Koordinater i svaret: punkt_px / bbox_px i RUTANS pixlar (bilden som skickades) + ruta-id. Sidan räknar om till planens mm.
//
// Miljö (Vercel, Production): ANTHROPIC_API_KEY (finns den -> Anthropic, annars OpenAI), OPENAI_API_KEY,
//   SNICKERI_AI_LEVERANTOR (tvinga anthropic|openai), SNICKERI_AI_MODELL (t.ex. claude-opus-5-5 / gpt-5.5; 'lev:modell' går också),
//   SNICKERI_AI_DAGTAK (anrop per dygn, standard 50), SNICKERI_AI_PRIS ('in,ut' USD/Mtok, annars tabellen nedan),
//   GARDEROB_TOKEN / SNICKERI_TOKEN (behörighet), GARDEROB_WEBHOOK (Discord Montering, kort logg utan bilder om inte logga_bilder),
//   KV_REST_API_URL + KV_REST_API_TOKEN (Vercel KV/Upstash: dygnsräknaren; saknas -> räknare i minnet + logg).
const TIMEOUT_MS = 58000;
const PRIS = {   // USD per Mtok (in, ut). ANTAGANDE där inget listpris är verifierat – sätt SNICKERI_AI_PRIS för exakt.
  'claude-opus-5-5': [5, 25], 'claude-sonnet-5-5': [3, 15], 'claude-haiku-5-5': [1, 5],
  'gpt-5.5': [5, 30], 'gpt-5': [1.25, 10], 'gpt-5-mini': [0.25, 2],
};
const MATT_NYCKLAR = new Set(['bredd', 'hojd', 'höjd', 'djup', 'matt', 'mått', 'mm', 'langd', 'längd', 'area', 'area_m2', 'm2', 'langd_mm', 'bredd_mm', 'djup_mm', 'hojd_mm', 'varde']);
const RUMSTYPER = 'sovrum|vardagsrum|allrum|kok|matplats|badrum|wc|dusch|tvatt|teknik|entre|hall|passage|walkin|klk|forrad|skafferi|kontor|gastrum|barnrum|bastu|groventre|trapphall|garage|uterum|altan|ovrigt';
const INRITAT = 'garderob|linne|stad|klk|hogskap|kapphylla|koksrad|koksö|tvattbank|tvatt_stadskap|skap_omarkt|bank|ovrigt';
const VIT = 'kyl|frys|kylfrys|diskmaskin|ugn|mikro|ugn_mikro|hall|diskho|tvattmaskin|torktumlare|torkskap|vp|teknik';

const SCHEMA_TEXT = `Svara ENDAST med ett JSON-objekt:
{"blad":[{"index":0,"typ":"plan",
  "rum":[{"namn":str,"typ":"${RUMSTYPER}","ruta":id,"punkt_px":[x,y],"var_id":rum-id ur sammandraget|null,"sakerhet":0-1}],
  "dorrar":[{"ruta":id,"punkt_px":[x,y],"typ":"slag|dubbel|skjut|ytter|oppning","rum":[namn],"sakerhet":0-1}],
  "fonster":[{"ruta":id,"punkt_px":[x,y],"rum":namn,"sakerhet":0-1}],
  "vitvaror":[{"kod":str,"typ":"${VIT}","ruta":id,"bbox_px":[x0,y0,x1,y1],"rum":namn,"sakerhet":0-1}],
  "inritat":[{"kod":str|null,"typ":"${INRITAT}","ruta":id,"bbox_px":[x0,y0,x1,y1],"rum":namn,"text":str,"sakerhet":0-1}],
  "okanda_koder":[{"kod":str,"ruta":id,"punkt_px":[x,y],"gissning":str}],
  "oppna_planlosningar":[[rumsnamn,...]],
  "matttext":[{"text_id":id ur sammandraget|null,"text":str,"ruta":id,"punkt_px":[x,y],"hor_till":"vagg|nisch|rum|inritat","ref":namn eller id}],
  "anmarkningar":[str]},
 {"index":1,"typ":"sektion|uppstallning","snitt":"A-A"|null,"rum":[namn],
  "matttext":[{"text_id":id|null,"text":str,"ruta":id,"punkt_px":[x,y],"roll":"takhojd|undertak|nisch_bredd|nisch_hojd|nisch_djup|sockel|annat","ref":str}],
  "anmarkningar":[str]}]}
Koordinater: punkt_px och bbox_px i pixlar i DEN RUTA (bild) du anger med "ruta", origo uppe till vänster.`;

const REGLER = `Du är en erfaren snickare och läser svenska arkitektritningar (planritningar, sektioner, uppställningar) åt ett
verktyg som tar fram platsbyggda snickerier (garderober, kök, tvätt). Bladet är delat i överlappande rutor; samma sak kan synas
i två rutor – rapportera den EN gång (i den ruta där den syns bäst).
UPPGIFT (plan): klassa varje rum och rumstyp (öppen planlösning: ange zonerna som egna rum + oppna_planlosningar), alla dörrar
(bågar, skjutdörrar, öppningar) och fönster (tunna dubbel-/trippellinjer i yttervägg, glaspartier), vitvaror (K/F, KF, K, F, DM,
U/M, M/U, U, M, TM, TT, TS, VP …), inritade snickerier (G, GL, G/L, L, LS, ST, KLK, KH, SNxx-y, köksrader, köksö, tvättbänk,
OMÄRKTA skåp: rektangel/band ~300–650 djupt längs vägg, kryss = högskåp), okända koder och öppna planlösningar.
Möbler (sängar, soffor, bord, stolar), sanitet (wc, dusch, badkar, handfat) och trappor är INTE snickerier. VP är teknik, ingen vitvara.
Sammandraget är VÅR läsares resultat (kan ha fel och missar) – rätta det: ange var_id när ditt rum är samma som vårt.
MÅTT: du får ALDRIG ange mått, längder, areor eller skala som siffror. Du får bara säga vilken måtttext (text_id eller exakt text
som den står) som hör till vilken vägg, nisch eller vilket snickeri, och (sektion/uppställning) vilken roll den har.
Sektion/uppställning: vilket snitt (A-A …) eller rum bladet gäller och vilken måtttext som är takhöjd, undertak, nisch eller sockel.
Var hellre försiktig än påhittig: sätt sakerhet < 0.5 när du är osäker. Skriv på svenska.`;

let minne = { dag: '', n: 0 };
const dag = () => new Date().toISOString().slice(0, 10);

async function rakna(oka) {   // -> antal anrop idag (efter ökning), 'kv'|'minne'
  const url = process.env.KV_REST_API_URL, tok = process.env.KV_REST_API_TOKEN, nyckel = `snickeri-ai:${dag()}`;
  if (url && tok) {
    try {
      const h = { Authorization: `Bearer ${tok}` };
      const r = await fetch(`${url}/${oka ? 'incr' : 'get'}/${nyckel}`, { headers: h });
      const j = await r.json();
      if (oka) await fetch(`${url}/expire/${nyckel}/172800`, { headers: h });
      return [parseInt(j.result || 0, 10), 'kv'];
    } catch (e) { console.error('kv', e); }
  }
  if (minne.dag !== dag()) minne = { dag: dag(), n: 0 };
  if (oka) minne.n++;
  return [minne.n, 'minne'];
}

function utanMatt(o, bort, vag = '') {   // AI ger aldrig mått: stryk numeriska mått-nycklar (rekursivt)
  if (Array.isArray(o)) return o.map((x, i) => utanMatt(x, bort, `${vag}[${i}]`));
  if (o && typeof o === 'object') {
    const ut = {};
    for (const [k, v] of Object.entries(o)) {
      if (MATT_NYCKLAR.has(k.toLowerCase()) && (typeof v === 'number' || (typeof v === 'string' && /^\s*[\d.,]+\s*(mm|m|cm|m²|m2)?\s*$/.test(v)))) { bort.push(`${vag}.${k}`); continue; }
      ut[k] = utanMatt(v, bort, `${vag}.${k}`);
    }
    return ut;
  }
  return o;
}

function leverantor() {
  let lev = (process.env.SNICKERI_AI_LEVERANTOR || '').toLowerCase(), modell = process.env.SNICKERI_AI_MODELL || '';
  if (modell.includes(':')) { [lev, modell] = modell.split(':', 2); }
  if (!lev) lev = process.env.ANTHROPIC_API_KEY ? 'anthropic' : 'openai';
  if (lev === 'anthropic' && !process.env.ANTHROPIC_API_KEY) lev = 'openai';
  if (lev === 'anthropic' && (!modell || !/^claude/.test(modell))) modell = modell && /^claude/.test(modell) ? modell : 'claude-opus-5-5';
  if (lev === 'openai' && (!modell || /^claude/.test(modell))) modell = process.env.GARDEROB_MODEL || 'gpt-5.5';
  return { lev, modell };
}

function bladUr(b) {
  let blad = Array.isArray(b.blad) && b.blad.length ? b.blad : (Array.isArray(b.rutor) ? [{ typ: 'plan', rutor: b.rutor, sammandrag: b.sammandrag }] : []);
  let n = 0;
  blad = blad.slice(0, 4).map((x, i) => ({ index: i, typ: ['plan', 'sektion', 'uppstallning'].includes(x.typ) ? x.typ : 'plan', namn: String(x.namn || '').slice(0, 120),
    rutor: (x.rutor || []).filter(r => r && typeof r.bild === 'string' && /^data:image\/(png|jpeg|webp);base64,/.test(r.bild)).filter(() => ++n <= 12)
      .map((r, j) => ({ id: String(r.id || `b${i}r${j}`).slice(0, 20), bbox_px: (r.bbox_px || []).slice(0, 4).map(Number), bild: r.bild })),
    sammandrag: x.sammandrag || null }));
  return blad.filter(x => x.rutor.length);
}

function innehall(blad, b) {
  const delar = [{ t: 'text', s: `Fil: ${String(b.filnamn || 'okänd').slice(0, 120)}. ${blad.length} blad.` + (b.zon ? ` Fokusera på zonen ${JSON.stringify(b.zon).slice(0, 200)} (bladets px) – rapportera bara det som ligger i zonen.` : '') }];
  for (const x of blad) {
    delar.push({ t: 'text', s: `\n=== BLAD ${x.index} (typ ${x.typ}${x.namn ? ', ' + x.namn : ''}) ===` + (x.sammandrag ? `\nVÅR LÄSARES SAMMANDRAG (bladets px):\n${JSON.stringify(x.sammandrag).slice(0, 14000)}` : '') });
    for (const r of x.rutor) {
      delar.push({ t: 'text', s: `Ruta ${r.id} = bladets px ${JSON.stringify(r.bbox_px)} (bilden nedan kan vara skalad; svara i bildens egna pixlar):` });
      delar.push({ t: 'bild', s: r.bild });
    }
  }
  delar.push({ t: 'text', s: SCHEMA_TEXT });
  return delar;
}

async function anropa(lev, modell, delar, signal) {
  if (lev === 'anthropic') {
    const content = delar.map(d => d.t === 'text' ? { type: 'text', text: d.s } : (() => { const m = /^data:(image\/\w+);base64,(.*)$/.exec(d.s); return { type: 'image', source: { type: 'base64', media_type: m[1], data: m[2] } }; })());
    const r = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', signal,
      headers: { 'content-type': 'application/json', 'x-api-key': process.env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model: modell, max_tokens: 12000, system: REGLER, messages: [{ role: 'user', content }] }) });
    const j = await r.json();
    if (!r.ok) throw Object.assign(new Error((j.error && j.error.message) || `Anthropic ${r.status}`), { status: r.status });
    return { text: (j.content || []).map(c => c.text || '').join(''), tin: j.usage.input_tokens + (j.usage.cache_read_input_tokens || 0) + (j.usage.cache_creation_input_tokens || 0), tut: j.usage.output_tokens };
  }
  const content = delar.map(d => d.t === 'text' ? { type: 'text', text: d.s } : { type: 'image_url', image_url: { url: d.s, detail: 'high' } });
  const r = await fetch('https://api.openai.com/v1/chat/completions', { method: 'POST', signal,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
    body: JSON.stringify({ model: modell, response_format: { type: 'json_object' },
      ...(/^gpt-5|^o\d/.test(modell) ? { reasoning_effort: process.env.SNICKERI_AI_EFFORT || 'low' } : {}),
      messages: [{ role: 'system', content: REGLER }, { role: 'user', content }] }) });
  const j = await r.json();
  if (!r.ok) throw Object.assign(new Error((j.error && j.error.message) || `OpenAI ${r.status}`), { status: r.status });
  return { text: j.choices[0].message.content, tin: j.usage.prompt_tokens, tut: j.usage.completion_tokens };
}

function tolka(text) {
  try { return JSON.parse(text); } catch (e) { /* */ }
  const m = /\{[\s\S]*\}/.exec(text || ''); if (!m) throw new Error('AI-svaret var inte JSON');
  return JSON.parse(m[0]);
}

const LISTOR = ['rum', 'dorrar', 'fonster', 'vitvaror', 'inritat', 'okanda_koder', 'oppna_planlosningar', 'matttext', 'anmarkningar'];
function stada(svar, blad) {   // strikt form: bara kända listor, ruta-id som finns, koordinater som tal
  const ut = [];
  const lista = Array.isArray(svar.blad) ? svar.blad : [Object.assign({ index: 0 }, svar)];
  for (const x of blad) {
    const s = lista.find(y => Number(y.index) === x.index) || (blad.length === 1 ? lista[0] : null) || {};
    const ids = new Set(x.rutor.map(r => r.id)), o = { index: x.index, typ: x.typ };
    const okP = p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite);
    const okB = p => Array.isArray(p) && p.length === 4 && p.every(Number.isFinite);
    for (const k of LISTOR) {
      let l = Array.isArray(s[k]) ? s[k] : [];
      if (!['oppna_planlosningar', 'anmarkningar'].includes(k)) l = l.filter(e => e && typeof e === 'object' && (!e.ruta || ids.has(String(e.ruta))) && (e.punkt_px ? okP(e.punkt_px) : true) && (e.bbox_px ? okB(e.bbox_px) : true));
      o[k] = l.slice(0, 200);
    }
    if (x.typ !== 'plan') { o.snitt = s.snitt || null; o.galler = s.galler || null; }
    ut.push(o);
  }
  return ut;
}

async function discord(meddelande, bilder, svar) {
  const hook = process.env.GARDEROB_WEBHOOK; if (!hook) return;
  try {
    const fd = new FormData();
    fd.append('payload_json', JSON.stringify({ content: meddelande.slice(0, 1900), allowed_mentions: { parse: [] } }));
    (bilder || []).slice(0, 4).forEach((u, i) => { const m = /^data:(image\/\w+);base64,(.*)$/.exec(u); if (m) fd.append(`files[${i}]`, new Blob([Buffer.from(m[2], 'base64')], { type: m[1] }), `ruta${i + 1}.${m[1].split('/')[1]}`); });
    if (svar) fd.append('files[9]', new Blob([JSON.stringify(svar, null, 1)], { type: 'application/json' }), 'ai_svar.json');
    await fetch(hook, { method: 'POST', body: fd });
  } catch (e) { console.error('discord', e); }
}

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ fel: 'POST' });
  let b; try { b = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {}); } catch (e) { return res.status(400).json({ fel: 'ogiltig JSON' }); }
  const tok = [process.env.GARDEROB_TOKEN, process.env.SNICKERI_TOKEN].filter(Boolean);
  if (!tok.length || !tok.includes(b.token)) return res.status(401).json({ fel: 'ej behörig' });
  const { lev, modell } = leverantor();
  if (lev === 'openai' && !process.env.OPENAI_API_KEY) return res.status(503).json({ fel: 'ingen AI-nyckel på servern', leverantor: lev, modell });
  const blad = bladUr(b);
  if (!blad.length) return res.status(400).json({ fel: 'inga rutor (bilder) i anropet', leverantor: lev, modell });
  const tak = parseInt(process.env.SNICKERI_AI_DAGTAK || '50', 10);
  const [fore, rk] = await rakna(false);
  if (fore >= tak) return res.status(429).json({ fel: `dagens AI-tak nått (${fore}/${tak} anrop) – planen fungerar utan AI`, leverantor: lev, modell, anrop_idag: fore, tak });
  const [nu] = await rakna(true);
  const fil = String(b.filnamn || 'plan').slice(0, 80), t0 = Date.now();
  const ctl = new AbortController(), tid = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  try {
    const r = await anropa(lev, modell, innehall(blad, b), ctl.signal);
    const bort = [], svar = utanMatt(tolka(r.text), bort);
    const [pi, po] = (process.env.SNICKERI_AI_PRIS || '').split(',').map(Number).filter(Number.isFinite).length === 2 ? process.env.SNICKERI_AI_PRIS.split(',').map(Number) : (PRIS[modell] || [5, 30]);
    const usd = +(r.tin * pi / 1e6 + r.tut * po / 1e6).toFixed(4), ms = Date.now() - t0;
    const ut = { leverantor: lev, modell, ms, usd, tokens: { in: r.tin, ut: r.tut }, anrop_idag: nu, tak, raknare: rk, strukna_matt: bort.slice(0, 50), blad: stada(svar, blad) };
    const p0 = ut.blad[0] || {};
    console.log(JSON.stringify({ snickeri_ai: fil, lev, modell, ms, usd, nu, tak, rk }));
    await discord(`🤖 [snickeri-ai] ${fil} · ${lev}/${modell} · ${(ms / 1000).toFixed(1)} s · ${usd} USD · ${blad.length} blad, ${blad.reduce((s, x) => s + x.rutor.length, 0)} rutor · `
      + `${(p0.rum || []).length} rum, ${(p0.dorrar || []).length} dörrar, ${(p0.fonster || []).length} fönster, ${(p0.inritat || []).length} inritat · anrop ${nu}/${tak} idag`,
      b.logga_bilder ? blad.flatMap(x => x.rutor.map(r => r.bild)) : null, b.logga_bilder ? ut : null);
    return res.status(200).json(ut);
  } catch (e) {
    const avbrutet = e.name === 'AbortError', ms = Date.now() - t0;
    const fel = avbrutet ? `AI-anropet tog över ${TIMEOUT_MS / 1000} s – avbrutet` : String(e.message || e).slice(0, 300);
    console.error(JSON.stringify({ snickeri_ai_fel: fil, lev, modell, ms, fel }));
    await discord(`⚠ [snickeri-ai] ${fil} · ${lev}/${modell} · fel efter ${(ms / 1000).toFixed(1)} s: ${fel}`);
    return res.status(avbrutet ? 504 : 502).json({ fel, leverantor: lev, modell, ms, anrop_idag: nu, tak });
  } finally { clearTimeout(tid); }
};
module.exports.config = { maxDuration: 60 };
