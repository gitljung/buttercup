#!/usr/bin/env python3
"""Skiss: föreslagen lösning för växthusets bågar (lådbåge + hanbjälke + vindkryss). Skriver skiss_losning.svg/.png."""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))

# geometri (mm)
Bredd, Nockhojd, SyllH = 4000.0, 3500.0, 120.0
HB = Bredd / 2; BH = Nockhojd - SyllH
BagCx = (BH * BH - HB * HB) / (2 * HB); BagCz = SyllH; R = BagCx + HB
D = 230.0; FL = 30.0; WEB = 9.0; BB = 70.0      # bågdjup, fläns (2x15), sidoskiva, flänsbredd
ZH = 2000.0                                       # hanbjälke
CC = 1250.0; L = 10000.0

W, H = 2400, 1650
INK, GREY, RED, LIGHT, PLY = '#1d1d1b', '#8a8a86', '#c8321a', '#e9e6df', '#e8cf9c'
out = []
def a(s): out.append(s)
def txt(x, y, s, size=20, anchor='start', w='normal', col=INK, it=False):
    st = ' font-style="italic"' if it else ''
    a(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow, Helvetica, Arial" font-size="{size}" font-weight="{w}" fill="{col}" stroke="white" stroke-width="5" stroke-linejoin="round" paint-order="stroke" text-anchor="{anchor}"{st}>{s}</text>')
def line(x1, y1, x2, y2, col=INK, w=2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{da}/>')
def rect(x, y, w, h, fill='none', col=INK, sw=2):
    a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
def path(d, fill='none', col=INK, sw=2):
    a(f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>')
def bubble(x, y, n, col=RED):
    a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="white" stroke="{col}" stroke-width="2.5"/>'); txt(x, y + 7, n, 20, 'middle', 'bold', col)
def leader(x1, y1, x2, y2, label, n=None, anchor='start', col=RED):
    line(x1, y1, x2, y2, col, 1.6); a(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="3.5" fill="{col}"/>')
    if n: bubble(x2 + (18 if anchor == 'start' else -18), y2, n, col); x2 += 40 if anchor == 'start' else -40
    for i, s in enumerate(label.split('\n')): txt(x2 + (4 if anchor == 'start' else -4), y2 + 7 + i * 24, s, 19, anchor, col=INK)
def frame(x, y, w, h, title, scale):
    rect(x, y, w, h, 'none', '#cfcac0', 1.5)
    txt(x + 16, y + 32, title, 24, w='bold'); txt(x + w - 16, y + 32, scale, 18, 'end', col=GREY)

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a(f'<rect width="{W}" height="{H}" fill="white"/>')
txt(40, 62, 'VÄXTHUS – FÖRSLAG BÄRANDE BÅGE', 40, w='bold')
txt(40, 96, 'Lådbåge 230 mm (limmad), hanbjälke, vindkryss och markskruv. Skiss – inte arbetsritning. Underlag: berakning/BERAKNING.md', 20, col=GREY)

# ---------- 1. gavelsektion ----------
fx, fy, fw, fh = 40, 120, 1240, 1000
frame(fx, fy, fw, fh, '1  SEKTION GENOM MELLANBÅGE', 'ca 1:25')
s = 0.23; ox, oy = fx + fw / 2, fy + fh - 110
X = lambda x: ox + x * s; Y = lambda z: oy - z * s
# mark + syll
line(X(-2600), Y(0), X(2600), Y(0), GREY, 2)
for xx in range(-2600, 2600, 90): line(X(xx), Y(0), X(xx - 60), Y(-60), GREY, 1)
def arc_pts(rr, side, t0, t1, n=80):
    cx = -BagCx * side
    return [(cx + rr * math.cos(t0 + (t1 - t0) * k / n) * side, BagCz + rr * math.sin(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]
tN = math.acos(BagCx / R)          # mittlinjen når x = 0
for side in (1, -1):
    # syll (bredare): 2 x 120x120 sida vid sida
    xs = HB * side
    rect(X(xs - 120), Y(SyllH), 240 * s, SyllH * s, PLY if False else '#d9d4c7', INK, 1.6)
    line(X(xs), Y(SyllH), X(xs), Y(0), INK, 1)
    # båge: yttre och inre kontur
    tN_o = math.acos(BagCx / (R + D / 2)); tN_i = math.acos(BagCx / (R - D / 2))
    po = arc_pts(R + D / 2, side, math.asin(0), tN_o); pi = arc_pts(R - D / 2, side, 0, tN_i)
    d = 'M' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in po) + ' L' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in reversed(pi)) + ' Z'
    path(d, PLY, INK, 2)
    # fläns-linjer (2x15)
    for rr in (R + D / 2 - FL, R - D / 2 + FL):
        tt = math.acos(BagCx / rr); p = arc_pts(rr, side, 0, tt)
        path('M' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in p), 'none', INK, 0.9)
    # sidoskivornas skarvar (förskjutna) + klossar vid skarvar
    for frac in (0.38, 0.72):
        t = tN * frac; cx = -BagCx * side
        x1, z1 = cx + (R - D / 2) * math.cos(t) * side, BagCz + (R - D / 2) * math.sin(t)
        x2, z2 = cx + (R + D / 2) * math.cos(t) * side, BagCz + (R + D / 2) * math.sin(t)
        line(X(x1), Y(z1), X(x2), Y(z2), INK, 1.2, '6 4')
# nockskarv: sidoskivor (lask) över krönet
tt = 0.16
cx = -BagCx
pts_o = [(-BagCx * sd + (R + D / 2 + 4) * math.cos(tN - tt * k / 10) * sd, BagCz + (R + D / 2 + 4) * math.sin(tN - tt * k / 10)) for sd in (1,) for k in range(11)]
nx = 560
for sd in (1, -1):
    t1 = math.acos(BagCx / (R + D / 2)); t0 = t1 - 0.13
    po = arc_pts(R + D / 2 + 6, sd, t0, t1, 12); pi_ = arc_pts(R - D / 2 - 6, sd, t0 + 0.0, math.acos(BagCx / (R - D / 2)), 12)
    path('M' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in po) + ' L' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in reversed(pi_)) + ' Z', 'rgba(200,50,26,0.18)', RED, 2.2)
line(X(0), Y(Nockhojd - D / 2), X(0), Y(Nockhojd + D / 2), INK, 2)
# nockregel under krönet
rect(X(-22.5), Y(Nockhojd - D / 2), 45 * s, 120 * s, '#d9d4c7', INK, 1.4)
# hanbjälke
xi = -BagCx + math.sqrt((R - D / 2) ** 2 - (ZH - BagCz) ** 2)
rect(X(-xi), Y(ZH + 60), 2 * xi * s, 120 * s, '#f1d9d3', RED, 2.5)
for sd in (1, -1):
    for dz in (-30, 30): a(f'<circle cx="{X(sd * (xi + 60)):.1f}" cy="{Y(ZH + dz):.1f}" r="3.5" fill="{RED}"/>')
# sidoregel (vid inre fläns, på vinkel)
for sd in (1, -1):
    zr = 1900; xr = -BagCx + math.sqrt((R - D / 2) ** 2 - (zr - BagCz) ** 2)
    rect(X(sd * xr) - (34 * s if sd > 0 else 0), Y(zr + 72), 34 * s, 145 * s, '#d9d4c7', INK, 1.2)
# mått
line(X(-HB), Y(-200), X(HB), Y(-200), GREY, 1.2); txt(X(0), Y(-200) + 26, 'Bredd 4 000 (c/c bågfötter)', 18, 'middle', col=GREY)
line(X(-2350), Y(0), X(-2350), Y(Nockhojd), GREY, 1.2); line(X(-2420), Y(Nockhojd), X(-2280), Y(Nockhojd), GREY, 1.2); txt(X(-2350) + 10, Y(Nockhojd / 2), 'Nock 3 500', 18, col=GREY)
line(X(-xi), Y(ZH - 200), X(-xi), Y(ZH), GREY, 1); txt(X(-xi) + 8, Y(ZH - 120), '2 000', 16, col=GREY)
# pekare
tA = tN * 0.55; xA = -BagCx + (R + D / 2) * math.cos(tA); zA = BagCz + (R + D / 2) * math.sin(tA)
leader(X(xA), Y(zA), X(xA) + 120, Y(zA) - 70, 'Lådbåge 230 djup\n(se sektion A–A)', '1')
leader(X(xi * 0.4), Y(ZH), X(xi * 0.4) + 40, Y(ZH) + 120, 'Hanbjälke 45×120 på 2,0 m\n2 × M10 genom båge', '2')
leader(X(250), Y(Nockhojd - 150), X(700), Y(Nockhojd - 330), 'Nock: halvorna stöts mot varandra,\nlask 12 mm plywood på båda sidor\n(limmad + skruv) = stel nock', '3')
leader(X(HB), Y(SyllH + 40), X(HB) + 60, Y(SyllH + 420), 'Bågfot på bredare syll\n2 × 120×120 (detalj 4)', '4')
leader(X(0), Y(Nockhojd - D / 2 - 60), X(0) - 120, Y(Nockhojd - D / 2) + 120, 'Nockregel 45×120 flyttas\nunder krönet (vinklar)', None, anchor='end', col=INK)
line(X(1720), Y(1150), X(2200), Y(1250), RED, 2, '10 6'); txt(X(2210), Y(1260), 'A', 22, w='bold', col=RED)

# ---------- 2. sektion A-A ----------
sx, sy, sw, sh = 1300, 120, 520, 560
frame(sx, sy, sw, sh, '2  SEKTION A–A', '1:4')
k = 1.6; cx0, cy0 = sx + 130, sy + 110
Wt = BB + 2 * WEB
xL = cx0 - Wt / 2 * k
# sidoskivor
rect(xL, cy0, WEB * k, D * k, PLY, INK, 1.6); rect(xL + (WEB + BB) * k, cy0, WEB * k, D * k, PLY, INK, 1.6)
# flänsar 2x15
for yy, lab in ((cy0, 'yttre'), (cy0 + (D - FL) * k, 'inre')):
    rect(xL + WEB * k, yy, BB * k, 15 * k, '#f3dfb0', INK, 1.4); rect(xL + WEB * k, yy + 15 * k, BB * k, 15 * k, '#f3dfb0', INK, 1.4)
# limfogar
for yy in (cy0 + 15 * k,): pass
# skruvar genom sidoskivor
for yy in (cy0 + 15 * k, cy0 + (D - 15) * k):
    for sdx, x0 in ((1, xL - 18), (-1, xL + Wt * k + 18)):
        line(x0 + sdx * 6, yy, x0 + sdx * (WEB + 18) * k, yy, RED, 2.2)
txt(cx0, cy0 - 14, 'film + låsprofil ↑ utsida', 16, 'middle', col=GREY)
lx = xL + Wt * k + 60
leader(xL + (WEB + BB / 2) * k, cy0 + 8, lx, cy0 + 10, 'Fläns 2 × 15×70 plywood,\nlimmade (lameller böjs\nvar för sig)', None)
leader(xL + Wt * k - 4, cy0 + D * k / 2, lx, cy0 + D * k / 2 - 10, 'Sidoskiva 9 mm plywood\nbåda sidor, utsågad båge,\nlim + skruv 4×30 c/c 100', None)
leader(xL + (WEB + BB / 2) * k, cy0 + D * k / 2 + 60, lx, cy0 + D * k / 2 + 100, 'Hålrum. Kloss 70×200\nvid skarvar, hanbjälke\noch bågfot', None)
# mått
line(xL - 50, cy0, xL - 50, cy0 + D * k, GREY, 1.2); txt(xL - 58, cy0 + D * k / 2 + 6, '230', 18, 'end', col=GREY)
line(xL, cy0 + D * k + 30, xL + Wt * k, cy0 + D * k + 30, GREY, 1.2); txt(cx0, cy0 + D * k + 56, '88', 18, 'middle', col=GREY)

# ---------- 3. vindkryss (långsida) ----------
vx, vy, vw, vh = 1300, 700, 1060, 420
frame(vx, vy, vw, vh, '5  LÅNGSIDA – VINDKRYSS I ÄNDFACKEN', 'ca 1:80')
s3 = 0.078; ox3, oy3 = vx + 120, vy + vh - 75
X3 = lambda y: ox3 + y * s3; Y3 = lambda z: oy3 - z * s3
line(X3(-300), Y3(0), X3(L + 300), Y3(0), GREY, 2)
rect(X3(-155), Y3(120), (L + 310) * s3, 120 * s3, '#d9d4c7', INK, 1.2)
n = int(L / CC) + 1
for i in range(n):
    y = i * CC
    rect(X3(y) - 44 * s3, Y3(Nockhojd + 115), 88 * s3, (Nockhojd - 5) * s3, PLY, INK, 1.2)
# sidoregel + nockregel
line(X3(0), Y3(1900), X3(L), Y3(1900), INK, 2.2); line(X3(0), Y3(Nockhojd - 115), X3(L), Y3(Nockhojd - 115), INK, 2.2)
for y0 in (0, L - CC):
    for (z0, z1) in ((120, 1900), (1900, Nockhojd - 115)):
        line(X3(y0), Y3(z0), X3(y0 + CC), Y3(z1), RED, 3); line(X3(y0), Y3(z1), X3(y0 + CC), Y3(z0), RED, 3)
# markskruvar
for i in range(n):
    line(X3(i * CC), Y3(0), X3(i * CC), Y3(-450), INK, 2)
    for zz in range(-60, -450, -70): line(X3(i * CC) - 6, Y3(zz), X3(i * CC) + 6, Y3(zz - 30), INK, 1)
leader(X3(CC / 2), Y3(1000), X3(1.6 * CC), Y3(2900), 'Vindkryss stålband 40×2 vfz\n(spännbart), båda långsidorna\n+ taket, första och sista facket', '5')
leader(X3(6 * CC), Y3(-250), X3(6.2 * CC), Y3(-330), 'Markskruv under varje bågfot (≈ 20 st)', None, col=INK)
txt(X3(L / 2), Y3(-420), '9 bågar c/c 1 250', 16, 'middle', col=GREY)

# ---------- 4. bågfot ----------
bx, by, bw, bh = 1840, 120, 520, 560
frame(bx, by, bw, bh, '4  BÅGFOT', '1:8')
k4 = 0.95; ox4, oy4 = bx + bw / 2, by + 430
X4 = lambda x: ox4 + x * k4; Y4 = lambda z: oy4 - z * k4
rect(X4(-120), Y4(120), 240 * k4, 120 * k4, '#d9d4c7', INK, 1.6); line(X4(0), Y4(120), X4(0), Y4(0), INK, 1)
# båge (sned ner mot syll, nästan lodrät vid foten)
path(f'M{X4(-115):.1f},{Y4(120):.1f} L{X4(115):.1f},{Y4(120):.1f} L{X4(132):.1f},{Y4(330):.1f} L{X4(-98):.1f},{Y4(330):.1f} Z', PLY, INK, 2)
# fotkloss streckad
path(f'M{X4(-85):.1f},{Y4(120):.1f} L{X4(85):.1f},{Y4(120):.1f} L{X4(100):.1f},{Y4(300):.1f} L{X4(-70):.1f},{Y4(300):.1f} Z', 'none', INK, 1.2)
# stålvinklar/sko båda sidor
path(f'M{X4(-140):.1f},{Y4(120):.1f} L{X4(-140):.1f},{Y4(250):.1f} L{X4(-118):.1f},{Y4(250):.1f}', 'none', RED, 4)
path(f'M{X4(140):.1f},{Y4(120):.1f} L{X4(150):.1f},{Y4(250):.1f} L{X4(128):.1f},{Y4(250):.1f}', 'none', RED, 4)
line(X4(-140), Y4(122), X4(140), Y4(122), RED, 4)
# bult genom foten
line(X4(-160), Y4(190), X4(160), Y4(195), RED, 3)
# markskruv
rect(X4(-40), Y4(0) , 80 * k4, 10 * k4, RED, RED, 1)
line(X4(0), Y4(-10), X4(0), Y4(-120), RED, 6)
for zz in range(-20, -120, -22): line(X4(-14), Y4(zz), X4(14), Y4(zz - 10), RED, 1.5)
line(X4(-230), Y4(0), X4(230), Y4(0), GREY, 1.5)
leader(X4(-140), Y4(220), X4(-170), Y4(400), 'Bågfotssko stål 3 mm,\nU-form runt foten', None, anchor='start')
leader(X4(160), Y4(195), X4(175), Y4(270), 'Genomgående\nbult M12', None)
leader(X4(0), Y4(-80), X4(60), Y4(-75), 'Markskruv, syllen\nfäst i dess platta', None)
txt(X4(0), Y4(60) + 6, 'syll 2 × 120×120', 15, 'middle', col=INK)

# ---------- fotnot ----------
ny = 1150
rect(40, ny, 2320, 470, 'none', '#cfcac0', 1.5)
txt(60, ny + 36, 'VARFÖR', 24, w='bold')
rows = [
 'Nuvarande stegbåge (15 + kloss 70 + 15, klossar var 0,5 m) klarar inte snö (utnyttjande ≈ 7) och viker sig i vind: remsorna böjs var för sig mellan klossarna.',
 'Lådbåge: sidoskivorna limmas mot flänsarna så att hela djupet samverkar – och 230 mm djup med dubbla flänsar ger ca 15× styvheten.',
 'Hanbjälken tar en del av vindens snedlast; stel nock och vindkryss stabiliserar huset i längsled; markskruvarna tar lyftet (≈ 3 kN per fot).',
 'Räknat: 230 mm + hanbjälke, c/c 1 250 → utnyttjande ≈ 0,33 snö / 1,2–1,35 vind enligt Eurocode (50 års vind).',
 'Med växthusstandarden EN 13031-1 (kortare livslängd, ~30–40 % lägre last) → ca 0,8–0,95 = OK. Vill vi klara full Eurocode: 330 mm djup och c/c 900 (0,82).',
 'Ändringar i modellen: BagDjup 100 → 230, PlyT → 2 lameller, nya sidoskivor + hanbjälke + vindkryss + bredare syll; klossarna blir bara vid skarvar och fot.',
]
for i, r in enumerate(rows):
    bubble(76, ny + 82 + i * 62, str(i + 1), INK if i < 3 else RED)
    txt(106, ny + 89 + i * 62, r, 20)
a('</svg>')
p = os.path.join(HERE, 'skiss_losning.svg'); open(p, 'w').write('\n'.join(out))
subprocess.run(['rsvg-convert', '-w', str(W), '-o', os.path.join(HERE, 'skiss_losning.png'), p], check=True)
print('ok', p)
