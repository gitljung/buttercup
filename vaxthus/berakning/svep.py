# Svep: vilken bågsektion klarar lasterna? (full samverkan = limmad/sidoskivad låda, fyllt fack)
import sys, json
src = open('belastning.py').read().replace("if __name__ == '__main__':\n    main()", "").replace("ds = 30.0", "ds = 60.0")
exec(src)
def kor_kort(KH, PT, cc_bag, full='hel', kl=None):
    global KlossH, PlyT, h_r, A_ch, I_ch, W_ch, BagCC, klossar
    KlossH, PlyT, BagCC = KH, PT, cc_bag
    h_r = (KlossH + PlyT) / 2; A_ch, I_ch, W_ch = BagB * PlyT, BagB * PlyT ** 3 / 12, BagB * PlyT ** 2 / 6
    klossar = gen_klossar(kl or 0, full if kl is None else False)
    m, H = build(E0 / gM); ut = {}
    for nm, case, dur, cpi in (('snö osymm', dict(G=1.2 * gd, S2=1.5 * gd), 'snö', 0.0), ('vind+snö', dict(G=1.2 * gd, W=1.5 * gd, S0=1.5 * gd * 0.6), 'vind', -0.3), ('vind lyft', dict(G=1.0, W=1.5 * gd), 'vind', 0.2)):
        F, _ = loads(m, H, case, cpi); u, f, Rr = solve(m, F); lam = buckling(m, f)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        ut[nm] = round(kontroll(m, H, f, amp, kmod[dur])[0][0], 2)
    return ut
for KH, PT, cc in ((70, 15, 1250), (170, 15, 1250), (170, 30, 1250), (270, 30, 1250), (170, 30, 900), (270, 30, 900)):
    print('djup', KH + 2 * PT, 'remsa', PT, 'c/c', cc, json.dumps(kor_kort(KH, PT, cc), ensure_ascii=False), flush=True)
