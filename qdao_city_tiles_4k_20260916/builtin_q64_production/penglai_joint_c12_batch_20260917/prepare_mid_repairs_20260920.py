import json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
B=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');J=B/'penglai_mid_autumn/r09_c10_c11_c12_joint';R=J/'repairs_v2_20260920'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
R.mkdir();(R/'guides').mkdir();(R/'prompts').mkdir();(R/'native').mkdir()
source=J/'output_v1_20260920/extended-context.png';im=Image.open(source)
jobs=[]
for ident,box,roi in [('water-upper',[7565,2242,8819,3496],[7990,2670,8440,3400]),('water-lower',[7565,2957,8819,4211],[7990,3150,8440,4140])]:
    guide=R/'guides'/f'{ident}.png';im.crop(tuple(v+115 for v in box)).save(guide)
    jobs.append({'id':ident,'sourceCropLTRB':box,'pasteROIInTriple':roi,'guide':str(guide),'guideSha256':sha(guide)})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'penglai_mid_autumn','source':str(source),'sourceSha256':sha(source),'coordinateSystem':'triple origin; extended context uses +115 xy; lower support includes existing bottom halo','jobs':jobs,'finding':'Six full c12 internal seam lines and nine internal junctions viewed at original pixels; no definite structural break. Full c11/c12 four boundary crops reveal a vertical water luminance/reflection join around x8192, y2700 onward. Bridge arch and rail remain continuous.','state':'two native localized water repairs planned; not accepted'}
(R/'plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(R)
