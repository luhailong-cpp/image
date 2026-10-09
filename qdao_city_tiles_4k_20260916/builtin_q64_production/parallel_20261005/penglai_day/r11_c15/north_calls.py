from pathlib import Path
import sys
R=Path(__file__).resolve().parent;O=R/'repairs/north'
sys.path.insert(0,str(R/'repairs/internal'));import ai_helper as h
h.O=O
scenes=[
'Golden rope railing and rectangular wooden posts on a dock over turquoise water. At y627 the large left-middle post has an abrupt paint cut and slight side-outline step, water wave caustics also have a horizontal color change. Repair these into continuous coherent painting. Preserve post silhouette, wood grain, rope twist count and every deck groove. Do not add any cross joint at y627.',
'Upper gold sail yard and lower-left cropped dock post over blue water. The cream sail left outline at x770 has a small artificial kink at y627 and cream folds jump in palette there. Continue the same sail outline and existing folds; remove the horizontal water and sail color split. Keep real edge fasteners and yard connections exactly as present.',
'Large ivory folded sail, vertical golden mast with one real collar at y590, diagonal wooden yard. There is an artificial horizontal seam at y627 with offset mast contour and cloth folds. Preserve the REAL rounded mast collar and connect the shaft directly beneath it smoothly, matching shaft width and highlights to existing endpoints. Keep existing fabric fold count; remove abrupt rectangular fold-tone patches at right around x1050..1200. Diagonal yard remains straight.',
'Ivory sail with dark golden edge left, wooden pier pile and its water reflection right. Remove horizontal y627 patchwork through the sail and water reflection, connecting exact existing fabric folds and edge contour smoothly. Keep real wooden pier pile, its current reflection shape and wave crests. No added fabric folds or changed silhouette.'
]
for i,s in enumerate(scenes,1):
 n=f'north-{i}';prompt='Native two-tile shared boundary repair. Reference1 is exact1254x1254 with the existing horizontal shared boundary y627. '+s+' Work in a narrow band around y627 with any small necessary connected contour adjustment. Preserve outer200px top and bottom, composition, scale, object counts, camera and all genuine construction joints. Reference2 is the actual approved style: bright clean rounded Taoist Q-game handpainting only; no UI elements. Sharp native detailed painting, no blur, no global recoloring, no added lines or objects, no rescale. Output exactly1254x1254.'
 h.savecall(n,prompt,[O/(n+'-source.png'),h.STYLE],['exact native627north+627south source union','actual approved style04guild'])
