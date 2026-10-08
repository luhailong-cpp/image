from prepare_repair import *
v=HERE/"geometry-east-v1";req=read(v/"repair.request.json");raw=v/"host-result-shifted.png";source=Path("C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-be46b1c8-4860-4faf-932b-6555fc7fc912.png")
im=Image.open(raw).convert("RGB");assert im.size==(1254,1254)
write(str(raw)+".generation.json",dict(**ref(raw),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format="PNG",tool="image_gen.imagegen",route="builtin",configSnapshot=req["configSnapshot"],submittedParameters=req["submittedParameters"],actualSubmitted=req["actualSubmitted"],actualModel=None,actualQuality=None,unverifiedReason="Host-managed builtin does not expose actual model/quality",evidence={"sourceOutputPath":str(source),"sourceOutputSha256":sha(source),"resultId":source.stem},prompt=req["prompt"],promptSha256=req["promptSha256"],references=req["references"],mapping=ref(v/"mapping.json"),approvedForPromotion=False))
base=Image.open(req["baseProposal"]["file"]).convert("RGB");assert sha(req["baseProposal"]["file"])==req["baseProposal"]["sha256"]
box=req["repairWorkCanvas"]["holeLTRB"];offset=req["repairWorkCanvas"]["applicationOffsetWorkToNative"]
proposal=base.copy();proposal.paste(im.crop(box),(box[0]+offset[0],box[1]+offset[1]))
out=v/"proposal-p14.png";proposal.save(out)
a,b=np.asarray(base),np.asarray(proposal);diff=np.any(a!=b,axis=2);ys,xs=np.where(diff)
checks=dict(changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedPixels=int(diff.sum()),application="Exact opaque crop of returned host inside the prepared hole only. All surrounding candidate pixels and all true N/E/NE support remain byte-identical.",sourceWorkCropLTRB=box,pasteNativeXY=[box[0]+offset[0],box[1]+offset[1]],outsideLocalHoleUnchanged=True)
write(str(out)+".generation.json",dict(**ref(out),derivedFrom=[req["baseProposal"],ref(raw)],operation=checks,mapping=ref(v/"mapping.json"),actualModel=None,actualQuality=None,approvedForPromotion=False))
for n,box in [("qa-east-endpoint",(1030,570,1254,850)),("qa-local-return",(932,545,1254,885)),("qa-east-whole",(780,0,1254,1254))]:
 p=v/(n+".png");proposal.crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(out)],operation={"cropLTRB":box},nativeScale=1,actuallyViewed=False))
write(v/"proposal-checks.json",dict(**checks,proposal=ref(out),nativeUnchanged=sha(TILE/"native/p14.png")==req["sourceNative"]["sha256"],approvedForPromotion=False))
print(json.dumps(checks))

