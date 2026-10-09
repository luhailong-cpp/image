from pathlib import Path
from PIL import Image
import numpy as np,json,shutil,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");R=D/'alignment-repair-v2';host=Path(r"C:/Users/luyua/.codex/generated_images/01a11b05-7488-7d11-bfe3-c3b64c8f7651/exec-ad8f1370-afd2-4c50-9153-160dbab3d4fe.png");shutil.copy2(host,R/'native.png')
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
p=json.loads((R/'preparation.json').read_text(encoding='utf-8'));(R/'native.png.generation.json').write_text(json.dumps({'operation':'builtin AI same-world cross-border repair','output':ref(R/'native.png'),'host':ref(host),'preparation':ref(R/'preparation.json'),'configTarget':p['configTarget'],'actualReturnedPixels':[1254,1254],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'nativeScale':1,'formalAccepted':False},indent=2),encoding='utf-8')
for f in ['native.png','source-composite.png']:
 a=np.array(Image.open(R/f).convert('RGB'));o=[]
 for y in [200,500,780,800,900,1100]:
  l=a[y,:,0]>a[y,:,1]*1.7;m=l & (a[y,:,0]>120)
  indices=np.where(m[200:700])[0]+200
  o.append([y,int(indices.min()) if len(indices) else None,int(indices.max()) if len(indices) else None])
 print(f,o)

