# Svep: stegbåge med fler klossar (ingen limmad låda) – klossavstånd x djup x nockhöjd, fyllt sidoregelfack, ev. hanbjälke
import json, math, sys, itertools
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
def kor(nock, PT, depth, cc, KL, han):
    src = base.replace("Bredd, Nockhojd, SyllH, Spets = 4000.0, 3500.0, 120.0, 0.0", f"Bredd, Nockhojd, SyllH, Spets = 4000.0, {nock}, 120.0, 0.0")
    src = src.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", f"PlyT, BagB, KlossH = {PT}, 70.0, {depth - 2 * PT}")
    src = src.replace("KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0", f"KlossL, FackKlossL, KlossCCmax = {KL}, {max(KL, 250.0)}, {cc}")
    src = src.replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5", "SidoregelZ, SidoregelH, FackSpel = 1900.0, 0.0, 0.0")  # fack fyllt (sidoregel på insidan)
    g = {}; exec(src, g)
    if han:
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
    n_kl = len(g['klossar'])
    return ut, n_kl
res = []
for nock, (PT, depth), (cc, KL), han in itertools.product((3500, 2800, 2400), ((15, 100), (15, 160), (30, 230)), ((300, 120), (200, 120), (150, 120)), (False, True)):
    ut, n = kor(nock, PT, depth, cc, KL, han)
    r = dict(nock=nock, djup=depth, remsa=PT, kloss_cc=cc, klossar_per_halva=n, hanbjalke=han, **ut, max=max(ut.values()))
    res.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(res, open('svep_klossar.json', 'w'), ensure_ascii=False, indent=1)
