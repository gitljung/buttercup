#!/usr/bin/env python3
"""Verkstadsritning A3 (PDF), båge "som Norhage" (steg 13b): fläns 1×15 plywood × 95, klossar regel 45×95 × 130,
fotkloss 300, djup 75. Värden ur Fusion (v13_param.json). Blad 1 halvbåge, 2 remsor, 3 klossar + laskar.
Skriver ritning_bage.pdf (+ ritning_bage_1..3 .svg/.png)."""
import json, math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, '..', 'fusion', 'v13_param.json'), encoding='utf-8'))
src = open(os.path.join(HERE, 'ritning_bage_B.py'), encoding='utf-8').read()
INK, GREY, RED, PLY, PLY2, WOOD, LIGHT = '#1d1d1b', '#8a8a86', '#c8321a', '#ecd6a6', '#d9b77a', '#c9a46b', '#f4f1ea'
exec(src.split('# ---------------- svg i mm ----------------')[1].split('def arcpts')[0].replace('båge B · mått', 'båge 1×15 · mått'))     # Sheet-klassen
# ---------------- geometri ----------------
Bredd, Nockhojd, SyllH, NockT = P['Bredd'], P['Nockhojd'], P['SyllH'], P['NockT']
HB = Bredd / 2; BH = Nockhojd - SyllH; cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
PT, BB, KH, D = P['PlyT'], P['BagB'], P['KlossH'], P['BagDjup']
ri, ro = R - D / 2, R + D / 2
XN = NockT / 2
def th_end(r): return math.acos((XN + cx) / r)
def pt(r, th): return (-cx + r * math.cos(th), r * math.sin(th))
def x_at(r, z): return -cx + math.sqrt(r * r - z * z)
def zc(r, x): return math.sqrt(r * r - (x + cx) ** 2)
def arcpts(r, t0, t1, n=60): return [pt(r, t0 + (t1 - t0) * k / n) for k in range(n + 1)]
def band(r0, r1, t0, t1, n=40): return arcpts(r1, t0, t1, n) + list(reversed(arcpts(r0, t0, t1, n)))
KL, FKL, FOTL, BL = P['KlossL'], P['FackKlossL'], P['FotKlossL'], P['BagLangd']
NM, OM, NP, OP = int(P['NedreMellan']), int(P['OvreMellan']), P['NedrePitch'], P['OvrePitch']
FN, FO = P['FackNedreS'], P['FackOvreS']
# (start, längd, typ) längs mittlinjen – samma formler som skissen Bågform
KLS = [(0.0, FOTL, 'fot')]
KLS += [(P['FotKlossS'] + k * NP - KL / 2, KL, 'kloss') for k in range(1, NM + 1)]
KLS += [(FN - FKL / 2, FKL, 'fack'), (FO - FKL / 2, FKL, 'fack')]
o0 = FO + (FKL - KL) / 2
KLS += [(o0 + k * OP - KL / 2, KL, 'kloss') for k in range(1, OM + 1)]
KLS += [(BL - KL, KL, 'nock')]
NKL = len(KLS)
SRH, SRT, SPEL = P['SidoregelH'], P['SidoregelT'], P['FackSpel']
Gp = SRH + 2 * SPEL
zf = P['SidoregelZ'] - SyllH
LASKL = P['LaskL']
SKY, SKI = P['SkarvYtterS'], P['SkarvInnerS']                  # skarvar längs mittlinjen (mitt på fackklossarna)
OVER, SKIVA_L, SKIVA_B, KERF = 25.0, 2500.0, 1200.0, 3.0
FL = [('inner', ri, ri + PT, SKI), ('ytter', ro - PT, ro, SKY)]
def flen(r0, r1): rm = (r0 + r1) / 2; return rm * th_end(rm)
# hanbjälke: bultas genom den kloss som ligger närmast hanbjälkens höjd
HanZ, HanH, HanX, HanXu = P['HanZ'] - SyllH, P['HanH'], P['HanX'], P['HanXu']
def han_x(z): return HanXu + (HanX - HanXu) * (z - (HanZ - HanH / 2)) / HanH
def s2z(s): return R * math.sin(s / R)
kh = min([k for k in KLS if k[2] == 'kloss'], key=lambda k: abs(s2z(k[0] + k[1] / 2) - HanZ))
kh_i = KLS.index(kh)
BULT = [pt(R, (kh[0] + kh[1] / 2 + d) / R) for d in (-30, 30)]
bult_ok = all(HanZ - HanH / 2 + 15 < z < HanZ + HanH / 2 - 15 and x < han_x(z) - 15 for x, z in BULT)
# nocklask (raka snitt)
NLT, LX, LAV = P['NockLaskT'], P['NockLaskL'] / 2, P['NockLaskAvdrag']
rr = ro - LAV; sag = 0.0
NBB, NBH, NLU = P['NockBalkB'], P['NockBalkH'], P['NockLaskUnder']
ZOK = zc(ro, XN)                                   # nockens ytterkant (lokalt, fotens nivå = 0)
zE, zS = zc(rr, LX), zc(rr, XN); zN = ZOK - NBH; zU0 = zN - NLU; zUE = zU0 - (zS - zE)
LASK = [(-LX, zE), (-XN, zS), (-XN, zN), (XN, zN), (XN, zS), (LX, zE), (LX, zUE), (0, zU0), (-LX, zUE)]
NHALV, NNLASK = 2 * int(P['AntalBagar']), 2 * (int(P['AntalBagar']) - 2) + 2

# ======================= BLAD 1 =======================
S = Sheet()
S.frame('HALVBÅGE – FÄRDIG', f'{NHALV} st (2 per båge). Fläns 1 × {PT:.0f} plywood, klossar regel 45×95.', 'blad 1/3')
sc = 1 / 15.0; ox, oy = 28, 272
X = lambda x: ox + x * sc; Y = lambda z: oy - z * sc
T = lambda pts: [(X(x), Y(z)) for x, z in pts]
S.t(14, 18, 'HALVBÅGE, SIDA (sett från husets insida)  1:15', 4.0, w='bold')
for nm, a, b, sj in FL:
    rm = (a + b) / 2; tj = sj / R
    S.p(T(band(a, b, 0, tj)), PLY, INK, 0.15)
    S.p(T([(max(x, XN), z) for x, z in band(a, b, tj, th_end(a))]), PLY, INK, 0.15)
    # skarvlask utanpå/innanför flänsen
    r0, r1 = (ro, ro + PT) if nm == 'ytter' else (ri - PT, ri)
    S.p(T(band(r0, r1, (sj - LASKL / 2) / R, (sj + LASKL / 2) / R, 8)), '#f6e7c6', RED, 0.25)
for i, (s0, L, typ) in enumerate(KLS):
    poly = [(max(x, XN), z) for x, z in band(ri + PT, ro - PT, s0 / R, (s0 + L) / R, 4)]
    S.p(T(poly), WOOD, INK, 0.2)
S.p(T(arcpts(ri, 0, th_end(ri))), 'none', INK, 0.4, close=False); S.p(T(arcpts(ro, 0, th_end(ro))), 'none', INK, 0.4, close=False)
S.l(X(x_at(ri, 0)), Y(0), X(x_at(ro, 0)), Y(0), INK, 0.4)
S.l(X(XN), Y(zc(ri, XN)), X(XN), Y(zc(ro, XN)), INK, 0.4)
for i, (s0, L, typ) in enumerate(KLS):
    th = (s0 + L / 2) / R; bx, bz = pt(ro + 230, th); kx, kz = pt(R, th)
    S.l(X(kx), Y(kz), X(bx), Y(bz), RED, 0.15); S.bub(X(bx), Y(bz), str(i + 1))
# sidoregel
thf = math.asin(zf / R); srx, srz = pt(R, thf)
ux, uz = math.cos(thf), math.sin(thf); tx, tz = -math.sin(thf), math.cos(thf)
S.p(T([(srx + ux * a + tx * b, srz + uz * a + tz * b) for a, b in ((-SRT / 2, -SRH / 2), (SRT / 2, -SRH / 2), (SRT / 2, SRH / 2), (-SRT / 2, SRH / 2))]), '#ffffff', RED, 0.25, dash='0.8 0.5')
S.t(X(srx) + 4, Y(srz) + 1, 'sidoregel', 2.5, col=RED)
# hanbjälke + bultar
S.p(T([(HanX - 900, HanZ - HanH / 2), (HanXu, HanZ - HanH / 2), (HanX, HanZ + HanH / 2), (HanX - 900, HanZ + HanH / 2)]), 'none', RED, 0.25, close=False, dash='1.2 0.6')
for bx, bz in BULT: S.c(X(bx), Y(bz), 0.6, 'white', RED, 0.3)
S.t(X(HanX - 880), Y(HanZ + HanH / 2) - 1.2, 'hanbjälke (monteras efter)', 2.5, col=RED)
# nocklask
S.p(T([(XN, zS), (LX, zE), (LX, zUE), (0.0, zU0), (0.0, zN), (XN, zN)]), 'none', RED, 0.3, dash='1.2 0.6')
S.p(T([(-NBB / 2 + XN * 0, zN), (NBB / 2, zN), (NBB / 2, ZOK), (0, ZOK)]), 'none', RED, 0.3, dash='1.2 0.6')
# mått
fi, fo = x_at(ri, 0), x_at(ro, 0); zni, zno = zc(ri, XN), zc(ro, XN)
S.dim((X(XN), Y(0)), (X(fo), Y(0)), -9, f'{fo - XN:.0f}')
S.dim((X(0), Y(0)), (X(fi), Y(0)), -15, f'{fi:.0f} (husets mitt → fot insida)')
S.dim((X(fi), Y(0)), (X(fo), Y(0)), 4, f'{fo - fi:.0f}', 2.4)
S.l(X(0), Y(-30), X(0), Y(zno + 150), GREY, 0.15, '3 1 0.6 1')
S.t(X(0) - 1, Y(1500), 'husets mitt', 2.6, col=GREY, rot=-90.0)
S.dim((X(XN), Y(0)), (X(XN), Y(zno)), 12, f'{zno:.0f} (ytterkant nock)')
S.dim((X(XN), Y(0)), (X(XN), Y(zni)), 6, f'{zni:.0f}', 2.6)
S.dim((X(0), Y(zno)), (X(XN), Y(zno)), 6, f'{XN:.1f}', 2.4)
S.dim((X(fo), Y(0)), (X(fo), Y(zf)), 26, f'{zf:.0f} sidoregel', 2.6)
S.l(X(fo) + 27, Y(zf), X(srx) + 3, Y(zf), GREY, 0.12, '1 0.6')
S.dim((X(fo), Y(0)), (X(fo), Y(HanZ)), 33, f'{HanZ:.0f} hanbjälke', 2.6)
S.l(X(fo) + 34, Y(HanZ), X(x_at(ro, HanZ)) + 3, Y(HanZ), GREY, 0.12, '1 0.6')
S.dim((X(0), Y(zE + 40)), (X(LX), Y(zE + 40)), 5, f'lask {LX:.0f}', 2.4)
lx, lz = pt(ri, 0.62); S.l(X(lx), Y(lz), X(lx) - 30, Y(lz) + 8, INK, 0.15); S.t(X(lx) - 31, Y(lz) + 9, f'R {ri:.0f} insida', 3.0, 'end', w='bold')
lx, lz = pt(ro, 0.85); S.l(X(lx), Y(lz), X(lx) + 40, Y(lz) - 6, INK, 0.15); S.t(X(lx) + 41, Y(lz) - 5.4, f'R {ro:.0f} utsida', 3.0, w='bold')
S.t(X(110), Y(-160), f'Cirkelns centrum: {cx:.0f} bortom husets mitt, i fotens nivå (andra halvans sida).', 2.7, col=GREY)
# tabell
tx0, ty0 = 200, 22
S.t(tx0, ty0, 'KLOSSAR – läge mätt längs YTTERKANTEN från foten (måttband på bågen)', 3.4, w='bold')
cols = ['nr', 'typ', 'längd', 'från', 'till', 'insida från', 'insida till']; cxs = [0, 8, 40, 56, 74, 92, 114]
for c_, x_ in zip(cols, cxs): S.t(tx0 + x_, ty0 + 6, c_, 2.8, w='bold')
for i, (s0, L, typ) in enumerate(KLS):
    so0, so1 = s0 * ro / R, (s0 + L) * ro / R; si0, si1 = s0 * ri / R, (s0 + L) * ri / R
    t_ = typ + (' (hanbj.)' if i == kh_i else '')
    for v, x_ in zip([str(i + 1), t_, f'{L:.0f}', f'{so0:.0f}', f'{so1:.0f}', f'{si0:.0f}', f'{si1:.0f}'], cxs): S.t(tx0 + x_, ty0 + 11 + i * 4.0, v, 2.7)
yy = ty0 + 11 + NKL * 4.0 + 1
S.t(tx0, yy, f'Fack för sidoregel {SRT:.0f}×{SRH:.0f} mellan fackklossarna = {Gp:.0f} fritt ({SPEL} spel/sida).', 2.7)
S.t(tx0, yy + 4, f'Ytterkant fot → nock ≈ {ro * th_end(ro):.0f}, insida ≈ {ri * th_end(ri):.0f}. Klossar c/c ≈ {NP:.0f} nedre / {OP:.0f} övre.', 2.7)
S.t(tx0, yy + 8, 'Nockklossens övre ände kapas lodrätt med flänsarna.', 2.7)
# snitt
ax0, ay0, s3 = 200, 122, 0.5
S.t(ax0, ay0 - 4, 'SNITT A-A (genom kloss)  1:2', 3.4, w='bold')
S.r(ax0, ay0, PT * s3, BB * s3, PLY, INK, 0.2); S.r(ax0 + PT * s3, ay0, KH * s3, BB * s3, WOOD, INK, 0.2); S.r(ax0 + (PT + KH) * s3, ay0, PT * s3, BB * s3, PLY, INK, 0.2)
S.dim((ax0, ay0 + BB * s3), (ax0 + D * s3, ay0 + BB * s3), -5, f'{D:.0f} bågdjup')
S.dim((ax0, ay0 + BB * s3), (ax0 + PT * s3, ay0 + BB * s3), -10, f'{PT:.0f}', 2.4)
S.dim((ax0 + PT * s3, ay0 + BB * s3), (ax0 + (PT + KH) * s3, ay0 + BB * s3), -10, f'{KH:.0f}', 2.4)
S.dim((ax0 + D * s3, ay0), (ax0 + D * s3, ay0 + BB * s3), -5, f'{BB:.0f}')
for i, t_ in enumerate([f'innerfläns 1 × {PT:.0f} × {BB:.0f} plywood',
                        f'kloss regel 45×95 (45 radiellt, 95 tvärs bågen)',
                        f'ytterfläns 1 × {PT:.0f} × {BB:.0f} plywood',
                        'flänsarna böjs runt klossarna: lim + 2 skruv 5×60 per fläns och kloss',
                        f'skarv: en per fläns, mitt på en fackkloss + lask {LASKL:.0f} (blad 3)']):
    S.t(ax0, ay0 + BB * s3 + 18 + i * 4.5, t_, 2.7)
# hel båge
hx0, hy0, s4 = 350, 200, 1 / 50
S.t(hx0 - 50, hy0 - 86, 'HEL BÅGE (2 halvor) 1:50', 3.4, w='bold')
for sd in (1, -1):
    S.p([(hx0 + sd * x * s4, hy0 - z * s4) for x, z in arcpts(ro, 0, th_end(ro))] + [(hx0 + sd * x * s4, hy0 - z * s4) for x, z in reversed(arcpts(ri, 0, th_end(ri)))], PLY, INK, 0.2)
S.p([(hx0 - HanXu * s4, hy0 - (HanZ - HanH / 2) * s4), (hx0 + HanXu * s4, hy0 - (HanZ - HanH / 2) * s4), (hx0 + HanX * s4, hy0 - (HanZ + HanH / 2) * s4), (hx0 - HanX * s4, hy0 - (HanZ + HanH / 2) * s4)], WOOD, INK, 0.2)
S.dim((hx0 - Bredd / 2 * s4, hy0), (hx0 + Bredd / 2 * s4, hy0), -6, f'{Bredd:.0f} mittlinje fot')
S.dim((hx0 - fo * s4, hy0), (hx0 + fo * s4, hy0), -11, f'{2 * fo:.0f} utsida')
S.dim((hx0 + 55, hy0), (hx0 + 55, hy0 - zno * s4), -3, f'{zno:.0f}', 2.4)
S.t(hx0 + 50, hy0 - zno * s4 - 3, f'+ syll {SyllH:.0f} = nock {zno + SyllH:.0f}', 2.4, 'end', col=GREY)
S.t(hx0, hy0 - (HanZ + HanH) * s4 - 1.5, f'hanbjälke 45×120 × {2 * HanXu:.0f} (underkant)', 2.5, 'middle')
S.t(hx0, hy0 - zno * s4 - 5, f'nockbalk {NBB:.0f}×{NBH:.0f} i glipan {NockT:.0f} + nocklask {2 * LX:.0f}', 2.5, 'middle')
notes = ['ANMÄRKNINGAR',
         f'Foten kapas vågrätt, nocken lodrätt. Flänsarna kapas med {OVER:.0f} mm övermått i ändarna och putsas efter montering.',
         f'Hanbjälke mitt på kloss {kh_i + 1}: 2 bult M10×160, Ø11 genom klossen, ±30 från klossens mitt längs bågen' + ('.' if bult_ok else ' – KOLLA LÄGET.'),
         f'  Änden kapas snett längs bågen: överkant x = {HanX:.0f}, underkant x = {HanXu:.0f} från husets mitt.',
         'Gavelbågar (4 halvor): ingen hanbjälke, nocklask bara på insidan.',
         'Röd streckad = monteras senare (sidoregel, hanbjälke, nocklask). Röd heldragen = skarvlask.',
         f'Kontroll: två halvor ihop = {Bredd:.0f} c/c fot (mittlinjen), utsida {2 * fo:.0f}.']
for i, n_ in enumerate(notes): S.t(200, 222 + i * 4.6, n_, 3.0 if i == 0 else 2.7, w='bold' if i == 0 else 'normal')
p1 = S.save('ritning_bage_1')

# ======================= BLAD 2 =======================
S = Sheet()
S.frame('PLYWOODREMSOR', 'Kapplista per halvbåge + skivplan', 'blad 2/3')
S.t(14, 18, f'REMSOR {BB:.0f} × {PT:.0f} ur konstruktionsplywood {PT:.0f} × {SKIVA_L:.0f} × {SKIVA_B:.0f} (raka snitt, sågsnitt {KERF:.0f})', 4.0, w='bold')
rows = []
for nm, a, b, sj in FL:
    rm = (a + b) / 2; L = flen(a, b); j = sj * rm / R
    rows.append((nm, rm, L, j, j + OVER, L - j + OVER))
pieces = [r[4] for r in rows] + [r[5] for r in rows] + [LASKL, LASKL]
tx0, ty0 = 16, 30
S.t(tx0, ty0, f'KAPPLISTA – EN HALVBÅGE (4 flänsbitar + 2 skarvlaskar). Flänsbitar med {OVER:.0f} mm övermått i ytteränden.', 3.3, w='bold')
hdr = ['fläns', 'radie (mitt)', 'båglängd', 'skarv vid', 'bit A (fot)', 'bit B (nock)']; cxs = [0, 18, 42, 64, 86, 110]
for c_, x_ in zip(hdr, cxs): S.t(tx0 + x_, ty0 + 7, c_, 2.8, w='bold')
for i, rw in enumerate(rows):
    for v, x_ in zip([rw[0], f'R {rw[1]:.0f}', f'{rw[2]:.0f}', f'{rw[3]:.0f}', f'{rw[4]:.0f}', f'{rw[5]:.0f}'], cxs): S.t(tx0 + x_, ty0 + 12 + i * 4.4, v, 2.9, w='bold' if x_ >= 86 else 'normal')
S.t(tx0, ty0 + 12 + 2 * 4.4, 'lask', 2.9); S.t(tx0 + 86, ty0 + 12 + 2 * 4.4, f'2 × {LASKL:.0f}', 2.9, w='bold'); S.t(tx0 + 110, ty0 + 12 + 2 * 4.4, '(en per skarv)', 2.9)
yy = ty0 + 12 + 3 * 4.4 + 3
nrem = NHALV * 4 + math.ceil(NHALV * 2 * (LASKL + KERF) / SKIVA_L)
for i, n_ in enumerate([f'Skarven mäts längs flänsens egen kant från foten och ligger mitt på en fackkloss (innerfläns nedre, ytterfläns övre).',
                        'Bitarna läggs stumt med lim i ändarna; lasken limmas och skruvas över skarven.',
                        f'Totalt {NHALV} halvbågar: {NHALV * 4} flänsbitar (en remsa var) + {NHALV * 2} laskar ({math.floor(SKIVA_L / (LASKL + KERF))} per remsa)',
                        f'  = {nrem} remsor = {math.ceil(nrem / 12)} skivor (12 remsor per skiva). Spillet från bit B räcker ofta till laskarna.']):
    S.t(tx0, yy + i * 4.4, n_, 2.75)
gx0, gy0, gs = 16, 112, 0.042
S.t(gx0, gy0 - 5, 'SKARVLÄGEN, utvikt (fot till vänster, nock till höger)  ca 1:24', 3.3, w='bold')
for i, rw in enumerate(rows):
    y = gy0 + i * 9
    S.r(gx0 + 14, y, rw[4] * gs, 4.4, PLY, INK, 0.2); S.r(gx0 + 14 + rw[4] * gs, y, rw[5] * gs, 4.4, '#f6e7c6', INK, 0.2)
    S.r(gx0 + 14 + (rw[4] - LASKL / 2) * gs, y + (-2.2 if rw[0] == 'ytter' else 4.6), LASKL * gs, 1.6, '#f6e7c6', RED, 0.25)
    S.t(gx0, y + 3.4, rw[0], 2.7)
    S.t(gx0 + 14 + rw[4] * gs / 2, y + 3.3, f'A {rw[4]:.0f}', 2.5, 'middle'); S.t(gx0 + 14 + rw[4] * gs + rw[5] * gs / 2, y + 3.3, f'B {rw[5]:.0f}', 2.5, 'middle')
for s0, L, typ in KLS:
    S.r(gx0 + 14 + (s0 + OVER) * gs, gy0 + 5.2, L * gs, 2.4, WOOD, INK, 0.1)
S.t(gx0 + 14, gy0 + 22, 'brunt mellan flänsarna = klossarnas lägen, röd = skarvlask', 2.5, col=GREY)
px0, py0, ps = 225, 30, 0.072
S.t(px0, py0 - 4, f'SKIVPLAN – 1 skiva {SKIVA_L:.0f} × {SKIVA_B:.0f} → 12 remsor  1:14', 3.3, w='bold')
S.r(px0, py0, SKIVA_L * ps, SKIVA_B * ps, '#f8f3e6', INK, 0.35)
y = 0
for k in range(12):
    S.r(px0, py0 + y * ps, SKIVA_L * ps, BB * ps, PLY if k % 2 == 0 else '#f1dfb6', INK, 0.15)
    S.t(px0 + 2, py0 + (y + BB / 2) * ps + 1, f'remsa {k + 1}', 2.3); y += BB + KERF
rest = SKIVA_B - y + KERF
S.dim((px0 + SKIVA_L * ps, py0), (px0 + SKIVA_L * ps, py0 + SKIVA_B * ps), -5, f'{SKIVA_B:.0f}')
S.dim((px0, py0 + SKIVA_B * ps), (px0 + SKIVA_L * ps, py0 + SKIVA_B * ps), 6, f'{SKIVA_L:.0f}')
S.dim((px0, py0), (px0, py0 + BB * ps), 4, f'{BB:.0f}', 2.4)
S.t(px0, py0 + SKIVA_B * ps + 15, f'12 × {BB:.0f} + 11 snitt × {KERF:.0f} = {12 * BB + 11 * KERF:.0f}; rest {rest:.0f} mm.', 2.75)
S.t(px0, py0 + SKIVA_B * ps + 19.5, 'Såga längs skivans långa riktning (ytskiktets fibrer längs remsan).', 2.75)
S.t(px0, py0 + SKIVA_B * ps + 24, 'Anslagslist + cirkelsåg / spårsåg; samma anslag till alla remsor.', 2.75)
ey = py0 + SKIVA_B * ps + 34
S.t(px0, ey, 'EN REMSA: flänsbit + spill', 3.3, w='bold')
for i, pc in enumerate([rows[0][4], rows[0][5], rows[1][4], rows[1][5]]):
    yq = ey + 5 + i * 5.5; rest_ = SKIVA_L - pc - KERF; nl = int(rest_ // (LASKL + KERF))
    S.r(px0, yq, pc * ps * 0.5, 3.4, PLY, INK, 0.15); x = px0 + pc * ps * 0.5
    for _ in range(nl): S.r(x, yq, LASKL * ps * 0.5, 3.4, '#f6e7c6', RED, 0.15); x += (LASKL + KERF) * ps * 0.5
    S.t(px0 + SKIVA_L * ps * 0.5 + 3, yq + 2.8, f'{pc:.0f} + spill {rest_:.0f} → {nl} lask', 2.5)
p2 = S.save('ritning_bage_2')

# ======================= BLAD 3 =======================
S = Sheet()
S.frame('KLOSSAR OCH LASKAR', 'Raka snitt. Klossar av regel 45×95.', 'blad 3/3')
S.t(14, 18, 'KLOSSAR AV REGEL 45×95  1:2', 4.0, w='bold')
ks = 0.5
def kloss(x0, y0, L, titel, antal):
    S.t(x0, y0 - 4, titel, 3.2, w='bold')
    S.r(x0, y0, L * ks, BB * ks, WOOD, INK, 0.3)
    for fx in (25, L - 25):
        for fy in (30, BB - 30): S.c(x0 + fx * ks, y0 + fy * ks, 1.0, 'white', RED, 0.25)
    S.dim((x0, y0 + BB * ks), (x0 + L * ks, y0 + BB * ks), -5, f'{L:.0f} (längs bågen)')
    S.dim((x0 + L * ks, y0), (x0 + L * ks, y0 + BB * ks), -5, f'{BB:.0f}')
    sx = x0 + L * ks + 22
    S.r(sx, y0, KH * ks, BB * ks, WOOD, INK, 0.3)
    S.dim((sx, y0 + BB * ks), (sx + KH * ks, y0 + BB * ks), -5, f'{KH:.0f}', 2.4)
    S.t(sx + KH * ks + 4, y0 + 8, 'regel 45×95, kapas', 2.7); S.t(sx + KH * ks + 4, y0 + 13, antal, 2.7, w='bold')
    S.t(sx + KH * ks + 4, y0 + 18, 'röda = skruv 5×60 genom flänsen', 2.7, col=RED); S.t(sx + KH * ks + 4, y0 + 23, '(2 från insidan, 2 från utsidan)', 2.7, col=RED)
nk = sum(1 for k in KLS if k[2] in ('kloss', 'fack', 'nock'))
kloss(18, 32, KL, f'Kloss {KL:.0f} (vanlig, fack och nock)', f'{nk} per halvbåge = {NHALV * nk} st')
kloss(18, 100, FOTL, f'Fotkloss {FOTL:.0f}', f'1 per halvbåge = {NHALV} st')
regel = NHALV * (nk * (KL + KERF) + FOTL + KERF) / 1000
S.t(18, 168, f'Regel 45×95 totalt ≈ {regel:.0f} m (+ spill). Kapa vinkelrätt, alla klossar lika.', 2.8)
S.t(18, 173, 'Klossen är rak och flänsen böjd: på 130 blir glipan mot innerflänsen under 1 mm, på fotklossen ca 3 mm – limmet fyller.', 2.8)
S.t(18, 178, 'Nockklossen läggs med övermått och kapas lodrätt tillsammans med flänsarna.', 2.8)
# skarvlask
S.t(18, 196, f'SKARVLASK  {PT:.0f} × {BB:.0f} × {LASKL:.0f} plywood  1:4', 3.6, w='bold')
lsx, lsy, l4 = 18, 204, 0.25
S.r(lsx, lsy, LASKL * l4, BB * l4, '#f6e7c6', INK, 0.3)
for fx in (40, 100, LASKL - 100, LASKL - 40):
    for fy in (25, BB - 25): S.c(lsx + fx * l4, lsy + fy * l4, 0.8, 'white', RED, 0.25)
S.l(lsx + LASKL / 2 * l4, lsy - 2, lsx + LASKL / 2 * l4, lsy + BB * l4 + 2, RED, 0.3, '1 0.6')
S.dim((lsx, lsy + BB * l4), (lsx + LASKL * l4, lsy + BB * l4), -5, f'{LASKL:.0f}')
S.dim((lsx + LASKL * l4, lsy), (lsx + LASKL * l4, lsy + BB * l4), -5, f'{BB:.0f}')
S.t(lsx + LASKL * l4 + 14, lsy + 5, 'Ytterfläns: lasken på utsidan. Innerfläns: på insidan.', 2.7)
S.t(lsx + LASKL * l4 + 14, lsy + 10, 'Skarven (röd streckad) mitt på lasken = mitt på fackklossen.', 2.7)
S.t(lsx + LASKL * l4 + 14, lsy + 15, f'PU-lim + 8 skruv 4,5×25. {NHALV * 2} st totalt.', 2.7, w='bold')
# nocklask
lx0, ly0, ls = 262, 60, 0.24
S.t(lx0 - 40, 18, f'NOCKLASK  {NLT:.0f} mm plywood  1:4', 4.0, w='bold')
zmin = min(z for x, z in LASK); zmax = max(z for x, z in LASK)
LX_ = lambda x: lx0 + (x + LX) * ls; LY_ = lambda z: ly0 + (zmax - z) * ls
S.p([(LX_(x), LY_(z)) for x, z in LASK], PLY, INK, 0.35)
for sd in (1, -1):
    for r_ in (ri, ro):
        pts = [(sd * x, zc(r_, x)) for x in [XN + (LX + 40 - XN) * k / 30 for k in range(31)]]
        S.p([(LX_(x), LY_(z)) for x, z in pts], 'none', GREY, 0.2, close=False, dash='1 0.6')
for sd in (1, -1):
    for k in range(3):
        xs_ = XN + 60 + k * 85; zs = (zc(ri + PT, xs_) + zc(ro - PT, xs_)) / 2
        S.c(LX_(sd * xs_), LY_(zs), 0.9, 'white', RED, 0.25)
S.p([(LX_(-NBB / 2), LY_(zN)), (LX_(NBB / 2), LY_(zN)), (LX_(NBB / 2), LY_(ZOK)), (LX_(-NBB / 2), LY_(ZOK))], 'none', RED, 0.3, dash='1 0.6')
S.dim((LX_(-LX), LY_(zUE)), (LX_(LX), LY_(zUE)), -10, f'{2 * LX:.0f}')
S.dim((LX_(-XN), LY_(zS)), (LX_(XN), LY_(zS)), 4, f'urtag {2 * XN:.0f}', 2.4)
S.dim((LX_(LX), LY_(zUE)), (LX_(LX), LY_(zE)), -6, f'{zE - zUE:.1f}', 2.4)
S.dim((LX_(XN), LY_(zN)), (LX_(XN), LY_(zS)), -6 - 8, f'{zS - zN:.1f}', 2.4)
S.dim((LX_(0), LY_(zU0)), (LX_(0), LY_(zN)), 6, f'{NLU:.0f}', 2.4)
# punkttabell
tx, ty = lx0 - 40, LY_(zmin) + 24
S.t(tx, ty, 'Hörn (x från mitten, ned = mm under ytterkanten i nocken):', 2.9, w='bold')
names = ['A ände, överkant', 'B urtagets kant, överkant', 'C urtagets botten', 'D ände, underkant', 'E mitt, underkant']
vals = [(LX, ZOK - zE), (XN, ZOK - zS), (XN, ZOK - zN), (LX, ZOK - zUE), (0, ZOK - zU0)]
for i, (nm_, (xv, dv)) in enumerate(zip(names, vals)):
    S.t(tx, ty + 5 + i * 4.3, nm_, 2.75); S.t(tx + 58, ty + 5 + i * 4.3, f'x = ±{xv:.1f}', 2.75); S.t(tx + 82, ty + 5 + i * 4.3, f'ned {dv:.1f}', 2.75, w='bold')
for i, t_ in enumerate([f'Raka snitt. Urtaget ({2 * XN:.0f} × {zS - zN:.0f}) är där nockbalken {NBB:.0f}×{NBH:.0f} vilar.',
                        f'Överkanten {LAV:.0f} under bågens ytterkant så att nockens låsprofil går fri.',
                        'Röda = skruv 4,5×40 i flänsar och nockkloss + PU-lim. Gör en mall av den första.',
                        f'Antal: 2 per inre båge + 1 per gavelbåge (insidan) = {NNLASK} st.']):
    S.t(tx, ty + 30 + i * 4.5, t_, 2.75, w='bold' if i == 3 else 'normal')
p3 = S.save('ritning_bage_3')
from pypdf import PdfWriter
w = PdfWriter()
for p in (p1, p2, p3): w.append(p)
w.write(os.path.join(HERE, 'ritning_bage.pdf'))
print('klossar', NKL, [round(k[0]) for k in KLS], 'hanbj kloss', kh_i + 1, bult_ok, BULT, 'flänsbitar', [(round(r[4]), round(r[5])) for r in rows], 'remsor', nrem, 'regel m', round(regel))
