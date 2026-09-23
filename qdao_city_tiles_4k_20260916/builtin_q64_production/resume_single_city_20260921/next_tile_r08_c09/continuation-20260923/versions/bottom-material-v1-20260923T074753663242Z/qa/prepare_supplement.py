from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).resolve().parent
V=P.parent
BASE=V.parent/'hard-core-20260923T070734660600Z'
SESSION=V.parents[3]
NEIGHBOR=SESSION/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
assert sha(V/'r08_c09.png')=='534b82614f5b9dfbfd4441f8f6e10080668989bc11c2f560ed501bf12183ffbf'
assert sha(NEIGHBOR)=='5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c'
before=Image.open(BASE/'r08_c09.png').convert('RGB');after=Image.open(V/'r08_c09.png').convert('RGB');bottom=Image.open(NEIGHBOR).convert('RGB');items=[]
def save(name,im,sources,operation):
    f=P/(name+'.png');assert not f.exists();im.save(f);items.append({'id':name,**info(f),'pixels':list(im.size),'pixelScale':'1:1','sources':sources,'operation':operation})
for x in [1024,2048,3072]:
    box=[x-384,3328,x+384,4096]
    save(f'wide-v{x}-before',before.crop(box),[info(BASE/'r08_c09.png')],{'cropLTRB':box})
    save(f'wide-v{x}-after',after.crop(box),[info(V/'r08_c09.png')],{'cropLTRB':box})
for x0,name in [(2304,'focus-bottom-gold-joint'),(2944,'wide-bottom-fourth')]:
    w=384 if name.startswith('focus') else 1152
    h=192 if name.startswith('focus') else 576
    out=Image.new('RGB',(w,h*2));out.paste(after.crop((x0,4096-h,x0+w,4096)),(0,0));out.paste(bottom.crop((x0,0,x0+w,h)),(0,h))
    save(name,out,[info(V/'r08_c09.png'),info(NEIGHBOR)],{'candidateCropLTRB':[x0,4096-h,x0+w,4096],'neighborCropLTRB':[x0,0,x0+w,h],'boundaryY':h})
with (P/'supplement-index.json').open('x',encoding='utf-8') as f:json.dump({'script':info(Path(__file__)),'evidence':items,'resized':False,'accepted':False},f,indent=2)
print(json.dumps({'evidenceCount':len(items)}))
