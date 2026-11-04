import json
exec(open('svep_1x15.py').read().split('res = []')[0])
res = []
for BB, D, cc, KLa, bcc in ((95, 150, 200, 95, 1250), (95, 200, 200, 45, 1250), (95, 150, 150, 45, 1250), (95, 125, 200, 45, 833), (95, 150, 200, 45, 833), (95, 125, 250, 45, 625), (95, 150, 250, 45, 625), (70, 125, 250, 45, 625), (70, 150, 200, 45, 625)):
    ut = kor(BB, D, cc, KLa, bagcc=bcc); r = dict(BB=BB, D=D, kl_cc=cc, KL=KLa, bagcc=bcc, **ut, max=max(ut.values())); res.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
json.dump(res, open('svep_1x15b.json', 'w'), ensure_ascii=False, indent=1)
