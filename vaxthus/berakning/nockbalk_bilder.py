#!/usr/bin/env python3
"""Monteringsbilder nockbalk (linjestil: grått = monterat, rött = nytt, utdragna skruvar längs sin axel, bubblor).
Geometri ur v13_param.json (båge 1×15, djup 75, nocklask 15, nockbalk 45×120). Skriver bilder/nockbalk_1..3.png"""
import json, math, os, subprocess
V = os.path.expanduser('~/code/buttercup/vaxthus')
P = json.load(open(V + '/fusion/v13_param.json', encoding='utf-8'))
OUTD = V + '/fusion/bilder/'
INK, GREY, LG, RED, PINK, WHITE = '#2b2b2b', '#8a8a86', '#e4e2dd', '#c8321a', '#f6c9bd', '#ffffff'
Bredd, Nockhojd, SyllH, NockT = P['Bredd'], P['Nockhojd'], P['SyllH'], P['NockT']
HB = Bredd / 2; BH = Nockhojd - SyllH; cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
D, BB, KL, LT = P['BagDjup'], P['BagB'], P['KlossL'], P['NockLaskT']
PT = P['PlyT']; ri, ro = R - D / 2, R + D / 2
XN = NockT / 2; CC = P['BagCC']; LX = P['NockLaskL'] / 2; LAV = P['NockLaskAvdrag']
NH = P['NockH']; BL = P['BagLangd']
def zc(r, x): return math.sqrt(r * r - (x + cx) ** 2)
ZT = zc(ro, XN)                      # nockens ytterkant (lokal nolla nedan)
def th_end(r): return math.acos((XN + cx) / r)
def pt(r, th, sd): return (sd * (-cx + r * math.cos(th)), r * math.sin(th) - ZT)
def band(r0, r1, t0, t1, sd, n=8):
    a = [pt(r1, t0 + (t1 - t0) * k / n, sd) for k in range(n + 1)]
    b = [pt(r0, t1 - (t1 - t0) * k / n, sd) for k in range(n + 1)]
    return a + b
rr = ro - LAV; sag = LX ** 2 / (8 * ri)
LASK = [(-LX, zc(rr, LX) - ZT), (0, zc(rr, 0) - ZT), (LX, zc(rr, LX) - ZT), (LX, zc(ri, LX) + sag - ZT), (0, zc(ri, 0) + sag - ZT), (-LX, zc(ri, LX) + sag - ZT)]
LB = CC - BB - 2 * LT                # nockbalkens längd
X_CUT = 470.0                        # hur långt ut bågen ritas
t_cut = math.acos((X_CUT + cx) / R)

class Svg:
    def __init__(s, W, H): s.W, s.H, s.o = W, H, [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>']
    def a(s, x): s.o.append(x)
    def poly(s, pts, fill, col=INK, sw=1.6):
        s.a('<path d="M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f' Z" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>')
    def line(s, x1, y1, x2, y2, col=INK, w=1.6, dash=None, cap='round'):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}"{da}/>')
    def circ(s, x, y, r, fill, col=INK, sw=1.6): s.a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    def txt(s, x, y, t, sz=24, anc='start', w='normal', col=INK):
        s.a(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow, Helvetica, Arial" font-size="{sz}" font-weight="{w}" fill="{col}" text-anchor="{anc}" stroke="white" stroke-width="5" paint-order="stroke">{t}</text>')
    def bub(s, x, y, n, col=RED): s.circ(x, y, 20, WHITE, col, 2.6); s.txt(x, y + 8, n, 24, 'middle', 'bold', col)
    def arrow(s, x1, y1, x2, y2, col=RED, w=3):
        s.line(x1, y1, x2, y2, col, w); a = math.atan2(y2 - y1, x2 - x1)
        for d in (2.6, -2.6): s.line(x2, y2, x2 - 18 * math.cos(a + d / 6), y2 - 18 * math.sin(a + d / 6), col, w)
    def save(s, name):
        s.a('</svg>'); sv = OUTD + name + '.svg'; open(sv, 'w', encoding='utf-8').write('\n'.join(s.o))
        subprocess.run(['rsvg-convert', '-o', OUTD + name + '.png', sv], check=True); return OUTD + name + '.png'

class Scene:
    def __init__(s, az, el): s.az, s.el = math.radians(az), math.radians(el); s.F = []
    def pr(s, p):
        x, y, z = p
        xr = x * math.cos(s.az) - y * math.sin(s.az); yr = x * math.sin(s.az) + y * math.cos(s.az)
        return (xr, -(z * math.cos(s.el) - yr * math.sin(s.el)), yr * math.cos(s.el) + z * math.sin(s.el))
    def prism_xz(s, poly, y0, y1, fill, col=INK):        # polygon i (x, z), extruderad i y
        A = [(x, y0, z) for x, z in poly]; B = [(x, y1, z) for x, z in poly]; n = len(poly)
        s.F += [(A, fill, col), (B, fill, col)] + [([A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]], fill, col) for i in range(n)]
    def box(s, x0, x1, y0, y1, z0, z1, fill, col=INK, nseg=1):
        for k in range(nseg):
            a, b = y0 + (y1 - y0) * k / nseg, y0 + (y1 - y0) * (k + 1) / nseg
            s.prism_xz([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], a, b, fill, col)
    def render(s, S, box_px, extra=()):
        P2 = [[s.pr(p) for p in f[0]] for f in s.F]
        ex = [s.pr(p) for p in extra]
        xs = [q[0] for f in P2 for q in f] + [q[0] for q in ex]; ys = [q[1] for f in P2 for q in f] + [q[1] for q in ex]
        x0, y0, w, h = box_px
        sc = min(w / (max(xs) - min(xs)), h / (max(ys) - min(ys)))
        ox = x0 + (w - (max(xs) - min(xs)) * sc) / 2 - min(xs) * sc; oy = y0 + (h - (max(ys) - min(ys)) * sc) / 2 - min(ys) * sc
        s.T = lambda p: (ox + s.pr(p)[0] * sc, oy + s.pr(p)[1] * sc)
        order = sorted(range(len(s.F)), key=lambda i: sum(q[2] for q in P2[i]) / len(P2[i]))
        for i in order:
            pts, fill, col = s.F[i]
            S.poly([s.T(p) for p in pts], fill, col, 1.3 if fill in (LG, WHITE) else 1.6)
        return s.T

def seg(sc, r0, r1, t0, t1, sd, y0, y1, fill, step=70.0):
    n = max(1, int((t1 - t0) * R / step))
    for k in range(n):
        sc.prism_xz(band(r0, r1, t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n, sd, 2), y0, y1, fill)

def bage(sc, y, lask_bada=True):
    for sd in (1, -1):
        seg(sc, ri, ri + PT, t_cut, th_end(ri + PT), sd, y - BB / 2, y + BB / 2, LG)
        seg(sc, ro - PT, ro, t_cut, th_end(ro), sd, y - BB / 2, y + BB / 2, LG)
        sc.prism_xz(band(ri + PT, ro - PT, (BL - KL) / R, th_end(R), sd, 3), y - BB / 2, y + BB / 2, '#d6d1c4')
        sc.prism_xz(band(ri + PT, ro - PT, (BL - KL - 258) / R, (BL - 258) / R, sd, 3), y - BB / 2, y + BB / 2, '#d6d1c4')
    for sg in ((-1, 1) if lask_bada else (1,)):
        y0 = y + sg * BB / 2; y1 = y0 + sg * LT
        sc.prism_xz(LASK, min(y0, y1), max(y0, y1), WHITE)

def skruvar(y_end, sgn):
    """2 korsade snedskruvar 6x120 i balkänden vid y_end (sgn = riktning mot bågen). Returnerar [(start, slut)]"""
    out = []
    for sx in (1, -1):
        e = (sx * XN, y_end - sgn * 30, -24 if sx > 0 else -46)         # in i balkens sida, i nockklossens höjd
        d = (-sx * 0.6, sgn * 0.75, -0.05); L_ = math.sqrt(sum(v * v for v in d)); d = tuple(v / L_ for v in d)
        out.append((e, tuple(e[i] + d[i] * 120 for i in range(3)), d))
    return out

def rita_skruv(S, T, e, tip, d, pull=150):
    a = tuple(e[i] - d[i] * pull for i in range(3)); b = tuple(tip[i] - d[i] * pull for i in range(3))
    S.line(*T(e), *T(tip), RED, 1.4, '6 5')                                # skruvens väg i träet (streckad)
    S.line(*T(a), *T(e), RED, 1.2, '3 6')
    (ax_, ay_), (bx_, by_) = T(a), T(b)
    S.line(ax_, ay_, bx_, by_, RED, 5)
    S.circ(ax_, ay_, 9, WHITE, RED, 3)

# ---------------- bild 1: översikt, lyft upp biten ----------------
S = Svg(1600, 1100)
S.txt(40, 60, 'NOCKBALK 1 – lyft upp biten mellan bågarna (sett inifrån, underifrån)', 38, w='bold')
S.txt(40, 96, f'Nockbalk 45×120 × {LB:.0f}, på högkant mitt i nocken, mellan nocklaskarna. Mät c/c {CC:.0f} med lattan.', 22, col=GREY)
sc = Scene(-30, -18)
bage(sc, 0); bage(sc, CC)
sc.box(-XN, XN, BB / 2 + LT, CC - BB / 2 - LT, -NH, 0, PINK, RED, nseg=12)
T = sc.render(S, (60, 130, 1480, 860), extra=[(0, -200, -700), (0, CC + 200, 200)])
for yy in (BB / 2 + LT + 200, CC - BB / 2 - LT - 200):
    S.arrow(*T((0, yy, -NH - 420)), *T((0, yy, -NH - 30)))
yl0, yl1, zl = 0, CC, -NH - 520
S.line(*T((0, yl0, zl)), *T((0, yl1, zl)), INK, 2.5)
for yy in (yl0, yl1): S.line(*T((0, yy, zl - 40)), *T((0, yy, zl + 40)), INK, 2.5)
mx, my = T((0, CC / 2, zl)); S.txt(mx, my + 36, f'mätlatta c/c {CC:.0f}', 24, 'middle', 'bold')
bx, by = T((0, CC * 0.5, -NH)); S.bub(bx + 60, by + 60, '1'); S.line(bx, by, bx + 42, by + 45, RED, 1.6)
lx, ly = T((LX * 0.6, -BB / 2 - LT, LASK[3][1])); S.bub(lx - 90, ly + 60, '2', INK); S.line(lx, ly, lx - 72, ly + 48, INK, 1.4)
S.txt(60, 1050, '1  Nockbalk (ny, röd)     2  Nocklask, båda sidor om varje båge (gavelbåge: bara insidan)', 24)
p1 = S.save('nockbalk_1')

# ---------------- bild 2: detalj korsade snedskruvar ----------------
S = Svg(1600, 1100)
S.txt(40, 60, 'NOCKBALK 2 – korsade snedskruvar i varje ände', 38, w='bold')
S.txt(40, 96, '2 × 6×120 per ände: en från varje sida, snett in genom balkänden och nocklasken in i motsatta halvans nockkloss. Förborra Ø4.', 22, col=GREY)
sc = Scene(-55, -16)
bage(sc, 0)
sc.box(-XN, XN, BB / 2 + LT, BB / 2 + LT + 520, -NH, 0, PINK, RED, nseg=3)
SK = skruvar(BB / 2 + LT, -1)
T = sc.render(S, (60, 140, 1480, 880), extra=[e for e, t, d in SK] + [tuple(e[i] - d[i] * 170 for i in range(3)) for e, t, d in SK])
for i, (e, tip, d) in enumerate(SK): rita_skruv(S, T, e, tip, d, 150)
hx, hy = T(tuple(SK[0][0][i] - SK[0][2][i] * 150 for i in range(3))); S.bub(hx + 50, hy - 40, '3')
bx, by = T((0, BB / 2 + LT + 400, -NH)); S.bub(bx + 30, by + 60, '1'); S.line(bx, by, bx + 15, by + 40, RED, 1.6)
kx, ky = T(pt(R, (BL - KL / 2) / R, -1)[0:1] + (0,) + pt(R, (BL - KL / 2) / R, -1)[1:]) if False else T((-90, 0, -45))
S.bub(kx - 70, ky + 90, '4', INK); S.line(kx, ky, kx - 52, ky + 72, INK, 1.4)
S.txt(60, 1050, '1  Nockbalk     3  Skruv 6×120 (utdragen – streckat = vägen i träet)   4  Nockkloss (motsatta halvan)', 24)
p2 = S.save('nockbalk_2')

# ---------------- bild 3: uppifrån ----------------
S = Svg(1600, 900)
S.txt(40, 60, 'NOCKBALK 3 – uppifrån: skruvarna korsar glipan', 38, w='bold')
S.txt(40, 96, f'Balken ({NockT:.0f} bred) ligger över nockglipan ({NockT:.0f}). Skruvarna går snett över till nockklossen på andra sidan.', 22, col=GREY)
k = 2.1; ox, oy = 800, 520
X = lambda x: ox + x * k; Y = lambda y: oy - (y - 60) * k
# båge (snitt i nockhöjd): halvornas nockklossar + flänsar, glipa i mitten
for sd in (1, -1):
    S.poly([(X(sd * XN), Y(-BB / 2)), (X(sd * 300), Y(-BB / 2)), (X(sd * 300), Y(BB / 2)), (X(sd * XN), Y(BB / 2))], LG, INK, 1.4)
    S.poly([(X(sd * XN), Y(-BB / 2)), (X(sd * (XN + 120)), Y(-BB / 2)), (X(sd * (XN + 120)), Y(BB / 2)), (X(sd * XN), Y(BB / 2))], '#d6d1c4', INK, 1.4)
for sg in (-1, 1):
    y0 = sg * BB / 2; y1 = y0 + sg * LT
    S.poly([(X(-LX), Y(y0)), (X(LX), Y(y0)), (X(LX), Y(y1)), (X(-LX), Y(y1))], WHITE, INK, 1.4)
S.poly([(X(-XN), Y(BB / 2 + LT)), (X(XN), Y(BB / 2 + LT)), (X(XN), Y(BB / 2 + LT + 160)), (X(-XN), Y(BB / 2 + LT + 160))], PINK, RED, 2)
for e, tip, d in skruvar(BB / 2 + LT, -1):
    S.line(X(e[0]), Y(e[1]), X(tip[0]), Y(tip[1]), RED, 5)
    a = (e[0] - d[0] * 90, e[1] - d[1] * 90); S.line(X(a[0]), Y(a[1]), X(e[0]), Y(e[1]), RED, 1.4, '4 6'); S.circ(X(a[0]), Y(a[1]), 9, WHITE, RED, 3)
S.txt(X(0), Y(-BB / 2) + 60, f'nockglipa {NockT:.0f}', 22, 'middle', col=GREY)
S.txt(X(-200), Y(0) + 8, 'nockkloss', 22, 'middle'); S.txt(X(200), Y(0) + 8, 'nockkloss', 22, 'middle')
S.txt(X(LX) + 14, Y(BB / 2 + LT / 2) + 8, f'nocklask {LT:.0f}', 22)
S.txt(X(XN) + 14, Y(BB / 2 + LT + 120), 'nockbalk', 22, col=RED, w='bold')
S.txt(60, 860, 'Sett ovanifrån i nockhöjd, en båge och balkens ände. Samma i balkens andra ände.', 24)
p3 = S.save('nockbalk_3')
print(p1, p2, p3, 'LB', round(LB))
