import datetime,hashlib,importlib.util,json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;REC=R.parent;SESSION=REC.parents[1];ART=SESSION.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(REC/'vendor'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
request=read(R/'request.json');receipt=read(R/'tool-response.json');derive=read(R/'context-native-1254.png.derivation.json')
native=R/'native.png';cached=Path(re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S).group(1))
assert sha(native)==sha(cached)
with Image.open(native) as im:im.load();assert im.size==(1254,1254) and im.format=='PNG';n=np.array(im.convert('RGB'))
for ref in read(R/'references.json'):assert sha(ref['file'])==ref['sha256']
gen={'schemaVersion':1,**info(native),'width':1254,'height':1254,'format':'PNG','generatedAt':None,
 'observedStartedAtUtc':receipt['hostObservedStartedAtUtc'],'observedCompletionAtUtc':receipt['hostObservedFinishedAtUtc'],'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R/'config.snapshot.json'),'configSnapshotEvidence':info(R/'config.snapshot.json'),
 'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'backendModelVerified':False,
 'unverifiedReason':'Host-managed builtin route; actual model/quality and server-generated timestamp not exposed. 1254 dimensions are decoded from raw tool output; no enlargement.',
 'request':info(R/'request.json'),'prompt':info(R/'prompt.txt'),'references':read(R/'references.json'),'editBefore':derive,'evidence':{'receipt':info(R/'tool-response.json'),'cacheOriginal':info(cached),'byteIdenticalCopy':True},'formalAccepted':False}
write(R/'native.png.generation.json',gen)
source=Path(derive['source']);assert sha(source)==derive['sourceSha256'];before=np.array(Image.open(source).convert('RGB'))
x0,y0,x1,y1=derive['cropLTRB'];context=before[y0:y1,x0:x1]
assert np.array_equal(context,np.array(Image.open(R/'context-native-1254.png').convert('RGB')))
yy,xx=np.mgrid[:1254,:1254].astype(np.float32);dist=np.minimum.reduce([xx,yy,1253-xx,1253-yy])
alpha=np.clip(dist/128.0,0,1);mask=np.rint(alpha*alpha*(3-2*alpha)*255).astype(np.uint8)
helperpath=ART/'builtin_q64_production/tools/mechanical_join.py';spec=importlib.util.spec_from_file_location('join_existing',helperpath);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
joined,flow,tone,reg=helper.registered_join(context,n,mask,max_shift=4.0,flow_inner=160.0,flow_full=64.0,tone_inner=200.0,tone_full=80.0,match_tone=True)
after=before.copy();after[y0:y1,x0:x1]=joined;allowed=np.zeros((4096,4096),bool);allowed[y0:y1,x0:x1]=mask>0
changed=np.any(before!=after,axis=2);assert not np.any(changed&~allowed)
out=R/'candidate-v4';out.mkdir(exist_ok=False)
candidate=out/'r08_c07.png';Image.fromarray(after).save(candidate)
Image.fromarray(joined).save(out/'context-after.png');Image.fromarray(mask).save(out/'mask.png');np.save(out/'flow.npy',flow,allow_pickle=False);np.save(out/'tone.npy',tone,allow_pickle=False)
rects={'return-top':[x0-128,y0-128,x1+128,y0+128],'return-bottom':[x0-128,y1-128,x1+128,y1+128],
 'return-left':[x0-128,y0-128,x0+128,y1+128],'return-right':[x1-128,y0-128,x1+128,y1+128],
 'frame-bends-repaired':[2073,2243,2527,2697],'upper-grid-junction':[1856,1856,2240,2240]}
qa=[]
for name,rect in rects.items():
 l,t,r,b=rect;f=out/(name+'.png');Image.fromarray(after[t:b,l:r]).save(f);qa.append({'id':name,**info(f),'sourceRectLTRB':rect,'pixels':[r-l,b-t],'resized':False})
Image.fromarray(after).resize((1024,1024),Image.Resampling.LANCZOS).save(out/'overview-preview-only.png')
record={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'new_return_repair_candidate_pending_visual_review','candidate':{**info(candidate),'pixels':[4096,4096]},
 'derivedFrom':[info(source),{**info(native),'generationRecord':info(R/'native.png.generation.json')}],'cropLTRB':[x0,y0,x1,y1],
 'script':info(Path(__file__)),'mechanicalHelper':info(helperpath),'registration':reg,'mask':{**info(out/'mask.png'),'outerFadePixels':128,'shape':'rectangle'},
 'flow':info(out/'flow.npy'),'tone':info(out/'tone.npy'),'changedPixels':int(changed.sum()),'outsideMaskUnchanged':True,'nativeInputsUpscaled':False,
 'sourceUnchanged':sha(source)==derive['sourceSha256'],'sourceRepairRecord':info(REC/'full-rect-v3/repair.json'),'qa':qa,
 'actualModel':None,'actualQuality':None,'formalAccepted':False,'runtimeAccepted':False,'sharedRecordsModified':False}
write(out/'repair.json',record)
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'nativeSha256':sha(native),'registration':reg},ensure_ascii=False))
