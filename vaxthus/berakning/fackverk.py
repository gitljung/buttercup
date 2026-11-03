# Fackverksbåge (Norhage-princip, bara raka snitt): böjda flänsar av limmade plywoodlameller + SNEDA klossar (diagonaler) i sicksack.
# Diagonaler = ledade stänger (C24 45 x BagB). Fot/nock = styva klossar. Hanbjälke till närmaste inre knutpunkt vid z 2 m.
import json, math, itertools, sys
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
fc_t, E_t, E05_t, gM_t = 21.0, 11000.0, 7400.0, 1.3       # C24 diagonaler
def kor(D, PT, BB, P, qp_vind, cc_bage=1250.0, nock=3500.0, han=True, diagT=45.0, detalj=False):
    src = base.replace("Bredd, Nockhojd, SyllH, Spets = 4000.0, 3500.0, 120.0, 0.0", f"Bredd, Nockhojd, SyllH, Spets = 4000.0, {nock}, 120.0, 0.0")
    src = src.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", f"PlyT, BagB, KlossH = {PT}, {BB}, {D - 2 * PT}")
    src = src.replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5", "SidoregelZ, SidoregelH, FackSpel = 1900.0, 0.0, 0.0")
    src = src.replace("BagCC = 1250.0", f"BagCC = {cc_bage}")
    g = {}; exec(src, g)
    if qp_vind: g['qp'] = qp_vind
    R, BagCx, BagCz, FotV, BagLangd, h_r = g['R'], g['BagCx'], g['BagCz'], g['FotV'], g['BagLangd'], g['h_r']
    n = max(2, round(BagLangd / (P / 2))); step = BagLangd / n
    panel = [k * step for k in range(n + 1)]
    g['klossar'] = []
    g['g_ark'] = (2 * PT * BB + (n * math.hypot(step, 2 * h_r) * diagT * BB) / BagLangd) * 460e-9 * 9.81
    def build(E):
        m = g['Model'](E); ds = 40.0
        ss = []
        for a, b in zip(panel[:-1], panel[1:]):
            k_ = max(1, int(math.ceil((b - a) / ds))); ss += [a + (b - a) * k / k_ for k in range(k_)]
        ss.append(BagLangd)
        idx = {round(p, 6): min(range(len(ss)), key=lambda k: abs(ss[k] - p)) for p in panel}
        halves = {}
        for side in (1, -1):
            cx = -BagCx * side; out, inn = [], []
            for s_ in ss:
                th = FotV + s_ / R; ux, uz = math.cos(th) * side, math.sin(th); px, pz = cx + R * ux, BagCz + R * uz
                out.append(m.node(px + h_r * ux, pz + h_r * uz)); inn.append(m.node(px - h_r * ux, pz - h_r * uz))
            for k in range(len(ss) - 1):
                m.elem(out[k], out[k + 1], g['A_ch'], g['I_ch'], 'ytter', tag=(side, ss[k], ss[k + 1]))
                m.elem(inn[k], inn[k + 1], g['A_ch'], g['I_ch'], 'inner', tag=(side, ss[k], ss[k + 1]))
            pn = []
            for k, p in enumerate(panel):
                i = idx[round(p, 6)]; pn.append(out[i] if k % 2 == 0 else inn[i])
            for k in range(n):
                a_, b_ = pn[k], pn[k + 1]
                if k == n - 1 and n % 2 == 1: pass
                m.elem(a_, b_, diagT * BB * E_t / g['E0'], 1e-3, 'diag', hinge_j=True, tag=(side, k))
            th = FotV; ux, uz = math.cos(th) * side, math.sin(th); f = m.node(cx + R * ux, BagCz + R * uz)
            m.elem(f, out[0], 1e5, 1e9, 'stel'); m.elem(f, inn[0], 1e5, 1e9, 'stel'); m.fix[f] = (1, 1, 0)
            th = FotV + BagLangd / R; ux, uz = math.cos(th) * side, math.sin(th); nn = m.node(cx + R * ux, BagCz + R * uz)
            m.elem(nn, out[-1], 1e5, 1e9, 'stel'); m.elem(nn, inn[-1], 1e5, 1e9, 'stel')
            halves[side] = dict(out=out, inn=inn, ss=ss, foot=f, nock=nn, pinn=[pn[k] for k in range(1, n + 1, 2)])
        m.elem(halves[1]['nock'], halves[-1]['nock'], 1e5, 1e9, 'nockled', hinge_j=True)
        if han:
            def nz(side):
                return min(halves[side]['pinn'], key=lambda q: abs(m.nodes[q][1] - 2000))
            m.elem(nz(1), nz(-1), 45 * 120 * E_t / g['E0'], 1.0, 'hanbjalke', hinge_j=True)
        return m, halves
    def kontroll(m, H, forces, amp, kmd):
        fcd, ftd, fmd = kmd * g['fck'] / g['gM'], kmd * g['ftk'] / g['gM'], kmd * g['fmk'] / g['gM']
        w = []
        for e, f in zip(m.el, forces):
            if e['kind'] in ('ytter', 'inner'):
                N = f[3]; M = max(abs(f[2]), abs(f[5])) * amp; sc = M / g['W_ch']; sn = N / g['A_ch']
                if N < 0:
                    kc, _ = g['kc_chord'](2 * step); u = -sn / (kc * fcd) + sc / fmd
                else: u = sn / ftd + sc / fmd
                w.append((u, e['kind'], round(N / 1000, 2)))
            elif e['kind'] == 'diag':
                (x1, y1), (x2, y2) = m.nodes[e['i']], m.nodes[e['j']]; L = math.hypot(x2 - x1, y2 - y1)
                N = f[3] * amp; A = diagT * BB
                lam = L / (diagT / math.sqrt(12)); lr = lam / math.pi * math.sqrt(fc_t / E05_t); kk = 0.5 * (1 + 0.2 * (lr - 0.3) + lr ** 2)
                kc = min(1.0, 1 / (kk + math.sqrt(kk * kk - lr * lr)))
                u = (-N / A) / (kc * kmd * fc_t / gM_t) if N < 0 else (N / A) / (kmd * 14.5 / gM_t)
                w.append((u, 'diag', round(N / 1000, 2)))
        w.sort(reverse=True); return w
    m, H = build(g['E0'] / g['gM']); gd = g['gd']; ut = {}; Nd = 0.0; var = {}
    for nm, case, dur, cpi in (('snö', dict(G=1.2 * gd, S2=1.5 * gd), 'snö', 0.0), ('snö jämn', dict(G=1.2 * gd, S0=1.5 * gd), 'snö', 0.0),
                               ('vind', dict(G=1.2 * gd, W=1.5 * gd, S0=1.5 * gd * 0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5 * gd), 'vind', 0.2)):
        F, _ = g['loads'](m, H, case, cpi); u, f, Rr = g['solve'](m, F); lam = g['buckling'](m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        w = kontroll(m, H, f, amp, g['kmod'][dur]); ut[nm] = round(w[0][0], 2); var[nm] = w[0][1]
        Nd = max(Nd, max(abs(ff[3]) for e, ff in zip(m.el, f) if e['kind'] == 'diag') / 1000)
    mS, HS = build(g['E0']); F, _ = g['loads'](mS, HS, dict(G=1, W=1), -0.3); u, _, _ = g['solve'](mS, F)
    defl = max(math.hypot(u[3 * k], u[3 * k + 1]) for k in range(len(mS.nodes)))
    return dict(ut=ut, var=var, diag_per_halva=n, panel_mm=round(step), diag_maxkraft_kN=round(Nd, 2), vind_def_mm=round(defl))

if __name__ == '__main__':
    q30 = 0.5 * 1.25 * 30 ** 2 / 1000
    res = []
    for (PT, lab), D, ndiag, cc in itertools.product(((24, '2x12'), (36, '3x12')), (150, 200, 250), (12, 16, 20, 24), (1250.0, 1000.0)):
        P = 2 * 4100.0 / ndiag
        r = kor(D, PT, 95.0, P, q30, cc_bage=cc)
        row = dict(lameller=lab, djup=D, cc=cc, vindniva='30 m/s', **r, max=max(r['ut'].values())); res.append(row)
        print(json.dumps(row, ensure_ascii=False, default=float), flush=True)
        json.dump(res, open('svep_fackverk.json', 'w'), ensure_ascii=False, indent=1, default=float)
