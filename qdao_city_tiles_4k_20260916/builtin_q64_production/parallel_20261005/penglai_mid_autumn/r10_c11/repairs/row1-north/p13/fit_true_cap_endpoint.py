from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
D=Path(__file__).resolve().parent;T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
cv=engine.base.cv_module();base=D/'v2-rock/bounded-native';out=D/'v2-rock/endpoint-fit';out.mkdir(exist_ok=False)
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
plan=json.loads((T/'plan.json').read_text(encoding='utf-8-sig'));l=engine.Layout();neighbors={k:ar(plan[v]) for k,v in [('north','northCandidate'),('east','eastCandidate'),('northeast','northEastCandidate')]};imgs={**neighbors,'p14':ar(T/'native/p14.png')};ops=engine.context_operations(l,0,2,'NE',neighbors);context,known=engine.materialize_context(l,ops,imgs);owner=engine.owner_mask(known,['right','top'],l)
native=ar(base/'unregistered-native.png');flow=np.load(base/'flow.npy');tone=np.load(base/'tone.npy');alpha=np.load(base/'alpha.npy');yy,xx=np.mgrid[:1254,:1254].astype(np.float32);aligned=cv.remap(native,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
def peak(row):
 g=np.linalg.norm(np.diff(row[750:815].astype(np.float32),axis=0),axis=1);a=int(g.argmax());lo=max(0,a-2);hi=min(len(g),a+3);z=g[lo:hi];return float((z*np.arange(lo,hi)).sum()/z.sum()+750)
samples=[dict(y=y,trueEdge=peak(context[y]),alignedEdge=peak(aligned[y])) for y in range(108,115)];ys=np.array([z['y'] for z in samples]);ds=np.array([z['alignedEdge']-z['trueEdge'] for z in samples]);fit=np.polyfit(ys,ds,1);delta=float(np.polyval(fit,115));assert abs(delta)<=6
weight=sm((xx-660)/60)*sm((900-xx)/60)*sm((371-yy)/224);newflow=flow.copy();newflow[:,:,0]+=delta*weight;magn=np.linalg.norm(newflow,axis=2);clip=magn>6;newflow*=np.minimum(1,6/np.maximum(magn,1e-8))[:,:,None]
dyu,dxu=np.gradient(newflow[:,:,0]);dyv,dxv=np.gradient(newflow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;use=(weight>0)&(alpha>0);assert float(jac[use].min())>=.25
reg=np.clip(np.rint(cv.remap(native,xx+newflow[:,:,0],yy+newflow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE).astype(np.float32)+tone),0,255).astype(np.uint8);reg=np.where(owner[:,:,None],reg,context);original=ar(T/'native/p13.png');new=np.clip(np.rint(original*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8);previous=ar(base/'proposal-native.png');proposal=previous.copy();proposal[use]=new[use];assert np.array_equal(proposal[515:],original[515:]);p=out/'proposal-native.png';Image.fromarray(proposal).save(p);np.save(out/'flow.npy',newflow)
diag=dict(script=ref(__file__),sourceProposal=ref(base/'proposal-native.png'),sourceNativeAI=ref(base/'unregistered-native.png'),trueNorth=ref(plan['northCandidate']),samples=samples,method='Subpixel RGB-gradient edge centroid in true NORTH rows108..114 only; linear extrapolation to first owned row115; horizontal source-flow correction, bounded norm6 with finite256 return. No pixel or shape drawing.',fitCoefficients=fit.tolist(),sourceFlowDeltaXAtContact=delta,maxAppliedFlow=float(np.linalg.norm(newflow[use],axis=1).max()),clippedFraction=float(clip[use].mean()),minJacobian=float(jac[use].min()),toneUnchanged=ref(base/'tone.npy'),influenceNativeLTRB=[660,115,900,371],proposal=ref(p),visualPass=False,canonicalUnchanged=True);write(out/'diagnostic.json',diag);write(Path(str(p)+'.generation.json'),dict(**ref(p),derivedFrom=[ref(base/'proposal-native.png'),ref(base/'unregistered-native.png')],operation=ref(out/'diagnostic.json'),actualModel=None,actualQuality=None,sourceUpscaled=False,resizedAfterGeneration=False))
canvas,covered,_=engine.seed_neighbors(l,neighbors)
for col in [3,2]:
 source=T/'native/p14.png' if col==3 else p;x,y=l.origin(0,col);con=canvas[y:y+1254,x:x+1254].copy();kn=covered[y:y+1254,x:x+1254].copy();edges=engine.active_edges(l,0,col,'NE',neighbors);own=engine.owner_mask(kn,edges,l);merged,f,t,report=engine.register_native(con,ar(source),kn,own,edges,l,max_shift=6.,tone_cap=18.,return_depth=256);canvas[y:y+1254,x:x+1254]=merged;covered[y:y+1254,x:x+1254]=True
runtime=Image.fromarray(merged);rp=out/'actual-assembly-native-frame.png';runtime.save(rp)
for n,b in [('qa-rock',(450,0,1000,515)),('qa-cap-detail',(650,60,850,240)),('qa-return',(570,280,1000,440))]:
 q=out/(n+'.png');runtime.crop(b).save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(rp),cropLTRB=list(b),nativeScale=1,actuallyViewed=False))
print(json.dumps(diag))
