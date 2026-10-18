from pathlib import Path
from PIL import Image
import numpy as np, hashlib, json
from datetime import datetime,timezone
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/village-west-courtyard')
O=B/'qa/r12c07-resume2-north-review-v1'
S=B/'qa/r12c07-resume2-r18-v1/context-native.png'
Q=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest/qa')
N=Q/'block2x2-r10r11c06c07-v3-r11_c07-context-native.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
n=np.asarray(Image.open(N).convert('RGB'));s=np.asarray(Image.open(S).convert('RGB'))
assert n.shape==s.shape==(4326,4326,3)
assert sha(N)=='2145b89fd06d761e00b6e3cdc0ded93caa18f917f81801b47cc72f7a3322cc5a'
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'read-only actual core join','north':{'path':N.as_posix(),'sha256':sha(N),'globalContextBox':[24461,40845,28787,45171]},'south':{'path':S.as_posix(),'sha256':sha(S),'globalContextBox':[24461,44941,28787,49267]},'seamGlobalY':45056,'noResize':True,'noBlend':True,'sourceModified':False,'strips':[]}
for i in range(4):
 x=115+1024*i;a=n[3866:4211,x:x+1024];b=s[115:460,x:x+1024];c=np.concatenate([a,b]);p=O/f'N{i+1:02d}-actual-core-join-native.png';Image.fromarray(c).save(p);d=np.asarray(Image.open(p))
 out['strips'].append({'id':f'N{i+1:02d}','path':p.as_posix(),'sha256':sha(p),'size':[1024,690],'northContextBox':[x,3866,x+1024,4211],'southContextBox':[x,115,x+1024,460],'globalBox':[24461+x,44711,24461+x+1024,45401],'joinYInStrip':345,'northCropIdentityDifferentPixels':int(np.any(d[:345]!=a,axis=2).sum()),'southCropIdentityDifferentPixels':int(np.any(d[345:]!=b,axis=2).sum())})
(O/'qa-inputs-v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'northSha':out['north']['sha256'],'southSha':out['south']['sha256'],'strips':len(out['strips']),'cropIdentityDifferentPixels':sum(x['northCropIdentityDifferentPixels']+x['southCropIdentityDifferentPixels'] for x in out['strips'])}))
for name in ['block2x2-r10r11c06c07-v3-trace.json','block2x2-r10r11c06c07-v2-trace.json','full-tile-r11_c07-assembly.json','repair-r11_c07-internal-v1-trace.json']:
 j=json.loads((Q/name).read_text(encoding='utf-8-sig'))
 print(name,list(j))
 for k,v in j.items():
  if k in ['base','baseTrace','inputs','sources','context','r11_c07','tiles','outputs','repair','patches']:
   print(k, str(v)[:1800])
