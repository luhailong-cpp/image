from prepare_repair import *
v=HERE/"geometry-east-v1";d=v/"bounded-v2";d.mkdir(exist_ok=False)
req=read(v/"repair.request.json");raw=v/"host-result-shifted.png";base=Image.open(req["baseProposal"]["file"]).convert("RGB");host=Image.open(raw).convert("RGB")
patch=base.copy();patch.paste(host.crop((0,0,742,1254)),(512,0));patch=np.asarray(patch)
records=read(TILE/"native/p14.request.json")["contextRegions"];sources={}
for q in records:assert sha(q["file"])==q["sha256"];sources[q["source"]]=np.asarray(Image.open(q["file"]).convert("RGB"))
layout=engine.Layout();context,known=engine.materialize_context(layout,records,sources);owner=engine.owner_mask(known,["top","right"],layout)
normal,flow,tone,rep=engine.register_native(context,patch,known,owner,["top","right"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
cv=engine.base.cv_module();yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
aligned=cv.remap(patch,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
def gradient(im):
 g=cv.cvtColor(im,cv.COLOR_RGB2GRAY).astype(np.float32);gy,gx=np.gradient(g);return np.hypot(gx,gy)
residual=context.astype(np.float32)-aligned.astype(np.float32)
safe=(xx>=1139)&known&(gradient(context)<12)&(gradient(aligned)<12)&(np.max(np.abs(residual),axis=2)<40)
weights=cv.GaussianBlur(safe.astype(np.float32),(0,0),3)
measured=cv.GaussianBlur(residual*safe[:,:,None],(0,0),3)/np.maximum(weights[:,:,None],1e-6)
_,lab=cv.distanceTransformWithLabels((~safe).astype(np.uint8),cv.DIST_L2,5,labelType=cv.DIST_LABEL_PIXEL)
tab=np.zeros((int(lab.max())+1,3),np.float32);tab[lab[safe]]=measured[safe]
extended=cv.GaussianBlur(tab[lab],(0,0),3)
def smooth(a):
 a=np.clip(a,0,1);return a*a*(3-2*a)
tone=np.clip(extended,-18,18)*smooth((256-(1138-xx))/(256-32))[:,:,None]
matched=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
alpha=smooth((xx-932)/70)*smooth((yy-545)/50)*smooth((885-yy)/70)
alpha[(xx>=1139)|(yy<115)]=0
result=np.clip(np.rint(matched*alpha[:,:,None]+np.asarray(base)*(1-alpha[:,:,None])),0,255).astype(np.uint8)
proposal=d/"proposal-p14.png";Image.fromarray(result).save(proposal)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
changed=np.any(result!=np.asarray(base),axis=2);ys,xs=np.where(changed)
stats=dict(proposal=ref(proposal),sourceAI=ref(raw),base=req["baseProposal"],script=ref(__file__),operation="Map same-scale shifted AI host to original frame, bounded production optical flow 6; east-only sigma3 support residual tone <=18 finite256; local AI composite with smooth alpha within [932,545,1139,885]. No pixel artwork blur or shape drawing.",alphaFullRegion=[1002,595,1139,815],alphaZeroOutside=[932,545,1139,885],registration=rep,toneMax=float(np.abs(tone).max()),rawToneClippedSupportFraction=float(np.mean(np.any(np.abs(extended[safe])>18,axis=1))),jacobianMinimum=float(jac[alpha>0].min()),changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedPixels=int(changed.sum()),trueSupportUnchanged=bool(np.array_equal(result[known],np.asarray(base)[known])),nativeUnchanged=sha(TILE/"native/p14.png")==req["sourceNative"]["sha256"],approvedForPromotion=False,automaticVisualPass=False)
write(d/"diagnostic.json",stats);write(str(proposal)+".generation.json",dict(**ref(proposal),derivedFrom=[ref(raw),req["baseProposal"]]+[dict(file=q["file"],sha256=q["sha256"]) for q in records],operation=ref(d/"diagnostic.json"),actualModel=None,actualQuality=None))
np.save(d/"flow.npy",flow);np.save(d/"tone.npy",tone);np.save(d/"alpha.npy",alpha)
for n,box in [("qa-east-endpoint",(1030,570,1254,850)),("qa-local-return",(902,515,1254,915)),("qa-east-whole",(780,0,1254,1254))]:
 p=d/(n+".png");Image.fromarray(result).crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(proposal)],operation={"cropLTRB":box},nativeScale=1,actuallyViewed=False))
write(v/"hard-composite-review.json",dict(proposal=ref(v/"proposal-p14.png"),items=[dict(**ref(v/n),actuallyViewed=True,nativeScale=1,verdict="fail",review="True east restored at x1139 shows visible wave width step and straight tone cut; hard region return is visible.") for n in ["qa-east-endpoint.png","qa-local-return.png"]],scopedPass=False,approvedForPromotion=False))
print(json.dumps(stats))

