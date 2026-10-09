from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
B=Path(__file__).parent;Q=B/'full-tile-qa';Q.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};cur=Image.new('RGBA',(4096,4096));bottom=None;entries=[];previous=None
for row in [4,3,2,1]:
 for col in ([4,3,2,1] if row in [4,2] else [1,2,3,4]):
  D=B/f'r{row:02}_c{col:02}-v1';q=read(D/'request.json');F=D/q.get('selectedFinalDirectory','final-v1');mp=F/'manifest.json';m=read(mp);assert m['requiresPriorManifest']==previous
  for p in m['patches']:
   f=Path(p['asset']['file']);assert ref(f)['sha256']==p['asset']['sha256'];box=p['destinationTileLTRB'];src=p['requiredPriorSource'];im=Image.open(f).convert('RGBA');assert im.size==(box[2]-box[0],box[3]-box[1])
   if p['destinationTile']=='r05_c10':target=cur
   else:
    if bottom is None:bottom=Image.open(src['file']).convert('RGBA')
    target=bottom
   if src:
    assert ref(src['file'])['sha256']==src['sha256'];assert np.array_equal(np.array(target.crop(box)),np.array(Image.open(src['file']).convert('RGBA').crop(box))),str(mp)+' priorROI '+p['name']
   else:assert not np.any(np.array(target.crop(box))[:,:,3])
   target.paste(im,box[:2])
  candidate=F/'r05_c10-fragment.png';assert np.array_equal(np.array(cur),np.array(Image.open(candidate).convert('RGBA')))
  if row==4:assert np.array_equal(np.array(bottom),np.array(Image.open(F/'r06_c10-coupled.png').convert('RGBA')))
  previous=ref(mp);entries.append({'manifest':previous,'candidate':ref(candidate),'coveragePixels':int((np.array(cur)[:,:,3]==255).sum()),'allRequiredPriorROIsExact':True,'allAssetsHashVerified':True})
cp=read(B/'local-source-checkpoint.json');assert ref(cp['fragment']['file'])==cp['fragment'];a=np.array(cur);assert a.shape==(4096,4096,4) and np.all(a[:,:,3]==255);assert np.array_equal(a,np.array(Image.open(cp['fragment']['file']).convert('RGBA')))
for r in range(4):
 for c in range(4):cur.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(Q/f'row{r+1}-col{c+1}-native.png')
cur.convert('RGB').resize((1280,1280),Image.Resampling.LANCZOS).save(Q/'overview-preview-only.png')
out={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r05_c10','tileGlobalLTRB':[36864,16384,40960,20480],'finalFragment':cp['fragment'],'fullCoveragePixels':16777216,'nativeScale':1,'finalRGBAOpaque':True,'manifestCount':len(entries),'sequentialReconstructionExact':True,'entries':entries,'finalCoupled06':cp['coupledBottom'],'noUpscale':True,'formalAccepted':False,'rootPublished':False};(B/'full-chain-integration-proof.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({'proof':ref(B/'full-chain-integration-proof.json'),'final':cp['fragment'],'coverage':16777216}))
