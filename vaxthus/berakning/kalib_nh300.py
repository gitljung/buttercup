# Kalibrering: Norhage TRÄ300 (3 m bred, ~2,45 m hög, c/c 1050) med uppmätta/uppskattade mått, våra laster.
import json, math, itertools
base = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 40.0")
def kor(nock, PT, BB, D, cc_kl, KL, qp):
    src = base.replace("Bredd, Nockhojd, SyllH, Spets = 4000.0, 3500.0, 120.0, 0.0", f"Bredd, Nockhojd, SyllH, Spets = 3000.0, {nock}, 120.0, 0.0")
    src = src.replace("PlyT, BagB, KlossH = 15.0, 70.0, 70.0", f"PlyT, BagB, KlossH = {PT}, {BB}, {D - 2 * PT}")
    src = src.replace("KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0", f"KlossL, FackKlossL, KlossCCmax = {KL}, {max(KL, 150.0)}, {cc_kl}")
    src = src.replace("SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5", "SidoregelZ, SidoregelH, FackSpel = 1300.0, 0.0, 0.0")
    src = src.replace("BagCC = 1250.0", "BagCC = 1050.0")
    g = {}; exec(src, g)
    if qp: g['qp'] = qp
    m, H = g['build'](g['E0'] / g['gM']); gd = g['gd']; ut = {}
    for nm, case, dur, cpi in (('snö', dict(G=1.2 * gd, S2=1.5 * gd), 'snö', 0.0), ('vind', dict(G=1.2 * gd, W=1.5 * gd, S0=1.5 * gd * 0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5 * gd), 'vind', 0.2)):
        F, _ = g['loads'](m, H, case, cpi); u, f, Rr = g['solve'](m, F); lam = g['buckling'](m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        ut[nm] = round(float(g['kontroll'](m, H, f, amp, g['kmod'][dur])[0][0]), 2)
    return ut
for D, cc in ((100, 250), (120, 250), (100, 350)):
    for lab, v in (('20 m/s', 20), ('25 m/s', 25), ('Eurocode', None)):
        q = 0.5 * 1.25 * v ** 2 / 1000 if v else None
        print(json.dumps(dict(djup=D, kloss_cc=cc, niva=lab, **kor(2450.0, 15.0, 70.0, D, cc, 120.0, q)), ensure_ascii=False), flush=True)
