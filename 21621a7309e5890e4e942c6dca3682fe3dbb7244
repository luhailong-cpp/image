from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival/L_r09_c07_r10_c07_c10');r=p/'repairs/v3'
for n in ('inputs','native','prompts'): (r/n).mkdir(parents=True,exist_ok=True)
src=p/'output_v2/pair_4096x8192_candidate.png';box=[1421,0,2675,1254];im=Image.open(src).crop(box);im.save(r/'inputs/short_joint.png');im.save(r/'inputs/short_joint.jpg',quality=87)
(r/'plan.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'boxLTRB':box,'status':'short upper grout still incomplete after prior native repair'},indent=2),encoding='utf-8')
