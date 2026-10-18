from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageChops
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
oldq=Z/'qa/r07_c04_v6_internal_delta_review/qa_index.json'
old=json.loads(oldq.read_text(encoding='utf-8-sig'))
p=Z/'tiles/r07_c04_candidate-v7_4096.png';rp=p.with_suffix('.native-repair.json')
qdir=Z/'qa/r07_c04_v7_internal_delta_root_20261016';qdir.mkdir(exist_ok=True)
im=Image.open(p).convert('RGB');entries=[];changed=[];unchanged=[]
for x in old['seamAndJunctionCrops']:
 before=Path(x['path']);assert sha(before)==x['sha256']
 current=im.crop(tuple(x['tileCropBoxHalfOpen']));same=ImageChops.difference(current,Image.open(before).convert('RGB')).getbbox() is None
 name=before.name
 if same:
  e={**x,'reuseBasis':'Current final crop has exactly unchanged RGB pixels from the hash-bound prior crop.'};unchanged.append(name)
 else:
  out=qdir/name
  if out.exists(): assert ImageChops.difference(current,Image.open(out).convert('RGB')).getbbox() is None
  else: current.save(out)
  e={**x,**pin(out),'reviewStatus':'PENDING_NATIVE_DELTA_REVIEW','prior':pin(before)};e.pop('reusedUnchangedV1Crop',None);changed.append(name)
 entries.append(e)
index={'candidate':pin(p),'record':pin(rp),'priorIndex':pin(oldq),'seamAndJunctionCrops':entries,'changedNames':changed,'unchangedNames':unchanged,'coverage':old.get('coverage',{'cropCount':len(entries),'junctionCount':9,'finalVerticalSeamBands':3,'finalHorizontalSeamBands':3,'eachBandFullyCoveredAt100Percent':True}),'internalClosurePassed':False,'formalAccepted':False}
(qdir/'qa_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
baseline=Z/'tiles/r07_c04_candidate-v6_4096.png';a=np.array(Image.open(baseline).convert('RGB'));n=np.array(im);edges={}
for side,b in {'north':[0,0,4096,115],'south':[0,3981,4096,4096],'west':[0,0,115,4096],'east':[3981,0,4096,4096]}.items():
 x0,y0,x1,y1=b;before=a[y0:y1,x0:x1];after=n[y0:y1,x0:x1];edges[side]={'tileBox':b,'changedPixelsVsV6':int(np.count_nonzero(np.any(before!=after,axis=2))),'currentRgbSha256':hashlib.sha256(after.tobytes()).hexdigest()}
ed={'candidate':pin(p),'baseline':pin(baseline),'edges':edges,'externalVisualAcceptance':False}
(qdir/'outer115_delta.json').write_text(json.dumps(ed,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qaIndex':pin(qdir/'qa_index.json'),'changedNames':changed,'unchangedCount':len(unchanged),'edgeDeltas':edges}))
