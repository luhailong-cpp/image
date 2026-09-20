from pathlib import Path
from PIL import Image
import json,hashlib
TOP=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
specs={
'lanxian_day':{
'paving_left':([1450,220,2704,1474],[1840,420,2200,1040]),
'paving_right':([2580,730,3834,1984],[3010,1010,3400,1650])},
'lanxian_spring':{
'paving_left':([1450,600,2704,1854],[1830,940,2190,1320]),
'paving_right':([2580,730,3834,1984],[3000,1060,3410,1490]),
'roof_joints':([1010,400,2264,1654],[1410,810,1810,1210])}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for variant,items in specs.items():
 root=TOP/variant/'r08_c06';repair=root/'repairs/v3'
 base=root/'output'/f'{variant}_r08_c06_q64_4k_candidate_v2.png'
 im=Image.open(base).convert('RGB')
 for d in ['guides','prompts','native']:(repair/d).mkdir(parents=True,exist_ok=True)
 patches={}
 for ident,(box,focus) in items.items():
  p=repair/'guides'/f'{ident}.layout-only.png'
  assert not p.exists(),p
  im.crop(box).save(p)
  patches[ident]={'rect':box,'focusRect':focus,'guideSha256':sha(p)}
 (repair/'plan.json').write_text(json.dumps({'base':str(base),'baseSha256':sha(base),'patches':patches,'nativeRequired':[1254,1254],'operation':'local native seam repair; composite only focused defect area with narrow hard seam; no final resampling'},indent=2),encoding='utf8')
 print(variant, len(patches))

