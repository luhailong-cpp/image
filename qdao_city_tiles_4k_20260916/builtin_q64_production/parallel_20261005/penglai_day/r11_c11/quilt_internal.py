from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import internal_qa as q
h=q.h;O=T/'repairs/internal-quilt';O.mkdir(parents=True,exist_ok=True)
canvas=np.zeros((4326,4326,3),np.float32);valid=np.zeros((4326,4326),bool);yy,xx=np.mgrid[:1254,:1254];records=[]
for r in range(4):
 for c in range(4):
  name=f'p{r+1}{c+1}';src=T/'native'/(name+'.png');new=q.arr(src);x,y=c*1024,r*1024;old=canvas[y:y+1254,x:x+1254];ov=valid[y:y+1254,x:x+1254]
  err=np.mean(abs(new-old),2);gx=np.diff(new,axis=1,prepend=new[:,:1])-np.diff(old,axis=1,prepend=old[:,:1]);gy=np.diff(new,axis=0,prepend=new[:1])-np.diff(old,axis=0,prepend=old[:1]);cost=err+2*np.mean(abs(gx)+abs(gy),2)
  mask=np.ones((1254,1254),bool);dist=np.full((1254,1254),1e4,np.float32);top=[];left=[]
  if r:
   top=q.path(cost[60:171].T)+60;mask &= yy>=top[None,:];dist=np.minimum(dist,yy-top[None,:])
  if c:
   left=q.path(cost[:,60:171])+60;mask &= xx>=left[:,None];dist=np.minimum(dist,xx-left[:,None])
  mask|=~ov
  # RGB only, exact native geometry retained. No pixel texture blending.
  w=np.clip(1-np.maximum(dist,0)/55,0,1)**2*ov*mask
  field=np.clip(q.smooth2(old-new,8),-12,12)*w[:,:,None]
  rep=np.clip(np.rint(new+field),0,255).astype('uint8')
  old[mask]=rep[mask];valid[y:y+1254,x:x+1254]=True
  rp=O/(name+'-replacement.png');mp=O/(name+'-mask.png');fp=O/(name+'-field.npz')
  Image.fromarray(rep).save(rp);Image.fromarray(mask.astype('uint8')*255).save(mp);np.savez_compressed(fp,field=field,topCut=top,leftCut=left)
  h.p.derived(rp,[src]+[e['replacement'] for e in records[-4:]],{'method':'native min-error source ownership with bounded12 RGB matching field; no image resampling, warping, texture blur or feather','originTileXY':[x-115,y-115],'field':str(fp),'ownershipMask':str(mp)})
  h.p.derived(mp,[src],{'method':'binary min-error native source ownership mask','originTileXY':[x-115,y-115],'fieldFile':str(fp),'fieldSha256':h.p.sha(fp)})
  records.append({'source':str(src),'sourceSha256':h.p.sha(src),'replacement':str(rp),'mask':str(mp),'originTileXY':[x-115,y-115],'fields':str(fp),'maxRGBField':float(abs(field).max())})
out=O/'r11_c11-internal-v2.png';im=Image.fromarray(canvas[115:4211,115:4211].astype('uint8'));im.save(out)
h.p.derived(out,[e['replacement'] for e in records],{'method':'native integer source quilt, exact masks and boundedRGB fields','formalAccepted':False})
h.p.write(O/'record-v2.json',{'candidate':str(out),'sha256':h.p.sha(out),'repairs':records})
q.qa(im,'internal-v2',out)
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:
  b=(x-627,y-627,x+627,y+627);f=T/'qa'/f'internal-v2-full-{x}-{y}.png';im.crop(b).save(f);h.p.derived(f,[out],{'method':'native1254 context crop','boxLTRB':b})
im.resize((1254,1254),Image.Resampling.LANCZOS).save(O/'preview.png')


h.p.derived(O/'preview.png',[out],{'method':'review-only downscale'})
