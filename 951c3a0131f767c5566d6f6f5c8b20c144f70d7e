from pathlib import Path
from PIL import Image
import json,hashlib,shutil
import numpy as np
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916');city=root/'builtin_q64_production/tianyong_festival';p=city/'r09_c08'
assert not p.exists()
for n in ('native','guides','prompts','output','qa'): (p/n).mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
src=root/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png'
box=(1258.4375,2026.4375,2069.5625,2837.5625)
layout=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=box)
left=city/'L_r09_c07_r10_c07_c10/output_v3/vertical-extended-context.png';bottom=city/'L_r09_c07_r10_c07_c10/output_v3/row10-extended-context.png'
li=Image.open(left).convert('RGB').crop((4096,0,4326,4326));bi=Image.open(bottom).convert('RGB').crop((4096,0,8422,230))
assert np.array_equal(np.array(li)[-230:],np.array(bi)[:,:230])
layout.paste(li,(0,0));layout.paste(bi,(0,4096));layout.resize((1254,1254),Image.Resampling.LANCZOS).save(p/'layout-input.jpg',quality=85)
Image.open(left).crop((115,115,4211,4211)).resize((1254,1254),Image.Resampling.LANCZOS).save(p/'left-style-input.jpg',quality=85)
Image.open(bottom).crop((4211,115,8307,4211)).resize((1254,1254),Image.Resampling.LANCZOS).save(p/'bottom-style-input.jpg',quality=85)
record={'role':'Reference-only layout and neighbor inputs; not final art','layoutSource':str(src),'layoutSourceSha256':sha(src),'layoutSourceBoxLTRB':box,'guidePixels':[1254,1254],'guideResized':True,'nextTile':'r09_c08','globalPixelRectXYWH':[28672,32768,4096,4096],'worldRect':{'x':181.25,'z':131.25,'width':18.75,'height':18.75},'neighborConstraints':[{'edge':'left','source':str(left),'sha256':sha(left),'sourceBoxLTRB':[4096,0,4326,4326],'pasteXY':[0,0]},{'edge':'bottom','source':str(bottom),'sha256':sha(bottom),'sourceBoxLTRB':[4096,0,8422,230],'pasteXY':[0,4096]}],'cornerOverlapPixelsIdentical':True,'sourceArtUpscaledForFinal':False}
(p/'layout-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
plan=json.loads((city/'r09_c07/plan.json').read_text());plan.update({'status':'layout_only_native_generation_pending','sampleTile':{'row':9,'column':8,'worldRect':record['worldRect']},'samplePixelRectInWholeCity':[28672,32768,32768,36864],'patches':[]})
for k in ('selectedCandidate','selectedAssembly','styleReferenceSha256','guidePreparation'):plan.pop(k,None)
(p/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
shutil.copyfile(city/'r09_c07/record_native.py',p/'record_native.py')
code=(city/'r09_c07/assemble_builtin.py').read_text();(p/'assemble_builtin.py').write_text(code.replace('r09_c07','r09_c08'),encoding='utf-8')
print('r09_c08 references prepared; exact left/bottom corner agreement verified')
