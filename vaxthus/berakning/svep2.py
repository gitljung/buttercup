import json
src = open('svep.py').read().split("for KH, PT, cc in")[0]
exec(src)
_build = build
def build_fast(E, fot_fast=True, nock_stel=True):
    m, H = _build(E)
    for s_ in (1, -1):
        if fot_fast: m.fix[H[s_]['foot']] = (1, 1, 1)
    if nock_stel:
        for e in m.el:
            if e['kind'] == 'nockled': e['hinge_j'] = False
    return m, H
for fot, nock in ((False, False), (True, False), (True, True)):
    build = lambda E, f=fot, n=nock: build_fast(E, f, n)
    for KH, PT, cc, kl in ((70, 15, 1250, 550), (70, 15, 1250, None), (170, 30, 1250, None)):
        print('fot fast' if fot else 'fot led', '| nock stel' if nock else '| nock led', '| djup', KH + 2 * PT, 'remsa', PT, 'klossar', kl or 'full', json.dumps(kor_kort(KH, PT, cc, kl=kl), ensure_ascii=False), flush=True)
