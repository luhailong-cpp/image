from native_work import *
import argparse
ident='r03_c09_p02_02_v2'
assert not (ZONE/'guides'/f'{ident}.anchored-layout-only.png').exists()
guide(argparse.Namespace(id=ident,neighbor=['r03_c09_p01_02_v3','r03_c09_p02_03'],base='r03_c09_p02_02'))
p=ZONE/'prompts'/f'{ident}.inputs.json'
d=read(p);d[0]['role']='edit target: current complete native candidate with exact upper and right overlaps restored; only correct seam material continuity'
d[1]['role']='native neighbor reference plate left-to-right UPPER then RIGHT; no resizing'
d[3]={'file':(ZONE/'guides/r03c09-context-layout-only-20261016.png').as_posix(),'sha256':sha(ZONE/'guides/r03c09-context-layout-only-20261016.png'),'role':'original map layout context ONLY, no final art pixels'}
write(p,d)
prompt='''Use case: precise-object-edit. Edit Image1 as one opaque native1254x1254 map patch. Keep exact framing, all current ivory wall, stone posts, plants and paving layout. Fix only its right overlap seam: the right230px now contains the exact native right neighbor, a hard material transition at x1024. Repaint the transition naturally through the nearby interior while retaining all contour crossings at x1139 and preserving the rightmost115px. Match the larger irregular stone mottling, pale cyan/ivory tone, sharpness and leaf shapes in the right strip. Large diagonal slab grout lines and individual leaves must continue across x1024 and x1139 without a straight dividing line, cut-off leaves, duplicate branches or changes in slab scale. Preserve upper230px and the entire left half architecture exactly; do not add or move any post or wall. Image2 left half UPPER neighbor, right half RIGHT neighbor. Image3 full original layout; Image4 cropped original-layout context only; Image5 painting style only, no UI/night/people. Daylight Daoist Q hand-painted map, native fine paint details, no blur/no resizing/no framing changes. Output1254x1254 opaque.'''
(ZONE/'prompts'/f'{ident}.prompt.txt').write_text(prompt,encoding='utf-8')
q=read(ZONE/'qa/r03_c09_p01_02_v3__r03_c09_p02_02.json');q.update(status='passed_internal_only',reviewedAtUtc=now(),reviewer='root',observed='Direct1:1 upper join preserves curb, foliage and grout.');write(ZONE/'qa/r03_c09_p01_02_v3__r03_c09_p02_02.json',q)
q=read(ZONE/'qa/r03_c09_p02_02__r03_c09_p02_03.json');q.update(status='failed_material_and_leaf_continuity',reviewedAtUtc=now(),reviewer='root',observed='Straight texture density difference at exact core join; a few leaf edges interrupted.');write(ZONE/'qa/r03_c09_p02_02__r03_c09_p02_03.json',q)
print(json.dumps({'id':ident,'prompt':prompt,'references':[x['file'] for x in d]}))

