from prepare_repair import *
v=HERE/"geometry-east-v2";v.mkdir(exist_ok=False)
prev=HERE/"geometry-east-v1";req=read(prev/"repair.request.json")
im=Image.open(prev/"same-scale-context.png").convert("RGB");im.save(v/"same-scale-context.png")
hole=[420,550,725,870];target=im.convert("RGBA");target.paste((0,0,0,0),hole);target.save(v/"edit-target.png")
mapping=req["repairWorkCanvas"].copy();mapping["holeLTRB"]=hole;mapping["holeCrossesRealSeamForContext"]=True;mapping["applicationOnlyCurrentSide"]=True
write(v/"mapping.json",mapping)
prompt="""Use case: precise-object-edit.
Fill the small transparent rectangle in Image1, a 1254x1254 original-scale crop of a finished painted game-map water surface. Continue exactly the blue water cells and cyan wave ribbons meeting every side of the opening. Repair their local direction and width so each curve flows cleanly through the opening, with no little notch, square corner, double endpoint or straight vertical cutoff near the middle. In particular the broad slanted cyan ribbon entering the upper-left side of the hole must flow into its matching cyan curve on the right without a width step. Use the same existing shades and softly painted surface. This is a tiny continuity repair; keep all water outside the opening exactly as it is. Do not add highlights, reflections, foam, new cells, objects or texture.
Image2 is approved style only. Keep the exact 1254x1254 frame and native scale, no crop, resize, zoom, rotation or mirror. Return a fully opaque completed image."""
refs=[v/"edit-target.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")]
call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
req.update(startedAt=datetime.now(timezone.utc).isoformat(),prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(q) for q in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),repairWorkCanvas=mapping,approvedForPromotion=False)
write(v/"repair.request.json",req)
for n in ["same-scale-context.png","edit-target.png"]:write(str(v/n)+".generation.json",dict(**ref(v/n),operation="Exact native crop/paste and local alpha hole crossing seam for context only; old neighbors never modified.",mapping=ref(v/"mapping.json"),sources=[ref(prev/"same-scale-context.png")],nativeScale=1))
print(str(v/"repair.call.json"))

