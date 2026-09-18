from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival/quad_r10_c07_c10')
a=Image.open(p/'output/quad_16384x4096_candidate.png').convert('RGB');im=a.crop((12288,0,16384,4096));q=p/'qa';records=[]
for direction in ('vertical','horizontal'):
 for v in (1024,2048,3072):
  board=Image.new('RGB',(1200,1024) if direction=='vertical' else (1024,1200))
  boxes=[]
  for i in range(4):
   box=(v-150,i*1024,v+150,(i+1)*1024) if direction=='vertical' else (i*1024,v-150,(i+1)*1024,v+150)
   board.paste(im.crop(box),(i*300,0) if direction=='vertical' else (0,i*300));boxes.append(box)
  f=q/f'full_{direction}_{v}_100pct.jpg';board.save(f,quality=83)
  records.append({'file':f.name,'localTile':'r10_c10','cropRectsLTRB':boxes,'segmentOrder':'left-to-right' if direction=='vertical' else 'top-to-bottom','pixelScale':1,'resized':False})
for y in (1024,2048,3072):
 for x in (1024,2048,3072):
  im.crop((x-450,y-450,x+450,y+450)).save(q/f'intersection_x{x}_y{y}_100pct.jpg',quality=85)
(q/'full-seam-crops.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Saved 6 full seam bands and 9 original pixel intersections')
