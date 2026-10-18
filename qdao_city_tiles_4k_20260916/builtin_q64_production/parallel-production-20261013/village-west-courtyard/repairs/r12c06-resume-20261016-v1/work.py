from pathlib import Path
from PIL import Image
import json, hashlib, datetime, sys, shutil
import numpy as np
R=Path(__file__).resolve().parent
B=R.parent.parent
BASE=B/'repairs/r12c06-rock-seams-v1/context-repair-candidate-v2.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def save(p,a):
    with Path(p).open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def dp(cost):
    rows,cols=cost.shape;prev=cost[0].copy();links=np.zeros((rows,cols),np.int8)
    for r in range(1,rows):
        c=np.stack((prev,np.r_[np.inf,prev[:-1]],np.r_[prev[1:],np.inf]));q=np.argmin(c,axis=0);links[r]=np.array([0,-1,1],np.int8)[q];prev=cost[r]+np.min(c,axis=0)
    p=np.empty(rows,np.int32);p[-1]=np.argmin(prev)
    for r in range(rows-1,0,-1):p[r-1]=p[r]+links[r,p[r]]
    return p
windows=[('w08-I09',1600,2200,[280,300,850,1100]),('w09-I10',2600,2050,[115,115,1139,1254]),('w10-I13',550,3072,[115,320,1139,1254]),('w11-I14',1600,3072,[115,250,1139,1254]),('w12-I09b',500,2250,[430,400,1254,1100])]
if sys.argv[1]=='prepare':
    arr=np.asarray(Image.open(BASE).convert('RGB'))
    js(R/'checkpoint-v1.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r12_c06','base':str(BASE),'sha256':sha(BASE),'baseTraceSha256':sha(BASE.parent/'repair-assembly-trace-v2.json'),'status':'water-repair-inputs-prepared','rockQa':{'status':'passed-local-scope','issues':['I04','I05','I06','I07','I08','I11','I12'],'viewed':'five composites and 20 native border crops v2','note':'Original surrounding water seams remain failed; local repair is not whole tile acceptance.'},'remaining':['I09','I09b','I10','I13','I14','north external seam','other external seams'],'formalAccepted':False})
    for name,x,y,allow in windows:
        p=R/(name+'.input.png');save(p,arr[y:y+1254,x:x+1254]);js(R/(name+'.request.json'),{'id':name,'tile':'r12_c06','contextNativeBox':[x,y,x+1254,y+1254],'globalNativeBox':[20365+x,44941+y,21619+x,46195+y],'allowedRepairLocalBox':allow,'expectedSize':[1254,1254],'input':str(p),'inputSha256':sha(p),'baseSha256':sha(BASE),'route':'builtin-image_gen','actualModel':'not returned','status':'prepared-not-submitted','formalAccepted':False})
elif sys.argv[1]=='archive':
    name=sys.argv[2];src=Path(sys.argv[3]);dst=R/(name+'.generated-v1.png');assert not dst.exists();shutil.copy2(src,dst);assert Image.open(dst).size==(1254,1254)
    js(R/(name+'.receipt-v1.json'),{'id':name,'source':str(src),'saved':str(dst),'sha256':sha(dst),'size':[1254,1254],'route':'builtin-image_gen','actualModel':'not returned','operation':'unaltered copy','time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False})
elif sys.argv[1]=='compose':
    ver=sys.argv[2];out=R/('assembly-'+ver);out.mkdir(exist_ok=False);base=np.asarray(Image.open(BASE).convert('RGB'));cand=base.copy();ids=np.zeros(base.shape[:2],np.uint8);records=[]
    for sid,(name,x,y,allow) in enumerate(windows,1):
        path=R/(name+'.generated-v1.png')
        if not path.exists():continue
        gen=np.asarray(Image.open(path).convert('RGB'));old=base[y:y+1254,x:x+1254];l,t,r,b=allow;cost=np.mean((gen.astype(float)-old.astype(float))**2,axis=2)[t:b,l:r];h,w=cost.shape;band=50
        left=dp(cost[:,:band]);right=w-band+dp(cost[:,-band:]);top=dp(cost[:band,:].T);bottom=h-band+dp(cost[-band:,:].T);yy,xx=np.indices((h,w));inside=(xx>=left[:,None])&(xx<=right[:,None])&(yy>=top[None,:])&(yy<=bottom[None,:]);mask=np.zeros((1254,1254),bool);mask[t:b,l:r]=inside
        if b==1254 and y+1254==base.shape[0]:
            inside=(xx>=left[:,None])&(xx<=right[:,None])&(yy>=top[None,:]);mask[t:b,l:r]=inside
        assert not np.any(ids[y:y+1254,x:x+1254][mask]);cand[y:y+1254,x:x+1254][mask]=gen[mask];ids[y:y+1254,x:x+1254][mask]=sid
        comp=old.copy();comp[mask]=gen[mask];save(out/(name+'.composite.png'),comp);save(out/(name+'.mask.png'),(mask*255).astype(np.uint8))
        crops=[]
        for side,box in [('top',[l-80,t-80,r+80,t+band+80]),('bottom',[l-80,b-band-80,r+80,b+80]),('left',[l-80,t-80,l+band+80,b+80]),('right',[r-band-80,t-80,r+80,b+80])]:
            box=[max(0,box[0]),max(0,box[1]),min(1254,box[2]),min(1254,box[3])];p=out/(name+'.'+side+'.png');save(p,comp[box[1]:box[3],box[0]:box[2]]);crops.append({'path':p.name,'box':box,'sha256':sha(p),'scale':1})
        records.append({'sourceId':sid,'id':name,'source':str(path),'sha256':sha(path),'contextNativeBox':[x,y,x+1254,y+1254],'allowedBox':allow,'mask':name+'.mask.png','maskSha256':sha(out/(name+'.mask.png')),'selectedPixels':int(mask.sum()),'qa':crops})
    save(out/'context-native.png',cand);save(out/'r12_c06.candidate.png',cand[115:4211,115:4211]);save(out/'source-id.png',ids)
    replay=base.copy()
    for r in records:
        x,y,_,_=r['contextNativeBox'];m=ids[y:y+1254,x:x+1254]==r['sourceId'];g=np.asarray(Image.open(r['source']).convert('RGB'));replay[y:y+1254,x:x+1254][m]=g[m]
    js(out/'assembly.json',{'tile':'r12_c06','formalAccepted':False,'base':str(BASE),'baseSha256':sha(BASE),'contextSha256':sha(out/'context-native.png'),'tileSha256':sha(out/'r12_c06.candidate.png'),'sourceMapSha256':sha(out/'source-id.png'),'repairs':records,'proof':{'mismatches':int(np.any(replay!=cand,axis=2).sum()),'outsideSelectionChanges':int(np.any(base[ids==0]!=cand[ids==0],axis=1).sum())},'operation':'integer crop and binary native source selection only; no resampling, blend, blur or pixel painting','actualModel':'not returned','route':'builtin-image_gen','status':'pending-visual-QA'})
    print(out)
