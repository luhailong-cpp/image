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
original=np.asarray(Image.open(P/'edit-target.png').convert('RGB')).astype(np.float32)
base=np.asarray(Image.open(P/'proposed-joint-v9.png').convert('RGB')).astype(np.float32)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# Match actual adjacent painted endpoints, including the already aligned grout highlight.
# No excluded20px band: that band froze the unwanted light/color step in earlier proposals.
raw=original[:,319]-base[:,320]
profile=cv.GaussianBlur(raw[:,None,:],(1,0),.85)[:,0,:]
profile=np.clip(profile,-18,18)
vertical=smooth((yy-860)/28)*smooth((990-yy)/18)
horizontal=smooth((448-xx)/128)
owner=(xx>=320)&(xx<448)&(yy>=860)&(yy<990)
field=profile[:,None,:]*vertical[:,:,None]*horizontal[:,:,None]*owner[:,:,None]
res=base.copy();res[owner]=np.clip(np.rint(base+field),0,255)[owner];res=np.uint8(res)
assert np.array_equal(res[:,:320],base.astype(np.uint8)[:,:320]);assert np.array_equal(res[:860],base.astype(np.uint8)[:860]);assert np.array_equal(res[990:],base.astype(np.uint8)[990:]);assert np.array_equal(res[:,448:],base.astype(np.uint8)[:,448:])
out=P/'proposed-joint-v10.png';assert not out.exists();Image.fromarray(res).save(out)
fields=[]
for label,a in [('colorCorrection',field),('measuredEndpointResidual',raw),('boundedEndpointProfile',profile)]:
 q=P/('proposal-v10.'+label+'.npy');np.save(q,a);fields.append(ref(q))
q=P/'proposal-v10.apply-mask.png';Image.fromarray(owner.astype(np.uint8)*255).save(q);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v10',(240,0,1000,180)),('right-perimeter-v10',(840,0,1000,1070)),('lower-perimeter-v10',(240,910,1000,1070)),('west-join-v10',(160,0,480,1070))]:
 q=P/(name+'.png');Image.fromarray(res).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v9.json'),'baseJoint':ref(P/'proposed-joint-v9.png'),'joint':ref(out),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'additionalCandidateColorBoxLTRB':[0,3620,128,3750],'trueWestSupport':ref(P/'edit-target.png'),'supportDescription':'Actual fixed west last pixel X319 versus current native repaired endpoint X320, same row.0.85px Gaussian only smooths the color profile, never the artwork. All contour pixels included; nogeometry shift.','fields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'additionalDisplacement':0,'additionalJacobian':1,'actualMaxAdditionalColorCorrectionRGB':np.abs(field).max(axis=(0,1)).tolist(),'maxAllowedAdditionalColorCorrectionRGB':18,'finiteReturn':'128px horizontally into current tile; vertical860..888 ramp, full888..972, return972..990 in joint coordinates','oldWestUnchanged':True,'topApprovedAreaUnchanged':True,'rightApprovedAreaUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'candidateNotChanged':True,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'accepted':False}
write(P/'proposal-v10.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':'Bounded native endpoint color matching of small true-west lower stone/grout highlight, zero geometry change','derivedFrom':[ref(P/'proposed-joint-v9.png'),ref(P/'edit-target.png')],'mappingRecord':ref(P/'proposal-v10.json'),'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Bounded actual-west color endpoint field or mask','mappingRecord':ref(P/'proposal-v10.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v10.json'),'maxTone':v['actualMaxAdditionalColorCorrectionRGB'],'endpointRawMax':np.abs(raw[888:972]).max(axis=0).tolist()}))

