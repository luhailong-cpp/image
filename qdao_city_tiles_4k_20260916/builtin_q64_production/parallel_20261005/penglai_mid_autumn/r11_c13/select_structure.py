from prepare_structure import *
src=R/'structure-canopy-corrected.png'
plan=read(F/'plan.json');plan.update(nightStructure=str(src),structureSha256=sha(src),stage='structure_preparing_guides_for_root_review',rootReviewPending=True,nativePatchCount=0)
plan['nativePatchConstraints']={
'p11':'True north canopy cloth, left edge, stripe endpoints and left post position override planning interpolation. Preserve same blue canopy, no stacked fabric/paste band; real N top115 pixels must flow into newly painted detail.',
'p12':'Preserve corrected single continuous canopy and pale stripe; actual N endpoint/hem tangent and width are authoritative. Do not recreate the previous white stripe side jump or horizontal fabric splice. Retain same stall/support count and footprint.',
'p13':'Continue real north native wooden upright and diagonal rail exactly, including both rail edges and their thickness; align same quay masonry plane and existing timber water post. Planning approximates paint detail; no new post or change of attachment.',
'p14':'Continue the exact real north wall waterline, fender edge and water ripples. Blend existing reflection color naturally at boundary without a horizontal warm-color band; no extra light source or new wave geometry.'}
write(F/'plan.json',plan);print(src)
