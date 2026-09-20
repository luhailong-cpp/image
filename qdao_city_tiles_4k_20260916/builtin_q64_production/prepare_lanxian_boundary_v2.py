from pathlib import Path
from PIL import Image
import json
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
for v,ys in [('lanxian_day',[450,2000,2842]),('lanxian_spring',[0,1024,2048])]:
 d=P/v/'pair_r08_c06_c07';rep=d/'repairs/boundary_v2'
 for sub in ('guides','prompts','native'): (rep/sub).mkdir(parents=True,exist_ok=True)
 im=Image.open(d/'output/pair-v1.png').convert('RGB')
 entries=[]
 for i,y in enumerate(ys):
  id=f'boundary_{i+1}';rect=[3470,y,4724,y+1254];im.crop(rect).save(rep/f'guides/{id}.layout-only.png');entries.append({'id':id,'rect':rect})
 (rep/'plan.json').write_text(json.dumps({'source':str(d/'output/pair-v1.png'),'entries':entries},indent=2))
 print(v,entries)

