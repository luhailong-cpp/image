"""Bounded material-matched south-edge color field, no geometry/neighbor mutation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
D=ROOT/'r07_c16/repairs/south-west-tone'
B=ROOT/'r07_c16/repairs/internal-color-match/candidate.png'
S=ROOT/'r08_c16/output/r08_c16.png'
E=ROOT/'r08_c16/output/extended-context.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B)=='f9ce61978e9cf7c97ffe931283731a8cdb5a45a3fb8c1a938a7e76eeb222666c'
assert sha(S)=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
base=np.asarray(Image.open(B).convert('RGB'));south=np.asarray(Image.open(S).convert('RGB'))
x0,x1,y0,y1=700,1320,3600,4096
n=np.median(base[-3:,x0:x1],axis=0).astype(np.float32)
s=np.median(south[:3,x0:x1],axis=0).astype(np.float32)
def warm(x):return ((x[...,0]>x[...,2]+18)&(x[...,0]>x[...,1]+7))
valid=warm(n)&warm(s)
delta=s-n
def smooth(v):
 for _ in range(3):
  p=np.pad(v,[(8,8)]+[(0,0)]*(v.ndim-1),mode='reflect')
  c=np.concatenate([np.zeros_like(p[:1]),np.cumsum(p,axis=0,dtype=np.float64)],axis=0)
  v=(c[17:]-c[:-17])/17
 return v
edge=smooth(delta*valid[:,None])/np.maximum(smooth(valid.astype(np.float32))[:,None],0.001)
edge=np.clip(edge,-32,32)
# Feather to exact preservation before x1320; no light correction to water/rope-white.
xf=np.ones(x1-x0,np.float32);xf[:100]=np.linspace(0,1,100);xf[-80:]=np.linspace(1,0,80)
yf=np.linspace(0,1,y1-y0,dtype=np.float32)**2
raw=base[y0:y1,x0:x1].astype(np.float32)
material=np.minimum(np.clip((raw[:,:,0]-raw[:,:,2]-18)/24,0,1),
                    np.clip((raw[:,:,0]-raw[:,:,1]-7)/16,0,1))
correction=np.rint(edge[None,:,:]*xf[None,:,None]*yf[:,None,None]*material[:,:,None]).astype(np.int16)
patch=np.clip(raw+correction,0,255).astype(np.uint8)
diff=patch.astype(np.int16)-raw.astype(np.int16)
assert np.abs(diff).max()<=32
D.mkdir(exist_ok=True)
Image.fromarray(patch).save(D/'patch.png')
np.savez_compressed(D/'correction.npz',correction_rgb_i16=diff,rect_core_xyxy=np.array([x0,y0,x1,y1]),edge_delta_rgb_f32=edge,changed_mask_u8=np.any(diff!=0,axis=2).astype(np.uint8),warm_confidence_u8=np.rint(material*255).astype(np.uint8))
merged=base.copy();merged[y0:y1,x0:x1]=patch
pair=np.concatenate([merged[3750:,700:1400],south[:240,700:1400]],axis=0)
Image.fromarray(pair).save(D/'boundary-after.png')
Image.fromarray(merged[y0:y1,x0:x1]).save(D/'insertion-region.png')
v={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':{'file':str(B),'sha256':sha(B)},'south':{'file':str(S),'sha256':sha(S)},'haloReference':{'file':str(E),'sha256':sha(E),'copiedIntoCandidate':False,'observation':'North115 halo shape differs in mast width and rope lead-in; used only for actual visual comparison.'},'rectCoreXYXY':[x0,y0,x1,y1],'patch':{'file':str(D/'patch.png'),'sha256':sha(D/'patch.png'),'pixels':[x1-x0,y1-y0]},'correction':{'file':str(D/'correction.npz'),'sha256':sha(D/'correction.npz')},'method':'Same-warm-material median3 adjacent-edge RGB delta, normalized17px three-pass one-dimensional difference-field smooth; cap32; warm-only material gate; quadratic vertical fade across last496rows and horizontal fades. No image blur/resampling/registration or source-pixel copying.','maxAppliedChannelChange':int(np.abs(diff).max()),'geometryWarp':False,'xAtLeast1320Unchanged':True,'outsideROIUnchanged':True,'southUnchanged':True,'canonicalOutputUnchanged':True,'visualReview':'pending','formalAccepted':False}
(D/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'patch':v['patch'],'maxChange':v['maxAppliedChannelChange']}))

