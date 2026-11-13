/* Export: TCN-zip (en fil per del, mapp per material) + PDF-sammanställning. UMD. */
(function (root, f) {
  if (typeof module === 'object' && module.exports) module.exports = f(require('./garderob.js'), require('./ritning.js'));
  else root.Export = f(root.Garderob, root.Ritning);
})(this, function (G, R) {
  'use strict';
  const rot = ut => (ut.konfig.namn || 'Garderob').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^\x20-\x7e]/g, '-').replace(/[\\/:*?"<>|]/g, '-') + (ut.konfig.dorrar ? '_DORRAR' : '_UTAN_DORRAR');

  async function tcnZip(ut, JSZip, typ = 'uint8array') {
    const z = new JSZip(), r = z.folder(rot(ut));
    ut.delar.forEach(d => r.folder(d.mapp).file(d.fil, G.tillBytes(G.skrivTcn(d))));
    r.file('konfig.json', JSON.stringify(ut.konfig, null, 2));
    return z.generateAsync({ type: typ, compression: 'DEFLATE' });
  }

  function mattOch(d) {
    const c = { ø8: 0, ø5: 0, ø35: 0, kant: 0, rad: 0, spar: 0 };
    d.ops.forEach(o => {
      if (o.typ === 'hal' && o.sida > 1) c.kant++;
      else if (o.typ === 'hal') { if (o.d >= 30) c.ø35++; else if (o.d >= 8) c.ø8++; else c.ø5++; }
      else if (o.typ === 'hylltapp') c.rad++;
      else if (o.typ === 'spar') c.spar++;
    });
    return [c.ø8 && `${c.ø8}×Ø8`, c.ø5 && `${c.ø5}×Ø5`, c.ø35 && `${c.ø35}×Ø35`, c.kant && `${c.kant} kanthål`, c.rad && `${c.rad} hylltapprader`, c.spar && 'ryggspår/bottenspår'].filter(Boolean).join(', ');
  }

  function pdfRapport(ut, jsPDF) {
    const doc = new jsPDF({ unit: 'mm', format: 'a4' }), L = R.lat, k = ut.konfig;
    const W = 210, M = 14;
    let sid = 0;
    const huvud = (t) => {
      if (sid++) doc.addPage();
      doc.setFillColor(251, 192, 33); doc.rect(0, 0, W, 16, 'F');
      doc.setTextColor(30, 30, 30); doc.setFontSize(13); doc.setFont('helvetica', 'bold');
      doc.text(L(t), M, 10.5);
      doc.setFontSize(8); doc.setFont('helvetica', 'normal');
      doc.text(L(`${k.namn || ''}  ·  ${new Date().toISOString().slice(0, 10)}  ·  sid ${sid}`), W - M, 10.5, { align: 'right' });
      doc.setTextColor(0, 0, 0);
    };
    const txt = (s, x, y, o = {}) => { doc.setFontSize(o.size || 9); doc.setFont('helvetica', o.bold ? 'bold' : 'normal'); if (o.color) doc.setTextColor(...o.color); doc.text(L(s), x, y, o.align ? { align: o.align } : undefined); doc.setTextColor(0, 0, 0); };

    // --- sid 1: översikt ---
    huvud('Garderob – sammanställning');
    let y = 24;
    txt(`Jobb: ${k.jobb}`, M, y); y += 5;
    txt(`Bredd ${k.bredd} · total höjd ${k.hojd}` + (k.sockel ? ` · sockel ${k.sockel}` : '') + (k.galler ? ` · galler ${k.galler}` : '') + (k.nisch ? ` · nisch ${k.nisch.bredd}×${k.nisch.hojd}` : ''), M, y); y += 5;
    k.skap.forEach(s => { txt(`Skåp ${s.nr}: ${s.hojd} h × ${s.djup} d · rygg: ${s.bak === 'spar' ? 'i spår' : 'ingen'}` + (s.fast != null ? ` · fast hylla ${s.fast}` : '') + ` · ${s.hyllor.length} ställbara hyllor · ${s.lador} innerlådor`, M, y); y += 5; });
    txt(k.dorrar ? `Dörrar: ${k.dorrar.antal} st, gångjärn på ${k.dorrar.gangjarn.join(' / ')} från dörrens underkant, ${k.dorrar.under || 0} under skåpet` : 'Dörrar: inga', M, y); y += 7;
    R.pdf(doc, R.front(ut), M, y, 88, 150);
    if (k.dorrar) R.pdf(doc, R.front(ut, { dorrar: true }), M + 92, y, 88, 150);
    txt('Front utan dörrar', M, y + 156, { size: 8, color: [90, 90, 90] });
    if (k.dorrar) txt('Front med dörrar (gröna = gångjärnskoppar)', M + 92, y + 156, { size: 8, color: [90, 90, 90] });
    y += 164;
    if (ut.varningar.length) { txt('Varningar', M, y, { bold: true, color: [200, 50, 26] }); y += 5; ut.varningar.forEach(v => { txt('• ' + v, M, y, { color: [200, 50, 26] }); y += 4.5; }); }
    if (ut.info.length) { ut.info.forEach(v => { txt('• ' + v, M, y); y += 4.5; }); }
    txt('Filerna är genererade av konfiguratorn och INTE provkörda. Kör TpaCAD-simulering innan fräsning.', M, 288, { size: 8, color: [200, 50, 26] });

    // --- sid 2: stycklista ---
    huvud('Stycklista · såglista · beslag');
    y = 24;
    const kol = [M, M + 52, M + 98, M + 128, M + 186];
    txt('Fil', kol[0], y, { bold: true }); txt('Del', kol[1], y, { bold: true }); txt('L × B × T', kol[2], y, { bold: true }); txt('Bearbetning', kol[3], y, { bold: true });
    y += 2; doc.line(M, y, W - M, y); y += 4;
    const sorterad = ut.delar.slice().sort((a, b) => a.mapp.localeCompare(b.mapp) || a.fil.localeCompare(b.fil, 'sv', { numeric: true }));
    let mapp = null;
    sorterad.forEach(d => {
      if (y > 280) { huvud('Stycklista (forts.)'); y = 24; }
      if (d.mapp !== mapp) { mapp = d.mapp; txt(mapp, M, y, { bold: true, size: 8, color: [120, 70, 20] }); y += 4.2; }
      txt(d.fil.replace('.tcn', ''), kol[0], y, { size: 7.5 });
      txt(d.typ, kol[1], y, { size: 7.5 });
      txt(`${G.fmt(d.L)} × ${G.fmt(d.B)} × ${G.fmt(d.T)}`, kol[2], y, { size: 7.5 });
      txt(mattOch(d) || (d.overmatt ? 'kontur' : '–'), kol[3], y, { size: 7 });
      y += 4.2;
    });
    y += 4;
    txt(`Totalt ${ut.delar.length} TCN-filer`, M, y, { bold: true }); y += 7;
    txt('Såglista (ingen TCN)', M, y, { bold: true }); y += 5;
    ut.saglista.forEach(s => { txt(`${s.namn}: ${G.fmt(s.L)} × ${G.fmt(s.B)} × ${G.fmt(s.T)}  ${s.material}`, M, y, { size: 8 }); y += 4.2; });
    if (!ut.saglista.length) { txt('–', M, y); y += 4.2; }
    y += 4; txt('Beslag / köpdelar', M, y, { bold: true }); y += 5;
    ut.beslag.forEach(b => { txt(`${b.antal} × ${b.namn}`, M, y, { size: 8 }); y += 4.2; });

    // --- delritningar, 6 per sida ---
    const unika = [], sett = new Map();
    sorterad.forEach(d => { const nyckel = JSON.stringify([d.L, d.B, d.T, d.ops, d.mapp]); if (sett.has(nyckel)) sett.get(nyckel).filer.push(d.fil); else { const u = { d, filer: [d.fil] }; sett.set(nyckel, u); unika.push(u); } });
    unika.forEach((u, i) => {
      if (i % 6 === 0) huvud('Delar – hål och spår');
      const c = i % 2, r = Math.floor((i % 6) / 2);
      const bx = M + c * 93, by = 22 + r * 89, bw = 88, bh = 64;
      const d = u.d;
      txt(`${d.typ}  (${u.filer.length} st)`, bx, by + 3, { bold: true, size: 8.5 });
      txt(u.filer.map(f => f.replace('.tcn', '')).join(', ').slice(0, 70), bx, by + 7, { size: 6.5, color: [100, 100, 100] });
      const rr = R.delbild(d), s = Math.min(bw / d.L, (bh - 4) / d.B);
      R.pdf(doc, rr, bx, by + 10, bw, bh - 4);
      txt(`L ${G.fmt(d.L)}`, bx + d.L * s / 2, by + 10 + d.B * s + 4, { size: 7, align: 'center' });
      txt(`B ${G.fmt(d.B)} · T ${G.fmt(d.T)} · ${d.mapp}`, bx, by + 10 + d.B * s + 8, { size: 6.5, color: [90, 90, 90] });
      txt(mattOch(d), bx, by + 10 + d.B * s + 11.5, { size: 6.5, color: [90, 90, 90] });
    });
    // teckenförklaring på sista delsidan
    txt('Blå = Ø8 (yta), blå streck = kanthål Ø8, röd = Ø5 / hylltapp, grön = Ø35 kopp, lila = spår. Origo nere till vänster = TCN-origo.', M, 290, { size: 7, color: [90, 90, 90] });

    // --- regelbok ---
    huvud('Regelbok (härledd ur skåpprogrammets TCN)');
    y = 26;
    ut.regler.forEach(r => {
      const osak = /OSÄKER/.test(r.status);
      txt(`${osak ? '!' : '✓'.replace('✓', '+')} ${r.text}`, M, y, { size: 8.5 });
      txt(r.status, W - M, y, { size: 8, align: 'right', color: osak ? [200, 50, 26] : [40, 120, 40] });
      y += 6;
    });
    y += 4;
    txt('OSÄKER = bara en datapunkt. Fler TCN-filer från andra projekt bekräftar eller rättar regeln.', M, y, { size: 8, color: [90, 90, 90] });
    return doc;
  }

  return { tcnZip, pdfRapport, rot };
});
