from pathlib import Path
from PIL import Image
import sys,json,hashlib,datetime,numpy as np
T=Path(__file__).resolve().parent.parent;R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
col=int(sys.argv[1]);D=T/'repairs/row1-north'/f'p1{col}'/sys.argv[2];out=D/'bounded-native';out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
req=read(D/'repair.request.json');plan=read(T/'plan.json');assert sha(T/'plan.json')==req['plan']['sha256']
for z in req['sources']+req['references']:assert sha(z['file'])==z['sha256']
src=Path(req['sources'][1]['file']);east=Path(req['sources'][4]['file']);host=D/'host-result.png';layout=engine.Layout();neighbors={'north':ar(plan['northCandidate']),'east':ar(plan['eastCandidate']),'northeast':ar(plan['northEastCandidate'])}
images={**neighbors,f'p1{col+1}':ar(east)};ops=engine.context_operations(layout,0,col-1,'NE',neighbors);context,known=engine.materialize_context(layout,ops,images);edges=['right','top'];owner=engine.owner_mask(known,edges,layout)
unregistered=Image.open(src).convert('RGB');unregistered.paste(Image.open(host).convert('RGB').crop((0,512,1254,1254)),(0,0));unregistered.save(out/'unregistered-native.png')
reg,flow,tone,stats=engine.register_native(context,np.asarray(unregistered),known,owner,edges,layout,max_shift=6.,tone_cap=18.,return_depth=256)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32);alpha=sm((515-yy)/128);alpha[~owner]=0;alpha[yy<115]=0
original=ar(src);proposal=np.clip(np.rint(original*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8)
support_restore=known&(~owner)&(yy<515);proposal[support_restore]=context[support_restore]
assert np.array_equal(proposal[515:],original[515:])
p=out/'proposal-native.png';Image.fromarray(proposal).save(p)
for n,a in [('flow',flow),('tone',tone),('alpha',alpha)]:np.save(out/(n+'.npy'),a)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;used=alpha>0
diag=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),script=ref(__file__),request=ref(D/'repair.request.json'),proposal=ref(p),sources=[ref(src),ref(host),ref(east),ref(plan['northCandidate'])],nativePaste=dict(hostCropLTRB=[0,512,1254,1254],pasteXY=[0,0]),coreRepairNativeY=[115,515],exactKnownHaloRestoredBeforeSecondRegistration=True,registration=stats,maxAppliedFlow=float(np.linalg.norm(flow[used],axis=1).max()),maxAppliedTone=float(np.abs(tone[used]).max()),minAppliedJacobian=float(jac[used].min()),bottom230Unchanged=True,allNativeRows515OnwardUnchanged=True,canonicalUnchanged=True,approvedForPromotion=False)
assert diag['maxAppliedFlow']<=6.00001 and diag['maxAppliedTone']<=18 and diag['minAppliedJacobian']>=.25
write(out/'diagnostic.json',diag)
for f in [p,out/'unregistered-native.png']:write(Path(str(f)+'.generation.json'),dict(**ref(f),derivedFrom=diag['sources'],operation=ref(out/'diagnostic.json'),actualModel=None,actualQuality=None,sourceUpscaled=False,resizedAfterGeneration=False,approvedForPromotion=False))
canvas,covered,_=engine.seed_neighbors(layout,neighbors);runtime_reports=[]
for c in range(3,col-2,-1):
 source=p if c==col-1 else (east if c==col else T/'native'/f'p1{c+1}.png');patch=ar(source);x,y=layout.origin(0,c);s=1254;actualcontext=canvas[y:y+s,x:x+s].copy();actualknown=covered[y:y+s,x:x+s].copy();actualedges=engine.active_edges(layout,0,c,'NE',neighbors);actualowner=engine.owner_mask(actualknown,actualedges,layout)
 merged,f,t,report=engine.register_native(actualcontext,patch,actualknown,actualowner,actualedges,layout,max_shift=6.,tone_cap=18.,return_depth=256);canvas[y:y+s,x:x+s]=merged;covered[y:y+s,x:x+s]=True;runtime_reports.append(dict(source=ref(source),registration=report))
runtime=Image.fromarray(merged);rp=out/'actual-assembly-native-frame.png';runtime.save(rp);write(out/'actual-assembly.json',dict(script=ref(__file__),proposal=ref(p),plan=ref(T/'plan.json'),runtime=ref(rp),patches=runtime_reports,nativeCorePixelsChangedOnRepeat=int(np.any(merged[115:515,:1139]!=proposal[115:515,:1139],axis=2).sum()),pendingVisualQA=True))
coreX=(col-1)*1024;join=Image.new('RGB',(1024,550));join.paste(Image.fromarray(neighbors['north']).crop((coreX,3946,coreX+1024,4096)),(0,0));join.paste(runtime.crop((115,115,1139,515)),(0,150));join.save(out/'qa-north.png')
boxes=[('qa-return-y400',(0,375,1254,655)),('qa-east-north-corner',(930,0,1254,655)),('qa-rock',(450,0,1000,515)),('qa-left-support',(0,0,350,650))]
for name,box in boxes:runtime.crop(box).save(out/(name+'.png'))
for q in out.glob('qa-*.png'):write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(rp),north=ref(plan['northCandidate']),operation=ref(out/'actual-assembly.json'),nativeScale=1,actuallyViewed=False))
print(json.dumps(dict(proposal=ref(p),diagnostic=ref(out/'diagnostic.json'),maxAppliedFlow=diag['maxAppliedFlow'],maxAppliedTone=diag['maxAppliedTone'],minAppliedJacobian=diag['minAppliedJacobian'])))
