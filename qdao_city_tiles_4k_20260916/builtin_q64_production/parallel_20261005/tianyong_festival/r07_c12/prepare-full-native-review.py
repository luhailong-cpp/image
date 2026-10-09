from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent;O=N/'full-review-native-v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
local=read(N/'local-source-checkpoint.json');src=local['fragment'];assert sha(src['file'])==src['sha256']
im=Image.open(src['file']).convert('RGBA');assert im.size==(4096,4096) and np.all(np.asarray(im)[:,:,3]==255)
raw=(T/'source-checkpoint.json').read_bytes();cp=json.loads(raw.decode('utf-8-sig'))
def source(tile):
 s=next(v for v in cp['candidateSet'] if v['tile']==tile);assert sha(s['file'])==s['sha256'];return s
left=source('r07_c11');sw=source('r08_c11');L=Image.open(left['file']).convert('RGBA');SW=Image.open(sw['file']).convert('RGBA')
# Prove the final neighbor includes every locally generated return; later external returns are allowed elsewhere.
expected={}
for p in local['externalReturnDependencies']:
 tile=p['destinationTile'];box=p['destinationTileLTRB'];assert sha(p['asset']['file'])==p['asset']['sha256']
 expected.setdefault(tile,[]).append(p)
for tile,patches in expected.items():
 base=read(N/'initial-neighbor-sources.json')['sources'][tile];b=Image.open(base['file']).convert('RGBA');mask=np.zeros((4096,4096),bool)
 for p in patches:
  x1,y1,x2,y2=p['destinationTileLTRB'];b.paste(Image.open(p['asset']['file']).convert('RGBA'),(x1,y1));mask[y1:y2,x1:x2]=True
 actual=L if tile=='r07_c11' else SW
 assert np.array_equal(np.asarray(actual)[mask],np.asarray(b)[mask]),'Root missing a final local external return'
O.mkdir(exist_ok=False);(O/'root-checkpoint-at-preparation.json').write_bytes(raw)
idx={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c12','source':src,'sourceSHA256':src['sha256'],'localCheckpoint':ref(N/'local-source-checkpoint.json'),'rootCheckpointAtPreparation':ref(O/'root-checkpoint-at-preparation.json'),'westNeighbor':left,'southWestNeighbor':sw,'externalReturnsPresentExactlyInRoot':True,'images':[],'westBoundaryImages':[],'cornerImages':[],'nativeScale':1,'formalAccepted':False}
cover=np.zeros((4096,4096),np.uint8)
for r,y in enumerate([0,1280,2560],1):
 for c,x in enumerate([0,1280,2560],1):
  ident=f'full-r{r}-c{c}';box=[x,y,x+1536,y+1536];p=O/(ident+'.png');im.crop(box).save(p);cover[y:y+1536,x:x+1536]+=1
  idx['images'].append({'id':ident,'image':ref(p),'tileLocalLTRB':box,'pixels':[1536,1536],'nativeScale':1,'actuallyViewed':False})
assert np.all(cover>0);idx['coveredNativeTilePixels']=int(np.count_nonzero(cover))
for r,y in enumerate([0,1280,2560],1):
 ident=f'west-r{r}';B=Image.new('RGBA',(768,1536));B.paste(L.crop((3712,y,4096,y+1536)),(0,0));B.paste(im.crop((0,y,384,y+1536)),(384,0));p=O/(ident+'.png');B.save(p)
 idx['westBoundaryImages'].append({'id':ident,'image':ref(p),'tileLocalLTRB':[-384,y,384,y+1536],'pixels':[768,1536],'nativeScale':1,'actuallyViewed':False})
B=Image.new('RGBA',(768,768));B.paste(L.crop((3712,3712,4096,4096)),(0,0));B.paste(im.crop((0,3712,384,4096)),(384,0));B.paste(SW.crop((3712,0,4096,384)),(0,384));p=O/'southwest-known-corner.png';B.save(p)
idx['cornerImages'].append({'id':'southwest-known-corner','image':ref(p),'tileLocalLTRB':[-384,3712,384,4480],'pixels':[768,768],'nativeScale':1,'actuallyViewed':False,'missingQuadrants':['southeast r08_c12 absent']})
save(O/'review-image-index.json',idx)
print(json.dumps({'index':ref(O/'review-image-index.json'),'source':src,'images':len(idx['images'])+len(idx['westBoundaryImages'])+len(idx['cornerImages'])}))
