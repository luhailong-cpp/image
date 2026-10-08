from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image

ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005')
T=ROOT/'lanxian_spring/r08_c10';O=ROOT/'parent_audit_20261008/town/southwest-current-qa';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={'c10core':T/'selected-v2/core4096.png','c10extended':T/'selected-v2/extended4326.png','c09core':ROOT/'lanxian_spring/r08_c09/repairs/join-endpoint/candidate_4096.png','c09extended':ROOT/'lanxian_spring/r08_c09/repairs/join-endpoint/candidate_with_halo.png','currentSouthwestCrop':T/'spring-edits/southwest/edited-1254.png','oldWestBoard':T/'shared-geometry/qa/southwest/west-seam-04-y3072-4096.png'}
sources={k:{'path':str(p),'sha256':sha(p)} for k,p in files.items()};ims={k:Image.open(p).convert('RGB') for k,p in files.items()}
assert sources['c10core']['sha256']=='482a2c7d3e3bfe648c067bd9f55e56f68ca9d7fa0f5f8e68736808b9b83b3e9e'
assert sources['c09core']['sha256']=='eacc709f26e6224c3b24e493bb4a3a60b8eb44cda18afa787e208f5a1805ff38'
assert np.array_equal(np.asarray(ims['currentSouthwestCrop']),np.asarray(ims['c10extended'].crop((0,3072,1254,4326))))
boards=[]
def make(name,size,parts,purpose):
 board=Image.new('RGB',size)
 mappings=[]
 for key,box,xy in parts:
  q=ims[key].crop(tuple(box));board.paste(q,xy);mappings.append({'sourceKey':key,'sourceBoxLTRB':box,'boardBoxLTRB':[xy[0],xy[1],xy[0]+q.width,xy[1]+q.height]})
 p=O/name;board.save(p)
 boards.append({'path':str(p),'sha256':sha(p),'pixels':list(size),'purpose':purpose,'mappings':mappings,'resampling':None})
make('01-current-west-y3072-4096.png',(1024,1024),[('c09core',[3584,3072,4096,4096],(0,0)),('c10core',[0,3072,512,4096],(512,0))],'Current c09/c10 shared west seam, join at boardx512; entire native1024 bottom segment.')
make('02-current-southwest-corner-with-halo.png',(1024,512),[('c09extended',[3699,3814,4211,4326],(0,0)),('c10extended',[115,3814,627,4326],(512,0))],'Current shared lower corner y3699:4211. Bottom115px are halo; missing southern neighbor is not accepted by this image.')
make('03-old-current-changed-region.png',(1024,608),[('oldWestBoard',[512,416,1024,1024],(0,0)),('c10core',[0,3488,512,4096],(512,0))],'Left historical viewed crop; right current selected crop. Current local coordinates x0:512,y3488:4096. No scaling.')
make('04-current-rail-gold-highlight.png',(512,320),[('c09core',[3968,3480,4096,3800],(0,0)),('c10core',[0,3480,384,3800],(128,0))],'Rail crossing true external seam x128, then current gold-highlight irregularity at corex115,y3680 (boardx243,y200).')
make('05-current-planter-return-boundaries.png',(512,400),[('c10core',[0,3696,512,4096],(0,0))],'Current planter/stone/foliage and lower return surfaces around all changed pixels; original scale.')
old=np.asarray(ims['oldWestBoard'].crop((512,0,1024,1024)));new=np.asarray(ims['c10core'].crop((0,3072,512,4096)));diff=np.any(old!=new,axis=2);yy,xx=np.where(diff)
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Read-only source pixel audit; integer crop/paste into parent audit QA images only; no resizing/warp/blend or active task file write.','sources':sources,'boards':boards,'currentSouthwestCropEqualsCurrentExtendedROI':[0,3072,1254,4326],'changedPixelsFromHistoricalWestBoard':int(diff.sum()),'changedBBoxCoreLTRB':[int(xx.min()),int(yy.min()+3072),int(xx.max()+1),int(yy.max()+3073)],'actualVisualReview':'pending; preparation alone is not review','formalAccepted':False,'wholeCityComplete':False}
for k,p in files.items():report['sources'][k]['afterSha256']=sha(p);assert report['sources'][k]['afterSha256']==report['sources'][k]['sha256']
(O/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(O/'manifest.json'),'boards':[{k:b[k] for k in ('path','pixels')} for b in boards],'changedPixels':int(diff.sum())}))
