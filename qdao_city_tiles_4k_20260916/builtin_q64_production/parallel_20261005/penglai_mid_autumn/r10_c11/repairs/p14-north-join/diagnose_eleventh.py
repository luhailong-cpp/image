from prepare_repair import *
v=HERE/"v11";patch=np.asarray(Image.open(v/"host-result.png").convert("RGB"))
sources={};ops=[]
for op in read(TILE/"native/p14.request.json")["contextRegions"]:
 sources[op["source"]]=np.asarray(Image.open(op["file"]).convert("RGB"));ops.append(op)
layout=engine.Layout();context,known=engine.materialize_context(layout,ops,sources);owner=engine.owner_mask(known,["right","top"],layout)
merged,flow,tone,report=engine.register_native(context,patch,known,owner,["right","top"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
rows=[]
for x in [40,120,190,300,500,700,900,1100]:
 rows.append(dict(edge="north",xy=[x,115],actualPreviousPixel=context[114,x].tolist(),generatedPreviousPixel=patch[114,x].tolist(),generatedFirstCorePixel=patch[115,x].tolist(),boundedFirstCorePixel=merged[115,x].tolist(),boundedTone=tone[115,x].tolist(),flow=flow[115,x].tolist(),jump=(merged[115,x].astype(int)-context[114,x].astype(int)).tolist()))
for y in [160,220,450,600,850,1100]:
 rows.append(dict(edge="east",xy=[1138,y],actualNextPixel=context[y,1139].tolist(),generatedNextPixel=patch[y,1139].tolist(),generatedLastCorePixel=patch[y,1138].tolist(),boundedLastCorePixel=merged[y,1138].tolist(),boundedTone=tone[y,1138].tolist(),flow=flow[y,1138].tolist(),jump=(merged[y,1138].astype(int)-context[y,1139].astype(int)).tolist()))
write(v/"boundary-numeric-evidence.json",dict(scope="Read-only diagnostic sampling; no automatic visual pass, no changed registration limits.",source=ref(v/"host-result.png"),preview=ref(v/"bounded-preview.png"),report=report,samples=rows))
print(json.dumps(rows))
for version,names,issues in [
("v9",["qa-north-join.png","qa-ne-corner.png","qa-real-ne-e-only.png","qa-real-n-ne-only.png"],["Cross-boundary repair did not remove straight N/E material/tone line in production bounded preview. True independent neighbor-only curves are coherent. Do not promote."]),
("v10",["qa-north-join.png","qa-east-join.png"],["Matte water material improves north fit substantially, but east dark rectangular join remains and cliff foot moved from roughly y600 to y950. Do not promote."]),
("v11",["qa-north-join.png","qa-east-join.png","qa-rock-join.png"],["Cliff contour restored to roughly y600 and matte water retained, but northern cliff material/tone step remains; east rectangular tone edge and several wave endpoints still differ after exact6/18/256 preview. Do not promote."])]:
 folder=HERE/version
 write(folder/"review.json",dict(reviewedAt=datetime.now(timezone.utc).isoformat(),reviewer="/root/r09c14_row3_resume",items=[dict(**ref(folder/n),actuallyViewed=True,nativeScale=1,viewTool="view_image detail original",verdict="inspected_not_accepted") for n in names],approvedForPromotion=False,nativeFileModified=False,verdict="needs_repair",issues=issues))
write(HERE/"current-status.json",dict(updatedAt=datetime.now(timezone.utc).isoformat(),native=ref(TILE/"native/p14.png"),nativeModified=False,latestProposal=ref(v/"host-result.png"),latestBoundedPreview=ref(v/"bounded-preview.png"),approvedForPromotion=False,method="Cross-boundary shifted L retry then full matte-water regeneration then same-frame coast restoration; all exact sources saved. Pausing AI repetition for numeric/independent root review.",remainingIssues=["north rock tone/material boundary","east tone/curve mismatch"],numericEvidence=ref(v/"boundary-numeric-evidence.json")))

