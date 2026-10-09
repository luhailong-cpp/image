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
tone=np.zeros_like(src,np.float32)
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
out=P/'proposed-joint-v14.png';assert not out.exists();Image.fromarray(result).save(out)
fields=[]
for label,v in [('alpha',alpha),('colorCorrection',tone),('sameMaterialEndpointMask',safe)]:
 q=P/('proposal-v14.'+label+'.npy');np.save(q,v);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v14',(240,0,1000,180)),('right-perimeter-v14',(840,0,1000,1070)),('lower-perimeter-v14',(240,910,1000,1070)),('west-join-v14',(160,0,480,1070)),('lower-detail-v14',(256,830,480,1050)),('three-crossings-v14',(260,80,520,990))]:
 q=P/(name+'.png');Image.fromarray(result).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v9.json'),'baseJoint':ref(P/'proposed-joint-v9.png'),'joint':ref(out),'nativeSource':ref(P/'three-endpoints-v14.png'),'trueWestSource':ref(P/'root-lower-bevel-v12-target.png'),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'additionalCandidateBoxLTRB':[0,2907,180,3737],'sourceToJointXY':[-307,82],'nativeSourceBoxesLTRB':boxes,'fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'actualMaxSourceDisplacement':0,'sourceDisplacementIsCumulative':True,'sourceHasNoInheritedV4Flow':True,'jacobian':1,'actualMaxColorRGB':np.abs(tone).max(axis=(0,1)).tolist(),'oldWestUnchanged':True,'rightApprovedAreaUnchanged':True,'topFirst147JointRowsUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'candidateNotChanged':True,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'accepted':False}
write(P/'proposal-v14.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':'Three native AI inpainted endpoint patches, finite opacity return and bounded same-material tone; no registration','derivedFrom':[ref(P/'proposed-joint-v9.png'),ref(P/'three-endpoints-v14.png'),ref(P/'root-lower-bevel-v12-target.png')],'mappingRecord':ref(P/'proposal-v14.json'),'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Finite native local blend/color field','mappingRecord':ref(P/'proposal-v14.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v14.json'),'tone':v['actualMaxColorRGB']}))

