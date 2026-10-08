from pathlib import Path
from PIL import Image
import json,numpy as np
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c02-v1/final-v1');T=D.parent.parent.parent
cp=json.loads((D/'source-checkpoint-input.json').read_text(encoding='utf-8'))
tile=Image.open(cp['fragment']['file']).convert('RGBA')
tile.paste(Image.open(D/'joined.png').convert('RGBA'),(909,909))
for name,b in {'out-left-bottom':(789,1833,1189,2190),'out-right-bottom':(1883,1833,2283,2190),'out-top-left':(829,1009,1209,1249),'out-top-right':(1843,1009,2243,1249),'out-bottom':(909,2060,2163,2300)}.items():
 tile.crop(b).save(D/'qa'/f'{name}.png')
a=np.array(Image.open(D/'joined.png').convert('RGB')).mean(2)
b=np.array(Image.open(cp['fragment']['file']).convert('RGB').crop((909,909,2163,2163))).mean(2)
for x in [0,20,60,120,400,800,1200,1253]:
 va=np.abs(np.diff(a[1060:1140,max(0,x-3):min(1254,x+4)].mean(1)))
 vb=np.abs(np.diff(b[1060:1140,max(0,x-3):min(1254,x+4)].mean(1)))
 print(x,'n',np.argsort(va)[-3:]+1060,'c',np.argsort(vb)[-3:]+1060)

