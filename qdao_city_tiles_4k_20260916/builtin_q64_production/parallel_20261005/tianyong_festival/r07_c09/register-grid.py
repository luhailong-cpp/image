from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
Ndir=Path(__file__).parent;D=Ndir/sys.argv[1];F=D/(sys.argv[2] if len(sys.argv)>2 else 'final-v2');F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
c=read(D/'registration-input.json');p=read(D/'preparation.json');kx=p['knownStartX'];ky=p.get('knownStartY',1139)
sx=kx+(16 if kx<=1024 else 0);ex=min(kx+176,1200);sy=ky+(16 if ky<=1024 else 0);ey=min(ky+176,1200)
N=np.array(Image.open(D/c['native']).convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
Y,X=np.indices((1254,1254),dtype=float);smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
right={int(k):v for k,v in c['right'].items()};bottom={int(k):v for k,v in c['bottom'].items()}
ry=[]
for xx,pairs in right.items():
 a=np.array(pairs);ry.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
ry=np.array(ry);l,r=c['rightFadeX'];dy=np.stack([np.interp(np.arange(1254),list(right),ry[:,yy]) for yy in range(1254)])*smooth((X-l)/(r-l))
bx=[]
for yy,pairs in bottom.items():
 a=np.array(pairs);bx.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
bx=np.array(bx);l,r=c['bottomFadeY'];dx=np.stack([np.interp(np.arange(1254),list(bottom),bx[:,xx]) for xx in range(1254)],axis=1)*smooth((Y-l)/(r-l))
assert abs(dx).max()<=c['allowedMaxDx'] and abs(dy).max()<=c['allowedMaxDy']
R=cv2.remap(N,(X+dx).astype('float32'),(Y+dy).astype('float32'),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
w=np.where(C[:,:,3]==255,np.maximum(smooth((X-sx)/(ex-sx)),smooth((Y-sy)/(ey-sy))),0)
J=np.rint(R*(1-w[:,:,None])+C[:,:,:3]*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
np.savez_compressed(F/'registration-fields.npz',inverseDx=dx.astype('float32'),inverseDy=dy.astype('float32'))
save(F/'registration-controls.json',dict(c,method='Manually assigned same physical signed grayscale gradient peaks after actual AI redraw; no optical flow',diagnosticSource=ref(D/'final-v1/profile-peaks.json')))
for name,box in [('full',[0,0,1254,1254]),('right',[kx-64,0,min(1254,kx+246),1254]),('bottom',[0,ky-129,1254,1254]),('corner',[kx-64,ky-129,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(D/c['native']),'context':ref(D/'context.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':True,'actualMaxAbsDx':float(abs(dx).max()),'actualMaxAbsDy':float(abs(dy).max()),'interpolation':'OpenCV INTER_CUBIC inverse map BORDER_REPLICATE','fields':ref(F/'registration-fields.npz'),'controls':ref(F/'registration-controls.json'),'sourceWeight':ref(F/'source-weight.png'),'blendSmoothstepX':[sx,ex],'blendSmoothstepY':[sy,ey],'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'knownBeyondBlendExact':bool(np.array_equal(J[(C[:,:,3]==255)&((X>=ex)|(Y>=ey))],C[:,:,:3][(C[:,:,3]==255)&((X>=ex)|(Y>=ey))])),'formalAccepted':False,'visualReviewPending':True})
print(json.dumps({'joined':ref(F/'joined.png'),'maxDx':float(abs(dx).max()),'maxDy':float(abs(dy).max())}))
