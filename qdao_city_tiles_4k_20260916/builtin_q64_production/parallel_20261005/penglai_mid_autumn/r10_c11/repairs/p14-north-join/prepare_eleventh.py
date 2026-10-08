from prepare_repair import *
v=HERE/"v11";v.mkdir(exist_ok=False)
records=read(TILE/"native/p14.request.json")["contextRegions"];sources={}
for op in records:
 assert sha(op["file"])==op["sha256"];sources[op["source"]]=np.asarray(Image.open(op["file"]).convert("RGB"))
context,known=engine.materialize_context(engine.Layout(),records,sources)
base=np.asarray(Image.open(HERE/"v10/host-result.png").convert("RGB"))
base=np.where(known[:,:,None],context,base)
Image.fromarray(base).save(v/"same-frame-context.png")
target=Image.fromarray(base).convert("RGBA")
holes=[[0,115,400,1030],[925,115,1139,1254]]
for box in holes:target.paste((0,0,0,0),box)
target.save(v/"edit-target.png")
prompt="""Use case: precise-object-edit / local inpainting.
Image1 is the exact1254x1254 EDIT TARGET with two transparent areas. Fully fill these two areas while retaining the unmasked central matte-blue water, exact camera and scale. The top115px and far-right115px are real neighboring artwork and are authoritative.
LEFT OPENING: restore the original partial cliff silhouette shown at exactly the SAME FRAME AND SCALE in Image2. In Image2 the cliff's right contour begins atx230 along the top, bows gently to aboutx300, then curves left; the cliff foot reaches the left edge near y600. Copy that silhouette at those same pixel positions. Do NOT stretch it down to y950 or import a larger rock. The area below that original y600 rock foot is WATER. Use Image2 for geometry only, not its shiny water. Paint the repaired rock as smooth broad low-contrast matte lavender vertical planes exactly matching Image1's true top rock. Keep one partial cropped cliff; no new faceted edges, ledges, foreground rocks or object changes.
RIGHT OPENING: join the fixed central water naturally to the true far-right neighboring water. Image3 is a wider sample of that real east neighbor, starting at the physical edge; its color and endpoints govern this side. Carry that neighbor's deeper blue cell shading and existing wave tangents gently LEFT through the opening as natural curved water cells. The previous straight x1139 dark rectangular edge is a seam to heal, not a shadow boundary or underwater object. This local deeper color must blend over the cell interiors into the center, never create a vertical strip or a sudden step. Keep all existing opaque curve endpoints aligned. No additional subdivided wave grid, white glitter or small foam veins.
The central water of Image1 is already the correct material, matching the matte actual north neighbor. Preserve its broad blue faces and cyan curves; do not revert it to the glossier water in Image2. Image4 is approved rounded clean hand-painted style only; no UI or objects.
Fully opaque output, same1254x1254 frame. No resizing, reframing, rotation, mirror, new objects, text or borders. Keep the whole visible top/right reference geometry unchanged and join the missing colors seamlessly."""
refs=[v/"edit-target.png",HERE/"v8/host-result.png",HERE/"actual-east-focus.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")]
call=dict(prompt=prompt,referenced_image_paths=[str(x) for x in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
write(v/"repair.request.json",dict(startedAt=datetime.now(timezone.utc).isoformat(),tile="r10_c11",patch="p14",configSnapshot=read(HERE/"repair.request.json")["configSnapshot"],prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(x) for x in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),actualModel=None,actualQuality=None,sourceNative=ref(TILE/"native/p14.png"),priorRepair=ref(HERE/"v10/host-result.png"),holeLTRB=holes,approvedForPromotion=False,nativeFileModified=False))
for n in ["same-frame-context.png","edit-target.png"]:
 write(str(v/n)+".generation.json",dict(**ref(v/n),operation="Exact current-frame context restoration and alpha-hole preparation only.",sources=[ref(HERE/"v10/host-result.png")]+[dict(file=o["file"],sha256=o["sha256"]) for o in records],nativeScale=1,holesLTRB=holes))
print(str(v/"repair.call.json"))

