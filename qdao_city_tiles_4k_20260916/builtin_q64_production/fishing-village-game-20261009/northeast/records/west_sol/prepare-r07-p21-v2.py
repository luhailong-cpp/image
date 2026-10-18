import sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
p='r07_c11_p21';v='v2';src=w.Z/f'native/{p}-v1-west_sol.png';d=w.read(w.R/f'{p}-v1.plan.json')
refs=[w.ref(src,'PRIMARY EDIT TARGET: remove premature pedestal')]+w.mandatory()
prompt="""Edit IMAGE1 only. A single precise correction: REMOVE ALL of the stepped bronze pedestal at the bottom y1040..1254. The existing straight bronze vertical post x710..929 must keep its current shaft width and continue vertically OUT THROUGH THE BOTTOM image edge, with NO plinth, foot, widening, shoulder or base visible anywhere in this frame. Its real base is another 600 pixels below this crop. Replace only the removed pedestal outside the shaft with the same continuous pale-gray diagonal paving stones and correct cast shadow. Preserve all other pixels and contours: lantern bottom, gold rim, red tassel, top230 and right230 native edge anchors, stone geometry and lighting. Do not fit a complete object in the square or move/scale the post. Images2/3/4 are map/material/DaoistQ style reference only. Opaque native1254x1254, r07_c11_p21 world[40845,25485,42099,26739], core[115,115,1139,1139], halo115."""
d.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(src),guidePurpose='Native localized removal of prematurely introduced lamp pedestal',previousCandidate=w.ref(src),formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',d);(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{p}-v1.review.json',dict(native=w.ref(src),reviewedAtUtc=w.now(),status='not_selected_layout_error',issues=['Premature bronze pedestal at y1040..1254; shaft should continue through bottom to actual row3 base'],formalAccepted=False))

