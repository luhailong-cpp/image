from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
first=read(D/'r04_c01-v1/preparation.json')
inputs={'r07_c10':first['northPriorFragment'],'r08_c10':first['sourceTile'],'r08_c09':first['bottomLeftTile']}
for v in inputs.values(): assert ref(v['file'])['sha256']==v['sha256']
tiles={k:np.array(Image.open(v['file']).convert('RGBA')) for k,v in inputs.items()}
paths=['r04_c01-v1/final-v1','r03_c01-v1/final-v3','r03_c02-v1/final-v1','r03_c03-v1/final-v1','r03_c04-v1/final-v1']+[f'r02_c{c:02}-v1/final-v1' for c in [4,3,2,1]]+[f'r01_c{c:02}-v1/final-v1' for c in [1,2,3,4]]
proofs=[]
for sub in paths:
 mp=D/sub/'manifest.json';m=read(mp);assert ref(m['joined']['file'])==m['joined'];j=Image.open(m['joined']['file']).convert('RGB');window=m['windowGlobalLTRB'];out=[]
 for p in m['patches']:
  assert ref(p['asset']['file'])==p['asset'];asset=Image.open(p['asset']['file']).convert('RGB');assert np.array_equal(np.array(asset),np.array(j.crop(p['cropFromJoinedLTRB'])))
  tile=p['destinationTile'];l,t,r,b=p['destinationTileLTRB'];assert asset.size==(r-l,b-t);crop=p['cropFromJoinedLTRB'];rr=int(tile[1:3]);cc=int(tile[5:7])
  assert [window[0]+crop[0],window[1]+crop[1],window[0]+crop[2],window[1]+crop[3]]==[(cc-1)*4096+l,(rr-1)*4096+t,(cc-1)*4096+r,(rr-1)*4096+b]
  current=tiles[tile][t:b,l:r];prior=p['requiredPriorSource']
  if prior:
   assert ref(prior['file'])['sha256']==prior['sha256'];source=np.array(Image.open(prior['file']).convert('RGBA'))[t:b,l:r];assert np.array_equal(current,source),(sub,p['name'],'prior mismatch')
  else:assert not np.any(current[:,:,3]),(sub,p['name'],'new already covered')
  tiles[tile][t:b,l:r]=np.array(asset.convert('RGBA'));out.append({'name':p['name'],'pixelSourceVerified':True,'worldPositionVerified':True,'requiredPriorROIExact':True,'nativeScale':1})
 expected=np.array(Image.open(D/sub/'r07_c10-fragment.png').convert('RGBA'));assert np.array_equal(tiles['r07_c10'],expected),(sub,'full fragment mismatch')
 proofs.append({'manifest':ref(mp),'patches':out,'reconstructedFullFragmentExact':True,'coveragePixels':int(np.count_nonzero(expected[:,:,3]==255))})
assert proofs[-1]['coveragePixels']==4096*4096
cp=read(D/'local-source-checkpoint.json');assert ref(cp['fragment']['file'])==cp['fragment'];assert np.array_equal(tiles['r07_c10'],np.array(Image.open(cp['fragment']['file']).convert('RGBA')))
out={'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initialTiles':inputs,'proofs':proofs,'finalCheckpoint':ref(D/'local-source-checkpoint.json'),'finalFragment':cp['fragment'],'coveragePixels':4096*4096,'allPixelsOpaque':True,'formalAccepted':False,'rootPublished':False,'note':'Read-only validation of thirteen sequential local manifests after prior r04_c02. Root publication requires live current ROI validation. No root state changed.'}
(D/'full-chain-integration-proof.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'proof':ref(D/'full-chain-integration-proof.json'),'manifests':len(proofs),'coverage':proofs[-1]['coveragePixels'],'finalFragment':cp['fragment']}))
