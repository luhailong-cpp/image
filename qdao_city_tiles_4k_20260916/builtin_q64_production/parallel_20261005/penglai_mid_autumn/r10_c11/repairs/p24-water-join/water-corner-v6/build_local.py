from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
cv=engine.base.cv_module();O=D/'bounded';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
req=read(D/'repair.request.json');assert sha(T/'plan.json')==req['plan']['sha256']
for src in req['sources']+req['references']:assert sha(src['file'])==src['sha256']
base=Path(req['sources'][0]['file']);north=Path(req['sources'][1]['file']);east=Path(req['sources'][2]['file']);host=D/'host-result.png'
b=ar(base);h=ar(host);n=ar(north);e=ar(east);patch=b.copy();patch[:742]=h[512:]
c=np.zeros_like(patch);known=np.zeros((1254,1254),bool);c[:230]=n[1024:];known[:230]=True;c[:,1139:]=e[909:2163,:115];known[:,1139:]=True
layout=engine.base.Layout();owner=engine.owner_mask(known,['top','right'],layout);reg,flow,tone,stats=engine.register_native(c,patch,known,owner,['top','right'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# Native coordinates: only AI-painted small L corridor plus a25px selection return.
a1=sm((xx-825)/25)*sm((373-yy)/25);a2=sm((xx-825)/25)*sm((1095-xx)/25)*sm((523-yy)/25)
alpha=np.maximum(a1,a2);alpha[known]=0
result=np.clip(np.rint(b*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype('uint8');result[known]=c[known]
out=O/'p24-proposal.png';Image.fromarray(result).save(out);np.save(O/'flow.npy',flow);np.save(O/'tone.npy',tone);np.save(O/'selection.npy',alpha)
ys,xs=np.where(np.any(result!=b,axis=2));bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
diag=dict(proposal=ref(out),sources=[ref(base),ref(host),ref(north),ref(east)],script=ref(__file__),registration=stats,selection=dict(nativeFullUnionLTRB=[[850,230,1139,348],[850,348,1070,498]],returnPixels=25,knownSupportExact=True),actualChangedBBoxLTRB=bbox,sourceUpscaled=False,resizedAfterGeneration=False,canonicalUnchanged=True,approvedForPromotion=False)
write(O/'diagnostic.json',diag);write(str(out)+'.generation.json',dict(**ref(out),derivedFrom=[ref(base),ref(host),ref(north),ref(east)],hostGeneration=ref(str(host)+'.generation.json'),operation=ref(O/'diagnostic.json'),configSnapshot=req['configSnapshot'],actualModel=None,actualQuality=None,globalPatchXYWH=[43917,37773,1254,1254],sourceUpscaled=False,resizedAfterGeneration=False,approvedForPromotion=False))
print(json.dumps(dict(proposal=ref(out),changedBBox=bbox,registration=stats),indent=2))
