from pathlib import Path
import sys,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from heal import now,ref,write,read,derived
base=P/'fixed-anchor-base-v2.png';source=P/'heal-v5-source.png';a=np.array(Image.open(base).convert('RGB'));shift=1280*1254/4736
mapped=Image.open(source).convert('RGB').transform((1254,1254),Image.Transform.AFFINE,(1,0,shift,0,1,0),Image.Resampling.BICUBIC)
b=np.array(mapped);y,x=np.mgrid[:1254,:1254]
hole=((x>=85)&(x<265)&(y>=85)&(y<610))|((y>=85)&(y<205)&(x>=85)&(x<465))
ext=hole.copy();ext[:,:85]=ext[:,85:86];ext[:85,:]=ext[85:86,:];alive=ext.copy();dist=np.zeros(ext.shape,dtype=float)
for i in range(1,31):
 dist[alive]=i;q=np.pad(alive,1,mode='edge');alive=q[1:-1,1:-1]&q[:-2,1:-1]&q[2:,1:-1]&q[1:-1,:-2]&q[1:-1,2:]
s=np.clip(dist/30,0,1);alpha=s*s*(3-2*s)*hole
out=np.rint(a*(1-alpha[:,:,None])+b*alpha[:,:,None]).astype('uint8')
assert np.array_equal(out[:85],a[:85]) and np.array_equal(out[:,:85],a[:,:85])
mask=P/'proposal-v5-selection-mask.png';derived(Image.fromarray(np.rint(alpha*255).astype('uint8')),mask,[base,source],dict(kind='select AI water only; smooth 30px return'))
dst=P/'structure-proposal-v5.png';derived(Image.fromarray(out),dst,[base,source,mask],dict(kind='source-coordinate mapping, same planning scale',sourceCoordinateX='outputX +1280*1254/4736',frameTranslationOnly=True,localWarp=0,tone=0,fixedNeighbors=True,notCanonical=True))
qa=P/'qa-v5';qa.mkdir(exist_ok=True);im=Image.fromarray(out);items=[]
boxes={'north-join':[0,0,1254,250],'west-join':[0,0,300,1254],'northwest-corner':[0,0,350,350],'west-wall-detail':[0,360,300,840],'north-post-detail':[475,0,665,250],'west-boat-detail':[0,610,320,1040]}
for name,box in boxes.items():
 p=qa/(name+'.png');derived(im.crop(box),p,[dst],dict(kind='1:1 planning crop; not native production',cropLTRB=box,scale=1));items.append(dict(**ref(p),cropLTRB=box,actuallyViewed=False))
write(P/'proposal-v5.json',dict(createdAt=now(),candidate=ref(dst),source=ref(source),base=ref(base),mask=ref(mask),mapping=dict(sourceGlobalFrameXYWH=[51648,40640,4736,4736],proposalGlobalFrameXYWH=[52928,40640,4736,4736],sameScale=True,sourceCoordinateX='proposalX+1280*1254/4736'),fixedNandWPlanningPixelsUnchanged=True,physicalBoatSailMastStoneUnchanged=True,localWarp=0,tone=0,productionPixels=False,nativeDetailCount=0,qa=items,rootReviewPending=True))
print(ref(dst))
