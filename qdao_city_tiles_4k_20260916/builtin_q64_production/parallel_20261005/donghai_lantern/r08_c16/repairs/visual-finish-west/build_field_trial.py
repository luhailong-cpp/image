from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
T=B.parent.parent
BASE=T/'repairs/approved-sync/output/r08_c16.png'
WEST=T.parent/'r08_c15/west-common-edge-v3/output/r08_c15.png'
BASE_SHA='7d821e83179cae126dd4e0f1be7f6b83f6a762bfe7b0f0caa4bfa3ec8de0bb22'
WEST_SHA='7c18bf09e962b458ee285c04067655d6198c426d2bb53cccbe13bc58f24c8a4f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
assert sha(BASE)==BASE_SHA and sha(WEST)==WEST_SHA
im=np.array(Image.open(BASE).convert('RGB')); w=np.array(Image.open(WEST).convert('RGB'))
# Estimate local continuous material jump from opposite immediate boundary strips.
l=np.median(w[:,-7:-1].astype(np.float32),axis=1)
r=np.median(im[:,1:7].astype(np.float32),axis=1)
raw=l-r
rgb=(l+r)/2
classes=np.where((rgb[:,2]>rgb[:,0]+12)&(rgb[:,2]>rgb[:,1]-3),0,np.where(rgb[:,0]>rgb[:,2]+12,1,2))
sm=np.zeros_like(raw)
for y in range(4096):
    ids=np.arange(max(0,y-12),min(4096,y+13))
    ids=ids[classes[ids]==classes[y]]
    dy=ids-y;weights=(1-(dy/13)**2)**2
    vals=np.clip(raw[ids],-24,24)
    sm[y]=np.sum(vals*weights[:,None],axis=0)/weights.sum()
sm=np.clip(sm,-24,24)
xs=np.arange(220,dtype=np.float32)
fall=(1-(xs/219)**2)**2
field=sm[:,None,:]*fall[None,:,None]
candidate=im.copy()
candidate[:,:220]=np.clip(np.rint(im[:,:220].astype(np.float32)+field),0,255).astype(np.uint8)
assert np.abs(candidate.astype(np.int16)-im.astype(np.int16)).max()<=24
assert np.array_equal(candidate[:,220:],im[:,220:])
out=B/'field-trial'
out.mkdir(exist_ok=True)
Image.fromarray(candidate).save(out/'candidate.png')
np.savez_compressed(out/'field.npz',offset=field.astype(np.float32),boundaryRawDifference=raw,boundaryAppliedDifference=sm,materialClasses=classes)
refs=[ref(BASE),ref(WEST)]
write(out/'candidate.png.generation.json',{'operation':'bounded RGB additive color field; no image blur/warp/resampling','derivedFrom':refs,'maxAbsRGBDelta':24,'supportTileXYXY':[0,0,220,4096],'model':None,'AIgenerated':False,'visualReview':'pending'})
qa=[]
pair=Image.fromarray(np.concatenate([w,candidate],axis=1))
for i,y in enumerate((0,1024,2048,3072),1):
    box=[4096-448,y,4096+448,y+1024];p=out/f'pair-part{i}.png';pair.crop(box).save(p)
    q={**ref(p),'pairRectXYXY':box,'operation':'exact original-pixel crop','resized':False,'derivedFrom':refs+[ref(out/'candidate.png')]}
    write(Path(str(p)+'.generation.json'),q);qa.append(q)
stats={'unclippedRawBoundaryMax':np.abs(raw).max(0).tolist(),'medianAbsRawBoundary':np.median(np.abs(raw),axis=0).tolist(),'rowsRawExceed24':int((np.abs(raw).max(1)>24).sum()),'fieldMax':float(np.abs(field).max()),'outsideSupportChangedPixels':0}
write(out/'manifest.json',{'generatedUtc':datetime.now(timezone.utc).isoformat(),'base':ref(BASE),'immutableWest':ref(WEST),'candidate':ref(out/'candidate.png'),'field':ref(out/'field.npz'),'qa':qa,'stats':stats,'formalAccepted':False})
print(json.dumps(stats))

