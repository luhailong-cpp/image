from pathlib import Path
import json,hashlib,sys
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');sys.path.insert(0,str(B/'tools'));import native_batch as n
s=json.loads((B/'selections/right-r04c14-candidate-sixteen-v003.json').read_text(encoding='utf-8-sig'))
s['selectionVersion']='right-r04c14-p22-joint-repair-context-v001';s['status']='joint_repair_input_only_not_adopted'
r=B/'versions/right-r04c14-p12-native-v002/r04_c14/native/p12.png.generation.json';d=json.loads(r.read_text(encoding='utf-8-sig'));s['patches']['p12']={'record':str(r),'recordSha256':n.sha(r),'sha256':d['sha256']};del s['patches']['p22'];del s['patches']['p21']
f=B/'selections/right-r04c14-p22-joint-repair-context-v001.json';f.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
g=n.guide('r04_c14','p22',[f],n.Scope(),'right-r04c14-p22-guide-v002');m=n.read_json(g['metadata']);im=Image.open(B/'versions/right-r04c14-p22-native-v001/r04_c14/native/p22.png').convert('RGB');guide=Image.open(g['guide']).convert('RGB')
for lock in m['lockedSources']:
 x,y=lock['paste'];w,h=lock['pixels'];im.paste(guide.crop((x,y,x+w,y+h)),(x,y))
out=Path(g['guide']).with_name('p22-REPAIR-INPUT-only.png');im.save(out)
Path(g['guide']).with_name('p22-REPAIR-INPUT-only.json').write_text(json.dumps({'role':'exact-pixel-edit-input-only-not-generated-art','target':'p22v001','guide':g,'changedOnly':'exact known neighboring core intersections','sourceSha256':n.sha(B/'versions/right-r04c14-p22-native-v001/r04_c14/native/p22.png'),'inputSha256':n.sha(out)},indent=2),encoding='utf-8');print(out)

