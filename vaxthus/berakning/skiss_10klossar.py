#!/usr/bin/env python3
"""Skiss: båge 3x12 lameller, djup 200, 10 raka klossar 120 per halvbåge, dubbel syll + U-sko, hanbjälke, nock med lask.
Skriver skiss_10klossar_2d.svg/.png och skiss_10klossar_3d.svg/.png."""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
# ---------------- geometri (mm) ----------------
Bredd, Nockhojd, SyllH = 4000.0, 3500.0, 120.0
HB = Bredd / 2; BH = Nockhojd - SyllH
BagCx = (BH * BH - HB * HB) / (2 * HB); BagCz = SyllH; R = BagCx + HB
LT, NL = 12.0, 3; PT = LT * NL                 # lameller
BB, D = 95.0, 200.0; KH = D - 2 * PT; KL = 120.0
NockT = 45.0
NockV = math.acos((NockT / 2 + BagCx) / R); BL = R * NockV
SR = (45.0, 120.0)                              # sidoregel 45 längs bågen x 120 radiellt (högkant)
zS, zH = 1900.0, 2100.0
sS = R * math.asin((zS - BagCz) / R); sH = R * math.asin((zH - BagCz) / R)
def jamn(a, b, n): return [a + (b - a) * k / (n + 1) for k in range(1, n + 1)]
KLOSS = [KL / 2] + jamn(KL / 2, sS, 3) + [sH] + jamn(sH, BL - KL / 2, 4) + [BL - KL / 2]
assert len(KLOSS) == 10
CC, NB = 1250.0, 9
def P(s, r, side=1):     # punkt i bågplanet: s längs mittlinjen från foten, r radiellt (+ utåt); x från husets mitt
    th = s / R; return (side * (-BagCx + (R + r) * math.cos(th)), BagCz + (R + r) * math.sin(th))
def band(s0, s1, r0, r1, side=1, n=None):
    n = n or max(2, int((s1 - s0) / 40))
    return [P(s0 + (s1 - s0) * k / n, r1, side) for k in range(n + 1)] + [P(s1 - (s1 - s0) * k / n, r0, side) for k in range(n + 1)]
INK, GREY, RED, PLY, PLY2, STEEL, LIGHT = '#1d1d1b', '#8a8a86', '#c8321a', '#e8cf9c', '#d9b77a', '#b9bec4', '#efece5'

class Svg:
    def __init__(s, W, H): s.W, s.H, s.o = W, H, [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>']
    def a(s, x): s.o.append(x)
    def txt(s, x, y, t, size=20, anchor='start', w='normal', col=INK):
        s.a(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow, Helvetica, Arial" font-size="{size}" font-weight="{w}" fill="{col}" stroke="white" stroke-width="5" stroke-linejoin="round" paint-order="stroke" text-anchor="{anchor}">{t}</text>')
    def line(s, x1, y1, x2, y2, col=INK, w=2.0, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{da}/>')
    def rect(s, x, y, w, h, fill='none', col=INK, sw=2.0):
        s.a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    def poly(s, pts, fill='none', col=INK, sw=2.0, op=1.0, close=True):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + (' Z' if close else '')
        s.a(f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>')
    def circ(s, x, y, r, fill='white', col=INK, sw=1.5):
        s.a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    def bubble(s, x, y, n, col=RED):
        s.circ(x, y, 17, 'white', col, 2.5); s.txt(x, y + 7, n, 20, 'middle', 'bold', col)
    def leader(s, x1, y1, x2, y2, label, n=None, anchor='start', col=RED):
        s.line(x1, y1, x2, y2, col, 1.6); s.circ(x1, y1, 3.5, col, col, 1)
        if n: s.bubble(x2 + (18 if anchor == 'start' else -18), y2, n, col); x2 += 40 if anchor == 'start' else -40
        for i, t in enumerate(label.split('\n')): s.txt(x2 + (4 if anchor == 'start' else -4), y2 + 7 + i * 24, t, 19, anchor)
    def frame(s, x, y, w, h, title, scale=''):
        s.rect(x, y, w, h, 'none', '#cfcac0', 1.5); s.txt(x + 16, y + 32, title, 24, w='bold')
        if scale: s.txt(x + w - 16, y + 32, scale, 18, 'end', col=GREY)
    def save(s, name):
        s.a('</svg>'); p = os.path.join(HERE, name + '.svg'); open(p, 'w').write('\n'.join(s.o))
        subprocess.run(['rsvg-convert', '-w', str(s.W), '-o', os.path.join(HERE, name + '.png'), p], check=True)

# ======================= 2D =======================
S = Svg(2400, 1700)
S.txt(40, 62, 'VÄXTHUS – BÅGE MED 10 KLOSSAR (3 × 12 MM LAMELLER, DJUP 200)', 40, w='bold')
S.txt(40, 96, 'Bara raka sågsnitt: remsor 95 mm ur 12 mm konstruktionsplywood, böjs och limmas i 3 lager per fläns. Skiss – inte arbetsritning.', 20, col=GREY)
# --- 1 halvbåge ---
fx, fy, fw, fh = 40, 120, 1180, 1060
S.frame(fx, fy, fw, fh, '1  HALVBÅGE, SIDA', 'ca 1:20')
s1 = 0.235; ox, oy = fx + 110, fy + fh - 80
X = lambda x: ox + x * s1; Y = lambda z: oy - z * s1
T = lambda pts: [(X(x), Y(z)) for x, z in pts]
S.line(X(-150), Y(0), X(2500), Y(0), GREY, 2)
for xx in range(-150, 2500, 90): S.line(X(xx), Y(0), X(xx - 60), Y(-60), GREY, 1)
for dx in (-120, 0): S.rect(X(HB + dx), Y(SyllH), 120 * s1, SyllH * s1, LIGHT, INK, 1.4)
S.poly(T(band(0, BL, D / 2 - PT, D / 2)), PLY, INK, 1.6); S.poly(T(band(0, BL, -D / 2, -D / 2 + PT)), PLY, INK, 1.6)
for c in KLOSS:
    S.poly(T(band(c - KL / 2, c + KL / 2, -KH / 2, KH / 2, n=3)), PLY2, INK, 1.3)
S.poly(T(band(sS - SR[0] / 2, sS + SR[0] / 2, -SR[1] / 2, SR[1] / 2, n=2)), '#c9a46b', INK, 1.3)
# hanbjälke (inåt)
xi = -BagCx + (R - D / 2) * math.cos(sH / R)
S.rect(X(0), Y(zH + 60), (xi + 60) * s1, 120 * s1, '#f1d9d3', INK, 1.4)
S.txt(X(xi / 2), Y(zH + 60) - 8, 'hanbjälke 45×120 → andra halvbågen', 15, 'middle', col=GREY)
S.line(X(0), Y(Nockhojd - 250), X(0), Y(Nockhojd + 160), GREY, 1, '8 6'); S.txt(X(0) + 8, Y(Nockhojd + 120), '← husets mitt', 16, col=GREY)
# lask i nocken
S.poly(T(band(BL - 420, BL, -D / 2 - 5, D / 2 + 5, 1)) + [(X(-(BagCx * 0) + 0), Y(0))][:0], RED, RED, 2.2, 0.18)
# numrering klossar
for i, c in enumerate(KLOSS):
    x, z = P(c, -D / 2 - 70); S.txt(X(x), Y(z) + 6, str(i + 1), 17, 'middle', 'bold', RED)
# leaders
x, z = P(2600, D / 2 - PT / 2); S.leader(X(x), Y(z), fx + 720, Y(3000), 'Ytterfläns 3 × 12 × 95\nböjd + limmad lager för lager', '1')
x, z = P(700, -D / 2 + PT / 2); S.leader(X(x), Y(z), fx + 720, Y(800), 'Innerfläns 3 × 12 × 95', '1')
x, z = P(KLOSS[3], 0); S.leader(X(x), Y(z), fx + 720, Y(1500), f'Kloss {KL:.0f} lång, {KH:.0f} hög, 95 bred\n10 st per halvbåge (röda nr)', '2')
x, z = P(sS, 0); S.leader(X(x), Y(z), fx + 720, Y(2250), 'Sidoregel 45×120 på högkant\nfyller sitt fack (z 1900)', '3')
x, z = P(sH, -D / 2 - 20); S.leader(X(x) - 40, Y(zH) + 12, fx + 40, Y(1350), 'Hanbjälke 45×120, z 2100\n2 × M10 vid kloss 5', '4')
x, z = P(BL - 200, D / 2); S.leader(X(x), Y(z), fx + 420, Y(3550), 'Nock: lask 12 mm båda sidor\n+ nockregel + nockplåt', '5')
S.leader(X(HB + 60), Y(60), X(HB) + 70, Y(SyllH + 360), 'Dubbel syll 2 × 120×120\n+ U-sko 3 mm', '6')
# --- 2 sektion ---
sx, sy, sw, sh = 1240, 120, 560, 560
S.frame(sx, sy, sw, sh, '2  SEKTION GENOM KLOSS', '1:4')
k2 = 1.6; cx0, cy0 = sx + 190, sy + 110; xL = cx0 - BB / 2 * k2
for j in range(NL):
    S.rect(xL, cy0 + j * LT * k2, BB * k2, LT * k2, PLY, INK, 1.2)
    S.rect(xL, cy0 + (D - PT + j * LT) * k2, BB * k2, LT * k2, PLY, INK, 1.2)
S.rect(xL, cy0 + PT * k2, BB * k2, KH * k2, PLY2, INK, 1.4)
for xx in (xL + 25 * k2, xL + 70 * k2):
    S.line(xx, cy0 - 6, xx, cy0 + (PT + 45) * k2, INK, 2.4); S.line(xx, cy0 + D * k2 + 6, xx, cy0 + (D - PT - 45) * k2, INK, 2.4)
S.txt(cx0, cy0 - 16, 'film ↑ utsida (låsprofil på flänsen)', 16, 'middle', col=GREY)
S.line(xL - 50, cy0, xL - 50, cy0 + D * k2, GREY, 1.2); S.txt(xL - 58, cy0 + D * k2 / 2, '200', 18, 'end', col=GREY)
S.line(xL, cy0 + D * k2 + 34, xL + BB * k2, cy0 + D * k2 + 34, GREY, 1.2); S.txt(cx0, cy0 + D * k2 + 60, '95', 18, 'middle', col=GREY)
lx = xL + BB * k2 + 60
S.leader(xL + BB * k2 - 4, cy0 + 18 * k2, lx, cy0 + 20, '3 × 12 lameller, limmade\n(PU-lim utomhus)', '1')
S.leader(xL + BB * k2 - 4, cy0 + D / 2 * k2, lx, cy0 + 150, f'Kloss {KH:.0f} × 95 × {KL:.0f}\nlimmad + 2 skruv\n5×80 per sida', '2')
S.leader(xL + 70 * k2, cy0 + (D - PT - 30) * k2, lx, cy0 + 300, 'Skruv genom fläns\nin i klossen', None, col=INK)
# --- 3 foten ---
px, py, pw, ph = 1820, 120, 540, 560
S.frame(px, py, pw, ph, '3  BÅGFOT, FRAMIFRÅN', '1:8')
k3 = 0.9; bx, by = px + 270, py + 480
S.rect(bx - 120 * k3, by - 120 * k3, 120 * k3, 120 * k3, LIGHT, INK, 1.4); S.rect(bx, by - 120 * k3, 120 * k3, 120 * k3, LIGHT, INK, 1.4)
S.rect(bx - 100 * k3, by - 123 * k3, 200 * k3, 3 * k3 + 1, STEEL, RED, 1.8)
S.rect(bx - D / 2 * k3, by - (120 + 300) * k3, D * k3, 297 * k3, PLY, INK, 1.4)
S.rect(bx - D / 2 * k3 + PT * k3, by - (120 + 300) * k3, KH * k3, 297 * k3, 'none', GREY, 1)
S.rect(bx - D / 2 * k3 - 3 * k3, by - (120 + 250) * k3, 3 * k3 + 1, 247 * k3, STEEL, RED, 1.8)
S.rect(bx + D / 2 * k3, by - (120 + 250) * k3, 3 * k3 + 1, 247 * k3, STEEL, RED, 1.8)
for zz in (190, 300):
    S.line(bx - D / 2 * k3 - 18, by - zz * k3, bx + D / 2 * k3 + 18, by - zz * k3, INK, 3.5)
S.leader(bx + D / 2 * k3 + 4, by - 330 * k3, bx + 150, by - 360, 'U-sko 3 mm stål\n(varmförzinkad)', '6')
S.leader(bx + D / 2 * k3 + 18, by - 190 * k3, bx + 150, by - 230, '2 × M12 genom\nbåge + kloss', None, col=INK)
S.leader(bx + 100 * k3, by - 60 * k3, bx + 150, by - 90, 'Syll 2 × 120×120\nmarkskruv per fot', None, col=INK)
# --- 4 mängd/effekt ---
ny = 700
S.rect(1240, ny, 1120, 480, 'none', '#cfcac0', 1.5)
S.txt(1256, ny + 34, '4  VARFÖR / MÄNGD', 24, w='bold')
cc_lo = KLOSS[2] - KLOSS[1]; cc_hi = KLOSS[6] - KLOSS[5]
rows = ['Beräknat 30 m/s vind, snö Höör, c/c 1250: utnyttjande 0,40 / 0,60 / 0,64',
        '   (snö / vind / lyft – under 1,0 = håller). 2 × 12 klarar INTE 10 klossar (1,23).',
        f'Klossar c/c ≈ {cc_lo:.0f} nedre / {cc_hi:.0f} övre + sidoregel i eget fack',
        f'Per halvbåge: 6 remsor 95 × 12 × ~{BL/1000:.1f} m (skarvas förskjutet), 10 klossar',
        f'Hela huset (9 bågar): {9*2*6} remsor ≈ {9*2*6*BL/1000:.0f} lpm → ca {math.ceil(9*2*6*BL/2440/12)+1} skivor 12×2500×1200',
        f'Klossar: {9*2*10} st ur 2 × 12 limmat eller 45×{KH:.0f}-regel',
        'Eurocode 50-årsstorm: ca 1,1 – dimensionerat som Norhages hus (25–30 m/s)']
for i, r in enumerate(rows): S.txt(1256, ny + 80 + i * 48, r, 19)
# --- montering ---
S.rect(40, 1200, 2320, 460, 'none', '#cfcac0', 1.5)
S.txt(60, 1236, 'BYGGORDNING', 24, w='bold')
steps = ['Rita bågen 1:1 på golv/plywoodbord, skruva fast klossar som mall längs ytter- och innerradie.',
         'Lägg innerflänsens första remsa mot mallen, lim (PU) + klamra lager 2 och 3 – skarvar minst 600 förskjutna.',
         'Ytterflänsen likadant. Klossarna limmas och skruvas 2 × 5×80 per sida genom flänsen.',
         'Fot: U-sko trär på, borra M12 genom båge + kloss 1. Nock: lask 12 mm båda sidor, limmad + skruvad.',
         'Res bågarna på dubbelsyllen, sidoreglar 45×120 genom facken, hanbjälke 2 × M10 vid kloss 5.',
         'Låsprofil för film på ytterflänsens utsida som tidigare; vindkryss i ändfacken.']
for i, r in enumerate(steps): S.bubble(76, 1284 + i * 62, str(i + 1), INK); S.txt(106, 1291 + i * 62, r, 20)
S.save('skiss_10klossar_2d')

# ======================= 3D (isometri, painter) =======================
az, el = math.radians(-38), math.radians(24)
def proj(p):
    x, y, z = p
    xr = x * math.cos(az) - y * math.sin(az); yr = x * math.sin(az) + y * math.cos(az)
    return xr, -(z * math.cos(el) - yr * math.sin(el)), yr * math.cos(el) + z * math.sin(el)   # sx, sy, djup (större = närmare)
faces = []
def prism(poly2, y0, y1, fill, col=INK, sw=0.9):     # polygon i (x,z) extruderad längs y
    n = len(poly2)
    A = [(x, y0, z) for x, z in poly2]; B = [(x, y1, z) for x, z in poly2]
    faces.append((A, fill, col, sw)); faces.append((B, fill, col, sw))
    for i in range(n):
        j = (i + 1) % n; faces.append(([A[i], A[j], B[j], B[i]], fill, col, 0.5))
def box(x0, x1, y0, y1, z0, z1, fill, col=INK):
    prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, fill, col)
def bage3d(y, side):
    for s0 in range(0, int(BL), 150):
        s1_ = min(BL, s0 + 150)
        for r0, r1 in ((D / 2 - PT, D / 2), (-D / 2, -D / 2 + PT)):
            prism(band(s0, s1_, r0, r1, side, 3), y - BB / 2, y + BB / 2, PLY)
    for c in KLOSS:
        prism(band(c - KL / 2, c + KL / 2, -KH / 2, KH / 2, side, 2), y - BB / 2 + 2, y + BB / 2 - 2, PLY2)
    # U-sko
    for yy in (y - BB / 2 - 3, y + BB / 2):
        box(side * HB - D / 2, side * HB + D / 2, yy, yy + 3, SyllH, SyllH + 250, STEEL, RED)
YS = [k * CC for k in range(3)]
for y in YS:
    for side in (1, -1): bage3d(y, side)
    xi = -BagCx + (R - D / 2) * math.cos(sH / R)
    box(-xi, xi, y + BB / 2, y + BB / 2 + 45, zH, zH + 120, '#f1d9d3')
    for yy in (y - BB / 2 - 12, y + BB / 2):
        prism(band(BL - 420, BL, -D / 2, D / 2, 1, 4) , yy, yy + 12, '#f3c9bf', RED)
        prism(band(BL - 420, BL, -D / 2, D / 2, -1, 4), yy, yy + 12, '#f3c9bf', RED)
y0, y1 = -400, YS[-1] + 400
for side in (1, -1):
    for dx in (-120, 0): box(side * HB + dx, side * HB + dx + 120, y0, y1, 0, SyllH, LIGHT)
    x, z = P(sS, 0, side); box(x - 22, x + 22, y0, y1, z - 60, z + 60, '#c9a46b')
box(-NockT / 2, NockT / 2, y0, y1, Nockhojd - D - 120, Nockhojd - D, '#c9a46b')
pr = [[proj(p) for p in f[0]] for f in faces]
order = sorted(range(len(faces)), key=lambda i: sum(q[2] for q in pr[i]) / len(pr[i]))
xs = [q[0] for f in pr for q in f]; ys = [q[1] for f in pr for q in f]
W3, H3 = 2400, 1600; m = 80
sc = min((W3 - 2 * m) / (max(xs) - min(xs)), (H3 - 2 * m - 120) / (max(ys) - min(ys)))
offx = (W3 - (max(xs) - min(xs)) * sc) / 2
TX = lambda x: offx + (x - min(xs)) * sc; TY = lambda y: m + 120 + (y - min(ys)) * sc
S3 = Svg(W3, H3)
S3.txt(40, 62, 'VÄXTHUS – 3D: TVÅ FACK, BÅGE MED 10 KLOSSAR', 40, w='bold')
S3.txt(40, 96, 'Flänsar 3 × 12, djup 200, klossar 120, sidoreglar 45×120 genom facken, hanbjälke z 2100, nocklask 12 mm (röd), U-sko (röd), dubbel syll.', 20, col=GREY)
for i in order:
    pts, fill, col, sw = faces[i]
    S3.poly([(TX(q[0]), TY(q[1])) for q in pr[i]], fill, col, sw)
S3.save('skiss_10klossar_3d')
print('klossar', [round(c) for c in KLOSS], 'BL', round(BL), 'c/c', round(KLOSS[2] - KLOSS[1]), round(KLOSS[6] - KLOSS[5]))
