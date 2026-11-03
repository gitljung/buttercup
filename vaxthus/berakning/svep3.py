import json, math
src = open('svep.py').read().split("for KH, PT, cc in")[0]
exec(src)
_build = build
def build_tie(E, zt=2400.0, diag=False):
    m, H = _build(E)
    def nod_vid_z(side, z):
        ss = H[side]['ss']; best = None
        for k, s_ in enumerate(ss):
            th = FotV + s_ / R
            if best is None or abs(BagCz + R * math.sin(th) - z) < best[0]: best = (abs(BagCz + R * math.sin(th) - z), k)
        return H[side]['inn'][best[1]]
    a, b = nod_vid_z(1, zt), nod_vid_z(-1, zt)
    m.elem(a, b, 45 * 120, 1.0, 'hanbjalke', hinge_j=True)   # 45x120 hanbjälke, ledad i ändarna (I ≈ 0)
    if diag:
        for s_ in (1, -1):
            m.elem(H[s_]['foot'], nod_vid_z(-s_, zt), 45 * 120, 1.0, 'diagonal', hinge_j=True)
    return m, H
for zt, diag in ((2400, False), (2000, False), (2800, False)):
    build = lambda E, z=zt, d=diag: build_tie(E, z, d)
    for KH, PT, cc, kl in ((70, 15, 1250, 550), (70, 15, 1250, 300), (70, 15, 1250, None), (170, 15, 1250, None), (170, 30, 1250, None)):
        print('hanbjälke z', zt, '| djup', KH + 2 * PT, 'remsa', PT, 'klossar', kl or 'full', json.dumps(kor_kort(KH, PT, cc, kl=kl), ensure_ascii=False), flush=True)
