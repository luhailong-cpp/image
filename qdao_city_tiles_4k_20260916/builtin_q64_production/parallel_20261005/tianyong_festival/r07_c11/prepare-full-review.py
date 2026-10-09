from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=(T/'source-checkpoint.json').read_bytes();cp=json.loads(raw.decode('utf-8-sig'))
def source(tile):
    matches=[s for s in cp['candidateSet'] if s['tile']==tile]
    assert len(matches)==1
    s=matches[0];assert sha(s['file'])==s['sha256'];return s
src=source('r07_c11');im=Image.open(src['file']).convert('RGBA');a=np.asarray(im)
assert im.size==(4096,4096) and np.all(a[:,:,3]==255),'Root tile not complete yet'
local=read(N/'local-source-checkpoint.json')['fragment'];assert sha(local['file'])==local['sha256']
b=np.asarray(Image.open(local['file']).convert('RGBA')).copy();appliedRepair=None
if len(sys.argv)>2:
 mf=Path(sys.argv[2]);assert sha(mf)==sys.argv[3];m=read(mf)
 for patch in m['patches']:
  assert patch['destinationTile']=='r07_c11' and sha(patch['asset']['file'])==patch['asset']['sha256']
  x1,y1,x2,y2=patch['destinationTileLTRB'];asset=np.array(Image.open(patch['asset']['file']).convert('RGBA'))
  prior=patch['requiredPriorSource'];assert sha(prior['file'])==prior['sha256'];priorroi=np.array(Image.open(prior['file']).convert('RGBA').crop((x1,y1,x2,y2)))
  assert np.array_equal(b[y1:y2,x1:x2],priorroi),'Repair baseline mismatch'
  assert np.array_equal(a[y1:y2,x1:x2],asset),'Root has not integrated exact repair yet'
  b[y1:y2,x1:x2]=asset
 appliedRepair=ref(mf)
changed=np.any(a!=b,axis=2)
assert not changed[:4035].any(),'Unexpected root changes outside coupled south-return band'
O=N/sys.argv[1];O.mkdir(exist_ok=False);(O/'source-checkpoint.json').write_bytes(raw)
index={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':src,'sourceSHA256':src['sha256'],'sourceCheckpoint':ref(O/'source-checkpoint.json'),'localCompleteSource':local,'appliedLocalRepair':appliedRepair,'rootDifferenceFromLocal':{'baseline':'Local complete source plus explicitly listed appliedLocalRepair, if any','changedPixels':int(changed.sum()),'restrictedToTileLocalLTRB':[0,4035,4096,4096],'allPixelsOutsideBandExactlyIdentical':True},'images':[],'westBoundaryImages':[],'southBoundaryImages':[]}
cover=np.zeros((4096,4096),np.uint8)
for r,y in enumerate([0,1280,2560],1):
 for c,x in enumerate([0,1280,2560],1):
  box=[x,y,x+1536,y+1536];ident=f'full-r{r}-c{c}';p=O/(ident+'.png');im.crop(box).save(p);cover[y:y+1536,x:x+1536]+=1
  index['images'].append({'id':ident,'image':ref(p),'tileLocalLTRB':box,'pixels':[1536,1536],'nativeScale':1,'actuallyViewed':False})
assert np.all(cover>0);index['coveredPixels']=int(np.count_nonzero(cover));index['minViewCoverage']=int(cover.min())
left=source('r07_c10');L=Image.open(left['file']).convert('RGBA');assert np.all(np.asarray(L)[:,:,3]==255)
index['westNeighbor']=left
for r,y in enumerate([0,1280,2560],1):
 ident=f'west-r{r}';B=Image.new('RGBA',(768,1536));B.paste(L.crop((3712,y,4096,y+1536)),(0,0));B.paste(im.crop((0,y,384,y+1536)),(384,0));p=O/(ident+'.png');B.save(p)
 index['westBoundaryImages'].append({'id':ident,'image':ref(p),'tileLocalLTRB':[-384,y,384,y+1536],'nativeScale':1,'pixels':[768,1536],'actuallyViewed':False})
below=source('r08_c11');B=Image.open(below['file']).convert('RGBA');index['southNeighbor']=below
if np.all(np.asarray(B)[:384,:,3]==255):
 for c,x in enumerate([0,1280,2560],1):
  ident=f'south-c{c}';S=Image.new('RGBA',(1536,768));S.paste(im.crop((x,3712,x+1536,4096)),(0,0));S.paste(B.crop((x,0,x+1536,384)),(0,384));p=O/(ident+'.png');S.save(p)
  index['southBoundaryImages'].append({'id':ident,'image':ref(p),'tileLocalLTRB':[x,3712,x+1536,4480],'nativeScale':1,'pixels':[1536,768],'actuallyViewed':False})
save(O/'review-image-index.json',index)
print(json.dumps({'directory':str(O),'index':ref(O/'review-image-index.json'),'source':src,'rootDifferenceFromLocal':index['rootDifferenceFromLocal'],'fullImages':len(index['images']),'westImages':len(index['westBoundaryImages']),'southImages':len(index['southBoundaryImages'])}))
