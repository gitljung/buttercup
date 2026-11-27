import json,sys
from PIL import Image
m=json.load(open('sprites.json')); rows=[]
for k,v in m['ovn'].items():
  im=Image.open(k+'.png').convert('RGBA'); n=v['n']; w=v['w']
  pick=[0,4,8,12] if n>=13 else range(n)
  row=Image.new('RGBA',(len(pick)*(w+4)*4,v['h']*4),(36,26,58,255))
  for j,i in enumerate(pick):
    f=im.crop((i*w,0,i*w+w,v['h'])).resize((w*4,v['h']*4),Image.NEAREST); row.alpha_composite(f,(j*(w+4)*4,0))
  rows.append(row)
W=max(r.width for r in rows); out=Image.new('RGBA',(W,sum(r.height+8 for r in rows)),(20,14,30,255)); y=0
for r in rows: out.alpha_composite(r,(0,y)); y+=r.height+8
out.convert('RGB').save(sys.argv[1] if len(sys.argv)>1 else '/Users/hiro/.hermes/cache/scratch/k735/px_kontakt.png')
