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
def arr(n):return np.array(Image.open(P/n).convert('RGB'))
base=arr('proposed-joint-v9.png');fixed=arr('root-lower-bevel-v12-target.png');src=arr('three-endpoints-v14.png')
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
alpha=np.zeros((1254,1254),np.float32)
boxes=[[627,65,807,150],[627,310,807,490],[627,790,807,895]]
for x0,y0,x1,y1 in boxes:
 alpha+=((xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1))*smooth((x1-xx)/48)*smooth((yy-y0)/16)*smooth((y1-yy)/16)
originalsrc=src.copy()
left=fixed[:,626].astype(np.float32); right=src[:,627].astype(np.float32)
ranges=[(90,135),(320,370),(400,480),(810,875)]
values=[];measurements=[]
for lo,hi in ranges:
 scores=[]
 for shift in np.arange(-6,6.001,.125):
  sampled=np.stack([np.interp(np.arange(lo,hi)+shift,np.arange(1254),right[:,c]) for c in range(3)],axis=1)
  residual=left[lo:hi]-sampled
  bias=np.clip(np.median(residual,axis=0),-18,18)
  score=float(np.mean((residual-bias)**2))
  scores.append((float(shift),score))
 best=min(scores,key=lambda v:v[1]);values.append(best[0])
 measurements.append({'targetRows':[lo,hi],'actualWestColumn':626,'nativeSourceColumn':627,'bestShiftY':best[0],'candidateShiftScorePairs':scores})
profile=np.interp(np.arange(1254),[(lo+hi)/2 for lo,hi in ranges],values).astype(np.float32)
profile=cv.GaussianBlur(profile[:,None],(1,0),12)[:,0]
flow=np.zeros((1254,1254,2),np.float32)
flow[:,:,1]=profile[:,None]*smooth((807-xx)/128)*alpha
flow[alpha==0]=0
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1])
jac=(1+dxu)*(1+dyv)-dyu*dxv
assert np.linalg.norm(flow,axis=2).max()<=6.00001
assert jac[alpha>0].min()>=.25
src=cv.remap(originalsrc,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
# Measure only low-gradient endpoint material color, not geometry-bearing highlight edges.
left=fixed[:,626].astype(np.float32);right=src[:,627].astype(np.float32);res=left-right
def grad(a):return np.abs(np.gradient(cv.cvtColor(a,cv.COLOR_RGB2GRAY).astype(np.float32),axis=0))
safe=(grad(fixed)[:,626]<8)&(grad(src)[:,627]<8)&(np.max(np.abs(res),axis=1)<30)
den=cv.GaussianBlur(safe.astype(np.float32)[:,None],(1,0),8)[:,0]
prof=cv.GaussianBlur((res*safe[:,None])[:,None,:],(1,0),8)[:,0]/np.maximum(den[:,None],1e-6)
tone=np.clip(prof,-18,18)[:,None,:]*smooth((807-xx)/128)[:,:,None]*(alpha>0)[:,:,None]
matched=np.clip(src.astype(np.float32)+tone,0,255)
result=base.copy()
a=alpha[:908,627:927,None];d=base[82:990,320:620].astype(np.float32)
result[82:990,320:620]=np.uint8(np.clip(np.rint(d*(1-a)+matched[:908,627:927]*a),0,255))
assert np.array_equal(result[:,:320],base[:,:320]) and np.array_equal(result[:,620:],base[:,620:]) and np.array_equal(result[:147],base[:147]) and np.array_equal(result[977:],base[977:])
out=P/'proposed-joint-v15.png';assert not out.exists();Image.fromarray(result).save(out)
fields=[]
for label,v in [('alpha',alpha),('flow',flow),('jacobian',jac),('colorCorrection',tone),('sameMaterialEndpointMask',safe)]:
 q=P/('proposal-v15.'+label+'.npy');np.save(q,v);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v15',(240,0,1000,180)),('right-perimeter-v15',(840,0,1000,1070)),('lower-perimeter-v15',(240,910,1000,1070)),('west-join-v15',(160,0,480,1070)),('lower-detail-v15',(256,830,480,1050)),('three-crossings-v15',(260,80,520,990))]:
 q=P/(name+'.png');Image.fromarray(result).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v9.json'),'baseJoint':ref(P/'proposed-joint-v9.png'),'joint':ref(out),'nativeSource':ref(P/'three-endpoints-v14.png'),'trueWestSource':ref(P/'root-lower-bevel-v12-target.png'),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'additionalCandidateBoxLTRB':[0,2907,180,3737],'sourceToJointXY':[-307,82],'nativeSourceBoxesLTRB':boxes,'fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'actualMaxSourceDisplacement':float(np.linalg.norm(flow,axis=2).max()),'measuredNativeEndpointCorrespondence':measurements,'sourceDisplacementIsCumulative':True,'sourceHasNoInheritedV4Flow':True,'jacobianMinimumInAppliedPixels':float(jac[alpha>0].min()),'actualMaxColorRGB':np.abs(tone).max(axis=(0,1)).tolist(),'oldWestUnchanged':True,'rightApprovedAreaUnchanged':True,'topFirst147JointRowsUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'candidateNotChanged':True,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'accepted':False}
write(P/'proposal-v15.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':'Three native AI inpainted endpoint patches, finite opacity return and bounded same-material tone; bounded native source registration','derivedFrom':[ref(P/'proposed-joint-v9.png'),ref(P/'three-endpoints-v14.png'),ref(P/'root-lower-bevel-v12-target.png')],'mappingRecord':ref(P/'proposal-v15.json'),'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Finite native local blend/color field','mappingRecord':ref(P/'proposal-v15.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v15.json'),'tone':v['actualMaxColorRGB']}))

