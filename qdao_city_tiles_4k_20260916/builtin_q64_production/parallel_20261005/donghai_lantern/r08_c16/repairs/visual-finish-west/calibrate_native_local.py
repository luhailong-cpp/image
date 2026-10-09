from pathlib import Path
import numpy as np, json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def features(rgb):return np.concatenate([rgb/128,np.ones(rgb.shape[:-1]+(1,),np.float32)],axis=-1)
def memberships(rgb):
    signed=rgb[...,0]-rgb[...,2]
    warm=1/(1+np.exp(-np.clip((signed-8)/8,-30,30)))
    blue=1/(1+np.exp(-np.clip((-signed-8)/8,-30,30)))
    return np.stack([warm,blue,np.clip(1-warm-blue,0,1)],axis=-1)
for i in range(1,5):
    source=B/'native'/f's{i}.png';target=B/'guides'/f's{i}-actual-pair.png'
    n=np.array(Image.open(source).convert('RGB')).astype(np.float32)
    t=np.array(Image.open(target).convert('RGB')).astype(np.float32)
    centers=np.r_[np.arange(0,1254,64),1253].astype(np.float32)
    coeff=[]
    for cy in centers:
        lo=max(0,int(cy)-160);hi=min(1254,int(cy)+161)
        nn=n[lo:hi:2,420:627:2];tt=t[lo:hi:2,420:627:2]
        x=features(nn).reshape(-1,4);z=(tt-nn).reshape(-1,3)
        mu=memberships(nn).reshape(-1,3)
        yy=np.broadcast_to(np.arange(lo,hi,2)[:,None],nn.shape[:2]).reshape(-1)
        spatial=np.exp(-((yy-cy)/75)**2)
        valid=np.max(np.abs(z),axis=1)<65
        cs=[]
        for k in range(3):
            wt=mu[:,k]*valid*spatial
            c=np.zeros((4,3),np.float64)
            for _ in range(5):
                pred=x@c;err=np.sqrt(np.mean((pred-z)**2,axis=1));rw=wt*np.minimum(1,7/np.maximum(err,1e-5))
                aa=x.T@(rw[:,None]*x)+np.diag([3,3,3,.01]);c=np.linalg.solve(aa,x.T@(rw[:,None]*z))
            cs.append(c)
        coeff.append(cs)
    coeff=np.asarray(coeff);byrow=np.empty((1254,3,4,3))
    for k in range(3):
        for j in range(4):
            for ch in range(3):byrow[:,k,j,ch]=np.interp(np.arange(1254),centers,coeff[:,k,j,ch])
    allx=features(n);mu=memberships(n);delta=np.zeros_like(n,dtype=np.float64)
    for k in range(3):delta+=np.einsum('yxj,yjc->yxc',allx,byrow[:,k])*mu[...,k,None]
    delta=np.clip(delta,-24,24).astype(np.float32)
    corrected=np.clip(np.rint(n+delta),0,255).astype(np.uint8)
    p=B/'calibrated-local'/f's{i}.png';p.parent.mkdir(exist_ok=True);Image.fromarray(corrected).save(p)
    field=p.with_name(f's{i}-field.npz');np.savez_compressed(field,offset=delta,controlYs=centers,affineCoefficients=coeff)
    r={'operation':'Local robust material-affine RGB-only correction from actual immutable c15 and generated-left SAME COORDINATE pixels; 64px-spaced controls smoothly interpolated; warm/blue/neutral smooth color memberships; no image blur/warp/resampling; not an along-y blanket offset','derivedFrom':[ref(source),ref(target)],'field':ref(field),'maxAbsRGBField':float(np.max(np.abs(delta))),'trainingPairRect':[420,0,627,1254],'colorSampleOutlierRejectionAbsMax':65,'immutableC15UsedOnlyAsEvidence':True,'visualReview':'pending'}
    write(Path(str(p)+'.generation.json'),{**ref(p),**r})
    print(json.dumps({'id':i,'beforeMedian':np.median(np.abs(t[:,520:627]-n[:,520:627]),axis=(0,1)).tolist(),'afterMedian':np.median(np.abs(t[:,520:627]-corrected[:,520:627]),axis=(0,1)).tolist(),'fieldMax':r['maxAbsRGBField']}))

