/* Garderobssystem: rad av moduler (som uteköket). Varje modul = egen stomme (egna sidor, skruvas ihop),
 * gemensam delning nedre/övre, sockel och galler. Bredder: fria mått eller "auto" som fyller nischen.
 * modul -> garderob-konfig -> Garderob.generera.  UMD.
 */
(function (root, f) {
  if (typeof module === 'object' && module.exports) module.exports = f(require('./garderob.js'));
  else root.System = f(root.Garderob);
})(this, function (G) {
  'use strict';

  const TYPER = {
    lada: { namn: 'Lådor + hyllor', kort: 'Lador+hyllor' },
    hang: { namn: 'Hängdel', kort: 'Hangdel' },
    hylla: { namn: 'Hyllor', kort: 'Hyllor' },
  };

  // n hyllor jämnt mellan a och b (tappradens mitt), avrundat till 10
  function jamn(a, b, n) {
    const st = (b - a) / (n + 1), u = [];
    for (let i = 1; i <= n; i++) u.push(Math.round((a + st * i) / 10) * 10);
    return u;
  }

  function bredder(sys) {
    const pass = sys.passbit != null ? sys.passbit : 0;
    const tillg = sys.nisch && sys.nisch.bredd ? sys.nisch.bredd - 2 * pass : null;
    const fasta = sys.moduler.filter(m => m.bredd).reduce((a, m) => a + m.bredd, 0);
    const auto = sys.moduler.filter(m => !m.bredd);
    let rest = tillg != null ? tillg - fasta : 600 * auto.length;
    const per = auto.length ? Math.floor(rest / auto.length) : 0;
    let extra = auto.length ? rest - per * auto.length : 0;
    return sys.moduler.map(m => {
      if (m.bredd) return m.bredd;
      const w = per + (extra > 0 ? 1 : 0); if (extra > 0) extra--;
      return w;
    });
  }

  function modulKonfig(sys, m, i, W) {
    const [Hn, Ho] = sys.hojder || [1500, 980];
    const [Dn, Do] = sys.djup || [488, 488];
    const T = 20, n = sys.moduler.length;
    const ned = { hojd: Hn, djup: Dn, bak: 'spar', fast: null, hyllor: [], lador: 0 };
    const ovr = { hojd: Ho, djup: Do, bak: 'spar', fast: null, hyllor: [], lador: 0 };
    if (m.typ === 'lada') {
      ned.lador = m.lador != null ? m.lador : 2;
      ned.fast = m.fast != null ? m.fast : (ned.lador ? 96.5 + 260 * (ned.lador - 1) + 233.5 + 0 : null);
      if (ned.fast != null) ned.fast = Math.round(ned.fast);
      ned.hyllor = jamn((ned.fast != null ? ned.fast + 10 : T), Hn - T, m.hyllorNed != null ? m.hyllorNed : 2);
    } else if (m.typ === 'hang') {
      ned.stang = m.stang || Hn - 70;
    } else if (m.typ === 'hylla') {
      ned.hyllor = jamn(T, Hn - T, m.hyllorNed != null ? m.hyllorNed : 4);
    }
    ovr.hyllor = jamn(T, Ho - T, m.hyllorOvr != null ? m.hyllorOvr : 2);
    if (m.ned) Object.assign(ned, m.ned);
    if (m.ovr) Object.assign(ovr, m.ovr);
    const skap = Ho > 0 ? [ned, ovr] : [ned];
    const antalD = m.dorrar != null ? m.dorrar : (W > 650 ? 2 : 1);
    const dorrar = antalD ? Object.assign({ antal: antalD, under: sys.sockel ? 50 : 0, gangjarn: [90, 780, 1420] }, antalD === 1 ? { hand: m.hand || 'v' } : {}, m.dorrinst || {}) : null;
    return {
      namn: n === 1 ? sys.namn : `${sys.namn} M${i + 1}`,
      jobb: m.jobb || (n === 1 ? sys.jobb : `${sys.jobb} M${i + 1}`),
      bredd: W, skap, dorrar,
    };
  }

  function generera(sys) {
    sys = JSON.parse(JSON.stringify(sys));
    sys.namn = sys.namn || 'Garderob'; sys.jobb = sys.jobb || 'Garderob';
    const W = bredder(sys);
    const su = { sys, moduler: [], delar: [], saglista: [], beslag: [], varningar: [], info: [], regler: G.REGLER };
    let x = sys.nisch && sys.nisch.bredd ? (sys.passbit || 0) : 0;
    const flera = sys.moduler.length > 1;
    sys.moduler.forEach((m, i) => {
      const k = modulKonfig(sys, m, i, W[i]);
      const ut = G.generera(k);
      const mapp = flera ? `M${i + 1} ${TYPER[m.typ].kort} ${W[i]}` : '';
      const mod = { nr: i + 1, typ: m.typ, x0: x, bredd: W[i], konfig: ut.konfig, ut, mapp };
      su.moduler.push(mod);
      ut.delar.forEach(d => su.delar.push(Object.assign({}, d, { modul: i + 1, modulMapp: mapp, etikett: (flera ? `M${i + 1}/` : '') + d.fil.replace('.tcn', '') })));
      ut.saglista.forEach(s2 => su.saglista.push(Object.assign({}, s2, { namn: (flera ? `M${i + 1} ` : '') + s2.namn })));
      ut.beslag.forEach(b => su.beslag.push(b));
      ut.varningar.forEach(v => su.varningar.push((flera ? `M${i + 1}: ` : '') + v));
      if (W[i] < 300) su.varningar.push(`M${i + 1}: bredd ${W[i]} < 300.`);
      if (W[i] > 1200) su.varningar.push(`M${i + 1}: bredd ${W[i]} > 1200 – hyllorna svajar, dela modulen.`);
      if (k.dorrar && k.dorrar.antal === 1 && W[i] > 650) su.varningar.push(`M${i + 1}: en dörr på ${W[i]} – välj 2 dörrar.`);
      if (k.dorrar && k.dorrar.antal === 2 && W[i] < 500) su.varningar.push(`M${i + 1}: två dörrar på ${W[i]} blir smala.`);
      if (m.typ === 'lada' && W[i] < 400) su.varningar.push(`M${i + 1}: lådor kräver bredd ≥ 400.`);
      x += W[i];
    });
    const sum = new Map(); su.beslag.forEach(b => sum.set(b.namn, (sum.get(b.namn) || 0) + b.antal));
    su.beslag = [...sum].map(([namn, antal]) => ({ namn, antal }));
    if (flera) su.beslag.push({ namn: 'Skruv modul–modul (4 per skarv)', antal: 4 * (sys.moduler.length - 1) * (sys.hojder && sys.hojder[1] ? 2 : 1) });
    su.bredd = W.reduce((a, b) => a + b, 0);
    su.hojd = (sys.hojder || [1500, 980]).reduce((a, b) => a + b, 0);
    if (sys.nisch && sys.nisch.bredd) {
      const fritt = sys.nisch.bredd - su.bredd;
      if (fritt < 0) su.varningar.push(`Modulerna (${su.bredd}) är bredare än nischen (${sys.nisch.bredd}).`);
      else su.info.push(`Passbitar: ${G.fmt(fritt / 2)} per sida.`);
      if (sys.nisch.hojd && su.hojd + (sys.sockel || 0) + (sys.galler || 0) > sys.nisch.hojd) su.varningar.push('Skåp + sockel + galler är högre än nischen.');
      else if (sys.nisch.hojd) su.info.push(`Fritt i höjd: ${sys.nisch.hojd - su.hojd - (sys.sockel || 0) - (sys.galler || 0)}.`);
    }
    su.info.push(`${sys.moduler.length} moduler · ${su.bredd} bred · ${su.delar.length} TCN-filer`);
    return su;
  }

  // Acaciagatan som system (1 modul) – ska ge samma 31 filer som Garderob.ACACIA
  const ACACIA = {
    namn: 'Acaciagatan 12.32 B.1.08 Sovrum 1 – SN.B.1.08-A', jobb: 'Hurts 2 L + inlåda',
    nisch: { bredd: 970, hojd: 2680 }, passbit: 30, sockel: 100, galler: 100,
    hojder: [1500, 980], djup: [488, 340],
    moduler: [{ typ: 'lada', lador: 2, fast: 590, ned: { hyllor: [880, 1180] }, ovr: { bak: 'ingen', hyllor: [320, 640] }, dorrar: 2 }],
  };
  const EXEMPEL = {
    namn: 'Exempel system 2,4 m', jobb: 'Garderob',
    nisch: { bredd: 2420, hojd: 2680 }, passbit: 10, sockel: 100, galler: 100,
    hojder: [1500, 980], djup: [488, 488],
    moduler: [{ typ: 'lada' }, { typ: 'hang' }, { typ: 'hylla', bredd: 500 }],
  };

  // gammal enkel konfig (skap/dorrar) -> system med en modul
  function franEnkel(k) {
    if (k.moduler) return k;
    const s0 = k.skap[0] || {}, s1 = k.skap[1];
    return {
      namn: k.namn, jobb: k.jobb, nisch: k.nisch, passbit: k.nisch ? (k.nisch.bredd - k.bredd) / 2 : 0, sockel: k.sockel, galler: k.galler,
      hojder: [s0.hojd, s1 ? s1.hojd : 0], djup: [s0.djup, s1 ? s1.djup : s0.djup],
      moduler: [{ typ: s0.lador ? 'lada' : 'hylla', bredd: k.bredd, lador: s0.lador || 0, fast: s0.fast, ned: s0, ovr: s1, dorrar: k.dorrar ? k.dorrar.antal : 0, dorrinst: k.dorrar || undefined }],
    };
  }

  return { generera, bredder, modulKonfig, TYPER, ACACIA, EXEMPEL, franEnkel, jamn };
});
