from prepare_repair import *
old=HERE/"v8";v=HERE/"v9";v.mkdir(exist_ok=False)
sources={}
records=read(TILE/"native/p14.request.json")["contextRegions"]
for op in records:
 assert sha(op["file"])==op["sha256"]
 sources[op["source"]]=Image.open(op["file"]).convert("RGB")
canvas=Image.new("RGB",(1254,1254))
canvas.paste(sources["north"].crop((2957,3725,4096,4096)),(0,0))
canvas.paste(sources["northeast"].crop((0,3725,115,4096)),(1139,0))
canvas.paste(Image.open(old/"host-result.png").convert("RGB").crop((0,115,1254,998)),(0,371))
canvas.paste(sources["east"].crop((0,0,115,883)),(1139,371))
canvas.save(v/"same-scale-context.png")
masked=canvas.convert("RGBA")
# Erase both sides of physical joins, not just the unknown side. Far true N/NE/E remains anchored.
holes=[[0,275,1204,550],[1029,275,1204,1160]]
for box in holes:masked.paste((0,0,0,0),box)
masked.save(v/"edit-target.png")
mapping=dict(canvasGlobalXYWH=[43917,36493,1254,1254],canvasShiftFromOriginalP14XY=[0,-256],originalP14GlobalXYWH=[43917,36749,1254,1254],scale=1,resized=False,rotated=False,realNorthBoundaryY=371,realEastBoundaryX=1139,holesLTRB=holes,sourceRegions=[dict(source="north",cropLTRB=[2957,3725,4096,4096],pasteXY=[0,0]),dict(source="northeast",cropLTRB=[0,3725,115,4096],pasteXY=[1139,0]),dict(source="east",cropLTRB=[0,0,115,883],pasteXY=[1139,371]),dict(source="v8 geometry",cropLTRB=[0,115,1254,998],pasteXY=[0,371])],finalProposalOperation="Map host rows256:1254 to native p14 rows0:998, preserving v8 lower body; native rows958:998 use a 40px cosine compositing return only in the bottom support band which was not erased. Production diagnostic remains6/18/256.")
write(v/"mapping.json",mapping)
for name in ["same-scale-context.png","edit-target.png"]:
 write(str(v/name)+".generation.json",dict(**ref(v/name),operation="Exact native crop/paste and transparent edit holes; no AI art drawn by code.",mapping=mapping,sources=[ref(old/"host-result.png")]+[dict(file=op["file"],sha256=op["sha256"]) for op in records],actualModel=None,actualQuality=None))
prompt="""Use case: precise-object-edit / seamless inpainting.
Image 1 is the EDIT TARGET at exactly 1254 by 1254 native pixels. Fill the transparent L-shaped opening with one continuous painting of the same blue water and lavender stone cliff. The missing opening intentionally crosses former tile boundaries, because the original error was a faint rectangular shading seam. The broad finished region above and the thin finished strip on the far right are authoritative real neighboring artwork. Match their actual restrained flat blue cell color, cyan curved ribbon widths, smooth purple rock material, endpoint placement and tangent. Continue these exact colors through the opening, with no horizontal or vertical shelf, strip of lighting, rectangular color band, glow edge or grid of additional little ripples.
Image 2 is the same shifted crop before erasing, used only to preserve coastline, large curved water-cell placement and rock geography. Its straight horizontal paint change through y371 and vertical change at x1139 are the defects to remove, not physical features. The repair can gently repaint the water-cell interiors to inherit the real surrounding flat blue color; it must not preserve an incompatible interior color merely because Image2 had it. The cliff at the left remains the same partial smooth lavender cliff, with the same silhouette, broad simple planes, narrow pale rim and existing rounded lower coastline. Do not make it rougher or add a rock ledge.
Image 3 is only the approved clean rounded hand-painted style reference; import none of its UI content.
Preserve the exact frame, all object counts, outside geography and native scale. Do not mirror, rotate, zoom, resize or change perspective. Keep all visible opaque surroundings visually unchanged, especially the top actual neighboring water, far right neighboring water and finished bottom support. No white glitter, foam grid, extra objects, leaves, texture noise, text or borders. Fill all transparent parts opaquely and return exactly the same whole picture."""
refs=[v/"edit-target.png",v/"same-scale-context.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")]
call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
(v/"repair.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"repair.call.json",call)
write(v/"repair.request.json",dict(startedAt=datetime.now(timezone.utc).isoformat(),tile="r10_c11",patch="p14",repairWorkCanvas=mapping,configSnapshot=read(HERE/"repair.request.json")["configSnapshot"],prompt=str(v/"repair.prompt.txt"),promptSha256=sha(v/"repair.prompt.txt"),references=[ref(p) for p in refs],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),actualModel=None,actualQuality=None,sourceNative=ref(TILE/"native/p14.png"),priorRepair=ref(old/"host-result.png"),approvedForPromotion=False,nativeFileModified=False))
print(json.dumps(dict(call=str(v/"repair.call.json"),mapping=mapping)))

