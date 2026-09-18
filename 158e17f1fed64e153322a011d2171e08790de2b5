from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location('assembly',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
for v in ('lanxian_day','lanxian_spring'):
 d=P/v/'pair_r08_c06_c07';(d/'output').mkdir(parents=True,exist_ok=True);(d/'qa').mkdir(exist_ok=True)
 m=load(P/v/'r08_c07/assemble_builtin.py')
 l=P/v/'r08_c06/output/extended-context-v4.png';r=P/v/'r08_c07/output/extended-context.png'
 left=np.array(Image.open(l).convert('RGB'));right=np.array(Image.open(r).convert('RGB'))
 joined,metric=m.append_patch(left,right,m.load_seam_helper(),'cross4K_c06_c07')
 assert joined.shape==(4326,8422,3)
 ext=Image.fromarray(joined);art=ext.crop((115,115,8307,4211))
 assert art.size==(8192,4096)
 ext.save(d/'output/pair-extended-v1.png');art.save(d/'output/pair-v1.png')
 art.resize((1600,800),Image.Resampling.LANCZOS).save(d/'qa/pair-v1-overview.jpg',quality=80)
 for i,y in enumerate((0,800,1600,2400,3196)):
  art.crop((3646,y,4546,y+900)).save(d/f'qa/boundary-v1-{i}_100pct.png')
 (d/'output/pair-v1-assembly.json').write_text(json.dumps({'appearance':v,'sources':[{'file':str(l),'sha256':sha(l)},{'file':str(r),'sha256':sha(r)}],'sourceResampling':'none at pair join; c06 v4 prior subpixel registration disclosed in repair-v4-assembly','sourceUpscaled':False,'join':metric,'pair':str(d/'output/pair-v1.png'),'size':[8192,4096],'sha256':sha(d/'output/pair-v1.png'),'formalAcceptance':False},indent=2))
 rep=P/v/'r08_c07/repairs/curved_paving'
 for sub in ('guides','native','prompts'): (rep/sub).mkdir(parents=True,exist_ok=True)
 rect=[2640,390,3894,1644]
 im=Image.open(P/v/f'r08_c07/output/{v}_r08_c07_q64_4k_candidate.png').crop(rect)
 im.save(rep/'guides/curve.layout-only.png');im.save(rep/'guides/curve.input-preview.jpg',quality=85)
 (rep/'plan.json').write_text(json.dumps({'rect':rect,'source':str(P/v/f'r08_c07/output/{v}_r08_c07_q64_4k_candidate.png'),'scope':'repair dead-ended grout in curved paving, preserve original layout'}))
 print(v,sha(d/'output/pair-v1.png'))

