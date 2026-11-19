// Vercel-funktion: tolkar uppladdat underlag (bilder av PDF-sidor / foton / skisser) till ett garderobssystem.
// POST { token, filnamn, bilder: [dataURL...], text?: [rader], matt?: [måttkedjor], forslag?: konfig, exempel?: [{matt, konfig}] }
//   ->  { konfig, lasat, antaget, kontrollera, ejGarderob }
// matt = måttkedjor utlästa geometriskt i webbläsaren (pdfgeom.js: vy | riktning | position | delar = summa),
// forslag = den lokala måttkedjetolkningen, exempel = 1–2 facit (facit_exempel.js, aldrig samma fil = leave-one-out).
// Miljövariabler (Vercel): OPENAI_API_KEY, GARDEROB_TOKEN, GARDEROB_WEBHOOK (Discord, valfri), GARDEROB_MODEL (valfri)
const SCHEMA = `Svara ENDAST med JSON:
{"konfig":{"namn":str,"jobb":"Garderob","nisch":{"bredd":mm,"hojd":mm}|null,"nischAuto":bool,"passbit":mm,"sockel":mm,"galler":mm,
 "hojder":[nedre_mm, ovre_mm],   // ovre 0 = bara en skåphöjd
 "djup":[nedre_mm, ovre_mm],
 "moduler":[{"typ":"lada"|"hang"|"hylla"|"bank","bredd":mm|null,"hel":bool,"lador":0-3,"hyllorNed":antal,"hyllorOvr":antal,
            "dorrar":0|1|2,"hand":"v"|"h","ovr":{"bak":"ingen"}?,"utvLador":[fronthöjd_mm nerifrån]?,"utvStart":mm?,
            "hojdNed":mm?,"djup":mm?,"mellan":mm?}]},
 "lasat":[str], "antaget":[str], "kontrollera":[str], "ejGarderob":bool}`;
const REGLER = `Du är snickare och läser underlag (arkitektritning, foto, handskiss) för platsbyggda garderober.
Bygg ett modulsystem: moduler från vänster till höger, varje modul 300–1200 bred (dela bredare partier).
typ: "lada" = innerlådor + fast hylla + hyllor, "hang" = klädstång (hängdel), "hylla" = bara hyllor,
"bank" = sittbänk (en låg stomme, hojdNed = stommens höjd, utvändig låda, ingen dörr).
utvLador = utvändiga lådor (synliga lådfronter, ingen dörr) i nedre stommen: fronthöjder nerifrån; dörrarna sitter då bara
på övre stommen (t.ex. byrådel 3 lådor under en hängdel med klädstång i ÖVRE skåpet: ovr {"stang", "fast"}).
mellan = synlig panel till vänster om modulen (t.ex. TYP VP2 90). Höjdkedjan: sockel + nedre + övre + galler/passbit ovan
= nisch; "30" i kedjan är ofta ram runt fronterna och hör till stommen. Mått med "ca" är osäkra – lägg dem i kontrollera.
hel=true om stommen är odelad i full höjd, annars delad i nedre+övre skåp (hojder).
Standard om inget anges: sockel 100, galler 0, passbit 30, nedre 1500, djup 488 (stommens djup, ritningsdjup − 10),
dörrar 2 per modul över 650 bredd annars 1. Kylmaskin/AC bakom övre skåp => ovr.bak="ingen".
Om nischens mått finns: sätt nisch och nischAuto=false och låt moduler utan angiven bredd få bredd null (fyller nischen).
Annars nischAuto=true och ange modulbredder.
MÅTTKEDJOR: finns en lista med geometriskt utlästa måttkedjor, lita på den före bilden. Bredd: passbit v + (panel) + moduler
+ passbit h = nisch, modulerna följer dörr-/stomdelningen (oftast kedjan i uppställningen/planen). Höjd: sockel + nedre + övre +
galler (eller passbit ovan) = nisch. Djup per sektion: skåp | luft (t.ex. 550 + 100 = 650: skåpet 550, inte 650). Sektion med
en enda stomme i full höjd = hel modul. Innerlådor räknas per modul (texten i modulens del av uppställningen).
KONTROLL: summan av passbitar + moduler måste bli nischbredden och sockel + nedre + övre + galler nischhöjden. Går det inte
ihop: skriv det i kontrollera i stället för att justera ett mått i tysthet. TV-/mediamöbel eller kök: ejGarderob=true.
PRIORITET (beslut 2026-11-19): 1) samma KONFIGURATION som ritningen – rätt antal moduler i rätt ordning, typ, hel/delad,
antal innerlådor, utvändiga lådor, hyllor, klädstänger och dörrar per modul; 2) nischens yttermått exakt. Inredningshöjder
(delning, lådfronter, hyllor, stång) är riktvärden – konfiguratorn lägger dem i 32 mm-raster och standardfronter efteråt, så
lägg krut på att antalen blir rätt och lägg inte en kontrollera-rad för höjder som skiljer några mm.
Mått i mm som heltal. Skriv på svenska i lasat (det du faktiskt läst med värden), antaget (dina antaganden),
kontrollera (det snickaren måste verifiera). Hitta inte på mått du inte ser – lägg dem i antaget.`;

// summa = nisch (samma regel som PdfTolk.kontroll i webbläsaren)
function kontroll(k) {
  const ut = [];
  if (!k || !k.nisch || !k.moduler) return ut;
  const p = Array.isArray(k.passbit) ? k.passbit : [k.passbit || 0, k.passbit || 0];
  if (k.moduler.every(m => m.bredd)) {
    const s = (p[0] || 0) + (p[1] || 0) + k.moduler.reduce((a, m, i) => a + m.bredd + (i ? m.mellan || 0 : 0), 0);
    if (k.nisch.bredd && Math.abs(s - k.nisch.bredd) > 2) ut.push(`bredd: passbitar + moduler = ${s} ≠ nisch ${k.nisch.bredd}`);
  }
  const h = (k.sockel || 0) + ((k.hojder || [])[0] || 0) + ((k.hojder || [])[1] || 0) + (k.galler || 0);
  if (k.nisch.hojd && Math.abs(h - k.nisch.hojd) > 2) ut.push(`höjd: sockel + nedre + övre + galler = ${h} ≠ nisch ${k.nisch.hojd}`);
  return ut;
}

async function discord(webhook, filnamn, bilder, svar) {
  try {
    const fd = new FormData();
    fd.append('payload_json', JSON.stringify({ content: `📥 Garderob-underlag: **${filnamn}** → ${svar.konfig ? svar.konfig.moduler.length + ' moduler' : 'fel'}` }));
    bilder.slice(0, 4).forEach((b, i) => {
      const m = /^data:(image\/\w+);base64,(.*)$/.exec(b); if (!m) return;
      fd.append(`files[${i}]`, new Blob([Buffer.from(m[2], 'base64')], { type: m[1] }), `sida${i + 1}.${m[1].split('/')[1]}`);
    });
    fd.append(`files[9]`, new Blob([JSON.stringify(svar, null, 2)], { type: 'application/json' }), 'tolkning.json');
    await fetch(webhook, { method: 'POST', body: fd });
  } catch (e) { console.error('discord', e); }
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ fel: 'POST' });
  const b = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
  if (!process.env.GARDEROB_TOKEN || b.token !== process.env.GARDEROB_TOKEN) return res.status(401).json({ fel: 'ej behörig' });
  if (!process.env.OPENAI_API_KEY) return res.status(503).json({ fel: 'OPENAI_API_KEY saknas på servern' });
  const bilder = (b.bilder || []).slice(0, 4);
  if (!bilder.length && !(b.text || []).length) return res.status(400).json({ fel: 'inget underlag' });
  const exempel = (Array.isArray(b.exempel) ? b.exempel : []).slice(0, 3).map(e => JSON.stringify({ matt: (e.matt || []).slice(0, 30), konfig: e.konfig }).slice(0, 5000));
  const matt = (Array.isArray(b.matt) ? b.matt : []).slice(0, 120).map(x => String(x).slice(0, 200));
  const innehall = [{ type: 'text', text: `Fil: ${b.filnamn || 'okänd'}.`
    + (exempel.length ? `\nEXEMPEL (andra ritningar, facit: utlästa måttkedjor -> rätt konfig):\n${exempel.join('\n')}` : '')
    + (matt.length ? `\nMÅTTKEDJOR i denna ritning (vy | riktning | position i pt | delar = summa):\n${matt.join('\n')}` : '')
    + (b.forslag ? `\nLokal tolkning av måttkedjorna (kan ha fel, rätta den):\n${JSON.stringify(b.forslag).slice(0, 4000)}` : '')
    + ((b.text || []).length ? `\nTextlager (läsordning):\n${b.text.slice(0, 600).join(' | ')}` : '') + '\n' + SCHEMA }];
  bilder.forEach(u => innehall.push({ type: 'image_url', image_url: { url: u, detail: 'high' } }));
  try {
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
      body: JSON.stringify({ model: process.env.GARDEROB_MODEL || 'gpt-5.5', response_format: { type: 'json_object' },
        ...(/^gpt-5|^o\d/.test(process.env.GARDEROB_MODEL || 'gpt-5.5') ? { reasoning_effort: process.env.GARDEROB_EFFORT || 'low' } : {}),
        messages: [{ role: 'system', content: REGLER }, { role: 'user', content: innehall }] }),
    });
    const j = await r.json();
    if (!r.ok) return res.status(502).json({ fel: (j.error && j.error.message) || 'AI-fel' });
    const svar = JSON.parse(j.choices[0].message.content);
    (svar.kontrollera = svar.kontrollera || []).push(...kontroll(svar.konfig));
    if (process.env.GARDEROB_WEBHOOK) await discord(process.env.GARDEROB_WEBHOOK, b.filnamn || 'underlag', bilder, svar);
    return res.status(200).json(svar);
  } catch (e) {
    return res.status(500).json({ fel: String(e.message || e) });
  }
};
module.exports.config = { maxDuration: 60 };
