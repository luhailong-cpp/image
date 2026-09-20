from pathlib import Path
import json,shutil,hashlib
p=Path(r'E:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\r10_c10')
d=p/'rejected';d.mkdir(exist_ok=True)
for rel in ['native/r02_c03.png','native/r02_c03.record.json','prompts/r02_c03.prompt.txt']:
 s=p/rel;shutil.move(str(s),str(d/s.name))
r=json.loads((d/'r02_c03.record.json').read_text());r['outputFile']='rejected/r02_c03.png';r['promptFile']='rejected/r02_c03.prompt.txt';r['visualQa']={'status':'rejected','reason':'Transparent background removed required paving.'};r['retainedForProvenanceOnly']=True
(d/'r02_c03.record.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
