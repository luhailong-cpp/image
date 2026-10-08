from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=T/'source-checkpoint.json'; h=sha(p);cp=json.loads(p.read_text(encoding='utf-8-sig'))
items={}
for v in cp['candidateSet']:
 f=Path(v['file']);assert sha(f)==v['sha256'];im=Image.open(f).convert('RGBA');assert im.size==(4096,4096);a=np.asarray(im)[:,:,3];assert np.all((a==0)|(a==255))
 n=int((a==255).sum());assert v['tile'] not in items
 items[v['tile']]={**v,'actualCoveredNativePixels':n,'fullyPainted':n==4096*4096,'partialFragment':n<4096*4096,'formalAccepted':False}
rows=[]
for r in range(1,17):
 for c in range(1,17):
  tile=f'r{r:02}_c{c:02}';data=items.get(tile);rows.append({'tile':tile,'globalLTRB':[(c-1)*4096,(r-1)*4096,c*4096,r*4096],'status':'complete-native-candidate' if data and data['fullyPainted'] else ('partially-painted' if data else 'unpainted'),'coveredPixels':data['actualCoveredNativePixels'] if data else 0,'source':data})
full=sum(v['fullyPainted'] for v in items.values());partial=sum(not v['fullyPainted'] for v in items.values())
out={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':{'file':str(p),'sha256':h},'cityPixels':[65536,65536],'tilePixels':[4096,4096],'grid':[16,16],'targetTileCount':256,'completeNativeCandidateCount':full,'partialNativeTileCount':partial,'fullyMissingTileCount':256-full-partial,'formalAcceptedCount':0,'wholeCityComplete':False,'clientAccepted':False,'singleCallNative4096Claimed':False,'rows':rows}
assert sha(p)==h
dest=T/'inventory/current-candidate-inventory.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'completeNativeCandidateCount':full,'partialNativeTileCount':partial,'fullyMissingTileCount':256-full-partial,'output':str(dest)}))

