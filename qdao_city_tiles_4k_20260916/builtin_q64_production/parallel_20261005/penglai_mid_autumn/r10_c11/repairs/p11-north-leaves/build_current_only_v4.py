from pathlib import Path
from PIL import Image
from types import SimpleNamespace
import json,hashlib,datetime,sys
import numpy as np
D=Path(__file__).resolve().parent/'current-only-v4';T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
out=D/'bounded';out.mkdir(exist_ok=False);src=T/'native/p11.png';context=ar(D.parent/'north-leaves-v1-target.png');host=D/'host-result.png';yy,xx=np.mgrid[:1254,:1254].astype(np.float32);known=yy<627
req=read(D/'repair.request.json');assert sha(T/'plan.json')==req['plan']['sha256']
for z in req['sources']+req['references']:assert sha(z['file'])==z['sha256']
reg,flow,tone,stats=engine.base.register_native(context,ar(host),known,~known,['top'],SimpleNamespace(patch=1254,halo=627),max_shift=6.,tone_cap=18.,return_depth=256)
alpha=sm((1024-xx)/100)*sm((1027-yy)/128);alpha[known]=0;mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8)
proposal=Image.open(src).convert('RGB');proposal.paste(Image.fromarray(mixed).crop((0,627,1024,1027)),(115,115));p=out/'p11-proposal.png';proposal.save(p);joint=out/'joint-frame.png';Image.fromarray(mixed).save(joint)
for n,a in [('flow',flow),('tone',tone),('alpha',alpha)]:np.save(out/(n+'.npy'),a)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;used=alpha>0;changed=np.any(np.asarray(proposal)!=ar(src),axis=2);y,x=np.where(changed)
assert np.array_equal(np.asarray(proposal)[515:],ar(src)[515:]) and np.array_equal(np.asarray(proposal)[:,1139:],ar(src)[:,1139:])
diag=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=ref(src),host=ref(host),hostGeneration=ref(str(host)+'.generation.json'),proposal=ref(p),script=ref(__file__),mapping=dict(cropLTRB=[0,627,1024,1027],pasteXY=[115,115],allowedNativeLTRB=[115,115,1139,515]),registration=stats,maxAppliedFlow=float(np.linalg.norm(flow[used],axis=1).max()),maxAppliedTone=float(np.abs(tone[used]).max()),minAppliedJacobian=float(jac[used].min()),changedBBoxLTRB=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],bottomAndRightUnchanged=True,currentCanonicalUnchanged=True,approvedForPromotion=False)
assert diag['maxAppliedFlow']<=6.00001 and diag['maxAppliedTone']<=18 and diag['minAppliedJacobian']>=.25;write(out/'diagnostic.json',diag)
for f in [p,joint]:write(Path(str(f)+'.generation.json'),dict(**ref(f),derivedFrom=[ref(src),ref(host)],operation=ref(out/'diagnostic.json'),actualModel=None,actualQuality=None,approvedForPromotion=False))
for n,b in [('qa-north-join',(0,477,1024,817)),('qa-return-y400',(0,897,1024,1157)),('qa-return-x1024',(884,447,1164,1157)),('qa-left-platform',(0,457,320,957))]:
 q=out/(n+'.png');Image.fromarray(mixed).crop(b).save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(joint),cropLTRB=list(b),nativeScale=1,actuallyViewed=False))
print(json.dumps(diag))
