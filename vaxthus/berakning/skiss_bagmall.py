#!/usr/bin/env python3
"""Skiss: bågmall för halvbågen (1×12 fläns, klossar 45×95, ur v13_param.json) av enkelt material.
Bord av 2 OSB 18 på reglar, formklossar av 45×95 längs innerradien, motklossar + kilpar för pressning.
Skriver skiss_mall_2d.svg/.png och skiss_mall_3d.svg/.png."""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'skiss_10klossar.py'), encoding='utf-8').read()
INK, GREY, RED, PLY, PLY2, STEEL, LIGHT = '#1d1d1b', '#8a8a86', '#c8321a', '#e8cf9c', '#d9b77a', '#b9bec4', '#efece5'
OSB = '#dcc79a'
exec('class Svg:' + src.split('class Svg:')[1].split('# ======================= 2D')[0])
# ---------------- geometri (mm) ur modellen (v13_param.json) ----------------
import json
P = json.load(open(os.path.join(HERE, '..', 'fusion', 'v13_param.json'), encoding='utf-8'))
Bredd, Nockhojd, SyllH, NockT = P['Bredd'], P['Nockhojd'], P['SyllH'], P['NockT']
HB = Bredd / 2; BH = Nockhojd - SyllH
cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
PT, KH, BB = P['PlyT'], P['KlossH'], P['BagB']; D = 2 * PT + KH
ri, ro = R - D / 2, R + D / 2
tN = math.acos((NockT / 2 + cx) / ri)
c = 2 * ri * math.sin(tN / 2); a0 = math.sqrt(ri * ri - (c / 2) ** 2)      # korda + centrumavstånd
GAP = 45.0; RF = ri; RM = ro + GAP                                         # formkant / motklossarnas kant (kilpar emellan)
KL, FKL, FOTL, BL = P['KlossL'], P['FackKlossL'], P['FotKlossL'], P['BagLangd']
NM, OM, NP, OP = int(P['NedreMellan']), int(P['OvreMellan']), P['NedrePitch'], P['OvrePitch']
FN, FO = P['FackNedreS'], P['FackOvreS']
K_ = [(0.0, FOTL, 'fot')] + [(P['FotKlossS'] + k * NP - KL / 2, KL, 'kloss') for k in range(1, NM + 1)]
K_ += [(FN - FKL / 2, FKL, 'fack'), (FO - FKL / 2, FKL, 'fack')]
o0 = FO + (FKL - KL) / 2
K_ += [(o0 + k * OP - KL / 2, KL, 'kloss') for k in range(1, OM + 1)] + [(BL - KL, KL, 'nock')]
KLS = [(t, s0, L) for s0, L, t in K_]
KC = [s0 + L / 2 for t, s0, L in KLS]                          # klossmitt längs mittlinjen
FC = [10 + 50 / 2] + [(KLS[i][1] + KLS[i][2] + KLS[i + 1][1]) / 2 for i in range(len(KLS) - 1)] + [BL - 35]   # formklossar i facken
NKL, NFK = len(KLS), len(FC)
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
PH = lambda s_: -tN / 2 + s_ / R
blk_phi = [PH(s_) for s_ in KC]          # motklossar + kilar vid varje båg-kloss
form_phi = [PH(s_) for s_ in FC]         # formklossar mitt i facken (innerflänsen åtkomlig vid klossarna)

# ======================= 2D =======================
S = Svg(2400, 1750)
S.txt(40, 62, 'VÄXTHUS – BÅGMALL FÖR HALVBÅGEN (OSB + REGLAR + KILAR)', 40, w='bold')
S.txt(40, 96, f'Bara raka snitt och handverktyg. Mallen ger innerradien R {ri:.0f}; fläns 1×{PT:.0f}×{BB:.0f}, klossar 45×95, djup {D:.0f}. Samma mall till alla 18 halvbågar. Skiss – mått ur modellen.', 20, col=GREY)
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
    S.poly(blk(RM, RM + 45, 200), '#c9a46b', INK, 1.1)
    S.poly(blk(ro + 2, RM - 2, 60), '#f3c9bf', RED, 1.0)
for ph in form_phi:
    ux, uv = math.sin(ph), math.cos(ph); tx, tv = math.cos(ph), -math.sin(ph)
    p = [(r_ * ux + w_ * tx, r_ * uv - a0 + w_ * tv) for r_, w_ in ((RF - 200, -22.5), (RF, -22.5), (RF, 22.5), (RF - 200, 22.5))]
    S.poly([(X(u), Y(v)) for u, v in p], '#c9a46b', INK, 1.1)
for i, s_ in enumerate(KC):
    u, v = J(ro - R + 150, s_) if False else Jphi(RM + 120, PH(s_)); S.txt(X(u), Y(v) + 6, str(i + 1), 14, 'middle', 'bold', INK)
# kaplinjer
for (pu, pv), dv, lab in ((J(R, 0), husvek(0.0), 'kaplinje fot (vågrätt i huset)'), (J(R, BL), nock_lod, 'kaplinje nock (lodrätt i huset)')):
    S.line(X(pu - dv[0] * 130), Y(pv - dv[1] * 130), X(pu + dv[0] * 130), Y(pv + dv[1] * 130), RED, 2.4)
# etiketter
u, v = Jphi(RF - 100, form_phi[4]); S.leader(X(u), Y(v), X(-2350), Y(-150), f'Formkloss 45×95×200 radiellt, ände på\ninnerradien, mitt i facken, {NFK} st', '1')
u, v = Jphi(RM + 22, blk_phi[9]); S.leader(X(u), Y(v), X(-1500), Y(900), f'Motkloss 45×95×200 vid varje kloss, {NKL} st\n({GAP:.0f} mm utanför ytterflänsen; siffra = klossnr)', '2')
u, v = Jphi(ro + 12, blk_phi[11]); S.leader(X(u), Y(v), X(300), Y(900), 'Kilpar (två kilar ur 45×95)\nmitt för varje kloss = presstryck', '3')
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
S.rect(sx, sy, 760, 420, 'none', '#cfcac0', 1.5); S.txt(sx + 16, sy + 32, '3  SNITT VID EN KLOSS (ca 1:3)', 24, w='bold')
k3 = 2.6; by = sy + 300; x = sx + 40
S.rect(sx + 20, by, 720, 14, OSB, INK, 1); S.txt(sx + 24, by + 38, 'OSB-bord', 16, col=GREY)
S.rect(x, by - 95 * k3 / 2.6 * 1.6, 45 * k3, 95 * 1.6, '#e9e5dc', GREY, 1, ) if False else None
S.txt(x - 10, by - 110, 'insida', 15, col=GREY); S.txt(x - 10, by - 90, '(formkloss', 15, col=GREY); S.txt(x - 10, by - 70, ' i facken)', 15, col=GREY)
x += 120
for j_, (t, cl, nm) in enumerate(((PT, PLY, f'innerfläns {PT:.0f}'), (KH, PLY2, 'kloss 45'), (PT, PLY, f'ytterfläns {PT:.0f}'))):
    S.rect(x, by - 95 * 1.6, t * k3, 95 * 1.6, cl, INK, 1.2)
    S.line(x + t * k3 / 2, by - 95 * 1.6, x + t * k3 / 2, by - 95 * 1.6 - 14 - j_ * 22, GREY, 1)
    S.txt(x + t * k3 / 2 + 4, by - 95 * 1.6 - 18 - j_ * 22, nm, 15); x += t * k3
S.poly([(x + 4, by - 150), (x + 40, by - 150), (x + 22, by)], '#f3c9bf', RED, 1.2)
S.poly([(x + 44, by - 150), (x + 62, by), (x + 22, by)], '#f3c9bf', RED, 1.2)
S.txt(x + 34, by - 162, 'kilpar', 15, 'middle', col=RED); S.txt(x + 110, by - 162, 'motkloss', 15, col=GREY)
x += 66
S.rect(x, by - 95 * 1.6, 45 * k3, 95 * 1.6, '#c9a46b', INK, 1); S.txt(x + 58, by - 70, '2', 18, w='bold', col=RED)
for zz in (0.3, 0.7):
    yy = by - 95 * 1.6 * zz
    S.line(sx + 120 + PT * k3 + KH * k3 + PT * k3 + 1, yy, sx + 120 + PT * k3 + 6, yy, RED, 3.2)
    S.line(sx + 120 - 70, yy, sx + 120 + PT * k3 + 30, yy, '#2b6cb0', 3.2)
S.txt(sx + 16, sy + 352, 'Röd = 2 skruv 5×50 genom ytterflänsen (i mallen). Blå = 2 skruv 5×50 genom', 16)
S.txt(sx + 16, sy + 376, 'innerflänsen, från insidan mellan formklossarna. Lim (PU) på klossens båda sidor.', 16)
S.txt(sx + 16, sy + 400, f'5×60 är för lång vid djup {D:.0f} (går ut i andra flänsen).', 16, col=GREY)
# --- 4 material + arbetsgång ---
mx, my = 1600, 920
S.rect(mx, my, 760, 420, 'none', '#cfcac0', 1.5); S.txt(mx + 16, my + 32, '4  MATERIAL TILL MALLEN', 24, w='bold')
mat = ['2 st OSB 18 × 2500 × 1200 (skivan som bord)',
       'Reglar 45×95: 3 × 5,1 m (längsgående) + 9 × 1,2 m (tvärs c/c 625)',
       f'{NFK + NKL} st klossar 45×95×200 (≈ {(NFK + NKL) * 0.2 + 0.5:.0f} m regel) – form + mot',
       f'{NKL} kilpar ur 45×95 (≈ 3 m regel, sågas diagonalt)',
       'Skruv 5×80 (mallklossar, 3 per kloss) + 4,2×40 (OSB)',
       'Snöre, tumstock, vinkelhake, packtejp/plastfolie',
       '2 bockar eller plant golv']
for i, r in enumerate(mat): S.txt(mx + 20, my + 74 + i * 40, '• ' + r, 18)
# arbetsgång
S.rect(40, 1360, 2320, 370, 'none', '#cfcac0', 1.5); S.txt(60, 1396, 'ARBETSGÅNG', 24, w='bold')
steps = [f'Bygg bordet: reglar på bockar/golv, OSB ovanpå. Spänn snöre = korda {c:.0f} mm, mät ut ordinaterna (tabell 2), dra kurvan R {ri:.0f} med en böjd läkt.',
         f'Märk de {NKL} klossarnas lägen på bordet (mått längs ytterkanten, ritning blad 1). Skruva formklossarna (1) mitt i facken, motklossarna (2) mitt för klossarna.',
         'Lägg innerflänsens två bitar (25 mm övermått i ändarna) mot formklossarna, skarven mitt på kloss 7. Lim på klossarna, ställ dem på märkena.',
         'Böj ytterflänsens bitar runt klossarna, skarven mitt på kloss 8. Slå in kilparen (3) vid varje kloss – flänsarna ska ligga an mot alla klossar.',
         'Skruva 2 × 5×50 genom ytterflänsen i varje kloss, sedan innerflänsen inifrån mellan formklossarna. Skarvlaskar + 8 skruv 4,5×25.',
         'Knacka ur kilarna, lyft ur halvbågen direkt (skruvarna håller limmet). Kapa foten och nocken längs kaplinjerna (5). Märk H1–H18. Nästa!']
for i, r in enumerate(steps): S.bubble(76, 1440 + i * 50, str(i + 1), INK); S.txt(106, 1447 + i * 50, r, 19)
S.save('skiss_bagmall_2d')

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
for ph in form_phi:
    ux, uv = math.sin(ph), math.cos(ph); tx, tv = math.cos(ph), -math.sin(ph)
    prism([(r_ * ux + w_ * tx, r_ * uv - a0 + w_ * tv) for r_, w_ in ((RF - 200, -22.5), (RF, -22.5), (RF, 22.5), (RF - 200, 22.5))], 0, 95, '#c9a46b')
for ph in blk_phi:
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
S3.txt(40, 62, 'BÅGMALL – 3D (halvbåge i mallen)', 40, w='bold')
S3.txt(40, 96, f'OSB-bord på reglar, formklossar i facken längs innerradien, motklossar + röda kilpar vid varje kloss. Båge: {PT:.0f} + kloss {KH:.0f} + {PT:.0f}.', 20, col=GREY)
for f in bg:
    if f[0][0][2] == 0 and all(q[2] == 0 for q in f[0]): S3.poly([(TX(proj(q)[0]), TY(proj(q)[1])) for q in f[0]], f[1], f[2], f[3])
for i in order:
    pts, fill, col, sw = faces[i]
    S3.poly([(TX(q[0]), TY(q[1])) for q in pr[i]], fill, col, sw)
S3.save('skiss_bagmall_3d')
print('korda', round(c), 'pil', round(TAB[0][1]), 'a0', round(a0), 'klossar', len(KLS), 'nockkap mot korda', round(ang_nock, 1), 'fot', round(ang_fot, 1))
