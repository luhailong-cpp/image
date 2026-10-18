from pathlib import Path
from PIL import Image
import importlib.util,json
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bp',B/'batch_pipeline_v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
tile='r02_c04';picked=m.selected(tile);pending={'s01_01':'s01_01-v003.png','s03_04':'s03_04-v008.png','s04_04':'s04_04-v003.png'}
D=B/tile/'qa/draft-native4096-v002';D.mkdir(exist_ok=False,parents=True)
im=Image.new('RGB',(4096,4096));sources=[]
for r in range(1,5):
 for c in range(1,5):
  patch=f's{r:02d}_{c:02d}';rec=picked.get(patch);p=Path(rec['file']) if rec else B/tile/'native'/pending[patch]
  with Image.open(p) as a:
   assert a.size==(1254,1254);im.paste(a.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
  sources.append({'patch':patch,'file':str(p),'sha256':m.sha(p),'quickSelected':rec is not None,'pending':rec is None})
out=D/'r02_c04-draft-native4096.png';im.save(out);evidence=[]
for r in range(1,5):
 for c in range(1,4):
  box=(c*1024-160,(r-1)*1024,c*1024+160,r*1024);p=D/f'vertical-r{r}-c{c}.png';im.crop(box).save(p);evidence.append({'file':str(p),'box':box,'status':'PENDING_ACTUAL_VIEW'})
for r in range(1,4):
 for c in range(1,5):
  box=((c-1)*1024,r*1024-160,c*1024,r*1024+160);p=D/f'horizontal-r{r}-c{c}.png';im.crop(box).save(p);evidence.append({'file':str(p),'box':box,'status':'PENDING_ACTUAL_VIEW'})
for r in range(1,4):
 for c in range(1,4):
  box=(c*1024-160,r*1024-160,c*1024+160,r*1024+160);p=D/f'junction-r{r}-c{c}.png';im.crop(box).save(p);evidence.append({'file':str(p),'box':box,'status':'PENDING_ACTUAL_VIEW'})
layout=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png')
a=Image.open(layout);wb=(12288,4096,16384,8192);a.transform((800,800),Image.Transform.EXTENT,tuple(v*a.width/65536 for v in wb),Image.Resampling.BICUBIC).save(D/'approved-layout-enlarged-context.png')
manifest={'kind':'DRAFT_WITH_PENDING_SOURCES','tile':tile,'file':str(out),'sha256':m.sha(out),'pixels':[4096,4096],'selectedCoreCount':len(picked),'totalCorePositions':16,'pendingCoreCount':3,'formalAccepted':False,'allPixelsFromNativeSources':True,'singleModelNative4096':False,'resampled':False,'method':'Integer1024 center crops from16 native1254 sources. Three explicitly pending sources included for review only.','sources':sources,'evidence':evidence,'layoutReference':str(layout),'layoutSHA256':m.sha(layout),'layoutContextIsEnlargedOnly':True}
m.write_new(D/'draft-manifest.json',manifest);print(json.dumps({'draft':str(out),'sha256':m.sha(out),'manifest':str(D/'draft-manifest.json'),'selected':len(picked),'formalAccepted':False}))

