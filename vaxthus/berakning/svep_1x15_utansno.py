# Victor: räkna inte med snölast. Bara egenvikt + vind 20 m/s (tryck och lyft). Fläns 1x15, kloss regel 45.
import json, math
exec(open('svep_1x15.py').read().split('res = []')[0].replace(
 "for nm, case, dur, cpi in (('snö', dict(G=1.2*gd, S2=1.5*gd), 'snö', 0.0), ('snö jämn', dict(G=1.2*gd, S0=1.5*gd), 'snö', 0.0), ('vind', dict(G=1.2*gd, W=1.5*gd, S0=1.5*gd*0.6), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5*gd), 'vind', 0.2)):",
 "for nm, case, dur, cpi in (('vind', dict(G=1.2*gd, W=1.5*gd), 'vind', -0.3), ('lyft', dict(G=1.0, W=1.5*gd), 'vind', 0.2)):"))
res = []
for BB, D, cc, KLa, bcc, han in ((70, 100, 250, 45, 1250, 2400), (70, 125, 250, 45, 1250, 2400), (95, 100, 250, 45, 1250, 2400), (95, 125, 250, 45, 1250, 2400), (95, 150, 250, 45, 1250, 2400),
                                 (95, 125, 200, 45, 1250, 2400), (95, 125, 250, 45, 1250, 0), (70, 125, 250, 45, 1050, 2400), (95, 150, 200, 45, 1250, 0)):
    ut = kor(BB, D, cc, KLa, han=han, bagcc=bcc); r = dict(BB=BB, D=D, kl_cc=cc, bagcc=bcc, han=han, **ut, max=max(ut.values())); res.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(res, open('svep_1x15_utansno.json', 'w'), ensure_ascii=False, indent=1)
