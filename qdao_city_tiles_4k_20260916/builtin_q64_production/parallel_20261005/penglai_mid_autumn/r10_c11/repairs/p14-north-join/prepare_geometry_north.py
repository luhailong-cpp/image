from prepare_repair import *
v=HERE/"geometry-north-v1";v.mkdir(exist_ok=False)
base=HERE/"tone-diagnostic-separated-v2/separate-edges256/proposal-native-frame.png";assert sha(base)=="79ab50f726e4d7f15330fb89af7e16f55ae78fdc1676cf53bbbb25487d0dbc45"
records=read(TILE/"native/p14.request.json")["contextRegions"];sources={}
for q in records:assert sha(q["file"])==q["sha256"];sources[q["source"]]=Image.open(q["file"]).convert("RGB")
im=Image.new("RGB",(1254,1254));im.paste(sources["north"].crop((2957,3469,4096,4096)),(0,0));im.paste(sources["northeast"].crop((0,3469,115,4096)),(1139,0));im.paste(Image.open(base).convert("RGB").crop((0,115,1139,742)),(0,627));im.paste(sources["east"].crop((0,0,115,627)),(1139,627))
im.save(v/"same-scale-context.png");holes=[[0,595,272,760],[425,599,615,700]]
target=im.convert("RGBA")
for box in holes:target.paste((0,0,0,0),box)
target.save(v/"edit-target.png")
mapping=dict(canvasGlobalXYWH=[43917,36237,1254,1254],canvasShiftFromOriginalP14XY=[0,-512],originalP14GlobalXYWH=[43917,36749,1254,1254],trueNorthBoundaryWorkY=627,scale=1,resized=False,rotated=False,holesLTRB=holes,onlyCurrentSideMayBeApplied=True,applicationOffsetWorkToNative=[0,-512],sourceRegions=[dict(source=ref(base),cropLTRB=[0,115,1139,742],pasteXY=[0,627]),dict(source=[q for q in records if q["source"]=="north"][0],cropLTRB=[2957,3469,4096,4096],pasteXY=[0,0]),dict(source=[q for q in records if q["source"]=="northeast"][0],cropLTRB=[0,3469,115,4096],pasteXY=[1139,0]),dict(source=[q for q in records if q["source"]=="east"][0],cropLTRB=[0,0,115,627],pasteXY=[1139,627])])
write(v/"mapping.json",mapping)
prompt="""Use case: precise-object-edit / small local inpainting.
Image1 is a 1254x1254 native-scale edit target. Fill only the TWO small transparent openings. The left opening crosses a flat purple rock wall: continue the same large soft purple face and its narrow pale vertical corner highlight smoothly through the gap, matching the exact existing outlines above and below. No horizontal ledge, step, tile, new rock, rectangular lighter patch or edge across the face. Do not move the shoreline, widen the rock or change its silhouette.
The small middle opening crosses one cyan water curve. Connect the existing wave edges and cyan width exactly from the intact top to the intact bottom, smoothly removing a tiny broken endpoint, with the same neighboring water colors. Keep the existing water cells, no new cells or glow.
Image2 gives exactly the same frame before erasing as a placement reference. Preserve its entire scene, all large planes, shore silhouette, every water cell and their positions; only heal the tiny straight contact defects within the two openings. Image3 is approved rounded hand-painted style only, no UI.
Keep all surroundings unchanged and retain the precise 1254x1254 frame at original scale. No zoom, resize, rotate, mirror, new objects or broad repaint. Return fully opaque."""
refs=[v/"edit-target.png",v/"same-scale-context.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")]
call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
write(v/"repair.request.json",dict(startedAt=datetime.now(timezone.utc).isoformat(),tile="r10_c11",patch="p14",configSnapshot=read(HERE/"repair.request.json")["configSnapshot"],prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(q) for q in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),sourceNative=ref(TILE/"native/p14.png"),baseProposal=ref(base),actualModel=None,actualQuality=None,repairWorkCanvas=mapping,approvedForPromotion=False))
for n in ["same-scale-context.png","edit-target.png"]:write(str(v/n)+".generation.json",dict(**ref(v/n),operation="Exact native crop/paste and two small alpha holes only.",mapping=ref(v/"mapping.json"),sources=[ref(base)]+[dict(file=q["file"],sha256=q["sha256"]) for q in records],nativeScale=1))
print(str(v/"repair.call.json"))

