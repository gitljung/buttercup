#!/usr/bin/env python3
"""Skiss: mall för HEL båge (båda halvorna + nocklaskar + nockklots i ett limpass, hanbjälke bultas i mallen).
Båge B: flänsar 3×12, klossar 2×12, djup 96. Skriver skiss_mall_hel_2d/3d .svg/.png."""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
INK, GREY, RED, PLY, PLY2, STEEL, LIGHT = '#1d1d1b', '#8a8a86', '#c8321a', '#e8cf9c', '#d9b77a', '#b9bec4', '#efece5'
OSB, WOOD, WEDGE, HAN = '#dcc79a', '#c9a46b', '#f3c9bf', '#b98a4e'
src = open(os.path.join(HERE, 'skiss_10klossar.py'), encoding='utf-8').read()
exec('class Svg:' + src.split('class Svg:')[1].split('# ======================= 2D')[0])
def _cb(s, x, y, w, h):
    s.a(f'<clipPath id="c{len(s.o)}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#c{len(s.o)})">')
Svg.clip_begin = _cb
Svg.clip_end = lambda s: s.a('</g>')
# ---------- geometri (mm, husets x/z = mallens x/y) ----------
Bredd, Nockhojd, SyllH, NockT = 4000.0, 3500.0, 120.0, 45.0
HB = Bredd / 2; BH = Nockhojd - SyllH
cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
LT = 12.0; PT = 3 * LT; KH = 2 * LT; D = 2 * PT + KH; BB = 95.0
ri, ro = R - D / 2, R + D / 2
GAP = 25.0; RM = ro + GAP
LASK_L, LASK_AV = 600.0, 35.0
HanZ, HanH, HanT = 2400.0, 120.0, 45.0
def th_end(r): return math.acos((NockT / 2 + cx) / r)
def P(r, th, sd=1): return (sd * (-cx + r * math.cos(th)), SyllH + r * math.sin(th))
def band(r0, r1, t0, t1, sd=1, n=None):
    n = n or max(2, int(abs(t1 - t0) * R / 60))
    return [P(r1, t0 + (t1 - t0) * k / n, sd) for k in range(n + 1)] + [P(r0, t1 - (t1 - t0) * k / n, sd) for k in range(n + 1)]
# klossar (samma regel som modellen)
KL, FKL, CCmax, SRH, SPEL = 120.0, 250.0, 450.0, 95.0, 2.5
BL = R * th_end(R)
FackS = R * math.asin((1900 - SyllH) / R); Gp = SRH + 2 * SPEL
FotS = KL / 2; FNs = FackS - Gp / 2 - FKL / 2; FOs = FackS + Gp / 2 + FKL / 2; NockS = BL - KL / 2
nm = max(1, math.ceil((FNs - FKL / 2 - FotS - KL / 2) / CCmax) - 1); npch = (FNs - FotS - (FKL - KL) / 2) / (nm + 1)
om = max(1, math.ceil((NockS - KL / 2 - FOs - FKL / 2) / CCmax) - 1); opch = (NockS - FOs - (FKL - KL) / 2) / (om + 1)
KLS = [(0, KL)] + [(FotS + (k + 1) * npch - KL / 2, KL) for k in range(nm)] + [(FNs - FKL / 2, FKL), (FOs - FKL / 2, FKL)]
o0 = FOs + (FKL - KL) / 2
KLS += [(o0 + (k + 1) * opch - KL / 2, KL) for k in range(om)] + [(BL - KL, KL)]
# lamellskarvar (skiva 2500): skarv i lager k vid s = SK[k] från foten, längs respektive radie
SK = [1650.0, 2050.0, 2450.0]
# hanbjälke: ändar i bågens ytterkant vid överkanten
HanX = -cx + math.sqrt(ro * ro - (HanZ + HanH / 2 - SyllH) ** 2)
# nocklask: |x| < LASK_L/2 mellan ri och ro - LASK_AV
def lask_pts():
    rr = ro - LASK_AV
    a_o, a_i = math.acos((LASK_L / 2 + cx) / rr), math.acos((LASK_L / 2 + cx) / ri)
    m_o, m_i = math.acos(cx / rr), math.acos(cx / ri)                       # x = 0 på respektive radie
    ro_r = [P(rr, a_o + (m_o - a_o) * k / 12) for k in range(13)]           # höger ytterkant, fot→nock
    ri_r = [P(ri, a_i + (m_i - a_i) * k / 12) for k in range(13)]
    outer = ro_r + [(-x, z) for x, z in reversed(ro_r)][1:]                 # höger -> vänster längs ytterkant
    inner = ri_r + [(-x, z) for x, z in reversed(ri_r)][1:]
    return outer + list(reversed(inner))
LASK = lask_pts()
nphi = 13
blk_t = [th_end(ri) * k / (nphi - 1) for k in range(nphi)]
def blk(r0, r1, th, w, sd=1):
    ux, uz = math.cos(th), math.sin(th); tx, tz = -math.sin(th), math.cos(th)
    c0 = (-cx, SyllH)
    pts = [(c0[0] + r * ux + h * tx, c0[1] + r * uz + h * tz) for r, h in ((r0, -w / 2), (r1, -w / 2), (r1, w / 2), (r0, w / 2))]
    return [(sd * x, z) for x, z in pts]

def scene(S, X, Y, lw=1.0, detalj=False):
    T = lambda pts: [(X(x), Y(z)) for x, z in pts]
    for sd in (1, -1):
        # underlägg 12 (spillremsor) under bågen utom vid lasken
        # form/mot-klossar + kilar
        for k, th in enumerate(blk_t):
            if th * R > BL - 250: continue
            S.poly(T(blk(ri - 45, ri, th, 200, sd)), WOOD, INK, lw)
            S.poly(T(blk(RM, RM + 45, th, 200, sd)), WOOD, INK, lw)
            S.poly(T(blk(ro + 2, RM - 2, th, 60, sd)), WEDGE, RED, lw)
        # flänsar (3 lager vardera) med skarvar
        for base, sgn in ((ri, 1), (ro, -1)):
            for k in range(3):
                r0 = base + sgn * k * LT; r1 = r0 + sgn * LT; a, b = min(r0, r1), max(r0, r1)
                te = th_end(a); tj = SK[k] / ((a + b) / 2)
                S.poly(T(band(a, b, 0, tj, sd)), PLY, INK, lw * 0.6)
                S.poly(T(band(a, b, tj, te, sd)), PLY, INK, lw * 0.6)
        for s0, L in KLS:
            S.poly(T(band(ri + PT, ro - PT, s0 / R, (s0 + L) / R, sd, 2)), PLY2, INK, lw * 0.8)
        # fotlinje + fotklossar (stopp utanför ytterflänsen)
        fx = -cx + ro
        S.line(X(sd * (-cx + ri - 150)), Y(SyllH), X(sd * (fx + 150)), Y(SyllH), RED, 2.2, '12 6')
    # V-motkloss i nocken och nockklots
    zt = SyllH + math.sqrt(RM ** 2 - cx ** 2)
    S.poly(T([(-260, zt - 140), (0, zt), (260, zt - 140), (260, zt + 45 - 140 + 20), (0, zt + 50), (-260, zt + 45 - 140 + 20)]), WOOD, INK, lw)
    zi, zo = SyllH + math.sqrt(ri ** 2 - (cx + NockT / 2) ** 2), SyllH + math.sqrt(ro ** 2 - (cx + NockT / 2) ** 2)
    S.poly(T([(-NockT / 2, zi), (NockT / 2, zi), (NockT / 2, zo), (-NockT / 2, zo)]), HAN, INK, lw)
    # nocklask (ovanpå), streckad kontur
    S.poly(T(LASK), 'none', RED, 2.0 if not detalj else 2.6)
    # hanbjälke (ovanpå, bultas efter härdning)
    S.poly(T([(-HanX, HanZ - HanH / 2), (HanX, HanZ - HanH / 2), (HanX, HanZ + HanH / 2), (-HanX, HanZ + HanH / 2)]), HAN, INK, lw * 1.2)
    for sd in (1, -1):
        for dx in (60, 170):
            S.circ(X(sd * (HanX - dx)), Y(HanZ), 4 if not detalj else 7, STEEL, INK) if hasattr(S, 'circ') else S.rect(X(sd * (HanX - dx)) - 3, Y(HanZ) - 3, 6, 6, STEEL, INK, 0.8)

# ======================= 2D =======================
S = Svg(2400, 1900)
S.txt(40, 62, 'VÄXTHUS – MALL FÖR HEL BÅGE (båda halvorna + nocklaskar i ett limpass)', 38, w='bold')
S.txt(40, 96, 'Bara raka snitt, handverktyg. Bågen ligger plant; kilar pressar flänsarna mot formklossarna. Hanbjälken bultas medan bågen ligger kvar. Skiss.', 20, col=GREY)
fx, fy, fw, fh = 40, 120, 1500, 1060
S.frame(fx, fy, fw, fh, '1  MALLEN UPPIFRÅN MED BÅGEN', 'ca 1:16')
s1 = 0.255; ox, oy = fx + fw / 2, fy + fh - 60
X = lambda x: ox + x * s1; Y = lambda z: oy - z * s1
for i in range(3):
    for j in (-1, 0):
        S.rect(X(j * 2500), Y((i + 1) * 1200), 2500 * s1, 1200 * s1, OSB, '#a89468', 1.0)
S.txt(X(-2500) + 8, Y(3600) + 20, '6 st OSB 18 × 2500 × 1200 (eller plant betonggolv)', 15, col=GREY)
scene(S, X, Y, 0.8)
lab = [((-cx + ri - 22) , 900, -2450, 1900, 'Formkloss 45×95×200,\nkant på innerradien R %.0f' % ri, '1'),
       (None, None, 1800, 3300, 'Motkloss 45×95×200\n%d mm utanför bågen' % GAP, '2'),
       (None, None, 2000, 2700, 'Kilpar (2 kilar ur 45×95)', '3'),
       (0, 3380, -2450, 3450, 'Nocklask 12 (båda sidor)\n+ nockklots 45 i glipan', '4'),
       (-HanX + 300, HanZ, -2450, 2650, 'Hanbjälke 45×120 på z %.0f\nbultas M10 i mallen' % HanZ, '5'),
       (-cx + ro + 100, SyllH, -2450, 500, 'Fotlinje (kritstreck):\nkapas här efter härdning', '6')]
pt2 = blk(RM, RM + 45, blk_t[6], 200, 1); pt3 = blk(ro + 2, RM - 2, blk_t[8], 60, 1)
lab[0] = (*blk(ri - 45, ri, blk_t[4], 200, -1)[0], *lab[0][2:])
lab[1] = (pt2[1][0], pt2[1][1], *lab[1][2:]); lab[2] = (pt3[1][0], pt3[1][1], *lab[2][2:])
for x0, z0, x1, z1, t, n in lab:
    S.leader(X(x0), Y(z0), X(x1), Y(z1), t, n)
S.txt(X(-2000), Y(-60) + 26, '◄ ────────  spännvidd %.0f (ytterkant fot)  ──────── ►' % (2 * (-cx + ro)), 16, col=GREY)
# ---- 2 detalj nock ----
dx0, dy0, dw, dh = 1560, 120, 800, 620
S.frame(dx0, dy0, dw, dh, '2  NOCKEN I MALLEN', 'ca 1:5')
s2 = 1.05; ox2, oy2 = dx0 + dw / 2, dy0 + 330
X2 = lambda x: ox2 + x * s2; Y2 = lambda z: oy2 - (z - 3300) * s2
S.clip_begin(dx0 + 4, dy0 + 40, dw - 8, dh - 46) if hasattr(S, 'clip_begin') else None
scene(S, X2, Y2, 1.2, detalj=True)
S.clip_end() if hasattr(S, 'clip_end') else None
S.rect(dx0 + 2, dy0 + dh - 150, dw - 4, 148, '#ffffff', 'none', 0)
for i, t in enumerate(['Lamellerna slutar vid nockklotsen (nocken är en spets, %.0f° knäck –' % (2 * math.degrees(math.atan(cx / BH))),
                       'plywood kan inte böjas över den). Klotsen 45×95 limmas i glipan,',
                       'laskarna (12 mm, ca 600 lång) limmas + skruvas på båda sidor.',
                       'Undre lasken läggs först på bordet; resten av bågen ligger på',
                       'underlägg 12 mm (spillremsor) så att allt ligger plant.']):
    S.txt(dx0 + 16, dy0 + dh - 122 + i * 26, t, 17)
# ---- 3 snitt ----
sx, sy, sw_, sh = 1560, 760, 800, 420
S.frame(sx, sy, sw_, sh, '3  SNITT GENOM MALLEN', 'ca 1:4')
k3 = 1.6
def snitt(bx, by, titel, nock):
    S.txt(bx, by - 230, titel, 17, w='bold')
    S.rect(bx - 10, by, 330, 18 * k3 * 0.6, OSB, INK, 1)
    S.rect(bx + 4, by - 12 * k3, 300, 12 * k3, PLY if nock else '#e5dcc8', INK, 1)        # underlägg / undre lask
    S.rect(bx + 4, by - 12 * k3 - 95 * k3, 45 * k3 * 0.5, 95 * k3, WOOD, INK, 1)
    x = bx + 4 + 45 * k3 * 0.5
    for t, c in ((PT, PLY), (KH, PLY2), (PT, PLY)) if not nock else ((PT, PLY), (NockT, HAN), (PT, PLY)):
        S.rect(x, by - 12 * k3 - 95 * k3, t * k3 * 0.9, 95 * k3, c, INK, 1); x += t * k3 * 0.9
    S.poly([(x + 2, by - 12 * k3 - 95 * k3), (x + 22, by - 12 * k3 - 95 * k3), (x + 12, by - 12 * k3)], WEDGE, RED, 1)
    S.rect(x + 26, by - 12 * k3 - 95 * k3, 45 * k3 * 0.5, 95 * k3, WOOD, INK, 1)
    if nock: S.rect(bx + 4 + 45 * k3 * 0.5, by - 24 * k3 - 95 * k3, (2 * PT + NockT) * k3 * 0.9, 12 * k3, PLY, RED, 1.6)
    S.txt(bx, by + 40, 'underlägg 12 · fläns 36 · kloss 24 · fläns 36' if not nock else 'undre lask · fläns · klots 45 · fläns · övre lask', 14, col=GREY)
snitt(sx + 30, sy + 330, 'A  längs bågen', False); snitt(sx + 420, sy + 330, 'B  vid nocken', True)
# ---- 4 material + arbetsgång ----
S.rect(40, 1200, 2320, 680, 'none', '#cfcac0', 1.5)
S.txt(60, 1238, '4  MATERIAL TILL EN MALL', 24, w='bold')
mat = ['6 OSB 18 × 2500 × 1200 (bord ca 5,0 × 3,6 m) – eller direkt på plant betonggolv',
       '7 reglar 45×95 × 5,1 m under OSB:n (c/c 600) – behövs inte på betonggolv',
       '%d formklossar + %d motklossar 45×95×200 + V-kloss i nocken (≈ 11 m regel)' % (2 * sum(1 for t in blk_t if t * R <= BL - 250), 2 * sum(1 for t in blk_t if t * R <= BL - 250)),
       '%d kilpar ur 45×95 (≈ 5 m regel), sågas diagonalt' % (2 * sum(1 for t in blk_t if t * R <= BL - 250)),
       'Underlägg: spillremsor 12 × 95 längs bågen (≈ 8 m)',
       'Skruv 5×80 (3 per kloss), packtejp/plastfolie på allt som rör limmet']
for i, r in enumerate(mat): S.txt(80, 1280 + i * 34, '• ' + r, 18)
S.txt(1240, 1238, 'ARBETSGÅNG (4 personer, ett limpass ≈ 40 min)', 24, w='bold')
steps = ['Rita fotlinjen och båda kurvorna (snöre + ordinater som förra skissen, spegla).',
         'Skruva form-, mot- och V-klossar, tejpa. Lägg underlägg och undre nocklask.',
         'Torrpassa en gång: lameller, klossar, nockklots, övre lask.',
         'Limpass: innerfläns 3 lager → klossar → ytterfläns 3 lager, båda halvorna',
         '  (en grupp per halva), klots + övre lask, slå in alla kilar.',
         'Härdar 4–5 h (≥ 15 °C). Skruva laskarna och klossarna 5×90.',
         'Lägg hanbjälken, borra Ø10 och bulta (4 st per ände ×2).',
         'Kapa båda fötterna längs fotlinjen, märk bågen, lyft ut (3–4 pers, ≈ 45 kg).']
for i, r in enumerate(steps): S.txt(1260, 1280 + i * 34, r, 18)
S.txt(60, 1520, 'BÅGEN (som ritad)', 24, w='bold')
bag = ['Flänsar 3 × 12 × 95 per sida, skarvar vid s ≈ %s mm från foten (lager 1–3).' % ' / '.join('%.0f' % s for s in SK),
       '  Skivlängden 2500 räcker inte till 600 mm förskjutning med 3 lager – 400 mm är max utan extra skarvar.',
       '11 klossar 2 × 12 per halva (c/c ≤ 450), två fackklossar runt sidoregeln 19 × 95.',
       'Nockklots 45 × 95 × 96 + nocklask 12 mm × ca 600 på båda sidor (gavelbågar: bara insidan).',
       'Hanbjälke 45 × 120 × %.0f på z %.0f, 2 × M10 per ände (gavelbågar: ingen).' % (2 * HanX, HanZ),
       'Vikt med hanbjälke ≈ 45 kg. Stapling: 2 bågar i höjd går om form-/motklossarna är 2 × 95 höga',
       '  och den övre bågen ligger på en 12 mm skiva ovanpå den undre (laskarna kommer emellan).']
for i, r in enumerate(bag): S.txt(80, 1560 + i * 34, r, 18)
S.save('skiss_mall_hel_2d')

# ======================= 3D =======================
az, el = math.radians(152), math.radians(40)
def proj(p):
    x, y, z = p
    xr = x * math.cos(az) - y * math.sin(az); yr = x * math.sin(az) + y * math.cos(az)
    return xr, -(z * math.cos(el) - yr * math.sin(el)), yr * math.cos(el) + z * math.sin(el)
faces = []
def prism(poly2, z0, z1, fill, col=INK, sw=0.6):
    n = len(poly2); A = [(u, v, z0) for u, v in poly2]; B = [(u, v, z1) for u, v in poly2]
    faces.append((A, fill, col, sw)); faces.append((B, fill, col, sw))
    for i in range(n):
        j = (i + 1) % n; faces.append(([A[i], A[j], B[j], B[i]], fill, col, 0.3))
bg = []
for i in range(3):
    for j in (-1, 0):
        x0, y0 = j * 2500, i * 1200
        bg.append(([(x0, y0, 0), (x0 + 2500, y0, 0), (x0 + 2500, y0 + 1200, 0), (x0, y0 + 1200, 0)], OSB, '#a89468', 0.8))
U = 12.0
for sd in (1, -1):
    for th in blk_t:
        if th * R > BL - 250: continue
        prism(blk(ri - 45, ri, th, 200, sd), 0, 2 * 95, WOOD)
        prism(blk(RM, RM + 45, th, 200, sd), 0, 2 * 95, WOOD)
        prism(blk(ro + 2, RM - 2, th, 60, sd), U + 10, U + 85, WEDGE, RED)
    te = th_end(R)
    for k in range(int(te * R / 250) + 1):
        t0, t1 = k * 250 / R, min(te, (k + 1) * 250 / R)
        if t1 <= t0: continue
        prism(band(ri, ri + PT, t0, t1, sd, 3), U, U + BB, PLY)
        prism(band(ro - PT, ro, t0, t1, sd, 3), U, U + BB, PLY)
    for s0, L in KLS: prism(band(ri + PT, ro - PT, s0 / R, (s0 + L) / R, sd, 2), U + 2, U + BB - 2, PLY2)
prism(LASK, U + BB, U + BB + 12, PLY, RED, 1.0)
prism([(-HanX, HanZ - HanH / 2), (HanX, HanZ - HanH / 2), (HanX, HanZ + HanH / 2), (-HanX, HanZ + HanH / 2)], U + BB, U + BB + HanT, HAN)
pr = [[proj(p) for p in f[0]] for f in faces]; prb = [[proj(p) for p in f[0]] for f in bg]
order = sorted(range(len(faces)), key=lambda i: sum(q[2] for q in pr[i]) / len(pr[i]))
xs = [q[0] for f in pr + prb for q in f]; ys = [q[1] for f in pr + prb for q in f]
W3, H3 = 2400, 1500; m = 70
sc = min((W3 - 2 * m) / (max(xs) - min(xs)), (H3 - 2 * m - 120) / (max(ys) - min(ys)))
offx = (W3 - (max(xs) - min(xs)) * sc) / 2
TX = lambda x: offx + (x - min(xs)) * sc; TY = lambda y: m + 120 + (y - min(ys)) * sc
S3 = Svg(W3, H3)
S3.txt(40, 62, 'MALL FÖR HEL BÅGE – 3D (bågen i mallen, hanbjälken på plats)', 38, w='bold')
S3.txt(40, 96, 'OSB-bord 5,0 × 3,6 m, form-/motklossar 2 × 95 höga (2 bågar kan staplas), röda kilar, nocklask och hanbjälke ovanpå.', 20, col=GREY)
for f, p in zip(bg, prb): S3.poly([(TX(q[0]), TY(q[1])) for q in p], f[1], f[2], f[3])
for i in order:
    pts, fill, col, sw = faces[i]
    S3.poly([(TX(q[0]), TY(q[1])) for q in pr[i]], fill, col, sw)
S3.save('skiss_mall_hel_3d')
print('R', round(R), 'ri', round(ri), 'ro', round(ro), 'HanX', round(HanX), 'knack', round(2 * math.degrees(math.atan(cx / BH)), 1), 'BL', round(BL))
