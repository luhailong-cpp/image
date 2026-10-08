"""v5 finite photometric return of existing native AI geometry, never canonical."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'tools/deps'));import cv2 as cv
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
base=np.array(Image.open(P/'edit-target.png').convert('RGB'))
raw=np.array(Image.open(P/'repair-v3.png').convert('RGB'))
flow=np.load(P/'proposal-v4.flow.npy');tone=np.load(P/'proposal-v4.colorCorrection.npy')
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
owner=(xx>=320)&(xx<920)&(yy>=80)&(yy<990)
aligned=cv.remap(raw,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE).astype(np.float32)
# The previous proposal used a hard binary rectangle and no opacity ramp.
# Blend only the already-matched geometry into actual fixed context over finite widths.
alpha=smooth((yy-80)/72)*smooth((919-xx)/96)*smooth((989-yy)/96)*owner
matched=aligned+tone
desired=alpha[:,:,None]*matched+(1-alpha[:,:,None])*base.astype(np.float32)
# Entire effective per-channel change to sampled AI is limited, including the ramp.
effective=np.clip(desired-aligned,-18,18)*owner[:,:,None]
# True W is not returned to the original broken current seam. Only low-gradient
# lower-stone paint is locally color-matched to actual west, leaving line geometry.
west_expected=np.median(base[:,308:320].astype(np.float32),axis=1)
west_source=np.median(aligned[:,320:332],axis=1)
delta=west_expected-west_source
gray=cv.cvtColor(base,cv.COLOR_RGB2GRAY).astype(np.float32)
gy,gx=np.gradient(gray)
safe=(np.max(np.abs(delta),axis=1)<40)&(np.median(np.hypot(gx,gy)[:,308:320],axis=1)<12)
weighted=cv.GaussianBlur((delta*safe[:,None])[:,None,:],(1,0),3)[:,0,:]
weights=cv.GaussianBlur(safe.astype(np.float32)[:,None],(1,0),3)[:,0]
profile=weighted/np.maximum(weights[:,None],1e-6)
profile=np.clip(profile,-18,18)
wx=smooth((416-xx)/96)
wy=smooth((yy-830)/48)*smooth((989-yy)/48)
w=wx*wy*owner
effective=effective*(1-w[:,:,None])+profile[:,None,:]*w[:,:,None]
effective=np.clip(effective,-18,18)*owner[:,:,None]
adjusted=np.clip(np.rint(aligned+effective),0,255).astype(np.uint8)
result=base.copy();result[owner]=adjusted[owner]
assert np.array_equal(result[~owner],base[~owner])
assert np.abs(effective).max()<=18
out=P/'proposed-joint-v5.png';assert not out.exists();Image.fromarray(result).save(out)
fields=[]
for n,a in [('flow',flow),('effectiveColorCorrection',effective),('requestedAlphaRamp',alpha)]:
 q=P/('proposal-v5.'+n+'.npy');np.save(q,a);fields.append(ref(q))
for n,a in [('apply-mask',owner),('requestedAlphaRamp',np.uint8(np.rint(alpha*255)))]:
 q=P/('proposal-v5.'+n+'.png');Image.fromarray(a.astype(np.uint8)*255 if a.dtype==bool else a).save(q);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v5',(240,0,1000,180)),('right-perimeter-v5',(840,0,1000,1070)),('lower-perimeter-v5',(240,910,1000,1070)),('west-join-v5',(160,0,480,1070))]:
 q=P/(name+'.png');Image.fromarray(result).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
diff=np.any(result!=base,axis=2);ys,xs=np.nonzero(diff)
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseTarget':ref(P/'edit-target.png'),'source':ref(P/'repair-v3.png'),'sourceCropLTRB':[320,80,920,990],'candidateCropLTRB':[0,2840,600,3750],'joint':ref(out),'fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'actualChangedPixels':int(diff.sum()),'actualChangedJointBBoxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'operation':'Existing registered AI geometry with finite top/right/bottom original-context photometric return. Total effective RGB correction INCLUDING requested alpha return is capped at18, so clipped pixels may not equal requested alpha blend. True W remains AI-painted line geometry with bounded low-gradient lower-stone color support.','alphaRampWidths':{'top':72,'right':96,'bottom':96},'previousBinaryMaskHadAlphaRamp':False,'oldWestUnchanged':True,'outsideAuthorizedAreaUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'candidateNotChanged':True,'actualMaxDisplacementVector':float(np.linalg.norm(flow,axis=2).max()),'actualMaxColorCorrectionRGB':np.abs(effective).max(axis=(0,1)).tolist(),'jacobianMinimumInAppliedPixels':float(jac[owner].min()),'foldedAppliedPixels':int(((jac<=0)&owner).sum()),'sourcePixelScale':1,'sourceUpscaling':False,'codePaintedMissingStructure':False,'accepted':False}
write(P/'proposal-v5.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':v['operation'],'derivedFrom':[ref(P/'edit-target.png'),ref(P/'repair-v3.png')],'mappingRecord':ref(P/'proposal-v5.json'),'actualModel':None,'actualQuality':None,'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Finite registered native support/ramp field','derivedFrom':[ref(P/'edit-target.png'),ref(P/'repair-v3.png')],'mappingRecord':ref(P/'proposal-v5.json')})
print(json.dumps({'proposal':ref(P/'proposal-v5.json'),'joint':ref(out),'displacement':v['actualMaxDisplacementVector'],'color':v['actualMaxColorCorrectionRGB'],'jacobian':v['jacobianMinimumInAppliedPixels']}))

