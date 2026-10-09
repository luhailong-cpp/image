from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from types import SimpleNamespace
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools/deps'))
import cv2 as cv
from native_assemble import register_native
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def arr(n):return np.array(Image.open(P/n).convert('RGB'))
original=arr('edit-target.png');base=arr('proposed-joint-v9.png');raw=arr('repair-v3.png')
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
moving=base.copy();moving[:,:320]=raw[:,:320]
known=(xx>=256)&(xx<320)&(yy>=840)&(yy<1010)
owner=(xx>=320)&(xx<448)&(yy>=860)&(yy<990)
_,flow,_,reg=register_native(original,moving,known,owner,['left'],SimpleNamespace(patch=1254,halo=320),max_shift=4.5,tone_cap=0,return_depth=128)
vertical=smooth((yy-860)/28)*smooth((990-yy)/18)
flow*=vertical[:,:,None];flow[~owner]=0
# Preserve total native displacement cap, including v4's already-applied registration.
prior=np.load(P/'proposal-v4.flow.npy')
for _ in range(24):
 dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
 composed=flow+np.stack([cv.remap(prior[:,:,k],xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_LINEAR,borderMode=cv.BORDER_REPLICATE) for k in range(2)],axis=2)
 if jac[owner].min()>=.25 and np.linalg.norm(composed[owner],axis=1).max()<=6:break
 flow*=.75
else:raise RuntimeError('bounded field failed')
aligned=cv.remap(base,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
# Color only low-gradient matched stone samples; preserve edge profile rather than row-color copying.
def gy(a):
 g=cv.cvtColor(a,cv.COLOR_RGB2GRAY).astype(np.float32)
 return np.abs(np.gradient(g,axis=0))
residual=original[:,319].astype(np.float32)-aligned[:,320].astype(np.float32)
safe=(gy(original)[:,319]<8)&(gy(aligned)[:,320]<8)&(np.max(np.abs(residual),axis=1)<30)
weights=cv.GaussianBlur(safe.astype(np.float32)[:,None],(1,0),12)[:,0]
measured=cv.GaussianBlur((residual*safe[:,None])[:,None,:],(1,0),12)[:,0,:]/np.maximum(weights[:,None],1e-6)
tone=np.clip(measured,-18,18)[:,None,:]*vertical[:,:,None]*smooth((448-xx)/128)[:,:,None]*owner[:,:,None]
res=base.copy();res[owner]=np.uint8(np.clip(np.rint(aligned.astype(np.float32)+tone),0,255))[owner]
assert np.array_equal(res[~owner],base[~owner])
out=P/'proposed-joint-v11.png';assert not out.exists();Image.fromarray(res).save(out)
fields=[]
for label,a in [('flow',flow),('composedFlow',composed),('jacobian',jac),('colorCorrection',tone),('endpointResidual',residual),('sameMaterialEndpointMask',safe)]:
 q=P/('proposal-v11.'+label+'.npy');np.save(q,a);fields.append(ref(q))
for label,a in [('apply-mask',owner),('support-mask',known)]:
 q=P/('proposal-v11.'+label+'.png');Image.fromarray(a.astype(np.uint8)*255).save(q);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v11',(240,0,1000,180)),('right-perimeter-v11',(840,0,1000,1070)),('lower-perimeter-v11',(240,910,1000,1070)),('west-join-v11',(160,0,480,1070)),('lower-detail-v11',(256,830,480,1050))]:
 q=P/(name+'.png');Image.fromarray(res).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v9.json'),'baseJoint':ref(P/'proposed-joint-v9.png'),'joint':ref(out),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'additionalCandidateBoxLTRB':[0,3620,128,3750],'trueWestSupport':ref(P/'edit-target.png'),'nativeMovingSupport':ref(P/'repair-v3.png'),'supportDescription':'True old west x256..319,y840..1009 versus corresponding native AI source, then finite return128px, vertical28/18px ramps. Same-material low-gradient endpoint color only; no direct high-gradient row residual transfer.','fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'helper':ref(ROOT/'native_assemble.py'),'registration':reg,'actualMaxAdditionalDisplacement':float(np.linalg.norm(flow[owner],axis=1).max()),'actualMaxComposedDisplacement':float(np.linalg.norm(composed[owner],axis=1).max()),'jacobianMinimumInAppliedPixels':float(jac[owner].min()),'foldedPixels':int((jac[owner]<=0).sum()),'actualMaxAdditionalColorRGB':np.abs(tone).max(axis=(0,1)).tolist(),'oldWestUnchanged':True,'topApprovedAreaUnchanged':True,'rightApprovedAreaUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'candidateNotChanged':True,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'accepted':False}
write(P/'proposal-v11.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':'Bounded native microregistration of existing grout and color matching of same-material stone endpoints','derivedFrom':[ref(P/'proposed-joint-v9.png'),ref(P/'edit-target.png'),ref(P/'repair-v3.png')],'mappingRecord':ref(P/'proposal-v11.json'),'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Native finite-support registration or color field/mask','mappingRecord':ref(P/'proposal-v11.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v11.json'),'shift':v['actualMaxAdditionalDisplacement'],'composed':v['actualMaxComposedDisplacement'],'jacobian':v['jacobianMinimumInAppliedPixels'],'tone':v['actualMaxAdditionalColorRGB']}))

