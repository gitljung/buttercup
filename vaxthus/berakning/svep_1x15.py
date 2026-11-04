# Victor: fläns 1×15 plywood, klossar av 45 regel (som Norhage). 20 m/s, hanbjälke 2400, 4 m bred, c/c 1250.
import json, math
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
def kor(BB, D, cc, KLa, han=2400, bagcc=1250.0):
    src = base.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", f"PlyT, BagB, KlossH = 15.0, {BB}, {D - 30}")
    src = src.replace("KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0", f"KlossL, FackKlossL, KlossCCmax = {KLa}, {KLa}, {cc}")
    src = src.replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5", "SidoregelZ, SidoregelH, FackSpel = 1900.0, 95.0, 2.5")
    src = src.replace("BagCC = 1250.0", f"BagCC = {bagcc}")
    g = {}; exec(src, g); g['qp'] = 0.5 * 1.25 * 20 ** 2 / 1000
    if han:
        _b = g['build']
        def b2(E, _b=_b, g=g):
            m, H = _b(E)
            def nz(side):
                ss = H[side]['ss']; k = min(range(len(ss)), key=lambda k: abs(g['BagCz'] + g['R'] * math.sin(g['FotV'] + ss[k] / g['R']) - han))
                return H[side]['inn'][k]
            m.elem(nz(1), nz(-1), 45 * 120, 1.0, 'hanbjalke', hinge_j=True); return m, H
        g['build'] = b2
    m, H = g['build'](g['E0'] / g['gM']); gd = g['gd']; ut = {}
    for nm, case, dur, cpi in (('snö', dict(G=1.2*gd, S2=1.5*gd), 'snö', 0.0), ('snö jämn', dict(G=1.2*gd, S0=1.5*gd), 'snö', 0.0), ('vind', dict(G=1.2*gd, W=1.5*gd, S0=1.5*gd*0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5*gd), 'vind', 0.2)):
        F, _ = g['loads'](m, H, case, cpi); u, f, Rr = g['solve'](m, F); lam = g['buckling'](m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        ut[nm] = round(float(g['kontroll'](m, H, f, amp, g['kmod'][dur])[0][0]), 2)
    return ut
res = []
for BB in (70, 95):
    for D in (100, 125, 150):
        for cc in (250, 200):
            ut = kor(BB, D, cc, 45.0); r = dict(BB=BB, D=D, kl_cc=cc, **ut, max=max(ut.values())); res.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(res, open('svep_1x15.json', 'w'), ensure_ascii=False, indent=1)
