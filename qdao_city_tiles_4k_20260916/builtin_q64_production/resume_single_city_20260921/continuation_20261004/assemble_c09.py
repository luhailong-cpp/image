"""Apply two real AI-generated native patches to a new paired-map candidate."""
import datetime, hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

RUN=Path(__file__).resolve().parent
SESSION=RUN.parent
ART=SESSION.parents[1]
sys.path.insert(0,str(RUN/'c07-recovery/vendor'))
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('mechanical_join',ART/'builtin_q64_production/tools/mechanical_join.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
OUT=RUN/'c09-pair-v2';OUT.mkdir(exist_ok=False)
OLD=SESSION/'next_tile_r08_c09/continuation-20260923/versions/cross-boundary-pair-v1-20260923T125829004582Z'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
sources=[OLD/'r08_c09.png',OLD/'r09_c09.png']
expected=['94a3c47e0b2f91278e3727c30e15a787237b1eb70c909c8e1573a4378c1b907e','06d36c552c660eba847255feeabc36dac2270d3025b55c7767683381ad8a5d51']
assert [sha(p) for p in sources]==expected
before=np.concatenate([np.array(Image.open(p).convert('RGB')) for p in sources])
after=before.copy();allowed=np.zeros((8192,4096),bool)
patches=[('c09-shared-02',[909,3469,2163,4723]),('c09-return-04',[2842,4096,4096,5350])]
records=[]
for name,box in patches:
    native_path=RUN/name/'native.png'
    generation=RUN/name/'native.png.generation.json'
    native=np.array(Image.open(native_path).convert('RGB'))
    assert native.shape==(1254,1254,3)
    assert sha(native_path)==json.loads(generation.read_text(encoding='utf-8'))['sha256']
    x0,y0,x1,y1=box;context=before[y0:y1,x0:x1]
    yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
    dist=np.minimum.reduce([xx,yy,1253-xx,1253-yy])
    a=np.clip(dist/96.0,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
    joined,flow,tone,report=helper.registered_join(context,native,mask,max_shift=4.0,flow_inner=180,flow_full=70,tone_inner=180,tone_full=70,match_tone=True)
    after[y0:y1,x0:x1]=joined;allowed[y0:y1,x0:x1]=mask>0
    d=OUT/name;d.mkdir()
    Image.fromarray(mask).save(d/'mask.png')
    Image.fromarray(joined).save(d/'context-after.png')
    np.save(d/'flow.npy',flow,allow_pickle=False);np.save(d/'tone.npy',tone,allow_pickle=False)
    records.append({'id':name,'native':info(native_path),'generation':info(generation),'combinedCropLTRB':box,'operation':report,'mask':info(d/'mask.png'),'flow':info(d/'flow.npy'),'tone':info(d/'tone.npy')})
changed=np.any(before!=after,axis=2)
assert not np.any(changed & ~allowed)
entries=[]
for i,name in enumerate(['r08_c09','r09_c09']):
    p=OUT/(name+'.png');Image.fromarray(after[i*4096:(i+1)*4096]).save(p)
    entry={**info(p),'tile':name,'pixels':[4096,4096],'source':info(sources[i]),'changedPixels':int(changed[i*4096:(i+1)*4096].sum()),'formalAccepted':False}
    entries.append(entry)
record={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'new_pair_candidate_pending_visual_review','candidates':entries,'derivedFrom':[info(p) for p in sources],'priorAssembly':info(OLD/'assembly.json'),'patches':records,'outsideMasksUnchanged':True,'originalSourcesUnchanged':[sha(p) for p in sources]==expected,'nativeInputsUpscaled':False,'newModelCallsInThisAssembly':0,'aiRepairSources':2,'formalAccepted':False,'clientRuntimeAccepted':False,'script':info(Path(__file__))}
(OUT/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for ent in entries:
    p=Path(ent['file'])
    derived={**ent,'derivedFrom':record['derivedFrom']+[r['native'] for r in records],'operation':'Native-dimension patch reinsertion with recorded bounded perimeter registration and tone match; no enlargement','assembly':info(OUT/'assembly.json'),'actualModel':None,'actualQuality':None,'newGeneration':False}
    p.with_name(p.name+'.generation.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Q=OUT/'qa';Q.mkdir();qa=[]
def crop(name,box):
    x0,y0,x1,y1=box;p=Q/(name+'.png');Image.fromarray(after[y0:y1,x0:x1]).save(p)
    qa.append({'id':name,**info(p),'combinedCropLTRB':box,'pixels':[x1-x0,y1-y0],'pixelScale':'1:1','viewed':False})
for i in range(4):crop('shared-wide-'+str(i+1).zfill(2),[i*1024,3469,(i+1)*1024,4723])
for name,box in patches:
    x0,y0,x1,y1=box
    crop(name+'-surround',[max(0,x0-128),y0-128,min(4096,x1+128),y1+128])
    crop(name+'-top',[max(0,x0-128),y0-128,min(4096,x1+128),y0+128])
    crop(name+'-bottom',[max(0,x0-128),y1-128,min(4096,x1+128),y1+128])
    crop(name+'-left',[max(0,x0-128),y0-128,x0+128,y1+128])
    if x1<4096:crop(name+'-right',[x1-128,y0-128,x1+128,y1+128])
crop('r09-right-top-unchanged-edge',[3936,4096,4096,5504])
Image.fromarray(after).resize((1024,2048),Image.Resampling.LANCZOS).save(OUT/'pair-preview-only.png')
(Q/'index.json').write_text(json.dumps({'assembly':info(OUT/'assembly.json'),'evidence':qa,'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidates':entries,'qa':str(Q),'outsideMasksUnchanged':True},ensure_ascii=False))
