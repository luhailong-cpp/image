from prepare_repair import *

target=HERE/'actual-context-target.png';masked=HERE/'repair-edit-target.png'
assert not masked.exists()
im=Image.open(target).convert('RGBA')
holes=[[0,115,1139,371],[883,115,1139,1254]]
for box in holes:im.paste((0,0,0,0),tuple(box))
im.save(masked)
write(str(masked)+'.generation.json',{**ref(masked),'operation':'mechanical alpha holes over exact real-context target; no drawn pixels','source':ref(target),'transparentRepairRectsLTRB':holes,'outputMustBeOpaque':True,'actuallyViewed':False})
prompt='''Use case: precise-object-edit. Repair the missing L-shaped area in Image1, a 1254x1254 native game-map fragment. Return exactly 1254x1254, fully opaque. Do not zoom, crop, rotate or mirror.
Image1 is the edit target. Its transparent region is the only area to paint: the horizontal area x=0..1138, y=115..370 and the right-side vertical area x=883..1138, y=115..1253. The visible pixels are fixed authoritative surroundings. Preserve every visible rock, water cell, wave branch and highlight position. The whole visible upper 115 rows and far-right 115 columns are actual neighboring artwork and must remain unchanged.
Fill the transparent L as one continuous hand-painted scene. At the top edge, continue the exact incoming pale violet rock face and its thin rim downwards with a smooth consistent rock silhouette, eliminating the former abrupt rock step. Continue each broad cyan water-wave band crossing the top and right hole edges with the SAME positions, widths, colors and smooth curved tangents. Connect them organically to the existing water shapes on the lower and left edges of the holes. There must be no horizontal or vertical line, tinted rectangle, pasted strip, shelf or sudden switch in water-cell scale at any edge of the repair.
Image2 gives the full same-frame context with the defective old core. Use it only for the existing overall composition and the unchanged visible interior. Its straight top/right splice lines, stepped rock and mismatched wave endpoints are defects to replace inside the hole, never features to copy. Image3 shows the actual upstream northern rock and broad cyan wave drawing at native pixel scale. Image4 shows the actual eastern water and tiny cropped leaf at native scale. Their native boundary color, broad water ribbons and contour character are authoritative; do not replace them with new thin glittery foam, invent another wave grid or introduce more foliage.
Image5 is the approved clean, rounded Daoist chibi hand-painted style reference only; add none of its objects or UI. Keep the cobalt/azure nighttime water, lavender rock and controlled cyan highlights already present. Preserve the existing cropped rock and all interior/lower/left composition. No new objects, text, stars, bubbles, extra foam, borders, noise, blur or sharpened outlines. Only fill the missing areas, matching the surrounding native scene without retaining any straight splice boundary.'''
refs=[masked,target,HERE/'actual-north-focus.png',HERE/'actual-east-focus.png',Path('D:/work/image/designs/gameplay-ui/04-guild.png')]
call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
(HERE/'repair.prompt.txt').write_text(prompt,encoding='utf-8')
write(HERE/'repair.call.json',call)
write(HERE/'repair.request.json',dict(startedAt=datetime.now(timezone.utc).isoformat(),tile='r10_c11',patch='p14',purpose='Repair real N/E incoming contour joins; proposal only, no native promotion',configSnapshot=read(TILE/'native/p14.png.generation.json')['configSnapshot'],prompt=str(HERE/'repair.prompt.txt'),promptSha256=sha(HERE/'repair.prompt.txt'),references=[ref(p) for p in refs],submittedParameters=dict(model=None,quality=None,**call),actualModel=None,actualQuality=None,sourceNative=ref(TILE/'native/p14.png'),transparentRepairRectsLTRB=holes,approvedForPromotion=False))
print(json.dumps({'call':str(HERE/'repair.call.json'),'promptSha256':sha(HERE/'repair.prompt.txt')}))
