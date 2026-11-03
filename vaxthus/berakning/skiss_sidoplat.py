#!/usr/bin/env python3
"""Skiss alt 1: bågformade sidoplåtar 3 mm stål (vattenskurna) i bågens momentzon. -> skiss_sidoplat.svg/.png (+ sidoplat.dxf-förslag)"""
import math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
Bredd, Nockhojd, SyllH = 4000.0, 3500.0, 120.0
HB = Bredd / 2; BH = Nockhojd - SyllH
BagCx = (BH * BH - HB * HB) / (2 * HB); BagCz = SyllH; R = BagCx + HB
D, FL, BB = 230.0, 30.0, 70.0          # bågdjup, fläns 2x15, bågbredd
T = 3.0                                 # plåt
S0, S1 = 800.0, 3000.0                  # plåtzon längs mittlinjen från foten
INS = 5.0                               # plåten 5 mm innanför bågens ytter- och innerkant
PH = D - 2 * INS                        # plåthöjd 220
BCC = 150.0                             # bultdelning
ROWS = (D / 2 - FL / 2, -(D / 2 - FL / 2))   # bultrader mitt i flänsarna (radiellt från mittlinjen)
nb = int(round((S1 - S0 - 2 * 50) / BCC)) + 1
W, H = 2400, 1650
INK, GREY, RED, PLY, STEEL = '#1d1d1b', '#8a8a86', '#c8321a', '#e8cf9c', '#b9bec4'
out = []
def a(s): out.append(s)
def txt(x, y, s, size=20, anchor='start', w='normal', col=INK):
    a(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Barlow, Helvetica, Arial" font-size="{size}" font-weight="{w}" fill="{col}" stroke="white" stroke-width="5" stroke-linejoin="round" paint-order="stroke" text-anchor="{anchor}">{s}</text>')
def line(x1, y1, x2, y2, col=INK, w=2.0, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{da}/>')
def rect(x, y, w, h, fill='none', col=INK, sw=2.0):
    a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
def path(d, fill='none', col=INK, sw=2.0, op=1.0):
    a(f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>')
def circ(x, y, r, fill='white', col=INK, sw=1.5):
    a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
def bubble(x, y, n, col=RED):
    circ(x, y, 17, 'white', col, 2.5); txt(x, y + 7, n, 20, 'middle', 'bold', col)
def leader(x1, y1, x2, y2, label, n=None, anchor='start', col=RED):
    line(x1, y1, x2, y2, col, 1.6); circ(x1, y1, 3.5, col, col, 1)
    if n: bubble(x2 + (18 if anchor == 'start' else -18), y2, n, col); x2 += 40 if anchor == 'start' else -40
    for i, s in enumerate(label.split('\n')): txt(x2 + (4 if anchor == 'start' else -4), y2 + 7 + i * 24, s, 19, anchor)
def frame(x, y, w, h, title, scale):
    rect(x, y, w, h, 'none', '#cfcac0', 1.5); txt(x + 16, y + 32, title, 24, w='bold'); txt(x + w - 16, y + 32, scale, 18, 'end', col=GREY)

def P(s, r):   # punkt på höger halvbåge: s längs mittlinjen från foten, r radiellt från mittlinjen (+ utåt)
    th = s / R; return (-BagCx + (R + r) * math.cos(th), BagCz + (R + r) * math.sin(th))
def band(s0, s1, r0, r1, n=60):
    pts = [P(s0 + (s1 - s0) * k / n, r1) for k in range(n + 1)] + [P(s1 - (s1 - s0) * k / n, r0) for k in range(n + 1)]
    return pts
sN = R * math.acos(BagCx / R)

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'); a(f'<rect width="{W}" height="{H}" fill="white"/>')
txt(40, 62, 'VÄXTHUS – ALT 1: BÅGFORMADE SIDOPLÅTAR 3 MM STÅL', 40, w='bold')
txt(40, 96, f'Vattenskurna plåtar på båda sidor av bågen där vindmomentet är störst ({S0/1000:.1f}–{S1/1000:.1f} m längs bågen från foten), genombultade. Skiss – inte arbetsritning.', 20, col=GREY)

# ---- 1. halvbåge ----
fx, fy, fw, fh = 40, 120, 1180, 1000
frame(fx, fy, fw, fh, '1  HALVBÅGE, SIDA', 'ca 1:20')
s = 0.225; ox, oy = fx + 120, fy + fh - 70
X = lambda x: ox + x * s; Y = lambda z: oy - z * s
line(X(-200), Y(0), X(2600), Y(0), GREY, 2)
for xx in range(-200, 2600, 90): line(X(xx), Y(0), X(xx - 60), Y(-60), GREY, 1)
def pd(pts): return 'M' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in pts) + ' Z'
rect(X(HB - 120), Y(SyllH), 240 * s, SyllH * s, '#d9d4c7', INK, 1.6)
path(pd(band(0, sN, -D / 2, D / 2, 120)), PLY, INK, 2)
for r_ in (D / 2 - FL, -D / 2 + FL):
    p = [P(sN * k / 120, r_) for k in range(121)]; path('M' + ' L'.join(f'{X(x):.1f},{Y(z):.1f}' for x, z in p), 'none', INK, 0.9)
# klossar c/c 200 (streckade)
k = 0
while k * 200 + 60 < sN:
    sc = k * 200 + 60
    for ds in (-35, 35):
        x1, z1 = P(sc + ds, -D / 2 + FL); x2, z2 = P(sc + ds, D / 2 - FL); line(X(x1), Y(z1), X(x2), Y(z2), GREY, 0.8, '3 3')
    k += 1
# plåt
path(pd(band(S0, S1, -PH / 2, PH / 2)), STEEL, RED, 2.6, 0.85)
for r_ in ROWS:
    for i in range(nb):
        x, z = P(S0 + 50 + i * BCC, r_); circ(X(x), Y(z), 3.2, 'white', INK, 1.4)
# hanbjälke + nock antydan
zh = 2000; xi = -BagCx + math.sqrt((R - D / 2) ** 2 - (zh - BagCz) ** 2)
rect(X(0), Y(zh + 60), xi * s, 120 * s, '#f1d9d3', INK, 1.4); txt(X(xi / 2), Y(zh + 60) - 8, 'hanbjälke', 15, 'middle', col=GREY)
line(X(0), Y(Nockhojd - 200), X(0), Y(Nockhojd + 200), GREY, 1, '8 6'); txt(X(0) + 8, Y(Nockhojd + 150), '← husets mitt / nock', 16, col=GREY)
# mått längs bågen
for sv, lab in ((S0, f'{S0/1000:.1f} m'), (S1, f'{S1/1000:.1f} m')):
    x1, z1 = P(sv, D / 2 + 20); x2, z2 = P(sv, D / 2 + 140)
    line(X(x1), Y(z1), X(x2), Y(z2), GREY, 1.2); txt(X(x2) + 8, Y(z2) - 4, lab + ' längs bågen', 16, col=GREY)
xm, zm = P((S0 + S1) / 2, 0)
leader(X(xm), Y(zm), X(xm) + 230, Y(zm) - 160, f'Sidoplåt 3 mm stål, båda sidor\n{PH:.0f} hög, båglängd {(S1-S0)/1000:.1f} m\nvarmförzinkad efter skärning', '1')
x1, z1 = P(S0 + 50 + 4 * BCC, ROWS[0])
leader(X(x1), Y(z1), X(x1) + 300, Y(z1) + 40, f'Bult M10 genom plåt–fläns–plåt\n2 rader c/c {BCC:.0f} ({2*nb} st per halvbåge)', '2')
x1, z1 = P(400, 0)
leader(X(x1), Y(z1), X(x1) + 170, Y(z1) - 40, 'Båge 230: fläns 2×15 K20/70,\nklossar c/c 200 (oförändrat)', None, col=INK)
leader(X(HB), Y(SyllH + 30), X(HB) + 110, Y(SyllH + 250), 'U-sko + markskruv\n(som tidigare förslag)', None, col=INK)

# ---- 2. sektion ----
sx, sy, sw, sh = 1240, 120, 560, 600
frame(sx, sy, sw, sh, '2  SEKTION GENOM PLÅTZONEN', '1:4')
k2 = 1.55; cx0, cy0 = sx + 170, sy + 120
Wt = BB + 2 * T; xL = cx0 - Wt / 2 * k2
# plywood
rect(xL + T * k2, cy0, BB * k2, FL * k2, '#f3dfb0', INK, 1.4); line(xL + T * k2, cy0 + 15 * k2, xL + (T + BB) * k2, cy0 + 15 * k2, INK, 0.8)
rect(xL + T * k2, cy0 + (D - FL) * k2, BB * k2, FL * k2, '#f3dfb0', INK, 1.4); line(xL + T * k2, cy0 + (D - 15) * k2, xL + (T + BB) * k2, cy0 + (D - 15) * k2, INK, 0.8)
rect(xL + T * k2, cy0 + FL * k2, BB * k2, (D - 2 * FL) * k2, 'none', GREY, 1, ) ; txt(cx0, cy0 + D * k2 / 2 + 6, 'kloss c/c 200', 15, 'middle', col=GREY)
# plåtar
for xx in (xL, xL + (T + BB) * k2):
    rect(xx, cy0 + INS * k2, T * k2, PH * k2, STEEL, RED, 2)
# bultar
for yy in (cy0 + FL / 2 * k2, cy0 + (D - FL / 2) * k2):
    line(xL - 22, yy, xL + Wt * k2 + 22, yy, INK, 3.2)
    rect(xL - 30, yy - 9, 8, 18, INK, INK, 1); rect(xL + Wt * k2 + 22, yy - 9, 8, 18, INK, INK, 1)
txt(cx0, cy0 - 14, 'film/plast ↑ utsida', 16, 'middle', col=GREY)
lx = xL + Wt * k2 + 80
leader(xL + (T + BB) * k2 + 2, cy0 + 70 * k2, lx, cy0 + 60, 'Sidoplåt 3 mm\n5 mm innanför bågens kanter\n(filmen ligger fritt på flänsen)', '1')
leader(xL + Wt * k2 + 26, cy0 + FL / 2 * k2, lx, cy0 + 200, 'M10 + stora brickor,\nmitt i flänsen (70 mm trä)', '2')
leader(xL + T * k2 + 30, cy0 + (D - 8) * k2, lx, cy0 + 330, 'Inre fläns 2×15 limmad', None, col=INK)
line(xL - 55, cy0, xL - 55, cy0 + D * k2, GREY, 1.2); txt(xL - 62, cy0 + D * k2 / 2, '230', 18, 'end', col=GREY)
line(xL, cy0 + D * k2 + 30, xL + Wt * k2, cy0 + D * k2 + 30, GREY, 1.2); txt(cx0, cy0 + D * k2 + 56, f'{Wt:.0f}', 18, 'middle', col=GREY)

# ---- 3. skärbild ----
px, py, pw, ph = 1820, 120, 540, 600
frame(px, py, pw, ph, '3  PLÅT, PLAN (SKÄRFIL)', 'ca 1:15')
th0, th1 = S0 / R, S1 / R; ri, ro = R - PH / 2, R + PH / 2
# rotera så att kordan blir vågrät
mid = (th0 + th1) / 2
def Q(r, th): return (r * math.sin(th - mid), r * math.cos(th - mid))
pts = [Q(ro, th0 + (th1 - th0) * k / 60) for k in range(61)] + [Q(ri, th1 - (th1 - th0) * k / 60) for k in range(61)]
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
k3 = 0.215; cxp = px + pw / 2; cyp = py + 120
TX = lambda x: cxp + x * k3; TY = lambda y: cyp + (max(ys) - y) * k3
path('M' + ' L'.join(f'{TX(x):.1f},{TY(y):.1f}' for x, y in pts) + ' Z', STEEL, RED, 2.2, 0.85)
for r_ in ROWS:
    for i in range(nb):
        x, y = Q(R + r_, (S0 + 50 + i * BCC) / R); circ(TX(x), TY(y), 2.2, 'white', INK, 1.1)
bw = max(xs) - min(xs); bh = max(ys) - min(ys)
line(TX(min(xs)), TY(min(ys)) + 30, TX(max(xs)), TY(min(ys)) + 30, GREY, 1.2); txt(cxp, TY(min(ys)) + 56, f'{bw:.0f}', 18, 'middle', col=GREY)
line(TX(max(xs)) + 20, TY(max(ys)), TX(max(xs)) + 20, TY(min(ys)), GREY, 1.2); txt(TX(max(xs)) + 26, (TY(max(ys)) + TY(min(ys))) / 2, f'{bh:.0f}', 18, col=GREY)
area = (th1 - th0) / 2 * (ro ** 2 - ri ** 2) / 1e6; kg = area * T / 1000 * 7850
yy = TY(min(ys)) + 100
for i, r in enumerate([f'Ytterradie R {ro:.0f}, innerradie R {ri:.0f}', f'Hål Ø11, {2*nb} st, delning {BCC:.0f} längs bågen',
                       f'Yta {area:.2f} m², vikt ≈ {kg:.1f} kg', 'Spegelvänd plåt till andra sidan (samma fil)',
                       f'Plåt {bw:.0f} × {bh:.0f} → 3–4 st per 1500×3000-skiva']):
    txt(px + 24, yy + i * 30, r, 18)

# ---- 4. sammanställning ----
ny = 740
rect(1240, ny, 1120, 380, 'none', '#cfcac0', 1.5)
txt(1256, ny + 34, '4  MÄNGD OCH EFFEKT (uppskattning, ej beräknad)', 24, w='bold')
nh = 18
rows = [f'Plåtar: 2 per halvbåge × {nh} halvbågar = {2*nh} st, ca {2*nh*kg:.0f} kg stål ({12} skivor 1500×3000×3)',
        f'Bultar M10 × 100 + 2 brickor + mutter: {2*nb} per halvbåge = {2*nb*nh} st',
        'Stålet är ~30× styvare än plywood: två plåtar 3×220 ≈ 4× flänsarnas böjstyvhet',
        '→ vinden tas med god marginal i plåtzonen; utanför den räcker plywoodbågen',
        'Kan troligen gå ner i bågdjup (t.ex. 160) – kräver beräkning',
        'Plåtändarna ska ligga där momentet är litet; exakt zon bestäms i beräkningen']
for i, r in enumerate(rows): txt(1256, ny + 80 + i * 44, '• ' + r, 19)

# fotnot
rect(40, 1140, 2320, 470, 'none', '#cfcac0', 1.5)
txt(60, 1176, 'MONTERING', 24, w='bold')
steps = ['Bygg plywoodbågen som förut (flänsar 2×15 limmade, klossar c/c 200).',
         'Lägg en plåt mot bågens sida i zonen, märk och borra Ø11 genom bågen med plåten som mall.',
         'Montera plåten på andra sidan, bulta M10 med stora brickor – dra efter efter en säsong (träet krymper).',
         'Plåtarna varmförzinkas eller målas innan montering; skär hålen före förzinkning.',
         'Filmens låsprofil sitter på flänsens utsida som förut – plåtarna går fria 5 mm innanför kanten.',
         'Gavelbågarna: plåten på insidan + mot gaveln, eller bara insidan om gavelns stomme stöttar.']
for i, r in enumerate(steps): bubble(76, 1222 + i * 62, str(i + 1), INK); txt(106, 1229 + i * 62, r, 20)
a('</svg>')
p = os.path.join(HERE, 'skiss_sidoplat.svg'); open(p, 'w').write('\n'.join(out))
subprocess.run(['rsvg-convert', '-w', str(W), '-o', os.path.join(HERE, 'skiss_sidoplat.png'), p], check=True)
print('ok', round(kg, 1), 'kg/plåt', nb, 'bultar/rad', round(bw), round(bh))
