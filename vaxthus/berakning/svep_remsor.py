# Svep: böjda raka remsor (bara raka sågsnitt) – lamelltjocklek 12/15, antal lager, remsbredd, bågdjup, c/c. Klossar c/c 200, fyllt fack, hanbjälke, vind 30 m/s.
import json, math, itertools
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
def kor(D, PT, BB, cc_bage, qp_vind, kl_cc=200.0):
    src = base.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", f"PlyT, BagB, KlossH = {PT}, {BB}, {D - 2 * PT}")
    src = src.replace("KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0", f"KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, {kl_cc}")
    src = src.replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5", "SidoregelZ, SidoregelH, FackSpel = 1900.0, 0.0, 0.0")
    src = src.replace("BagCC = 1250.0", f"BagCC = {cc_bage}")
    g = {}; exec(src, g)
    if qp_vind: g['qp'] = qp_vind
    _b = g['build']
    def b2(E, _b=_b, g=g):
        m, H = _b(E)
        def nz(side, z):
            ss = H[side]['ss']; k = min(range(len(ss)), key=lambda k: abs(g['BagCz'] + g['R'] * math.sin(g['FotV'] + ss[k] / g['R']) - z))
            return H[side]['inn'][k]
        m.elem(nz(1, 2000), nz(-1, 2000), 45 * 120, 1.0, 'hanbjalke', hinge_j=True); return m, H
    g['build'] = b2
    m, H = g['build'](g['E0'] / g['gM']); ut = {}; gd = g['gd']
    for nm, case, dur, cpi in (('snö', dict(G=1.2 * gd, S2=1.5 * gd), 'snö', 0.0), ('vind', dict(G=1.2 * gd, W=1.5 * gd, S0=1.5 * gd * 0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5 * gd), 'vind', 0.2)):
        F, _ = g['loads'](m, H, case, cpi); u, f, Rr = g['solve'](m, F); lam = g['buckling'](m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        ut[nm] = round(g['kontroll'](m, H, f, amp, g['kmod'][dur])[0][0], 2)
    return ut
q30 = 0.5 * 1.25 * 30 ** 2 / 1000
res = []
for (PT, lab_l), BB, D, cc in itertools.product(((24, '2x12'), (36, '3x12'), (30, '2x15')), (70, 95), (200, 250), (1000, 1250)):
    ut = kor(D, PT, BB, cc, q30)
    r = dict(lameller=lab_l, remsbredd=BB, djup=D, cc=cc, **ut, max=max(ut.values())); res.append(r)
    print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(res, open('svep_remsor.json', 'w'), ensure_ascii=False, indent=1)
