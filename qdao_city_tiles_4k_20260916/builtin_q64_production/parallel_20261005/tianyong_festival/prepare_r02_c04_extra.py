from pathlib import Path
import json,hashlib
from PIL import Image
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c04-v1')
s=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r03_c04-v2/joined.png')
im=Image.open(d/'context.png').convert('RGBA');im.paste(Image.open(s).convert('RGBA').crop((0,0,1254,230)),(0,1024));im.save(d/'context.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((d/'preparation.json').read_text());p['nativeInputs'].append({'file':str(s),'sha256':sha(s),'role':'exact same-world lower230, includes right halo clipped out of current tile'})
p['references'][0]['sha256']=sha(d/'context.png');(d/'preparation.json').write_text(json.dumps(p,indent=2))
r=json.loads((d/'request.json').read_text());r['knownPixels']=1254*230;r['missingPixels']=1254*1024
r['payload']['prompt']+='\nSpecific crop geometry: the missing top area is quiet broad ivory pavement, with the sparse slightly sloping slab joints shown in image2, not little tiles. A narrow horizontal edging course runs across the lower part ABOVE the existing finished molding. Draw those broad surfaces and the upper edge course as the canonical image shows. Continue the exact lower230 rows of image1 across their full width. No additional cloud motif, vertical frame or inset gray stone appears in this crop. The bottom is part of the same larger plaza panel continuing off canvas; do not frame the picture.'
(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');(d/'prompt.txt').write_text(r['payload']['prompt'],encoding='utf-8')
rec=json.loads((d/'context.png.generation.json').read_text());rec['sha256']=sha(d/'context.png');rec['derivedFrom'].append({'file':str(s),'sha256':sha(s)});(d/'context.png.generation.json').write_text(json.dumps(rec,indent=2))
print(json.dumps(r))

