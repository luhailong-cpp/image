from pathlib import Path
import datetime,hashlib,json,shutil,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;S=R.parents[1]
sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'))
import cv2
O=R/sys.argv[1];host=Path(sys.argv[2])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
req=json.loads((O/'request.json').read_text());prep=json.loads((O/'preparation.json').read_text())
shutil.copy2(host,O/'native.png')
raw=np.array(Image.open(O/'native.png').convert('RGB'));assert raw.shape==(1254,1254,3)
ctx=np.array(Image.open(O/'context.png').convert('RGBA'));known=ctx[:,:,3]==255
context=raw.copy();context[known]=ctx[:,:,:3][known]
kin=cv2.distanceTransform(known.astype(np.uint8),cv2.DIST_L2,5)
kout=cv2.distanceTransform((~known).astype(np.uint8),cv2.DIST_L2,5)
smooth=lambda t:t*t*(3-2*t)
retreat={'r04_c02':200}.get(req['patch'],0)
max_shift=24 if req['patch']=='r03_c02_seed' else 4
weight=np.where(known,smooth(np.clip((180+retreat-kin)/100,0,1))*smooth(np.clip((kin-retreat+80)/80,0,1)),smooth(np.clip((80-kout)/80,0,1)) if not retreat else 0).astype(np.float32)
flow=cv2.calcOpticalFlowFarneback(cv2.cvtColor(context,cv2.COLOR_RGB2GRAY),cv2.cvtColor(raw,cv2.COLOR_RGB2GRAY),None,0.5,4,51,5,7,1.5,0)
flow=np.clip(cv2.GaussianBlur(flow,(0,0),5),-max_shift,max_shift)*weight[:,:,None]
extended_flow=False
if req['patch']=='r03_c02_seed':
 assert known[512:].all() and not known[:512].any()
 # Estimate contour displacement only where actual context exists, then extend it
 # continuously to the new side. Using raw pixels as fake unknown context gave
 # a zero-flow cliff at the alpha boundary and made the earlier joins wave.
 anchor=np.mean(flow[552:592],axis=0)
 anchor[:,1]=0
 flow[:,:,1]=0
 for ry in range(512):flow[ry]=anchor*smooth(np.float32(ry/511))
 for ry in range(512,572):
  t=smooth(np.float32((ry-512)/60));flow[ry]=anchor*(1-t)+flow[ry]*t
 extended_flow=True
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
aligned=cv2.remap(raw,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
delta=context.astype(np.float32)-aligned.astype(np.float32)
delta[~known]=0
norm=cv2.GaussianBlur(known.astype(np.float32),(0,0),24)
tone=cv2.GaussianBlur(delta,(0,0),24)/np.maximum(norm[:,:,None],0.001)
tone=np.clip(tone,-18,18)*weight[:,:,None]
aligned=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
alpha=np.where(known,1-smooth(np.clip((kin-retreat)/128,0,1)),1).astype(np.float32)
joined=np.clip(np.rint(context*(1-alpha[:,:,None])+aligned*alpha[:,:,None]),0,255).astype(np.uint8)
assert np.array_equal(joined[known & (kin>=180+retreat)],ctx[:,:,:3][known & (kin>=180+retreat)])
if not extended_flow:assert np.array_equal(joined[(~known)&(kout>=80)],raw[(~known)&(kout>=80)])
Image.fromarray(joined).save(O/'joined.png')
Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(O/'mask.png')
np.save(O/'flow.npy',flow,allow_pickle=False);np.save(O/'tone.npy',tone,allow_pickle=False)
generation={'file':str(O/'native.png'),'sha256':sha(O/'native.png'),'generatedAt':None,'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((R/'config.snapshot.json').read_text()),'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool does not expose model, quality, size selectors or actual model and quality metadata.','prompt':str(O/'prompt.txt'),'references':prep['references'],'evidence':{'toolResponse':info(O/'tool-response.json'),'hostSavedOriginal':str(host),'hostSha256':sha(host),'copyByteIdentical':sha(host)==sha(O/'native.png')}}
(O/'native.png.generation.json').write_text(json.dumps(generation,indent=2),encoding='utf-8')
assembly={'patch':req['patch'],'globalCropLTRB':req['globalCropLTRB'],'canvasCropLTRB':req['canvasCropLTRB'],'candidate':info(O/'joined.png'),'derivedFrom':[info(O/'native.png'),info(O/'context.png')],'generationRecord':info(O/'native.png.generation.json'),'operation':'Native-dimension bounded optical registration and local tone correction only near unknown-known boundary, no scaling or creative painting.','nativePixels':[1254,1254],'maxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),'maxToneRGB':np.abs(tone).max(axis=(0,1)).tolist(),'knownRetreatToAvoidBevelPixels':retreat,'knownUnchangedBeyondPixels':180+retreat,'newUnchangedBeyond80':True,'knownNativeContextPixels':int(known.sum()),'newlyFilledPixels':int((~known).sum()),'fields':[info(O/f) for f in ('flow.npy','tone.npy','mask.png')],'referenceGuidePixelsInOutput':False,'formalAccepted':False,'visualQaPending':True}
assembly['maximumAllowedShiftPixels']=max_shift
assembly['flowExtendedFromKnownOverlap']=extended_flow
if extended_flow:
 assembly['newUnchangedBeyond80']=False
 assembly['resamplingScope']='Native 1254 geometry; known-overlap displacement smoothly extends across new upper512 from zero at y0 to measured anchor at y512, max24px. No source enlargement.'
assembly['script']=info(__file__)
(O/'assembly.json').write_text(json.dumps(assembly,indent=2),encoding='utf-8')
(O/'joined.png.generation.json').write_text(json.dumps({'file':str(O/'joined.png'),'sha256':sha(O/'joined.png'),'derivedFrom':assembly['derivedFrom'],'assembly':info(O/'assembly.json'),'newModelCalls':0,'operation':assembly['operation']},indent=2),encoding='utf-8')
print(json.dumps(assembly))
