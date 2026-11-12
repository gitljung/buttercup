// Yamay Utekök – konfigurationsmotor (samma kod i webben och i node-pipelinen).
// Konfiguration: { id, namn, rad: [...], vagg: "ingen"|"obrannbar"|"brannbar", anm }
//   rad-element: "bank500" | "bank1000" | "horno1000" | "asado1500" | "firetable1500" | "tizon500" | { typ: "horn1000", blind: "slut" | "start" }
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
        pos = add(pos, d, D + (m.panel_t || 0)); d = cw(d); ben++; s = 0;
      }
      const n = cw(d), p0 = pos, p1 = add(pos, d, m.bredd);
      const c = add(add(p0, d, m.bredd / 2), n, D / 2);
      out.push({ i, typ: e.typ, m, blind, ben, tillval: e.tillval ? [].concat(e.tillval) : [], d, n, p0, p1, c, rot: r2(Math.atan2(d[1], d[0]) * 180 / Math.PI),
                 s0: s, s1: s + m.bredd, poly: [p0, p1, add(p1, n, D), add(p0, n, D)].map(q => q.map(r2)) });
      if (blind === 'slut') { pos = add(p1, cw(d), D + (m.panel_t || 0) + fog); d = cw(d); ben++; s = 0; }
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
      if (p.typ === 'tizon500') {   // Tizón (vedspis) på låg modul, hällen i bänkhöjd (koncept 2026-11-09)
        const gr = p.m.grill, sk = gr.skorsten;
        if (p.m.status) varn.push(`Modul ${i + 1}: ${p.m.namn} är ${p.m.status}.`);
        if (p.m.skarv_anm) varn.push(`Modul ${i + 1} (Tizón): ${p.m.skarv_anm}.`);
        if (sk && sk.riktning === 'bak') {
          if (konf.vagg === 'brannbar') fel.push(`Modul ${i + 1} (Tizón): vedspis – får inte stå mot brännbar vägg.`);
          else if (konf.vagg && konf.vagg !== 'ingen') varn.push(`Modul ${i + 1} (Tizón): skorstenen ska gå bakom modulen (ca ${sk.bak_om_modul} mm, beslut 2026-11-09) – mot vägg krävs plats för röret och brandavstånd, inte utrett.`);
          else info.push(`Modul ${i + 1} (Tizón): skorsten Ø${sk.dim} bakåt, vertikalt rör ca ${sk.bak_om_modul} mm bakom modulen (fristående kök).`);
        }
        info.push(`Modul ${i + 1} (Tizón): hällen på ${gr.topp} mm${gr.topp !== kat.gemensamt.bankhojd ? ` (${gr.topp - kat.gemensamt.bankhojd} mm över bänken)` : ''}; brandavstånd till trä okänt → grannarna får rostfri skiva.`);
        info.push(`Modul ${i + 1} (Tizón): spisen kan låsas med 2 × M8 A4 + bricka underifrån genom topplåten (rekommenderas vid fast installation, offentlig miljö och barn).`);
      }
      if (p.typ === 'firetable1500') {   // Fire Table (vickesluring 2026-11-09): öppen eld på Asado-modulen
        const gr = p.m.grill;
        varn.push(`Modul ${i + 1}: ${p.m.status}.`);
        if (konf.vagg === 'brannbar') fel.push(`Modul ${i + 1} (Fire Table): öppen eld – får inte stå mot brännbar vägg. Välj vägg "ingen" eller "obrännbar".`);
        else if (konf.vagg === 'obrannbar') info.push(`Modul ${i + 1} (Fire Table): bakväggens rygg och bultskallar sticker ut ${gr.utstick_bak} mm bakom modulen – lämna minst ${gr.utstick_bak} mm till väggen.`);
        info.push(`Modul ${i + 1} (Fire Table): ca ${gr.vikt_kg} kg på 4 fötter nära gavlarna – handräknat OK för modulen (inte kontrollerat i Fusion).`);
        info.push(`Modul ${i + 1} (Fire Table): bara ${gr.fotspel} mm luft mellan lådans botten och skivan – värmeskydd/luftspalt (≥ 25 mm) är inte löst; silikonlisten under skivan tål ca 200 °C.`);
      }
      if (p.m.horn) {
        if (p.m.status) varn.push(`Modul ${i + 1}: ${p.m.namn} är ${p.m.status}.`);
        const mot = p.blind === 'slut' ? L[i + 1] : L[i - 1];
        if (mot && mot.m.typ === 'grill') info.push(`Modul ${i + 1}: ${mot.m.namn} står mot hörnbänkens blindpanel (Corten, obrännbart).`);
        if (!mot) varn.push(`Modul ${i + 1}: hörnbänken har inget ben mot blindpanelen.`);
      }
    });
    const S = kat.gemensamt.skiva;
    if (S.pa_grill) L.forEach((p, i) => { if (p.typ === 'asado1500' && Math.abs(p.m.grill.z0 + p.m.grill.hojd + S.epdm + S.t - kat.gemensamt.bankhojd) > 0.5) varn.push(`Modul ${i + 1} (Asado): med skiva under grillen hamnar lådans överkant på ${p.m.grill.z0 + p.m.grill.hojd + S.epdm + S.t} mm, inte ${kat.gemensamt.bankhojd} – ändra Asado-modulens ModH till ${kat.gemensamt.bankhojd - p.m.grill.hojd - S.epdm - S.t} i Fusion.`); });
    if (S.pa_grill && L.some(p => p.m.bult_anm)) info.push('Skivans bultraster på grillmodulerna är ett förslag – Ø9-hålen finns inte i grillmodulernas topplåt i Fusion än.');
    const ben = Math.max(...L.map(p => p.ben));
    if (L.length === 1 && L[0].m.typ === 'bank' && konf.vagg === 'ingen')
      varn.push('Ensam bänkmodul utan vägg tippar vid ca 155 N i bänkhöjd – skruva i vägg eller bygg ihop med fler moduler.');
    L.forEach((p, i) => p.tillval.forEach(t => {
      const tv = (kat.tillval || {})[t];
      if (!tv) { fel.push(`Modul ${i + 1}: okänt tillval ${t}.`); return; }
      if (!tv.pa_typ.includes(p.m.typ)) { fel.push(`Modul ${i + 1}: ${tv.namn} kan bara stå på en bänkmodul.`); return; }
      const G = grannar(L)[i];
      for (const q of [G.v, G.h]) if (q && q.m.utstick && q.m.utstick_z && 900 + tv.hojd > q.m.utstick_z[0])
        fel.push(`Modul ${i + 1}: ${tv.namn} (topp ${900 + tv.hojd} mm) krockar med ${q.m.namn}s rattar, som sticker ut ${q.m.utstick} mm över grannbänken på ${q.m.utstick_z[0]}–${q.m.utstick_z[1]} mm. Ställ den på en bänk som inte står bredvid Asado.`);
      if (tv.langd > p.m.bredd + 50) varn.push(`Modul ${i + 1}: ${tv.namn} (${tv.langd} mm) är bredare än modulen.`);
      else if (tv.langd > p.m.bredd) info.push(`Modul ${i + 1}: ${tv.namn} är ${tv.langd} mm och sticker ut ${(tv.langd - p.m.bredd) / 2} mm per sida över modulen.`);
      info.push(`Modul ${i + 1}: ${tv.namn} ${tv.anm}. Värmen mot skivan under grillen är inte kontrollerad (EPDM under bänkskivan tål ca 120–130 °C).`);
    }));
    if (konf.skiva === 'tra') {
      const M = materialer(L, konf, kat), ST = kat.gemensamt.skiva.tra;
      M.forEach((x, i) => { if (x.varfor) info.push(`Modul ${i + 1}: rostfri skiva i stället för trä (${x.varfor}).`); });
      const hb = Math.max(...L.filter((p, i) => M[i].mat === 'tra').map(p => p.m.stommehojd + ST.epdm + ST.t), 0);
      if (hb) varn.push(`Träskivan (${ST.t} mm) gör bänkytan ${hb} mm hög, ${hb - kat.gemensamt.bankhojd} mm över de rostfria skivorna och Asado-lådan. Samma höjd kräver bänkmoduler med ModH ${kat.gemensamt.bankhojd - ST.epdm - ST.t} (ny variant i Fusion).`);
      if (!M.some(x => x.mat === 'tra')) varn.push('Ingen bänk får träskiva – alla bänkar står intill en grill.');
    }
    if (ben > 1) info.push(`${ben} ben (${ben === 2 ? 'L-kök' : 'U-kök'}).`);
    return { fel, varn, info };
  }

  // ---- skivmaterial: konf.skiva = 'rostfri' (standard) | 'tra' ----------------------------
  // Trä bara på bänkar. En bänk intill en grill blir rostfri om träets avstånd till grillen < grillens brannbart_min,
  // eller om avståndet är okänt (ingen brannbart_min i katalogen) – försiktig standard.
  let konfMat = [];
  function materialer(L, konf, kat) {
    const fog = kat.gemensamt.fog, G = grannar(L);
    return L.map((p, i) => {
      if (konf.skiva !== 'tra' || p.m.typ !== 'bank') return { mat: 'rostfri' };
      for (const q of [G[i].v, G[i].h]) if (q && q.m.grill) {
        const g = q.m.grill, avst = g.bredd < q.m.bredd - 10 && g.fritt_sida != null ? g.fritt_sida + fog : fog;
        if (g.brannbart_min == null) return { mat: 'rostfri', varfor: `intill ${q.m.namn} – avstånd till brännbart okänt, träet hade legat ${avst} mm från grillen` };
        if (avst < g.brannbart_min) return { mat: 'rostfri', varfor: `intill ${q.m.namn} – träet hade legat ${avst} mm från grillen, krav ${g.brannbart_min} mm` };
      }
      return { mat: 'tra' };
    });
  }
  const skT = (S, mat) => mat === 'tra' ? S.tra.t : S.t;
  const skE = (S, mat) => mat === 'tra' ? S.tra.epdm : S.epdm;

  // ---- skivor -------------------------------------------------------------------------------
  // En skiva per sammanhängande bänklopp i ett ben; delas i modulfogar så att varje del <= max_langd.
  // Där ett ben möter en blindpanel kapas skivan (overhang - fog) så den stöter mot hörnskivans framkant.
  function skivor(konf, kat) {
    konfSidor = konf.sidor !== false;
    const L = layout(konf, kat);
    konfMat = materialer(L, konf, kat);
    const S = kat.gemensamt.skiva, fog = kat.gemensamt.fog, out = [];
    const kap = S.overhang_fram - fog - ((Object.values(kat.moduler).find(x => x.horn) || {}).panel_t || 0);
    let lopp = [];
    const flush = () => {
      if (!lopp.length) return;
      let del = [];
      const ut = () => { if (del.length) out.push(skivaAv(del, L, S, kap, out.length + 1, fog)); del = []; };
      for (const p of lopp) {
        if (p.m.bredd > S.max_langd) throw new Error('modul bredare än max skivlängd');
        if (del.length && p.s1 - del[0].s0 > S.max_langd) ut();
        del.push(p);
      }
      ut(); lopp = [];
    };
    // bänklopp bryts av ben, hörnsväng och grillmoduler; varje grillmodul får en egen skiva på sin (lägre) topplåt
    L.forEach((p, i) => {
      const sist = lopp[lopp.length - 1];
      if (sist && (sist.ben !== p.ben || sist.m.typ !== 'bank' || p.m.typ !== 'bank' || konfMat[sist.i].mat !== konfMat[p.i].mat)) flush();
      if (p.m.typ === 'bank' || S.pa_grill) lopp.push(p);
    });
    flush();
    return out;
  }
  function skivaAv(del, L, S, kap, nr, fog) {
    const a = del[0], b = del[del.length - 1];
    const fore = L[a.i - 1], efter = L[b.i + 1];
    const kapStart = fore && fore.ben !== a.ben && fore.blind === 'slut' ? kap : 0;      // benet börjar mot blindpanel
    const kapSlut = efter && efter.ben !== b.ben && efter.blind === 'start' ? kap : 0;   // benet slutar mot blindpanel
    const SP = sidorAv(L, konfSidor, S).filter(q => !q.fran);                                                               // fri gavel med sidopanel -> skivan går in till panelens insida
    const panStart = SP.some(q => q.i === a.i && q.ande === 'start') ? fog : 0;
    const panSlut = SP.some(q => q.i === b.i && q.ande === 'slut') ? fog : 0;
    const s0 = a.s0 + kapStart - panStart, s1 = b.s1 - kapSlut + panSlut, mitt = (s0 + s1) / 2;
    const bultar = [];
    for (const p of del) for (const bx of p.m.bult_x) for (const by of S.bult_y) bultar.push({ x: r2(p.s0 + p.m.bredd / 2 + bx - s0), y: by });
    let best = 0; const k = q => Math.abs(q.x - (mitt - s0)) + (q.y < 0 ? 0.1 : 0);
    bultar.forEach((q, i) => { if (k(q) < k(bultar[best])) best = i; });
    bultar.forEach((q, i) => q.fast = i === best);
    const langd = r2(s1 - s0), djup = D + S.overhang_fram, mat = (konfMat[a.i] || {}).mat || 'rostfri', t = skT(S, mat);
    const p0 = add(add(a.p0, a.d, s0 - a.s0), a.n, 0);
    return { nr, ben: a.ben, moduler: del.map(p => p.i + 1), s0, s1, langd, djup, t, mat, kapStart, kapSlut, z: a.m.stommehojd + skE(S, mat),
             grill: a.m.typ === 'grill', bult_anm: a.m.bult_anm,
             kg: r2(langd * djup * t * (mat === 'tra' ? S.tra.densitet : 8.0e-6)), bultar,
             poly: [p0, add(p0, a.d, langd), add(add(p0, a.d, langd), a.n, djup), add(p0, a.n, djup)].map(q => q.map(r2)) };
  }

  // ---- sidopaneler i bänkmaterial ---------------------------------------------------------
  // Fri gavel = ingen granne i samma ben på den sidan och inte den gavel som skruvas mot en hörnbänks blindpanel.
  // (Hörnbänkens ytterhörn är alltså en fri gavel.) konf.sidor === false stänger av.
  let konfSidor = true;
  const topp = (m, S, mat) => m.stommehojd + (m.typ === 'bank' || S.pa_grill ? skE(S, mat) + skT(S, mat) : 0);   // skivans ovansida
  // Grannens höjd som täcker vår gavel: dess skiva, eller grillen om den är lika bred som modulen (Asado-lådan).
  function tackt(q, S) {
    let h = topp(q.m, S, (konfMat[q.i] || {}).mat);
    const g = q.m.grill;
    if (g && g.bredd >= q.m.bredd - 10) h = Math.max(h, g.z0 + (S.pa_grill ? S.epdm + S.t : 0) + g.hojd);
    return h;
  }
  function sidorAv(L, pa, S) {
    if (pa === false) return [];
    const G = grannar(L), out = [];
    L.forEach((p, i) => {
      const g = G[i];
      if (i === 0) out.push({ i, ande: 'start' });                       // bara radens ändgavlar får sidopanel (vickesluring: inte gavlarna i hörnen)
      const tp = topp(p.m, S, (konfMat[i] || {}).mat);   // nivåskillnad < 40 mm mot grannen: ingen överdelspanel
      if (i === 0) {} else if (g.v && S && tackt(g.v, S) < tp - 40) out.push({ i, ande: 'start', fran: tackt(g.v, S) });   // lägre granne: stäng överdelen
      if (i === L.length - 1) out.push({ i, ande: 'slut' });
      else if (g.h && S && tackt(g.h, S) < tp - 40) out.push({ i, ande: 'slut', fran: tackt(g.h, S) });
    });
    return out;
  }
  function sidor(konf, kat) {
    const L = layout(konf, kat), P = kat.gemensamt.sidopanel, S = kat.gemensamt.skiva, fog = kat.gemensamt.fog;
    konfMat = materialer(L, konf, kat);
    return sidorAv(L, konf.sidor !== false, S).map((q, k) => {
      const p = L[q.i], harSkiva = p.m.typ === 'bank' || S.pa_grill, mat = konfMat[q.i].mat, t = mat === 'tra' ? S.tra.t : P.t;
      const djup = harSkiva ? D + S.overhang_fram : D, z0 = q.fran || (mat === 'tra' ? S.tra.golvspel_sida : P.golvspel), z1 = topp(p.m, S, mat);
      const u0 = q.ande === 'start' ? -fog - t : p.m.bredd + fog, u1 = u0 + t;   // längs modulens d
      const loc = (u, v) => add(add(p.p0, p.d, u), p.n, v).map(r2);
      const zb = K_skarvZ(kat, p.m.typ === 'bank').filter(z => z > z0 + 40 && z < z1 - 40);
      return { nr: k + 1, modul: q.i + 1, ande: q.ande, ovre: !!q.fran, t, mat, djup, z0, z1, hojd: r2(z1 - z0),
               kg: r2(djup * (z1 - z0) * t * (mat === 'tra' ? S.tra.densitet : 8.0e-6)), bultar: zb.length * kat.gemensamt.skarv.y.length, bult_z: zb,
               poly: [loc(u0, 0), loc(u1, 0), loc(u1, djup), loc(u0, djup)] };
    });
  }
  const K_skarvZ = (kat, bank) => kat.gemensamt.skarv.z_alla.concat(bank ? kat.gemensamt.skarv.z_bank_bank : []);

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
    SV.forEach(s => rader.push({ art: s.mat === 'tra' ? `Skiva ${s.nr}: trä ${s.t} × ${s.djup} × ${s.langd} mm, ${s.bultar.length} insatsmuttrar M6` : `Skiva ${s.nr}: rostfri ${s.t} × ${s.djup} × ${s.langd} mm, ${s.bultar.length} svetsbultar`, antal: 1, kg: s.kg }));
    const SVr = SV.filter(s => s.mat !== 'tra'), SVt = SV.filter(s => s.mat === 'tra');
    const nbult = SVr.reduce((s, k) => s + k.bultar.length, 0), ntb = SVt.reduce((s, k) => s + k.bultar.length, 0);
    if (nbult) {
      rader.push({ art: 'ISO 4032 M6 A4 + isolerbricka (skivans bultar)', antal: nbult });
      rader.push({ art: 'Fixbricka M6 (fast punkt, en per skiva)', antal: SVr.length });
    }
    if (ntb) rader.push({ art: 'Insatsmutter M6 A4 + ISO 7380 M6x16 A4 + bricka (träskivans skruvar underifrån)', antal: ntb });
    const SP = sidor(konf, kat);
    SP.forEach(q => rader.push({ art: `Sidopanel ${q.nr} (modul ${q.modul}, ${q.ande === 'start' ? 'början' : 'slut'}${q.ovre ? ', överdel mot lägre granne' : ''}): ${q.mat === 'tra' ? 'trä' : 'rostfri'} ${q.t} × ${q.djup} × ${q.hojd} mm, ${q.bultar} ${q.mat === 'tra' ? 'insatsmuttrar M8' : 'pinnbultar M8'}`, antal: 1, kg: q.kg }));
    const nsb = SP.reduce((s, q) => s + q.bultar, 0);
    if (nsb) rader.push({ art: 'ISO 4032 M8 A4 + distans 6 mm + EPDM-bricka (sidopanelernas bultar)', antal: nsb });
    for (const p of L) for (const t of p.tillval) { const tv = (kat.tillval || {})[t]; if (tv) rader.push({ art: tv.namn + ' (tillval, egen produkt)', fusion: tv.fusion, antal: 1, kg: tv.vikt_kg || 0 }); }
    for (const p of L) if (p.m.grill) rader.push({ art: p.m.grill.namn + ' (egen produkt)', fusion: p.m.grill.fusion, antal: 1, kg: p.m.grill.vikt_kg });
    const kg = rader.reduce((s, r) => s + (r.kg || 0), 0);
    const allp = L.flatMap(p => p.poly).concat(SP.flatMap(q => q.poly), SV.flatMap(q => q.poly));
    const xs = allp.map(q => q[0]), ys = allp.map(q => q[1]);
    return { rader, kg: Math.round(kg), matt: [r2(Math.max(...xs) - Math.min(...xs)), r2(Math.max(...ys) - Math.min(...ys))] };
  }

  function kortnamn(konf, kat) {
    const k = { bank500: 'B500', bank1000: 'B1000', horno1000: 'H1000', asado1500: 'A1500', firetable1500: 'FT1500', tizon500: 'T500', horn1000: 'HÖRN' };
    return konf.rad.map(el => { const e = norm(el); const tv = e.tillval ? [].concat(e.tillval).map(t => '+' + (((kat.tillval || {})[t] || {}).kort || t)).join('') : ''; return (e.typ === 'horn1000' ? (e.blind === 'start' ? '⌐HÖRN' : 'HÖRN¬') : (k[e.typ] || e.typ)) + tv; }).join(' | ');
  }

  return { layout, validera, skivor, sidor, skarvar, stycklista, kortnamn };
});
