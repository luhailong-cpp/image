from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival/L_r09_c07_r10_c07_c10')
rp=p/'repairs/v2'
for n in ('inputs','native','prompts'): (rp/n).mkdir(parents=True,exist_ok=True)
src=p/'output/pair_4096x8192_candidate.png';im=Image.open(src).convert('RGB')
boxes={'tree_boundary':[0,3469,1254,4723],'floor_boundary':[1200,3270,2454,4524],'upper_stone_joints':[1450,200,2704,1454]}
for n,b in boxes.items():
 im.crop(b).save(rp/'inputs'/f'{n}.png');im.crop(b).save(rp/'inputs'/f'{n}.jpg',quality=87)
(rp/'plan.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'boxesLTRB':boxes,'status':'native_repair_required'},indent=2),encoding='utf-8')
print('Three native-size contexts saved')
