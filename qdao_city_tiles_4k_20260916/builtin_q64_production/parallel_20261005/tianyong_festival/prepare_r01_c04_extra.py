from pathlib import Path
import json,hashlib
from PIL import Image
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r01_c04-v1');s=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c04-v1/joined.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(d/'context.png').convert('RGBA');im.paste(Image.open(s).convert('RGBA').crop((0,0,1254,230)),(0,1024));im.save(d/'context.png')
p=json.loads((d/'preparation.json').read_text());p['nativeInputs'].append({'file':str(s),'sha256':sha(s),'role':'exact full width lower230 and right halo'});p['references'][0]['sha256']=sha(d/'context.png');(d/'preparation.json').write_text(json.dumps(p,indent=2))
r=json.loads((d/'request.json').read_text());r['knownPixels']=1254*230;r['missingPixels']=1254*1024
r['payload']['prompt']=r['payload']['prompt'].replace('Do not invent extra seams or carvings.','Retain the canonical ornament visible in the layout guide; do not invent extra seams or extra carvings.')
r['payload']['prompt']+='\nSpecific missing crop geometry: one large partial ivory cloud-scroll bas-relief occupies the upper three quarters and exits the top, left and right canvas edges. Render its broad curled spiral and gently rounded thick embossed outer rim exactly in the relative positions of image2, with the same clean ivory/gold bevel style as the known stone. It is a partial inlaid cloud ornament on plaza paving, NOT a standalone UI badge or whole icon. Below its curved lower rim near y750..900 are the broad plain slanted stone paving slabs, continuing upward from the known lower230 rows. Preserve and continue those native joints from exactly their known positions. Keep the cloudy surface texture extremely restrained, with no fine noise, busy material veins or added engraving. Do not move or scale the partial ornament to fit the frame.'
(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');(d/'prompt.txt').write_text(r['payload']['prompt'],encoding='utf-8')
rec=json.loads((d/'context.png.generation.json').read_text());rec['sha256']=sha(d/'context.png');rec['derivedFrom'].append({'file':str(s),'sha256':sha(s)});(d/'context.png.generation.json').write_text(json.dumps(rec,indent=2))
print(json.dumps(r))

