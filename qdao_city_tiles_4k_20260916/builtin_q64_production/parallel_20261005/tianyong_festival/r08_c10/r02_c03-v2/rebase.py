from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c03-v2');T=D.parent.parent
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
(D/'source-checkpoint-v015.json').write_bytes((T/'source-checkpoint.json').read_bytes())
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((1933,909,3187,2163)))
Image.fromarray(c).save(D/'context-v015.png')
n=np.array(Image.open(D/'native.png').convert('RGB')); j=n.copy();m=c[:,:,3]==255;j[m]=c[:,:,:3][m]
Image.fromarray(j).save(D/'naive-v015.png')
Image.fromarray(j).crop((0,850,550,1254)).save(D/'left-bottom-naive.png')
Image.fromarray(n).crop((0,850,550,1254)).save(D/'left-bottom-native.png')

