from prepare_repair import *
v=HERE/"geometry-north-v1";d=v/"rock-sigma1";d.mkdir(exist_ok=False);req=read(v/"repair.request.json");raw=v/"host-result-shifted.png";host=Image.open(raw).convert("RGB")
base=Image.open(req["baseProposal"]["file"]).convert("RGB");patch=base.copy();patch.paste(host.crop((0,512,1254,1254)),(0,0));patch=np.asarray(patch)
records=read(TILE/"native/p14.request.json")["contextRegions"];sources={}
for q in records:assert sha(q["file"])==q["sha256"];sources[q["source"]]=np.asarray(Image.open(q["file"]).convert("RGB"))
layout=engine.Layout();context,known=engine.materialize_context(layout,records,sources);owner=engine.owner_mask(known,["top","right"],layout)
normal,flow,oldt,rep=engine.register_native(context,patch,known,owner,["top","right"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
cv=engine.base.cv_module();yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
aligned=cv.remap(patch,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
def gradient(im):
 g=cv.cvtColor(im,cv.COLOR_RGB2GRAY).astype(np.float32);gy,gx=np.gradient(g);return np.hypot(gx,gy)
residual=context.astype(np.float32)-aligned.astype(np.float32)
safe=(yy<115)&known&(gradient(context)<12)&(gradient(aligned)<12)&(np.max(np.abs(residual),axis=2)<40)
weights=cv.GaussianBlur(safe.astype(np.float32),(0,0),1);measured=cv.GaussianBlur(residual*safe[:,:,None],(0,0),1)/np.maximum(weights[:,:,None],1e-6)
_,lab=cv.distanceTransformWithLabels((~safe).astype(np.uint8),cv.DIST_L2,5,labelType=cv.DIST_LABEL_PIXEL)
tab=np.zeros((int(lab.max())+1,3),np.float32);tab[lab[safe]]=measured[safe];extended=cv.GaussianBlur(tab[lab],(0,0),1)
def smooth(a):
 a=np.clip(a,0,1);return a*a*(3-2*a)
tone=np.clip(extended,-18,18)*smooth((256-(yy-115))/(256-32))[:,:,None]
matched=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
a1=smooth((312-xx)/40)*smooth((288-yy)/40)
a2=smooth((xx-390)/35)*smooth((650-xx)/35)*smooth((223-yy)/35)
alpha=a1;alpha[(xx>=1139)|(yy<115)]=0
result=np.clip(np.rint(matched*alpha[:,:,None]+np.asarray(base)*(1-alpha[:,:,None])),0,255).astype(np.uint8)
out=d/"proposal-p14.png";Image.fromarray(result).save(out);np.save(d/"alpha.npy",alpha);np.save(d/"flow.npy",flow);np.save(d/"tone.npy",tone)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
diff=np.any(result!=np.asarray(base),axis=2);ys,xs=np.where(diff)
diag=dict(proposal=ref(out),sourceAI=ref(raw),base=req["baseProposal"],script=ref(__file__),mapping=ref(v/"mapping.json"),registration=rep,operation="Map host row512..1254 to native row0..742, bounded flow6 plus north-only local sigma1 true support tone <=18 return256. Local AI alpha return40 rock/35 wave; all nonlocal base and true N/E/NE pixels exact.",alphaZeroOutsideUnion=[[0,115,312,288]],alphaFullUnion=[[0,115,272,248]],toneMax=float(np.abs(tone).max()),rawToneClippedSupportFraction=float(np.mean(np.any(np.abs(extended[safe])>18,axis=1))),jacobianMinimum=float(jac[alpha>0].min()),changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedPixels=int(diff.sum()),trueSupportUnchanged=bool(np.array_equal(result[known],np.asarray(base)[known])),nativeUnchanged=sha(TILE/"native/p14.png")==req["sourceNative"]["sha256"],approvedForPromotion=False,automaticVisualPass=False)
write(d/"diagnostic.json",diag);write(str(out)+".generation.json",dict(**ref(out),derivedFrom=[ref(raw),req["baseProposal"]]+[dict(file=q["file"],sha256=q["sha256"]) for q in records],operation=ref(d/"diagnostic.json"),actualModel=None,actualQuality=None))
for n,box in [("qa-north-wave",(360,45,670,255)),("qa-rock-join",(0,0,420,390)),("qa-north-whole",(0,0,1254,460)),("qa-rock-return",(0,208,380,358)),("qa-wave-return",(360,150,700,280))]:
 p=d/(n+".png");Image.fromarray(result).crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(out)],operation={"cropLTRB":box},nativeScale=1,actuallyViewed=False))
print(json.dumps(diag))

