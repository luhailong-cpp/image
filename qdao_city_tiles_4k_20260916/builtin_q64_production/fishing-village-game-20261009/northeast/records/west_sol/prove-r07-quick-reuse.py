import sys,re
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
from PIL import Image
q=w.Z/'qa/r07_c11-west-resume-v1';m=w.read(q/'manifest.json');sel=w.own_selection('r07_c11');result=[]
for e in m['qa']:
 name=__import__('pathlib').Path(e['file']).name;kind=e['kind'];entry=dict(file=e['file'],sha256=e['sha256'],kind=kind)
 if kind in ('vertical_boundary','horizontal_boundary'):
  ids=e['neighborPatchIds'];pid=ids[0] if kind=='vertical_boundary' else ids[1];stem=__import__('pathlib').Path(sel[pid]['path']).stem.removesuffix('-west_sol');side='right' if kind=='vertical_boundary' else ('top-check-only' if pid.endswith('p44') else 'top');f=w.Z/'qa/west_sol'/stem/(side+'.native-1to1.png');im=Image.open(f).convert('RGB');c=im.crop((0,115,256,1139) if kind=='vertical_boundary' else (115,0,1139,256));entry.update(reusedQuickView=w.ref(f),exactPixelSubsetVerified=c.tobytes()==Image.open(e['file']).convert('RGB').tobytes())
 elif kind=='core':
  entry['note']='Original 1254 native full image already visually reviewed; integer core crop hash proved by assembler'
 result.append(entry)
w.write(q/'quick-review-reuse-proof.json',dict(createdAtUtc=w.now(),candidate=m['candidate'],checks=result))
print([(x['file'].split('\\\\')[-1],x.get('exactPixelSubsetVerified')) for x in result if 'exactPixelSubsetVerified' in x])
print('kinds',set(x['kind'] for x in result))

