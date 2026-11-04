import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
D=os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(D,'..','img'),exist_ok=True)
for k in sys.argv[1:]:
    im=np.asarray(Image.open(os.path.join(D,'..','art',k+'.png')).convert('RGB')).astype(np.float32)
    # background = bright/near white; soft alpha cut
    dist=np.sqrt(((im-255.0)**2).sum(-1))
    a=np.clip((dist-10)/30,0,1)
    m=a>.45
    lab,n=ndi.label(ndi.binary_dilation(m,iterations=5))
    if n:
        sizes=ndi.sum(m,lab,range(1,n+1)); keep=np.isin(lab,1+np.where(sizes>sizes.max()*.025)[0]); a=a*keep
    a=np.where(ndi.binary_fill_holes(a>.5),1.0,a)
    yy,xx=np.where(a>.04)
    if not len(yy): continue
    y0,y1,x0,x1=max(yy.min()-8,0),min(yy.max()+9,im.shape[0]),max(xx.min()-8,0),min(xx.max()+9,im.shape[1])
    rgba=np.dstack([im[y0:y1,x0:x1],a[y0:y1,x0:x1]*255]).astype(np.uint8)
    out=Image.fromarray(rgba,'RGBA')
    h=512 if k in ['boar','megaboar'] else 640
    w=round(out.width*h/out.height)
    if w>640: w=640; h=round(out.height*w/out.width)
    out.resize((w,h),Image.LANCZOS).save(os.path.join(D,'..','img',k+'.webp'),quality=90,method=6)
    print(k,w,h)
