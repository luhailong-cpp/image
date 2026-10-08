from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent; P=D.parent; T=P.parent.parent
(D/'qa').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp_path=P/'source-checkpoint-v015.json'
assert sha(cp_path)=='a127c39dc80e894748d6349b15edf248362122b3a2bda075d8190348b384c694'
cp=json.loads(cp_path.read_text(encoding='utf-8'))
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((1933,909,3187,2163)))
n=np.array(Image.open(P/'native.png').convert('RGB')).astype(np.float32)
r=np.array(Image.open(P/'left-lower-repair-v1/native.png').convert('RGB')).astype(np.float32)
h,w=n.shape[:2];yy,xx=np.mgrid[:h,:w].astype(np.float32)
# The first native image supplies the already accepted body. The actual AI repair
# replaces only the small gray-channel foot, never the full edited frame.
ra=np.minimum.reduce([np.clip((xx-150)/16,0,1),np.clip((620-xx)/50,0,1),np.clip((yy-900)/30,0,1),np.clip((1160-yy)/30,0,1)])
repaired=n*(1-ra[:,:,None])+r*ra[:,:,None]
# Known bands are exact-source outside explicit narrow returns.
a=np.minimum.reduce([np.clip((xx-150)/80,0,1),np.clip((1104-xx)/80,0,1),np.clip((yy-150)/80,0,1),np.clip((1104-yy)/80,0,1)])
a=np.maximum(a,ra)
out=np.rint(repaired*a[:,:,None]+c[:,:,:3].astype(float)*(1-a[:,:,None])).clip(0,255).astype(np.uint8)
Image.fromarray(out).save(D/'joined.png')
Image.fromarray(np.uint8(a*255)).save(D/'mask.png')
Image.fromarray(np.uint8(ra*255)).save(D/'repair-mask.png')
qa={'top':(0,100,1254,350),'left':(100,0,400,1254),'right':(924,0,1174,1254),'bottom':(0,950,1254,1254),'left-lower':(50,850,700,1220),'foot-finding':(130,1000,625,1200),'top-left':(80,80,500,500),'bottom-right':(850,850,1200,1200),'bottom-return':(120,1110,660,1220),'left-return':(90,820,220,1220),'right-return':(1050,100,1170,1190),'top-return':(100,80,1150,260)}
for name,b in qa.items():Image.fromarray(out).crop(b).save(D/'qa'/f'{name}.png')
assembly={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':info(cp_path),'sources':[info(P/'native.png'),info(P/'left-lower-repair-v1/native.png'),cp['fragment']],'method':'Two true native AI sources, explicit repaired foot ROI and known-edge returns; no resize, geometric warp or sharpening.','nativeScale':1,'maxAbsDx':0,'maxAbsDy':0,'maxAbsToneRGB':0,'joined':info(D/'joined.png'),'mask':info(D/'mask.png'),'repairMask':info(D/'repair-mask.png'),'qaCrops':qa,'reviewStatus':'pending'}
(D/'source-checkpoint-input.json').write_bytes(cp_path.read_bytes())
assembly['repairReadLTRB']=[150,900,620,1160]
assembly['repairReadReason']='The actual repaired gray foot and adjacent ivory foot belong to one continuous structure. Cropping at the originally masked x425 cuts the same actual AI-rendered foot and introduces a 6px edge mismatch; the native source is therefore taken through its complete foot to x620 before returning over featureless matching stone.'
assembly['fades']={'knownSourceReturn':80,'repairLeft':16,'repairRight':50,'repairTop':30,'repairBottom':30}
assembly['knownPixelsUnchangedOutsideMask']=bool(np.array_equal(out[(a==0)&(c[:,:,3]==255)],c[:,:,:3][(a==0)&(c[:,:,3]==255)]))
assembly['newPixels630436AllOpaque']=bool(np.all(a[c[:,:,3]==0]==1))
before=np.array(Image.open(P/'naive-v015.png').convert('RGB'))
Image.fromarray(before).crop((130,1000,625,1200)).save(D/'qa'/'foot-finding-before.png')
prospective=np.array(Image.open(cp['fragment']['file']).convert('RGBA'))
prospective[909:2163,1933:3187,:3]=out
prospective[909:2163,1933:3187,3]=255
Image.fromarray(prospective).crop((1983,1759,2633,2129)).save(D/'qa'/'out-left-lower.png')
(D/'assembly.json').write_text(json.dumps(assembly,indent=2),encoding='utf-8')
print(json.dumps({'joined':info(D/'joined.png'),'newCount':int((c[:,:,3]==0).sum())}))
