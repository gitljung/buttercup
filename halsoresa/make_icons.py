# Ikoner + delningsbild för Hasses Hälsoresa (körs en gång)
from PIL import Image, ImageDraw, ImageFont
import os
R = '/Users/hiro/code/buttercup/halsoresa'
F = '/Users/hiro/.hermes/cache/scratch/fonts/Anton.ttf'
YEL, CHI, INK, CRE = (252, 194, 34), (200, 52, 10), (42, 18, 6), (255, 246, 220)
bust = Image.open('/Users/hiro/code/stark_igen_sprites/hasse/hasse_bust.png').convert('RGBA')
# vit bakgrund bort (flood från kanterna) om bilden saknar alfa
if bust.getextrema()[3][0] == 255:
    from PIL import ImageDraw as D
    b = bust.copy(); w, h = b.size
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]: D.floodfill(b, xy, (0, 0, 0, 0), thresh=40)
    bust = b
bb = bust.getbbox(); bust = bust.crop(bb)

def icon(n):
    im = Image.new('RGBA', (n, n), YEL); d = ImageDraw.Draw(im)
    r = int(n * .40); d.ellipse([n / 2 - r, n * .53 - r, n / 2 + r, n * .53 + r], fill=CHI)
    bh = int(n * .70); b = bust.resize((int(bust.width * bh / bust.height), bh), Image.LANCZOS)
    im.alpha_composite(b, ((n - b.width) // 2, n - bh - int(n * .1)))
    return im.convert('RGB')
icon(512).save(os.path.join(R, 'icon-512.png')); icon(192).save(os.path.join(R, 'icon-192.png'))

og = Image.new('RGBA', (1200, 630), YEL); d = ImageDraw.Draw(og)
d.ellipse([760, 60, 1260, 560], fill=CHI)
h = Image.open('/Users/hiro/code/buttercup/traning/hasse.webp').convert('RGBA'); h = h.resize((int(h.width * 560 / h.height), 560), Image.LANCZOS)
og.alpha_composite(h, (1200 - h.width - 30, 630 - 560))
f1 = ImageFont.truetype(F, 150); f2 = ImageFont.truetype(F, 46)
d.text((60, 70), 'HASSES', font=f1, fill=INK); d.text((60, 230), 'HÄLSORESA', font=f1, fill=CHI)
d.rounded_rectangle([60, 440, 520, 510], 14, fill=INK); d.text((82, 447), 'HALLÅ GÄNGET!', font=f2, fill=CRE)
og.convert('RGB').save(os.path.join(R, 'og.jpg'), quality=86)
print('ok')
