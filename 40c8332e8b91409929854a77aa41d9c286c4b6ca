from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/r08_c06')
base=root/'output/lanxian_spring_r08_c06_q64_4k_candidate.png'
repair=root/'repairs/v2'
for d in ['guides','prompts','native']: (repair/d).mkdir(parents=True,exist_ok=True)
boxes={'paving':[1980,320,3234,1574],'roof_joints':[400,400,1654,1654]}
im=Image.open(base).convert('RGB')
for k,b in boxes.items():
 im.crop(b).save(repair/'guides'/f'{k}.layout-only.png')
(repair/'plan.json').write_text(json.dumps({'base':str(base),'baseSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'patches':boxes,'nativeRequired':[1254,1254],'operation':'native local repaint with hard minimum-error boundary seam; no resize'},indent=2),encoding='utf8')
print(json.dumps({'repair':str(repair),'boxes':boxes}))


