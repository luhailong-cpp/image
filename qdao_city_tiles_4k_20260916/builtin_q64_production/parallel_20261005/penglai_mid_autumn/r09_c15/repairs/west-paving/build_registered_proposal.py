"""Bounded registration of already AI-painted geometry; independent proposal only."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'tools/deps'))
import cv2 as cv
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
base=np.array(Image.open(P/'edit-target.png').convert('RGB'))
moving=np.array(Image.open(P/'repair-v3.png').convert('RGB'))
assert base.shape==moving.shape==(1254,1254,3)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
owner=(xx>=320)&(xx<920)&(yy>=80)&(yy<990)
outside=~owner
distance=cv.distanceTransform(owner.astype(np.uint8),cv.DIST_L2,5)
outside_distance=cv.distanceTransform(outside.astype(np.uint8),cv.DIST_L2,5)
known=outside&(outside_distance<=128)
reference=np.where(known[:,:,None],base,moving)
raw=cv.calcOpticalFlowFarneback(cv.cvtColor(reference,cv.COLOR_RGB2GRAY),cv.cvtColor(moving,cv.COLOR_RGB2GRAY),None,.5,4,41,5,7,1.5,0)
support=known.astype(np.float32)
denom=cv.GaussianBlur(support,(0,0),3)
estimated=cv.GaussianBlur(raw*support[:,:,None],(0,0),3)/np.maximum(denom[:,:,None],1e-6)
_,labels=cv.distanceTransformWithLabels((~known).astype(np.uint8),cv.DIST_L2,5,labelType=cv.DIST_LABEL_PIXEL)
lut=np.zeros((int(labels.max())+1,2),np.float32);lut[labels[known]]=estimated[known]
field=cv.GaussianBlur(lut[labels],(0,0),3)
weight=smooth((192-distance)/(192-32))*owner
mag=np.linalg.norm(field,axis=2);flow=field*np.minimum(1,6/np.maximum(mag,1e-6))[:,:,None]*weight[:,:,None]
initial=None;scale=1.
for _ in range(24):
 dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
 lo=float(jac[owner].min())
 if initial is None:initial=lo
 if lo>=.25:break
 flow*=.75;scale*=.75
else:raise RuntimeError('Jacobian safety failed')
aligned=cv.remap(moving,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
# Outside source also needs registration for correct measured photometric residual.
# Use same capped measured support flow there only for measurement, never apply to base.
supportflow=field*np.minimum(1,6/np.maximum(mag,1e-6))[:,:,None]*scale
supportaligned=cv.remap(moving,xx+supportflow[:,:,0],yy+supportflow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
def grad(a):
 g=cv.cvtColor(a,cv.COLOR_RGB2GRAY).astype(np.float32);gy,gx=np.gradient(g);return np.hypot(gx,gy)
res=base.astype(np.float32)-supportaligned.astype(np.float32)
safe=known&(grad(base)<12)&(grad(supportaligned)<12)&(np.max(np.abs(res),axis=2)<40)
weights=cv.GaussianBlur(safe.astype(np.float32),(0,0),12)
measured=cv.GaussianBlur(res*safe[:,:,None],(0,0),12)/np.maximum(weights[:,:,None],1e-6)
_,cl=cv.distanceTransformWithLabels((~safe).astype(np.uint8),cv.DIST_L2,5,labelType=cv.DIST_LABEL_PIXEL)
tl=np.zeros((int(cl.max())+1,3),np.float32);tl[cl[safe]]=measured[safe]
tone=np.clip(cv.GaussianBlur(tl[cl],(0,0),12),-18,18)*weight[:,:,None]
adjusted=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
adjusted[weight==0]=moving[weight==0]
joint=base.copy();joint[owner]=adjusted[owner]
assert np.array_equal(joint[~owner],base[~owner])
assert np.linalg.norm(flow,axis=2).max()<=6.00001 and np.abs(tone).max()<=18.00001
out=P/'proposed-joint-v4.png';assert not out.exists();Image.fromarray(joint).save(out)
fields=[]
for n,a in [('flow',flow),('colorCorrection',tone),('jacobian',jac)]:
 q=P/('proposal-v4.'+n+'.npy');np.save(q,a);fields.append(ref(q))
for n,a in [('apply-mask',owner),('support-mask',known),('same-material-support',safe)]:
 q=P/('proposal-v4.'+n+'.png');Image.fromarray(a.astype(np.uint8)*255).save(q);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v4',(240,0,1000,180)),('right-perimeter-v4',(840,0,1000,1070)),('lower-perimeter-v4',(240,910,1000,1070)),('west-join-v4',(160,0,480,1070))]:
 q=P/(name+'.png');Image.fromarray(joint).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec)
 write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
diff=np.any(joint!=base,axis=2);ys,xs=np.nonzero(diff)
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseTarget':ref(P/'edit-target.png'),'source':ref(P/'repair-v3.png'),'sourceCropLTRB':[320,80,920,990],'candidateCropLTRB':[0,2840,600,3750],'joint':ref(out),'fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'actualChangedPixels':int(diff.sum()),'actualChangedJointBBoxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'registration':{'trueSupport':'Actual original pixels outside the authorized rectangle in a128px ring compared with corresponding AI native pixels. Original pixels never modified.','flowConvention':'AI source sampled at output XY plus recorded XY flow','maxAllowedDisplacementVector':6,'actualMaxDisplacementVector':float(np.linalg.norm(flow,axis=2).max()),'maxAllowedColorCorrectionRGB':18,'actualMaxColorCorrectionRGB':np.abs(tone).max(axis=(0,1)).tolist(),'returnDepth':192,'fullStrengthDepth':32,'jacobianInitialMinimum':initial,'orientationSafetyScale':scale,'jacobianMinimumInAppliedPixels':float(jac[owner].min()),'foldedAppliedPixels':int(((jac<=0)&owner).sum()),'supportPixels':int(known.sum()),'sameMaterialColorSupportPixels':int(safe.sum()),'clippedSupportFraction':float(np.mean(mag[known]>6)),'geometryFeather':False,'sourcePixelScale':1,'sourceUpscaling':False,'codePaintedMissingStructure':False},'oldWestUnchanged':True,'outsideAuthorizedAreaUnchanged':True,'candidateNotChanged':True,'accepted':False}
write(P/'proposal-v4.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':'Binary ownership of native AI repair with bounded native registration and finite photometric return','derivedFrom':[ref(P/'edit-target.png'),ref(P/'repair-v3.png')],'mappingRecord':ref(P/'proposal-v4.json'),'actualModel':None,'actualQuality':None,'sourcePixelScale':1,'formalAccepted':False})
for q in fields:
 write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Recorded native registration/support field','derivedFrom':[ref(P/'edit-target.png'),ref(P/'repair-v3.png')],'mappingRecord':ref(P/'proposal-v4.json')})
print(json.dumps({'proposal':ref(P/'proposal-v4.json'),'joint':ref(out),'registration':v['registration']}))

