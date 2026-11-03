# Svep: båge SÅGAD i bågens plan ur plywood (Norhage-princip): flänsar = materialet utanför hålen, bryggor = klossar.
import json, math, itertools
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
def kor(D, b, cc_bage, qp_vind, fl=30.0, brygga=100.0, hal_cc=450.0, han=True, nock=3500):
    src = base.replace("Bredd, Nockhojd, SyllH, Spets = 4000.0, 3500.0, 120.0, 0.0", f"Bredd, Nockhojd, SyllH, Spets = 4000.0, {nock}, 120.0, 0.0")
    src = src.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", f"PlyT, BagB, KlossH = {fl}, {b}, {D - 2 * fl}")
    src = src.replace("KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0", f"KlossL, FackKlossL, KlossCCmax = {brygga}, {brygga}, {hal_cc}")
    src = src.replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5", "SidoregelZ, SidoregelH, FackSpel = 1900.0, 0.0, 0.0")
    src = src.replace("BagCC = 1250.0", f"BagCC = {cc_bage}")
    # plywood i planet, kurvsågad (fiberavvikelse): kantvis böjning ~ drag, 0,8 för fiberriktning
    src = src.replace("fmk, fck, ftk = 23.1, 17.6, 10.6", "fmk, fck, ftk = 10.6 * 0.8, 17.6 * 0.8, 10.6 * 0.8")
    src = src.replace("E0 = 7034.0", "E0 = 7034.0 * 0.85")
    g = {}; exec(src, g)
    if qp_vind: g['qp'] = qp_vind
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
    for nm, case, dur, cpi in (('snö', dict(G=1.2 * gd, S2=1.5 * gd), 'snö', 0.0), ('snö jämn', dict(G=1.2 * gd, S0=1.5 * gd), 'snö', 0.0), ('vind', dict(G=1.2 * gd, W=1.5 * gd, S0=1.5 * gd * 0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5 * gd), 'vind', 0.2)):
        F, _ = g['loads'](m, H, case, cpi); u, f, Rr = g['solve'](m, F); lam = g['buckling'](m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        ut[nm] = round(g['kontroll'](m, H, f, amp, g['kmod'][dur])[0][0], 2)
    return ut
q30 = 0.5 * 1.25 * 30 ** 2 / 1000
res = []
for (D, b), cc, (lab, q) in itertools.product(((150, 42), (180, 42), (180, 30), (220, 42), (220, 30)), (1000, 1250), (('30 m/s', q30), ('Eurocode', None))):
    ut = kor(D, b, cc, q)
    r = dict(djup=D, tjocklek=b, cc=cc, vindniva=lab, **ut, max=max(ut.values())); res.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(res, open('svep_sagad.json', 'w'), ensure_ascii=False, indent=1)
