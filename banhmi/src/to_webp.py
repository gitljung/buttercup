"""art/*.png (vit bakgrund) -> img/*.webp med alfa, beskuren, höjd 780."""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = os.path.dirname(os.path.abspath(__file__))
for k in sys.argv[1:]:
    im = np.asarray(Image.open(os.path.join(D, '..', 'art', k + '.png')).convert('RGB')).astype(np.float32)
    dist = np.sqrt(((im - 255.0) ** 2).sum(-1))
    a = np.clip((dist - 10) / 28, 0, 1)
    m = a > .5
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=4))
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        a = a * np.isin(lab, 1 + np.where(sizes > sizes.max() * .03)[0])
    a = np.where(ndi.binary_fill_holes(a > .5), 1.0, a)   # vitt inuti motivet ska vara opakt
    yy, xx = np.where(a > .05)
    y0, y1, x0, x1 = max(yy.min() - 6, 0), yy.max() + 7, max(xx.min() - 6, 0), xx.max() + 7
    rgba = np.dstack([im[y0:y1, x0:x1], a[y0:y1, x0:x1] * 255]).astype(np.uint8)
    out = Image.fromarray(rgba, 'RGBA')
    h = 780
    w = round(out.width * h / out.height)
    if w > 760:
        w = 760
        h = round(out.height * w / out.width)
    out.resize((w, h), Image.LANCZOS).save(os.path.join(D, '..', 'img', k + '.webp'), quality=90, method=6)
    print(k, w, h)
