// Vercel-funktion: tolkar uppladdat underlag (bilder av PDF-sidor / foton / skisser) till ett garderobssystem.
// POST { token, filnamn, bilder: [dataURL...], text?: [rader] }  ->  { konfig, lasat, antaget, kontrollera }
// Miljövariabler (Vercel): OPENAI_API_KEY, GARDEROB_TOKEN, GARDEROB_WEBHOOK (Discord, valfri), GARDEROB_MODEL (valfri)
const SCHEMA = `Svara ENDAST med JSON:
{"konfig":{"namn":str,"jobb":"Garderob","nisch":{"bredd":mm,"hojd":mm}|null,"nischAuto":bool,"passbit":mm,"sockel":mm,"galler":mm,
 "hojder":[nedre_mm, ovre_mm],   // ovre 0 = bara en skåphöjd
 "djup":[nedre_mm, ovre_mm],
 "moduler":[{"typ":"lada"|"hang"|"hylla"|"bank","bredd":mm|null,"hel":bool,"lador":0-3,"hyllorNed":antal,"hyllorOvr":antal,
            "dorrar":0|1|2,"hand":"v"|"h","ovr":{"bak":"ingen"}?,"utvLador":[fronthöjd_mm nerifrån]?,"utvStart":mm?,
            "hojdNed":mm?,"djup":mm?,"mellan":mm?}]},
 "lasat":[str], "antaget":[str], "kontrollera":[str]}`;
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
Mått i mm som heltal. Skriv på svenska i lasat (det du faktiskt läst med värden), antaget (dina antaganden),
kontrollera (det snickaren måste verifiera). Hitta inte på mått du inte ser – lägg dem i antaget.`;

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
  const innehall = [{ type: 'text', text: `Fil: ${b.filnamn || 'okänd'}.` + ((b.text || []).length ? `\nTextlager (läsordning):\n${b.text.slice(0, 600).join(' | ')}` : '') + '\n' + SCHEMA }];
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
    if (process.env.GARDEROB_WEBHOOK) await discord(process.env.GARDEROB_WEBHOOK, b.filnamn || 'underlag', bilder, svar);
    return res.status(200).json(svar);
  } catch (e) {
    return res.status(500).json({ fel: String(e.message || e) });
  }
};
module.exports.config = { maxDuration: 60 };
