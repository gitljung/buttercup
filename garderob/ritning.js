/* Ritningar för garderobskonfiguratorn: genererar primitiver i mm (y uppåt) som
 * renderas till SVG (webb) eller jsPDF (sammanställning).
 * prim: {t:'rect',x,y,w,h,fill?,stroke?,dash?,lw?} {t:'line',x1,y1,x2,y2,dash?,lw?,stroke?}
 *       {t:'circle',x,y,r,fill?,stroke?} {t:'text',x,y,s,size?,anchor?,color?,rot?}
 */
(function (root, f) {
  if (typeof module === 'object' && module.exports) module.exports = f();
  else root.Ritning = f();
})(this, function () {
  'use strict';
  const FARG = { stomme: '#d8b98a', lada: '#c9c9c9', dorr: '#b98a55', rygg: '#e9dcc0', regel: '#bdbdbd', hal8: '#1f4e8c', hal5: '#c8321a', kopp: '#2f7d32', spar: '#7a3fa0' };

  // ---------- frontvy ----------
  function front(ut, opt = {}) {
    const k = ut.konfig, T = k.T, W = k.bredd, P = [];
    const sock = k.sockel || 0, gal = k.galler || 0;
    const nb = k.nisch ? k.nisch.bredd : W, x0 = (nb - W) / 2;
    if (k.nisch) {
      P.push({ t: 'rect', x: 0, y: 0, w: nb, h: k.nisch.hojd, stroke: '#999', dash: [8, 6], lw: 0.6 });
      P.push({ t: 'text', x: nb / 2, y: k.nisch.hojd + 25, s: `nisch ${nb} × ${k.nisch.hojd}`, anchor: 'middle', size: 9, color: '#666' });
    }
    if (sock) { P.push({ t: 'rect', x: x0, y: 0, w: W, h: sock, fill: '#eee', stroke: '#888' }); P.push({ t: 'text', x: x0 + W / 2, y: sock / 2 - 12, s: `sockel ${sock}`, anchor: 'middle', size: 8, color: '#666' }); }
    let z = sock;
    k.skap.forEach(s => {
      const H = s.hojd;
      P.push({ t: 'rect', x: x0, y: z, w: T, h: H, fill: FARG.stomme, stroke: '#333' });
      P.push({ t: 'rect', x: x0 + W - T, y: z, w: T, h: H, fill: FARG.stomme, stroke: '#333' });
      P.push({ t: 'rect', x: x0 + T, y: z, w: W - 2 * T, h: T, fill: FARG.stomme, stroke: '#333' });
      P.push({ t: 'rect', x: x0 + T, y: z + H - T, w: W - 2 * T, h: T, fill: FARG.stomme, stroke: '#333' });
      if (s.fast != null) P.push({ t: 'rect', x: x0 + T, y: z + s.fast - T / 2, w: W - 2 * T, h: T, fill: FARG.stomme, stroke: '#333' });
      s.hyllor.forEach(m => {
        P.push({ t: 'rect', x: x0 + T + 1, y: z + m + 6, w: W - 2 * T - 2, h: T, fill: '#ead7b5', stroke: '#555' });
        P.push({ t: 'text', x: x0 + W + 12, y: z + m, s: `hylla ${m}`, size: 7, color: '#555' });
      });
      const med = !!k.dorrar, inv = med ? 20 : 0;
      for (let i = 0; i < s.lador; i++) {
        const lb = z + T + 260 * i;
        P.push({ t: 'rect', x: x0 + T + 4 + inv, y: lb, w: W - 2 * T - 8 - 2 * inv, h: 220, fill: FARG.lada, stroke: '#444' });
        P.push({ t: 'text', x: x0 + W / 2, y: lb + 100, s: `innerlåda ${i + 1}`, anchor: 'middle', size: 8 });
      }
      if (med && s.lador) [x0 + T, x0 + W - T - 20].forEach(x => P.push({ t: 'rect', x, y: z + 75, w: 20, h: 200 + 260 * (s.lador - 1), fill: '#a9b7c6', stroke: '#444' }));
      if (s.bak !== 'spar') P.push({ t: 'text', x: x0 + W / 2, y: z + H - 70, s: 'ingen rygg', anchor: 'middle', size: 7, color: '#888' });
      P.push({ t: 'text', x: x0 - 12, y: z + H / 2, s: `skåp ${s.nr}: ${H}`, anchor: 'end', size: 8 });
      z += H;
    });
    if (gal) { P.push({ t: 'rect', x: x0, y: z, w: W, h: gal, fill: '#f4f4f4', stroke: '#888', dash: [4, 3] }); P.push({ t: 'text', x: x0 + W / 2, y: z + gal / 2 - 4, s: `galler ${gal}`, anchor: 'middle', size: 8, color: '#666' }); }
    if (opt.dorrar && k.dorrar) {
      const d = k.dorrar, DH = d.hojd || (k.hojd + (d.under || 0)), DB = d.bredd || (d.antal === 2 ? (W - 6) / 2 : W - 4);
      const yb = sock - (d.under || 0);
      const xs = d.antal === 2 ? [x0 + 1, x0 + W - 1 - DB] : [x0 + 2];
      xs.forEach((x, i) => {
        P.push({ t: 'rect', x, y: yb, w: DB, h: DH, fill: 'rgba(185,138,85,0.55)', stroke: '#5b3b17', lw: 1 });
        const kant = (i === 0) ? x + 21.5 : x + DB - 21.5;
        d.gangjarn.forEach(c => P.push({ t: 'circle', x: kant, y: yb + c, r: 17.5, stroke: FARG.kopp, fill: 'none' }));
      });
    }
    // mått
    const top = sock + k.hojd;
    P.push({ t: 'text', x: x0 + W / 2, y: -40, s: `bredd ${W}`, anchor: 'middle', size: 9 });
    P.push({ t: 'text', x: x0 + W + 12, y: top + 10, s: `total ${k.hojd}`, size: 8 });
    return { prim: P, box: [-190, -70, nb + 380, Math.max(k.nisch ? k.nisch.hojd : 0, top + gal) + 160] };
  }

  // ---------- sidosnitt ----------
  function sida(ut) {
    const k = ut.konfig, P = [];
    let z = k.sockel || 0, maxD = 0;
    k.skap.forEach(s => {
      maxD = Math.max(maxD, s.djup);
      P.push({ t: 'rect', x: 0, y: z, w: s.djup, h: s.hojd, fill: FARG.stomme, stroke: '#333' });
      if (s.bak === 'spar') P.push({ t: 'rect', x: s.djup - 25.5, y: z + 13, w: 6.5, h: s.hojd - 26, fill: '#7a5a2c' });
      P.push({ t: 'text', x: s.djup / 2, y: z + s.hojd / 2, s: `djup ${s.djup}`, anchor: 'middle', size: 8 });
      z += s.hojd;
    });
    return { prim: P, box: [-40, -40, maxD + 80, z + 80] };
  }

  // ---------- delritning ----------
  function delbild(d) {
    const P = [], L = d.L, B = d.B;
    P.push({ t: 'rect', x: 0, y: 0, w: L, h: B, fill: '#faf6ee', stroke: '#333', lw: 0.8 });
    const kant = (sida, p) => { // kanthål: [x,y] på kanten + riktning in
      if (sida === 3) return [p, 0, 0, 1];
      if (sida === 5) return [p, B, 0, -1];
      if (sida === 4) return [L, p, -1, 0];
      if (sida === 6) return [0, p, 1, 0];
      return null;
    };
    const ink = Math.max(L, B) / 120;
    d.ops.forEach(o => {
      if (o.typ === 'hal' && o.sida === 1) {
        const c = o.d >= 30 ? FARG.kopp : o.d >= 8 ? FARG.hal8 : FARG.hal5;
        P.push({ t: 'circle', x: o.x, y: o.y, r: Math.max(o.d / 2, ink * 0.9), fill: c });
      } else if (o.typ === 'hal') {
        const k2 = kant(o.sida, o.x); if (!k2) return;
        const [x, y, dx, dy] = k2, len = Math.max(21, ink * 3);
        P.push({ t: 'line', x1: x, y1: y, x2: x + dx * len, y2: y + dy * len, stroke: FARG.hal8, lw: 1.6 });
      } else if (o.typ === 'hylltapp') {
        for (let i = 0; i < 3; i++) { const x = o.langd + Math.sign(o.steg) * 32 * i; P.push({ t: 'circle', x, y: o.y, r: Math.max(2.5, ink * 0.9), fill: FARG.hal5 }); }
      } else if (o.typ === 'spar') {
        const x1 = Math.max(0, o.x0), x2 = Math.min(L, o.x0 + o.langd);
        P.push({ t: 'line', x1, y1: o.y + 1.8, x2, y2: o.y + 1.8, stroke: FARG.spar, lw: 1.2 });
      }
    });
    return { prim: P, box: [0, 0, L, B] };
  }

  // ---------- SVG ----------
  function svg(r, px = 600, opts = {}) {
    const [bx, by, bw, bh] = r.box, s = px / bw, H = bh * s;
    const Y = y => (by + bh - y) * s, X = x => (x - bx) * s;
    const o = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${px} ${H.toFixed(1)}" width="${opts.fit ? '100%' : px}" ${opts.fit ? '' : `height="${H.toFixed(1)}"`}>`];
    const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    r.prim.forEach(p => {
      const st = `stroke="${p.stroke || 'none'}" stroke-width="${p.lw || 0.6}"${p.dash ? ` stroke-dasharray="${p.dash.join(' ')}"` : ''}`;
      if (p.t === 'rect') o.push(`<rect x="${X(p.x)}" y="${Y(p.y + p.h)}" width="${p.w * s}" height="${p.h * s}" fill="${p.fill || 'none'}" ${st}/>`);
      else if (p.t === 'line') o.push(`<line x1="${X(p.x1)}" y1="${Y(p.y1)}" x2="${X(p.x2)}" y2="${Y(p.y2)}" ${st}/>`);
      else if (p.t === 'circle') o.push(`<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="${Math.max(p.r * s, 1)}" fill="${p.fill || 'none'}" ${st}/>`);
      else if (p.t === 'text') o.push(`<text x="${X(p.x)}" y="${Y(p.y)}" font-size="${(p.size || 9) * 1.25}" text-anchor="${p.anchor || 'start'}" fill="${p.color || '#222'}" font-family="Barlow, Helvetica, sans-serif">${esc(p.s)}</text>`);
    });
    o.push('</svg>');
    return o.join('');
  }

  // ---------- jsPDF ----------
  const lat = s => String(s).replace(/−/g, '-').replace(/–/g, '-').replace(/≥/g, '>=').replace(/≤/g, '<=').replace(/→/g, '->').replace(/•/g, '-').replace(/[^\x00-\xff]/g, '?');
  function hex(c) {
    if (!c || c === 'none') return null;
    const m = /rgba?\((\d+),\s*(\d+),\s*(\d+)/.exec(c); if (m) return [+m[1], +m[2], +m[3]];
    const h = c.replace('#', ''); const f = h.length === 3 ? h.split('').map(x => x + x).join('') : h;
    return [parseInt(f.slice(0, 2), 16), parseInt(f.slice(2, 4), 16), parseInt(f.slice(4, 6), 16)];
  }
  function pdf(doc, r, ox, oy, maxW, maxH) {
    const [bx, by, bw, bh] = r.box, s = Math.min(maxW / bw, maxH / bh);
    const X = x => ox + (x - bx) * s, Y = y => oy + (by + bh - y) * s;
    r.prim.forEach(p => {
      const f = hex(p.fill), st = hex(p.stroke);
      doc.setLineWidth((p.lw || 0.6) * 0.25);
      if (st) doc.setDrawColor(...st);
      if (f) doc.setFillColor(...f);
      doc.setLineDashPattern(p.dash ? p.dash.map(v => v * 0.3) : [], 0);
      const mode = f && st ? 'FD' : f ? 'F' : 'S';
      if (p.t === 'rect') { if (f || st) doc.rect(X(p.x), Y(p.y + p.h), p.w * s, p.h * s, mode); }
      else if (p.t === 'line') { doc.line(X(p.x1), Y(p.y1), X(p.x2), Y(p.y2)); }
      else if (p.t === 'circle') { doc.circle(X(p.x), Y(p.y), Math.max(p.r * s, 0.25), mode); }
      else if (p.t === 'text') {
        doc.setFontSize(p.size || 8); const c = hex(p.color || '#222'); doc.setTextColor(...c);
        doc.text(lat(p.s), X(p.x), Y(p.y), { align: p.anchor === 'middle' ? 'center' : p.anchor === 'end' ? 'right' : 'left' });
      }
    });
    doc.setLineDashPattern([], 0);
    return s;
  }

  return { front, sida, delbild, svg, pdf, lat, FARG };
});
