from pathlib import Path
import json, hashlib
import archive_generation as archive

root=archive.IMAGE_ROOT
work=Path(__file__).parent/'work-idle-final'
work.mkdir(exist_ok=True)
hashes={}
for direction in ['N','NE','E','SE','S','SW','W','NW']:
    old=root/f'qdao_original_roster_v13/candidate/06_thunder_caster_boy/idle/{direction}.png'
    hashes[direction]=hashlib.sha256(old.read_bytes()).hexdigest()
if not (work/'old-idle-sha256-before.json').exists():
    (work/'old-idle-sha256-before.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')

def prepare(direction):
    refs=[str((root/f'qdao_original_roster_v13/candidate/06_thunder_caster_boy/idle/{direction}.png').resolve()),str((root/'qdao_original_roster_v13/references/06_thunder_caster_boy/original-identity-1024.png').resolve()),str((root/'designs/jubaozhai-ui/02-characters.png').resolve())]
    view={'N':'straight rear view, facing away from viewer; no face visible','NE':'rear three-quarter view facing upper-right','E':'right side profile, facing right','SE':'front three-quarter view facing lower-right','S':'straight front view facing viewer','SW':'front three-quarter view facing lower-left','W':'left side profile, facing left','NW':'rear three-quarter view facing upper-left'}[direction]
    prompt=f'''Use case: identity-preserve. Asset: a single independent IDLE sprite for the Chinese Daoist chibi game 五行奇谈, character 06 thunder caster boy, direction {direction} ({view}).
Input image 1 is the EDIT TARGET and strict idle pose/camera/silhouette reference. Image 2 is identity, costume and prop detailing only, never its pose. Image 3 is the user-confirmed PRIMARY ART STYLE reference: clear bright refined hand-painted Daoist chibi rendering and softly rounded volumes; do not copy its UI, people, scenery or text.
Restore image 1 as fresh high-resolution clean hand-painted artwork, preserving its exact idle standing pose, facing direction, proportions, silhouette, head/hair silhouette, costume layers, expression where visible, gold thunder motifs, warm brown hair and tied gold ribbons, white/ivory gold-bordered robe, dark navy trousers, gold-black shoes, turquoise ornaments, hand anatomy, gold talisman and gold ritual staff, their correct hands and orientation. Both feet remain firmly planted in the same stable resting stance as image 1. Do not turn this idle into walking or stepping. Do not move arms or props. Do not transfer image 2's pose.
Essential correction: thoroughly REMOVE all fluorescent magenta/red-purple chroma fringe and spill from the outer silhouette, inner gaps, hair tips, robe edges, gold ornaments and staff. Reconstruct crisp natural hair/gold/cloth edges with correct local material colors and smooth antialiasing into transparent alpha. Preserve actual dark navy cloth and intentional golden/turquoise ornaments. Image 2 also contains contamination: never copy its pink/purple edge defects. Redraw real sharp detail at native resolution, not a blurred upscaled 512 raster or sharpened pixels. Keep the same costume design and clean softly lit hand-painted material language as the supplied confirmed style. No new rim glow, no purple halo, no noise.
Output exactly ONE complete centered full-body character on a square genuinely transparent RGBA canvas, native dimensions at least 1024x1024 (1254x1254 is suitable). Character's highest hair tip near y=6% and feet lowest edge near y=94%, all head/hair/ribbons/staff and shoes fully inside canvas with generous lateral safety margin. Match image 1's visual body proportions, both feet stable and visible as in target. No sprite sheet, no comparison, no labels, no extra characters, no crop. Transparent empty background with no color matte, checkerboard pixels, ground, contact shadow or glow.'''
    return archive.prepare(f'idle-{direction}-edge-final-v1',prompt,refs)

if __name__=='__main__':
    import sys
    print(json.dumps(prepare(sys.argv[1]),ensure_ascii=True))
