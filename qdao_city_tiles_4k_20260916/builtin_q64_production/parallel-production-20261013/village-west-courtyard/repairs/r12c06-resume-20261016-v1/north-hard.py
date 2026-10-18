from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;B=R.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,a):
    with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def dp(cost):
    rows,cols=cost.shape;prev=cost[0].copy();links=np.zeros((rows,cols),np.int8)
    for r in range(1,rows):
        c=np.stack((prev,np.r_[np.inf,prev[:-1]],np.r_[prev[1:],np.inf]));q=np.argmin(c,axis=0);links[r]=np.array([0,-1,1],np.int8)[q];prev=cost[r]+np.min(c,axis=0)
    p=np.empty(rows,np.int32);p[-1]=np.argmin(prev)
    for r in range(rows-1,0,-1):p[r-1]=p[r]+links[r,p[r]]
    return p
out=R/'north-hard-v1';out.mkdir(exist_ok=False);basepath=R/'assembly-v2/context-native.png';base=np.asarray(Image.open(basepath).convert('RGB'));j=json.loads((B/'qa/r12-c06-complete-native-v1/assembly.json').read_text());s=next(x for x in j['sourceLegend'] if x['sourceId']==65535);source=Path(s['path']);assert sha(source)==s['sha256'];up=np.asarray(Image.open(source).convert('RGB'))[4096:4326];assert np.array_equal(base[:115],up[:115]);candidate=base.copy();diff=np.mean((up[115:230].astype(float)-base[115:230].astype(float))**2,axis=2);path=115+dp(diff.T);yy=np.arange(230)[:,None];take=yy<=path[None,:];candidate[:230][take]=up[take];save(out/'context-native.png',candidate);save(out/'r12_c06.candidate.png',candidate[115:4211,115:4211]);save(out/'north-source-mask.png',(take*255).astype(np.uint8))
for i,x in enumerate([0,1024,2048,3072],1):save(out/f'north-c{i}.qa.png',candidate[:345,x:x+1254])
proof={'north115Unchanged':bool(np.array_equal(base[:115],candidate[:115])),'outsideOverlapUnchanged':bool(np.array_equal(base[230:],candidate[230:])),'sourceMismatch':int(np.any(candidate[:230][take]!=up[take],axis=1).sum())}
rec={'tile':'r12_c06','formalAccepted':False,'base':str(basepath),'baseSha256':sha(basepath),'upstreamSource':s,'contextSha256':sha(out/'context-native.png'),'tileSha256':sha(out/'r12_c06.candidate.png'),'path':path.tolist(),'proof':proof,'operation':'binary hard source selection from existing exact native overlap; no AI generation, blending, resizing or painting','status':'pending-visual-QA'}
with (out/'assembly.json').open('x',encoding='utf-8') as f:json.dump(rec,f,indent=2)
print(proof)
