#!/usr/bin/env python3
"""Belastningsberäkning växthusets bågar (förenklad, EN 1990/1991/1995 + EKS).
Kör: ~/retro_upscale/.venv/bin/python belastning.py   (numpy + scipy)

Modell: en mellanbåge (lastbredd BagCC) som plan ram. Bågen modelleras som den är byggd:
ytter- och innerremsa (15x70 plywood) som två balkar, klossarna som styva radiella förband
(Vierendeel-/stegbalk). Fot = led i syllen, nock = led (halvorna möts mot nockregeln).
Linjär analys + linjär knäckning (geometrisk styvhet) -> andra ordningens förstoring 1/(1-1/λ).
"""
import math, json, os
import numpy as np
from scipy.linalg import eig

# ---------------- indata (samma som Fusion-modellen) ----------------
Bredd, Nockhojd, SyllH, Spets = 4000.0, 3500.0, 120.0, 0.0
BagCC = 1250.0
PlyT, BagB, KlossH = 15.0, 70.0, 70.0
KlossL, FackKlossL, KlossCCmax = 120.0, 250.0, 550.0
SidoregelZ, SidoregelH, FackSpel = 1900.0, 145.0, 2.5
NockT = 45.0
HB = Bredd / 2; BagHojd = Nockhojd - SyllH
BagCx = (BagHojd ** 2 - HB ** 2 + 2 * BagHojd * Spets) / (2 * HB)
BagCz = SyllH - Spets
R = math.sqrt((BagCx + HB) ** 2 + Spets ** 2)
FotV = math.asin(Spets / R); NockV = math.acos((NockT / 2 + BagCx) / R)
BagLangd = R * (NockV - FotV)
FackS = R * (math.asin((SidoregelZ - BagCz) / R) - FotV); FackGap = SidoregelH + 2 * FackSpel
FotKlossS = KlossL / 2; FackNedreS = FackS - FackGap / 2 - FackKlossL / 2; FackOvreS = FackS + FackGap / 2 + FackKlossL / 2
NockKlossS = BagLangd - KlossL / 2
def gen_klossar(cc, full=False):
    global NedreM, NedreP, OvreM, OvreP
    if full == 'hel':
        return [(0.0, BagLangd, 'Låda hel')]
    if full:   # sidoskivor/limmad låda: hela bågen samverkar utom sidoregelns fack
        return [(0.0, FackS - FackGap / 2, 'Låda nedre'), (FackS + FackGap / 2, BagLangd, 'Låda övre')]
    NedreM = max(1, math.ceil((FackNedreS - FackKlossL / 2 - FotKlossS - KlossL / 2) / cc) - 1)
    NedreP = (FackNedreS - FotKlossS - (FackKlossL - KlossL) / 2) / (NedreM + 1)
    OvreM = max(1, math.ceil((NockKlossS - KlossL / 2 - FackOvreS - FackKlossL / 2) / cc) - 1)
    OvreP = (NockKlossS - FackOvreS - (FackKlossL - KlossL) / 2) / (OvreM + 1)
    kl = [(0.0, KlossL, 'Fotkloss')]
    for k in range(NedreM):
        c = FotKlossS + (k + 1) * NedreP; kl.append((c - KlossL / 2, c + KlossL / 2, 'Kloss nedre %d' % (k + 1)))
    kl.append((FackNedreS - FackKlossL / 2, FackNedreS + FackKlossL / 2, 'Fackkloss nedre'))
    kl.append((FackOvreS - FackKlossL / 2, FackOvreS + FackKlossL / 2, 'Fackkloss övre'))
    o0 = FackOvreS + (FackKlossL - KlossL) / 2
    for k in range(OvreM):
        c = o0 + (k + 1) * OvreP; kl.append((c - KlossL / 2, c + KlossL / 2, 'Kloss övre %d' % (k + 1)))
    kl.append((BagLangd - KlossL, BagLangd, 'Nockkloss'))
    return kl
klossar = gen_klossar(KlossCCmax)
SKRUV_PER_SIDA = {'Fackkloss nedre': 6, 'Fackkloss övre': 6}

# material: Metsä spruce plywood 15 mm (5 skikt), längs ytfanéret (EN 789/13986-värden ur Metsä Spruce Plywood Manual tab 11.2/11.3)
fmk, fck, ftk = 23.1, 17.6, 10.6        # MPa (böjning flatvis, tryck, drag)
E0 = 7034.0                              # MPa tryck/drag-E (används som E i ramen)
E005 = 0.84 * E0                         # 5 %-fraktil (antagen, EN 1995 för plywood saknar egen)
gM = 1.2
SK = {'SK1': 0.83, 'SK2': 0.91, 'SK3': 1.0}; gd = SK['SK2']
# klimatklass 3 (fuktigt växthus) – plywood EN 636-3: kmod medellång 0,65, kort 0,70
kmod = {'snö': 0.65, 'vind': 0.70}

# laster (Båstad kommun: sk 1,5 kN/m², vb 27 m/s – BFS 2024:6; terräng I vid kusten)
sk, Ce, Ct = 1.5, 1.0, 1.0
vb = 27.0; z0, zmin = 0.01, 1.0; z = max(Nockhojd / 1000, zmin)
kr = 0.19 * (z0 / 0.05) ** 0.07; cr = kr * math.log(z / z0); Iv = 1 / math.log(z / z0)
qp = (1 + 7 * Iv) * 0.5 * 1.25 * (cr * vb) ** 2 / 1000    # kN/m²
cpe = {'A': 0.8, 'B': -1.2, 'C': -0.4}   # EN 1991-1-4 fig 7.11, h/d = 0, f/d = 0,5 (vårt f/d = 0,85 ligger utanför diagrammet)
g_ark = (2 * PlyT * BagB * 460e-9 * 9.81 + 0.6 * KlossH * BagB * 460e-9 * 9.81) / 1   # kN/m längs bågen (remsor + ~60 % klossar)
g_film = 0.0025                                                                 # kN/m², 200 µm film

h_r = (KlossH + PlyT) / 2          # avstånd mittlinje -> remsans tyngdpunkt
A_ch, I_ch = BagB * PlyT, BagB * PlyT ** 3 / 12
W_ch = BagB * PlyT ** 2 / 6

# ---------------- ram-FEM ----------------
def frame_K(x1, y1, x2, y2, E, A, I):
    L = math.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / L, (y2 - y1) / L
    k = np.array([[E * A / L, 0, 0, -E * A / L, 0, 0],
                  [0, 12 * E * I / L ** 3, 6 * E * I / L ** 2, 0, -12 * E * I / L ** 3, 6 * E * I / L ** 2],
                  [0, 6 * E * I / L ** 2, 4 * E * I / L, 0, -6 * E * I / L ** 2, 2 * E * I / L],
                  [-E * A / L, 0, 0, E * A / L, 0, 0],
                  [0, -12 * E * I / L ** 3, -6 * E * I / L ** 2, 0, 12 * E * I / L ** 3, -6 * E * I / L ** 2],
                  [0, 6 * E * I / L ** 2, 2 * E * I / L, 0, -6 * E * I / L ** 2, 4 * E * I / L]])
    T = np.zeros((6, 6)); r = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]); T[:3, :3] = r; T[3:, 3:] = r
    return k, T, L

def geo_K(L, N):
    return N / (30 * L) * np.array([[0, 0, 0, 0, 0, 0], [0, 36, 3 * L, 0, -36, 3 * L], [0, 3 * L, 4 * L * L, 0, -3 * L, -L * L],
                                    [0, 0, 0, 0, 0, 0], [0, -36, -3 * L, 0, 36, -3 * L], [0, 3 * L, -L * L, 0, -3 * L, 4 * L * L]])

class Model:
    def __init__(s, E):
        s.E = E; s.nodes = []; s.el = []; s.fix = {}
    def node(s, x, y):
        s.nodes.append((x, y)); return len(s.nodes) - 1
    def elem(s, i, j, A, I, kind, hinge_j=False, tag=None):
        s.el.append(dict(i=i, j=j, A=A, I=I, kind=kind, tag=tag, hinge_j=hinge_j))

def build(E):
    m = Model(E)
    ds = 30.0
    cut = sorted(set([0.0, BagLangd] + [a for a, b, _ in klossar] + [b for a, b, _ in klossar]))
    ss = []
    for a, b in zip(cut[:-1], cut[1:]):
        n = max(1, int(math.ceil((b - a) / ds)))
        ss += [a + (b - a) * k / n for k in range(n)]
    ss.append(BagLangd)
    inkloss = lambda s_: any(a - 1e-6 <= s_ <= b + 1e-6 for a, b, _ in klossar)
    halves = {}
    for side in (1, -1):
        cx = -BagCx * side
        out, inn, mid = [], [], []
        for s_ in ss:
            th = FotV + s_ / R
            ux, uz = math.cos(th) * side, math.sin(th)       # radiell enhetsvektor
            px, pz = cx + R * ux, BagCz + R * uz
            out.append(m.node(px + h_r * ux, pz + h_r * uz)); inn.append(m.node(px - h_r * ux, pz - h_r * uz))
        for k in range(len(ss) - 1):
            m.elem(out[k], out[k + 1], A_ch, I_ch, 'ytter', tag=(side, ss[k], ss[k + 1]))
            m.elem(inn[k], inn[k + 1], A_ch, I_ch, 'inner', tag=(side, ss[k], ss[k + 1]))
        for k, s_ in enumerate(ss):
            if inkloss(s_):   # kloss: styv radiell länk
                m.elem(out[k], inn[k], KlossH * 70.0, 70.0 * 70.0 ** 3 / 12 * 5, 'kloss', tag=(side, s_))
        # fot: led i mittlinjen (kort styv länk till båda remsorna)
        th = FotV; ux, uz = math.cos(th) * side, math.sin(th)
        f = m.node(cx + R * ux, BagCz + R * uz)
        m.elem(f, out[0], 1e5, 1e9, 'stel'); m.elem(f, inn[0], 1e5, 1e9, 'stel')
        m.fix[f] = (1, 1, 0)
        th = FotV + BagLangd / R; ux, uz = math.cos(th) * side, math.sin(th)
        nn = m.node(cx + R * ux, BagCz + R * uz)
        m.elem(nn, out[-1], 1e5, 1e9, 'stel'); m.elem(nn, inn[-1], 1e5, 1e9, 'stel')
        halves[side] = dict(out=out, inn=inn, ss=ss, foot=f, nock=nn)
    # nock: led – högra nockpunkten styvt mot en länk som är ledad i den vänstra
    m.elem(halves[1]['nock'], halves[-1]['nock'], 1e5, 1e9, 'nockled', hinge_j=True)
    return m, halves

def assemble(m, N_el=None):
    nd = 3 * len(m.nodes); K = np.zeros((nd, nd)); KG = np.zeros((nd, nd)); info = []
    for e in m.el:
        x1, y1 = m.nodes[e['i']]; x2, y2 = m.nodes[e['j']]
        k, T, L = frame_K(x1, y1, x2, y2, m.E, e['A'], e['I'])
        if e['hinge_j']:   # statisk kondensering av rotation i j
            kk = k.copy(); i5 = 5
            for a in range(6):
                for b in range(6):
                    kk[a, b] = k[a, b] - k[a, i5] * k[i5, b] / k[i5, i5]
            kk[i5, :] = 0; kk[:, i5] = 0; k = kk
        dof = [3 * e['i'], 3 * e['i'] + 1, 3 * e['i'] + 2, 3 * e['j'], 3 * e['j'] + 1, 3 * e['j'] + 2]
        Kg = T.T @ k @ T
        K[np.ix_(dof, dof)] += Kg
        if N_el is not None and e['kind'] in ('ytter', 'inner'):
            KG[np.ix_(dof, dof)] += T.T @ geo_K(L, N_el[len(info)]) @ T
        info.append((k, T, dof, L))
    return K, KG, info

def free_dofs(m):
    fx = set()
    for n, (a, b, c) in m.fix.items():
        if a: fx.add(3 * n)
        if b: fx.add(3 * n + 1)
        if c: fx.add(3 * n + 2)
    # ledad nock: rotationsfrihetsgraden i vänster nocknod hänger bara på remsorna – ok
    return [d for d in range(3 * len(m.nodes)) if d not in fx]

def solve(m, F):
    K, _, info = assemble(m); fr = free_dofs(m)
    u = np.zeros(len(F)); u[fr] = np.linalg.solve(K[np.ix_(fr, fr)], F[fr])
    forces = []
    for k, T, dof, L in info:
        forces.append(k @ (T @ u[dof]))
    R_ = K @ u - F
    return u, forces, R_

def buckling(m, forces):
    N = [-f[0] for f in forces]          # drag positivt i lokal x vid nod i: f[0] = -N
    N = [f[3] for f in forces]           # N i ände j (drag +)
    K, KG, _ = assemble(m, N); fr = free_dofs(m)
    Kf, Gf = K[np.ix_(fr, fr)], KG[np.ix_(fr, fr)]
    w = eig(Kf, -Gf, right=False)
    w = np.real(w[np.isfinite(w) & (np.abs(np.imag(w)) < 1e-6)])
    w = w[w > 0]
    return float(w.min()) if len(w) else float('inf')

# ---------------- laster ----------------
def loads(m, halves, case, cpi=0.0):
    """kN/m² / kN/m -> nodkrafter (N) på ytterremsan. case: dict med 'G','S0'(uniform), 'S2'(osymm), 'W' faktorer"""
    F = np.zeros(3 * len(m.nodes)); b = BagCC / 1000   # lastbredd m
    xs60 = []
    # horisontell bredd ls mellan β = 60°-punkterna (β = lutning)
    th60 = math.radians(30)   # β = 90° - θ  -> β < 60° när θ > 30° (rund båge, spets 0)
    x60 = abs(-BagCx + R * math.cos(max(th60, FotV)))
    ls = 2 * x60
    mu3 = min(2.0, 0.2 + 10 * BagHojd / Bredd)
    for side, H in halves.items():
        for k in range(len(H['ss']) - 1):
            i, j = H['out'][k], H['out'][k + 1]
            (x1, y1), (x2, y2) = m.nodes[i], m.nodes[j]
            L = math.hypot(x2 - x1, y2 - y1) / 1000; dx = abs(x2 - x1) / 1000
            xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
            nx, ny = (y2 - y1), -(x2 - x1); nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
            # normal utåt: peka bort från bågcentrum
            ccx = -BagCx * side
            if (xm - ccx) * nx + (ym - BagCz) * ny < 0: nx, ny = -nx, -ny
            fx = fy = 0.0
            fy -= case.get('G', 0) * (g_ark * L * 1 + g_film * b * L)      # kN
            ax = abs(xm)
            beta = math.degrees(math.atan2(abs(x2 - x1), abs(y2 - y1)))   # 0 = lodrät... lutning mot horisontalen:
            beta = 90 - beta
            if case.get('S0'):
                if beta <= 60: fy -= case['S0'] * 0.8 * Ce * Ct * sk * b * dx
            if case.get('S2'):
                if ax <= x60:
                    # triangel, 0 vid krön och vid 60°-punkten, topp mitt emellan (ls/4 från krön)
                    t = ax / x60; tri = (t / 0.5) if t <= 0.5 else (1 - t) / 0.5
                    mu = mu3 * (1.0 if side > 0 else 0.5) * tri     # läsida = höger (+x)
                    fy -= case['S2'] * mu * Ce * Ct * sk * b * dx
            if case.get('W'):
                # vind från vänster (-x). zon längs spännvidden d = Bredd: A [-HB, -HB/2], B, C [HB/2, HB]
                if xm < -HB / 2: c = cpe['A']
                elif xm > HB / 2: c = cpe['C']
                else: c = cpe['B']
                p = qp * (c - cpi)          # + = tryck inåt
                fx -= case['W'] * p * b * L * nx; fy -= case['W'] * p * b * L * ny
            for n_ in (i, j):
                F[3 * n_] += fx / 2 * 1000; F[3 * n_ + 1] += fy / 2 * 1000
    return F, dict(ls=ls, mu3=mu3, x60=x60)

def kc_chord(Lfri):
    i = PlyT / math.sqrt(12); lam = Lfri / i
    lr = lam / math.pi * math.sqrt(fck / E005)
    k = 0.5 * (1 + 0.2 * (lr - 0.3) + lr ** 2)
    return min(1.0, 1 / (k + math.sqrt(k * k - lr * lr))), lam

def kontroll(m, halves, forces, amp, kmd):
    fcd, ftd, fmd = kmd * fck / gM, kmd * ftk / gM, kmd * fmk / gM
    # fri längd för remsan mellan klossar (radiell knäckning) – tas per element
    def fri(s0):
        lo, hi = 0.0, BagLangd
        for a, b, _ in klossar:
            if b <= s0 + 1e-6: lo = max(lo, b)
            if a >= s0 + 1e-6: hi = min(hi, a)
        return max(hi - lo, 1.0)
    worst = []
    for e, f in zip(m.el, forces):
        if e['kind'] not in ('ytter', 'inner'): continue
        N = f[3]                                         # drag +
        M = max(abs(f[2]), abs(f[5])) * amp
        side, s0, s1 = e['tag']
        sc = M / W_ch; sn = N / A_ch
        if N < 0:
            Lf = fri((s0 + s1) / 2)
            inside = any(a - 1e-6 <= (s0 + s1) / 2 <= b + 1e-6 for a, b, _ in klossar)
            kc, lam = (1.0, 0) if inside else kc_chord(Lf)
            u = -sn / (kc * fcd) + sc / fmd
        else:
            u = sn / ftd + sc / fmd
        worst.append((u, e['kind'], side, round(s0), round(N / 1000, 2), round(M / 1e6, 3)))
    worst.sort(reverse=True)
    return worst

def skruv(m, halves, forces):
    """skjuvkraft som klossens skruvar ska föra över = skillnad i remsans normalkraft över klossen (per sida)"""
    res = []
    els = {(e['kind'], e['tag'][0], round(e['tag'][1], 3)): f for e, f in zip(m.el, forces) if e['kind'] in ('ytter', 'inner')}
    for side in (1, -1):
        ss = halves[side]['ss']
        for a, b, nm in klossar:
            for kind in ('ytter', 'inner'):
                ka = max([s_ for s_ in ss if s_ <= a + 1e-6]) if a > 0 else None
                kb = max([s_ for s_ in ss if s_ <= b + 1e-6 and s_ < BagLangd - 1e-6]) if b < BagLangd else None
                fa = els.get((kind, side, round(ka - 0, 3))) if ka is not None and a > 0 else None
                # normalkraft strax före och strax efter klossen
                before = [f for (kk, sd, s0), f in els.items() if kk == kind and sd == side and abs(s0 + 0) < 1e9]
                prev = [els[(kind, side, round(s0, 3))] for s0 in ss[:-1] if s0 < a - 1e-6 and (kind, side, round(s0, 3)) in els]
                nxt = [els[(kind, side, round(s0, 3))] for s0 in ss[:-1] if s0 >= b - 1e-6 and (kind, side, round(s0, 3)) in els]
                Na = prev[-1][3] if prev else 0.0
                Nb = nxt[0][3] if nxt else 0.0
                res.append((abs(Nb - Na) / 1000, nm, kind, side))
    res.sort(reverse=True)
    return res

def kor(etikett):
    m, H = build(E0 / gM); mS, HS = build(E0)
    fall = {
        'ULS1 snö jämn':          (dict(G=1.2 * gd, S0=1.5 * gd), 'snö', 0.0),
        'ULS2 snö osymmetrisk':   (dict(G=1.2 * gd, S2=1.5 * gd), 'snö', 0.0),
        'ULS3 snö osymm + 0,3 vind':  (dict(G=1.2 * gd, S2=1.5 * gd, W=1.5 * gd * 0.3), 'vind', -0.3),
        'ULS4 vind + 0,6 snö':    (dict(G=1.2 * gd, W=1.5 * gd, S0=1.5 * gd * 0.6), 'vind', -0.3),
        'ULS5 vind, lyft':        (dict(G=1.0, W=1.5 * gd), 'vind', 0.2),
    }
    res = {}
    for nm, (case, dur, cpi) in fall.items():
        F, geo = loads(m, H, case, cpi)
        u, forces, Rr = solve(m, F)
        lam = buckling(m, forces)
        amp = 1 / (1 - 1 / lam) if lam > 1 else float('inf')
        w = kontroll(m, H, forces, amp, kmod[dur])
        fot = {('höger' if s_ > 0 else 'vänster'): (round(float(Rr[3 * H[s_]['foot']]) / 1000, 2), round(float(Rr[3 * H[s_]['foot'] + 1]) / 1000, 2)) for s_ in (1, -1)}
        sk_ = skruv(m, H, forces)
        Nmax = min(f[3] for e, f in zip(m.el, forces) if e['kind'] in ('ytter', 'inner'))
        res[nm] = dict(lambda_cr=round(lam, 2), forstoring=round(amp, 2), max_utnyttj=round(w[0][0], 2), var=w[0][1:],
                       fot_H_V_kN=fot, skruv_max_kN_per_sida=round(sk_[0][0], 2), skruv_var=sk_[0][1:], max_tryck_remsa_kN=round(Nmax / 1000, 2))
    for nm, case in (('SLS snö osymm', dict(G=1, S2=1)), ('SLS vind', dict(G=1, W=1))):
        F, geo = loads(mS, HS, case, -0.3)
        u, forces, Rr = solve(mS, F)
        res[nm] = dict(max_deformation_mm=round(max(math.hypot(u[3 * n], u[3 * n + 1]) for n in range(len(mS.nodes))), 1))
    print('=====', etikett)
    for k, v in res.items(): print(' ', k, json.dumps(v, ensure_ascii=False))
    return res

def main():
    global klossar
    alla = {}
    for et, cc, full in (('Nu: klossar c/c ~0,5 m', 550, False), ('Klossar c/c ~0,3 m', 300, False), ('Klossar c/c ~0,2 m', 200, False), ('Låda: limmade sidoskivor/full samverkan', 0, True), ('Låda + fyllt sidoregelfack', 0, 'hel')):
        klossar = gen_klossar(cc, full)
        alla[et] = kor(et)
    meta = dict(R=round(R, 1), BagLangd=round(BagLangd, 1), qp=round(qp, 3), mu3=min(2.0, 0.2 + 10 * BagHojd / Bredd), gd=gd, kmod=kmod, sk=sk, vb=vb)
    print(json.dumps(meta, ensure_ascii=False))
    json.dump(dict(meta=meta, varianter=alla), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultat.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
