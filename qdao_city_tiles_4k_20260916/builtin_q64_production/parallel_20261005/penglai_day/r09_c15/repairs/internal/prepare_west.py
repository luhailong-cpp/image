import sys
sys.dont_write_bytecode=True
import ai_helper as h
O=h.O
issues=[
'At x627 the old/new tile boundary leaves a sharp water color strip and a false pale vertical rock spike on its right, spanning approximately x627..745,y260..950. Remove that pasted-edge artifact: the turquoise foamy water channel should continue naturally between the existing tall left cliff and the separate leafy rock on the right. Preserve the left cliff silhouette, the right rock and all plants. Make the bottom golden diagonal rail continuous in bevel and grain across x627, with no physical joint at that guide line.',
'At x627 the tile boundary makes a vertical tonal band and a little step across both diagonal golden rails. Reconstruct continuous clean rail bevels, the same existing ivory/coral hanging cloth edges and motifs, and the existing foliage. The old anchor-strip boundary is not a physical seam. Preserve the large rope-bound vertical post and its shape at left.',
'At x627 the tile boundary causes a vertical material strip, a rail-top step, and color discontinuity across the existing wood rail, leaves and stone floor. Remove only that pasted boundary and reconnect the identical existing rails, planter edge, stone tile grooves and leaf silhouettes, keeping their exact count and geometry.',
'At x627 the tile boundary causes small stairsteps in the two diagonal pale stone bevels and lower golden wooden rail. Reconnect these as smooth straight continuous edges with the same perspective, and remove the vertical floor color band. Preserve every existing groove, paving slab, round finial and shadow.'
]
for i,issue in enumerate(issues,1):
 n=f'west{i}-ai-v1';inp=O/f'west-joint-source-{i}.png'
 prompt='Native1254x1254 seamless map editing. Image1 is actual joint from two neighboring native game-map tiles; its central x627 vertical line is an artificial tile/guide boundary, never a physical object. Image2 is actual approved painting style, no UI. Repair only a narrow band x450..830 spanning full image height: '+issue+' Preserve exact camera, scale, crop, counts and lighting. Bright rounded clean Taoist Q painting, existing materials. Outside the repair band keep the original unchanged. No new items, text, denser foliage, extra shadow, blur, noise or rescaling. Output exactly1254x1254 pixels.'
 h.savecall(n,prompt,[inp,h.STYLE],['actual1254 native western two-tile joint crop','actual approved style04-guild'])
