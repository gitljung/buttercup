#!/usr/bin/env python3
"""Skiss: böjmall för halvbågen (båge B: flänsar 3×12, klossar 2×12, djup 96) av enkelt material.
Bord av 2 OSB 18 på reglar, formklossar av 45×95 längs innerradien, motklossar + kilpar för pressning.
Skriver skiss_mall_2d.svg/.png och skiss_mall_3d.svg/.png."""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'skiss_10klossar.py'), encoding='utf-8').read()
INK, GREY, RED, PLY, PLY2, STEEL, LIGHT = '#1d1d1b', '#8a8a86', '#c8321a', '#e8cf9c', '#d9b77a', '#b9bec4', '#efece5'
OSB = '#dcc79a'
exec('class Svg:' + src.split('class Svg:')[1].split('# ======================= 2D')[0])
# ---------------- geometri (mm), båge B ----------------
Bredd, Nockhojd, SyllH, NockT = 4000.0, 3500.0, 120.0, 45.0
HB = Bredd / 2; BH = Nockhojd - SyllH
cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
LT, NL = 12.0, 3; PT = LT * NL; KH = 2 * LT; D = 2 * PT + KH; BB = 95.0
ri, ro = R - D / 2, R + D / 2
tN = math.acos((NockT / 2 + cx) / ri)
c = 2 * ri * math.sin(tN / 2); a0 = math.sqrt(ri * ri - (c / 2) ** 2)      # korda + centrumavstånd
GAP = 25.0; RF = ri; RM = ro + GAP                                         # formkant / motklossarnas kant
NBLK = 15
# klossar längs mittlinjen (samma regel som modellen: KlossCCmax 450, fack för sidoregel 19×95 på z 1900)
KL, FKL, CCmax, SRH, SPEL = 120.0, 250.0, 450.0, 95.0, 2.5
BL = R * math.acos((NockT / 2 + cx) / R)
FackS = R * math.asin((1900 - SyllH) / R); Gap = SRH + 2 * SPEL
FotS = KL / 2; FNs = FackS - Gap / 2 - FKL / 2; FOs = FackS + Gap / 2 + FKL / 2; NockS = BL - KL / 2
nm = max(1, math.ceil((FNs - FKL / 2 - FotS - KL / 2) / CCmax) - 1); npch = (FNs - FotS - (FKL - KL) / 2) / (nm + 1)
om = max(1, math.ceil((NockS - KL / 2 - FOs - FKL / 2) / CCmax) - 1); opch = (NockS - FOs - (FKL - KL) / 2) / (om + 1)
KLS = [('fot', 0, KL)] + [('k', FotS + (k + 1) * npch - KL / 2, KL) for k in range(nm)] + [('fack', FNs - FKL / 2, FKL), ('fack', FOs - FKL / 2, FKL)]
o0 = FOs + (FKL - KL) / 2
KLS += [('k', o0 + (k + 1) * opch - KL / 2, KL) for k in range(om)] + [('nock', BL - KL, KL)]
# mallens koordinater: korda längs u (fot vid -c/2), höjd v uppåt; centrum (0, -a0); vinkel phi från v-axeln
def J(r, s_center):
    """punkt på radie r vid båglängd s längs mittlinjen från foten"""
    th = s_center / R                                    # vinkel från foten
    phi = -tN / 2 + th                                   # -tN/2 vid foten, +tN/2 vid nocken
    return (r * math.sin(phi), r * math.cos(phi) - a0)
def Jphi(r, phi): return (r * math.sin(phi), r * math.cos(phi) - a0)
def bandJ(s0, s1, r0, r1, n=None):
    n = n or max(2, int((s1 - s0) / 60))
    return [J(R + r1, s0 + (s1 - s0) * k / n) for k in range(n + 1)] + [J(R + r0, s1 - (s1 - s0) * k / n) for k in range(n + 1)]
# kaplinjer i mallens koordinater: foten = radiell (lodrätt i huset vid θ=0 -> vågrätt i huset = radiellt); nocken = lodrätt i huset
husrot = -tN / 2      # mallens phi = husets θ - tN/2 ; husets lodlinje i mallen: riktning (sin, cos) av ... 
# husets riktningar uttryckta i mallen: husets θ-axel (radiell vid θ) = mallens phi = θ - tN/2
def husvek(ang):     # husets enhetsvektor med vinkel ang från husets horisontal -> mallens (u, v)
    p = ang - tN / 2
    return (math.sin(p), math.cos(p))
nock_lod = husvek(math.pi / 2)
ang_nock = math.degrees(math.atan2(nock_lod[1], nock_lod[0]))
ang_fot = math.degrees(math.atan2(*reversed(husvek(0.0))))
TAB = [(u, math.sqrt(RF * RF - u * u) - a0) for u in range(0, int(c / 2) + 1, 250)] + [(c / 2, 0.0)]
blk_phi = [-tN / 2 + (tN) * k / (NBLK - 1) for k in range(NBLK)]

# ======================= 2D =======================
S = Svg(2400, 1750)
S.txt(40, 62, 'VÄXTHUS – BÖJMALL FÖR HALVBÅGEN (OSB + REGLAR + KILAR)', 40, w='bold')
S.txt(40, 96, f'Bara raka snitt och handverktyg. Mallen ger bågens innerradie R {ri:.0f}; samma mall till alla 18 halvbågar. Skiss – mått ur modellen.', 20, col=GREY)
fx, fy, fw, fh = 40, 120, 2320, 780
S.frame(fx, fy, fw, fh, '1  MALLEN UPPIFRÅN', 'ca 1:12')
s1 = 0.42; ox, oy = fx + fw / 2, fy + fh - 170
X = lambda u: ox + u * s1; Y = lambda v: oy - v * s1
T = lambda pts: [(X(u), Y(v)) for u, v in pts]
# bord 2 x OSB 2500x1200
for k in (-1, 0):
    S.rect(X(k * 2500), Y(950), 2500 * s1, 1200 * s1, OSB, INK, 1.4)
S.txt(X(-2500) + 10, Y(950) + 26, 'OSB 18 × 2500 × 1200', 17, col=GREY); S.txt(X(0) + 10, Y(950) + 26, 'OSB 18 × 2500 × 1200', 17, col=GREY)
for xx in range(-2500, 2501, 625): S.line(X(xx), Y(950), X(xx), Y(-250), '#b9a77d', 1, '6 6')
# korda + ordinater
S.line(X(-c / 2), Y(0), X(c / 2), Y(0), RED, 1.6, '10 6')
for u, v in TAB:
    for sg in ((1, -1) if u > 0 else (1,)):
        S.line(X(sg * u), Y(0), X(sg * u), Y(v), RED, 1.0)
# lamineringen (fläns + kloss + fläns) som tunt band
S.poly(T(bandJ(0, BL, -D / 2, -D / 2 + PT)), PLY, INK, 1.2)
S.poly(T(bandJ(0, BL, D / 2 - PT, D / 2)), PLY, INK, 1.2)
for t, s0, L in KLS:
    S.poly(T(bandJ(s0, s0 + L, -KH / 2, KH / 2, 2)), PLY2, INK, 1.0)
# formklossar (innanför RF) och motklossar (utanför RM) + kilpar
for ph in blk_phi:
    ux, uv = math.sin(ph), math.cos(ph); tx, tv = math.cos(ph), -math.sin(ph)
    def blk(r0, r1, w=45):
        p = [(r0 * ux - w / 2 * tx, r0 * uv - a0 - w / 2 * tv), (r1 * ux - w / 2 * tx, r1 * uv - a0 - w / 2 * tv),
             (r1 * ux + w / 2 * tx, r1 * uv - a0 + w / 2 * tv), (r0 * ux + w / 2 * tx, r0 * uv - a0 + w / 2 * tv)]
        return [(X(u), Y(v)) for u, v in p]
    S.poly(blk(RF - 45, RF, 200), '#c9a46b', INK, 1.1)
    S.poly(blk(RM, RM + 45, 200), '#c9a46b', INK, 1.1)
    S.poly(blk(ro + 2, RM - 2, 60), '#f3c9bf', RED, 1.0)
# kaplinjer
for (pu, pv), dv, lab in ((J(R, 0), husvek(0.0), 'kaplinje fot (vågrätt i huset)'), (J(R, BL), nock_lod, 'kaplinje nock (lodrätt i huset)')):
    S.line(X(pu - dv[0] * 130), Y(pv - dv[1] * 130), X(pu + dv[0] * 130), Y(pv + dv[1] * 130), RED, 2.4)
# etiketter
u, v = Jphi(RF - 22, blk_phi[4]); S.leader(X(u), Y(v), X(-2350), Y(-150), 'Formkloss 45×95×200 på högkant,\nkant på innerradien, 15 st', '1')
u, v = Jphi(RM + 22, blk_phi[9]); S.leader(X(u), Y(v), X(600), Y(900), 'Motkloss 45×95×200, 15 st\n(25 mm utanför bågens yttersida)', '2')
u, v = Jphi(ro + 12, blk_phi[11]); S.leader(X(u), Y(v), X(1250), Y(800), 'Kilpar (två kilar ur 45×95)\nslås in = presstryck', '3')
S.leader(X(-c / 2 + 300), Y(0), X(-300), Y(-170), f'Korda {c:.0f} (snöre / rak regel)\n+ ordinater, se tabell', '4')
pu, pv = J(R, BL); S.leader(X(pu), Y(pv), X(1900), Y(500), 'Nockänden kapas\nlodrätt i huset', '5')
pu, pv = J(R, 0); S.leader(X(pu), Y(pv), X(-2350), Y(820), 'Fotänden kapas\nvågrätt i huset (radiellt)', '5')
# --- 2 ordinattabell ---
tx0, ty0 = 40, 920
S.rect(tx0, ty0, 760, 420, 'none', '#cfcac0', 1.5); S.txt(tx0 + 16, ty0 + 32, '2  ORDINATER (rita innerradien)', 24, w='bold')
S.txt(tx0 + 16, ty0 + 64, f'Från kordans mitt, åt båda håll. Höjd över kordan till R {ri:.0f}.', 17, col=GREY)
for i, (u, v) in enumerate(TAB):
    S.txt(tx0 + 40, ty0 + 100 + i * 30, f'± {u:6.0f} mm', 19); S.txt(tx0 + 260, ty0 + 100 + i * 30, f'{v:6.1f} mm', 19, w='bold')
S.txt(tx0 + 420, ty0 + 100, f'Pilhöjd {TAB[0][1]:.0f} mm', 19)
S.txt(tx0 + 420, ty0 + 130, f'Centrum {a0:.0f} under kordan', 19)
S.txt(tx0 + 420, ty0 + 160, f'(alt. stråkpassare R {ri:.0f}:', 19); S.txt(tx0 + 420, ty0 + 190, ' läkt + spik i golvet)', 19)
# --- 3 sektion: pressning ---
sx, sy = 820, 920
S.rect(sx, sy, 760, 420, 'none', '#cfcac0', 1.5); S.txt(sx + 16, sy + 32, '3  PRESSNING (snitt, 1:4)', 24, w='bold')
k3 = 1.35
for col_i, (titel, lag) in enumerate((('Steg A: innerfläns', 'A'), ('Steg B: klossar + ytterfläns', 'B'))):
    bx = sx + 40 + col_i * 370; by = sy + 330
    S.txt(bx, sy + 66, titel, 18, w='bold')
    S.rect(bx, by, 300, 18 * k3 / 1.35 * 1.0, OSB, INK, 1)                       # OSB
    x = bx + 10
    S.rect(x, by - 95 * k3 / 1.35 * 0.7, 45 * k3 * 0.8, 95 * k3 * 0.7 / 1.35, '#c9a46b', INK, 1); S.txt(x + 4, by - 72, '1', 16, w='bold', col=RED)
    x += 45 * k3 * 0.8
    lay = [PT] if lag == 'A' else [PT, KH, PT]
    cols = [PLY] if lag == 'A' else [PLY, PLY2, PLY]
    if lag == 'A': lay.append(45); cols.append('#e5d3b0')
    for t, cl in zip(lay, cols):
        S.rect(x, by - 70, t * k3, 70, cl, INK, 1); x += t * k3
    S.poly([(x, by - 70), (x + 26, by - 70), (x + 14, by)], '#f3c9bf', RED, 1.2)
    S.poly([(x + 28, by - 70), (x + 40, by), (x + 14, by)], '#f3c9bf', RED, 1.2)
    x += 44
    S.rect(x, by - 66, 45 * k3 * 0.8, 66, '#c9a46b', INK, 1); S.txt(x + 4, by - 72, '2', 16, w='bold', col=RED)
    S.txt(bx, by + 40, '3 lager 12 + tryckbit 45' if lag == 'A' else '12×3 + kloss 24 + 12×3', 16, col=GREY)
S.txt(sx + 16, sy + 398, 'Plastfolie/packtejp på klossarna så att limmet inte fastnar.', 16, col=GREY)
# --- 4 material + arbetsgång ---
mx, my = 1600, 920
S.rect(mx, my, 760, 420, 'none', '#cfcac0', 1.5); S.txt(mx + 16, my + 32, '4  MATERIAL TILL MALLEN', 24, w='bold')
mat = ['2 st OSB 18 × 2500 × 1200 (skivan som bord)',
       'Reglar 45×95: 3 × 5,1 m (längsgående) + 9 × 1,2 m (tvärs c/c 625)',
       '30 st klossar 45×95×200 (≈ 6 m regel) – form + mot',
       '30 kilpar ur 45×95 (≈ 4 m regel, sågas diagonalt)',
       '3 st tryckbitar 45×95 × 1,4 m (steg A)',
       'Skruv 5×80 (klossar, 3 per kloss) + 4,2×40 (OSB)',
       'Snöre, tumstock, vinkelhake, packtejp/plastfolie',
       '2 bockar eller plant golv']
for i, r in enumerate(mat): S.txt(mx + 20, my + 74 + i * 40, '• ' + r, 18)
# arbetsgång
S.rect(40, 1360, 2320, 370, 'none', '#cfcac0', 1.5); S.txt(60, 1396, 'ARBETSGÅNG', 24, w='bold')
steps = [f'Bygg bordet: reglar på bockar/golv, OSB skruvad ovanpå. Spänn snöre = korda {c:.0f} mm, mät ut ordinaterna, dra kurvan med en böjd läkt.',
         f'Skruva formklossarna (1) med kanten på kurvan, 15 st jämnt fördelade. Motklossarna (2) radiellt utanför, {GAP + ro - ri:.0f} mm från formkanten.',
         'Steg A: lim (PU) på lager 1–3 (12 × 95, skarvarna förskjutna ≥ 600), lägg mot formklossarna, tryckbit utanför, slå in kilarna. Härdar 2–4 h.',
         'Märk klossarna på innerflänsen (tabell i modellen), limma + skruva klossarna 2 × 12. Steg B: ytterflänsens 3 lager över klossarna, kila mot motklossarna.',
         'Efter härdning: kapa fot- och nockänden längs kaplinjerna (5), borra för fotvinklar och nocklask. Märk halvbågen (H1–H18).',
         'Tips: lägg innerfläns till nästa halvbåge medan föregående härdar på ytterflänsen – två set kilar gör det smidigt.']
for i, r in enumerate(steps): S.bubble(76, 1440 + i * 50, str(i + 1), INK); S.txt(106, 1447 + i * 50, r, 19)
S.save('skiss_mall_2d')

# ======================= 3D =======================
az, el = math.radians(-30), math.radians(38)
def proj(p):
    x, y, z = p
    xr = x * math.cos(az) - y * math.sin(az); yr = x * math.sin(az) + y * math.cos(az)
    return xr, -(z * math.cos(el) - yr * math.sin(el)), yr * math.cos(el) + z * math.sin(el)
faces = []; bg = []
def prism(poly2, z0, z1, fill, col=INK, sw=0.8):     # polygon i (u, v) = (x, y) extruderad i z
    n = len(poly2)
    A = [(u, v, z0) for u, v in poly2]; B = [(u, v, z1) for u, v in poly2]
    faces.append((A, fill, col, sw)); faces.append((B, fill, col, sw))
    for i in range(n):
        j = (i + 1) % n; faces.append(([A[i], A[j], B[j], B[i]], fill, col, 0.4))
def box(x0, x1, y0, y1, z0, z1, fill, col=INK): prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, fill, col)
H0 = 0.0
for k in (-1, 0): box(k * 2500, k * 2500 + 2500, -250, 950, -18, 0, OSB)
bg = faces; faces = []
def blkpoly(ph, r0, r1, w):
    ux, uv = math.sin(ph), math.cos(ph); tx, tv = math.cos(ph), -math.sin(ph)
    return [(r0 * ux - w / 2 * tx, r0 * uv - a0 - w / 2 * tv), (r1 * ux - w / 2 * tx, r1 * uv - a0 - w / 2 * tv),
            (r1 * ux + w / 2 * tx, r1 * uv - a0 + w / 2 * tv), (r0 * ux + w / 2 * tx, r0 * uv - a0 + w / 2 * tv)]
for ph in blk_phi:
    prism(blkpoly(ph, RF - 45, RF, 200), 0, 95, '#c9a46b')
    prism(blkpoly(ph, RM, RM + 45, 200), 0, 95, '#c9a46b')
    prism(blkpoly(ph, ro + 2, RM - 2, 50), 10, 85, '#f3c9bf', RED)
for s0 in range(0, int(BL), 200):
    s1_ = min(BL, s0 + 200)
    prism(bandJ(s0, s1_, -D / 2, -D / 2 + PT, 3), 0, BB, PLY)
    prism(bandJ(s0, s1_, D / 2 - PT, D / 2, 3), 0, BB, PLY)
for t, s0, L in KLS: prism(bandJ(s0, s0 + L, -KH / 2, KH / 2, 2), 2, BB - 2, PLY2)
pr = [[proj(p) for p in f[0]] for f in faces]
order = sorted(range(len(faces)), key=lambda i: sum(q[2] for q in pr[i]) / len(pr[i]))
prb = [[proj(p) for p in f[0]] for f in bg]
xs = [q[0] for f in pr + prb for q in f]; ys = [q[1] for f in pr + prb for q in f]
W3, H3 = 2400, 1400; m = 80
sc = min((W3 - 2 * m) / (max(xs) - min(xs)), (H3 - 2 * m - 120) / (max(ys) - min(ys)))
offx = (W3 - (max(xs) - min(xs)) * sc) / 2
TX = lambda x: offx + (x - min(xs)) * sc; TY = lambda y: m + 120 + (y - min(ys)) * sc
S3 = Svg(W3, H3)
S3.txt(40, 62, 'BÖJMALL – 3D (halvbåge i mallen, steg B)', 40, w='bold')
S3.txt(40, 96, 'OSB-bord på reglar, formklossar längs innerradien, motklossar + röda kilpar som pressar flänsarna. Båge: 3×12 + kloss 2×12 + 3×12.', 20, col=GREY)
for f in bg:
    if f[0][0][2] == 0 and all(q[2] == 0 for q in f[0]): S3.poly([(TX(proj(q)[0]), TY(proj(q)[1])) for q in f[0]], f[1], f[2], f[3])
for i in order:
    pts, fill, col, sw = faces[i]
    S3.poly([(TX(q[0]), TY(q[1])) for q in pr[i]], fill, col, sw)
S3.save('skiss_mall_3d')
print('korda', round(c), 'pil', round(TAB[0][1]), 'a0', round(a0), 'klossar', len(KLS), 'nockkap mot korda', round(ang_nock, 1), 'fot', round(ang_fot, 1))
