"""r11_c16 native art and exact-context recording."""
import sys
import production_r09_c16 as common
common.p.T=common.p.ROOT/'r11_c16'
common.p.status=common.status

def structure():
 p=common.p
 if (p.T/'guides/local-structure.png').exists():raise ValueError('Preserve existing structure')
 prompt='Use case: precise-object-edit. Edit IMAGE1 only. It is an exact crop of an existing isometric fishing village. IMAGE2 is the approved bright rounded hand-painted Q-style material reference only. Keep this exact view, camera, crop, coordinates and all silhouettes. The broad center is cyan water. At upper-left preserve the clipped warm wooden landing platform, its existing dark support and pale contact rim; retain the clipped timber feet at the top edge exactly. The bottom edge is the existing diagonal warm plank pier with its four large existing upright round wooden posts and clipped left-edge post, two existing pale rope rails connecting them, their rope bindings and their cast shadows. Preserve all shapes, their individual heights, widths, location, cropped endpoints and gaps exactly. Do not complete anything that is cut off by an image edge. Clarify the existing planks and rounded timber using clean controlled hand-painted shading with warm golden highlights. Preserve genuine pale contact rings around the pictured upper supports. Elsewhere the cyan water stays quiet with broad low-contrast color gradients; remove distracting generic ripple scribbles, foam cells and grain. No new object, pier, post, rail, rope, plank joint, shore or decoration. No text, characters, UI, borders, zoom, crop or scene redesign. One opaque native1254x1254 square. This is a local structure reference only; never enlarged final game pixels.'
 common.save_prompt('local-structure',prompt,p.T/'guides/local-layout.png','edit target: reference-only exact crop of confirmed shared layout')

def prepare(r,c):
 target=common.guide(r,c)
 prompt='Use case: precise-object-edit. Edit IMAGE1 only. This is an exact native-pixel crop of a bright rounded Q-style fishing village. IMAGE2 is material style reference only, not composition or objects to add. Preserve every existing material silhouette, position, dimension, cut-off endpoint, shadow and color placement. Clarify only the existing wood, post, rope or contact highlight actually visible. A timber cut off by a picture edge continues outside the image: do not cap it, shorten it or create a new waterline. Do not complete cropped objects or invent new pier, post, rope, joint, ornament or shore. Actual neighboring native strips at the edges are geometry and hue anchors; continue the interior to them, eliminating artificial straight strip boundaries. Open cyan water is intentionally simple, with a quiet broad smooth low-contrast color field and no new linework, waves, foam, cells, dots, grain or bright streaks. If there is only water, output only water. Preserve genuine existing contact highlights and directional shadows. Round substantial timber, controlled clean edges, warm hand-painted surfaces. No text, UI, border, zoom, crop, blur filter or photoreal texture. One opaque native1254x1254 square at highest available finish.'
 if r==1:prompt+=' The top115 pixels are fixed actual NORTH context; preserve all geometry endpoints and hues exactly.'
 if c==4:prompt+=' The rightmost115 pixels are out-of-map continuation context, excluded from final core. Never draw a boundary.'
 common.save_prompt(f'r{r:02d}_c{c:02d}',prompt,target,'edit target: exact structure crop and verified actual neighboring native intersections')

if __name__=='__main__':
 command=sys.argv[1]
 if command=='prepare-structure':structure()
 elif command=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
 elif command=='record':common.p.record(sys.argv[2],sys.argv[3])
 elif command=='bind-neighbor':common.bind_neighbor(sys.argv[2],sys.argv[3],sys.argv[4])
 elif command=='status':common.status()
