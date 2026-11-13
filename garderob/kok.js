/* Kökskonfigurator v0 – samma motor som garderoben (Garderob.generera + TCN v2).
 * Kök = rader (en per vägg/ö) med moduler. Varje rad har id, start [X, Y] i rummets plan (mm) och rotation
 * (grader, radens x-riktning). Radens lokala koordinater = garderobens: x längs raden, y från front bakåt,
 * z från golv. Plan: P = start + yb·n + x·xdir − y·n, n = fronten ut (xdir vriden −90°).
 * Mått: IKEA METOD (Vicke 2026-11-13, beslut 2b). Regler: garderobens med T = 18, OSÄKER tills kök-TCN finns (3a).
 * UMD.
 */
(function (root, f) {
  if (typeof module === 'object' && module.exports) module.exports = f(require('./garderob.js'));
  else root.Kok = f(root.Garderob);
})(this, function (G) {
  'use strict';
  const OS = 'OSÄKER (ej bekräftad mot kök-TCN)';
  const METOD = { T: 18, sockel: 80, bankH: 800, bankD: 590, skena: 10, vaggD: 370, hogH: 2000, skiva: 38,
    skivaOver: 35, sockelFram: 520, skenaUnder: 60, fog: 3, vaggH: 600, bredder: [200, 300, 400, 600, 800] };
  const KMAT = { stomme: { mapp: 'Spanskiva vit 18mm_18', T: 18 }, dorr: { mapp: 'Front 18mm_18', T: 18 } };

  const TYPER = {
    lada: { namn: 'Lådskåp', kort: 'Lador', std: 600, txt: '3 eller 4 Blum-lådor, METOD-fronter' },
    bank: { namn: 'Bänkskåp', kort: 'Bankskap', std: 600, txt: 'dörr + hylla' },
    disk: { namn: 'Diskskåp', kort: 'Diskskap', std: 600, txt: 'öppen bak, ingen hylla' },
    spis: { namn: 'Spisskåp', kort: 'Spisskap', std: 600, txt: 'ugnsnisch 600 + låda, häll ovanpå' },
    dm: { namn: 'Diskmaskin', kort: 'Diskmaskin', std: 600, txt: 'integrerad, bara front' },
    horn: { namn: 'Blindhörn', kort: 'Blindhorn', std: 640, txt: 'stomme, ingen dörr på blindsidan' },
    dott: { namn: 'Dött hörn', kort: 'Dotthorn', std: 640, txt: 'ingen stomme, passbit mot grannradens front' },
    hog: { namn: 'Högskåp', kort: 'Hogskap', std: 600, txt: '200 hög, front 800 + 1200' },
    pass: { namn: 'Passbit', kort: 'Passbit', std: 50, txt: 'utfyllnad mot vägg (sågas)' },
    oppen: { namn: 'Bänk utan skåp', kort: 'Oppen', std: 600, txt: 'bara bänkskiva' },
  };
  const LADOR = { 3: [400, 200, 200], 4: [400, 200, 100, 100] };   // METOD-fronter nerifrån (nominellt)
  const STOMME = { lada: 1, bank: 1, disk: 1, spis: 1, horn: 1, hog: 1 };

  const REGLER_KOK = [
    { id: 'k_matt', text: 'METOD-mått: stomme 18, bänkskåp B×59(+skena 1)×80, ben/sockel 8, väggskåp B×37×H, högskåp B×59×200, bredder 20/30/40/60/80', status: 'IKEA METOD (ikea.com 2026-11-13)' },
    { id: 'k_bank', text: 'Bänkhöjd = sockel + 800 + bänkskiva (parameter, default 38); bänkskiva = såglista, djup = rad + 35 framöver', status: 'IKEA METOD (ikea.com 2026-11-13)' },
    { id: 'k_skena', text: 'Upphängningsskena: underkant 60 under stommens överkant (bänk-, vägg- och högskåp mot vägg)', status: 'IKEA METOD (ikea.com 2026-11-13)' },
    { id: 'k_front', text: 'Front = nominellt − 3 (597/797), underkant i stommens underkant; 2 dörrar om B > 650', status: OS },
    { id: 'k_gj', text: 'Gångjärn som garderoben: Blum 45/9,5 + montageplatta, antal efter dörrhöjd (gjAuto), hyllor flyttas ≥ 45 från plattan', status: OS },
    { id: 'k_lada', text: 'Lådfronter METOD-raster nerifrån: 3 lådor 40/20/20, 4 lådor 40/20/10/10. Frontfästets hål borras INTE (Blum-hålbild okänd)', status: OS },
    { id: 'k_blum', text: 'Blum Tandembox/Legrabox: hål i sidan = garderobens skenregel som PLATSHÅLLARE (Ø5 y 64/96/288/320, linje = lådans underkant + 76,5)', status: OS + ' · platshållare' },
    { id: 'k_disk', text: 'Diskskåp: ingen rygg, inga reglar, inga hyllor', status: OS },
    { id: 'k_spis', text: 'Spisskåp: ugnsnisch 600 över en låda (fast hylla 191); toppen är kvar som stomme – häll kräver urtag/framslå (ej löst)', status: OS },
    { id: 'k_hog', text: 'Högskåp (Vicke: hel stomme): EN stomme 2000, front delad 797 + 1197 (fog 3 vid 800), gjAuto per dörr, plattor i samma sidor, fast hylla 800 för styvhet; kyl/frys: samma stomme, inga hyllor (maskinnisch)', status: OS },
    { id: 'k_nisch', text: 'Högskåp med maskinnisch: två fasta hyllor (nischens under-/överkant), ugn 600 över 2 lådor, micro 400 på 1000', status: OS },
    { id: 'k_horn', text: 'Blindhörn (Vicke 1a): stomme B×59×80, lucka på öppna sidan (B − blindsida 600) om ≥ 150, annars täckfront; blindsidan täcks av grannradens skåp', status: OS },
    { id: 'k_dott', text: 'Dött hörn (Vicke 2026-11-13, Kök 1): ingen stomme i hörnrutan; passbit (B − 600) i frontplanet mot grannradens front, bänkskivan går över; passbit sågas med 20 övermått', status: 'EGEN (Vicke 2026-11-13)' },
    { id: 'k_dm', text: 'Diskmaskin: bara front 597×797, inga beslagshål (maskinens mall)', status: OS },
    { id: 'k_vagg', text: 'Väggskåp: djup 370, överkant = sockel + högskåp (linjerar), varning om bänk–väggskåp < 450 (rek. 500–600)', status: OS },
    { id: 'k_rad', text: 'Rader: en per vägg/ö, start + rotation i rummets plan; hörn = blindhörnsmodul 640', status: 'EGEN (v0)' },
  ];
  const ANV = ['kant5', 'bak5', 'spar', 'rygg', 'hylla', 'dorr'];
  const REGLER = [...REGLER_KOK, ...G.REGLER.filter(r => ANV.includes(r.id)).map(r => Object.assign({}, r, { status: `${OS} · garderob: ${r.status}` }))];

  function jamn(a, b, n) {
    const st = (b - a) / (n + 1), u = [];
    for (let i = 1; i <= n; i++) u.push(Math.round((a + st * i) / 10) * 10);
    return u;
  }
  function undvik(hyllor, plattor) {   // flytta hylla uppåt tills den går fri från montageplattorna
    return hyllor.map(m => { let i = 0; while (i++ < 20 && plattor.some(p => Math.abs(p - m) < 45)) m += 10; return m; });
  }
  const kontur = (L, B, T) => ({ typ: 'kontur', sida: 1, z: -(T + 2), start: [L / 2, 0], pts: [[L, 0], [L, B], [0, B], [0, 0], [L / 2, 0]], verktyg: 1050 });
  const r2 = x => Math.round(x * 100) / 100;

  function bredder(rad) {
    const auto = rad.moduler.filter(m => !m.bredd);
    const fasta = rad.moduler.filter(m => m.bredd).reduce((a, m) => a + m.bredd, 0);
    if (!rad.langd || !auto.length) return rad.moduler.map(m => m.bredd || TYPER[m.typ].std);
    const rest = rad.langd - fasta, per = Math.floor(rest / auto.length);
    let extra = rest - per * auto.length;
    return rad.moduler.map(m => m.bredd || (per + (extra-- > 0 ? 1 : 0)));
  }

  // dörrsegment [{zb, nom}] -> garderobens dorrar
  function dorrar(W, m, seg) {
    const antal = m.dorrar != null ? m.dorrar : (W > 650 ? 2 : 1);
    if (!antal) return null;
    const DB = antal === 2 ? W / 2 - METOD.fog : W - METOD.fog;
    return Object.assign({ antal, bredd: DB, segment: seg.map(s => ({ zb: s.zb, DH: s.nom - METOD.fog })) }, antal === 1 ? { hand: m.hand || 'v' } : {});
  }
  const plattor = d => d ? d.segment.flatMap(s => G.gjAuto(s.DH).map(c => s.zb + c)) : [];

  // en moduls stomme(ar): returnerar [{konfig, rad:'bank'|'hog'|'vagg', z0, y0, lador:[{zb, nom}], extra:[...]}]
  function modulBlock(sys, rad, m, W, nr) {
    const T = METOD.T, D = rad.djup - rad.skena, sock = sys.sockel, ut = [];
    const jobb = `${sys.jobb} ${rad.id}${nr}`;
    const bas = (skap, d) => ({ namn: `${sys.namn} M${nr}`, jobb, T, mat: KMAT, bredd: W, skap: [Object.assign({ djup: D, bak: 'spar', hyllor: [], lador: 0 }, skap)], dorrar: d });
    const H = METOD.bankH;
    if (m.typ === 'bank' || m.typ === 'disk' || m.typ === 'horn') {
      // blindhörn (Vicke 1a): lucka på öppna sidan (B − blindsida) om den är ≥ 150, gångjärn på sidan bort från blindsidan
      const oppen = W - (m.blindB || 600);
      const d = m.typ !== 'horn' ? dorrar(W, m, [{ zb: 0, nom: H }])
        : oppen >= 150 ? Object.assign(dorrar(W, { dorrar: 1, hand: m.blind === 'h' ? 'v' : 'h' }, [{ zb: 0, nom: H }]), { bredd: oppen - METOD.fog }) : null;
      const hy = m.typ === 'disk' ? [] : undvik(jamn(T, H - T, m.hyllor != null ? m.hyllor : 1), plattor(d));
      ut.push({ konfig: bas({ hojd: H, bak: m.typ === 'disk' ? 'ingen' : 'spar', hyllor: hy }, d), rad: 'bank', z0: sock });
    } else if (m.typ === 'lada') {
      const fr = LADOR[m.lador === 4 ? 4 : 3];
      let z = 0; const lador = fr.map(nom => { const o = { zb: z, nom }; z += nom; return o; });
      ut.push({ konfig: bas({ hojd: H }, null), rad: 'bank', z0: sock, lador });
    } else if (m.typ === 'spis') {
      ut.push({ konfig: bas({ hojd: H, fasta: [200 - T / 2] }, null), rad: 'bank', z0: sock, lador: [{ zb: 0, nom: 200 }],
        maskin: { namn: 'Ugn (köpdel)', z0: 200, z1: 800 }, hall: true });
    } else if (m.typ === 'hog') {
      const HH = sys.hogH, n = m.nisch || null;
      if (n === 'ugn' || n === 'micro') {
        const z0 = n === 'ugn' ? 400 : 1000, h = n === 'ugn' ? 600 : 400;
        const seg = [{ zb: z0 + h, nom: HH - z0 - h }];
        let lador = [];
        if (z0 <= 800) lador = Array.from({ length: z0 / 200 }, (_, i) => ({ zb: 200 * i, nom: 200 }));
        else seg.unshift({ zb: 0, nom: z0 });
        const d = dorrar(W, m, seg), pl = plattor(d);
        const hy = [...(z0 > 800 ? jamn(T, z0 - T, 1) : []), ...jamn(z0 + h + T, HH - T, m.hyllor != null ? m.hyllor : 2)];
        ut.push({ konfig: bas({ hojd: HH, fasta: [z0 - T / 2, z0 + h + T / 2], hyllor: undvik(hy, pl) }, d), rad: 'hog', z0: sock, lador,
          maskin: { namn: n === 'ugn' ? 'Ugn (köpdel)' : 'Mikro (köpdel)', z0, z1: z0 + h } });
      } else {
        const del = m.fronter === 'hel' ? [{ zb: 0, nom: HH }] : [{ zb: 0, nom: 800 }, { zb: 800, nom: HH - 800 }];
        const d = dorrar(W, m, del), pl = plattor(d);
        const kyl = n === 'kyl';
        const fasta = kyl || m.fronter === 'hel' ? [] : [800];
        const hy = kyl ? [] : (m.fronter === 'hel' ? jamn(T, HH - T, m.hyllor != null ? m.hyllor : 4)
          : [...jamn(T, 800 - T, 1), ...jamn(800 + T, HH - T, m.hyllor != null ? m.hyllor : 3)]);
        ut.push({ konfig: bas({ hojd: HH, fasta, hyllor: undvik(hy, pl) }, d), rad: 'hog', z0: sock, kyl });
      }
    }
    // väggskåp ovanför (inte ovanför högskåp)
    if (m.vagg && m.typ !== 'hog' && rad.vagg !== false) {
      const VH = m.vaggH || sys.vaggH, ok = sys.vaggOK || sys.sockel + sys.hogH;
      const d = dorrar(W, { dorrar: m.vaggDorrar, hand: m.hand }, [{ zb: 0, nom: VH }]);
      const hy = undvik(jamn(T, VH - T, m.vaggHyllor != null ? m.vaggHyllor : (VH >= 800 ? 2 : VH > 400 ? 1 : 0)), plattor(d));
      ut.push({ konfig: { namn: `${sys.namn} M${nr}V`, jobb: jobb + 'V', T, mat: KMAT, bredd: W, skap: [{ hojd: VH, djup: METOD.vaggD, bak: 'spar', hyllor: hy, lador: 0 }], dorrar: d },
        rad: 'vagg', z0: ok - VH, y0: rad.djup - rad.skena - METOD.vaggD, vagg: true });
    }
    return ut;
  }

  // Blum-låda: front (TCN) + skenhål i sidorna (platshållare = garderobens skenregel)
  function laddor(ut, k, lador) {
    const T = k.T, W = k.bredd, H = k.skap[0].hojd, FT = KMAT.dorr.T;
    let n = Math.max(0, ...ut.delar.map(d => +(/^\d+_(\d+)_/.exec(d.fil) || [0, 0])[1]));
    const sv = ut.delar.find(d => d.typ === 'Sida vänster'), sh = ut.delar.find(d => d.typ === 'Sida höger');
    lador.forEach((l, i) => {
      const FB = W - METOD.fog, FH = l.nom - METOD.fog;
      const linje = Math.max(l.zb, T) + 2 + 74.5;
      [64, 96, 288, 320].forEach(y => {
        sv.ops.push({ typ: 'hal', sida: 1, x: r2(H - linje), y, z: -13, d: 5, genom: 0 });
        sh.ops.push({ typ: 'hal', sida: 1, x: r2(linje), y, z: -13, d: 5, genom: 0 });
      });
      ut.delar.push({ skap: 1, fil: `1_${++n}_Drawer front_1.tcn`, mapp: KMAT.dorr.mapp, typ: `Lådfront ${i + 1}`, overmatt: 2.5,
        namn: `Drawer front ${k.jobb} L=${G.fmt(FB)} B=${G.fmt(FH)} T=${FT}`, L: FB, B: FH, T: FT, ops: [kontur(FB, FH, FT)] });
    });
    ut.beslag.push({ namn: 'Blum Tandembox/Legrabox-låda (köpdel) ⚠ hålbild ej bekräftad', antal: lador.length });
  }

  function generera(sys0) {
    const sys = JSON.parse(JSON.stringify(sys0));
    sys.namn = sys.namn || 'Kök'; sys.jobb = sys.jobb || 'Kok';
    sys.sockel = sys.sockel != null ? sys.sockel : METOD.sockel;
    sys.skiva = sys.skiva != null ? sys.skiva : METOD.skiva;
    sys.hogH = sys.hogH || METOD.hogH; sys.vaggH = sys.vaggH || METOD.vaggH;
    sys.rader = sys.rader || [];
    const su = { kok: true, sys, rader: [], moduler: [], delar: [], saglista: [], beslag: [], varningar: [], info: [], regler: REGLER, extra3d: [], extraFront: [] };
    const T = METOD.T, bankTopp = sys.sockel + METOD.bankH, bankHojd = bankTopp + sys.skiva;
    let nr = 0, fx = 0;   // fx: radens x-förskjutning i frontritningen (raderna efter varandra)
    sys.rader.forEach((rad, ri) => {
      rad.id = rad.id || String.fromCharCode(65 + ri);
      rad.djup = rad.djup || (METOD.bankD + METOD.skena);
      rad.skena = rad.skena != null ? rad.skena : (rad.vagg === false ? 0 : METOD.skena);
      const W = bredder(rad), yb = rad.djup;
      const R = { id: rad.id, namn: rad.namn || `Rad ${rad.id}`, start: rad.start || [0, 0], rot: rad.rot || 0, yb, vagg: rad.vagg !== false, langd: W.reduce((a, b) => a + b, 0), fx, moduler: [] };
      su.rader.push(R);
      const E = (o) => su.extra3d.push(Object.assign({ rad: ri }, o));
      const F = (o) => su.extraFront.push(Object.assign({ t: 'rect', stroke: '#555' }, o, { x: o.x + fx }));
      su.extraFront.push({ t: 'text', x: fx + R.langd / 2, y: -130, s: `${R.id} · ${R.namn}`, anchor: 'middle', size: 10, color: '#5a1a14' });
      let x = 0, skivSeg = null;
      const avslutaSkiva = () => {
        if (!skivSeg) return;
        const L = skivSeg[1] - skivSeg[0], Bd = rad.skivaDjup || (rad.djup + (rad.skivaOver != null ? rad.skivaOver : METOD.skivaOver));
        const over = rad.skivaOver != null ? rad.skivaOver : METOD.skivaOver;
        if (rad.skiva !== false) {
          su.saglista.push({ namn: `Bänkskiva ${rad.id} (${skivSeg[2].join('+')})`, L, B: Bd, T: sys.skiva, material: 'Bänkskiva (köpdel/sågas, ingen TCN)' });
          E({ x0: skivSeg[0], x1: skivSeg[1], y0: -over, y1: Bd - over, z0: bankTopp, z1: bankHojd, mat: 'skiva', namn: `Bänkskiva ${rad.id} ${L}×${Bd}×${sys.skiva}` });
          F({ x: skivSeg[0], y: bankTopp, w: L, h: sys.skiva, fill: '#9c8f7a' });
        }
        skivSeg = null;
      };
      rad.moduler.forEach((m, mi) => {
        nr++;
        const Wm = W[mi], typ = TYPER[m.typ] || TYPER.bank;
        const mapp0 = `${rad.id}-M${nr} ${typ.kort} ${Wm}`;
        const blocks = modulBlock(sys, rad, m, Wm, nr);
        const beskr = [`${typ.namn} ${Wm}`];
        blocks.forEach(b => {
          const ut = G.generera(b.konfig);
          if (b.lador && b.lador.length) laddor(ut, ut.konfig, b.lador);
          const mapp = b.vagg ? `${rad.id}-M${nr}V Vaggskap ${Wm}` : mapp0;
          const mod = { nr, typ: b.vagg ? 'vagg' : m.typ, typNamn: b.vagg ? 'Väggskåp' : typ.namn, rad: ri, radId: rad.id, x0: x, y0: b.y0 || 0, z0: b.z0, bredd: Wm, konfig: ut.konfig, ut, mapp, utanEtikett: !!b.vagg };
          mod.beskr = `${rad.id}-M${nr}${b.vagg ? 'V' : ''} ${mod.typNamn} ${Wm}×${ut.konfig.skap[0].djup}×${ut.konfig.hojd}` +
            (b.lador && b.lador.length ? `, ${b.lador.length} lådor (${b.lador.map(l => l.nom / 10).join('/')})` : '') +
            (ut.konfig.dorrar ? `, ${ut.konfig.dorrar.antal} × ${ut.konfig.dorrar.seg.map(s => G.fmt(s.DH)).join('+')} dörr` : '') +
            (ut.konfig.skap[0].hyllor.length ? `, ${ut.konfig.skap[0].hyllor.length} hyllor` : '') + (b.maskin ? `, ${b.maskin.namn}` : '') + (b.kyl ? ', kyl/frys' : '') +
            (ut.konfig.skap[0].bak !== 'spar' ? ', ingen rygg' : '');
          su.moduler.push(mod); R.moduler.push(su.moduler.length - 1);
          ut.delar.forEach(d => su.delar.push(Object.assign({}, d, { modul: nr, modulMapp: mapp, etikett: `${rad.id}-M${nr}${b.vagg ? 'V' : ''}/` + d.fil.replace('.tcn', '') })));
          ut.saglista.forEach(s2 => su.saglista.push(Object.assign({}, s2, { namn: `M${nr} ${s2.namn}` })));
          ut.beslag.forEach(bb => su.beslag.push(bb));
          ut.varningar.forEach(v => su.varningar.push(`${rad.id}-M${nr}${b.vagg ? 'V' : ''}: ${v}`));
          // lådfronter + maskiner i 3D/front
          (b.lador || []).forEach(l => {
            E({ x0: x + 1.5, x1: x + Wm - 1.5, y0: -19, y1: -1, z0: b.z0 + l.zb, z1: b.z0 + l.zb + l.nom - 3, mat: 'dorr', front: true, namn: `M${nr} lådfront ${l.nom / 10}` });
            F({ x: x + 1.5, y: b.z0 + l.zb, w: Wm - 3, h: l.nom - 3, fill: 'rgba(185,138,85,0.55)', stroke: '#5b3b17', dorr: true });
            F({ x: x + Wm / 2 - 60, y: b.z0 + l.zb + l.nom - 40, w: 120, h: 8, fill: '#555', dorr: true });
          });
          if (b.maskin) {
            E({ x0: x + T + 2, x1: x + Wm - T - 2, y0: -18, y1: 540, z0: b.z0 + b.maskin.z0 + 2, z1: b.z0 + b.maskin.z1 - 2, mat: 'maskin', namn: b.maskin.namn });
            F({ x: x + T, y: b.z0 + b.maskin.z0, w: Wm - 2 * T, h: b.maskin.z1 - b.maskin.z0, fill: '#3b3b3b' });
          }
          if (b.hall) E({ x0: x + 40, x1: x + Wm - 40, y0: 40, y1: 540, z0: bankHojd, z1: bankHojd + 6, mat: 'maskin', namn: 'Häll (köpdel)' });
          // skena bakom stommar mot vägg
          if (R.vagg) { const top = b.z0 + ut.konfig.hojd; E({ x0: x + 20, x1: x + Wm - 20, y0: yb - rad.skena, y1: yb, z0: top - METOD.skenaUnder, z1: top - METOD.skenaUnder + 40, mat: 'stang', namn: 'Upphängningsskena' }); }
          if (b.vagg) su.info.push(`${rad.id}-M${nr}V: väggskåp underkant ${b.z0}, överkant ${b.z0 + ut.konfig.hojd}, skena underkant ${b.z0 + ut.konfig.hojd - METOD.skenaUnder}.`);
          if (b.vagg && b.z0 - bankHojd < 450) su.varningar.push(`${rad.id}-M${nr}V: bara ${b.z0 - bankHojd} mellan bänkskiva och väggskåp (rek. 500–600).`);
        });
        // moduler utan stomme
        if (m.typ === 'dm') {
          const FB = Wm - 3, FH = METOD.bankH - 3, FT = KMAT.dorr.T;
          const d = { skap: 1, fil: '1_1_Dishwasher front_1.tcn', mapp: KMAT.dorr.mapp, typ: 'Diskmaskinsfront', overmatt: 2.5, namn: `Dishwasher front ${sys.jobb} ${rad.id}${nr} L=${FH} B=${FB} T=${FT}`, L: FH, B: FB, T: FT, ops: [kontur(FH, FB, FT)] };
          su.delar.push(Object.assign(d, { modul: nr, modulMapp: mapp0, etikett: `${rad.id}-M${nr}/1_1_Dishwasher front_1` }));
          su.beslag.push({ namn: 'Integrerad diskmaskin 60 (köpdel)', antal: 1 });
          su.moduler.push({ nr, typ: 'dm', typNamn: typ.namn, rad: ri, radId: rad.id, x0: x, y0: 0, z0: sys.sockel, bredd: Wm, konfig: null, ut: null, mapp: mapp0, beskr: `${rad.id}-M${nr} Diskmaskin ${Wm} (bara front ${FB}×${FH})` });
          R.moduler.push(su.moduler.length - 1);
          E({ x0: x + 1.5, x1: x + Wm - 1.5, y0: -19, y1: -1, z0: sys.sockel, z1: sys.sockel + FH, mat: 'dorr', front: true, namn: `M${nr} diskmaskinsfront` });
          E({ x0: x + 2, x1: x + Wm - 2, y0: 0, y1: 560, z0: sys.sockel, z1: bankTopp - 2, mat: 'maskin', namn: 'Diskmaskin (köpdel)' });
          F({ x: x + 1.5, y: sys.sockel, w: FB, h: FH, fill: '#c8dbe8', stroke: '#345' });
          F({ x: x + Wm / 2 - 80, y: sys.sockel + FH - 50, w: 160, h: 8, fill: '#555' });
        } else if (m.typ === 'dott') {
          const syn = Wm - 600, xb = m.pass === 'h' ? x : x + 600;   // passbiten på sidan mot grannraden ('v' = default, som blindhörnet)
          su.saglista.push({ namn: `${rad.id}-M${nr} dött hörn passbit`, L: METOD.bankH, B: syn + 20, T: KMAT.dorr.T, material: 'Front 18 (sågas, anpassas mot grannradens front)' });
          su.moduler.push({ nr, typ: 'dott', typNamn: typ.namn, rad: ri, radId: rad.id, x0: x, y0: 0, z0: sys.sockel, bredd: Wm, konfig: null, ut: null, mapp: mapp0, beskr: `${rad.id}-M${nr} Dött hörn ${Wm} (passbit ${syn})` });
          R.moduler.push(su.moduler.length - 1);
          if (syn > 0) { E({ x0: xb, x1: xb + syn, y0: -19, y1: 0, z0: sys.sockel, z1: bankTopp, mat: 'stomme', namn: `Passbit dött hörn ${syn}` }); F({ x: xb, y: sys.sockel, w: syn, h: METOD.bankH, fill: '#ddd' }); }
          F({ x: m.pass === 'h' ? x + syn : x, y: sys.sockel, w: 600, h: METOD.bankH, fill: 'none', stroke: '#aaa', dash: [6, 4] });
          su.extraFront.push({ t: 'text', x: fx + x + Wm / 2, y: sys.sockel + 330, s: 'dött hörn', anchor: 'middle', size: 8, color: '#888' });
          if (syn < 50) su.info.push(`⚠ ${rad.id}-M${nr}: dött hörn med passbit ${syn} – bara ~${syn - 19} mm från grannradens front till hörnet; handtag djupare än så krockar med lådorna intill (greppfri front/korta handtag, eller passbit ≥ 50).`);
        } else if (m.typ === 'pass' || m.typ === 'oppen') {
          if (m.typ === 'pass') su.saglista.push({ namn: `${rad.id}-M${nr} passbit`, L: METOD.bankH, B: Wm + 20, T, material: 'Front 18 (sågas, anpassas mot vägg)' });
          su.moduler.push({ nr, typ: m.typ, typNamn: typ.namn, rad: ri, radId: rad.id, x0: x, y0: 0, z0: sys.sockel, bredd: Wm, konfig: null, ut: null, mapp: mapp0, beskr: `${rad.id}-M${nr} ${typ.namn} ${Wm}` });
          R.moduler.push(su.moduler.length - 1);
          if (m.typ === 'pass') { E({ x0: x, x1: x + Wm, y0: -19, y1: 0, z0: sys.sockel, z1: bankTopp, mat: 'stomme', namn: `Passbit ${Wm}` }); F({ x, y: sys.sockel, w: Wm, h: METOD.bankH, fill: '#ddd' }); }
          else F({ x, y: sys.sockel, w: Wm, h: METOD.bankH, fill: 'none', stroke: '#aaa', dash: [6, 4] });
        }
        if (m.typ === 'horn' && Wm - (m.blindB || 600) >= 150) {
          su.info.push(`${rad.id}-M${nr}: blindhörn, lucka ${Wm - (m.blindB || 600) - METOD.fog} på öppna sidan (blindsida ${m.blindB || 600}).`);
        } else if (m.typ === 'horn') {
          const syn = Wm - (m.blindB || 600);
          su.info.push(`⚠ ${rad.id}-M${nr}: blindhörn ${Wm} – öppna sidan är bara ${syn} mm (grannraden täcker ${m.blindB || 600}); lucka ryms inte, täckfront ${syn} i stället. Bredare hörnskåp eller dött hörn behövs för en lucka.`);
          su.saglista.push({ namn: `${rad.id}-M${nr} blindhörn täckfront (synlig del)`, L: METOD.bankH - 3, B: Math.max(syn, 0), T: KMAT.dorr.T, material: 'Front 18 (sågas) ⚠' });
          const xb = m.blind === 'h' ? x : x + 600;   // blindsidan = 'v' (vänster) som default
          if (syn > 0) { E({ x0: xb, x1: xb + syn, y0: -19, y1: -1, z0: sys.sockel, z1: bankTopp - 3, mat: 'dorr', front: true, namn: 'Blindhörn täckfront' }); F({ x: xb, y: sys.sockel, w: syn, h: METOD.bankH - 3, fill: 'rgba(185,138,85,0.55)', stroke: '#5b3b17', dorr: true }); }
          F({ x: m.blind === 'h' ? x + syn : x, y: sys.sockel + 300, w: 600, h: 0.1, stroke: '#c8321a', dash: [6, 4] });
          su.extraFront.push({ t: 'text', x: fx + x + Wm / 2, y: sys.sockel + 330, s: 'blind', anchor: 'middle', size: 8, color: '#c8321a' });
        }
        if (m.typ === 'hog') avslutaSkiva();
        if (m.typ !== 'hog') { if (!skivSeg) skivSeg = [x, x, []]; skivSeg[1] = x + Wm; skivSeg[2].push(Wm); }
        x += Wm;
        if (m.typ === 'lada' && Wm < 400) su.varningar.push(`${rad.id}-M${nr}: lådskåp < 400 (Blum-låda).`);
        if (!METOD.bredder.includes(Wm) && STOMME[m.typ] && m.typ !== 'horn') su.info.push(`${rad.id}-M${nr}: ${Wm} är ingen METOD-bredd (specialfront).`);
      });
      avslutaSkiva();
      // sockel (ben 8 + sockellist) under alla moduler med stomme/front, framkant 520 från väggen
      const ySock = rad.vagg === false ? 80 : yb - METOD.sockelFram;
      if (sys.sockel) { E({ x0: 0, x1: x, y0: ySock, y1: ySock + 16, z0: 0, z1: sys.sockel - 2, mat: 'sockel', namn: `Sockel ${rad.id} ${x}` }); F({ x: 0, y: 0, w: x, h: sys.sockel, fill: '#eee', stroke: '#888' });
        su.saglista.push({ namn: `Sockel ${rad.id}`, L: x, B: sys.sockel - 2, T: 16, material: 'Sockel (köpdel/sågas)' }); }
      if (R.vagg) E({ x0: -40, x1: x + 40, y0: yb, y1: yb + 40, z0: 0, z1: sys.rumH || 2400, mat: 'vagg', namn: `Vägg ${rad.id}` });
      if (rad.osaker) su.info.push(`⚠ ${rad.id}: ${rad.osaker}`);
      fx += x + 600;
    });
    const sum = new Map(); su.beslag.forEach(b => sum.set(b.namn, (sum.get(b.namn) || 0) + b.antal));
    su.beslag = [...sum].map(([namn, antal]) => ({ namn, antal }));
    const benAntal = su.moduler.filter(m => m.konfig && m.typ !== 'vagg').length * 4;
    if (benAntal) su.beslag.push({ namn: 'Ben METOD 8 cm', antal: benAntal });
    const skenL = su.rader.filter(r => r.vagg).reduce((a, r) => a + r.langd, 0);
    if (skenL) su.beslag.push({ namn: `Upphängningsskena (totalt ${skenL} mm bänk/hög + väggskåp)`, antal: su.rader.filter(r => r.vagg).length });
    su.bankHojd = bankHojd; su.T = T;
    su.bredd = fx - 600; su.hojd = Math.max(...su.moduler.filter(m => m.konfig).map(m => m.z0 + m.konfig.hojd), bankHojd);
    su.info.unshift(`Bänkhöjd ${bankHojd} (sockel ${sys.sockel} + stomme ${METOD.bankH} + skiva ${sys.skiva}) · högskåp överkant ${sys.sockel + sys.hogH} · stomme T = ${T}.`);
    su.info.push(`${su.rader.length} rader · ${nr} moduler · ${su.delar.length} TCN-filer`);
    return su;
  }

  // ---------- exempel ----------
  // Kök 1 = Vickes köksplan (filer/kok1, bild 2026-11-13). Plan: X åt höger, Y uppåt i bilden, origo nedre vänstra hörnet.
  const KOK1 = {
    namn: 'Kök 1 (Vickes plan)', jobb: 'Kok1', sockel: 80, skiva: 38, hogH: 2000, rum: { bredd: 5400, djup: 3590 },
    rader: [
      { id: 'A', namn: 'Nedre väggen (bänk)', start: [5400, 0], rot: 180, moduler: [
        { typ: 'horn', bredd: 640, blind: 'v' }, { typ: 'lada', bredd: 600 }, { typ: 'disk', bredd: 600 }, { typ: 'dm', bredd: 600 },
        { typ: 'lada', bredd: 600 }, { typ: 'lada', bredd: 600 }, { typ: 'pass', bredd: 360 }] },
      { id: 'B', namn: 'Höger vägg (bänk)', start: [5400, 2640], rot: 270, moduler: [
        { typ: 'lada', bredd: 800 }, { typ: 'spis', bredd: 600 }, { typ: 'lada', bredd: 600 }] },
      { id: 'C', namn: 'Övre väggen (högskåp)', start: [1050, 3590], rot: 0, moduler: [
        { typ: 'hog', bredd: 600 }, { typ: 'hog', bredd: 600 }, { typ: 'hog', bredd: 600 }, { typ: 'hog', bredd: 600 }, { typ: 'hog', bredd: 600, nisch: 'kyl' }] },
      // Vicke 2a: ö = 2×2 lådskåp rygg mot rygg, stommar 400 djupa, + bänkdel 600 med ho till vänster (diskskåp)
      { id: 'D', namn: 'Köksö, sida mot nedre väggen', start: [550, 1900], rot: 0, djup: 400, vagg: false, skivaDjup: 850, skivaOver: 25,
        osaker: 'öns djup 2 × 400 är preliminärt (grov skala i planen); ho-delen till vänster = diskskåp 600 × 400.',
        moduler: [{ typ: 'disk', bredd: 600 }, { typ: 'lada', bredd: 600 }, { typ: 'lada', bredd: 600 }] },
      { id: 'E', namn: 'Köksö, sida mot högskåpen', start: [2350, 1900], rot: 180, djup: 400, vagg: false, skiva: false,
        moduler: [{ typ: 'lada', bredd: 600 }, { typ: 'lada', bredd: 600 }] },
    ],
  };
  // litet exempel med väggskåp (för test/demonstration av väggskåpsraden)
  const RAK = {
    namn: 'Rakt kök med väggskåp', jobb: 'KokRak', sockel: 80, skiva: 38, hogH: 2000, vaggH: 600,
    rader: [{ id: 'A', namn: 'Vägg', start: [0, 0], rot: 0, moduler: [
      { typ: 'hog', bredd: 600, nisch: 'ugn' }, { typ: 'lada', bredd: 600, vagg: true }, { typ: 'disk', bredd: 800, vagg: true },
      { typ: 'bank', bredd: 400, vagg: true }, { typ: 'lada', bredd: 600, lador: 4, vagg: true }, { typ: 'hog', bredd: 600, nisch: 'kyl', fronter: 'hel' }] }],
  };

  return { METOD, KMAT, TYPER, LADOR, REGLER, generera, bredder, KOK1, RAK, jamn };
});
