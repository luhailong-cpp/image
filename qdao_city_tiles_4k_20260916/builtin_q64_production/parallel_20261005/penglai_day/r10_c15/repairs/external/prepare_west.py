from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
scenes={
'west-1':'Existing harbor posts, rails, diagonal braces, edge beam and blue stone wall behind. Remove artificial vertical x627 split below y557: connect lower beam contours and highlights, diagonal brace strokes and stone-wall joints with exact existing endpoints. Keep true post collars and rope knots. The top557px are already repaired and protected: only work below y557. Do not invent new stone joints or sharpen wall detail.',
'west-2':'Existing two wooden harbor piles, left one with existing lower water/refraction sleeve; diagonal front brace, blue stone quay wall and under-pier water. Repair vertical x627 tone split and small contour steps through brace, wall base waterline and broad water waves. Preserve exact support geometry, existing foot water rings and reflections. The difference in left/right pile paint is natural lighting; do not recolor whole objects.',
'west-3':'Only broad blue-to-turquoise water, two broken vertical wooden-pile reflections entering from top, and large rounded caustics. Join the interrupted bright curves and remove the straight vertical x627 palette divide. Keep the original wave positions, count and cell scale, no extra wavelets or objects.',
'west-4':'Turquoise water with broad caustics behind one golden twisted rope, its existing bound square post at lower left-center, cropped second post lower right, wooden deck corner below. Repair straight vertical x627 water tone split and small rope contour/twist mismatch where it crosses the seam. Keep exact rope twists and endpoints, post count, rope knots and deck board grooves. No denser waves.'
}
for n,s in scenes.items():
 h.O=O/'west';p='Use case: native two-tile seam inpainting. Image1 exact1254px combined west/east source, shared boundary x627. Image2 actually attached approved PRIMARY style reference only, no UI. '+s+' Repair locally while preserving all existing composition, scale, crop, natural edge endpoints and object count. Bright clean rounded Taoist Q handpainting. No added objects, text, grain, blur, enlarged geometry or sharpening halos. Output exactly1254x1254.'
 h.savecall(n,p,[h.O/(n+'-source.png'),h.STYLE],['exact native627+627 two-tile joint source','actual approved style04guild'])
