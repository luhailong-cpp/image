"""Native r10_c16 recording and exact-neighbor guides."""
import sys
import production_r09_c16 as common
common.p.T=common.p.ROOT/'r10_c16'
common.p.status=common.status
def structure():
 p=common.p
 if (p.T/'guides/local-structure.png').exists():raise ValueError('Preserve existing structure')
 prompt='Use case: precise-object-edit. IMAGE1 is a reference crop of an existing isometric fishing-village pier, and IMAGE2 is the approved bright rounded hand-painted Q-style material reference. Repaint this exact crop clearly while retaining the precise composition, camera, crop, overall silhouettes and coordinates. Preserve the warm wooden walkway and its diagonal sides, every existing vertical round timber piling and crossbar, the existing rope bindings and sagging rope rails, the open top barrel/bucket near upper-left with its pictured blue-white contents, the clipped blue-white hanging float above it, the dark/blue fishing net or basket partly hidden between the front timbers, the cropped gray stone steps along the far left, and the small wooden platform clipped by the bottom edge. Do not relocate, straighten into a new layout, add, remove or multiply any support, plank joint, rope, bucket, float, net or step. Preserve existing pale contact rings around posts, ground shadows and gaps through the railings. The broad right-side cyan water must stay quiet and clean with gentle broad color gradients; no additional foam, grids, caustic cells or ripple scribbles. Round substantial edges and clean hand-painted timber shading, warm golden wood, tidy materials, same scale. No text, characters, UI, borders, zoom, crop, scene redesign or photoreal noise. Output one opaque native1254x1254 square. This image is local structural guidance only, never enlarged final game pixels.'
 common.save_prompt('local-structure',prompt,p.T/'guides/local-layout.png','edit target: reference-only crop of confirmed shared layout')
def prepare(r,c):
 target=common.guide(r,c)
 prompt='Use case: precise-object-edit. Edit IMAGE1 only into a clean native-pixel crop of a bright rounded hand-painted Q-style fishing village. IMAGE2 is the approved primary style and materials reference only. Keep exactly the same view, camera, crop, object positions, dimensions, silhouettes, shadows and color placement. Clarify only the existing wooden planks, round timbers, rope bindings, stone steps, float, bucket or net actually pictured; add no new objects, duplicate supports, rope strands, plank joints or decorations. Existing crisp edge strips come from actual neighboring native images: preserve their geometry and hues, continue the soft interior precisely into those strips without a straight boundary. Preserve real pale contact highlights around supports and their existing cast shadows. Quiet water remains broad soft cyan-blue tonal fields, with no added ripple linework, foam, dots, lattice, cells, grain or bright streaks. Preserve already pictured object contact highlights; they are not unwanted water detail. Clean controlled edges, round substantial volumes, warm timber, consistent directional light. No labels, text, characters, UI, border, new marks, blur filter, crop or zoom. One opaque native1254x1254 square image at highest available finish.'
 if r==1:prompt+=' The top115 pixels are fixed actual NORTH context. Keep all their existing parts and locations, and join to their exact endpoints.'
 if c==4:prompt+=' The outer right115 pixels are continuation context beyond the map, excluded from final core; do not add a border.'
 common.save_prompt(f'r{r:02d}_c{c:02d}',prompt,target,'edit target: exact reference field with verified actual native neighbor intersections')
if __name__=='__main__':
 command=sys.argv[1]
 if command=='prepare-structure':structure()
 elif command=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
 elif command=='record':common.p.record(sys.argv[2],sys.argv[3])
 elif command=='bind-neighbor':common.bind_neighbor(sys.argv[2],sys.argv[3],sys.argv[4])
 elif command=='status':common.status()
