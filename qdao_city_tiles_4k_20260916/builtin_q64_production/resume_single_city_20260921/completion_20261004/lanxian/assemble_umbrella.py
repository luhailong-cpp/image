from pathlib import Path
import datetime,hashlib,importlib.util,json,re,shutil,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'lanxian_day/umbrella-repair';S=R.parents[1];A=S.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'))
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prep=read(O/'preparation.json');resp=read(O/'tool-response.json');cached=Path(re.search(r' as (.+?\.png) by default\.',resp['response']['output_hint'],re.S).group(1))
native=O/'native.png'
if not native.exists():shutil.copy2(cached,native)
assert sha(native)==sha(cached)
im=Image.open(native);im.load();assert im.size==(1254,1254)
generation={**info(native),'width':im.width,'height':im.height,'format':im.format,'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':prep['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'generatedAt':None,'observedStartedAtUtc':resp['hostObservedStartedAtUtc'],'observedFinishedAtUtc':resp['hostObservedFinishedAtUtc'],'unverifiedReason':'Host managed builtin tool exposes no actual model, quality or server generation timestamp.','request':info(O/'request.json'),'prompt':info(O/'prompt.txt'),'references':prep['references'],'editBefore':prep['source'],'evidence':{'response':info(O/'tool-response.json'),'cachedOriginal':info(cached),'byteIdenticalCopy':True},'nativeUpscaled':False}
write(O/'native.png.generation.json',generation)
source=Path(prep['source']['file']);assert sha(source)==prep['source']['sha256']
before=np.array(Image.open(source).convert('RGB'));x0,y0,x1,y1=prep['cropLTRB'];context=before[y0:y1,x0:x1];n=np.array(im.convert('RGB'))
assert np.array_equal(context,np.array(Image.open(O/'context.png').convert('RGB')))
def pink(a):
 f=a.astype(np.float32);return (f[:,:,0]>1.23*f[:,:,1])&(f[:,:,2]>1.10*f[:,:,1])&(f[:,:,0]>140)
yy,xx=np.mgrid[:1254,:1254]
region=(pink(context)|pink(n))&(yy<1160)
region=cv2.dilate(region.astype(np.uint8),np.ones((65,65),np.uint8))
dist=cv2.distanceTransform(region,cv2.DIST_L2,5)
a=np.clip(dist/24,0,1);a=a*a*(3-2*a)
outer=np.minimum.reduce([yy,1253-yy,1253-xx]).astype(np.float32)
f=np.clip(outer/96,0,1);a*=f*f*(3-2*f)
mask=np.rint(a*255).astype(np.uint8)
hp=A/'builtin_q64_production/tools/mechanical_join.py';spec=importlib.util.spec_from_file_location('mechanical',hp);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
joined,flow,tone,reg=helper.registered_join(context,n,mask,edges=('top','right','bottom'),max_shift=4.0,flow_inner=128.0,flow_full=48.0,tone_inner=160.0,tone_full=64.0,match_tone=True)
after=before.copy();after[y0:y1,x0:x1]=joined
allowed=np.zeros((4096,4096),bool);allowed[y0:y1,x0:x1]=mask>0
assert np.array_equal(after[~allowed],before[~allowed])
out=O/'candidate-v1';out.mkdir(exist_ok=False)
P=out/'r08_c06.png';Image.fromarray(after).save(P);Image.fromarray(joined).save(out/'context-after.png');Image.fromarray(mask).save(out/'mask.png');np.save(out/'flow.npy',flow,allow_pickle=False);np.save(out/'tone.npy',tone,allow_pickle=False)
views=[]
for label,box in [('top',(0,2320,1380,2660)),('bottom',(0,3480,1380,3824)),('left',(0,2320,320,3824)),('right',(1080,2320,1380,3824)),('affected-y3072',(0,2816,1380,3328)),('affected-x1024',(768,2320,1280,3824))]:
 f=out/(label+'.png');Image.fromarray(after).crop(box).save(f);views.append({'id':label,**info(f),'cropLTRB':list(box),'resized':False})
record={'candidate':{**info(P),'pixels':[4096,4096]},'derivedFrom':[prep['source'],{**info(native),'generation':info(O/'native.png.generation.json')}],'cropLTRB':prep['cropLTRB'],'operation':'Native AI repair of pink umbrella ribs only, gated by source/output pink material union and 32px contour margin; 24px local mask taper,96px top/right/bottom crop taper; existing bounded attachment registration. Left tile boundary can change inside umbrella as no west neighbor exists in scoped current group.','registration':reg,'mask':info(out/'mask.png'),'flow':info(out/'flow.npy'),'tone':info(out/'tone.npy'),'sourceUnchanged':sha(source)==prep['source']['sha256'],'outsideMaskUnchanged':True,'nativeUpscaled':False,'changedPixels':int(np.any(after!=before,axis=2).sum()),'outerEdgesUnchanged':{'north':bool(np.array_equal(before[0],after[0])),'south':bool(np.array_equal(before[-1],after[-1])),'west':bool(np.array_equal(before[:,0],after[:,0])),'east':bool(np.array_equal(before[:,-1],after[:,-1]))},'qa':views,'actualVisualReview':'pending','script':info(Path(__file__)),'helper':info(hp),'formalAccepted':False}
write(out/'assembly.json',record);write(out/'r08_c06.png.generation.json',{'derivedFrom':record['derivedFrom'],'assembly':str(out/'assembly.json'),'operation':record['operation'],'actualModel':None,'actualQuality':None,'newGeneration':False,'nativeUpscaled':False,**info(P)})
print(json.dumps(record['candidate'],ensure_ascii=False))
