from prepare_repair import *
v=HERE/"v9";request=read(v/"repair.request.json");host=v/"host-result-shifted.png"
source=Path("C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-00151fc4-c9db-4257-b39d-fd34820a1cb0.png")
assert sha(TILE/"native/p14.png")==request["sourceNative"]["sha256"]
im=Image.open(host).convert("RGB");assert im.size==(1254,1254)
write(str(host)+".generation.json",dict(**ref(host),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format="PNG",tool="image_gen.imagegen",route="builtin",configSnapshot=request["configSnapshot"],submittedParameters=request["submittedParameters"],actualSubmitted=request["actualSubmitted"],actualModel=None,actualQuality=None,unverifiedReason="Host-managed model and quality not disclosed",evidence={"sourceOutputPath":str(source),"sourceOutputSha256":sha(source),"resultId":source.stem},prompt=request["prompt"],promptSha256=request["promptSha256"],references=request["references"],repairWorkCanvas=request["repairWorkCanvas"],approvedForPromotion=False,nativeFileModified=False))
old=Image.open(HERE/"v8/host-result.png").convert("RGB")
proposal=old.copy()
alpha=np.zeros((1254,1254),dtype=np.uint8);alpha[:958]=255
for y in range(958,998):alpha[y]=round(255*(1+np.cos(np.pi*(y-958)/40))/2)
mapped=Image.new("RGB",(1254,1254));mapped.paste(im.crop((0,256,1254,1254)),(0,0))
proposal.paste(mapped,(0,0),Image.fromarray(alpha))
p=v/"proposal-p14.png";proposal.save(p)
write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(host),ref(HERE/"v8/host-result.png")],operation=request["repairWorkCanvas"]["finalProposalOperation"],mapping=ref(v/"mapping.json"),actualModel=None,actualQuality=None,approvedForPromotion=False))
sources={};ops=[]
for op in read(TILE/"native/p14.request.json")["contextRegions"]:
 assert sha(op["file"])==op["sha256"]
 sources[op["source"]]=np.asarray(Image.open(op["file"]).convert("RGB"));ops.append(op)
layout=engine.Layout();context,known=engine.materialize_context(layout,ops,sources);owner=engine.owner_mask(known,["right","top"],layout)
merged,flow,tone,report=engine.register_native(context,np.asarray(proposal),known,owner,["right","top"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
preview=v/"bounded-preview.png";Image.fromarray(merged).save(preview)
write(str(preview)+".generation.json",dict(**ref(preview),source=ref(p),actualNativeSources=read(HERE/"preparation.json")["sources"],operation="Diagnostic exact production6/18/256 NE registration; no visual acceptance",nativeScale=1,formalAccepted=False))
write(v/"diagnostic.json",dict(report=report,source=ref(p),preview=ref(preview),automaticVisualPass=False))
for name,box in [("north-join",(0,0,1254,460)),("east-join",(780,0,1254,1254)),("rock-join",(0,0,420,600)),("north-return",(0,250,1139,490)),("east-return",(740,115,1020,1254)),("ne-corner",(894,0,1254,360)),("workcanvas-return",(0,848,1254,1128))]:
 path=v/("qa-"+name+".png");Image.fromarray(merged).crop(box).save(path);write(str(path)+".generation.json",dict(**ref(path),source=ref(preview),operation={"cropLTRB":box},nativeScale=1,actuallyViewed=False,formalAccepted=False))
print(json.dumps(dict(proposal=str(p),sha256=sha(p),preview=str(preview),rawSupportMax=report["rawSupportMaxDisplacementVector"],clippedSupportFraction=report["clippedSupportFraction"])))

