from pathlib import Path
from PIL import Image
from types import SimpleNamespace
import json,hashlib,sys,numpy as np
D=Path(__file__).resolve().parent/'v2-east-leaves';T=D.parents[3];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
out=D/'bounded';out.mkdir(exist_ok=False);req=read(D/'repair.request.json');plan=read(T/'plan.json');assert ref(T/'plan.json')==req['plan']
for z in req['sources']+req['references']:assert ref(z['file'])==z
src=Path(req['sources'][0]['file']);east=Path(req['sources'][2]['file']);host=D/'host-result.png';context=ar(D/'context.png');yy,xx=np.mgrid[:1254,:1254].astype(np.float32);known=(yy<627)|(xx>=627);owner=~known
reg,flow,tone,stats=engine.register_native(context,ar(host),known,owner,['right','top'],SimpleNamespace(patch=1254,halo=627),max_shift=6.,tone_cap=18.,return_depth=256)
alpha=sm((xx-340)/80)*sm((1027-yy)/96);alpha[known]=0;mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8);proposal=Image.open(src).convert('RGB');proposal.paste(Image.fromarray(mixed).crop((0,627,627,1027)),(512,115));proposal.paste(Image.open(east).convert('RGB').crop((115,115,230,515)),(1139,115));p=out/'proposal-native.png';proposal.save(p);Image.fromarray(mixed).save(out/'joint-frame.png')
for n,a in [('flow',flow),('tone',tone),('alpha',alpha)]:np.save(out/(n+'.npy'),a)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;use=alpha>0;assert np.array_equal(ar(p)[515:],ar(src)[515:]);assert np.array_equal(ar(p)[:,:230],ar(src)[:,:230])
diag=dict(script=ref(__file__),request=ref(D/'repair.request.json'),proposal=ref(p),source=ref(src),host=ref(host),east=ref(east),registration=stats,maxAppliedFlow=float(np.linalg.norm(flow[use],axis=1).max()),maxAppliedTone=float(np.abs(tone[use]).max()),minAppliedJacobian=float(jac[use].min()),left230ByteIdenticalToNorthV1=True,bottom230Unchanged=True,currentTileY400Maximum=True,canonicalUnchanged=True,approvedForPromotion=False);write(out/'diagnostic.json',diag)
assert diag['maxAppliedFlow']<=6.00001 and diag['maxAppliedTone']<=18 and diag['minAppliedJacobian']>=.25
write(Path(str(p)+'.generation.json'),dict(**ref(p),derivedFrom=[ref(src),ref(host),ref(east)],operation=ref(out/'diagnostic.json'),actualModel=None,actualQuality=None,sourceUpscaled=False,resizedAfterGeneration=False))
l=engine.Layout();neighbors={k:ar(plan[v]) for k,v in [('north','northCandidate'),('east','eastCandidate'),('northeast','northEastCandidate')]};canvas,covered,_=engine.seed_neighbors(l,neighbors);records=[]
for c,source in [(3,T/'native/p14.png'),(2,east),(1,p)]:
 x,y=l.origin(0,c);con=canvas[y:y+1254,x:x+1254].copy();kn=covered[y:y+1254,x:x+1254].copy();edges=engine.active_edges(l,0,c,'NE',neighbors);own=engine.owner_mask(kn,edges,l);merged,f,t,report=engine.register_native(con,ar(source),kn,own,edges,l,max_shift=6.,tone_cap=18.,return_depth=256);canvas[y:y+1254,x:x+1254]=merged;covered[y:y+1254,x:x+1254]=True;records.append(dict(source=ref(source),registration=report))
runtime=Image.fromarray(merged);rp=out/'actual-assembly-native-frame.png';runtime.save(rp);write(out/'actual-assembly.json',dict(script=ref(__file__),proposal=ref(p),runtime=ref(rp),patches=records))
for n,b in [('qa-east',(930,0,1254,655)),('qa-local-return',(790,115,1000,515)),('qa-bottom-return',(750,380,1254,650)),('qa-left-support',(0,0,350,650))]:
 q=out/(n+'.png');runtime.crop(b).save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(rp),cropLTRB=list(b),nativeScale=1,actuallyViewed=False))
join=Image.new('RGB',(1024,550));join.paste(Image.fromarray(neighbors['north']).crop((1024,3946,2048,4096)),(0,0));join.paste(runtime.crop((115,115,1139,515)),(0,150));q=out/'qa-north.png';join.save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(rp),north=ref(plan['northCandidate']),nativeScale=1,actuallyViewed=False));print(json.dumps(diag))
