from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import archive_generation as archive
BASE=HERE.parents[3]
GEN=HERE.parent.parent/'06-generation'
base=json.loads((GEN/'NW06-single-v1/request.json').read_text())['prompt']
base=base[:base.index('POSE NW06')]+ '{POSE}\n'+base[base.index('Ensure the two legs'):]
base=base.replace('REFERENCE2 and REFERENCE3: original native key poses before and after the requested phase; strongest camera, costume, scale and leg-ownership references.', 'REFERENCE2: established NORTHWEST idle, camera guide only. REFERENCE3 and REFERENCE4: original native key poses around the requested phase; strongest scale and leg-ownership references.')
base=base.replace('REFERENCE4: approved Jubaozhai','REFERENCE5: approved Jubaozhai')
poses={
7:('RIGHT late reach: LEFT foot remains planted, shin nearly straight and heel just starting to rise. RIGHT thigh at screen-right hip is moving forward AWAY from viewer; RIGHT boot lowers toward distant ground, knee opens, sole mostly disappears, its boot bottom remains above planted left sole. Distinct phase halfway between NW05 and NW09.',5,9),
8:('RIGHT pre-contact: RIGHT knee nearly straight, right boot from screen-right hip extended AWAY and UPPER LEFT, just above its farther ground landing spot. LEFT foot trails lower on screen-left with heel raised and toe still supporting. Almost NW09 but right heel is still airborne and left heel less high.',5,9),
10:('RIGHT loading: RIGHT boot screen-right/distant has landed flat and bears weight; RIGHT knee slightly flexed. LEFT trailing boot screen-left/nearer pushes on toe, heel raised and sole partly visible; left knee starts bending. Distinct from NW09 contact, prepare to lift left foot.',9,13),
11:('RIGHT midstance with LEFT toe-off: RIGHT boot screen-right/center planted solidly beneath the torso, RIGHT leg takes full weight. LEFT leg screen-left bends backwards at knee; left toes have just left ground, left boot heel raised with some sole showing. The left boot is still a little lower than in NW13. Left leg must not become the weightbearing leg.',9,13),
12:('LEFT passing: RIGHT leg screen-right supports body vertically, RIGHT sole flat lowest. LEFT thigh from screen-left hip comes forward away-left, LEFT knee bent, LEFT boot tucked upward behind lower robe around shin height, clearly airborne, two distinct knees. Between NW11 toe-off and NW13 lifted swing.',9,13),
14:('LEFT early reach: RIGHT foot screen-right stays planted. Elevated LEFT thigh from screen-left hip starts opening knee and extending the boot AWAY toward upper-left. Left boot slightly farther forward and lower than NW13, still airborne. Same leg ownership as NW13; not right foot lifted.',13,1),
15:('LEFT late reach: RIGHT foot screen-right remains supporting, heel begins to rise. LEFT knee opens farther, LEFT boot descends toward farther ground on screen-left, boot sole mostly hidden, lower than NW14 but still above right support sole. Prepare exact opposite contact NW01.',13,1),
16:('LEFT pre-contact: LEFT leg screen-left reaches away upper-left with knee nearly straight, LEFT heel just above distant landing spot; RIGHT leg screen-right trails toward lower-right with heel raised and toe supporting. Lead directly into NW01 left heel contact without changing camera, head or prop dimensions.',13,1)}
for n,(p,before,after) in poses.items():
    batch=f'NW{n:02d}-single-v1'
    refs=[BASE/'qdao_original_roster_v13/candidate/06_thunder_caster_boy/portrait.png',BASE/'qdao_original_roster_v13/candidate/06_thunder_caster_boy/idle/NW.png',GEN/f'NW{before:02d}-single-v1/raw.png',GEN/f'NW{after:02d}-single-v1/raw.png',BASE/'designs/jubaozhai-ui/02-characters.png']
    req=archive.prepare(batch,base.replace('{POSE}',f'POSE NW{n:02d} {p}'),refs)
    print(batch)
