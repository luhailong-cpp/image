from pathlib import Path
import json, hashlib
from PIL import Image
from datetime import datetime, timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; QA=Path(__file__).parent; OUT=ROOT/'output/r09_c13'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
r=read(QA/'review.json');m=read(OUT/'manifest.json');final=OUT/'r09_c13.png';old=Path(m['westSource'])
pair=Image.new('RGB',(320,4096));pair.paste(Image.open(old).crop((3936,0,4096,4096)),(0,0));pair.paste(Image.open(final).crop((0,0,160,4096)),(160,0))
for i in range(4):
    p=QA/f'shared-unrotated-{i+1}.png';pair.crop((0,i*1024,320,(i+1)*1024)).save(p)
    q=dict(**ref(p),pixels=[320,1024],scale=1,actuallyViewed=False,operation=dict(pairCropLTRB=[3936,i*1024,4256,(i+1)*1024],sharedEdgeImageX=160))
    r['qa'].append(q);m['qa'].append(q)
    write(str(p)+'.generation.json',dict(**q,createdAt=datetime.now(timezone.utc).isoformat(),derivedFrom=[ref(old),ref(final)],kind='native_pixel_QA_crop',sourceUpscaling=False))
a=np.array(pair).astype(float)
r['boundaryStatisticsForVisualFollowup']=[]
for y0,y1 in [(0,320),(400,600),(1100,1600),(1600,2050),(2200,2500),(2800,3200),(3700,3950),(3950,4096)]:
    d=a[y0:y1,160]-a[y0:y1,159]
    r['boundaryStatisticsForVisualFollowup'].append(dict(yRange=[y0,y1],meanRGBJump=d.mean(axis=0).tolist(),medianRGBJump=np.median(d,axis=0).tolist(),meanAbsoluteJump=float(abs(d).mean())))
write(QA/'review.json',r);write(OUT/'manifest.json',m)
print(json.dumps(r['boundaryStatisticsForVisualFollowup']))
