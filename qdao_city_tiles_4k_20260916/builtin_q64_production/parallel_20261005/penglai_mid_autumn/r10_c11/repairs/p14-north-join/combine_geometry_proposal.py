from prepare_repair import *
d=HERE/"geometry-combined-v1";d.mkdir(exist_ok=False)
base=HERE/"tone-diagnostic-separated-v2/separate-edges256/proposal-native-frame.png";b=np.asarray(Image.open(base).convert("RGB"));out=b.copy()
parts=[("east",HERE/"geometry-east-v3/bounded/proposal-p14.png",[844,525,1139,885]),("rock",HERE/"geometry-north-v1/rock-sigma1/proposal-p14.png",[0,115,312,288]),("north-wave",HERE/"geometry-north-v2/bounded/proposal-p14.png",[380,115,660,253])]
occupied=np.zeros((1254,1254),bool);details=[]
for name,p,box in parts:
 x0,y0,x1,y1=box;assert not occupied[y0:y1,x0:x1].any();part=np.asarray(Image.open(p).convert("RGB"));diff=np.any(part!=b,axis=2);allowed=np.zeros((1254,1254),bool);allowed[y0:y1,x0:x1]=True
 assert not diff[~allowed].any() if name!="north-wave" else not diff[(np.indices(diff.shape)[1]>320)&~allowed].any()
 out[y0:y1,x0:x1]=part[y0:y1,x0:x1];occupied[y0:y1,x0:x1]=True;details.append(dict(role=name,source=ref(p),cropLTRB=box,pasteXY=[x0,y0],scale=1,sourceDiagnostic=ref(p.parent/"diagnostic.json")))
proposal=d/"proposal-p14.png";Image.fromarray(out).save(proposal)
req=read(TILE/"native/p14.request.json");sources={}
for q in req["contextRegions"]:assert sha(q["file"])==q["sha256"];sources[q["source"]]=np.asarray(Image.open(q["file"]).convert("RGB"))
layout=engine.Layout();context,known=engine.materialize_context(layout,req["contextRegions"],sources);owner=engine.owner_mask(known,["top","right"],layout)
assert np.array_equal(out[known],context[known])
checked,flow,tone,rep=engine.register_native(context,out,known,owner,["top","right"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
Image.fromarray(checked).save(d/"production-recheck.png")
diff=np.any(out!=b,axis=2);ys,xs=np.where(diff)
report=dict(proposal=ref(proposal),base=ref(base),operation="Disjoint exact scale1 crop/paste of three isolated bounded AI repair proposals. No fresh drawing, resize, rotation or registration in combination.",parts=details,script=ref(__file__),sourceSupport=[dict(file=q["file"],sha256=q["sha256"]) for q in req["contextRegions"]],nativeCurrent=ref(TILE/"native/p14.png"),trueSupportExact=True,changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedPixels=int(diff.sum()),productionRecheck=dict(file=ref(d/"production-recheck.png"),pixelIdentical=bool(np.array_equal(checked,out)),registration=rep),approvedForPromotion=False,automaticVisualPass=False)
write(d/"proposal.json",report);write(str(proposal)+".generation.json",dict(**ref(proposal),derivedFrom=[ref(base)]+[q["source"] for q in details],operation=ref(d/"proposal.json"),actualModel=None,actualQuality=None,approvedForPromotion=False))
crops=[("north-join",(0,0,1254,460)),("east-join",(780,0,1254,1254)),("rock-join",(0,0,420,600)),("north-return",(0,250,1139,490)),("east-return",(740,115,1020,1254)),("ne-corner",(894,0,1254,360)),("north-wave-endpoint",(360,45,670,255)),("east-wave-endpoint",(1030,570,1254,850)),("east-local-return",(814,495,1254,915)),("rock-local-return",(0,208,380,358)),("north-wave-local-return",(360,175,700,290))]
for name,box in crops:
 p=d/("qa-"+name+".png");Image.fromarray(out).crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(proposal)],operation=dict(cropLTRB=box),nativeScale=1,actuallyViewed=False))
print(json.dumps(dict(proposal=ref(proposal),recheckIdentity=report["productionRecheck"]["pixelIdentical"],changed=report["changedPixels"])))

