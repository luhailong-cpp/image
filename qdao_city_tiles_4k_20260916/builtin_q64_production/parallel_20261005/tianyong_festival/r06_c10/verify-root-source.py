from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r06_c10");T=B.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{"file":str(p),"sha256":sha(p)}
cpPath=T/'source-checkpoint.json';cp=json.loads(cpPath.read_text(encoding='utf-8-sig'))
candidates=cp['candidateSet']; source=next(s for s in candidates if s['tile']=='r06_c10')
assert sha(source['file'])==source['sha256']
local=B/'r01_c04-v1/final-v1/r06_c10-fragment.png'; a=np.array(Image.open(local).convert('RGBA'));r=np.array(Image.open(source['file']).convert('RGBA'))
assert np.array_equal(a,r)
south=next(s for s in candidates if s['tile']=='r07_c10');assert sha(south['file'])==south['sha256']
rootSouth=np.array(Image.open(south['file']).convert('RGBA'));ls=np.array(Image.open(B/'r04_c01-v1/final-v1/r07_c10-coupled.png').convert('RGBA'))
diff=np.any(rootSouth[:320]!=ls[:320],axis=2); yy,xx=np.where(diff)
changed={"pixels":int(diff.sum()),"tileLocalLTRB":([int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None)}
combined=np.concatenate([r[-320:],rootSouth[:320]],axis=0)
paths=[]
for k,x in enumerate([0,1280,2560],1):
 p=B/f'full-tile-qa/root-south-overlap-{k}-native.png';Image.fromarray(combined[:,x:x+1536]).save(p);paths.append(ref(p))
v={"rootCheckpoint":ref(cpPath),"source":source,"reviewedLocalSource":ref(local),"rootVsReviewedLocalPixelIdentical":True,"rootVsReviewedLocalDifferentPixels":0,"rootSouth":south,"southVsReviewedLocal":changed,"rootSouthPanels":paths}
(B/'root-source-pixel-verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(v,ensure_ascii=False))

