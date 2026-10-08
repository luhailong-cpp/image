from prepare_repair import *
v=HERE/"geometry-north-v2";v.mkdir(exist_ok=False);old=HERE/"geometry-north-v1";req=read(old/"repair.request.json")
im=Image.open(old/"same-scale-context.png").convert("RGB");im.save(v/"same-scale-context.png");target=im.convert("RGBA");holes=[[0,627,280,760],[415,627,625,730]]
for box in holes:target.paste((0,0,0,0),box)
target.save(v/"edit-target.png");mapping=req["repairWorkCanvas"].copy();mapping["holesLTRB"]=holes;write(v/"mapping.json",mapping)
prompt="""Fill only the two small transparent openings in Image1 at original1254x1254 scale.
For the left rock opening, continue the exact purple rock face and its pale corner highlight DOWNWARD from the visible top edge of the opening. Meet the unchanged rock below without any horizontal line, terrace, rectangular patch or material change. The top purple plane is authoritative for tone and shape. Keep the nearby deep-blue vertical side face and the rock's outline in their exact positions.
For the cyan water-curve opening, extend the exact curved cyan shape at the TOP edge down into the gap, joining naturally to the existing blue shapes below. Preserve the top curve's width and tangent. There must be no detached thin stroke, doubled outline, tiny crack, notch or straight horizontal cutoff along this contact. Keep the water cells' broad shape and existing matte-blue colors.
All pixels surrounding the holes, particularly the entire upper half, must remain unchanged. No new cells, reflections, objects, zoom, crop, resize or rotation. Image2 is the approved painted style only. Return the complete same canvas fully opaque."""
refs=[v/"edit-target.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")];call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
req.update(startedAt=datetime.now(timezone.utc).isoformat(),prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(q) for q in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),repairWorkCanvas=mapping,approvedForPromotion=False);write(v/"repair.request.json",req)
for n in ["same-scale-context.png","edit-target.png"]:write(str(v/n)+".generation.json",dict(**ref(v/n),operation="Exact native crop/paste and current-side-only two alpha holes.",mapping=ref(v/"mapping.json"),sources=[ref(old/"same-scale-context.png")],nativeScale=1))
print(str(v/"repair.call.json"))

