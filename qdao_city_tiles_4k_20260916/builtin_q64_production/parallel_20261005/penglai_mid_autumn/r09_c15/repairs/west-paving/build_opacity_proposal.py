"""v8: distinguish bounded tone from opacity return of actual native paintings."""
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
base=np.array(Image.open(P/'proposed-joint-v5.png').convert('RGB')).astype(np.float32)
original=np.array(Image.open(P/'edit-target.png').convert('RGB')).astype(np.float32)
result=base.copy();yy,xx=np.mgrid[:1254,:1254].astype(np.float32);fields=[]
# The top defect is a paint surface, not the corrected grout. Freeze all true lines/wood.
tm=np.array(Image.open(P/'top-local-paint-mask.png'))>0
source=np.array(Image.open(P/'top-local.png').convert('RGB')).astype(np.float32)
tone=np.load(P/'proposal-v7.top-local.tone.npy')
mapped=np.zeros_like(base);mask=np.zeros((1254,1254),bool)
yt,xt=np.nonzero(tm);mapped[yt-547,xt]=np.clip(source[yt,xt]+tone[yt,xt],0,255);mask[yt-547,xt]=True
mask&=(xx>=420)&(xx<825)
t=smooth((yy-80)/72)
# Original and existing v5 pixels supply two exact surface endpoint colors.
w_original=(1-t)*mask
# Native local AI stone paint contributes only inside; opacity vanishes at both returns.
w_ai=(.5*np.sin(np.pi*np.clip((yy-80)/72,0,1))**2)*mask
context=w_original[:,:,None]*original+(1-w_original[:,:,None])*base
result[mask]=(w_ai[:,:,None]*mapped+(1-w_ai[:,:,None])*context)[mask]
fields_data=[('top-original-opacity',w_original),('top-AI-opacity',w_ai)]
# Small lower mask: long right return, short top/bottom/line-protection return.
fixed=np.array(Image.open(P/'lower-west-local-input.png').convert('RGB')).astype(np.float32)
raw=np.array(Image.open(P/'lower-west-local.png').convert('RGB')).astype(np.float32)
lm=np.array(Image.open(P/'lower-west-local-paint-mask.png'))>0
ltone=np.load(P/'proposal-v7.lower-west-local.tone.npy')
ext=lm.copy();ext[:,:625]=ext[:,625:626]
dist=cv.distanceTransform(ext.astype(np.uint8),cv.DIST_L2,5)
a=smooth(dist/16)*smooth((752-xx)/80)*lm
comp=a[:,:,None]*np.clip(raw+ltone,0,255)+(1-a[:,:,None])*fixed
yl,xl=np.nonzero(lm);result[yl+82,xl-305]=comp[yl,xl]
fields_data.append(('lower-local-AI-opacity',a))
result=np.uint8(np.clip(np.rint(result),0,255))
owner=np.zeros((1254,1254),bool);owner[80:990,320:920]=True
assert np.array_equal(result[~owner],original.astype(np.uint8)[~owner])
# Direct top return must now be the actual original bytes, not a clipped approximation.
assert np.array_equal(result[80][mask[80]],original.astype(np.uint8)[80][mask[80]])
out=P/'proposed-joint-v8.png';assert not out.exists();Image.fromarray(result).save(out)
for name,arr in fields_data:
 q=P/('proposal-v8.'+name+'.npy');np.save(q,arr);fields.append(ref(q))
 q=P/('proposal-v8.'+name+'.png');Image.fromarray(np.uint8(np.rint(arr*255))).save(q);fields.append(ref(q))
qa=[]
for name,b in [('upper-perimeter-v8',(240,0,1000,180)),('right-perimeter-v8',(840,0,1000,1070)),('lower-perimeter-v8',(240,910,1000,1070)),('west-join-v8',(160,0,480,1070))]:
 q=P/(name+'.png');Image.fromarray(result).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v5.json'),'baseJoint':ref(P/'proposed-joint-v5.png'),'originalJoint':ref(P/'edit-target.png'),'joint':ref(out),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'localizedAISources':[ref(P/'top-local.png'),ref(P/'lower-west-local.png')],'selectedOriginalMasks':[ref(P/'top-local-paint-mask.png'),ref(P/'lower-west-local-paint-mask.png')],'reuseToneFields':[ref(P/'proposal-v7.top-local.tone.npy'),ref(P/'proposal-v7.lower-west-local.tone.npy')],'newOpacityFields':fields,'qa':qa,'script':ref(Path(__file__).resolve()),'operation':'Finite opacity of real native painted stone layers; top starts at exact original bytes and returns to v5 over72px, AI local texture has zero endpoint opacity. Lower native local paint returns across80px within its small stone-only mask. Tone fields separately capped18; opacity is not clipped as an RGB correction. No geometry created or displaced.','topExactOriginalReturnVerified':True,'oldWestUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'newGeometryWarp':False,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'candidateNotChanged':True,'accepted':False}
write(P/'proposal-v8.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':v['operation'],'derivedFrom':[ref(P/'proposed-joint-v5.png'),ref(P/'edit-target.png'),ref(P/'top-local.png'),ref(P/'lower-west-local.png')],'mappingRecord':ref(P/'proposal-v8.json'),'sourcePixelScale':1,'formalAccepted':False})
for q in fields:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Finite stone-only opacity field','mappingRecord':ref(P/'proposal-v8.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v8.json'),'topOriginalBoundaryBitExact':True}))

