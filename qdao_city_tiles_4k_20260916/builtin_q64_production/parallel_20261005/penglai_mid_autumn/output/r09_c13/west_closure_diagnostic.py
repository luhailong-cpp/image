from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/r09_c13';QA=ROOT/'qa/west-final/closure';QA.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
m=read(OUT/'manifest.json');old=Path(m['westSource']);target=OUT/'r09_c13.png'
a=np.array(Image.open(old).convert('RGB')).astype(float);b=np.array(Image.open(target).convert('RGB')).astype(float)
pair=np.concatenate([a[:,-160:],b[:,:512]],axis=1).astype(np.uint8)
for name,box in [('north-rail-micro.png',[96,0,256,160]),('north-shadow-micro.png',[128,120,224,320]),('floor-bottom-context.png',[0,1560,672,2880]),('rail-context.png',[0,2640,672,3280]),('north-floor-context.png',[0,340,672,1004]),('mid-floor-micro.png',[32,1744,288,2000]),('lower-floor-micro.png',[32,2350,288,2606]),('roof-face-context.png',[0,3100,672,4096]),('roof-color-micro.png',[32,3370,288,3626])]:
    p=QA/name;Image.fromarray(pair).crop(box).save(p);write(str(p)+'.generation.json',dict(**ref(p),source=[ref(old),ref(target)],pairCropLTRB=box,nativeScale=1,operation='native_pixel_crop_no_resampling'))
lg=np.max(abs(np.diff(a[:,-4:],axis=1)),axis=(1,2));ng=np.max(abs(np.diff(b[:,:4],axis=1)),axis=(1,2))
d=b[:,0]-a[:,-1];valid=(lg<10)&(ng<10)
rows=[]
for y in range(0,4096,128):
    ids=np.arange(y,min(4096,y+128));ids=ids[valid[ids]]
    rows.append(dict(y=[y,min(4096,y+128)],flatSupportRows=len(ids),medianRGB=np.median(d[ids],axis=0).tolist() if len(ids) else None))
write(QA/'diagnostic.json',dict(input=ref(target),old=ref(old),flatSupportStatistics=rows))
print(json.dumps(rows))
