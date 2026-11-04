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
rr = ro - LAV
NBB, NBH, NLU = P['NockBalkB'], P['NockBalkH'], P['NockLaskUnder']
XS = XN
zE, zS = zc(rr, LX) - ZT, zc(rr, XS) - ZT
zN = -NBH; zU0 = zN - NLU; zUE = zU0 - (zS - zE)
LASK = [(-LX, zE), (-XS, zS), (-XS, zN), (XS, zN), (XS, zS), (LX, zE), (LX, zUE), (0, zU0), (-LX, zUE)]
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

def rita_skruv(S, T, e, d, L=40, pull=110):
    tip = tuple(e[i] + d[i] * L for i in range(3)); a = tuple(e[i] - d[i] * pull for i in range(3)); b = tuple(e[i] - d[i] * (pull - L) for i in range(3))
    S.line(*T(a), *T(e), RED, 1.2, '3 6'); S.line(*T(a), *T(b), RED, 5); S.circ(*T(a), 8, WHITE, RED, 3)

def vinkel(sc, y_face, sg):
    """vinkelbeslag 30x30x25: ett ben mot balkens sida (x = NBB/2), ett mot laskens yta (y = y_face)"""
    x0 = NBB / 2; z0, z1 = -55, -30; T_ = 2.5
    sc.box(x0, x0 + T_, y_face, y_face + sg * 30 if sg > 0 else y_face, z0, z1, '#b9bec4') if sg > 0 else sc.box(x0, x0 + T_, y_face - 30, y_face, z0, z1, '#b9bec4')
    ya, yb = (y_face, y_face + sg * T_) if sg > 0 else (y_face - T_, y_face)
    sc.box(x0, x0 + 30, min(ya, yb), max(ya, yb), z0, z1, '#b9bec4')

# ---------------- bild 1: lägg balken uppifrån ----------------
S = Svg(1600, 1100)
S.txt(40, 60, 'NOCKBALK 1 – lägg balken uppifrån i nockglipan', 38, w='bold')
S.txt(40, 96, f'Nockbalk {NBB:.0f}×{NBH:.0f} i hela längder, på högkant. Den vilar i urtagen i nocklaskarna, överkant = bågarnas ytterkant.', 22, col=GREY)
sc = Scene(-35, 28)
for b_ in range(3): bage(sc, b_ * CC)
LIFT = 320
sc.box(-NBB / 2, NBB / 2, -200, 2 * CC + 400, -NBH + LIFT, LIFT, PINK, RED, nseg=14)
T = sc.render(S, (60, 130, 1480, 880), extra=[(0, -300, 700), (0, 2 * CC + 500, -500)])
for yy in (CC * 0.5, CC * 1.5):
    S.arrow(*T((0, yy, LIFT + 300)), *T((0, yy, LIFT + 40)))
bx, by = T((NBB / 2, CC, LIFT - NBH)); S.bub(bx + 60, by + 50, '1'); S.line(bx, by, bx + 42, by + 36, RED, 1.6)
ux, uy = T((XS, CC + BB / 2 + LT, zN)); S.bub(ux + 90, uy + 70, '2', INK); S.line(ux, uy, ux + 72, uy + 56, INK, 1.4)
S.txt(60, 1050, f'1  Nockbalk (ny, röd)     2  Urtag {2 * XS:.0f} × {NBH:.0f} i nocklasken – balken vilar här (gavelbåge: lask bara på insidan)', 24)
p1 = S.save('nockbalk_1')

# ---------------- bild 2: vinkelbeslag ----------------
S = Svg(1600, 1100)
S.txt(40, 60, 'NOCKBALK 2 – ett vinkelbeslag per båge', 38, w='bold')
S.txt(40, 96, 'Vinkelbeslag 30×30×25 på ena sidan: 2 skruv 4,5×40 i laskens yta och 2 i balkens sida. Mät c/c 1250 innan du skruvar.', 22, col=GREY)
sc = Scene(62, 26)
bage(sc, 0)
sc.box(-NBB / 2, NBB / 2, -250, 450, -NBH, 0, PINK, RED, nseg=6)
yf = BB / 2 + LT
vinkel(sc, yf, 1)
T = sc.render(S, (60, 140, 1480, 860), extra=[(250, 400, 100), (-300, -200, -250)])
for zz in (-37, -48):
    rita_skruv(S, T, (NBB / 2 + 30 * 0.4 + (zz + 37) * 0, yf + 2.5, -42.5 + (zz + 42.5)), (0, -1, 0), 40, 120) if False else None
for dz in (-36, -49):
    rita_skruv(S, T, (NBB / 2 + 18, yf + 2.5, dz + 0), (0, -1, 0), 40, 120)     # i lasken
    rita_skruv(S, T, (NBB / 2 + 2.5, yf + 18, dz + 0), (-1, 0, 0), 40, 120)     # i balken
vx, vy = T((NBB / 2 + 30, yf + 30, -30)); S.bub(vx + 80, vy - 60, '3', INK); S.line(vx, vy, vx + 62, vy - 46, INK, 1.4)
bx, by = T((NBB / 2, 380, -NBH)); S.bub(bx + 40, by + 60, '1'); S.line(bx, by, bx + 26, by + 44, RED, 1.6)
S.txt(60, 1050, '1  Nockbalk     3  Vinkelbeslag 30×30×25 (grå)     röda = skruv 4,5×40, utdragna längs sin axel', 24)
p2 = S.save('nockbalk_2')

# ---------------- bild 3: skarv ----------------
S = Svg(1600, 1000)
S.txt(40, 60, 'NOCKBALK 3 – skarv mitt i ett fack', 38, w='bold')
S.txt(40, 96, 'Skarva mitt mellan två bågar (inte vid en båge – där är balkens sidor dolda). Spikplåt 2×100×200 på båda sidor, 8 ankarspik per halva.', 22, col=GREY)
sc = Scene(-40, 18)
bage(sc, 0); bage(sc, CC)
sc.box(-NBB / 2, NBB / 2, -300, CC / 2 - 2, -NBH, 0, LG, INK, nseg=4)
sc.box(-NBB / 2, NBB / 2, CC / 2 + 2, CC + 300, -NBH, 0, LG, INK, nseg=4)
for sx in (1, -1):
    x0 = sx * NBB / 2
    sc.box(min(x0, x0 + sx * 2), max(x0, x0 + sx * 2), CC / 2 - 100, CC / 2 + 100, -NBH / 2 - 35 + 0, -NBH / 2 + 35, PINK, RED)
T = sc.render(S, (60, 130, 1480, 760), extra=[(0, -400, 200), (0, CC + 400, -300)])
for yy in (CC / 2 - 70, CC / 2 - 30, CC / 2 + 30, CC / 2 + 70):
    rita_skruv(S, T, (NBB / 2 + 2, yy, -NBH / 2), (-1, 0, 0), 40, 110)
sx_, sy_ = T((NBB / 2 + 2, CC / 2 + 100, -NBH / 2 + 35)); S.bub(sx_ + 70, sy_ - 50, '4'); S.line(sx_, sy_, sx_ + 52, sy_ - 36, RED, 1.6)
S.txt(60, 960, 'Spikplåt (röd) på båda sidor om skarven. Skarvar t.ex. vid 3 125 och 6 875 från gaveln = längder ca 3,2 / 3,75 / 3,2 m.', 24)
p3 = S.save('nockbalk_3')
print(p1, p2, p3)
