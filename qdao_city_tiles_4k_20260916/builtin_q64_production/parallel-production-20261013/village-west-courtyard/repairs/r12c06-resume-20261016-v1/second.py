from pathlib import Path
from PIL import Image
import json, hashlib, datetime
import numpy as np
R=Path(__file__).resolve().parent
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
basepath=R/'assembly-v2/context-native.png';base=np.asarray(Image.open(basepath).convert('RGB'));candidate=base.copy();ids=np.zeros(base.shape[:2],np.uint8);out=R/'assembly-v3';out.mkdir(exist_ok=False);records=[]
specs=[('w09-I10-second',2600,2050,[[50,400,330,1254],[950,600,1245,1150]]),('w10-I13-second',550,3072,[[960,430,1245,1140]])]
for sid,(name,x,y,boxes) in enumerate(specs,1):
    sp=R/(name+'.generated-v1.png');gen=np.asarray(Image.open(sp).convert('RGB'));old=base[y:y+1254,x:x+1254];cost=np.mean((gen.astype(float)-old.astype(float))**2,axis=2);mask=np.zeros((1254,1254),bool)
    for l,t,r,b in boxes:
        c=cost[t:b,l:r];h,w=c.shape;band=35;left=dp(c[:,:band]);right=w-band+dp(c[:,-band:]);top=dp(c[:band,:].T);bottom=h-band+dp(c[-band:,:].T);yy,xx=np.indices(c.shape);mask[t:b,l:r]|=(xx>=left[:,None])&(xx<=right[:,None])&(yy>=top[None,:])&(yy<=bottom[None,:])
    candidate[y:y+1254,x:x+1254][mask]=gen[mask];ids[y:y+1254,x:x+1254][mask]=sid;comp=old.copy();comp[mask]=gen[mask];save(out/(name+'.composite.png'),comp);save(out/(name+'.mask.png'),(mask*255).astype(np.uint8))
    crops=[]
    for n,(l,t,r,b) in enumerate(boxes):
        box=[max(0,l-60),max(0,t-60),min(1254,r+60),min(1254,b+60)];p=out/(name+f'.region-{n}.png');save(p,comp[box[1]:box[3],box[0]:box[2]]);crops.append({'path':p.name,'box':box,'sha256':sha(p),'scale':1})
    records.append({'id':name,'sourceId':sid,'source':str(sp),'sha256':sha(sp),'contextNativeBox':[x,y,x+1254,y+1254],'allowedBoxes':boxes,'mask':name+'.mask.png','maskSha256':sha(out/(name+'.mask.png')),'qa':crops})
save(out/'context-native.png',candidate);save(out/'r12_c06.candidate.png',candidate[115:4211,115:4211]);save(out/'source-id.png',ids);replay=base.copy()
for r in records:
    x,y,_,_=r['contextNativeBox'];m=ids[y:y+1254,x:x+1254]==r['sourceId'];g=np.asarray(Image.open(r['source']).convert('RGB'));replay[y:y+1254,x:x+1254][m]=g[m]
j={'tile':'r12_c06','formalAccepted':False,'base':str(basepath),'baseSha256':sha(basepath),'baseAssemblySha256':sha(R/'assembly-v2/assembly.json'),'contextSha256':sha(out/'context-native.png'),'tileSha256':sha(out/'r12_c06.candidate.png'),'sourceMapSha256':sha(out/'source-id.png'),'repairs':records,'proof':{'mismatches':int(np.any(replay!=candidate,axis=2).sum()),'outsideSelectionChanges':int(np.any(base[ids==0]!=candidate[ids==0],axis=1).sum())},'operation':'binary native source selection, no resample, blend, blur or paint','actualModel':'not returned','route':'builtin-image_gen','status':'pending-visual-QA','scriptSha256':sha(__file__)}
with (out/'assembly.json').open('x',encoding='utf-8') as f:json.dump(j,f,indent=2)
print(json.dumps({'path':str(out),'sha256':j['tileSha256'],'proof':j['proof']}))
