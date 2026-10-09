from prepare_repair import *
v=HERE/"v11";D=HERE/"tone-diagnostic";D.mkdir(exist_ok=False)
records=read(TILE/"native/p14.request.json")["contextRegions"];sources={};frozen=[]
for op in records:
 assert sha(op["file"])==op["sha256"];sources[op["source"]]=np.asarray(Image.open(op["file"]).convert("RGB"));frozen.append(dict(file=op["file"],sha256=op["sha256"]))
native=ref(TILE/"native/p14.png");host=v/"host-result.png";patch=np.asarray(Image.open(host).convert("RGB"));layout=engine.Layout()
context,known=engine.materialize_context(layout,records,sources);owner=engine.owner_mask(known,["right","top"],layout)
baseline,flow,oldtone,base_report=engine.register_native(context,patch,known,owner,["right","top"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
cv=engine.base.cv_module();yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
aligned=cv.remap(patch,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
def gradient(im):
 gray=cv.cvtColor(im,cv.COLOR_RGB2GRAY).astype(np.float32);gy,gx=np.gradient(gray);return np.hypot(gx,gy)
residual=context.astype(np.float32)-aligned.astype(np.float32)
safe=known&(gradient(context)<12)&(gradient(aligned)<12)&(np.max(np.abs(residual),axis=2)<40)
sigma=3.0
weights=cv.GaussianBlur(safe.astype(np.float32),(0,0),sigma)
measured=cv.GaussianBlur(residual*safe[:,:,None],(0,0),sigma)/np.maximum(weights[:,:,None],1e-6)
_,labels=cv.distanceTransformWithLabels((~safe).astype(np.uint8),cv.DIST_L2,5,labelType=cv.DIST_LABEL_PIXEL)
lut=np.zeros((int(labels.max())+1,3),np.float32);lut[labels[safe]]=measured[safe]
local=cv.GaussianBlur(lut[labels],(0,0),sigma)
distance=np.minimum(yy-115,1138-xx)
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
finite=smooth((256-distance)/(256-32))
localc=np.clip(local,-18,18)*finite[:,:,None]
np.save(D/"unchanged-flow.npy",flow)
variants=[("sigma3-full256",localc,256),("sigma3-edge96",oldtone*(1-smooth((96-distance)/(96-16)))[:,:,None]+localc*smooth((96-distance)/(96-16))[:,:,None],96)]
reports=[]
for name,tone,depth in variants:
 out=D/name;out.mkdir()
 assert np.max(np.abs(tone))<=18.00001
 matched=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8);matched[finite==0]=patch[finite==0]
 result=np.where(owner[:,:,None],matched,context)
 assert np.array_equal(result[~owner],context[~owner])
 assert np.array_equal(result[(finite==0)&owner],patch[(finite==0)&owner])
 proposal=out/"proposal-native-frame.png";Image.fromarray(result).save(proposal);np.save(out/"tone.npy",tone)
 # Normal existing production registration should be identity with exact real support.
 checked,reflow,retone,rereport=engine.register_native(context,result,known,owner,["right","top"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
 checkpath=out/"production-recheck.png";Image.fromarray(checked).save(checkpath)
 diff=np.any(result!=baseline,axis=2);ys,xs=np.where(diff)
 dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
 report=dict(name=name,proposal=ref(proposal),sourceAI=ref(host),script=ref(__file__),nativeUnchanged=native,sourceSupport=frozen,method="Identical bounded optical flow; only replace local color residual estimation Gaussian sigma12 by sigma3, using real low-gradient support only. No artwork blur, geometry redraw, or larger registration.",localSigma=3.,safeGradientThreshold=12.,safeResidualThreshold=40.,maxAllowedFlow=6.,actualMaxFlow=float(np.linalg.norm(flow,axis=2).max()),maxAllowedTone=18.,actualMaxTone=np.abs(tone).max(axis=(0,1)).tolist(),toneRawClippedSupportFraction=float(np.mean(np.any(np.abs(local[safe])>18,axis=1))),flowClippedSupportFraction=base_report["clippedSupportFraction"],returnDepth=256,changedEstimatorReturnDepth=depth,geometryFieldIdentical=True,jacobianMinimum=float(jac[owner].min()),jacobianRequiredMinimum=.25,changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedPixels=int(diff.sum()),knownPixelsExact=True,outsideFiniteInfluenceNativeExact=True,sourceUpscaling=False,productionSecondPass=dict(file=str(checkpath),sha256=sha(checkpath),pixelIdentical=np.array_equal(checked,result),maxFlow=rereport["actualMaxDisplacementVector"],maxTone=rereport["actualMaxColorCorrectionRGB"]),automaticVisualPass=False,approvedForPromotion=False)
 assert report["actualMaxFlow"]<=6.00001 and report["jacobianMinimum"]>=.25
 write(out/"diagnostic.json",report)
 write(str(proposal)+".generation.json",dict(**ref(proposal),derivedFrom=[ref(host)]+frozen,operation=ref(out/"diagnostic.json"),actualModel=None,actualQuality=None,submittedModel=None,submittedQuality=None,approvedForPromotion=False,actualAIRecord=str(host)+".generation.json",nativePixelScale=1))
 for label,box in [("north-join",(0,0,1254,460)),("east-join",(780,0,1254,1254)),("rock-join",(0,0,420,600)),("north-return",(0,250,1139,490)),("east-return",(740,115,1020,1254)),("ne-corner",(894,0,1254,360)),("local-north-return",(0,131,1139,291)),("local-east-return",(962,115,1122,1254))]:
  path=out/("qa-"+label+".png");Image.fromarray(result).crop(box).save(path);write(str(path)+".generation.json",dict(**ref(path),derivedFrom=[ref(proposal)],operation={"cropLTRB":box},actuallyViewed=False,nativeScale=1,automaticVisualPass=False))
 reports.append(report)
for f in frozen:assert sha(f["file"])==f["sha256"]
assert sha(TILE/"native/p14.png")==native["sha256"]
write(D/"index.json",dict(createdAt=datetime.now(timezone.utc).isoformat(),variants=reports,productionHelpersModified=False,productionNativeModified=False,requiresActualOriginalPixelQA=True))
print(json.dumps([dict(name=r["name"],sha256=r["proposal"]["sha256"],maxTone=r["actualMaxTone"],rawToneClipped=r["toneRawClippedSupportFraction"],jacobian=r["jacobianMinimum"],secondPassIdentity=r["productionSecondPass"]["pixelIdentical"]) for r in reports]))

