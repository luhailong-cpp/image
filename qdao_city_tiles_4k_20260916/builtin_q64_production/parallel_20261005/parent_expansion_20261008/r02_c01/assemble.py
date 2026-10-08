from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=np.array(Image.open(R/'context.png').convert('RGBA'))
n=np.array(Image.open(R/'return-repair/native.png').convert('RGB'))
old=c[:,:,:3];opaque=c[:,:,3]==255
assert n.shape==(1254,1254,3)
cost=np.mean(np.abs(n.astype(float)-old.astype(float)),axis=2)
for axis in [0,1]:
    cost+=0.8*np.mean(np.abs(np.gradient(n.astype(float),axis=axis)-np.gradient(old.astype(float),axis=axis)),axis=2)
def horizontal_path(cost,lo,hi):
    b=cost[lo:hi].T
    w,h=b.shape;dp=b[0].copy();back=np.zeros((w,h),np.int16)
    for x in range(1,w):
        opts=np.full((5,h),np.inf)
        for k,step in enumerate([-2,-1,0,1,2]):
            if step>=0:opts[k,step:]=dp[:h-step]+abs(step)*0.6
            else:opts[k,:step]=dp[-step:]+abs(step)*0.6
        ids=opts.argmin(axis=0);dp=b[x]+opts[ids,np.arange(h)];back[x]=np.arange(h)-np.array([-2,-1,0,1,2])[ids]
    y=int(dp.argmin());path=np.empty(w,np.int32)
    for x in range(w-1,-1,-1):path[x]=y+lo;y=int(back[x,y]) if x else y
    return path
top=horizontal_path(cost,32,211)
bottom=horizontal_path(cost,1040,1223)
left=horizontal_path(cost.T,24,97)
yy,xx=np.indices((1254,1254));mask=(yy>=top[xx])&(yy<bottom[xx])&(xx>=left[yy])
assert mask[~opaque].all()
joined=old.copy();joined[mask]=n[mask]
out=R/'joined.png';Image.fromarray(joined).save(out)
Image.fromarray(mask.astype(np.uint8)*255).save(R/'join-mask.png')
np.savez_compressed(R/'seam-paths.npz',top=top,bottom=bottom,left=left)
Q=R/'qa';Q.mkdir(exist_ok=True)
qa=[]
for name,box in [('north-return',(0,0,1254,440)),('south-return',(0,850,1254,1254)),('west-return',(0,0,420,1254)),('east-return',(850,0,1254,1254)),('northwest-corner',(0,0,440,440)),('southwest-corner',(0,850,440,1254))]:
    p=Q/(name+'.png');Image.fromarray(joined).crop(box).save(p);qa.append(dict(**ref(p),cropLTRB=box,nativeScale=1,actuallyViewed=False))
now=datetime.now(timezone.utc).isoformat()
proof={'allTransparentPixelsFilled':bool(mask[~opaque].all()),'newNativeMissingPixels':int((~opaque).sum()),'newPixelsInC10':int((~opaque[:,115:]).sum()),'opaqueContextPixelsChanged':int(np.any(joined!=old,axis=2)[opaque].sum()),'opaquePixelsOutsideMaskExactlyPreserved':bool(np.array_equal(joined[opaque&~mask],old[opaque&~mask])),'sourceCopyExact':bool(np.array_equal(joined[mask],n[mask])),'nativePixelScale':1,'resampling':False,'registration':False,'blur':False,'colorCorrection':False,'maskFeather':False,'topSeamRange':[int(top.min()),int(top.max())],'bottomSeamRange':[int(bottom.min()),int(bottom.max())],'leftSeamRange':[int(left.min()),int(left.max())],'proofIsNotVisualAcceptance':True}
manifest={'createdAt':now,'patch':'r02_c01','tile':'r08_c10','windowTileLocalLTRB':[-115,909,1139,2163],'file':str(out),'sha256':sha(out),'pixels':[1254,1254],'context':ref(R/'context.png'),'nativeSource':ref(R/'return-repair/native.png'),'originalNativeSource':ref(R/'native.png'),'generationRecord':str(R/'return-repair/native.png.generation.json'),'sourceSelection':json.loads((R/'request.json').read_text(encoding='utf-8'))['sourceSelection'],'joinMask':ref(R/'join-mask.png'),'seamPaths':ref(R/'seam-paths.npz'),'proof':proof,'qa':qa,'status':'assembled_pending_native_return_visual_review','formalAccepted':False,'wholeCityComplete':False,'scope':'Native 1:1 cut paths within existing left/top/bottom overlap, after focused AI return correction. No edit outside this patch directory.'}
dump(R/'manifest.json',manifest)
dump(R/'joined.png.generation.json',{'file':str(out),'sha256':sha(out),'createdAt':now,'width':1254,'height':1254,'format':'PNG','derivedFrom':[ref(R/'context.png'),ref(R/'native.png'),ref(R/'return-repair/native.png')],'operation':'native-pixel binary min-cost seam ownership only; no resampling, warping, color correction or blur','manifest':ref(R/'manifest.json'),'formalAccepted':False})
dump(R/'join-mask.png.generation.json',{'file':str(R/'join-mask.png'),'sha256':sha(R/'join-mask.png'),'createdAt':now,'derivedFrom':[ref(R/'context.png'),ref(R/'return-repair/native.png')],'operation':'technical binary source ownership, not painted content'})
print(json.dumps({'joined':str(out),'sha256':sha(out),'proof':proof},ensure_ascii=True))
