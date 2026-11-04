#!/usr/bin/env python3
"""Verkstadsritning A3 (PDF): 1) färdig halvbåge måttsatt, 2) plywoodremsor kapplista + skivplan, 3) klossar + nocklask.
Parametrar som i Fusion-modellen (v11_antal.json). Skriver ritning_bage.pdf (+ svg/png per sida)."""
import json, math, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, '..', 'fusion', 'v11_antal.json'), encoding='utf-8'))['parametrar']
INK, GREY, RED, PLY, PLY2, WOOD, LIGHT = '#1d1d1b', '#8a8a86', '#c8321a', '#ecd6a6', '#d9b77a', '#c9a46b', '#f4f1ea'
# ---------------- geometri ----------------
Bredd, Nockhojd, SyllH = P['Bredd'], P['Nockhojd'], P['SyllH']
NockT = P['NockT']; HB = Bredd / 2; BH = Nockhojd - SyllH
cx = (BH * BH - HB * HB) / (2 * HB); R = cx + HB
LT = P['LamellT']; NL = int(P['Lameller']); PT = LT * NL; KH = P['KlossH']; D = 2 * PT + KH; BB = P['BagB']
ri, ro = R - D / 2, R + D / 2
XN = NockT / 2                          # nockkapets x (husets mitt = 0)
def th_end(r): return math.acos((XN + cx) / r)
def pt(r, th): return (-cx + r * math.cos(th), r * math.sin(th))          # lokalt: z från fotens underkant
KL, FKL, CCmax = P['KlossL'], P['FackKlossL'], 450.0
SRH, SRT, SPEL = P['SidoregelH'], P['SidoregelT'], 2.5
BL = R * th_end(R)
FackS = R * math.asin((1900 - SyllH) / R); Gp = SRH + 2 * SPEL
FotS = KL / 2; FNs = FackS - Gp / 2 - FKL / 2; FOs = FackS + Gp / 2 + FKL / 2; NockS = BL - KL / 2
nm = max(1, math.ceil((FNs - FKL / 2 - FotS - KL / 2) / CCmax) - 1); npch = (FNs - FotS - (FKL - KL) / 2) / (nm + 1)
om = max(1, math.ceil((NockS - KL / 2 - FOs - FKL / 2) / CCmax) - 1); opch = (NockS - FOs - (FKL - KL) / 2) / (om + 1)
KLS = [(0.0, KL)] + [(FotS + (k + 1) * npch - KL / 2, KL) for k in range(nm)] + [(FNs - FKL / 2, FKL), (FOs - FKL / 2, FKL)]
o0 = FOs + (FKL - KL) / 2
KLS += [(o0 + (k + 1) * opch - KL / 2, KL) for k in range(om)] + [(BL - KL, KL)]
NKL = len(KLS)
# lager (1 = innerst) radier
LAG = [(ri + k * LT, ri + (k + 1) * LT) for k in range(NL)] + [(ro - PT + k * LT, ro - PT + (k + 1) * LT) for k in range(NL)]
OVER = 25.0                                  # övermått per ände, kapas efter limning
SKIVA_L, SKIVA_B, KERF = 2500.0, 1200.0, 3.0
def lag_L(r0, r1): rm = (r0 + r1) / 2; return rm * th_end(rm)
Lmax = max(lag_L(*l) for l in LAG)
lo, hi = Lmax + 2 * OVER - SKIVA_L + 5, SKIVA_L - 2 * OVER - 5
J3 = [lo + (hi - lo) * k / (NL - 1) for k in range(NL)]
JOINT = [round(j / 5) * 5 for j in J3] + [round(j / 5) * 5 for j in reversed(J3)]   # inner 1..3, ytter 1..3 (ytterst kortast A)
# hanbjälke + bultar
HanZ, HanH = P['HanZ'] - SyllH, P['HanH']
def x_at(r, z): return -cx + math.sqrt(r * r - z * z)
HanX = x_at(ro, HanZ + HanH / 2)
BULT = [(x_at(ri + PT / 2, HanZ - 30), HanZ - 30), (x_at(ri + PT / 2, HanZ + 30), HanZ + 30)]   # båda genom innerflänsen (ytterflänsen ligger utanför hanbjälkens ände)
# nocklask, raka snitt
LAV = P.get('ProfilH', 13.0) + 10.0
rr = ro - LAV; LX = P['NockLaskL'] / 2
def zc(r, x): return math.sqrt(r * r - (x + cx) ** 2)
sag = LX ** 2 / (8 * ri)
LASK = [(-LX, zc(rr, LX)), (0, zc(rr, 0)), (LX, zc(rr, LX)), (LX, zc(ri, LX) + sag), (0, zc(ri, 0) + sag), (-LX, zc(ri, LX) + sag)]

# ---------------- svg i mm ----------------
class Sheet:
    def __init__(s, W=420, H=297):
        s.W, s.H = W, H
        s.o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>']
    def a(s, x): s.o.append(x)
    def t(s, x, y, txt, sz=3.2, anc='start', w='normal', col=INK, rot=0.0):
        tr = f' transform="rotate({rot:.2f} {x:.2f} {y:.2f})"' if rot else ''
        s.a(f'<text x="{x:.2f}" y="{y:.2f}" font-family="Barlow, Helvetica, Arial" font-size="{sz}" font-weight="{w}" fill="{col}" text-anchor="{anc}" stroke="white" stroke-width="{sz * 0.28:.2f}" paint-order="stroke"{tr}>{txt}</text>')
    def l(s, x1, y1, x2, y2, col=INK, w=0.25, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{w}"{da}/>')
    def r(s, x, y, w, h, fill='none', col=INK, sw=0.25):
        s.a(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    def p(s, pts, fill='none', col=INK, sw=0.25, close=True, dash=None):
        d = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + (' Z' if close else '')
        da = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"{da}/>')
    def c(s, x, y, rad, fill='white', col=INK, sw=0.25): s.a(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rad:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    def bub(s, x, y, n, col=RED, rad=2.4): s.c(x, y, rad, 'white', col, 0.3); s.t(x, y + 1.1, n, 3.0, 'middle', 'bold', col)
    def dim(s, p1, p2, off, txt=None, sz=2.8, col=INK):
        """måttlinje parallell med p1-p2, förskjuten off (mm på papper, + = vänster om p1->p2)"""
        (x1, y1), (x2, y2) = p1, p2; L = math.hypot(x2 - x1, y2 - y1)
        if L < 1e-6: return
        ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
        a1 = (x1 + nx * off, y1 + ny * off); a2 = (x2 + nx * off, y2 + ny * off)
        sg = 1 if off >= 0 else -1
        s.l(x1 + nx * sg * 1, y1 + ny * sg * 1, a1[0] + nx * sg * 1.5, a1[1] + ny * sg * 1.5, col, 0.15)
        s.l(x2 + nx * sg * 1, y2 + ny * sg * 1, a2[0] + nx * sg * 1.5, a2[1] + ny * sg * 1.5, col, 0.15)
        s.l(*a1, *a2, col, 0.2)
        for (ax, ay) in (a1, a2):
            s.l(ax - (ux + nx) * 1.1, ay - (uy + ny) * 1.1, ax + (ux + nx) * 1.1, ay + (uy + ny) * 1.1, col, 0.35)
        ang = math.degrees(math.atan2(uy, ux))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        mx, my = (a1[0] + a2[0]) / 2 + nx * sg * 0.9, (a1[1] + a2[1]) / 2 + ny * sg * 0.9
        s.t(mx, my, txt, sz, 'middle', col=col, rot=ang)
    def frame(s, title, sub, blad):
        s.r(8, 8, s.W - 16, s.H - 16, 'none', INK, 0.5)
        s.r(s.W - 128, s.H - 30, 120, 22, 'white', INK, 0.4)
        s.t(s.W - 124, s.H - 22, title, 4.2, w='bold'); s.t(s.W - 124, s.H - 16.5, sub, 2.8, col=GREY)
        s.t(s.W - 124, s.H - 11.5, f'Växthus buttercup · båge B · mått i mm · {blad}', 2.8)
    def save(s, name):
        s.a('</svg>'); sv = os.path.join(HERE, name + '.svg'); open(sv, 'w', encoding='utf-8').write('\n'.join(s.o))
        subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', os.path.join(HERE, name + '.pdf'), sv], check=True)
        subprocess.run(['rsvg-convert', '-d', '150', '-p', '150', '-o', os.path.join(HERE, name + '.png'), sv], check=True)
        return os.path.join(HERE, name + '.pdf')

def arcpts(r, t0, t1, n=60): return [pt(r, t0 + (t1 - t0) * k / n) for k in range(n + 1)]
def band(r0, r1, t0, t1, n=40): return arcpts(r1, t0, t1, n) + list(reversed(arcpts(r0, t0, t1, n)))

# ======================= BLAD 1: halvbåge =======================
S = Sheet()
S.frame('HALVBÅGE – FÄRDIG', f'18 st (2 per båge). Limmas en och en i mallen.', 'blad 1/3')
sc = 1 / 15.0; ox, oy = 28, 272
X = lambda x: ox + x * sc; Y = lambda z: oy - z * sc
T = lambda pts: [(X(x), Y(z)) for x, z in pts]
S.t(14, 18, 'HALVBÅGE, SIDA (sett från husets insida, +y)  1:15', 4.0, w='bold')
# flänsar + lager
for k, (a, b) in enumerate(LAG):
    j = JOINT[k]; rm = (a + b) / 2; tj = j / rm
    S.p(T(band(a, b, 0, min(tj, th_end(a)))), PLY, INK, 0.12)
    S.p(T([(max(x, XN), z) for x, z in band(a, b, tj, th_end(a))]), PLY, INK, 0.12)
for i, (s0, L) in enumerate(KLS):
    poly = band(ri + PT, ro - PT, s0 / R, min(th_end(ri + PT), (s0 + L) / R), 4)
    poly = [(max(x, XN), z) for x, z in poly]
    S.p(T(poly), PLY2, INK, 0.2)
    mx, mz = pt(R, (s0 + L / 2) / R)
    S.bub(X(mx) - 11 * math.cos((s0 + L / 2) / R) * 0 - 9, Y(mz) + 0, str(i + 1)) if False else None
# konturer
S.p(T(arcpts(ri, 0, th_end(ri))), 'none', INK, 0.4, close=False); S.p(T(arcpts(ro, 0, th_end(ro))), 'none', INK, 0.4, close=False)
S.l(X(x_at(ri, 0)), Y(0), X(x_at(ro, 0)), Y(0), INK, 0.4)
S.l(X(XN), Y(zc(ri, XN)), X(XN), Y(zc(ro, XN)), INK, 0.4)
# kloss-bubblor utanför ytterkanten
for i, (s0, L) in enumerate(KLS):
    th = (s0 + L / 2) / R; bx, bz = pt(ro + 230, th); kx, kz = pt(ro - PT - KH / 2, th)
    S.l(X(kx), Y(kz), X(bx), Y(bz), RED, 0.15); S.bub(X(bx), Y(bz), str(i + 1))
# fack + sidoregel (streckad)
zf = 1900 - SyllH; xf = x_at(R, zf)
thf = math.asin(zf / R)
S.p(T([(x_at(R, zf) - math.sin(thf) * 0 + dx, zf + dz) for dx, dz in []]), 'none') if False else None
srx, srz = pt(R, thf)
ux, uz = math.cos(thf), math.sin(thf); tx, tz = -math.sin(thf), math.cos(thf)
sr = [(srx + ux * a + tx * b, srz + uz * a + tz * b) for a, b in ((-SRT / 2, -SRH / 2), (SRT / 2, -SRH / 2), (SRT / 2, SRH / 2), (-SRT / 2, SRH / 2))]
S.p(T(sr), '#ffffff', RED, 0.25, dash='0.8 0.5')
# hanbjälke (streckad, ligger på +y-sidan) + bulthål
S.p(T([(HanX - 900, HanZ - HanH / 2), (HanX, HanZ - HanH / 2), (HanX, HanZ + HanH / 2), (HanX - 900, HanZ + HanH / 2)]), 'none', RED, 0.25, close=False, dash='1.2 0.6')
for bx, bz in BULT: S.c(X(bx), Y(bz), 10 * sc / 2 + 0.25, 'white', RED, 0.3)
# nocklask (streckad)
S.p(T([(max(x, XN), z) for x, z in LASK if x >= 0] + []), 'none', RED, 0.25, dash='1.2 0.6') if False else None
S.p(T([(XN, LASK[1][1] - (LASK[1][1] - zc(rr, XN)) * 0), (LX, LASK[2][1]), (LX, LASK[3][1]), (XN, zc(ri, XN) + sag)]), 'none', RED, 0.3, dash='1.2 0.6')
# centrum
S.c(X(-cx), Y(0), 0.8, INK, INK) if X(-cx) > 10 else None
# ---- mått ----
fi, fo = x_at(ri, 0), x_at(ro, 0)
zni, zno = zc(ri, XN), zc(ro, XN)
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
S.t(X(HanX - 880), Y(HanZ + HanH / 2) - 1.2, 'hanbjälke (monteras efter limning)', 2.5, col=RED)
S.t(X(srx) + 4, Y(srz) + 1, 'sidoregel', 2.5, col=RED)
S.dim((X(XN), Y(LASK[2][1] + 40)), (X(LX), Y(LASK[2][1] + 40)), 5, f'lask {LX - XN:.0f}', 2.4)
# radietexter
lx, lz = pt(ri, 0.62); S.l(X(lx), Y(lz), X(lx) - 30, Y(lz) + 8, INK, 0.15); S.t(X(lx) - 31, Y(lz) + 9, f'R {ri:.0f} insida', 3.0, 'end', w='bold')
lx, lz = pt(ro, 0.85); S.l(X(lx), Y(lz), X(lx) + 40, Y(lz) - 6, INK, 0.15); S.t(X(lx) + 41, Y(lz) - 5.4, f'R {ro:.0f} utsida', 3.0, w='bold')
S.t(X(110), Y(-160), f'Cirkelns centrum: {cx:.0f} bortom husets mitt, i fotens nivå (andra halvans sida).', 2.7, col=GREY)
# ---- tabell klossar ----
tx0, ty0 = 200, 22
S.t(tx0, ty0, 'KLOSSAR – läge mätt längs YTTERKANTEN från foten (måttband på bågen)', 3.4, w='bold')
cols = ['nr', 'typ', 'längd', 'från', 'till', 'insida från', 'insida till']
cxs = [0, 8, 40, 56, 74, 92, 114]
for c_, x_ in zip(cols, cxs): S.t(tx0 + x_, ty0 + 6, c_, 2.8, w='bold')
for i, (s0, L) in enumerate(KLS):
    typ = 'fot' if i == 0 else 'nock' if i == NKL - 1 else 'fack' if L == FKL else 'kloss'
    so0, so1 = s0 * ro / R, (s0 + L) * ro / R; si0, si1 = s0 * ri / R, (s0 + L) * ri / R
    row = [str(i + 1), typ, f'{L:.0f}', f'{so0:.0f}', f'{so1:.0f}', f'{si0:.0f}', f'{si1:.0f}']
    for v, x_ in zip(row, cxs): S.t(tx0 + x_, ty0 + 11 + i * 4.2, v, 2.8)
yy = ty0 + 11 + NKL * 4.2 + 1
S.t(tx0, yy, f'Fack för sidoregel {SRT:.0f}×{SRH:.0f} mellan kloss 4 och 5 = {Gp:.0f} fritt ({SPEL} spel/sida).', 2.7)
S.t(tx0, yy + 4, f'Ytterkantens totala längd fot → nock ≈ {ro * th_end(ro):.0f}, insidans ≈ {ri * th_end(ri):.0f}.', 2.7)
S.t(tx0, yy + 8, 'Nockklossens övre ände kapas lodrätt med flänsarna (29° mot radien).', 2.7)
# ---- snitt A-A ----
ax0, ay0, s3 = 200, 104, 0.5
S.t(ax0, ay0 - 4, 'SNITT A-A (genom kloss)  1:2', 3.4, w='bold')
x = ax0
for k, (th_, col_, lab_) in enumerate([(LT, PLY, '')] * NL + [(KH, PLY2, '')] + [(LT, PLY, '')] * NL):
    S.r(x, ay0, th_ * s3, BB * s3, col_, INK, 0.2); x += th_ * s3
S.dim((ax0, ay0 + BB * s3), (ax0 + D * s3, ay0 + BB * s3), -5, f'{D:.0f} bågdjup')
S.dim((ax0, ay0 + BB * s3), (ax0 + PT * s3, ay0 + BB * s3), -10, f'{PT:.0f}', 2.4)
S.dim((ax0 + PT * s3, ay0 + BB * s3), (ax0 + (PT + KH) * s3, ay0 + BB * s3), -10, f'{KH:.0f}', 2.4)
S.dim((ax0 + D * s3, ay0), (ax0 + D * s3, ay0 + BB * s3), -5, f'{BB:.0f}')
S.t(ax0, ay0 + BB * s3 + 18, f'innerfläns {NL} × {LT:.0f} plywood (lager 1–{NL}, 1 innerst)', 2.7)
S.t(ax0, ay0 + BB * s3 + 22.5, f'kloss 2 × {LT:.0f} plywood, limmad + 2 skruv 5×90 utifrån', 2.7)
S.t(ax0, ay0 + BB * s3 + 27, f'ytterfläns {NL} × {LT:.0f} plywood (lager 4–6, 6 ytterst)', 2.7)
S.t(ax0, ay0 + BB * s3 + 31.5, 'PU-lim i alla fogar, pressas med kilar i mallen', 2.7)
S.t(ax0, ay0 + BB * s3 + 36, f'Skarvar: se blad 2 (lager i olika lägen, ≈ {(J3[1] - J3[0]):.0f} isär)', 2.7)
# ---- hel båge 1:50 ----
hx0, hy0, s4 = 345, 184, 1 / 50
S.t(hx0 - 50, hy0 - 82, 'HEL BÅGE (2 halvor) 1:50', 3.4, w='bold')
for sd in (1, -1):
    S.p([(hx0 + sd * x * s4, hy0 - z * s4) for x, z in arcpts(ro, 0, th_end(ro))] + [(hx0 + sd * x * s4, hy0 - z * s4) for x, z in reversed(arcpts(ri, 0, th_end(ri)))], PLY, INK, 0.2)
S.r(hx0 - HanX * s4, hy0 - (HanZ + HanH / 2) * s4, 2 * HanX * s4, HanH * s4, WOOD, INK, 0.2)
S.dim((hx0 - Bredd / 2 * s4, hy0), (hx0 + Bredd / 2 * s4, hy0), -6, f'{Bredd:.0f} mittlinje fot')
S.dim((hx0 - x_at(ro, 0) * s4, hy0), (hx0 + x_at(ro, 0) * s4, hy0), -11, f'{2 * x_at(ro, 0):.0f} utsida')
S.dim((hx0 + 55, hy0), (hx0 + 55, hy0 - zno * s4), -3, f'{zno:.0f}', 2.4)
S.t(hx0 + 50, hy0 - zno * s4 - 3, f'+ syll {SyllH:.0f} = nock {zno + SyllH:.0f}', 2.4, 'end', col=GREY)
S.t(hx0, hy0 - (HanZ + HanH) * s4 - 1.5, f'hanbjälke 45×120 × {2 * HanX:.0f}', 2.5, 'middle')
S.t(hx0, hy0 - zno * s4 - 5, f'nockklots/glipa {NockT:.0f} + lask {2 * LX:.0f} båda sidor', 2.5, 'middle')
# noter
nx0, ny0 = 210, 214
notes = ['ANMÄRKNINGAR',
         f'Foten kapas vågrätt (= radiellt), nocken lodrätt. Flänsarna limmas med {OVER:.0f} mm övermått i båda ändar.',
         f'Hanbjälke: 2 bulthål Ø11 genom innerflänsen på {HanZ - 30:.0f} och {HanZ + 30:.0f} över foten,',
         f'  x = {BULT[0][0]:.0f} och {BULT[1][0]:.0f} från husets mitt. Hanbjälkens ände kapas lodrätt i x = {HanX:.0f}.',
         'Gavelbågar (4 halvor): ingen hanbjälke, nocklask bara på insidan.',
         'Röd streckad = delar som monteras senare (sidoregel, hanbjälke, nocklask).',
         'Kontroll: två halvor ihop = 4000 c/c fot (mittlinjen), utsida ' + f'{2 * x_at(ro, 0):.0f}.']
for i, n_ in enumerate(notes): S.t(nx0, ny0 + i * 4.6, n_, 3.0 if i == 0 else 2.7, w='bold' if i == 0 else 'normal')
p1 = S.save('ritning_bage_1')

# ======================= BLAD 2: remsor =======================
S = Sheet()
S.frame('PLYWOODREMSOR', 'Kapplista per halvbåge + skivplan', 'blad 2/3')
S.t(14, 18, f'REMSOR {BB:.0f} × {LT:.0f} ur konstruktionsplywood {LT:.0f} × {SKIVA_L:.0f} × {SKIVA_B:.0f} (raka snitt, sågsnitt {KERF:.0f})', 4.0, w='bold')
# kapplista
rows = []
for k, (a, b) in enumerate(LAG):
    L = lag_L(a, b); j = JOINT[k]
    A = j + OVER; B_ = L - j + OVER
    rows.append((k + 1, 'inner' if k < NL else 'ytter', (a + b) / 2, L, j, A, B_))
tx0, ty0 = 16, 30
hdr = ['lager', 'fläns', 'radie (mitt)', 'båglängd', 'skarv vid', 'bit A (fot)', 'bit B (nock)']
cxs = [0, 14, 30, 54, 76, 98, 122]
S.t(tx0, ty0, 'KAPPLISTA – EN HALVBÅGE (12 bitar). Alla bitar har ' + f'{OVER:.0f} mm övermått i ytteränden.', 3.3, w='bold')
for c_, x_ in zip(hdr, cxs): S.t(tx0 + x_, ty0 + 7, c_, 2.8, w='bold')
for i, rw in enumerate(rows):
    vals = [str(rw[0]), rw[1], f'R {rw[2]:.0f}', f'{rw[3]:.0f}', f'{rw[4]:.0f}', f'{rw[5]:.0f}', f'{rw[6]:.0f}']
    for v, x_ in zip(vals, cxs): S.t(tx0 + x_, ty0 + 12 + i * 4.4, v, 2.9, w='bold' if x_ >= 98 else 'normal')
yy = ty0 + 12 + len(rows) * 4.4 + 2
for i, n_ in enumerate([f'Skarven mäts längs lagrets egen kant från foten. Lager 1 = innerst (mot huset), lager 6 = ytterst (mot filmen).',
                        f'Skarvarna ligger {J3[1] - J3[0]:.0f} isär inom varje fläns (skivlängden {SKIVA_L:.0f} tillåter inte mer med {NL} lager).',
                        'Bitarna läggs stumt mot varandra med lim i ändarna. Kapa vinkelrätt.',
                        f'Totalt: {18 * 12} bitar till 18 halvbågar = {18 * 12} remsor à {SKIVA_L:.0f} = {math.ceil(18 * 12 / 12)} skivor (12 remsor per skiva).']):
    S.t(tx0, yy + i * 4.4, n_, 2.75)
# bitarnas längder grafiskt
gx0, gy0, gs = 16, 112, 0.042
S.t(gx0, gy0 - 5, 'SKARVLÄGEN, utvikt (fot till vänster, nock till höger)  ca 1:24', 3.3, w='bold')
for i, rw in enumerate(rows):
    y = gy0 + i * 6.2
    S.r(gx0 + 14, y, rw[5] * gs, 4.4, PLY, INK, 0.2); S.r(gx0 + 14 + rw[5] * gs, y, rw[6] * gs, 4.4, '#f6e7c6', INK, 0.2)
    S.t(gx0, y + 3.4, f'lager {rw[0]}', 2.7)
    S.t(gx0 + 14 + rw[5] * gs / 2, y + 3.3, f'A {rw[5]:.0f}', 2.5, 'middle'); S.t(gx0 + 14 + rw[5] * gs + rw[6] * gs / 2, y + 3.3, f'B {rw[6]:.0f}', 2.5, 'middle')
    if i == NL - 1: S.l(gx0 + 14, y + 5.3, gx0 + 14 + 4300 * gs, y + 5.3, GREY, 0.2, '1 0.6')
for i, (s0, L) in enumerate(KLS):
    xk = gx0 + 14 + (s0 * ((ri + ro) / 2) / R + OVER) * gs
    S.r(xk, gy0 + NL * 6.2 - 0.6, L * gs, 0.9, PLY2, INK, 0.1)
S.t(gx0 + 14, gy0 + 2 * NL * 6.2 + 4, 'brun linje mellan flänsarna = klossarnas lägen', 2.5, col=GREY)
# skivplan
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
S.t(px0, py0 + SKIVA_B * ps + 15, f'12 × {BB:.0f} + 11 snitt × {KERF:.0f} = {12 * BB + 11 * KERF:.0f}; rest {rest:.0f} mm (kantremsa, skräp).', 2.75)
S.t(px0, py0 + SKIVA_B * ps + 19.5, 'Såga längs skivans långa riktning (fiberriktning på ytskiktet längs remsan).', 2.75)
S.t(px0, py0 + SKIVA_B * ps + 24, 'Fäst en anslagslist och såga med cirkelsåg / spårsåg mot den; samma anslag till alla remsor.', 2.75)
# en remsa: bit + spill -> klossar
offs = []
for rw in rows:
    for piece in (rw[5], rw[6]): offs.append(SKIVA_L - piece - KERF)
small = sum(1 for s0, L in KLS if L == KL) * 2; big = sum(1 for s0, L in KLS if L == FKL) * 2
got_s = got_b = 0
offs_sorted = sorted(offs, reverse=True); used = []
need_b, need_s = big, small
for o in offs_sorted:
    nb = 0; ns = 0; rem = o
    while need_b > 0 and rem >= FKL + KERF: rem -= FKL + KERF; need_b -= 1; nb += 1
    while need_s > 0 and rem >= KL + KERF: rem -= KL + KERF; need_s -= 1; ns += 1
    used.append((o, nb, ns, rem))
ey = py0 + SKIVA_B * ps + 32
S.t(px0, ey, 'KLOSSAR UR SPILLET – en halvbåges 12 remsor', 3.3, w='bold')
S.t(px0, ey + 5, f'Spillbitarna räcker till alla {small} små + {big} stora klossbitar per halvbåge' + ('.' if need_s <= 0 and need_b <= 0 else f' – SAKNAS {need_s} små, {need_b} stora.'), 2.75)
for i, (o, nb, ns, rem) in enumerate(used[:6]):
    y = ey + 9 + i * 5
    S.r(px0, y, (SKIVA_L - o) * ps * 0.5, 3.4, PLY, INK, 0.15); x = px0 + (SKIVA_L - o) * ps * 0.5
    for _ in range(nb): S.r(x, y, FKL * ps * 0.5, 3.4, PLY2, INK, 0.15); x += (FKL + KERF) * ps * 0.5
    for _ in range(ns): S.r(x, y, KL * ps * 0.5, 3.4, PLY2, INK, 0.15); x += (KL + KERF) * ps * 0.5
    S.t(px0 + SKIVA_L * ps * 0.5 + 3, y + 2.8, f'spill {o:.0f} → {nb} × {FKL:.0f} + {ns} × {KL:.0f}', 2.5)
S.t(px0, ey + 9 + 6 * 5 + 2, '(skala 1:28; ljus = flänsbit, mörk = klossbitar)', 2.4, col=GREY)
TOT_SKIVOR_REMSOR = math.ceil(18 * 12 / 12)
p2 = S.save('ritning_bage_2')

# ======================= BLAD 3: klossar + nocklask =======================
S = Sheet()
S.frame('KLOSSAR OCH NOCKLASK', 'Raka snitt. Klossar ur remsornas spill.', 'blad 3/3')
S.t(14, 18, 'KLOSSAR  1:2', 4.0, w='bold')
ks = 0.5
def kloss(x0, y0, L, titel, antal):
    S.t(x0, y0 - 4, titel, 3.2, w='bold')
    # vy längs bågen (L × BB) och snitt (KH × BB)
    S.r(x0, y0, L * ks, BB * ks, PLY2, INK, 0.3)
    S.l(x0, y0 + BB * ks / 2, x0 + L * ks, y0 + BB * ks / 2, GREY, 0.12, '1 0.6')
    for fx in (30, L - 30):
        S.c(x0 + fx * ks, y0 + (BB / 2 + (12 if fx < L / 2 else -12)) * ks, 1.0, 'white', RED, 0.25)
    if L > 200: S.c(x0 + L / 2 * ks, y0 + BB / 2 * ks, 1.0, 'white', RED, 0.25)
    S.dim((x0, y0 + BB * ks), (x0 + L * ks, y0 + BB * ks), -5, f'{L:.0f} (längs bågen)')
    S.dim((x0 + L * ks, y0), (x0 + L * ks, y0 + BB * ks), -5, f'{BB:.0f}')
    sx = x0 + L * ks + 22
    S.r(sx, y0, LT * ks, BB * ks, PLY2, INK, 0.3); S.r(sx + LT * ks, y0, LT * ks, BB * ks, PLY2, INK, 0.3)
    S.dim((sx, y0 + BB * ks), (sx + KH * ks, y0 + BB * ks), -5, f'{KH:.0f}', 2.4)
    S.t(sx + KH * ks + 4, y0 + 8, f'2 × {LT:.0f} limmade', 2.7); S.t(sx + KH * ks + 4, y0 + 13, f'{antal}', 2.7, w='bold')
    S.t(sx + KH * ks + 4, y0 + 18, 'röda = skruv 5×90 utifrån', 2.7, col=RED)
nsmall = sum(1 for s0, L in KLS if L == KL); nbig = NKL - nsmall
kloss(18, 32, KL, f'Kloss / fotkloss / nockkloss {KL:.0f}', f'{nsmall} per halvbåge = {18 * nsmall} st ({2 * 18 * nsmall} bitar)')
kloss(18, 96, FKL, f'Fackkloss {FKL:.0f} (2 st, under/över sidoregeln)', f'{nbig} per halvbåge = {18 * nbig} st ({2 * 18 * nbig} bitar)')
S.t(18, 158, 'Tips: limma två 95-remsor på varandra först (ca 1 m), kapa sedan klossarna ur den dubbla remsan.', 2.8)
S.t(18, 163, 'Fackklossen ligger mot en böjd fläns: ca 2 mm glipa i mitten mot innerflänsen – PU-limmet fyller.', 2.8)
S.t(18, 168, 'Nockklossen: lägg den med övermått, kapas lodrätt tillsammans med flänsarna.', 2.8)
# nocklask
lx0, ly0, ls = 200, 70, 0.32
S.t(lx0, 18, f'NOCKLASK  {LT:.0f} mm plywood  1:3', 4.0, w='bold')
zmin = min(z for x, z in LASK); zmax = max(z for x, z in LASK)
LX_ = lambda x: lx0 + (x + LX) * ls; LY_ = lambda z: ly0 + (zmax - z) * ls
S.p([(LX_(x), LY_(z)) for x, z in LASK], PLY, INK, 0.35)
# bågarnas konturer runt
for sd in (1, -1):
    for r_ in (ri, ro):
        pts = [(sd * x, zc(r_, x)) for x in [XN + (LX + 40 - XN) * k / 30 for k in range(31)]]
        S.p([(LX_(x), LY_(z)) for x, z in pts], 'none', GREY, 0.2, close=False, dash='1 0.6')
S.l(LX_(-XN), LY_(zc(ri, XN)), LX_(-XN), LY_(zc(ro, XN)), GREY, 0.2); S.l(LX_(XN), LY_(zc(ri, XN)), LX_(XN), LY_(zc(ro, XN)), GREY, 0.2)
for sd in (1, -1):
    for k in range(4):
        xs_ = XN + 40 + k * 65; zs = (zc(ri, xs_) + sag + zc(rr, xs_)) / 2
        S.c(LX_(sd * xs_), LY_(zs), 0.9, 'white', RED, 0.25)
A, B_, C_, D_, E_, F_ = LASK
S.dim((LX_(A[0]), LY_(F_[1])), (LX_(C_[0]), LY_(F_[1])), -12, f'{2 * LX:.0f}')
S.dim((LX_(A[0]), LY_(F_[1])), (LX_(0), LY_(F_[1])), -6, f'{LX:.0f}', 2.4)
S.dim((LX_(C_[0]), LY_(C_[1])), (LX_(C_[0]), LY_(B_[1])), -6, f'{B_[1] - C_[1]:.1f}', 2.4)
S.dim((LX_(C_[0]), LY_(D_[1])), (LX_(C_[0]), LY_(C_[1])), -14, f'{C_[1] - D_[1]:.1f}', 2.4)
S.dim((LX_(0) , LY_(E_[1])), (LX_(0), LY_(B_[1])), 6, f'{B_[1] - E_[1]:.1f}', 2.4)
S.dim((LX_(D_[0]), LY_(D_[1])), (LX_(D_[0]), LY_(E_[1])), -22, f'{E_[1] - D_[1]:.1f}', 2.4)
ang = math.degrees(math.atan2(B_[1] - C_[1], LX))
S.t(lx0, LY_(zmin) + 24, f'Sexhörning, bara raka snitt: överkant och underkant är två räta linjer var som möts i mitten.', 2.75)
S.t(lx0, LY_(zmin) + 28.5, f'Lutning ≈ {ang:.1f}° mot vågrätt (båda kanterna parallella). Gör en mall av första lasken och rita resten.', 2.75)
S.t(lx0, LY_(zmin) + 33, f'Överkanten ligger {LAV:.0f} under bågens ytterkant så att nockens låsprofil går fri.', 2.75)
S.t(lx0, LY_(zmin) + 37.5, f'Grå streckad = bågarnas kanter; mitten = nockglipa {NockT:.0f} (nockklots). Röda = skruv 4,5×40, 4 per halva + PU-lim.', 2.75)
S.t(lx0, LY_(zmin) + 42, f'Antal: 2 per inre båge + 1 per gavelbåge (bara insidan) = 16 st.', 2.75, w='bold')
# lasknesting: V i V, ur en remsa 600 bred
nh = (B_[1] - C_[1]) + (C_[1] - D_[1])
pitch = C_[1] - D_[1] + KERF / math.cos(math.radians(ang))
S.t(lx0, LY_(zmin) + 52, f'Ur skivan: lägg V:na i varandra – en bit {2 * LX:.0f} × ca {16 * pitch + (B_[1] - C_[1]):.0f} räcker till alla 16 (snitt {KERF:.0f}).', 2.75)
p3 = S.save('ritning_bage_3')
out = os.path.join(HERE, 'ritning_bage.pdf')
subprocess.run(['python3', '-c', f"""
from pypdf import PdfWriter
w = PdfWriter()
for p in {[p1, p2, p3]!r}: w.append(p)
w.write({out!r})
"""], check=True)
print('pdf', out, 'klossar', NKL, nsmall, nbig, 'skarvar', JOINT, 'lask', [tuple(round(v, 1) for v in q) for q in LASK], 'bult', BULT, 'HanX', round(HanX))
