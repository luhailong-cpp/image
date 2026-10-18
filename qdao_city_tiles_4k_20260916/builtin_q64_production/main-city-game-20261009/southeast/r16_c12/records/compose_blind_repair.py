from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent.parent;R=T/'repairs/blind-grout-20261016-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prep=read(R/'preparation.json');bp=Path(prep['base']['path']);cp=Path(prep['baseContext']['path'])
assert sha(bp)==prep['base']['sha256'];base=np.array(Image.open(bp).convert('RGB'));native=np.array(Image.open(R/'I01-native.png').convert('RGB'));assert native.shape==(1254,1254,3)
out=base.copy();x0,y0,x1,y1=3320,1420,3415,1890;yy,xx=np.mgrid[y0:y1,x0:x1];a=np.clip(np.minimum.reduce([xx-x0,x1-1-xx,yy-y0,y1-1-yy])/12,0,1)
origin=(2740,1000);ax,ay=x0-origin[0],y0-origin[1]
out[y0:y1,x0:x1]=np.rint(base[y0:y1,x0:x1]*(1-a[...,None])+native[ay:ay+y1-y0,ax:ax+x1-x0]*a[...,None]).astype('uint8')
mask=np.zeros((4096,4096),dtype=np.float32);mask[y0:y1,x0:x1]=a;mp=R/'I01-alpha.npy';np.save(mp,mask,allow_pickle=False)
assert np.array_equal(out[mask==0],base[mask==0])
for sl in [(slice(0,384),slice(None)),(slice(None),slice(3712,4096)),(slice(None),slice(0,384)),(slice(3712,4096),slice(None))]:assert np.array_equal(out[sl],base[sl])
dest=T/'candidate/r16_c12-4k-blind-repair-v1-20261016.png';ctxdest=T/'candidate/r16_c12-context-blind-repair-v1-20261016.png'
Image.fromarray(out).save(dest);ctx=Image.open(cp).convert('RGB');ctx.paste(Image.fromarray(out),(115,115));ctx.save(ctxdest)
Image.fromarray(out).crop((3100,1330,3600,2000)).save(R/'I01-after-local.png')
Image.fromarray(base).crop((3100,1330,3600,2000)).save(R/'I01-before-local.png')
man={'base':prep['base'],'baseContext':prep['baseContext'],'native':{'path':str(R/'I01-native.png'),'sha256':sha(R/'I01-native.png'),'size':[1254,1254]},'candidate':{'path':str(dest),'sha256':sha(dest),'size':[4096,4096]},'context':{'path':str(ctxdest),'sha256':sha(ctxdest),'size':[4326,4326]},'mask':{'path':str(mp),'sha256':sha(mp),'box':[x0,y0,x1,y1],'feather':12},'outsideMaskUnchanged':True,'allFour384EdgesUnchanged':True,'resized':False,'actualModel':None,'status':'pending_local_visual_review','formalAccepted':False}
(R/'manifest.json').write_text(json.dumps(man,indent=2),encoding='utf-8');print(json.dumps(man))

