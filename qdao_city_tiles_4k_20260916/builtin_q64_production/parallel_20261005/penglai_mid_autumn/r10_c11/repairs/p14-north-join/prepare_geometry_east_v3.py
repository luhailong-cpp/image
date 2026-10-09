from prepare_repair import *
v=HERE/"geometry-east-v3";v.mkdir(exist_ok=False)
prev=HERE/"geometry-east-v1";req=read(prev/"repair.request.json")
im=Image.open(prev/"same-scale-context.png").convert("RGB");im.save(v/"same-scale-context.png")
hole=[382,575,627,835];target=im.convert("RGBA");target.paste((0,0,0,0),hole);target.save(v/"edit-target.png")
mapping=req["repairWorkCanvas"].copy();mapping["holeLTRB"]=hole;mapping["applicationOnlyCurrentSide"]=True
write(v/"mapping.json",mapping)
prompt="""Fill only the single transparent opening in this original-scale painted water image. Carefully continue the cyan ribbons from their exact visible endpoints at the RIGHT EDGE of the opening into the missing area on the left. Each bright ribbon must keep the same thickness and smooth tangent as it crosses from the intact right side into the fill. The curved dark-blue lobes on the right need to continue naturally left. Respect the endpoints on the other three sides too. A seamless continuation of the visible waves is the entire task.
Keep the intact right half exactly unchanged. Do not replace or simplify its wave shapes. Match the existing matte-blue colors and softly painted broad curves; no new glints, foam, divisions or objects. Image2 is approved painted style only. Return the same1254x1254 canvas, fully opaque, without zoom, resize, rotation, or reframing."""
refs=[v/"edit-target.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")]
call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
req.update(startedAt=datetime.now(timezone.utc).isoformat(),prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(q) for q in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),repairWorkCanvas=mapping,approvedForPromotion=False)
write(v/"repair.request.json",req)
for n in ["same-scale-context.png","edit-target.png"]:write(str(v/n)+".generation.json",dict(**ref(v/n),operation="Exact native crop/paste and current-side-only alpha hole; old neighbors never modified.",mapping=ref(v/"mapping.json"),sources=[ref(prev/"same-scale-context.png")],nativeScale=1))
print(str(v/"repair.call.json"))

