// Yamay Utekök – konfigurationsmotor (samma kod i webben och i node-pipelinen).
// Konfiguration: { id, namn, rad: [...], vagg: "ingen"|"obrannbar"|"brannbar", anm }
//   rad-element: "bank500" | "bank1000" | "horno1000" | "asado1500" | { typ: "horn1000", blind: "slut" | "start" }
//   Raden läses i gångriktningen med fronten på HÖGER hand. En hörnbänk vrider raden 90° mot fronten (innerhörn):
//   blind "slut" = nästa ben skruvas mot hörnbänkens blindpanel (hörnet avslutar benet),
//   blind "start" = föregående ben skruvas mot blindpanelen (hörnet inleder nästa ben).
// Planet: x/y i mm, modulens lokala x = gångriktningen d, front = n (d vriden 90° medurs), bak = -n. z upp.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.YamayKonfig = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  const D = 600;
  const cw = d => [d[1], -d[0]];
  const add = (p, v, s) => [p[0] + v[0] * s, p[1] + v[1] * s];
  const r2 = v => Math.round(v * 100) / 100;
  const norm = el => (typeof el === 'string' ? { typ: el } : Object.assign({}, el));

  function layout(konf, kat) {
    const fog = kat.gemensamt.fog;
    let pos = [0, 0], d = [1, 0], ben = 1, s = 0;           // pos = punkt på baklinjen där nästa modul börjar
    const out = [];
    konf.rad.forEach((el, i) => {
      const e = norm(el), m = kat.moduler[e.typ];
      if (!m) throw new Error('okänd modul: ' + e.typ);
      if (m.horn && !['slut', 'start'].includes(e.blind || 'slut')) throw new Error('hörnbänk: blind ska vara "slut" eller "start"');
      const blind = m.horn ? (e.blind || 'slut') : null;
      if (blind === 'start') {                               // vrid före: föregående ben möter blindpanelen
        if (!out.length) throw new Error('hörnbänk med blind "start" kan inte stå först');
        pos = add(pos, d, D); d = cw(d); ben++; s = 0;
      }
      const n = cw(d), p0 = pos, p1 = add(pos, d, m.bredd);
      const c = add(add(p0, d, m.bredd / 2), n, D / 2);
      out.push({ i, typ: e.typ, m, blind, ben, d, n, p0, p1, c, rot: r2(Math.atan2(d[1], d[0]) * 180 / Math.PI),
                 s0: s, s1: s + m.bredd, poly: [p0, p1, add(p1, n, D), add(p0, n, D)].map(q => q.map(r2)) });
      if (blind === 'slut') { pos = add(p1, cw(d), D + fog); d = cw(d); ben++; s = 0; }
      else { pos = add(p1, d, fog); s += m.bredd + fog; }
    });
    return out;
  }

  // granne i samma ben (fysiskt intill längs raden); över ett hörn räknas blindpanelen som granne
  function grannar(L) {
    return L.map((p, i) => {
      const v = L[i - 1], h = L[i + 1];
      return { v: v && v.ben === p.ben ? v : null, h: h && h.ben === p.ben ? h : null,
               hornV: v && v.ben !== p.ben ? v : null, hornH: h && h.ben !== p.ben ? h : null };
    });
  }

  // ---- regler -------------------------------------------------------------------------------
  function validera(konf, kat) {
    const fel = [], varn = [], info = [];
    if (!konf.rad || !konf.rad.length) { fel.push('Raden är tom.'); return { fel, varn, info }; }
    let L;
    try { L = layout(konf, kat); } catch (e) { fel.push(e.message); return { fel, varn, info }; }
    const G = grannar(L), nh = L.filter(p => p.m.horn).length;
    if (nh > 2) fel.push('Högst två hörn (U-kök).');
    L.forEach((p, i) => {
      const g = G[i];
      if (p.typ === 'asado1500') {
        for (const q of [g.v, g.h]) if (q && q.m.typ === 'grill')
          fel.push(`Modul ${i + 1} (Asado): rattarna sticker ut ${p.m.utstick} mm på ${p.m.utstick_z[0]}–${p.m.utstick_z[1]} mm höjd och krockar med ${q.m.namn} (modul ${q.i + 1}). Lägg en bänk emellan.`);
        if (!g.v && !g.hornV || !g.h && !g.hornH) varn.push(`Modul ${i + 1} (Asado) står i radens ände: rattarna sticker ut ${p.m.utstick} mm – lämna fritt där.`);
      }
      if (p.typ === 'horno1000') {
        const gr = p.m.grill;
        info.push(`Modul ${i + 1} (Horno): ${gr.fritt_sida} mm fritt till grannens gavel (krav ≥ ${gr.obrannbart_min} mm till obrännbart).`);
        if (konf.vagg === 'brannbar') varn.push(`Modul ${i + 1} (Horno): brännbar vägg – minst ${gr.brannbart_min} mm från ugnen till väggen.`);
        if (konf.vagg && konf.vagg !== 'ingen') info.push(`Modul ${i + 1} (Horno): minst 50 mm luft bakom till vägg (kylslitsar).`);
      }
      if (p.m.horn) {
        if (p.m.status) varn.push(`Modul ${i + 1}: ${p.m.namn} är ${p.m.status}.`);
        const mot = p.blind === 'slut' ? L[i + 1] : L[i - 1];
        if (mot && mot.m.typ === 'grill') info.push(`Modul ${i + 1}: ${mot.m.namn} står mot hörnbänkens blindpanel (Corten, obrännbart).`);
        if (!mot) varn.push(`Modul ${i + 1}: hörnbänken har inget ben mot blindpanelen.`);
      }
    });
    const ben = Math.max(...L.map(p => p.ben));
    if (L.length === 1 && L[0].m.typ === 'bank' && konf.vagg === 'ingen')
      varn.push('Ensam bänkmodul utan vägg tippar vid ca 155 N i bänkhöjd – skruva i vägg eller bygg ihop med fler moduler.');
    if (ben > 1) info.push(`${ben} ben (${ben === 2 ? 'L-kök' : 'U-kök'}).`);
    return { fel, varn, info };
  }

  // ---- skivor -------------------------------------------------------------------------------
  // En skiva per sammanhängande bänklopp i ett ben; delas i modulfogar så att varje del <= max_langd.
  // Där ett ben möter en blindpanel kapas skivan (overhang - fog) så den stöter mot hörnskivans framkant.
  function skivor(konf, kat) {
    const L = layout(konf, kat), S = kat.gemensamt.skiva, fog = kat.gemensamt.fog, out = [];
    const kap = S.overhang_fram - fog;
    let lopp = [];
    const flush = () => {
      if (!lopp.length) return;
      let del = [];
      const ut = () => { if (del.length) out.push(skivaAv(del, L, S, kap, out.length + 1)); del = []; };
      for (const p of lopp) {
        if (p.m.bredd > S.max_langd) throw new Error('modul bredare än max skivlängd');
        if (del.length && p.s1 - del[0].s0 > S.max_langd) ut();
        del.push(p);
      }
      ut(); lopp = [];
    };
    L.forEach((p, i) => {
      if (lopp.length && lopp[lopp.length - 1].ben !== p.ben) flush();
      if (p.m.typ === 'bank') lopp.push(p); else flush();
    });
    flush();
    return out;
  }
  function skivaAv(del, L, S, kap, nr) {
    const a = del[0], b = del[del.length - 1];
    const fore = L[a.i - 1], efter = L[b.i + 1];
    const kapStart = fore && fore.ben !== a.ben && fore.blind === 'slut' ? kap : 0;      // benet börjar mot blindpanel
    const kapSlut = efter && efter.ben !== b.ben && efter.blind === 'start' ? kap : 0;   // benet slutar mot blindpanel
    const s0 = a.s0 + kapStart, s1 = b.s1 - kapSlut, mitt = (s0 + s1) / 2;
    const bultar = [];
    for (const p of del) for (const bx of p.m.bult_x) for (const by of S.bult_y) bultar.push({ x: r2(p.s0 + p.m.bredd / 2 + bx - s0), y: by });
    let best = 0; const k = q => Math.abs(q.x - (mitt - s0)) + (q.y < 0 ? 0.1 : 0);
    bultar.forEach((q, i) => { if (k(q) < k(bultar[best])) best = i; });
    bultar.forEach((q, i) => q.fast = i === best);
    const langd = r2(s1 - s0), djup = D + S.overhang_fram;
    const p0 = add(add(a.p0, a.d, s0 - a.s0), a.n, 0);
    return { nr, ben: a.ben, moduler: del.map(p => p.i + 1), s0, s1, langd, djup, t: S.t, kapStart, kapSlut,
             kg: r2(langd * djup * S.t * 8.0e-6), bultar,
             poly: [p0, add(p0, a.d, langd), add(add(p0, a.d, langd), a.n, djup), add(p0, a.n, djup)].map(q => q.map(r2)) };
  }

  // ---- skarvar + stycklista -----------------------------------------------------------------
  function skarvar(konf, kat) {
    const L = layout(konf, kat), K = kat.gemensamt.skarv, out = [];
    for (let i = 0; i + 1 < L.length; i++) {
      const a = L[i], b = L[i + 1];
      const horn = a.ben !== b.ben;
      const bank = a.m.typ === 'bank' && b.m.typ === 'bank';
      const z = K.z_alla.concat(bank ? K.z_bank_bank : []);
      out.push({ mellan: [i + 1, i + 2], typ: horn ? 'gavel–blindpanel' : 'gavel–gavel', antal: z.length * K.y.length, z });
    }
    return out;
  }

  function stycklista(konf, kat) {
    const L = layout(konf, kat), mod = {}, rader = [];
    for (const p of L) { const k = p.typ + (p.blind ? ' ' + p.blind : ''); mod[k] = mod[k] || { p, n: 0 }; mod[k].n++; }
    for (const { p, n } of Object.values(mod))
      rader.push({ art: p.m.namn + (p.blind ? (p.blind === 'slut' ? ' (blindpanel höger)' : ' (blindpanel vänster)') : ''), fusion: p.m.fusion, antal: n, kg: p.m.vikt_kg * n, status: p.m.status });
    const SK = skarvar(konf, kat), nb = SK.reduce((s, k) => s + k.antal, 0);
    if (nb) {
      rader.push({ art: 'ISO 7380 M8x20 10.9 obehandlad (modulskarv)', antal: nb });
      rader.push({ art: 'ISO 4032 M8 kl. 8 obehandlad', antal: nb });
      rader.push({ art: 'Distanshylsa 6 mm M8 (skuggfog)', antal: nb });
    }
    const SV = skivor(konf, kat);
    SV.forEach(s => rader.push({ art: `Skiva ${s.nr}: rostfri 6 × ${s.djup} × ${s.langd} mm, ${s.bultar.length} svetsbultar`, antal: 1, kg: s.kg }));
    const nbult = SV.reduce((s, k) => s + k.bultar.length, 0);
    if (nbult) {
      rader.push({ art: 'ISO 4032 M6 A4 + isolerbricka (skivans bultar)', antal: nbult });
      rader.push({ art: 'Fixbricka M6 (fast punkt, en per skiva)', antal: SV.length });
    }
    for (const p of L) if (p.m.grill) rader.push({ art: p.m.grill.namn + ' (egen produkt)', fusion: p.m.grill.fusion, antal: 1, kg: p.m.grill.vikt_kg });
    const kg = rader.reduce((s, r) => s + (r.kg || 0), 0);
    const xs = L.flatMap(p => p.poly.map(q => q[0])), ys = L.flatMap(p => p.poly.map(q => q[1]));
    return { rader, kg: Math.round(kg), matt: [r2(Math.max(...xs) - Math.min(...xs)), r2(Math.max(...ys) - Math.min(...ys))] };
  }

  function kortnamn(konf, kat) {
    const k = { bank500: 'B500', bank1000: 'B1000', horno1000: 'H1000', asado1500: 'A1500', horn1000: 'HÖRN' };
    return konf.rad.map(el => { const e = norm(el); return e.typ === 'horn1000' ? (e.blind === 'start' ? '⌐HÖRN' : 'HÖRN¬') : (k[e.typ] || e.typ); }).join(' | ');
  }

  return { layout, validera, skivor, skarvar, stycklista, kortnamn };
});
