"""Create per-frame textual plans only; no image generation or canonical writes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CHAR='06_thunder_caster_boy'
phases=[
('right_contact','The anatomical RIGHT boot has just reached its forward extreme and touches the ground heel-first. The anatomical LEFT leg trails well behind, with only its toe at the last push-off point. A clearly split right-leading step, not a neutral standing stance.'),
('right_loading','The anatomical RIGHT front boot rolls from heel onto its sole and accepts the weight with a softly bent knee. The trailing LEFT heel is raised, its toes still touching at push-off. The body settles slightly while the two legs remain separated.'),
('right_support_left_toeoff','The anatomical RIGHT boot is planted under the forward body and carries the weight. The anatomical LEFT toes have just left the ground behind, with its knee beginning to bend. There must be a visible air gap under the left trailing boot.'),
('right_midstance_left_pass','The anatomical RIGHT boot stays planted as its leg passes toward mid-stance. The anatomical LEFT knee bends and swings forward to pass beside the supporting right leg, left boot entirely airborne and tucked up. Both boot silhouettes remain readable.'),
('right_late_stance_left_high','The anatomical RIGHT leg supports the body beneath and slightly behind the hip. The anatomical LEFT knee is lifted forward at the high swing position, left lower leg bent with its boot lifted clearly off the ground. This is left-leg high swing, not right-leg high swing.'),
('right_heelup_left_extend','The anatomical RIGHT support heel starts lifting while the right toes remain planted behind. The anatomical LEFT thigh is forward and its lower leg begins unfolding, left boot extending forward and downward through the air toward the next contact.'),
('right_toe_support_left_lower','Only the anatomical RIGHT forefoot/toes support behind the body. The anatomical LEFT leg reaches forward almost straight but relaxed, left heel lowered to just above the ground without touching yet. The left boot is visibly leading and airborne.'),
('left_precontact_right_pushoff','The anatomical LEFT heel is a hair above the ground at its forward extreme, just before touchdown. The anatomical RIGHT leg is stretched behind with toes performing the final push-off. Make the transition into frame 09 left contact smooth; do not repeat frame 09 exactly.'),
('left_contact','The anatomical LEFT boot has just reached its forward extreme and touches the ground heel-first. The anatomical RIGHT leg trails well behind, with only its toe at the last push-off point. A clearly split left-leading step, the opposite leg assignment to frame 01.'),
('left_loading','The anatomical LEFT front boot rolls from heel onto its sole and accepts the weight with a softly bent knee. The trailing RIGHT heel is raised, its toes still touching at push-off. The body settles slightly while the two legs remain separated.'),
('left_support_right_toeoff','The anatomical LEFT boot is planted under the forward body and carries the weight. The anatomical RIGHT toes have just left the ground behind, with its knee beginning to bend. There must be a visible air gap under the right trailing boot.'),
('left_midstance_right_pass','The anatomical LEFT boot stays planted as its leg passes toward mid-stance. The anatomical RIGHT knee bends and swings forward to pass beside the supporting left leg, right boot entirely airborne and tucked up. Both boot silhouettes remain readable.'),
('left_late_stance_right_high','The anatomical LEFT leg supports the body beneath and slightly behind the hip. The anatomical RIGHT knee is lifted forward at the high swing position, right lower leg bent with its boot lifted clearly off the ground. This is right-leg high swing, not left-leg high swing.'),
('left_heelup_right_extend','The anatomical LEFT support heel starts lifting while the left toes remain planted behind. The anatomical RIGHT thigh is forward and its lower leg begins unfolding, right boot extending forward and downward through the air toward the next contact.'),
('left_toe_support_right_lower','Only the anatomical LEFT forefoot/toes support behind the body. The anatomical RIGHT leg reaches forward almost straight but relaxed, right heel lowered to just above the ground without touching yet. The right boot is visibly leading and airborne.'),
('right_precontact_left_pushoff','The anatomical RIGHT heel is a hair above the ground at its forward extreme, just before touchdown. The anatomical LEFT leg is stretched behind with toes performing the final push-off. This closes the cycle smoothly into frame 01 and frame 02; do not repeat frame 01 exactly.')]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
identity=ROOT/'qdao_original_roster_v13/references'/CHAR/'original-identity-1024.png'
style=ROOT/'designs/jubaozhai-ui/02-characters.png'
jobs=[]
for direction in ['N','NE']:
    idle=ROOT/'qdao_original_roster_v13/candidate'/CHAR/'idle'/f'{direction}.png'
    orient=('NORTH: a straight rear view walking directly away toward screen top. The camera, head, chest, pelvis and both feet all face north; no face or front chest is visible. Anatomical right is image-right, anatomical left is image-left. Preserve the reference rear robe lightning motif.' if direction=='N' else 'NORTHEAST: a three-quarter rear-right view, walking diagonally away toward screen upper-right. The camera and body orientation exactly match the NE idle reference, showing the back and the small right cheek/ear contour. Do not turn into side profile, southeast or front view. The anatomical right side is the near side. Preserve the reference rear robe lightning motif.')
    refs=[str(identity),str(idle),str(style)]
    for frame,(phase,action) in enumerate(phases,1):
        prompt=f'''Use case: stylized-concept.
Asset type: one native high-resolution transparent game character walking-animation frame, for Wuxing Qitan.
Primary request: Draw ONE newly articulated full-body sprite of 06_thunder_caster_boy, direction {direction}, frame {frame:02d} of a 16-frame walk cycle. This is a unique genuine walking pose, not a standing idle or a copied/transformed previous image. No sprite sheet or collage.
Input image 1 is the immutable character identity reference. Input image 2 is the exact {direction} direction, rear clothing construction, held-equipment sides, and Q-body-proportion reference; its idle posture is not the target motion. Input image 3 is the approved PRIMARY STYLE REFERENCE from designs: match its clean luminous rounded hand-painted Daoist chibi finish, soft volume, warm gold material, crisp but delicate contours and polished detail. Do not copy its UI, characters, scenery or colors onto this character.
Identity lock: the same short chibi boy with brown layered hair gathered into a short high ponytail, gold ribbon and turquoise/gold hair beads; ornate warm-gold and ivory Daoist coat with navy details and gold lightning embroidery, navy short trousers, white leg wraps, black-and-gold boots, turquoise beads and short gold tassels. Preserve this exact costume, proportions and equipment through every frame. His anatomical RIGHT hand holds the gold pointed lightning staff with yin-yang ornament and turquoise beads. His anatomical LEFT hand holds the rectangular gold/yellow yin-yang talisman plaque. Do not swap hands or equipment, mirror the character, invent a backpack, add weapons, change colors or add new ornaments. In these rear views the staff remains on image-right and the talisman remains on image-left, as reference 2 shows.
Camera and direction: {orient} Use the same slightly elevated game-sprite camera and focal perspective as reference 2. Keep torso upright with only a subtle natural walking counterrotation; restrained hand/prop swing, no attack or casting gesture.
Exact leg phase ({phase}): {action} Here forward means along the stated travel direction, away from the viewer; backward means toward the viewer. Anatomical right/left are the character's own, never arbitrary screen-side replacements. Two anatomically connected legs and two distinct boots must be present; no extra limb or fused legs. Modest natural cloth/hair secondary motion corresponding to this phase.
Composition: square native PNG at least 1024x1024, preferably 1536x1536 if supported. Exactly one complete figure with all hair tips, staff tip, talisman, ribbons and both boots comfortably inside the frame. Match the consistent figure scale: topmost hair around 6 percent of canvas height and lowest grounded sole around 94 percent, body centered, no crop or camera zoom. Final whole-frame downsample uses fixed common_scale 0.88 and foot anchor [512,942] on 1024; do not bake an artificial pose translation into the drawing.
Background: genuinely transparent alpha, empty beyond the silhouette. No magenta, green, white, black or painted checkerboard background; no ground plane, cast ground shadow, halo, color fringe or drop shadow. Preserve fine clean antialiased hair and cloth edges against transparency. Highest visual finish available through this host-managed built-in route.
Avoid: grid, multiple views, labels, digits, text, watermark, outline glow, motion blur, speed lines, particles, spell effects, plastic render, realistic long-limbed anatomy, enlarged body, changed identity, duplicated poses, mirrored pose, interpolated or warped existing art. Return only the single complete transparent sprite.'''
        folder=HERE/'plans'/direction;folder.mkdir(parents=True,exist_ok=True)
        p=folder/f'{frame:02d}.prompt.txt';p.write_text(prompt,encoding='utf-8')
        jobs.append({'batch':f'{direction}{frame:02d}-walk-v1','direction':direction,'frame':frame,'phase':phase,
                     'prompt_path':str(p),'prompt_sha256':sha(p),'references':refs,
                     'status':'planned_not_submitted','requires_parent_edge_fix_release':True})
manifest={'prepared_at':datetime.now(timezone.utc).isoformat(),'character':CHAR,'scope':['N','NE'],
          'total':32,'actual_generation_calls':0,'status':'waiting_for_parent_edge_fix_release',
          'reference_inspected':True,'references':[{ 'path':str(p),'sha256':sha(p)} for p in [identity,ROOT/'qdao_original_roster_v13/candidate'/CHAR/'idle/N.png',ROOT/'qdao_original_roster_v13/candidate'/CHAR/'idle/NE.png',style]],
          'jobs':jobs,'notes':['Only textual plans saved. Call archive_generation.prepare immediately before each actual call; finalize with real tool result.','Native alpha required. No chroma-key fill.','Each direction needs individual visual review and cyclic closure review. No visual approval assigned.']}
(HERE/'plan.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'planned':len(jobs),'plan':str(HERE/'plan.json'),'generation_calls':0}))
