from pathlib import Path
import sys,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'provenance/run-north'
d,f=sys.argv[1],int(sys.argv[2])
assert d in ('NE','NW','E') and 1<=f<=16
refs=[str(ROOT/f'runtime/run/{d}/01.png'),'D:/work/image/designs/jubaozhai-ui/02-characters.png']
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
phases=[
'RIGHT foot is the leading planted contact foot; LEFT leg extends behind showing the sole, about to lift. RIGHT empty fist is forward with elbow bent; LEFT bow hand is back by left hip.',
'RIGHT knee bends accepting weight, RIGHT boot planted beneath the front of hips; LEFT knee folds behind with raised boot sole. RIGHT empty fist starts lowering from forward; LEFT bow hand begins to swing toward body center.',
'RIGHT boot stays grounded beneath hips with compressed knee; LEFT knee passes underneath and forward, LEFT boot airborne tucked close. RIGHT empty elbow swings back to waist; LEFT bow-side elbow moves forward a little, bow still on same anatomical left.',
'RIGHT leg extends backward to push off on toe, LEFT knee drives forward moderately. LEFT bow arm swings forward from shoulder, RIGHT empty arm swings backward, both elbows bent.',
'First flight: both boots clearly airborne just above virtual ground, LEFT thigh forward with knee bent, RIGHT trailing knee folds behind. LEFT bow forearm is forward and RIGHT empty forearm back, moderate excursion.',
'First flight apex: LEFT thigh advances forward and lower leg extends for landing; RIGHT knee bends behind. LEFT hand with bow reaches forward apex, RIGHT empty hand rear apex. Hips rise 12 px only.',
'Descending first flight: LEFT boot extends forward and down, RIGHT tucked trailing boot swings toward passing. LEFT bow arm begins moving back from front apex; RIGHT empty elbow begins swinging forward.',
'Precontact: LEFT boot approaches virtual ground, LEFT leg extended ahead but knee soft; RIGHT knee folds behind. LEFT bow hand moves closer to left hip and RIGHT empty fist moves forward slightly.',
'LEFT leading foot makes contact, RIGHT leg extends behind showing sole and is about to lift. LEFT bow arm is forward with bent elbow, RIGHT empty arm is back.',
'LEFT knee bends to accept weight, LEFT boot planted; RIGHT knee folds behind with raised boot sole. LEFT bow hand starts lowering from forward; RIGHT empty hand begins to swing toward body center.',
'LEFT boot stays grounded beneath hips with compressed knee; RIGHT knee passes underneath and forward, RIGHT boot airborne tucked close. LEFT bow elbow swings back toward waist; RIGHT empty elbow moves forward.',
'LEFT leg extends backward pushing off on toe, RIGHT knee drives forward moderately. RIGHT empty arm swings forward from shoulder, LEFT bow arm swings backward, both elbows bent.',
'Second flight: both boots airborne just above virtual ground, RIGHT thigh forward with knee bent, LEFT trailing knee folds behind. RIGHT empty forearm forward and LEFT bow forearm back, moderate excursion.',
'Second flight apex: RIGHT thigh advances forward and lower leg extends for landing; LEFT knee bends behind. RIGHT empty hand front apex, LEFT bow hand rear apex. Hips rise 12 px only.',
'Descending second flight: RIGHT boot extends forward and down, LEFT tucked trailing boot swings toward passing. RIGHT empty arm begins moving back from front apex, LEFT bow arm begins swinging forward.',
'Precontact joining frame01: RIGHT boot extends forward down to almost contact, LEFT leg extends back with sole visible. RIGHT empty fist in front near chest, LEFT hand bow behind at hip, both elbows bent. Only a small 30ms advance before frame01.'
]
cam={'NE':'NE back-threequarter facing away toward upper right. Camera-near RIGHT shoulder is same side as RIGHT quiver and its hand is EMPTY; far LEFT arm is partly occluded and holds the bow. Do not interpret the camera-near hand in the idle reference as left.','NW':'NW back-threequarter facing away toward upper left. Camera-near LEFT shoulder and arm hold the bow; far RIGHT arm is EMPTY. RIGHT quiver stays on upper-right back.','E':'E right-facing side view. Near RIGHT arm EMPTY, far LEFT hand carries long bow; quiver remains anatomical right.'}[d]
leg,sep,arm=phases[f-1].partition('. ')
phase=leg.replace('LEFT','TEMP').replace('RIGHT','LEFT').replace('TEMP','RIGHT')+sep+arm
side_lock='For NE bow stays on SCREEN LEFT beside the left hip, and the near hand on SCREEN RIGHT is always EMPTY. Advance far left elbow modestly 15-25 degrees behind body, do not move bow to screen-right or connect it to right shoulder.' if d=='NE' else ''
prompt=f"""Use case: stylized-concept, independent hand-painted run animation sprite.
Inputs: image1 selected running frame01, exact identity camera proportions and real hand ownership; image2 approved STYLE sample only, no UI.
Draw ONLY frame {f:02d}/16, one full character, native 1024x1024 or larger square true transparent RGBA. {cam}
Action phase: {phase}
{side_lock}
Always exactly two arms/hands/legs/boots, bamboo bow in anatomical LEFT hand only; RIGHT hand empty and visibly counter-swings through real shoulder and elbow changes. Preserve same full ornate long green bamboo bow and fine gold string; no drawing the bow, no arrow in hands. Bow follows left wrist, never jumps hands.
Lock image1 head size, body proportions, camera angle, framing and virtual ground plane; only subtle running bob, no horizontal drift or per-frame zoom. Short chibi legs/arms, running lean 8 degrees into travel, detailed white shorts and short ivory/jade boots. Show real opposing thighs, bent knees and ankle push, not walking or standing with frozen upper body. Keep exact brown high ponytail, bamboo leaf jade gold hair ornament, ivory jade gold short robe, quiver on right shoulder, warm bright polished painted material. Tail and ribbons lag smoothly.
Keep entire long bow tips, hair, fingers and toes safely inside at least 30px margins. No floor, no baked shadow, no effects, no text, no grid, no duplicate/ghost limbs. Independently redraw this precise phase, never mirror image1."""
if d=='NE':
    rx,ry=[(830,530),(820,545),(800,570),(775,595),(740,625),(705,655),(680,680),(665,695),(660,700),(665,695),(680,680),(705,655),(740,625),(775,595),(800,570),(820,545)][f-1]
    lx,ly=[(390,565),(395,568),(405,573),(415,580),(430,590),(440,600),(450,610),(460,620),(465,625),(460,620),(450,610),(440,600),(430,590),(415,580),(405,573),(395,568)][f-1]
    prompt+=f' On the normalized 1024 square, RIGHT EMPTY fist must now be near ({rx},{ry}) using an anatomically bent right elbow, LEFT gripping hand near ({lx},{ly}), moving shoulders/elbows naturally. These are approximate gesture guides not translations. The right forearm really changes angle from reference; do not keep reference right fist raised in front for every phase.'
    if 7<=f<=11:
        prompt+=' CRITICAL new arm pose: rotate the RIGHT upper arm backward at shoulder, point right elbow down toward her rear hip. Fold EMPTY RIGHT fist down beside back of waist, overlapping the GREEN ROBE silhouette instead of poking to the right beyond body. The NEAR visible right hand is now BELOW belt, not in front of chest. Make clear forward/back swing, not merely wrist adjustment. This must be visibly different from image1.'
    if 9<=f<=12:
        prompt+=' Opposite leg half-cycle from image1 is essential: the CAMERA-NEAR RIGHT thigh now reaches FORWARD toward upper-right, its boot presents its TOP/HEEL rather than broad sole. FAR LEFT thigh now goes BACK diagonally down-left, its tucked boot shows the SOLE. Near right thigh overlaps in front of far left thigh; do not repeat the exact leg silhouette of image1.'
if d=='NW':
    lx,ly=[(550,620),(530,615),(485,600),(435,580),(390,555),(350,535),(320,530),(305,535),(305,545),(325,560),(355,580),(390,600),(440,615),(480,625),(510,625),(535,620)][f-1]
    prompt+=f' NW LEFT BOW ARM must move continuously: on normalized1024 canvas, near LEFT gripping hand is approximately ({lx},{ly}) rather than copying frame01. Draw actual shoulder and bent elbow rotation to put wrist there. The hand grips the MIDDLE of the longbow, with equal length upper/lower limbs around grip, not its bottom. Keep same longbow ~700px tip-to-tip, near-vertical with only slight20-degree tilt; do not shorten to a small hunting bow. Far RIGHT EMPTY arm swings opposite, changing elbow angle. Preserve same head and body placement as image1.'
override=P/f'override-{d}-{f:02d}.json'
if override.exists():
    custom=json.loads(override.read_text(encoding='utf-8-sig'));prompt=custom['prompt'];refs=custom['references']
if d=='NW':
    refs=['D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/idle/NW.png','D:/work/image/designs/jubaozhai-ui/02-characters.png']
    prompt=f'''Use case stylized-concept. Draw one independent NW run animation frame {f}/16 of this exact Bamboo Archer. Image1 fixes identity, original longbow, camera, scale and head location; image2 is approved painted style only. NW back-threequarter facing away upper-left. Same fullbody chibi proportions, green ivory gold short robe, white shorts/boots, brown ponytail, bamboo-leaf jade-gold hair ornament, quiver on anatomical RIGHT shoulder.
Run phase: {phase}
Weapon carrying constrains LEFT arm swing to a moderate20-degree shoulder/elbow arc: LEFT hand always holds the MIDDLE of original complete LONG bamboo bow on SCREEN LEFT of her torso, bow never crosses her head, quiver or hair ornament. Bow stays near-vertical 700px long, same continuous shaft and two simple gold endcaps/string as reference. Near LEFT shoulder/elbow actually flex; far RIGHT arm is EMPTY, opposite swing. No weapon in right hand, no added arrow. Exactly two hands and feet.
Keep image1 head size and body placement, fixed orthographic camera and virtual ground y940. Lean torso8deg into run. Redraw true alternating knees, support/push/flight and ankle action, not idle legs. Subtle bob under15px, no zoom. Full longbow, ponytail, fingers and boots fit40px margins in1024square native RGBA transparent. No floor/shadow/text/UI/effects, no duplicate bow or ornament. Clear polished handpainted finish. Only one frame, never mirrored.'''
if d=='NW' and f>=10:
    refs=[str(ROOT/'runtime/run/NW/01.png'),'D:/work/image/designs/jubaozhai-ui/02-characters.png']
    prompt+=' Image1 is the selected two-arm running anchor. EMPTY RIGHT hand now swings in FRONT near chest, its upper arm mostly hidden behind torso; no rear right arm or hand remains visible below quiver. Keep exactly these two arms only, never add a rear third sleeve. Actively bend near left elbow back toward side of ribs while still holding full long bow at screenleft. Show shoulder/elbow rotation rather than still idle arms.'
if override.exists():
    custom=json.loads(override.read_text(encoding='utf-8-sig'));prompt=custom['prompt'];refs=custom['references']
attempt=1
while (P/f'run-{d}-{f:02d}-attempt-{attempt}.request.json').exists():attempt+=1
stem=f'run-{d}-{f:02d}-attempt-{attempt}'
args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True}
request={'slot':f'run/{d}/{f:02d}','attempt':attempt,'requestedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,**args},'referenceMetadata':[{'file':x,'sha256':hashlib.sha256(Path(x).read_bytes()).hexdigest(),'role':['identity/camera','style','fixed running continuity anchor'][i]} for i,x in enumerate(refs)]}
path=P/(stem+'.request.json')
path.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'args':args,'request':str(path),'direction':d,'frame':f,'attempt':attempt},ensure_ascii=False))


