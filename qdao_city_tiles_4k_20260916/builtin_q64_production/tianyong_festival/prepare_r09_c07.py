from pathlib import Path
from PIL import Image
import json,hashlib,shutil
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916');city=root/'builtin_q64_production/tianyong_festival';p=city/'r09_c07'
for name in ('guides','prompts','native','output','qa'): (p/name).mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=root/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png';box=(490.4375,2026.4375,1301.5625,2837.5625)
im=Image.open(source).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=box)
im.save(p/'layout-reference-only.png');im.save(p/'layout-input.jpg',quality=85)
neighbor=city/'quad_r10_c07_c10/output_v2/r10_c07.png'
Image.open(neighbor).convert('RGB').resize((1254,1254),Image.Resampling.LANCZOS).save(p/'neighbor-style-input.jpg',quality=85)
record={'role':'Reference-only layout and style inputs; not final art','layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceBoxLTRB':box,'guidePixels':[1254,1254],'guideResized':True,'nextTile':'r09_c07','globalPixelRectXYWH':[24576,32768,4096,4096],'worldRect':{'x':162.5,'z':131.25,'width':18.75,'height':18.75},'neighborCandidate':str(neighbor),'neighborSha256':sha(neighbor),'sourceArtUpscaledForFinal':False}
(p/'layout-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
plan=json.loads((city/'r10_c10/plan.json').read_text(encoding='utf-8'));plan.update({'status':'layout_reference_ready_style_reference_pending','sampleTile':{'row':9,'column':7,'worldRect':record['worldRect']},'samplePixelRectInWholeCity':[24576,32768,28672,36864],'styleReferenceSha256':None,'guidePreparation':{'status':'pending_unified_style_reference'},'patches':[]})
(p/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
shutil.copyfile(city/'r10_c10/record_native.py',p/'record_native.py')
(p/'assemble_builtin.py').write_text((city/'r10_c10/assemble_builtin.py').read_text(encoding='utf-8').replace('r10_c10','r09_c07'),encoding='utf-8')
print(str(p))
