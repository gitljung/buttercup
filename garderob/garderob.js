/* Garderobskonfigurator – generator (UMD: webb + node).
 * konfig -> delar (delmodell: namn, L, B, T, overmatt, ops) -> TCN v2 (skåpprogrammets dialekt).
 * Reglerna är härledda ur Acaciagatan B.1.08 (56 TCN-filer). Regler som bara har EN datapunkt
 * är märkta OSÄKER och listas i resultat.regler så att de syns i PDF:en.
 * Koordinater: skåpets x = från golv/botten uppåt, y = från front bakåt.
 */
(function (root, f) {
  if (typeof module === 'object' && module.exports) module.exports = f();
  else root.Garderob = f();
})(this, function () {
  'use strict';

  // ---------- talformat (som tcn_del.fmt) ----------
  function fmt(x) {
    x = Number(x);
    if (x === Math.trunc(x)) return String(Math.trunc(x));
    return String(Number(x.toFixed(6)));
  }
  const r2 = x => Math.round(x * 100) / 100;

  // ---------- regelbok ----------
  const REGLER = [
    { id: 'kant5', text: 'Kanttappar Ø8 stomme: 20 · 26,5 % · 50 % · 73,5 % · L−20 (kantdjup 21)', status: 'säker (3 djup)' },
    { id: 'bak5', text: 'Ryggskruv/fast hylla bakkant: a · a+0,2537(b−a) · mitt · spegel · b', status: 'OSÄKER (1 mått)' },
    { id: 'lada4', text: 'Lådans tapprader (4 hål) – tabell för sidhöjd 200', status: 'OSÄKER (1 lådhöjd)' },
    { id: 'spar', text: 'Ryggspår: y = D−25,5, 2 snitt (T1161 3,6) = 6,5 bred, djup 7,5; topp/botten 2 mm kortare djup', status: 'säker' },
    { id: 'rygg', text: 'Rygg 6,5: (H−2T+14) × (Bi+14)', status: 'säker' },
    { id: 'hylla', text: 'Hylltappsrad 3 hål c/c 32, rader y=41 och hyllans bakkant−37; hylla 2 mm in från front', status: 'säker' },
    { id: 'dorr', text: 'Dörr: kopp Ø35 21,5 från kant, skruv Ø8 ±22,5 / 31; montageplatta Ø5 y 23/55 vid kopp−underhäng', status: 'säker' },
    { id: 'distans', text: 'Med dörrar: distansklossar 20 mm per sida, lådan 40 mm smalare', status: 'säker' },
    { id: 'skena', text: 'Lådskena: hål y 64/96 + 288/320, linje 96,5 + 260·i från botten; låda 410 djup', status: 'OSÄKER (1 skåpdjup)' },
    { id: 'stang', text: 'Klädstång: fäste 2×Ø5 c/c 32 vertikalt, mitt i användbart djup', status: 'EGEN (ej i TCN-underlag)' },
    { id: 'hel', text: 'Hel garderob: en stomme i full höjd, fast hylla (lådor: ovanför lådorna, hängdel: hatthylla H−600 med stång 70 under, hyllor: i delningshöjd), 4 gångjärn (översta DH−90)', status: 'EGEN (ej i TCN-underlag)' },
    { id: 'dorrdel', text: 'Delad modul (nedre + övre stomme): en dörr per stomme, fog 3 mitt på delningen; nedre dörren går ner under-mått, övre slutar i överkant. Gångjärn per dörr efter höjd (Blum): ≤900 → 2, ≤1600 → 3, ≤2000 → 4, ≤2400 → 5, annars 6; 90 från ändarna, jämnt mellan; montageplattor i respektive stommes sidor', status: 'EGEN (Vicke 2026-11-13; Acaciagatan-facit har odelad dörr)' },
    { id: 'passbit', text: 'Passbit mot nischvägg på gångjärnssidan ≥ 30 så att dörren (17) går fri vid öppning', status: 'OSÄKER (Acaciagatan har 30)' },
    { id: 'klots', text: 'Distansklots 460×425: tappar 100/L−100, start 75 från botten', status: 'OSÄKER (2 lådor)' },
  ];

  const MATG = {
    stomme: { mapp: 'Ahorn 20mm_20', T: 20 },
    lada: { mapp: 'Egger H1334 15mm Span_15', T: 15 },
    distans: { mapp: 'Egger H1334 15mm Span_20', T: 20 },
    regel: { mapp: 'Egger H1334 19mm Span_19', T: 19 },
    dorr: { mapp: 'Faner_ek_17_17', T: 17 },
    rygg: { mapp: 'Fanerad MDF 6,5_6', T: 6.5 },
  };

  // ---------- hålrader ----------
  // 5-hålsrad längs en kant: värden + ordning som skåpprogrammet skriver dem
  function rad5stom(L) { // [a, .265L, mitt, .735L, b]
    return [20, r2(0.265 * L), r2(L / 2), r2(0.735 * L), L - 20];
  }
  const ORD_A = [2, 4, 0, 3, 1]; // mitt, sista, första, 3:e, 2:a
  const ORD_B = [2, 0, 4, 3, 1]; // mitt, första, sista, 3:e, 2:a
  const ord = (v, o) => o.map(i => v[i]);
  function rad5bak(a, b) {
    const f = 208.07 / 820; // OSÄKER: en datapunkt (870 inv. bredd)
    const p = r2(a + f * (b - a));
    return [a, p, r2((a + b) / 2), r2(a + b - p), b];
  }
  // låda, sidhöjd 200 (OSÄKER: tabell)
  const LADA = {
    200: { front: [25, 68.53, 122.98, 166.5], sidakant: [20, 63.52, 117.98, 161.5],
           sidayta: [22, 64.82, 118.68, 161.5], bak: [20, 62.82, 116.68, 159.5] },
  };
  const ORD4 = [2, 1, 3, 0];

  // ---------- op-byggare ----------
  const kontur = (L, B, T) => ({ typ: 'kontur', sida: 1, z: -(T + 2), start: [L / 2, 0],
    pts: [[L, 0], [L, B], [0, B], [0, 0], [L / 2, 0]], verktyg: 1050 });
  const hal = (sida, x, y, z, d, genom = 0) => ({ typ: 'hal', sida, x, y, z, d, genom });
  const kanthal = (sida, x, T) => hal(sida, x, T / 2, -21, 8);
  const ytaØ8 = (x, y) => hal(1, x, y, -10, 8);
  const ytaØ5 = (x, y) => hal(1, x, y, -13, 5);
  const spar2 = (y, x0, langd) => [0, 2.9].map(dy => ({ typ: 'spar', sida: 1, y: r2(y + dy), x0, langd, djup: 7.5, blad: 1161 }));
  const hylltapp = (y, langd, steg) => ({ typ: 'hylltapp', sida: 1, y, langd, steg, delning: 32, z: -13, d: 5 });

  function del(o) { return Object.assign({ overmatt: 2.5, ops: [] }, o); }

  // gångjärn per dörr efter dörrhöjd (Blum-tabell), 90 från ändarna, jämnt mellan
  function gjAuto(DH) {
    const n = DH <= 900 ? 2 : DH <= 1600 ? 3 : DH <= 2000 ? 4 : DH <= 2400 ? 5 : 6;
    const u = [];
    for (let i = 0; i < n; i++) u.push(Math.round((90 + i * (DH - 180) / (n - 1)) * 2) / 2);
    return u;
  }

  // ---------- normalisera konfig ----------
  function normalisera(k) {
    k = JSON.parse(JSON.stringify(k));
    k.T = k.T || 20;
    k.jobb = k.jobb || 'Garderob';
    k.dorrar = k.dorrar || null;
    let z = 0;
    k.skap.forEach((s, i) => {
      s.nr = i + 1;
      s.z0 = z; z += s.hojd;
      s.bak = s.bak || 'spar';
      s.hyllor = s.hyllor || [];
      s.lador = s.lador || 0;
      s.fast = s.fast == null ? null : s.fast; // mitt på fasta hyllan, från skåpets botten
      s.fasta = s.fasta ? s.fasta.slice() : (s.fast != null ? [s.fast] : []);   // flera fasta hyllor (kök: maskinnisch)
      if (s.fast == null && s.fasta.length) s.fast = s.fasta[0];
    });
    k.hojd = z;
    if (k.dorrar) {
      const d = k.dorrar, under = d.under || 0, sist = k.skap.length - 1, FOG = 3;
      if (d.segment) {   // explicita dörrsegment i skåp 1 (kök): [{zb, DH, cups?}]
        d.seg = d.segment.map(sg => ({ skap: sg.skap || 1, zb: sg.zb, DH: sg.DH, cups: sg.cups || gjAuto(sg.DH) }));
      } else if (d.delad && k.skap.length > 1) {
        d.seg = k.skap.map((s, i) => {
          const zb = i === 0 ? -under : s.z0 + FOG / 2, zt = i === sist ? k.hojd : s.z0 + s.hojd - FOG / 2;
          return { skap: s.nr, zb, DH: zt - zb, cups: gjAuto(zt - zb) };
        });
      } else {
        const DH = d.hojd || (k.hojd + under);
        d.seg = [{ skap: 1, zb: -under, DH, cups: d.gangjarn || gjAuto(DH) }];
      }
      d.gangjarn = d.seg[0].cups;
    }
    return k;
  }

  // ---------- generator ----------
  function generera(konfig) {
    const k = normalisera(konfig);
    const MAT = Object.assign({}, MATG, k.mat || {});   // kök: annan stomme/front
    const T = k.T, W = k.bredd, Bi = W - 2 * T;
    const ut = { konfig: k, delar: [], saglista: [], beslag: [], varningar: [], info: [], regler: REGLER };
    const med = !!k.dorrar;
    const nm = (typ, L, B, Tt) => `${typ} ${k.jobb} L=${fmt(L)} B=${fmt(B)} T=${fmt(Tt)}`;

    k.skap.forEach(s => {
      const H = s.hojd, D = s.djup, rygg = s.bak === 'spar';
      const ys = D - 25.5;                  // ryggspårets framkant i sidan
      const djTB = D - 2;                    // topp/botten
      const djH = rygg ? ys : D;             // fast hylla
      const djHy = (rygg ? ys : D) - 2;      // ställbar hylla
      let n = 0; const nr = () => ++n;
      const fil = (i, typ, suf) => `${s.nr}_${i}_${typ}_${suf}.tcn`;
      const push = (d) => { ut.delar.push(Object.assign({ skap: s.nr }, d)); return d; };

      // --- sidor i "från botten"-koordinater ---
      const sida = [];   // ops med x från botten
      // gångjärnsplattor (bara skåp med gångjärn)
      const gj = med ? k.dorrar.seg.flatMap(sg => sg.cups.map(c => sg.zb + c - s.z0)).filter(x => x > 0 && x < H) : [];
      gj.forEach(x => { sida.push(ytaØ5(x, 23), ytaØ5(x, 55)); });
      // hylltappsrader: 3 hål, start = mitt − 32
      const hylltappar = [];
      s.hyllor.forEach(m => { hylltappar.push([m - 32, 41], [m - 32, 2 + djHy - 37]); });
      // lådor
      const nL = s.lador, lin = [];
      for (let i = 0; i < nL; i++) lin.push(96.5 + 260 * i);
      const klotsL = nL ? 200 + 260 * (nL - 1) : 0, klots0 = 75;
      const sidaLada = [];
      if (nL) {
        if (med) [100, klotsL - 100].forEach(x => sidaLada.push(ytaØ8(klots0 + x, 60), ytaØ8(klots0 + x, 385)));
        else lin.forEach(x => [64, 96, 288, 320].forEach(y => sidaLada.push(ytaØ5(x, y))));
      }
      const tb = rad5stom(djTB);
      const radTopp = ord(tb, ORD_A).map(y => [H - T / 2, y + 2]);
      const radBott = ord(tb, ORD_A).map(y => [T / 2, y + 2]);
      const regl = [];
      if (rygg) {
        const yr = D - 19 / 2;
        [[T, 'bott'], [H - T - 80, 'topp'], [H / 2 - 40, 'mitt']].forEach(([x0]) => regl.push([x0 + 65, yr], [x0 + 15, yr]));
      }
      const hrad = s.fasta.flatMap(f => ord(rad5stom(djH), ORD_A).map(y => [f, y]));

      function bygg(vanster) {
        const X = x => vanster ? H - x : x;
        const ops = [kontur(H, D, T)];
        const hand = med && k.dorrar.antal === 1 ? (k.dorrar.hand || 'v') : null;
        if (med && (!hand || (hand === 'v') === vanster)) gj.forEach(x => ops.push(ytaØ5(X(x), 23), ytaØ5(X(x), 55)));
        s.hyllor.forEach(m => [41, 2 + djHy - 37].forEach(y =>
          ops.push(hylltapp(y, vanster ? H - (m - 32) : m - 32, vanster ? -2 : 2))));
        if (s.stang) { const yc = r2((rygg ? ys : D) / 2); [16, -16].forEach(dx => ops.push(ytaØ5(X(s.stang + dx), yc))); }
        sidaLada.forEach(o => ops.push(Object.assign({}, o, { x: X(o.x) })));
        radTopp.forEach(([x, y]) => ops.push(ytaØ8(X(x), y)));
        radBott.forEach(([x, y]) => ops.push(ytaØ8(X(x), y)));
        regl.forEach(([x, y]) => ops.push(ytaØ8(X(x), y)));
        hrad.forEach(([x, y]) => ops.push(ytaØ8(X(x), y)));
        if (rygg) ops.push(...spar2(ys, 13, H - 13));
        return ops;
      }
      const sL = { typ: 'SideLeft', L: H, B: D, T };
      const sR = { typ: 'SideRight', L: H, B: D, T };
      const iSL = nr(), iT = nr(), iB = nr(), iSR = nr();

      // topp / botten
      const tbOps = (forst) => {
        const o = [kontur(Bi, djTB, T)];
        forst.forEach(sd => tb.length && ord(tb, ORD_A).forEach(x => o.push(kanthal(sd, x, T))));
        if (rygg) o.push(...spar2(ys - 2, 0, Bi));
        return o;
      };
      push(del({ fil: fil(iSL, 'SideLeft', 2), mapp: MAT.stomme.mapp, typ: 'Sida vänster', namn: nm('SideLeft', H, D, T), L: H, B: D, T, ops: bygg(true) }));
      push(del({ fil: fil(iT, 'Toppanel', rygg ? 2 : 1), mapp: MAT.stomme.mapp, typ: 'Topp', namn: nm('Toppanel', Bi, djTB, T), L: Bi, B: djTB, T, ops: tbOps(rygg ? [6, 4] : [4, 6]) }));
      push(del({ fil: fil(iB, 'Bottompanel', 1), mapp: MAT.stomme.mapp, typ: 'Botten', namn: nm('Bottompanel', Bi, djTB, T), L: Bi, B: djTB, T, ops: tbOps([4, 6]) }));
      push(del({ fil: fil(iSR, 'SideRight', 1), mapp: MAT.stomme.mapp, typ: 'Sida höger', namn: nm('SideRight', H, D, T), L: H, B: D, T, ops: bygg(false) }));

      // rygg + reglar
      if (rygg) {
        const RL = H - 2 * T + 14, RB = Bi + 14, RT = MAT.rygg.T;
        const ops = [];
        s.fasta.forEach(f => {
          const x = (H - f) - (T - 7);
          ord(rad5bak(32, RB - 32), ORD_B).forEach(y => ops.push(hal(1, x, y, -8, 8, 1)));
        });
        push(del({ fil: fil(nr(), 'Back', 2), mapp: MAT.rygg.mapp, typ: 'Rygg', namn: nm('Back', RL, RB, RT), L: RL, B: RB, T: RT, overmatt: 0, ops }));
        for (let i = 0; i < 3; i++) {
          const RT2 = MAT.regel.T;
          push(del({ fil: fil(nr(), 'Visible back', 1), mapp: MAT.regel.mapp, typ: 'Regel bak', namn: nm('Visible back', 80, Bi, RT2), L: 80, B: Bi, T: RT2,
            ops: [kontur(80, Bi, RT2), ...[5, 3].flatMap(sd => [65, 15].map(x => kanthal(sd, x, RT2)))] }));
        }
      }

      // dörrar (numreras i det skåp de hör till; odelad dörr = skåp 1)
      if (med) k.dorrar.seg.filter(sg => sg.skap === s.nr).forEach(sg => {
        const dd = k.dorrar, DT = MAT.dorr.T;
        const DH = sg.DH;
        const DB = dd.bredd || (dd.antal === 2 ? (W - 6) / 2 : W - 4);
        const cups = sg.cups;
        const dorr = (typ, ytt) => {
          const ops = [kontur(DH, DB, DT)];
          cups.forEach(c => { const yk = ytt ? DB - 21.5 : 21.5, ys2 = ytt ? DB - 31 : 31;
            ops.push(hal(1, c, yk, -13, 35), hal(1, c + 22.5, ys2, -12, 8), hal(1, c - 22.5, ys2, -12, 8)); });
          return ops;
        };
        const iV = nr(); cups.forEach(() => nr());
        if (dd.antal === 1 && dd.hand === 'h')
          push(del({ fil: fil(iV, 'right door', 1), mapp: MAT.dorr.mapp, typ: 'Dörr höger', namn: nm('right door', DH, DB, DT), L: DH, B: DB, T: DT, ops: dorr('h', true) }));
        else
          push(del({ fil: fil(iV, 'left door', 1), mapp: MAT.dorr.mapp, typ: 'Dörr vänster', namn: nm('left door', DH, DB, DT), L: DH, B: DB, T: DT, ops: dorr('v', false) }));
        if (dd.antal === 2) {
          const iH = nr(); cups.forEach(() => nr());
          push(del({ fil: fil(iH, 'right door', 1), mapp: MAT.dorr.mapp, typ: 'Dörr höger', namn: nm('right door', DH, DB, DT), L: DH, B: DB, T: DT, ops: dorr('h', true) }));
        }
        ut.beslag.push({ namn: 'Gångjärn Blum 45/9,5 + montageplatta', antal: cups.length * dd.antal });
      });

      // fast hylla
      s.fasta.forEach(() => {
        const v = rad5stom(djH);
        const ops = [kontur(Bi, djH, T)];
        ord(rad5bak(25, Bi - 25), ORD_B).forEach(x => ops.push(kanthal(5, x, T)));
        [4, 6].forEach(sd => ord(v, ORD_A).forEach(x => ops.push(kanthal(sd, x, T))));
        push(del({ fil: fil(nr(), 'Horizontal', 1), mapp: MAT.stomme.mapp, typ: 'Fast hylla', namn: nm('Horizontal', Bi, djH, T), L: Bi, B: djH, T, ops }));
      });
      // ställbara hyllor
      s.hyllor.forEach(() => {
        const ops = [kontur(Bi, djHy, T), ytaØ5(Bi - 10, 39), ytaØ5(Bi - 10, djHy - 37), ytaØ5(10, 39), ytaØ5(10, djHy - 37)];
        push(del({ fil: fil(nr(), 'Adjustable_Shelf', 2), mapp: MAT.stomme.mapp, typ: 'Ställbar hylla', namn: nm('Adjustable_Shelf', Bi, djHy, T), L: Bi, B: djHy, T, ops }));
      });
      if (s.hyllor.length) ut.beslag.push({ namn: 'Hylltapp Ø5', antal: 4 * s.hyllor.length });
      if (s.stang) { ut.beslag.push({ namn: 'Klädstång + 2 fästen', antal: 1 }); ut.saglista.push({ namn: `Klädstång skåp ${s.nr}`, L: Bi - 2, B: 25, T: 25, material: 'Stång (köpdel, kapas)' }); }

      // lådor
      if (nL) {
        const LT = MAT.lada.T, sh = 200, P = LADA[sh];
        const FL = Bi - 8 - (med ? 40 : 0), BL = FL - 2 * 2 - 2 * LT, SL = 410;
        for (let i = 0; i < nL; i++) {
          const b = nr();
          const sidaOps = (v) => {
            const ops = [kontur(SL, sh, 15)];
            ord(P.sidayta, ORD4).forEach(y => ops.push(ytaØ8(v ? 7.5 : SL - 7.5, y)));
            ord(P.sidakant, ORD4).forEach(x => ops.push(hal(v ? 4 : 6, x, 7.5, -21, 8)));
            ops.push(...spar2(181.5, v ? 0 : -7, v ? SL + 7 : SL));
            return ops;
          };
          push(del({ fil: fil(b, 'Drawer_Left_Side', 2), mapp: MAT.lada.mapp, typ: `Låda ${i + 1} sida v`, namn: nm('Drawer_Left_Side', SL, sh, LT), L: SL, B: sh, T: LT, ops: sidaOps(true) }));
          push(del({ fil: fil(nr(), 'Drawer_Right_Side', 1), mapp: MAT.lada.mapp, typ: `Låda ${i + 1} sida h`, namn: nm('Drawer_Right_Side', SL, sh, LT), L: SL, B: sh, T: LT, ops: sidaOps(false) }));
          const fo = [kontur(FL, 220, 15)];
          [9.5, FL - 9.5].forEach(x => ord(P.front, ORD4).forEach(y => fo.push(ytaØ8(x, y))));
          fo.push(...spar2(186.5, 10, FL - 10));
          push(del({ fil: fil(nr(), 'Drawer_Front', 2), mapp: MAT.lada.mapp, typ: `Låda ${i + 1} front`, namn: nm('Drawer_Front', FL, 220, LT), L: FL, B: 220, T: LT, ops: fo }));
          const bo = [kontur(BL, 180, 15)];
          [4, 6].forEach(sd => ord(P.bak, ORD4).forEach(x => bo.push(hal(sd, x, 7.5, -21, 8))));
          push(del({ fil: fil(nr(), 'Drawer_Back', 1), mapp: MAT.lada.mapp, typ: `Låda ${i + 1} bak`, namn: nm('Drawer_Back', BL, 180, LT), L: BL, B: 180, T: LT, ops: bo }));
          nr(); // lådbotten (sågas)
          ut.saglista.push({ namn: `Låda ${i + 1} botten`, L: BL + 2 * 6.5, B: SL + 6.5, T: 6, material: 'Fanerad MDF 6,5' });
          if (med && i === 0) {
            const KL = klotsL, KB = 425, KT = 20, dow = [100, KL - 100];
            const skena = lin.map(x => x - klots0);           // från klotsens botten
            const ø8 = (xs) => xs.flatMap(x => [ytaØ8(x, 50), ytaØ8(x, 375)]);
            const ø5 = (xs) => xs.flatMap(x => [54, 86, 278, 310].map(y => ytaØ5(x, y)));
            const ia = nr(), ib = nr();
            const dn = (i2, s2, ops, om) => push(del({ fil: fil(i2, 'Distance for Interior drawer', s2), mapp: MAT.distans.mapp, typ: 'Distansklots', namn: nm('Distance for Interior drawer', KL, KB, KT), L: KL, B: KB, T: KT, overmatt: om, ops }));
            dn(ia, 1, [kontur(KL, KB, KT), ...ø8(dow)], 2.5);
            dn(ia, 2, ø5(skena.map(x => KL - x)), 0);
            dn(ib, 1, [kontur(KL, KB, KT), ...ø5(skena)], 2.5);
            dn(ib, 2, ø8(dow.slice().reverse()), 0);
          }
          nr(); // skena
        }
        ut.beslag.push({ namn: 'Lådskena (par), 400 mm', antal: nL });
      }
    });

    // tappar: räkna Ø8 kanthål
    let tapp = 0;
    ut.delar.forEach(d => d.ops.forEach(o => { if (o.typ === 'hal' && o.sida > 1 && o.d === 8) tapp++; }));
    ut.beslag.unshift({ namn: 'Tapp Ø8×30', antal: tapp });
    const sum = new Map(); ut.beslag.forEach(b => sum.set(b.namn, (sum.get(b.namn) || 0) + b.antal));
    ut.beslag = [...sum].map(([namn, antal]) => ({ namn, antal }));
    kontrollera(ut);
    return ut;
  }

  function kontrollera(ut) {
    const k = ut.konfig;
    if (k.nisch) {
      const fritt = k.nisch.bredd - k.bredd;
      if (fritt < 0) ut.varningar.push(`Garderoben (${k.bredd}) är bredare än nischen (${k.nisch.bredd}).`);
      else ut.info.push(`Passbitar: ${fritt / 2} per sida.`);
      if (k.nisch.hojd && k.hojd + (k.sockel || 0) > k.nisch.hojd) ut.varningar.push('Skåpen + sockel högre än nischen.');
    }
    k.skap.forEach(s => {
      s.hyllor.forEach(m => { if (m - 32 < k.T + 30 || m + 32 > s.hojd - k.T - 30) ut.varningar.push(`Skåp ${s.nr}: hylla ${m} för nära topp/botten.`); });
      if (k.dorrar) {   // montageplatta (framkant 23–55) får inte krocka med hylla/fast hylla
        const pl = k.dorrar.seg.flatMap(sg => sg.cups.map(c => sg.zb + c - s.z0)).filter(x => x > 0 && x < s.hojd);
        [...s.hyllor, ...s.fasta].forEach(h => pl.forEach(p => {
          if (Math.abs(p - h) < 40) ut.varningar.push(`Skåp ${s.nr}: hylla ${h} krockar med montageplatta ${fmt(p)}.`); }));
      }
      if (s.bak === 'spar' && s.hojd - 2 * k.T + 14 > 2440) ut.varningar.push(`Skåp ${s.nr}: ryggen ${s.hojd - 2 * k.T + 14} är längre än en MDF-skiva (2440), kontrollera skivformatet.`);
      if (s.lador && s.djup < 440) ut.varningar.push(`Skåp ${s.nr}: lådor 410 kräver djup ≥ 440.`);
      if (s.lador && s.fast != null && 96.5 + 260 * (s.lador - 1) + 220 > s.fast - 10) ut.varningar.push(`Skåp ${s.nr}: lådorna når upp till fasta hyllan.`);
    });
  }

  // ---------- TCN-skrivare (port av tcn_del.skriv_del) ----------
  const HUVUD = 'TPA\\ALBATROS\\EDICAD\\02.00:1560:r0w0h0s1', NL = '\r\n';
  const WSTXT = { 0: ' ', 1: ' WS=1  ', 2: ' WS=1 ', 3: '  ' };
  const WS_SIDA = { 1: 0, 2: 0, 3: 0, 4: 2, 5: 2, 6: 3 };
  const blk = (s, rad, F) => `SIDE#${s}{` + NL + (F ? '$=F #1' + NL : '') + rad + NL + '}SIDE';
  function skrivTcn(d) {
    const o = [HUVUD, `$=[Programname=${d.namn}]`, '::SIDE=1;2;3;4;5;6;', `::UNm DL=${fmt(d.L)} DH=${fmt(d.B)} DS=${fmt(d.T)}`,
      "'tcn version=2.1.15", "'code=ansi", 'EXE{'];
    for (let i = 0; i < 5; i++) o.push(`#${i}=0`);
    o.push('}EXE', 'OFFS{');
    const om = `${fmt(d.overmatt)}|${fmt(d.overmatt)}`;
    o.push(`#0=${om}`, `#1=${om}`, '#2=0.0|0', '}OFFS', 'VARV{');
    for (let i = 0; i < 8; i++) o.push(`#${i}=0.0|0`);
    o.push('}VARV', 'VAR{', '}VAR', 'SPEC{', '}SPEC', 'INFO{', '}INFO', 'OPTI{', '}OPTI', 'LINK{', '}LINK');
    for (const op of d.ops) {
      const s = op.sida;
      if (op.typ === 'kontur') {
        const z = fmt(op.z);
        o.push(blk(s, `W#89{ ::WTs WS=1  #8015=0 #1=${fmt(op.start[0])} #2=${fmt(op.start[1])} #3=${z} #201=1 #203=1 #205=${op.verktyg} #1001=100 #8096=0 #40=2 #46=0 #8135=0 #8136=0 #8180=1 #8181=2 #8182=120 #8184=0 #8185=1 #8186=2 #8187=120 #8189=0 #9511=1 #9512=0 #9513=0 }W`));
        for (const [x, y] of op.pts) o.push(blk(s, `W#2201{ ::WTl #1=${fmt(x)} #2=${fmt(y)} #3=${z} #203=1 #8015=0 }W`));
      } else if (op.typ === 'hal') {
        o.push(blk(s, `W#81{ ::WTp${WSTXT[WS_SIDA[s]]}#1=${fmt(op.x)} #2=${fmt(op.y)} #3=${fmt(op.z)} #8015=0 #1002=${fmt(op.d)} #201=1 #203=1 #1001=${op.genom} }W`));
      } else if (op.typ === 'hylltapp') {
        const n = fmt(op.langd), st = (op.steg >= 0 ? '+' : '') + op.steg;
        o.push(blk(s, `W#1001{ ::WT2 #8098=..\\custom\\mcr\\fittingx.tmcr #6=1 #8508=0 #8509=0 #8510=${n} #8511=${n}${st}*${fmt(op.delning)} #8512=${fmt(op.delning)} #8513=${fmt(op.z)} #8517=0 #8518=${fmt(op.y)} #8522=${fmt(op.d)} #8525=0 }W`));
      } else if (op.typ === 'spar') {
        o.push(blk(s, `W#1050{ ::WT2 WS=1  #8098=..\\custom\\mcr\\lame.tmcr #6=1 #8503=0 #8509=0 #8510=${fmt(op.x0)} #8511=${fmt(op.y)} #8512=-1 #8513=${fmt(-op.djup)} #8514=1 #8515=1 #8516=${op.blad} #8517=${fmt(op.langd)} #8525=1 #8526=1 #8527=0 }W`, true));
      }
    }
    return o.join(NL) + NL;
  }
  function tillBytes(s) { const b = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i) & 255; return b; }

  // ---------- exempel ----------
  const ACACIA = {
    namn: 'Acaciagatan 12.32 B.1.08 Sovrum 1 – SN.B.1.08-A', jobb: 'Hurts 2 L + inlåda',
    bredd: 910, nisch: { bredd: 970, hojd: 2680 }, sockel: 100, galler: 100,
    skap: [
      { hojd: 1500, djup: 488, bak: 'spar', fast: 590, hyllor: [880, 1180], lador: 2 },
      { hojd: 980, djup: 340, bak: 'ingen', hyllor: [320, 640] },
    ],
    dorrar: { antal: 2, under: 50, gangjarn: [90, 780, 1420] },
  };

  return { gjAuto, generera, skrivTcn, tillBytes, fmt, REGLER, MAT: MATG, ACACIA };
});
