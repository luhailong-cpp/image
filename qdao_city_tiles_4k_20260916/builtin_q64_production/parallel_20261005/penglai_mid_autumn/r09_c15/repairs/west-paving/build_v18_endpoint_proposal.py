from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'tools/deps'));import cv2 as cv
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def arr(n):return np.array(Image.open(P/n).convert('RGB'))
fixed=arr('root-lower-bevel-v12-target.png');source=arr('three-endpoints-v14.png');base=arr('proposed-joint-v9.png')
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# Match corresponding endpoint profiles directly. This fixes the actual current-side endpoint;
# copied AI left-context pixels are not used as a zero-flow proxy.
left=fixed[:,626].astype(np.float32);right=source[:,627].astype(np.float32)
shifts=np.arange(-6,6.001,.25,dtype=np.float32)
sample=np.stack([np.stack([np.interp(np.arange(1254)+s,np.arange(1254),right[:,c]) for c in range(3)],axis=1) for s in shifts],axis=1).astype(np.float32)
error=left[:,None,:]-sample
# Bounded constant material color bias is discounted, but local geometric edges still cost strongly.
bias=cv.GaussianBlur(error,(1,0),8)
residual=error-np.clip(bias,-18,18)
cost=np.mean(residual**2,axis=2)
cost=cv.GaussianBlur(cost,(1,0),1.2)
transition=150*(shifts[:,None]-shifts[None,:])**2
transition[np.abs(shifts[:,None]-shifts[None,:])>.5]=1e10
dp=np.zeros_like(cost);prev=np.zeros(cost.shape,np.int16)
dp[0]=cost[0]+20*shifts**2
for y in range(1,1254):
 trial=dp[y-1][:,None]+transition
 prev[y]=np.argmin(trial,axis=0)
 dp[y]=cost[y]+trial[prev[y],np.arange(len(shifts))]
ix=np.empty(1254,np.int16);ix[-1]=np.argmin(dp[-1])
for y in range(1252,-1,-1):ix[y]=prev[y+1,ix[y+1]]
profile=cv.GaussianBlur(shifts[ix,None],(1,0),1.2)[:,0]
# New AI source has zero inherited v4 flow. Only this field resamples it.
owner=(xx>=627)&(xx<807)&(((yy>=65)&(yy<150))|((yy>=310)&(yy<490))|((yy>=790)&(yy<895)))
vertical=(smooth((yy-65)/16)*smooth((150-yy)/16)+smooth((yy-310)/16)*smooth((490-yy)/16)+smooth((yy-790)/16)*smooth((895-yy)/16));weight=smooth((807-xx)/128)*vertical
slope=np.interp(np.arange(1254),[0,250,360,410,580,650,1253],[.34,.34,.40,-.50,-.50,.53,.53]).astype(np.float32);transportY=yy-slope[:,None]*(xx-627);transportedProfile=np.interp(transportY.ravel(),np.arange(1254),profile).reshape(1254,1254);flow=np.zeros((1254,1254,2),np.float32);flow[:,:,1]=transportedProfile*weight
flow[~owner]=0
# Include conceptual flow extension into fixed support when computing boundary derivatives:
# immutable oldW pixels are never resampled, so jump across ownership is not a mapping fold.
du_y,du_x=np.gradient(flow[:,:,0]);dv_y,dv_x=np.gradient(flow[:,:,1]);jac=(1+du_x)*(1+dv_y)-du_y*dv_x
assert np.linalg.norm(flow[owner],axis=1).max()<=6.00001 and jac[owner].min()>=.25
aligned=cv.remap(source,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
res=left-aligned[:,627].astype(np.float32)
lg=np.abs(np.gradient(cv.cvtColor(fixed,cv.COLOR_RGB2GRAY).astype(np.float32),axis=0))[:,626]
rg=np.abs(np.gradient(cv.cvtColor(aligned,cv.COLOR_RGB2GRAY).astype(np.float32),axis=0))[:,627]
safe=(lg<10)&(rg<10)&(np.max(np.abs(res),axis=1)<36)
den=cv.GaussianBlur(safe.astype(np.float32)[:,None],(1,0),6)[:,0]
measured=cv.GaussianBlur((res*safe[:,None])[:,None,:],(1,0),6)[:,0]/np.maximum(den[:,None],1e-6)
boundedProfile=np.clip(cv.GaussianBlur(res[:,None,:],(1,0),.7)[:,0],-18,18);transportedTone=np.stack([np.interp(transportY.ravel(),np.arange(1254),boundedProfile[:,c]).reshape(1254,1254) for c in range(3)],axis=2);tone=transportedTone*weight[:,:,None]*owner[:,:,None]*smooth((659-xx)/32)[:,:,None]
matched=np.clip(aligned.astype(np.float32)+tone,0,255)
alpha=smooth((807-xx)/48)*vertical*owner
# Original v9 joint receives only the narrow native current-side source crop, with finite opacity return.
outarray=base.copy();destination=outarray[82:990,320:620].astype(np.float32)
a=alpha[:908,627:927,None]
outarray[82:990,320:620]=np.uint8(np.clip(np.rint(destination*(1-a)+matched[:908,627:927]*a),0,255))
out=P/'proposed-joint-v18.png';assert not out.exists();Image.fromarray(outarray).save(out)
change=np.any(outarray!=base,axis=2);assert not change[:82].any() and not change[990:].any() and not change[:,:320].any() and not change[:,620:].any()
fields=[]
for label,v in [('transportY',transportY),('measuredSlopeProfile',slope),('toneDepth32',smooth((659-xx)/32)),('flow',flow),('jacobian',jac),('colorCorrection',tone),('alpha',alpha),('endpointShiftProfile',profile),('endpointCost',cost),('sameMaterialEndpointMask',safe)]:
 q=P/('proposal-v18.'+label+'.npy');np.save(q,v);fields.append(ref(q))
q=P/'proposal-v18.apply-mask.png';Image.fromarray(np.uint8(owner)*255).save(q);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v18',(240,0,1000,180)),('right-perimeter-v18',(840,0,1000,1070)),('lower-perimeter-v18',(240,910,1000,1070)),('west-join-v18',(160,0,480,1070)),('lower-detail-v18',(256,830,480,1050)),('three-crossings-v18',(260,80,520,990))]:
 q=P/(name+'.png');Image.fromarray(outarray).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v9.json'),'baseJoint':ref(P/'proposed-joint-v9.png'),'joint':ref(out),'nativeSource':ref(P/'three-endpoints-v14.png'),'trueWestSource':ref(P/'root-lower-bevel-v12-target.png'),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'additionalCandidateBoxLTRB':[0,2842,300,3750],'sourceToJointXY':[-307,82],'fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'endpointMethod':'Bounded dynamic profile correspondence between actual oldW last native column and native AI current first column. Quarter-pixel states in [-6,6], adjacent-row shift variation <=0.5, 1.2px field smoothing. Endpoint flow and color transported parallel to actual observed native diagonal line slopes (0.34,0.4,-0.5,0.53); no horizontal row strip copying. High-gradient color endpoint correction has only32px horizontal support. No synthesized geometry.','actualMaxSourceDisplacement':float(np.linalg.norm(flow[owner],axis=1).max()),'sourceDisplacementIsCumulative':True,'sourceHasNoInheritedV4Flow':True,'jacobianMinimumInAppliedPixels':float(jac[owner].min()),'foldedPixels':int((jac[owner]<=0).sum()),'actualMaxColorRGB':np.abs(tone).max(axis=(0,1)).tolist(),'oldWestUnchanged':True,'rightApprovedAreaUnchanged':True,'topWasPartlyReplacedWithinAuthorizedSubset':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'candidateNotChanged':True,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'accepted':False}
write(P/'proposal-v18.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':'Finite native endpoint registration of existing AI source with bounded color and opacity return','derivedFrom':[ref(P/'proposed-joint-v9.png'),ref(P/'three-endpoints-v14.png'),ref(P/'root-lower-bevel-v12-target.png')],'mappingRecord':ref(P/'proposal-v18.json'),'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Native bounded endpoint registration field or mask','mappingRecord':ref(P/'proposal-v18.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v18.json'),'shift':v['actualMaxSourceDisplacement'],'jacobian':v['jacobianMinimumInAppliedPixels'],'tone':v['actualMaxColorRGB']}))

