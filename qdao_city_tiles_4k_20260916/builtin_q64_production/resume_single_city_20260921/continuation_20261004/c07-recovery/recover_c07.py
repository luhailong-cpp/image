"""Mechanically place an existing native repair; no image generation or enlargement."""
import datetime, hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
SESSION = OUT.parents[1]
ART = SESSION.parents[1]
REPO = ART.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(OUT / 'vendor'))
SOURCE = SESSION / 'next_tile_r08_c07/continuation-20260923/qa-repair-20260923/repaired-v1/r08_c07.png'
NATIVE = SESSION / 'continuation_20260928T081700Z/repairs/c07-cross-2048-3072.native.png'
GENERATION = NATIVE.with_name(NATIVE.name + '.generation.json')
GUIDE = SESSION / 'continuation_20260928T081700Z/qa-c07/priority-cross-x2048-y3072.png'
HELPER = ART / 'builtin_q64_production/tools/mechanical_join.py'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
info = lambda p: {'file': str(p), 'sha256': sha(p)}
def write(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
def rgb(path, shape):
    with Image.open(path) as im:
        im.load()
        assert im.format == 'PNG' and im.size == shape
        return np.array(im.convert('RGB'))

assert sha(SOURCE) == '7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6'
assert sha(NATIVE) == '762725311f0c44dfac2c7d595090db1a363eb91cd6240852dfee94b641382763'
assert sha(GUIDE) == '0c086bb20210cb10511a987aaf3c9812b87d514a768edb1dda163ffaddb28785'
before = rgb(SOURCE, (4096,4096)); native = rgb(NATIVE, (1254,1254))
box = [1421,2445,2675,3699]; x0,y0,x1,y1=box
context = before[y0:y1,x0:x1]
assert np.array_equal(context, rgb(GUIDE,(1254,1254)))
yy,xx = np.mgrid[:1254,:1254].astype(np.float32)
distance = np.minimum.reduce([xx,yy,1253-xx,1253-yy])
a = np.clip(distance / 96.0,0,1); a = a*a*(3-2*a)
mask = np.rint(a*255).astype(np.uint8)
spec=importlib.util.spec_from_file_location('existing_mechanical_join',HELPER)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
joined, flow, tone, registration = helper.registered_join(context,native,mask,max_shift=8.0,match_tone=True)
after=before.copy(); after[y0:y1,x0:x1]=joined
changed=np.any(after!=before,axis=2)
allowed=np.zeros((4096,4096),bool);allowed[y0:y1,x0:x1]=mask>0
assert not np.any(changed & ~allowed)
candidate=OUT/'r08_c07.png'
assert not candidate.exists()
Image.fromarray(after).save(candidate)
Image.fromarray(mask).save(OUT/'mask.png')
Image.fromarray(joined).save(OUT/'context-after.png')
np.save(OUT/'flow.npy',flow,allow_pickle=False)
np.save(OUT/'tone.npy',tone,allow_pickle=False)
qa=OUT/'qa';qa.mkdir(exist_ok=False)
rects={
 'return-top':[x0-128,y0-128,x1+128,y0+128],
 'return-bottom':[x0-128,y1-128,x1+128,y1+128],
 'return-left':[x0-128,y0-128,x0+128,y1+128],
 'return-right':[x1-128,y0-128,x1+128,y1+128],
 'grid-x2048-inside-repair':[1920,y0,2176,y1],
 'grid-y3072-inside-repair':[x0,2944,x1,3200],
 'return-northwest':[x0-192,y0-192,x0+192,y0+192],
 'return-northeast':[x1-192,y0-192,x1+192,y0+192],
 'return-southwest':[x0-192,y1-192,x0+192,y1+192],
 'return-southeast':[x1-192,y1-192,x1+192,y1+192],
}
crops=[]
for name,rect in rects.items():
    l,t,r,b=rect;p=qa/(name+'.png');Image.fromarray(after[t:b,l:r]).save(p)
    crops.append({**info(p),'sourceRectLTRB':rect,'pixels':[r-l,b-t],'resized':False})
Image.fromarray(after).resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/'overview-preview-only.png')
ys,xs=np.where(changed)
record={
 'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'recovered_existing_native_patch_pending_visual_review','tile':'r08_c07',
 'candidate':{**info(candidate),'pixels':[4096,4096]},
 'derivedFrom':[info(SOURCE),{**info(NATIVE),'generationRecord':info(GENERATION)}],
 'referenceCrop':info(GUIDE),'cropLTRB':box,
 'mechanicalHelper':info(HELPER),'script':info(Path(__file__)),
 'mask':{**info(OUT/'mask.png'),'shape':'full_native_rectangle_with_96px_smoothstep_outer_fade'},
 'flow':info(OUT/'flow.npy'),'tone':info(OUT/'tone.npy'),'registration':registration,
 'changedBoundsLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
 'changedPixels':int(changed.sum()),'outsideMaskUnchanged':True,
 'existingSourceUnchanged':sha(SOURCE)=='7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6',
 'nativeRepairUnchanged':sha(NATIVE)=='762725311f0c44dfac2c7d595090db1a363eb91cd6240852dfee94b641382763',
 'nativeInputsUpscaled':False,'newGeneratedImages':0,'actualModel':None,'actualQuality':None,
 'formalAccepted':False,'runtimeAccepted':False,'sharedRecordsModified':False,
 'libraries':{'numpy':np.__version__,'opencv':helper.cv2.__version__},
 'qa':crops,'overviewMeaning':'1024 preview only, not detail or seam acceptance evidence'
}
write(OUT/'repair.json',record)
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'changedPixels':record['changedPixels'],'registration':registration},ensure_ascii=False))
