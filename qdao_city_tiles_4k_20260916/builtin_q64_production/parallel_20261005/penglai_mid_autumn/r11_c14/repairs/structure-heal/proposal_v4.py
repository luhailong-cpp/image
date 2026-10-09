from pathlib import Path
import sys,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from heal import now,ref,write,read,derived
base=P/'fixed-anchor-base-v2.png';source=P/'heal-v4-source.png';a=np.array(Image.open(base).convert('RGB'));b=np.array(Image.open(source).convert('RGB'))
y,x=np.mgrid[:1254,:1254];hole=np.array(Image.open(P/'water-l-edit-target-v4.png'))[:,:,3]==0
# Source blend restricted to true AI-filled water; 20px smooth return to unchanged interior.
extended=hole.copy();extended[:,:85]=extended[:,85:86];extended[:85,:]=extended[85:86,:]
dist=np.zeros(extended.shape,dtype=float);alive=extended.copy()
for i in range(1,21):
 dist[alive]=i;pad=np.pad(alive,1,mode='edge');alive=pad[1:-1,1:-1]&pad[:-2,1:-1]&pad[2:,1:-1]&pad[1:-1,:-2]&pad[1:-1,2:]
s=np.clip(dist/20,0,1);alpha=s*s*(3-2*s)*hole
out=np.rint(a*(1-alpha[:,:,None])+b*alpha[:,:,None]).astype('uint8')
assert np.array_equal(out[:85],a[:85]) and np.array_equal(out[:,:85],a[:,:85])
mask=P/'proposal-v4-selection-mask.png';derived(Image.fromarray(np.rint(alpha*255).astype('uint8')),mask,[base,source],dict(kind='water only AI selection, 20px smooth return; no shift/tone'))
dst=P/'structure-proposal-v4.png';derived(Image.fromarray(out),dst,[base,source,mask],dict(kind='AI water-only narrow L repair',flow=0,tone=0,fixedNeighbors=True,notCanonical=True))
qa=P/'qa-v4';qa.mkdir(exist_ok=True);im=Image.fromarray(out);items=[]
boxes={'north-join':[0,0,1254,250],'west-join':[0,0,250,1254],'northwest-corner':[0,0,330,330],'west-wall-detail':[0,360,300,840],'north-post-detail':[475,0,665,250],'west-boat-detail':[0,610,320,1040]}
for name,box in boxes.items():
 p=qa/(name+'.png');derived(im.crop(box),p,[dst],dict(kind='1:1 planning image crop; not native production',cropLTRB=box,scale=1));items.append(dict(**ref(p),cropLTRB=box,actuallyViewed=False))
write(P/'proposal-v4.json',dict(createdAt=now(),candidate=ref(dst),source=ref(source),base=ref(base),mask=ref(mask),fixedNandWPlanningPixelsUnchanged=True,physicalBoatSailMastStoneUnchanged=True,flow=0,tone=0,productionPixels=False,nativeDetailCount=0,qa=items,rootReviewPending=True))
write(P/'heal-v3.prepared-only.json',dict(createdAt=now(),request=ref(P/'heal-v3.request.json'),submitted=False,reason='Bottom rectangle crossed original hull; replaced with water-only polygon in v4 before call.'))
print(ref(dst))
