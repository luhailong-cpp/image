from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
scenes={
'north-1':'Existing pale paving across upper edge, golden wooden deck planks and cropped front rails below. Remove the horizontal y627 artificial wood-paint split, and the isolated small dark leaf-shadow fragments just BELOW that line on the deck. Maintain the true leaf shadow on stone at top right. Reconnect existing diagonal board grooves with original endpoints; do not add grooves. The left557px are already correct and must remain untouched; work only right of x557.',
'north-2':'Golden diagonal deck boards, pale paving upper left, cropped large stone mooring block with one round hole on right. Remove horizontal y627 color/texture splits through wood planks and stone face and tiny groove steps. Keep stone hole, bevels and object shadows exactly the same. No new stone joint lines.',
'north-3':'Large pale stone block with rounded top cap and existing side/front bevel, golden wood upright right of block, green leaves to right, pale curb and paving below, cropped small stacked stone foreground. Remove horizontal y627 palette split through stone, post, leaves and curb. Remove the spurious vertical groove at x255 below y627 on the big stone SIDE face: that is one continuous stone face, the only true vertical side/front bevel is at x315. Preserve top cap joint, every other existing contour and leaf count.',
'north-4':'Green broad leaves and pointed leaves behind two existing wood uprights, pale curb and paving below, blue water behind. Remove the artificial horizontal y627 material split, reconnect interrupted leaves and wood-paint seamlessly while maintaining original leaf count, shapes and post edges. No new leaves, no denser foliage, no new post joint or groove.'
}
for n,s in scenes.items():
 h.O=O/'north'
 p='Use case: native two-tile seam inpainting. Image1 exact1254px combined north/south source, shared boundary y627. Image2 approved PRIMARY style reference only, no UI. '+s+' Repair the narrow seam and needed connected outlines, preserve the rest of composition, scale, crop, object count and natural endpoints. Bright clean rounded Taoist Q handpainting, crisp native painted details. No text, object addition, grain, blur, enlarged geometry, global recoloring or sharpening halo. Output exactly1254x1254.'
 h.savecall(n,p,[h.O/(n+'-source.png'),h.STYLE],['exact native627+627 two-tile joint source','actual approved style04guild'])
