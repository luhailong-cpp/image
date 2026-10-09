from pathlib import Path
from PIL import Image
from types import SimpleNamespace
import json,hashlib,datetime,sys
import numpy as np
T=Path(__file__).resolve().parent.parent;R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def bbox(a):y,x=np.where(a);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(y) else None
mode=sys.argv[1];yy,xx=np.mgrid[:1254,:1254].astype(np.float32);l=SimpleNamespace(patch=1254,halo=627)
if mode=='p11':
 D=T/'repairs/p11-north-leaves/thin-v3';out=D/'bounded';out.mkdir(exist_ok=False);src=T/'native/p11.png';context=ar(T/'repairs/p11-north-leaves/north-leaves-v1-target.png');host=D/'host-result.png';known=yy<627;owner=~known
 reg,flow,tone,stats=engine.base.register_native(context,ar(host),known,owner,['top'],l,max_shift=6.,tone_cap=18.,return_depth=256)
 alpha=sm((1024-xx)/100)*sm((1027-yy)/128);alpha[known]=0;mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8)
 proposal=Image.open(src).convert('RGB');proposal.paste(Image.fromarray(mixed).crop((0,627,1024,1027)),(115,115));name='p11-proposal.png';mapping=dict(cropLTRB=[0,627,1024,1027],pasteXY=[115,115],allowedNativeLTRB=[115,115,1139,515]);boxes=[('qa-north-join',(0,477,1024,817)),('qa-return-y400',(0,897,1024,1157)),('qa-return-x1024',(884,447,1164,1157)),('qa-left-platform',(0,457,320,957))]
else:
 D=T/'repairs/p24-water-join/east-centered-v2';out=D/'bounded';out.mkdir(exist_ok=False);src=T/'repairs/p24-water-join/host-result.png';context=ar(D/'context.png');host=D/'host-result.png';known=xx>=627;owner=~known
 reg,flow,tone,stats=engine.register_native(context,ar(host),known,owner,['right'],l,max_shift=6.,tone_cap=18.,return_depth=256)
 alpha=sm((xx-270)/128)*sm((yy-115)/80);alpha[known]=0;mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8)
 proposal=Image.open(src).convert('RGB');proposal.paste(Image.fromarray(mixed).crop((0,0,627,1254)),(512,0));proposal.paste(Image.fromarray(context).crop((627,0,742,1254)),(1139,0));name='p24-proposal.png';mapping=dict(cropLTRB=[0,0,627,1254],pasteXY=[512,0],realEastSupportRestored=True);boxes=[('qa-east-join',(467,0,787,1254)),('qa-local-return',(190,135,510,1254)),('qa-top-water',(270,0,917,350)),('qa-lower-leaves',(320,840,927,1254))]
req=read(D/'repair.request.json');assert sha(T/'plan.json')==req['plan']['sha256']
for x in req['sources']+req['references']:assert sha(x['file'])==x['sha256']
p=out/name;proposal.save(p);joint=out/'joint-frame.png';Image.fromarray(mixed).save(joint);np.save(out/'flow.npy',flow);np.save(out/'tone.npy',tone);np.save(out/'alpha.npy',alpha)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;used=alpha>0
diag=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=ref(src),host=ref(host),hostGeneration=ref(str(host)+'.generation.json'),proposal=ref(p),script=ref(__file__),mapping=mapping,registration=stats,maxAppliedFlow=float(np.linalg.norm(flow[used],axis=1).max()),maxAppliedTone=float(np.abs(tone[used]).max()),minAppliedJacobian=float(jac[used].min()),changedBBoxLTRB=bbox(np.any(np.asarray(proposal)!=ar(src),axis=2)),currentCanonicalUnchanged=True,approvedForPromotion=False)
assert diag['maxAppliedFlow']<=6.00001 and diag['maxAppliedTone']<=18 and diag['minAppliedJacobian']>=.25;write(out/'diagnostic.json',diag)
for f in [p,joint]:write(Path(str(f)+'.generation.json'),dict(**ref(f),derivedFrom=[ref(src),ref(host)],operation=ref(out/'diagnostic.json'),actualModel=None,actualQuality=None,approvedForPromotion=False))
for n,b in boxes:
 q=out/(n+'.png');Image.fromarray(mixed).crop(b).save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(joint),cropLTRB=list(b),nativeScale=1,actuallyViewed=False))
print(json.dumps({k:v for k,v in diag.items() if k!='registration'},indent=2))
