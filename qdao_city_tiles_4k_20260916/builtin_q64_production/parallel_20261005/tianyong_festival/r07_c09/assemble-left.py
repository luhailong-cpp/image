from pathlib import Path
import numpy as np,json,hashlib,sys
from PIL import Image
D=Path(__file__).parent/sys.argv[1];F=D/(sys.argv[3] if len(sys.argv)>3 else 'final-v1');F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
p=read(D/'preparation.json');k=p['knownStartX'];ky=p.get('knownStartY',1139);sx=k+(16 if k<=1024 else 0);ex=min(k+176,1200);sy=ky+(16 if ky<=1024 else 0);ey=min(ky+176,1200);native=D/(sys.argv[2] if len(sys.argv)>2 else 'native.png')
N=np.array(Image.open(native).convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
x,y=np.meshgrid(np.arange(1254),np.arange(1254));smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
w=np.where(C[:,:,3]==255,np.maximum(smooth((x-sx)/(ex-sx)),smooth((y-sy)/(ey-sy))),0)
J=np.rint(N*(1-w[:,:,None])+C[:,:,:3]*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('right',[k-64,0,min(k+246,1254),1254]),('bottom',[0,ky-129,1254,1254]),('corner',[k-64,ky-129,1254,1254]),('full',[0,0,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
def peaks(v,lo=0,hi=1254):
 v=np.convolve(v,np.ones(7)/7,mode='same');a=np.gradient(v);ki=[i for i in range(max(lo,5),min(hi,1249)) if abs(a[i])>1 and abs(a[i])==max(abs(a[i-5:i+6]))]
 return [[i,round(float(a[i]),2)] for i in ki]
rec={'right':{},'bottom':{}}
for xx in sorted(set([min(k+16,ex),min(k+66,ex),min(k+116,ex),ex])):
 rec['right'][xx]={label:peaks(A[:,xx-5:xx+6,:3].mean(axis=(1,2)),15,1130) for label,A in [('context',C),('native',N)]}
for yy in sorted(set([ky+6,min(ky+56,ey),min(ky+116,ey),min(ey+20,1240)])):
 rec['bottom'][yy]={label:peaks(A[yy-3:yy+4,:,:3].mean(axis=(0,2)),5,1248) for label,A in [('context',C),('native',N)]}
save(F/'profile-peaks.json',rec)
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(native),'context':ref(D/'context.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'sourceWeight':ref(F/'source-weight.png'),'blendSmoothstepX':[sx,ex],'blendSmoothstepY':[sy,ey],'unknownPixelsUnchangedFromNative':bool(np.array_equal(J[C[:,:,3]==0],N[C[:,:,3]==0])),'knownBeyondBlendExact':bool(np.array_equal(J[(C[:,:,3]==255)&((x>=ex)|(y>=ey))],C[:,:,:3][(C[:,:,3]==255)&((x>=ex)|(y>=ey))])),'formalAccepted':False,'visualReviewPending':True})
print(json.dumps(rec))
