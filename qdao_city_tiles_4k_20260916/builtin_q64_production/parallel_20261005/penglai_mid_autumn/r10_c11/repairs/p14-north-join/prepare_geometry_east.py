from prepare_repair import *
v=HERE/"geometry-east-v1";v.mkdir(exist_ok=False)
base=HERE/"tone-diagnostic-separated-v2/separate-edges256/proposal-native-frame.png";assert sha(base)=="79ab50f726e4d7f15330fb89af7e16f55ae78fdc1676cf53bbbb25487d0dbc45"
rec=read(TILE/"native/p14.request.json")["contextRegions"];sources={}
for r in rec:assert sha(r["file"])==r["sha256"];sources[r["source"]]=Image.open(r["file"]).convert("RGB")
im=Image.new("RGB",(1254,1254))
im.paste(Image.open(base).convert("RGB").crop((512,0,1139,1254)),(0,0))
im.paste(sources["northeast"].crop((0,3981,627,4096)),(627,0))
im.paste(sources["east"].crop((0,0,627,1139)),(627,115))
im.save(v/"same-scale-context.png")
hole=[490,595,627,815];target=im.convert("RGBA");target.paste((0,0,0,0),hole);target.save(v/"edit-target.png")
mapping=dict(canvasGlobalXYWH=[44429,36749,1254,1254],canvasShiftFromOriginalP14XY=[512,0],originalP14GlobalXYWH=[43917,36749,1254,1254],trueEastBoundaryWorkX=627,scale=1,resized=False,rotated=False,holeLTRB=hole,onlyCurrentSideMayBeApplied=True,applicationOffsetWorkToNative=[512,0],sourceRegions=[dict(source=ref(base),cropLTRB=[512,0,1139,1254],pasteXY=[0,0]),dict(source=[r for r in rec if r["source"]=="northeast"][0],cropLTRB=[0,3981,627,4096],pasteXY=[627,0]),dict(source=[r for r in rec if r["source"]=="east"][0],cropLTRB=[0,0,627,1139],pasteXY=[627,115])])
write(v/"mapping.json",mapping)
prompt="""Use case: precise-object-edit / exact local inpainting.
Image1 is the1254x1254 EDIT TARGET at original pixel scale. Fill ONLY the small transparent opening just left of the vertical centerline. This opening covers a defective water-wave junction. The entire right half beyond x627 is the REAL FINISHED EAST NEIGHBOR: keep it unchanged and continue its existing cyan ribbon widths and tangent directions smoothly LEFT through the opening to the already finished water on the left. The error is a tiny endpoint/width step, not a request for a new water pattern.
At the former join x627 near y650–740, cyan ribbons and blue water-cell edges must meet the precise existing endpoints without a straight cut, short double line, notch, sudden change of width or squared-off segment. Keep the neighbor's real curves where they are; extend them naturally into the missing current side. Match the local soft blue colors exactly. Use the same quiet broad matte-blue cells and simple cyan curves already visible, with no added shine, subdivision, glow band, foam, sparkle or edge running along the hole boundary.
Image2 is the same exact frame before erasing. It documents the correct composition and all surrounding endpoints; the small water discontinuity beside x627 is the only defect. Image3 is the approved clean rounded hand-painted style reference only; no UI or objects.
All opaque surroundings must remain visually unchanged, including every pixel in the right neighbor, top context, water outside the opening, and all existing natural highlights. Keep same1254x1254 frame, no resize, zoom, rotation, mirror, new objects, border or text. Return fully opaque. This is a small line continuation repair, not a broad scene or water reconstruction."""
refs=[v/"edit-target.png",v/"same-scale-context.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")]
call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
write(v/"repair.request.json",dict(startedAt=datetime.now(timezone.utc).isoformat(),tile="r10_c11",patch="p14",configSnapshot=read(HERE/"repair.request.json")["configSnapshot"],prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(q) for q in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),sourceNative=ref(TILE/"native/p14.png"),baseProposal=ref(base),actualModel=None,actualQuality=None,repairWorkCanvas=mapping,approvedForPromotion=False))
for n in ["same-scale-context.png","edit-target.png"]:write(str(v/n)+".generation.json",dict(**ref(v/n),operation="Exact native crop/paste and small alpha hole only.",mapping=ref(v/"mapping.json"),sources=[ref(base)]+[dict(file=r["file"],sha256=r["sha256"]) for r in rec],nativeScale=1))
print(str(v/"repair.call.json"))

