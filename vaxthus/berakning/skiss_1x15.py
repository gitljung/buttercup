#!/usr/bin/env python3
"""Skiss förslag 'som Norhage': fläns 1×15 plywood × 95, klossar regel 45×95 (45 längs bågen), djup 150,
klossar c/c ≤ 200, 13 bågar c/c 833, hanbjälke 2400. Skriver skiss_1x15_2d / _3d (.svg/.png)."""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
INK, GREY, RED, PLY, WOOD, HAN, FILM = '#1d1d1b', '#8a8a86', '#c8321a', '#ecd6a6', '#c9a46b', '#b98a4e', '#cfe3ea'
src = open(os.path.join(HERE, 'skiss_10klossar.py'), encoding='utf-8').read()
exec('class Svg:' + src.split('class Svg:')[1].split('# ======================= 2D')[0])
Bredd, Langd, Nockhojd, SyllH, NockT = 4000.0, 10000.0, 3500.0, 120.0, 45.0
HB = Bredd / 2; BH = Nockhojd - SyllH; cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
PT, BB, D = 15.0, 95.0, 150.0; KH = D - 2 * PT; ri, ro = R - D / 2, R + D / 2
KL, CC, NB = 45.0, 200.0, 13; BCC = Langd / (NB - 1)
HanZ = 2400.0 - SyllH
def th_end(r): return math.acos((NockT / 2 + cx) / r)
def P(r, th): return (-cx + r * math.cos(th), r * math.sin(th))
def arc(r, t0, t1, n=50): return [P(r, t0 + (t1 - t0) * k / n) for k in range(n + 1)]
def band(r0, r1, t0, t1, n=40): return arc(r1, t0, t1, n) + list(reversed(arc(r0, t0, t1, n)))
BL = R * th_end(R)
zf = 1900 - SyllH; sF = R * math.asin(zf / R); gap = 95 + 5
# klossar: fot, jämnt c/c ≤ 200 upp till facket, fackklossar på båda sidor, jämnt till nock, nockkloss
def jamn(a, b):
    n = max(1, math.ceil((b - a) / CC)); return [a + (b - a) * k / n for k in range(n + 1)]
s_ned = jamn(KL / 2, sF - gap / 2 - KL / 2); s_upp = jamn(sF + gap / 2 + KL / 2, BL - KL / 2)
KLS = s_ned + s_upp
# skarvar (skiva 2500): innerfläns och ytterfläns vid olika klossar, dubbelkloss där
def nar(s): return min(range(len(KLS)), key=lambda i: abs(KLS[i] - s))
J_in, J_ut = nar(2000.0), nar(2450.0)
HanX = -cx + math.sqrt(ro * ro - (HanZ + 60) ** 2)

S = Svg(2400, 1700)
S.txt(40, 62, 'FÖRSLAG "SOM NORHAGE": FLÄNS 1 × 15 PLYWOOD, KLOSSAR AV REGEL 45×95', 38, w='bold')
S.txt(40, 96, f'13 bågar c/c {BCC:.0f}, djup {D:.0f}, {len(KLS)} klossar per halvbåge (c/c ≤ {CC:.0f}), hanbjälke på 2,4 m. Beräknat 20 m/s + full snö Höör: 0,94. Skiss.', 20, col=GREY)
# ---- 1 halvbåge ----
fx, fy, fw, fh = 40, 120, 1180, 1240
S.frame(fx, fy, fw, fh, '1  HALVBÅGE', 'ca 1:12')
s1 = 0.3; ox, oy = fx + 70, fy + fh - 70
X = lambda x: ox + x * s1; Y = lambda z: oy - z * s1
T = lambda pts: [(X(x), Y(z)) for x, z in pts]
S.poly(T(band(ri, ri + PT, 0, th_end(ri + PT))), PLY, INK, 1.2)
S.poly(T(band(ro - PT, ro, 0, th_end(ro))), PLY, INK, 1.2)
for i, s in enumerate(KLS):
    dbl = i in (J_in, J_ut); L = 2 * KL if dbl else KL
    S.poly(T(band(ri + PT, ro - PT, (s - L / 2) / R, (s + L / 2) / R, 3)), WOOD, INK, 1.0)
for i, col in ((J_in, RED), (J_ut, RED)):
    th = KLS[i] / R; r = ri + PT / 2 if i == J_in else ro - PT / 2
    x, z = P(r, th); S.line(X(x) - 9 * math.cos(th), Y(z) + 9 * math.sin(th), X(x) + 9 * math.cos(th), Y(z) - 9 * math.sin(th), RED, 3)
    S.poly(T(band(ri - 3, ro + 3, (KLS[i] - 200) / R, (KLS[i] + 200) / R, 6)), 'none', RED, 1.6)
# sidoregel + hanbjälke
th = sF / R; x, z = P(R, th)
S.rect(X(x) - 6, Y(z) - 14, 12, 28, 'white', RED, 1.6)
S.poly(T([(HanX - 1100, HanZ - 60), (HanX, HanZ - 60), (HanX, HanZ + 60), (HanX - 1100, HanZ + 60)]), 'none', RED, 1.4)
S.line(X(0), Y(-20), X(0), Y(BH + 120), GREY, 1, '10 4 2 4')
x, z = P(ri, 0.5); S.leader(X(x), Y(z), X(700), Y(1000), f'Innerfläns 1 × 15 × 95\nR {ri:.0f}', '1')
x, z = P(ro, 0.35); S.leader(X(x), Y(z), X(2700), Y(1900), f'Ytterfläns 1 × 15 × 95\nR {ro:.0f}', '2')
x, z = P(R, KLS[3] / R); S.leader(X(x), Y(z), X(2700), Y(900), f'Kloss regel 45×95 × {KH:.0f}\n(45 längs bågen), c/c ≤ {CC:.0f}', '3')
x, z = P(R, KLS[J_ut] / R); S.leader(X(x), Y(z), X(2400), Y(3300), 'Skarv på dubbelkloss\n+ sidolaskar (detalj 3)', '4')
x, z = P(R, sF / R); S.leader(X(x), Y(z), X(2700), Y(1500), 'Sidoregel 19×95 genom fack', '5')
S.leader(X(HanX - 600), Y(HanZ), X(300), Y(2750), 'Hanbjälke 45×120\npå 2,4 m', '6')
S.txt(X(0) - 4, Y(BH + 150), 'husets mitt', 16, 'end', col=GREY)
S.txt(X(200), Y(-40) + 40, f'Fot: {P(ri, 0)[0]:.0f}–{P(ro, 0)[0]:.0f} från mitten · nock {BH + SyllH:.0f} med syll · båglängd ytterkant ≈ {ro * th_end(ro):.0f}', 18)
# ---- 2 snitt ----
sx, sy = 1240, 120
S.frame(sx, sy, 560, 560, '2  SNITT GENOM KLOSS', '1:2')
k = 1.9; bx, by = sx + 120, sy + 110
S.rect(bx, by, PT * k, BB * k, PLY, INK, 1.4); S.rect(bx + PT * k, by, KH * k, BB * k, WOOD, INK, 1.4); S.rect(bx + (PT + KH) * k, by, PT * k, BB * k, PLY, INK, 1.4)
for xx, lab in ((bx, 'insida'), (bx + D * k, 'utsida (film)')): S.txt(xx, by - 10, lab, 15, 'middle', col=GREY)
S.txt(bx + D * k / 2, by + BB * k + 34, f'15 + {KH:.0f} + 15 = {D:.0f}', 20, 'middle', w='bold')
S.txt(bx + D * k + 20, by + BB * k / 2, f'{BB:.0f}', 20, w='bold')
for i, t in enumerate(['Kloss: regel 45×95 kapad till 120,', 'flänsarna skruvas 2 × 5×50 i varje kloss', '(från ut- och insidan) + lim.', 'Ingen laminering – flänsen böjs runt', f'klossarna (R/t = {ri / PT:.0f}, ok för 15 mm).']):
    S.txt(sx + 20, sy + 420 + i * 26, t, 17)
# ---- 3 skarv ----
jx, jy = 1820, 120
S.frame(jx, jy, 540, 560, '3  SKARV I FLÄNSEN', '1:5')
k3 = 0.85; cxp, czp = jx + 270, jy + 300
def Q(u, v): return (cxp + u * k3, czp - v * k3)
S.rect(*Q(-280, D / 2), 560 * k3, PT * k3, PLY, INK, 1.2)
S.rect(*Q(-280, -D / 2 + PT), 560 * k3, PT * k3, PLY, INK, 1.2)
S.line(*Q(0, D / 2), *Q(0, D / 2 - PT), RED, 3)
for u in (-KL, 0): S.rect(*Q(u, D / 2 - PT), KL * k3, KH * k3, WOOD, INK, 1)
for u in (-200 - KL / 2, 200 - KL / 2): S.rect(*Q(u, D / 2 - PT), KL * k3, KH * k3, WOOD, INK, 1)
S.rect(*Q(-200, D / 2 + 4), 400 * k3, (D + 8) * k3, 'none', RED, 1.8)
for u in (-160, -110, -70, -25, 25, 70, 110, 160):
    for v in (-35, 35): S.circ(*Q(u, v), 3, 'white', RED, 1.2) if abs(u) > 45 or True else None
for i, t in enumerate(['Skarven mitt på en dubbelkloss (2 × 45).',
                       'Sidolaskar 12 mm plywood 400 × 150 på', 'båda sidor, lim + 4,5×40 i klossarna.',
                       'Inner- och ytterfläns skarvas vid olika', f'klossar (≈ {KLS[J_ut] - KLS[J_in]:.0f} isär). Skivlängd 2500.']):
    S.txt(jx + 20, jy + 420 + i * 26, t, 17)
# ---- 4 plan ----
px, py = 1240, 700
S.frame(px, py, 1120, 330, '4  PLAN: 13 BÅGAR c/c %.0f' % BCC, '1:60')
k4 = 0.058; x0, y0 = px + 60, py + 60
S.rect(x0, y0, Langd * k4, Bredd * k4, 'none', INK, 1.4)
for i in range(NB): S.line(x0 + i * BCC * k4, y0, x0 + i * BCC * k4, y0 + Bredd * k4, WOOD, 4)
S.txt(x0, y0 + Bredd * k4 + 30, f'10 000 lång, 4 000 bred · 11 hanbjälkar · nock- och sidoregel i bitar', 17)
# ---- 5 material ----
mx, my = 1240, 1050
S.rect(mx, my, 1120, 310, 'none', '#cfcac0', 1.5); S.txt(mx + 16, my + 34, '5  MATERIAL (13 bågar = 26 halvbågar)', 24, w='bold')
nstrips = 26 * 4
mat = [f'Plywood 15 × 2500 × 1200: {math.ceil(nstrips / 12)} skivor till flänsar ({nstrips} remsor 95, 12 per skiva) + 1 till laskar',
       f'Regel 45×95: {len(KLS) + 2} klossar à 120 per halvbåge → ≈ {26 * (len(KLS) + 2) * 0.125:.0f} m',
       f'Hanbjälke 45×120: 11 st à ≈ {2 * HanX / 1000:.1f} m · nockregelbitar 12 st à ≈ 0,7 m',
       f'Skruv 5×50 ≈ {26 * (len(KLS) + 2) * 4} st (2 per fläns och kloss) · 4,5×40 till laskar',
       'Jämfört med båge B: ingen limning i lager, ingen böjmall med kilar – men 4 bågar till.',
       'Flänsen kan böjas runt klossarna direkt på en enkel mall (snöre + några stopp).']
for i, t in enumerate(mat): S.txt(mx + 24, my + 76 + i * 36, '• ' + t, 18)
S.save('skiss_1x15_2d')

# ---------------- 3D: tre bågar + nockregel ----------------
az, el = math.radians(-35), math.radians(22)
def pr(p):
    x, y, z = p
    xr = x * math.cos(az) - y * math.sin(az); yr = x * math.sin(az) + y * math.cos(az)
    return xr, -(z * math.cos(el) - yr * math.sin(el)), yr * math.cos(el) + z * math.sin(el)
F = []
def prism(poly, y0, y1, fill, sw=0.5):
    A = [(x, y0, z) for x, z in poly]; Bq = [(x, y1, z) for x, z in poly]; n = len(poly)
    F.append((A, fill, sw)); F.append((Bq, fill, sw))
    for i in range(n):
        j = (i + 1) % n; F.append(([A[i], A[j], Bq[j], Bq[i]], fill, 0.25))
def box(x0, x1, y0, y1, z0, z1, fill): prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, fill)
for b in range(3):
    y = b * BCC
    for sd in (1, -1):
        m = lambda pts: [(sd * x, z + SyllH) for x, z in pts]
        te_i, te_o = th_end(ri + PT), th_end(ro)
        for t0 in [k * 0.06 for k in range(int(te_o / 0.06) + 1)]:
            prism(m(band(ro - PT, ro, t0, min(te_o, t0 + 0.06), 2)), y, y + BB, PLY)
            if t0 < te_i: prism(m(band(ri, ri + PT, t0, min(te_i, t0 + 0.06), 2)), y, y + BB, PLY)
        for s in KLS: prism(m(band(ri + PT, ro - PT, (s - KL / 2) / R, (s + KL / 2) / R, 2)), y, y + BB, WOOD)
    box(-HanX, HanX, y + BB, y + BB + 45, HanZ + SyllH - 60, HanZ + SyllH + 60, HAN)
for sd in (1, -1): box(sd * HB - 60, sd * HB + 60, -200, 2 * BCC + 300, 0, SyllH, '#9c8a6a')
box(-22, 22, BB, 2 * BCC, Nockhojd - 120, Nockhojd, HAN)
P2 = [[pr(p) for p in f[0]] for f in F]
order = sorted(range(len(F)), key=lambda i: sum(q[2] for q in P2[i]) / len(P2[i]))
xs = [q[0] for f in P2 for q in f]; ys = [q[1] for f in P2 for q in f]
W3, H3 = 2400, 1500; mg = 80
sc = min((W3 - 2 * mg) / (max(xs) - min(xs)), (H3 - 2 * mg - 120) / (max(ys) - min(ys)))
TX = lambda x: (W3 - (max(xs) - min(xs)) * sc) / 2 + (x - min(xs)) * sc; TY = lambda y: mg + 120 + (y - min(ys)) * sc
S3 = Svg(W3, H3)
S3.txt(40, 62, 'FÖRSLAG 1 × 15 – 3D (3 av 13 bågar, c/c %.0f)' % BCC, 38, w='bold')
S3.txt(40, 96, f'Flänsar 15 × 95 plywood, klossar regel 45×95 c/c ≤ {CC:.0f}, djup {D:.0f}, hanbjälke 2,4 m, nockregel mellan bågarna.', 20, col=GREY)
for i in order: S3.poly([(TX(q[0]), TY(q[1])) for q in P2[i]], F[i][1], INK, F[i][2])
S3.save('skiss_1x15_3d')
print('klossar/halvbåge', len(KLS), 'c/c', round(KLS[2] - KLS[1]), round(KLS[-2] - KLS[-3]), 'skarv', round(KLS[J_in]), round(KLS[J_ut]), 'HanX', round(HanX))
