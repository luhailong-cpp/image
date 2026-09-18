from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival')
p=root/'L_r09_c07_r10_c07_c10'
for n in ('output','qa'): (p/n).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('assembler',root/'r09_c07/assemble_builtin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
top=root/'r09_c07/output/extended-context.png';bottom=root/'quad_r10_c07_c10/output_v2/extended-context.png'
a=np.array(Image.open(top).convert('RGB'));quad=np.array(Image.open(bottom).convert('RGB'))
b=quad[:,:4326].copy()
joinedT,metric=m.append_patch(a.transpose(1,0,2),b.transpose(1,0,2),m.load_seam_helper(),'join_r09_r10_c07_transposed')
joined=joinedT.transpose(1,0,2).copy()
assert joined.shape==(8422,4326,3)
newquad=quad.copy();newquad[:,:4326]=joined[4096:]
assert np.array_equal(newquad[230:],quad[230:])
assert np.array_equal(newquad[:,4326:],quad[:,4326:])
ext=Image.fromarray(joined);ext.save(p/'output/vertical-extended-context.png')
Image.fromarray(newquad).save(p/'output/row10-extended-context.png')
vertical=ext.crop((115,115,4211,8307));vertical.save(p/'output/pair_4096x8192_candidate.png')
row=Image.fromarray(newquad).crop((115,115,16499,4211));row.save(p/'output/row10_16384x4096_candidate.png')
files=[]
for ident,im in [('r09_c07',vertical.crop((0,0,4096,4096)))]+[(f'r10_c{c:02}',row.crop(((c-7)*4096,0,(c-6)*4096,4096))) for c in (7,8,9,10)]:
 f=p/'output'/f'{ident}.png';im.save(f);files.append({'tile':ident,'file':str(f.relative_to(p)),'pixels':[4096,4096],'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(p/'output'/f'r{r:02}_c07.png')) for r in (9,10)],axis=0),np.array(vertical))
assert np.array_equal(np.concatenate([np.array(Image.open(p/'output'/f'r10_c{c:02}.png')) for c in (7,8,9,10)],axis=1),np.array(row))
vertical.resize((750,1500),Image.Resampling.LANCZOS).save(p/'qa/vertical-overview.jpg',quality=85)
row.resize((2000,500),Image.Resampling.LANCZOS).save(p/'qa/row10-overview.jpg',quality=85)
new=vertical.crop((0,0,4096,4096));records=[]
for direction in ('vertical','horizontal'):
 for v in (1024,2048,3072):
  board=Image.new('RGB',(1200,1024) if direction=='vertical' else (1024,1200));boxes=[]
  for i in range(4):
   box=(v-150,i*1024,v+150,(i+1)*1024) if direction=='vertical' else (i*1024,v-150,(i+1)*1024,v+150)
   board.paste(new.crop(box),(i*300,0) if direction=='vertical' else (0,i*300));boxes.append(box)
  f=p/'qa'/f'full_{direction}_{v}_100pct.jpg';board.save(f,quality=85);records.append({'file':f.name,'source':'r09_c07','cropRectsLTRB':boxes,'pixelScale':1})
for x in (0,1024,2048,2842):
 box=(x,4096-627,x+1254,4096+627);vertical.crop(box).save(p/'qa'/f'boundary_x{x}_100pct.jpg',quality=87);records.append({'file':f'boundary_x{x}_100pct.jpg','source':'pair_4096x8192_candidate','cropLTRB':box,'pixelScale':1})
box=(4096-450,0,4096+450,900);row.crop(box).save(p/'qa/junction_below_100pct.jpg',quality=87);records.append({'file':'junction_below_100pct.jpg','source':'row10','cropLTRB':box,'pixelScale':1})
(p/'qa/crops.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(p/'assembly.json').write_text(json.dumps({'schemaVersion':1,'status':'candidate_pending_visual_qa','updatedAtUtc':datetime.now(timezone.utc).isoformat(),'parents':[{'path':str(top),'sha256':sha(top)},{'path':str(bottom),'sha256':sha(bottom)}],'nativeBaseSources':80,'newNativeSourcesInThisMechanicalJoin':0,'files':files,'seamMetric':metric,'resamplingInThisJoin':False,'parentIncludesLimitedSeamRegistration':True,'finalArtUpscaled':False,'exactTileRejoinVerified':True,'unaffectedPixelsUnchangedVerified':True,'layout':'L shape: r09_c07 above r10_c07..c10; no invented missing tiles','runtimePublished':False,'outputs':[{'file':str(f.relative_to(p)),'sha256':sha(f)} for f in (p/'output/vertical-extended-context.png',p/'output/row10-extended-context.png',p/'output/pair_4096x8192_candidate.png',p/'output/row10_16384x4096_candidate.png')]},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':files,'status':'pending_visual_qa'},ensure_ascii=False))
