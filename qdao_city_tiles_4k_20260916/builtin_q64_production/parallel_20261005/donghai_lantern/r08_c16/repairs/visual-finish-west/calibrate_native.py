from pathlib import Path
import numpy as np, json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def features(rgb):return np.concatenate([rgb/128,np.ones(rgb.shape[:-1]+(1,),np.float32)],axis=-1)
def memberships(rgb):
    # Smooth hue membership rather than fragmented hard pixel classifications.
    signed=rgb[...,0]-rgb[...,2]
    warm=1/(1+np.exp(-np.clip((signed-8)/8,-30,30)))
    blue=1/(1+np.exp(-np.clip((-signed-8)/8,-30,30)))
    neutral=np.clip(1-warm-blue,0,1)
    return np.stack([warm,blue,neutral],axis=-1)
for i in range(1,5):
    source=B/'native'/f's{i}.png';target=B/'guides'/f's{i}-actual-pair.png'
    n=np.array(Image.open(source).convert('RGB')).astype(np.float32)
    t=np.array(Image.open(target).convert('RGB')).astype(np.float32)
    # Actual c15 SAME COORDINATE input pixels are the evidence. No DAY RGB transfer.
    train_n=n[::2,300:627:2];train_t=t[::2,300:627:2]
    x=features(train_n).reshape(-1,4);z=(train_t-train_n).reshape(-1,3)
    m=memberships(train_n).reshape(-1,3)
    valid=np.max(np.abs(z),axis=1)<75
    coeff=[]
    for k in range(3):
        wt=m[:,k]*valid
        c=np.zeros((4,3),np.float64)
        for _ in range(4):
            pred=x@c;err=np.sqrt(np.mean((pred-z)**2,axis=1))
            rw=wt*np.minimum(1,10/np.maximum(err,1e-5))
            a=x.T@(rw[:,None]*x)+np.diag([10,10,10,.01])
            c=np.linalg.solve(a,x.T@(rw[:,None]*z))
        coeff.append(c)
    allx=features(n);mu=memberships(n);delta=np.zeros_like(n,dtype=np.float64)
    for k,c in enumerate(coeff):delta+=(allx@c)*mu[...,k,None]
    delta=np.clip(delta,-24,24).astype(np.float32)
    corrected=np.clip(np.rint(n+delta),0,255).astype(np.uint8)
    p=B/'calibrated'/f's{i}.png';p.parent.mkdir(exist_ok=True)
    Image.fromarray(corrected).save(p)
    field=B/'calibrated'/f's{i}-field.npz';np.savez_compressed(field,offset=delta,affineCoefficients=np.stack(coeff))
    difference_before=np.abs(train_t-train_n)
    difference_after=np.abs(t[::2,300:627:2]-corrected[::2,300:627:2])
    r={'operation':'RGB color-only correction from identical-coordinate immutable c15 pixels versus generated-left pixels; robust material-weighted affine color map; smooth hue memberships; NO image blur/warp/resampling','derivedFrom':[ref(source),ref(target)],'field':ref(field),'maxAbsRGBField':float(np.max(np.abs(delta))),'actualFieldReturnedModel':None,'beforeMedianAbsRGB':np.median(difference_before,axis=(0,1)).tolist(),'afterMedianAbsRGB':np.median(difference_after,axis=(0,1)).tolist(),'trainingPairRect':[300,0,627,1254],'immutableC15UsedOnlyAsEvidence':True,'visualReview':'pending'}
    write(Path(str(p)+'.generation.json'),{**ref(p),**r})
    print(json.dumps({'id':i,'before':r['beforeMedianAbsRGB'],'after':r['afterMedianAbsRGB'],'fieldMax':r['maxAbsRGBField']}))

