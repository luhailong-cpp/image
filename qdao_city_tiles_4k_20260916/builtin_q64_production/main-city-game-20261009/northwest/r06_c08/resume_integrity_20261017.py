from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08')
sel=json.loads((D/'selection.json').read_text())
info=[]
for p,f in sel.items():
 x=Path(f); result=json.loads((D/'receipts'/(x.stem+'.result.json')).read_text())
 info.append({'patch':p,'id':x.stem,'size':Image.open(x).size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'result':result})
print(json.dumps({'selectedCount':len(sel),'nativeCount':len(list((D/'native').glob('*.png'))),'requestsWithoutNative':[p.name for p in (D/'receipts').glob('*.request.json') if not (D/'native'/(p.name.replace('.request.json','.png'))).exists()],'toolWithoutNative':[p.name for p in (D/'receipts').glob('*.tool.json') if not (D/'native'/(p.name.replace('.tool.json','.png'))).exists()],'selected':[{k:v for k,v in i.items() if k!='result'} for i in info]},indent=2))

