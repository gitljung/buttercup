#!/usr/bin/env python3
"""Pixel-Hasse (kort #735): pixliserar Hasse-arken för passet Swing + drag till EN gemensam palett.
Källor: ../../ex/hasse/<ark>_x2.webp (32 rutor/rep, 16x2) + deadbug_gen.webp (2 nyckelposer, gpt-image-2 i Hasses stil).
Ut: ../px/<ovn>.png (palettbild, rutor i rad) + ../px/sprites.json.  Kör: python3 pix.py deadbug_gen.webp
"""
import json, os, sys
from collections import Counter
from PIL import Image

R = os.path.dirname(os.path.abspath(__file__))
HR = os.path.abspath(os.path.join(R, '..', '..'))
OUT = os.path.join(R, '..', 'px'); os.makedirs(OUT, exist_ok=True)
MAN = json.load(open(os.path.join(HR, 'ex', 'manifest.json')))['hasse']
H = 84            # Hasse stående ≈ 84 px hög (källa 480) – grovt nog för 16-bitskänsla
S = H / 480
NCOL = 20         # gemensam palett (+ transparent)
OVN = {'swing': 'swing', 'goblet': 'goblet', 'rodd': 'bojdrodd', 'halo': 'halo'}


def frames_x2(ark):
    w = MAN[ark]; im = Image.open(os.path.join(HR, 'ex', 'hasse', ark + '_x2.webp')).convert('RGBA')
    fr = []
    for sub in range(0, 32, 2):            # originalrutorna (jämna)
        c, r = sub % 16, (1 if sub >= 16 else 0)
        fr.append(im.crop((c * w, r * 480, c * w + w, r * 480 + 480)))
    return fr


def deadbug_frames(path):
    im = Image.open(path).convert('RGBA'); px = im.load(); W, Hh = im.size
    # vit bakgrund -> transparent (flood från kanterna)
    from collections import deque
    seen = bytearray(W * Hh); q = deque()
    for x in range(W): q.extend([(x, 0), (x, Hh - 1)])
    for y in range(Hh): q.extend([(0, y), (W - 1, y)])
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= W or y >= Hh or seen[y * W + x]: continue
        r, g, b, a = px[x, y]
        if r + g + b < 690: continue
        seen[y * W + x] = 1; px[x, y] = (0, 0, 0, 0)
        q.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    # dela i två poser på kolumnen med minst innehåll i mitten
    # (källan sparad i halv storlek)
    a = im.getchannel('A'); cols = [sum(1 for y in range(0, Hh, 4) if a.getpixel((x, y)) > 0) for x in range(W)]
    mid = min(range(int(W * .35), int(W * .65)), key=lambda x: cols[x])
    poses = [im.crop((0, 0, mid, Hh)), im.crop((mid, 0, W, Hh))]
    # gemensam skala ur startposen, poserna linjeras på västen (röda pixlar: vänsterkant + nederkant)
    def vast(p):
        d = p.load(); xs = []; ys = []
        for y in range(0, p.height, 2):
            for x in range(0, p.width, 2):
                r, g, b, al = d[x, y]
                if al and r > 150 and g < 70 and b < 70: xs.append(x); ys.append(y)
        return min(xs), max(ys)
    ref = Image.open(os.path.join(HR, 'ex', 'hasse', 'golvpress_x2.webp')).convert('RGBA').crop((0, 0, MAN['golvpress'], 480))
    L = ref.getbbox(); body = L[2] - L[0]
    b0 = poses[0].getbbox(); k = body / (b0[2] - b0[0])
    v = [vast(p) for p in poses]
    out = []
    CW = round(W * k * .9)
    for p, (vx, vy) in zip(poses, v):
        p = p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS)
        c = Image.new('RGBA', (CW, 480), (0, 0, 0, 0))
        # västens vänsterkant på x = 0.42*CW, nederkant på 480-12
        c.paste(p, (round(CW * .4 - vx * k), round(468 - vy * k)), p)
        out.append(c)
    # sekvens 16 rutor: start x4, sträck x8, start x4 (pixel-loop i takt)
    return [out[0]] * 4 + [out[1]] * 8 + [out[0]] * 4


def down(fr):
    w = max(1, round(fr.width * S))
    # förmultiplicerad nedskalning -> inga vita kanter
    r, g, b, a = fr.split()
    pm = Image.merge('RGBA', (*(Image.composite(ch, Image.new('L', fr.size, 0), a) for ch in (r, g, b)), a))
    sm = pm.resize((w, H), Image.LANCZOS)
    px = sm.load()
    for y in range(H):
        for x in range(w):
            R_, G, B, A = px[x, y]
            if A < 110: px[x, y] = (0, 0, 0, 0)
            else: px[x, y] = (min(255, R_ * 255 // A), min(255, G * 255 // A), min(255, B * 255 // A), 255)
    return sm


def build(db_path):
    sets = {k: [down(f) for f in frames_x2(a)] for k, a in OVN.items()}
    if db_path: sets['deadbug'] = [down(f) for f in deadbug_frames(db_path)]
    # gemensam palett ur alla opaka pixlar
    samp = []
    for fs in sets.values():
        for f in fs[::3]:
            samp += [p[:3] for p in f.getdata() if p[3]]
    pal_src = Image.new('RGB', (len(samp), 1)); pal_src.putdata(samp)
    q = pal_src.quantize(colors=NCOL - 1, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = q.getpalette()[:3 * (NCOL - 1)]
    pal = [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]
    ink = (28, 20, 22); pal.append(ink)                     # extra mörk konturfärg
    pimg = Image.new('P', (1, 1)); flat = sum(pal, ()) + pal[0] * (256 - len(pal)); pimg.putpalette(flat)
    global PAL_CACHE; PAL_CACHE = [c + (255,) for c in pal]
    meta = {'palett': ['#%02x%02x%02x' % c for c in pal], 'h': H, 'ovn': {}}
    for k, fs in sets.items():
        q = [clean(f.convert('RGB').quantize(palette=pimg, dither=Image.NONE), f, len(pal)) for f in fs]
        q = [outline(x, len(pal) - 1) for x in q]
        # gemensam bbox (fötterna på samma rad)
        bb = [x.getbbox() for x in q]
        l = min(b[0] for b in bb); t = min(b[1] for b in bb); r_ = max(b[2] for b in bb); bt = max(b[3] for b in bb)
        l, t, r_, bt = max(0, l - 1), max(0, t - 1), r_ + 1, bt + 1
        fw, fh = r_ - l, bt - t
        sheet = Image.new('RGBA', (fw * len(q), fh), (0, 0, 0, 0))
        for i, x in enumerate(q): sheet.paste(x.crop((l, t, r_, bt)), (i * fw, 0))
        sheet.quantize(colors=len(pal) + 1, method=Image.FASTOCTREE, dither=Image.NONE).save(os.path.join(OUT, k + '.png'), optimize=True)
        meta['ovn'][k] = {'w': fw, 'h': fh, 'n': len(q)}
        print(k, fw, 'x', fh, len(q), 'rutor')
    json.dump(meta, open(os.path.join(OUT, 'sprites.json'), 'w'), indent=1)


def clean(qp, src, n):
    """Palettindex -> RGBA, transparens från källan, ensamma pixlar ersätts av grannarnas majoritet."""
    w, h = qp.size; idx = list(qp.getdata()); al = [p[3] for p in src.getdata()]
    T = -1
    g = [idx[i] if al[i] else T for i in range(w * h)]
    out = g[:]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            v = g[y * w + x]
            nb = [g[(y + dy) * w + x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if v not in nb:
                c, m = Counter(nb).most_common(1)[0]
                if m >= 5: out[y * w + x] = c
    return (out, w, h)


def outline(q, ink_i):
    g, w, h = q
    pal = PAL_CACHE
    out = g[:]
    for y in range(h):
        for x in range(w):
            if g[y * w + x] != -1: continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and g[(y + dy) * w + x + dx] != -1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y * w + x] = ink_i
    im = Image.new('RGBA', (w, h))
    im.putdata([(0, 0, 0, 0) if v == -1 else pal[v] for v in out])
    return im


PAL_CACHE = []
if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else None)
