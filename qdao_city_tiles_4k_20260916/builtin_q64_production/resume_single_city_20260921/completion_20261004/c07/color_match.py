"""Bounded additive local tone registration of known 1024-pixel source joins.

No image generation, resizing, contour synthesis, sharpening, or texture blur.
Correction is estimated from robust flat-stone samples, recorded at full size,
and left for visual review rather than counted as an accepted game tile.
"""
from pathlib import Path
import datetime, hashlib, importlib.util, json, sys
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parent
S=R.parents[1]
sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'))
import cv2
P=S/'continuation_20261004/c07-recovery/repair-return/candidate-v4/r08_c07.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(P)=='322b8fab526479bf3eff208bc5ed7bf96296877d172187a8fbef56b731c5937c'
O=R/'tone-candidate-v1';O.mkdir(exist_ok=False)
a=np.array(Image.open(P).convert('RGB'),dtype=np.float32)
field=np.zeros_like(a)
reports=[]
radius=192

def estimate_line(b, at):
    # All channel measurements use original native-resolution pixels.
    left=np.median(b[:,at-5:at-1],axis=1)
    right=np.median(b[:,at+1:at+5],axis=1)
    gl=np.median(np.diff(b[:,at-15:at-5],axis=1),axis=1)
    gr=np.median(np.diff(b[:,at+5:at+15],axis=1),axis=1)
    jump=right-left-6*(gl+gr)/2
    texture=np.maximum(np.max(np.std(b[:,at-15:at-5],axis=1),axis=1),np.max(np.std(b[:,at+5:at+15],axis=1),axis=1))
    valid=(texture<6)&(np.max(np.abs(jump),axis=1)<24)
    ys=[];vs=[];counts=[]
    for start in range(0,4096,64):
        end=min(4096,start+64)
        local=valid[start:end]
        counts.append(int(local.sum()))
        if local.sum()>=12:
            ys.append((start+end-1)/2)
            vs.append(np.median(jump[start:end][local],axis=0))
    if len(ys)<4: raise RuntimeError('Too few flat source samples')
    smooth=np.stack([np.interp(np.arange(4096),ys,np.array(vs)[:,c]) for c in range(3)],axis=1).astype(np.float32)
    smooth=cv2.GaussianBlur(smooth,(1,0),sigmaX=0,sigmaY=32)
    smooth=np.clip(smooth,-16,16)
    return smooth,{'flatSamples':int(valid.sum()),'valid64pxGroups':len(ys),'sampleCenters':ys,'robustJumpRGB':np.array(vs).tolist(),'maxEstimatedJump':float(np.max(np.abs(smooth)))}

for axis in ('x','y'):
    b=a if axis=='x' else a.transpose(1,0,2)
    for at in (1024,2048,3072):
        jump,rep=estimate_line(b,at)
        d=np.arange(-radius,radius,dtype=np.float32)+.5
        w=np.clip(1-np.abs(d)/radius,0,1)
        w=w*w*(3-2*w)
        signed=np.where(d<0,.5,-.5)*w
        strip=jump[:,None,:]*signed[None,:,None]
        if axis=='x':field[:,at-radius:at+radius]+=strip
        else:field[at-radius:at+radius]+=strip.transpose(1,0,2)
        reports.append({'axis':axis,'at':at,**rep})

# Adjacent formal tiles retain their existing boundary pixels exactly.
yy,xx=np.mgrid[:4096,:4096]
outer=np.minimum.reduce([xx,yy,4095-xx,4095-yy]).astype(np.float32)
outer=np.clip(outer/48,0,1);outer=outer*outer*(3-2*outer)
field*=outer[:,:,None]
field=np.clip(field,-12,12)
out=np.rint(np.clip(a+field,0,255)).astype(np.uint8)
Image.fromarray(out).save(O/'r08_c07.png')
np.save(O/'tone-field.npy',field.astype(np.float16),allow_pickle=False)
assert all(np.array_equal(out.take(i,axis=ax),a.astype(np.uint8).take(i,axis=ax)) for ax in (0,1) for i in (0,4095))
record={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':{'file':str(P),'sha256':sha(P)},'candidate':{'file':str(O/'r08_c07.png'),'sha256':sha(O/'r08_c07.png'),'pixels':[4096,4096]},'operation':'bounded additive local tone registration only; no geometric resampling, resizing, texture blur, or AI generation','radiusPx':radius,'correctionLimitRGB':12,'actualMaxCorrection':float(np.abs(field).max()),'outerBoundaryPixelsUnchanged':True,'newModelCalls':0,'nativeInputsUpscaled':False,'seams':reports,'toneField':{'file':str(O/'tone-field.npy'),'sha256':sha(O/'tone-field.npy'),'storage':'float16; field applied before storage at float32'},'script':{'file':str(Path(__file__)),'sha256':sha(__file__)},'formalAccepted':False}
(O/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'r08_c07.png.generation.json').write_text(json.dumps({'derivedFrom':record['source'],'assembly':str(O/'assembly.json'),'actualModel':None,'actualQuality':None,'newGeneration':False,'newModelCalls':0,'nativeInputsUpscaled':False,'sha256':record['candidate']['sha256']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Q=O/'qa';Q.mkdir()
for axis in ('x','y'):
    for at in (1024,2048,3072):
        for seg in range(4):
            box=(at-160,seg*1024,at+160,(seg+1)*1024) if axis=='x' else (seg*1024,at-160,(seg+1)*1024,at+160)
            im=Image.fromarray(out).crop(box)
            if axis=='x':im=im.transpose(Image.Transpose.ROTATE_90)
            im.save(Q/f'{axis}{at}-seg{seg+1}.png')
for x in (1024,2048,3072):
    for y in (1024,2048,3072):Image.fromarray(out).crop((x-256,y-256,x+256,y+256)).save(Q/f'junction-{x}-{y}.png')
Image.fromarray(out).resize((1536,1536),Image.Resampling.LANCZOS).save(O/'overview-only.png')
print(json.dumps({'output':str(O),'sha256':record['candidate']['sha256'],'maxCorrection':record['actualMaxCorrection'],'groups':[s['valid64pxGroups'] for s in reports]},ensure_ascii=False))
