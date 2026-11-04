import json, math
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
src0 = base.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", "PlyT, BagB, KlossH = 36.0, 95.0, 24.0").replace("KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0","KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 450.0").replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5","SidoregelZ, SidoregelH, FackSpel = 1900.0, 95.0, 2.5")
def kor(zh):
    g = {}; exec(src0, g); g['qp'] = 0.5 * 1.25 * 20 ** 2 / 1000
    if zh:
        _b = g['build']
        def b2(E, _b=_b, g=g):
            m, H = _b(E)
            def nz(side):
                ss = H[side]['ss']; k = min(range(len(ss)), key=lambda k: abs(g['BagCz'] + g['R'] * math.sin(g['FotV'] + ss[k] / g['R']) - zh))
                return H[side]['inn'][k]
            m.elem(nz(1), nz(-1), 45 * 120, 1.0, 'hanbjalke', hinge_j=True); return m, H
        g['build'] = b2
    m, H = g['build'](g['E0'] / g['gM']); gd = g['gd']; ut = {}
    for nm, case, dur, cpi in (('snö', dict(G=1.2*gd, S2=1.5*gd), 'snö', 0.0), ('snö jämn', dict(G=1.2*gd, S0=1.5*gd), 'snö', 0.0), ('vind', dict(G=1.2*gd, W=1.5*gd, S0=1.5*gd*0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5*gd), 'vind', 0.2)):
        F, _ = g['loads'](m, H, case, cpi); u, f, Rr = g['solve'](m, F); lam = g['buckling'](m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        ut[nm] = round(float(g['kontroll'](m, H, f, amp, g['kmod'][dur])[0][0]), 2)
    # hanbjälkens längd (inre fläns, insida)
    R, cx, cz = g['R'], g['BagCx'], g['BagCz']; ri = R - g['h_r'] - 18
    L = 2 * (-cx + math.sqrt(max(ri * ri - (zh - cz) ** 2, 0))) if zh else 0
    return ut, round(L)
for zh in (0, 2100, 2300, 2500, 2700, 2900, 3100):
    ut, L = kor(zh); print(json.dumps(dict(z=zh, langd=L, **ut, max=max(ut.values())), ensure_ascii=False), flush=True)
