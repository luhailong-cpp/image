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
base=np.asarray(Image.open(P/'proposed-joint-v5.png').convert('RGB'));result=base.copy();inserts=[]
for name,offset,side in [('top-local',(0,-547),'top'),('lower-west-local',(-305,82),'left')]:
 fixed=np.asarray(Image.open(P/(name+'-input.png')).convert('RGB')).astype(np.float32)
 raw=np.asarray(Image.open(P/(name+'.png')).convert('RGB')).astype(np.float32)
 mask=np.asarray(Image.open(P/(name+'-paint-mask.png')))>0;ym,xm=np.nonzero(mask)
 yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
 ext=mask.copy()
 if side=='top':
  ext[:627]=ext[627]
  profile=np.median(fixed[611:627]-raw[611:627],axis=0)
  profile=cv.GaussianBlur(profile[None,:,:],(0,1),5)[0]
  tone=np.clip(profile[None,:,:],-18,18)*smooth((48-(yy-627))/48)[:,:,None]
 else:
  ext[:,:625]=ext[:,625:626]
  profile=np.median(fixed[:,609:625]-raw[:,609:625],axis=1)
  profile=cv.GaussianBlur(profile[:,None,:],(1,0),3)[:,0]
  tone=np.clip(profile[:,None,:],-18,18)*smooth((64-(xx-625))/64)[:,:,None]
 tone=np.broadcast_to(tone,raw.shape).copy()*mask[:,:,None]
 distance=cv.distanceTransform(ext.astype(np.uint8),cv.DIST_L2,5)
 alpha=smooth(distance/16)*mask
 corrected=np.clip(np.rint(raw+tone),0,255)
 # Opacity combines actual existing AI paintings only; grout/object masks are protected.
 composite=np.clip(np.rint(alpha[:,:,None]*corrected+(1-alpha[:,:,None])*fixed),0,255).astype(np.uint8)
 dx=xm+offset[0];dy=ym+offset[1];result[dy,dx]=composite[ym,xm]
 fields=[]
 for label,a in [('alpha',alpha),('tone',tone)]:
  q=P/('proposal-v7.'+name+'.'+label+'.npy');np.save(q,a);fields.append(ref(q))
 q=P/('proposal-v7.'+name+'.alpha.png');Image.fromarray(np.uint8(np.rint(alpha*255))).save(q);fields.append(ref(q))
 inserts.append({'source':ref(P/(name+'.png')),'fixedContext':ref(P/(name+'-input.png')),'mask':ref(P/(name+'-paint-mask.png')),'sourceXYToJointXYOffset':list(offset),'selectedMaskPixels':int(mask.sum()),'alphaRule':'16px smoothstep distance to mask return edges; exempt true target join side, preserve every black-mask pixel','trueJoinSide':side,'fields':fields,'actualMaxToneCorrectionRGB':np.abs(tone).max(axis=(0,1)).tolist(),'maxAllowedToneCorrection':18,'flow':0,'sourcePixelScale':1,'geometryProtected':'Top is stone-only; lower excludes20px each side of the existing grout/bevel.'})
out=P/'proposed-joint-v7.png';assert not out.exists();Image.fromarray(result).save(out)
owner=np.zeros((1254,1254),bool);owner[80:990,320:920]=True;original=np.asarray(Image.open(P/'edit-target.png').convert('RGB'))
assert np.array_equal(result[~owner],original[~owner])
qa=[]
for name,b in [('upper-perimeter-v7',(240,0,1000,180)),('right-perimeter-v7',(840,0,1000,1070)),('lower-perimeter-v7',(240,910,1000,1070)),('west-join-v7',(160,0,480,1070))]:
 q=P/(name+'.png');Image.fromarray(result).crop(b).save(q);rec={**ref(q),'cropOfProposedJointLTRB':list(b),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA'};qa.append(rec);write(Path(str(q)+'.generation.json'),{**rec,'operation':'Exact unscaled crop','derivedFrom':ref(out)})
v={'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'independent_proposal_not_applied','candidateSource':ref(P.parent.parent/'output/r09_c15-candidate.png'),'baseProposal':ref(P/'proposal-v5.json'),'baseJoint':ref(P/'proposed-joint-v5.png'),'joint':ref(out),'candidateCropLTRB':[0,2840,600,3750],'jointCropLTRB':[320,80,920,990],'localizedAIInserts':inserts,'qa':qa,'script':ref(Path(__file__).resolve()),'oldWestUnchanged':True,'candidateX600AndAfterUnchanged':True,'candidateY3750AndAfterUnchanged':True,'candidateSouth320Unchanged':True,'newGeometryWarp':False,'codePaintedMissingStructure':False,'sourcePixelScale':1,'sourceUpscaling':False,'candidateNotChanged':True,'accepted':False,'methodNote':'New localized opacity masks blend actual native stone paintings with fixed local input, not geometry reconstruction. Bounded additional tone belongs solely to these new AI sources; base v5 field limits remain unchanged. All grout and wood excluded from these localized edits.'}
write(P/'proposal-v7.json',v)
write(Path(str(out)+'.generation.json'),{**ref(out),'createdAt':v['createdAt'],'operation':v['methodNote'],'derivedFrom':[ref(P/'proposed-joint-v5.png'),ref(P/'top-local.png'),ref(P/'lower-west-local.png')],'mappingRecord':ref(P/'proposal-v7.json'),'sourcePixelScale':1,'formalAccepted':False})
for ins in inserts:
 for q in ins['fields']:write(Path(q['file']+'.generation.json'),{**q,'createdAt':v['createdAt'],'operation':'Local native stone-only opacity/tone field','source':ins['source'],'fixedContext':ins['fixedContext'],'mappingRecord':ref(P/'proposal-v7.json')})
print(json.dumps({'joint':ref(out),'proposal':ref(P/'proposal-v7.json'),'toneMax':[ins['actualMaxToneCorrectionRGB'] for ins in inserts]}))

