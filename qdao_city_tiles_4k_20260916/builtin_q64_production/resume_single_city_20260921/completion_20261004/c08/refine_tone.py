from pathlib import Path
import numpy as np,json,sys,hashlib,datetime
from PIL import Image
R=Path(__file__).resolve().parent;S=R.parents[1];sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'));import cv2
P=R/'geometry-candidate-v1/r08_c08.png';O=R/'tone-candidate-v2';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(P)=='f70bf0b4731a1a4a679f440023b9c297a819724a6e7aac354e7a6bb80c89cb95'
a=np.array(Image.open(P).convert('RGB'),dtype=np.float32);field=np.zeros_like(a);reports=[]
def est(b,k):
    l=np.median(b[:,k-5:k-1],axis=1);r=np.median(b[:,k+1:k+5],axis=1)
    sl=np.median(np.diff(b[:,k-15:k-5],axis=1),axis=1);sr=np.median(np.diff(b[:,k+5:k+15],axis=1),axis=1)
    j=r-l-6*(sl+sr)/2
    texture=np.maximum(np.max(np.std(b[:,k-15:k-5],axis=1),axis=1),np.max(np.std(b[:,k+5:k+15],axis=1),axis=1))
    valid=(texture<6)&(np.max(np.abs(j),axis=1)<20);idx=np.flatnonzero(valid)
    assert len(idx)>100
    values=np.stack([np.interp(np.arange(4096),idx,j[idx,c]) for c in range(3)],axis=1).astype(np.float32)
    values=cv2.medianBlur(values.reshape(4096,1,3),5).reshape(4096,3)
    values=cv2.GaussianBlur(values,(1,0),sigmaX=0,sigmaY=5)
    return np.clip(values,-16,16),int(valid.sum())
radius=192
for axis in ('x','y'):
 for k in (1024,2048,3072):
    b=a if axis=='x' else a.transpose(1,0,2);jump,count=est(b,k)
    d=np.arange(-radius,radius,dtype=np.float32)+.5;w=np.clip(1-np.abs(d)/radius,0,1);w=w*w*(3-2*w);signed=np.where(d<0,.5,-.5)*w
    strip=jump[:,None,:]*signed[None,:,None]
    if axis=='x':field[:,k-radius:k+radius]+=strip
    else:field[k-radius:k+radius]+=strip.transpose(1,0,2)
    reports.append({'axis':axis,'at':k,'validNativeSampleCount':count,'maxEstimatedJump':float(np.abs(jump).max())})
y,x=np.mgrid[:4096,:4096];edge=np.minimum.reduce([x,y,4095-x,4095-y]);fade=np.clip(edge/2,0,1);fade=fade*fade*(3-2*fade);field*=fade[:,:,None];field=np.clip(field,-12,12);out=np.rint(np.clip(a+field,0,255)).astype(np.uint8)
Image.fromarray(out).save(O/'r08_c08.png');np.save(O/'tone-field.npy',field.astype(np.float16))
assert all(np.array_equal(out.take(i,axis=ax),a.astype(np.uint8).take(i,axis=ax)) for ax in (0,1) for i in (0,4095))
rec={'candidate':{'file':str(O/'r08_c08.png'),'sha256':sha(O/'r08_c08.png'),'pixels':[4096,4096]},'derivedFrom':{'file':str(P),'sha256':sha(P)},'operation':'Bounded additive tone registration from native samples. Fine valid sample interpolation and 5px smoothing applied to correction estimate only; native artwork never blurred/resized/warped.','radiusPx':192,'maxCorrectionAllowed':12,'actualMaxCorrection':float(np.abs(field).max()),'outerEdgeUnchanged':True,'outerFadePx':2,'seams':reports,'field':{'file':str(O/'tone-field.npy'),'sha256':sha(O/'tone-field.npy')},'formalAccepted':False}
(O/'assembly.json').write_text(json.dumps(rec,indent=2));Image.fromarray(out).resize((1536,1536),Image.Resampling.LANCZOS).save(O/'overview-only.png')
Q=O/'qa';Q.mkdir(exist_ok=True)
for axis in ('x','y'):
 for k in (1024,2048,3072):
    board=Image.new('RGB',(1024,1280))
    for seg in range(4):
      box=(k-160,seg*1024,k+160,(seg+1)*1024) if axis=='x' else (seg*1024,k-160,(seg+1)*1024,k+160)
      im=Image.fromarray(out).crop(box)
      if axis=='x':im=im.transpose(Image.Transpose.ROTATE_90)
      im.save(Q/f'{axis}{k}-seg{seg+1}.png');board.paste(im,(0,seg*320))
    board.save(Q/f'{axis}{k}-board.png')
print(json.dumps(rec['candidate']))

