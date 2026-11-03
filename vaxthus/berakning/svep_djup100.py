import json, itertools
src = open('svep_remsor.py').read().split("q30 =")[0]
src = src.replace("def kor(D, PT, BB, cc_bage, qp_vind, kl_cc=200.0):", "def kor(D, PT, BB, cc_bage, qp_vind, kl_cc=200.0, KL=120.0):").replace('KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, {kl_cc}', 'KlossL, FackKlossL, KlossCCmax = {KL}, {max(KL,250.0)}, {kl_cc}')
g = {}; exec(src, g)
q30 = 0.5 * 1.25 * 30 ** 2 / 1000
res = []
for D, (PT, lab), BB, cc, kl in itertools.product((100, 120, 140), ((24, '2x12'), (36, '3x12')), (95, 120), (1250, 1000), (410, 200)):
    if PT * 2 >= D - 20: continue
    ut = g['kor'](D, PT, BB, cc, q30, kl)
    r = dict(djup=D, lameller=lab, bredd=BB, cc=cc, kloss_cc=kl, **{k: float(v) for k, v in ut.items()}); r['max'] = max(ut.values()); res.append(r)
    print(json.dumps(r, ensure_ascii=False, default=float), flush=True)
json.dump(res, open('svep_djup100.json', 'w'), ensure_ascii=False, indent=1, default=float)
