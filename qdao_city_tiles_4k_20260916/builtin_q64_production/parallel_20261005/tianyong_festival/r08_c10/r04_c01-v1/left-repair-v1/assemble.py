from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
O=Path(__file__).resolve().parent;P=O.parent;REG=P/'registration-v1';S=P/'shifted-curve-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def png(n,a):Image.fromarray(np.rint(a).clip(0,255).astype('uint8')).save(O/n)
def ss(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
raw=np.asarray(Image.open(S/'native.png').convert('RGB'),np.float32);cti=Image.open(S/'original-context.png').convert('RGBA');ctx=np.asarray(cti)[:,:,:3].astype(np.float32);known=np.asarray(cti)[:,:,3]==255
flow=np.load(REG/'flow.npy');oldtone=np.load(REG/'tone.npy');alpha=np.load(REG/'blend-alpha.npy')
xx,yy=np.meshgrid(np.arange(1254,dtype=np.float32),np.arange(1254,dtype=np.float32))
# Separate outer white highlight: original/source paired x residual1px at oldy920..932.
outer_dx=-1.05*ss((yy-260)/120)*(1-ss((yy-424)/64))*ss((xx-35)/40)*(1-ss((xx-145)/70))
flow[:,:,0]+=outer_dx
assert np.abs(flow).max()<=24
aligned=cv2.remap(raw,xx+flow[:,:,0],yy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
corrected=np.clip(aligned+oldtone,0,255)
shifted=np.rint(corrected*alpha[:,:,None]+ctx*(1-alpha[:,:,None])).clip(0,255).astype('uint8')
upper=np.asarray(Image.open(P/'repaired-v1/native.png').convert('RGB'),np.float32)
oldctx=np.asarray(Image.open(P/'repaired-v1/original-context.png').convert('RGBA'))
assembly=upper.copy();assembly[512:]=shifted[:742]
for k in range(128):
 w=float(ss(k/127));assembly[512+k]=upper[512+k]*(1-w)+shifted[k]*w
ax=ss((np.arange(1254)-51)/64)*(1-ss((np.arange(1254)-1024)/64))
for y in range(512):
 a=ax.copy();a[oldctx[y,:,3]!=255]=1;assembly[y]=assembly[y]*a[:,None]+oldctx[y,:,:3]*(1-a[:,None])
before=np.rint(assembly).clip(0,255).astype('uint8');png('before-material.png',before)
ai=np.asarray(Image.open(O/'native.png').convert('RGB'),np.float32)
assert ai.shape==assembly.shape and sha(O/'native.png')==sha(read(O/'tool-response.json')['hostPath'])
# Use only AI-painted flat stone material; all white/bevel contours stay with the aligned native source.
edge=np.interp(np.arange(1254),[0,460,500,600,700,800,850,880,900,1253],[420,306,293,259,221,180,159,146,137,0])
mat_alpha=ss((xx-51)/42)*(1-ss((xx-165)/80))*ss((yy-410)/90)*(1-ss((yy-830)/70))*ss((edge[:,None]-25-xx)/24)
material_delta=np.clip(ai-before.astype(np.float32),-12,12)
after=np.rint(before.astype(np.float32)+material_delta*mat_alpha[:,:,None]).clip(0,255).astype('uint8')
png('joined-r04_c01.png',after);png('material-mask.png',mat_alpha*255)
np.save(O/'flow.npy',flow);np.save(O/'material-alpha.npy',mat_alpha.astype('float32'));np.save(O/'material-delta.npy',material_delta);np.save(O/'outer-highlight-dx.npy',outer_dx)
png('qa-left.png',after[:1139,:320]);png('qa-bottom.png',after[1011:]);png('qa-upper-join.png',after[384:768]);png('qa-right.png',after[:1139,896:]);png('qa-left-material-before-above-after-below.png',np.concatenate([before[460:840,:300],after[460:840,:300]],0));png('qa-white-edge-before-beside-after.png',np.concatenate([before[830:980,50:220],after[830:980,50:220]],1))
req=read(O/'request.json');prep=read(O/'preparation.json');receipt=read(O/'tool-response.json')
write('native.png.generation.json',{'file':str(O/'native.png'),'sha256':sha(O/'native.png'),'generatedAt':None,'observedCompletionAt':receipt['hostObservedFinishedAtUtc'],'recordSavedAtUtc':datetime.now(timezone.utc).isoformat(),'timestampSemantics':'Server generation time unknown; observed tool completion separate','width':1254,'height':1254,'route':'builtin','tool':'image_gen.imagegen','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'prompt':info(O/'prompt.txt'),'references':prep['references'],'globalCropLTRB':req['globalCropLTRB'],'tileLocalCropLTRB':req['tileLocalCropLTRB'],'evidence':{'actualRequest':info(O/'request.json'),'actualToolResponse':info(O/'tool-response.json'),'hostSavedOutput':receipt['hostPath'],'hostOutputSha256':sha(receipt['hostPath']),'copiedByteIdentically':True},'resizedAfterGeneration':False,'upscaled':False,'formalAccepted':False})
params={'method':'Original complete paired contours bounded horizontal registration, plus AI material-only selective correction','sourceGeometry':info(S/'native.png'),'upperSource':info(P/'repaired-v1/native.png'),'sourceBaseRegistration':info(REG/'parameters.json'),'sourceAiLeftRepair':info(O/'native.png'),'outerWhiteHighlightRegistration':{'sampleDx':-1.05,'originalSharedObservationsOldY':[920,924,928,932],'targetX':[113.148,110.548,108.245,106.062],'rawX':[111.998,109.840,107.135,105.072],'field':'C1 yshift260..380 rise,424..488 fall, x35..75 rise145..215 fall','distinctFromLeftGraySlab':True},'maxFlowXY':[float(np.abs(flow[:,:,i]).max()) for i in range(2)],'materialOnly':{'source':info(O/'native.png'),'mask':info(O/'material-alpha.npy'),'delta':info(O/'material-delta.npy'),'maxAppliedDeltaRGB':np.abs(material_delta*mat_alpha[:,:,None]).max((0,1)).tolist(),'contourExclusion':'25px inside fitted white edge,24px falloff; no new AI geometry selected'},'tone':info(REG/'tone.npy'),'flow':info(O/'flow.npy'),'nativeSize':[1254,1254],'nativeScale':1,'originalTileLocalLTRB':[-115,2957,1139,4211],'globalLTRB':[36749,31629,38003,32883],'accepted':False,'joinedIntoCurrent':False}
write('assembly.json',params)
for p in list(O.glob('qa-*.png'))+[O/'joined-r04_c01.png',O/'before-material.png',O/'material-mask.png']:
 write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(S/'native.png'),info(P/'repaired-v1/native.png'),info(O/'native.png')],'operation':'Native-sized bounded mechanical registration and selective AI material composition or QA crop','newModelCalls':0,'actualModel':None,'actualQuality':None,'assembly':info(O/'assembly.json'),'formalAccepted':False,'pendingVisualReview':True})
print(json.dumps({'joined':info(O/'joined-r04_c01.png'),'maxFlowXY':params['maxFlowXY'],'maxAiMaterialColorDelta':params['materialOnly']['maxAppliedDeltaRGB']}))
