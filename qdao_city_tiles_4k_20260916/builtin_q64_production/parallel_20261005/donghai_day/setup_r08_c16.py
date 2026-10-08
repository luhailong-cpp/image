from pathlib import Path
import json,hashlib

R=Path(__file__).resolve().parent
T=R/'r08_c16'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for src,dst in [('production_r08_c15.py','production_r08_c16.py'),('assembly_r08_c15.py','assembly_r08_c16.py')]:
    target=R/dst
    assert not target.exists(),target
    s=(R/src).read_text(encoding='utf-8').replace('r08_c15','r08_c16').replace('r08_c14','r08_c15').replace('c14-c15','c15-c16').replace('57344','61440')
    target.write_text(s,encoding='utf-8')
prompt='''Use case: precise-object-edit. Repaint IMAGE 1 only as a clean bright rounded Daoist chibi fishing-village STRUCTURAL REFERENCE, tile r08_c16 plus context for 五行奇谈. This is not final HD art. Preserve the exact overhead-isometric camera, framing, scale, every existing silhouette, footprint, rigging direction, hull outline, rope and daylight shadow.
The existing cropped wooden fishing-boat bow occupies the left and lower-center, with warm brown planks, dark teal-blue upper hull band, an open deck containing the existing pale gray bundled net shape, a tall cropped wooden mast, crossing spars and taut rigging. Keep the single red-orange hanging lantern near lower-left and the small capped post at the bow in their existing places. Calm bright blue/cyan harbor water fills the right and upper areas. Repaint only these already-pictured structures; no added objects. Preserve the exact boat-water contact contour and its restrained thin highlight.
IMAGE 2 (04-guild) is the PRIMARY user-confirmed rendering and material style only: precise controlled hand painting, rounded full shapes, clean silhouettes, warm bright daylight, broad quiet wood shading and restrained highlights. No UI content. ALL water must remain quiet broad soft blue/cyan color fields with sparse low-contrast transitions, no bright white or pale cyan netlike caustic lines, no foam web, no busy repeating ripple cells. Do not enlarge boat contact highlight into waves.
This is the map east boundary: the narrow extra right-edge context extends only existing open water and will be cropped out of the final core. Fill the entire square with pictured scene and water, without black, transparent or blank margins. No extra boats, cargo, lanterns, flags, roofs, posts, plants, people, lettering or symbols. No zoom, rotation, crop, grain, cracks, photoreal texture, blur, sharp microtexture or plastic reflection. This structural reference does not claim native west-neighbor alignment, navigation acceptance or final pixel coverage. Return one opaque 1254x1254 image at highest available visual finish.'''
refs=[{'file':str(T/'guides/local-layout.png'),'sha256':sha(T/'guides/local-layout.png'),'role':'edit target, enlarged confirmed layout guidance only including clamped 115-pixel out-of-city water halo'}, {'file':str(R.parents[3]/'designs/gameplay-ui/04-guild.png'),'sha256':sha(R.parents[3]/'designs/gameplay-ui/04-guild.png'),'role':'primary confirmed style and materials only; no UI'}]
(T/'prompts/local-structure.txt').write_text(prompt,encoding='utf-8')
(T/'prompts/local-structure.references.json').write_text(json.dumps(refs,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'name':'local-structure','prompt':prompt,'references':[x['file'] for x in refs]}))
