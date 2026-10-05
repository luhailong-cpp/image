"""Two non-overlapping native repair crops, bounded existing mechanical join."""
import datetime,hashlib,importlib.util,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent; SESSION=ROOT.parents[1]; ART=SESSION.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'vendor'))
OUT=ROOT/'full-rect-v3';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
helperpath=ART/'builtin_q64_production/tools/mechanical_join.py'
helper=module('join_existing',helperpath)
maskpath=SESSION/'tools/city_repair.py';masks=module('existing_masks',maskpath)
source=SESSION/'next_tile_r08_c07/continuation-20260923/qa-repair-20260923/repaired-v1/r08_c07.png'
assert sha(source)=='7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6'
before=np.array(Image.open(source).convert('RGB'));after=before.copy();allowed=np.zeros((4096,4096),bool)
patches=[
 {'id':'cross-2048-3072','path':SESSION/'continuation_20260928T081700Z/repairs/c07-cross-2048-3072.native.png','expected':'762725311f0c44dfac2c7d595090db1a363eb91cd6240852dfee94b641382763','box':[1421,2445,2675,3699]},
 {'id':'cross-3072-1024','path':SESSION/'continuation_20261004/c07-cross-3072-1024/native.png','expected':'dd0e9ce1dc4f4d1745ea5751b14990d89c6ac41e4dbf6e08e2972ca075ecde71','box':[2445,397,3699,1651]},
]
records=[]
for p in patches:
 assert sha(p['path'])==p['expected']
 native=np.array(Image.open(p['path']).convert('RGB'));assert native.shape==(1254,1254,3)
 x0,y0,x1,y1=p['box'];context=before[y0:y1,x0:x1]
 yy,xx=np.mgrid[:1254,:1254].astype(np.float32);dist=np.minimum.reduce([xx,yy,1253-xx,1253-yy]);alpha=np.clip(dist/96.0,0,1);mask=np.rint(alpha*alpha*(3-2*alpha)*255).astype(np.uint8)
 joined,flow,tone,reg=helper.registered_join(context,native,mask,max_shift=8.0,match_tone=True)
 after[y0:y1,x0:x1]=joined;allowed[y0:y1,x0:x1]=mask>0
 d=OUT/p['id'];d.mkdir()
 Image.fromarray(mask).save(d/'mask.png');Image.fromarray(joined).save(d/'context-after.png')
 np.save(d/'flow.npy',flow,allow_pickle=False);np.save(d/'tone.npy',tone,allow_pickle=False)
 records.append({'id':p['id'],'sourceNative':info(p['path']),'cropLTRB':p['box'],'registration':reg,'mask':info(d/'mask.png'),'flow':info(d/'flow.npy'),'tone':info(d/'tone.npy')})
candidate=OUT/'r08_c07.png';Image.fromarray(after).save(candidate)
changed=np.any(before!=after,axis=2);assert not np.any(changed&~allowed)
qa=[]
for p in patches:
 x0,y0,x1,y1=p['box'];d=OUT/p['id']
 rects={'return-top':[x0-128,y0-128,x1+128,y0+128],'return-bottom':[x0-128,y1-128,x1+128,y1+128],
 'return-left':[x0-128,y0-128,x0+128,y1+128],'return-right':[x1-128,y0-128,x1+128,y1+128]}
 for name,rect in rects.items():
  l,t,r,b=rect;f=d/(name+'.png');Image.fromarray(after[t:b,l:r]).save(f)
  qa.append({'id':p['id']+'/'+name,**info(f),'sourceRectLTRB':rect,'pixels':[r-l,b-t],'resized':False})
Image.fromarray(after).resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/'overview-preview-only.png')
record={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'two_native_local_repairs_pending_visual_review',
 'candidate':{**info(candidate),'pixels':[4096,4096]},'source':info(source),'patches':records,'script':info(Path(__file__)),
 'mechanicalHelper':info(helperpath),'maskHelper':info(maskpath),'maskParameters':{'shape':'full_rectangle','outerFadePixels':96},
 'changedPixels':int(changed.sum()),'outsideMasksUnchanged':True,'sourceUnchanged':sha(source)=='7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6',
 'nativeInputsUpscaled':False,'newGenerationsByThisScript':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'runtimeAccepted':False,'sharedRecordsModified':False,'qa':qa}
with (OUT/'repair.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'changedPixels':int(changed.sum())}))
