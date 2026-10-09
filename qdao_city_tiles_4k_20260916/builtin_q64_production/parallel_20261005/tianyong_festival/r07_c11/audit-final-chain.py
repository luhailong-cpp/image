from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
N=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
cp=read(N/'local-source-checkpoint.json');refs=[];items=[];seen=set()
def verify(v):
 if isinstance(v,dict):
  if isinstance(v.get('file'),str) and isinstance(v.get('sha256'),str):
   k=(v['file'],v['sha256'])
   if k not in seen:
    assert sha(v['file'])==v['sha256'],v['file'];seen.add(k);refs.append({'file':v['file'],'sha256':v['sha256']})
  for s in v.values():verify(s)
 elif isinstance(v,list):
  for s in v:verify(s)
assert len(cp['manifestChain'])==16 and cp['coveragePixels']==4096**2
for mr in cp['manifestChain']:
 verify(mr);m=read(mr['file']);verify(m)
 for p in m['patches']:
  im=Image.open(p['asset']['file']);b=p['destinationTileLTRB'];assert im.size==(b[2]-b[0],b[3]-b[1])
 D=Path(mr['file']).parents[1]
 generation=read(D/'native.png.generation.json');verify(generation)
 assert generation.get('actualModel') is None and generation.get('actualQuality') is None
 review=read(m['visualReview']['file']);assert review.get('localVisualAccepted') and not review.get('findings');verify(review)
 items.append({'manifest':mr,'nativeGeneration':{'file':str(D/'native.png.generation.json'),'sha256':sha(D/'native.png.generation.json')},'patchCount':len(m['patches']),'visualReview':m['visualReview']})
rep=N/'r03_c03-v1'
for name in ['native-original.png','repair-1-native.png','repair-2-native.png']:
 g=read(rep/(name+'.generation.json'));verify(g);assert g.get('actualModel') is None and g.get('actualQuality') is None
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c11','completeNativePixels':cp['coveragePixels'],'manifestCount':16,'nativeBaseOutpaintingCalls':16,'extraActualRepairCalls':2,'totalActualBuiltinImageCalls':18,'actualModel':None,'actualQuality':None,'actualHostParametersUndisclosed':True,'manifestAndSourceReferenceHashesVerified':len(refs),'records':items,'verifiedReferences':refs,'rootStateModified':False,'formalAccepted':False,'note':'Audit of immutable local chain, source/image hashes and exact ROI dimensions. Final whole-tile visual approval requires the latest root-integrated tile with newer coupled south-return ROIs.'}
p=N/'final-chain-audit.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'file':str(p),'sha256':sha(p),'verifiedReferences':len(refs),'manifestCount':len(items),'actualBuiltinCalls':18}))
