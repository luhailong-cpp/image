from native_work import *
import argparse
ident='r03_c09_p04_01_v2';assert not (ZONE/'guides'/f'{ident}.anchored-layout-only.png').exists()
guide(argparse.Namespace(id=ident,neighbor=['r03_c09_p03_01_v2','r03_c09_p04_02'],base='r03_c09_p04_01'))
d=read(ZONE/'prompts'/f'{ident}.inputs.json');d[1]['role']='UPPER native neighbor left and RIGHT native neighbor right, unscaled'
write(ZONE/'prompts'/f'{ident}.inputs.json',d)
prompt='''Use case: precise-object-edit. Edit Image1 in the exact1254x1254 framing. Fix ONLY the cream wall panel's upper join. Its upper230px strip has just been restored from the actual upper neighbor: keep that strip exact, including the vertical recessed panel molding near the center-left. Continue that precise molding straight downward into the existing wall face, with no sideways step where y230 meets the interior, and match the neighbor at y115. The current deeper interior panel outline incorrectly jumps to the left; repaint only that narrow wall outline so it flows from the upper anchor as one continuous carved recess. Do not invent a second overlapping molding or staircase in the transition. Preserve the broad stone pillar, rightmost230px, the foliage throughout the lower half, every bottom230px pixel and all lower shrub/curb layout. Ivory mottling and fine hand-painted details must transition softly without a horizontal line, no blur.
Image2 left UPPER and right RIGHT neighboring native patches; Images3-5 original map and material style only. Same daylight Daoist Q painting. No new objects, no zoom/crop, no rewriting the garden, no resizing, no text/UI. Opaque native1254x1254.'''
(ZONE/'prompts'/f'{ident}.prompt.txt').write_text(prompt,encoding='utf-8')
p=ZONE/'qa/r03_c09_p03_01_v2__r03_c09_p04_01.json';q=read(p);q.update(status='failed_local_stone_molding_offset',reviewedAtUtc=now(),reviewer='root',observed='Recessed left wall-panel molding shifts left near actual horizontal join; right pillar remains aligned.');write(p,q)
p=ZONE/'qa/r03_c09_p04_01__r03_c09_p04_02.json';q=read(p);q.update(status='passed_internal_only',reviewedAtUtc=now(),reviewer='root',observed='Vertical cream framing and leaves continue through right join.');write(p,q)
print(json.dumps({'id':ident,'prompt':prompt,'references':[x['file'] for x in d]}))

