import datetime,hashlib,json
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent;R.mkdir(exist_ok=True)
RECOVERY=R.parent;SESSION=RECOVERY.parents[1];ART=SESSION.parents[1];REPO=ART.parent
source=RECOVERY/'full-rect-v3/r08_c07.png';expected='dafa9bf5fbb297b65f68fcce4f39d759e1a1bf3a6b330e20c01487cbfe86fe3b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==expected
box=[1573,1843,2827,3097]
with Image.open(source) as im:im.load();assert im.size==(4096,4096);im.crop(box).save(R/'context-native-1254.png')
style=REPO/'designs/gameplay-ui/04-guild.png'
material=SESSION/'next_tile_r08_c08/correction-20260923T114016880544Z/native-ivory-material-reference.png'
prompt='''Use case: precise-object-edit. Asset: exact-scale native game-map repair patch for the approved original Daoist Q-style city.
Edit reference image 1, an exact unscaled 1254 by 1254 pixel crop from a 4096 city tile. Return exactly the same 1254 by 1254 framing, artwork only. Image 1 is the geometry and pixel-scale authority. Image 2 is the approved project finish reference only (rounded clean material quality), not its UI, text, characters, objects or arrangement. Image 3 is a native clean ivory material reference only.
Repair the artificial compositing discontinuities, with the smallest possible edit. Near local y=600..760, around local x=640..800, the pale vertical rounded frames and the dark inset edges have small unnatural bends and doubled edges left by a mechanical patch return. Make these existing frame contours smoothly continuous through that band, following the trajectories immediately above and below. Also remove the false straight tone division running near local x=475 through a single stone surface; it is a generated 1024-grid seam, not real grout. Preserve genuine stone slab boundaries, carved groove trajectories, gold trims and inset counts. Match the scene's existing clean warm ivory, quiet blue-gray stone, thin polished gold and soft upper-left lighting.
Keep every real ornamental object, border and grout line in exactly the same position, scale, thickness and perspective. No redesigned patterns, no rearrangement, no crop, zoom, tilt, rotation or stretching. The entire outer 160-pixel border is an immutable attachment zone: preserve its original contours, colors and texture as closely as possible, with no movement. Concentrate correction on the inner return band and the visible artificial seam; do not repaint unrelated stone. No cloud stains, cracks, speckle, sharpening halos, new grout, blur, text, UI, labels or borders. The repaired surfaces must have crisp native details with single clean bevel edges, no ghosted or doubled outlines. Highest available host-managed quality; model and quality selectors are not exposed by this tool.'''
request={'prompt':prompt,'referenced_image_paths':[str(R/'context-native-1254.png'),str(style),str(material)],'transparent_background':False}
(R/'prompt.txt').write_text(prompt,encoding='utf-8')
(R/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'config.snapshot.json').write_bytes((REPO/'config/image-generation.json').read_bytes())
refs=[{'file':p,'sha256':sha(p),'role':role} for p,role in zip(request['referenced_image_paths'],['edit_target_exact_native_crop','approved_style_only','native_material_only'])]
(R/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),'sourceSha256':expected,'cropLTRB':box,'cropFile':str(R/'context-native-1254.png'),'cropSha256':sha(R/'context-native-1254.png'),'sourcePixels':[4096,4096],'cropPixels':[1254,1254],'resized':False,'operation':'native_pixel_crop_for_imagegen_repair','sourceRepairRecord':str(RECOVERY/'full-rect-v3/repair.json')}
(R/'context-native-1254.png.derivation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(R/'request.json'),'references':refs},ensure_ascii=False))
