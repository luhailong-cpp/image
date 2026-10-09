"""Smooth only RGB difference fields after native geometry joint repair."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
R=Path(__file__).resolve().parent;D=R/'r07_c16/repairs/south-joint-color-v4'
V=R/'r07_c16/repairs/integrated-southwest-v3';m=json.loads((V/'manifest.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
assert sha(V/'candidate.png')=='db2e1e223b5359ce5b563a6e20bd40870a29a17713274f6a19bbc1974e9c0749'
base=rgb(V/'candidate.png');prior=rgb(m['baseline']['file']);native=rgb(m['nativeRepair']['file']);south=rgb(m['immutableSouth']['file'])
assert sha(m['immutableSouth']['file'])=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
x0,y0,x1,y1=790,3790,1400,4096
def smooth(v,n=25,passes=3):
 for _ in range(passes):
  for axis in (0,1):
   pads=[(0,0)]*v.ndim;pads[axis]=(n//2,n//2);p=np.pad(v,pads,mode='reflect')
   c=np.cumsum(p,axis=axis,dtype=np.float64);z=np.take(c,[0],axis=axis)*0;c=np.concatenate([z,c],axis=axis)
   if axis==0:v=(c[n:]-c[:-n])/n
   else:v=(c[:,n:]-c[:,:-n])/n
 return v.astype(np.float32)
def warm(v):return (v[...,0]>v[...,2]+18)&(v[...,0]>v[...,1]+7)
raw=base[y0:y1,x0:x1].astype(np.float32)
old=prior[y0:y1,x0:x1].astype(np.float32)
new=native[y0-3469:y1-3469,x0-443:x1-443].astype(np.float32)
alpha_all=np.asarray(Image.open(m['insertions'][0]['alpha']['file']).convert('L'),dtype=np.float32)/255
alpha=alpha_all[y0-3469:y1-3469,x0-443:x1-443]
delta=old-new
valid=(warm(old)&warm(new)&(np.max(np.abs(delta),axis=2)<48)).astype(np.float32)
valid[3994-y0:]=0 # geometry-reconstructed hole excluded from estimating original-vs-edit tint
den=smooth(valid)
field=smooth(delta*valid[:,:,None])/np.maximum(den[:,:,None],0.001)
field=np.clip(field,-32,32)
soft_alpha=smooth(alpha)
top=(alpha-soft_alpha)[:,:,None]*field
# Correction is not texture/image blending: existing pixels plus a low-frequency RGB delta.
ygate=np.ones(y1-y0,np.float32);ygate[3980-y0:4020-y0]=np.linspace(1,0,40);ygate[4020-y0:]=0
xgate=np.ones(x1-x0,np.float32);xgate[:40]=np.linspace(0,1,40);xgate[-40:]=np.linspace(1,0,40)
material=np.clip((raw[:,:,0]-raw[:,:,2]+4)/20,0,1)
top*=ygate[:,None,None]*xgate[None,:,None]*material[:,:,None]
mid=np.clip(raw+top,0,255)
# Geometry now aligned: match only same-warm-material adjacent boundary color.
n=np.median(mid[-3:],axis=0);s=np.median(south[:3,x0:x1],axis=0).astype(np.float32)
valid_edge=np.minimum(np.clip((n[:,0]-n[:,2]+4)/20,0,1),np.clip((s[:,0]-s[:,2]+4)/20,0,1))
ed=s-n
def edge_smooth(v):
 for _ in range(2):
  p=np.pad(v,[(4,4)]+[(0,0)]*(v.ndim-1),mode='reflect')
  c=np.concatenate([np.zeros_like(p[:1]),np.cumsum(p,axis=0,dtype=np.float64)],axis=0)
  v=(c[9:]-c[:-9])/9
 return v
edge_den=edge_smooth(valid_edge)
edge=edge_smooth(ed*valid_edge[:,None])/np.maximum(edge_den[:,None],0.001)
support=edge_den>0.03
assert support.any()
for k in range(3):
 edge[:,k]=np.interp(np.arange(len(edge)),np.flatnonzero(support),edge[support,k])
edge=edge_smooth(edge)
edge=np.clip(edge,-32,32)
yf=np.zeros(y1-y0,np.float32);yf[3980-y0:]=np.linspace(0,1,y1-3980)**1.2
bottom=edge[None,:,:]*yf[:,None,None]*xgate[None,:,None]*material[:,:,None]
total=np.clip(np.rint(top+bottom),-32,32).astype(np.int16)
patch=np.clip(raw+total,0,255).astype(np.uint8)
candidate=base.copy();candidate[y0:y1,x0:x1]=patch
diff=candidate.astype(np.int16)-base.astype(np.int16)
D.mkdir(exist_ok=True)
assert not np.any(diff[:y0]) and not np.any(diff[:,x1:]) and not np.any(diff[:,:x0])
Image.fromarray(candidate).save(D/'candidate.png')
ext=rgb(V/'extended-context.png');ext[115:4211,115:4211]=candidate;Image.fromarray(ext).save(D/'extended-context.png')
np.savez_compressed(D/'correction.npz',rect_core_xyxy=np.array([x0,y0,x1,y1]),correction_rgb_i16=total,top_field_rgb_f32=field,edge_delta_rgb_f32=edge,alpha_original_f32=alpha,alpha_smooth_f32=soft_alpha,changed_mask_u8=np.any(total!=0,axis=2).astype(np.uint8))
Image.fromarray(np.concatenate([candidate[3830:,700:1460],south[:174,700:1460]],axis=0)).save(D/'mast-joint.png')
Image.fromarray(candidate[3810:4096,710:1480]).save(D/'mast-top-insertion.png')
a.QA=D/'qa';a.ART=D/'candidate.png';southim,ni=a.checked_south();qa=a.write_qa(Image.fromarray(candidate),Image.fromarray(ext),southim)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'baseline':m['candidate'],'prior':m['baseline'],'native':m['nativeRepair'],'south':m['immutableSouth'],'rectCoreXYXY':[x0,y0,x1,y1],'candidate':{'file':str(D/'candidate.png'),'sha256':sha(D/'candidate.png'),'pixels':[4096,4096]},'extendedContext':{'file':str(D/'extended-context.png'),'sha256':sha(D/'extended-context.png')},'correction':{'file':str(D/'correction.npz'),'sha256':sha(D/'correction.npz')},'method':'Preserved integrated native geometry; top insertion uses original-vs-native normalized same-material low frequency RGB difference times hard-alpha minus smooth-alpha. Geometry-reconstructed hole excluded from field estimation. Bottom uses aligned same-material adjacent-edge9px smooth RGB delta; local bounded fades. Edge-delta values without material support are interpolated from supported columns rather than abruptly zeroed. Continuous R-minus-B material confidence includes pale rope without a binary warm-class edge. Filtering applies only to RGB differences or alpha, never image texture.','maxChange':int(np.abs(diff).max()),'imageBlur':False,'resampling':False,'geometryWarp':False,'southUnchanged':True,'outsideROIUnchanged':True,'nativeUnchanged':True,'canonicalOutputUnchanged':True,'qa':qa,'visualReview':'pending','formalAccepted':False}
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'candidate':manifest['candidate'],'maxChange':manifest['maxChange']}))

