"""Exact single-frame request preparation for 06 SE/SW; no API invocation."""
from pathlib import Path
import argparse, importlib.util, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TOOLS=HERE.parent/'06-tools'
PHASES={
1:'RIGHT heel first touches down forward in the travel direction, right knee almost extended; LEFT leg stretches behind with only its toe touching and heel raised. Two-leg contact, right-leading stride.',
2:'RIGHT boot lowers from heel contact toward flat support and right knee flexes slightly; LEFT rear toe pushes off, left heel rises. Right-leading loading response, narrower stride than frame 01.',
3:'RIGHT sole planted under the forward half of the body taking all weight; LEFT rear foot has just lifted with left knee beginning to flex and left toe pointing down behind. Clear separate feet; no airborne hop.',
4:'RIGHT boot remains planted under body as it travels over support; LEFT knee bends and swings forward from behind, left boot suspended immediately behind the supporting ankle. This is early left swing, not crossed legs.',
5:'RIGHT leg supports the body with sole planted directly below hip; LEFT knee rises forward in passing pose, left boot visibly airborne beside and ahead of support leg, toe down. Left swing is halfway through, compact natural stride.',
6:'RIGHT support ankle pushes body onward with heel just beginning to rise; LEFT thigh forward, knee starting to unfold, left boot airborne ahead of body and lower than frame 05. Forward descending left swing.',
7:'RIGHT heel raised and right forefoot supports behind body; LEFT knee extends further forward, left heel just above the future ground point and toe lifted. Left leg about to land, no contact yet.',
8:'RIGHT rear forefoot still supports with heel raised; LEFT leg nearly straight reaching forward, heel barely above ground, toe slightly raised. Last instant before left heel contact, distinct from frame 09.',
9:'LEFT heel first touches down forward in the travel direction, left knee almost extended; RIGHT leg stretches behind with only its toe touching and heel raised. Two-leg contact, LEFT-leading stride, visibly opposite to frame 01.',
10:'LEFT boot lowers from heel contact toward flat support and left knee flexes slightly; RIGHT rear toe pushes off, right heel rises. Left-leading loading response, narrower stride than frame 09.',
11:'LEFT sole planted under the forward half of the body taking all weight; RIGHT rear foot has just lifted with right knee beginning to flex and right toe pointing down behind. Clear separate feet; no airborne hop.',
12:'LEFT boot remains planted under body as it travels over support; RIGHT knee bends and swings forward from behind, right boot suspended immediately behind the supporting ankle. Early right swing, not crossed legs.',
13:'LEFT leg supports the body with sole planted directly below hip; RIGHT knee rises forward in passing pose, right boot visibly airborne beside and ahead of support leg, toe down. Right swing is halfway through, compact natural stride.',
14:'LEFT support ankle pushes body onward with heel just beginning to rise; RIGHT thigh forward, knee starting to unfold, right boot airborne ahead of body and lower than frame 13. Forward descending right swing.',
15:'LEFT heel raised and left forefoot supports behind body; RIGHT knee extends further forward, right heel just above the future ground point and toe lifted. Right leg about to land, no contact yet.',
16:'LEFT rear forefoot still supports with heel raised; RIGHT leg nearly straight reaching forward, heel barely above ground, toe slightly raised. Last instant before right heel contact in frame 01; coherent closing of walk loop.'
}

def prepare(direction, frame, version, anchors=None, detail=''):
    refs=[str(ROOT/'qdao_original_roster_v13/references/06_thunder_caster_boy/original-identity-1024.png'),str(ROOT/f'qdao_original_roster_v13/candidate/06_thunder_caster_boy/idle/{direction}.png'),str(ROOT/'designs/jubaozhai-ui/02-characters.png')]
    refs += [str(Path(p).resolve()) for p in (anchors or [])]
    angle=('SOUTHEAST facing diagonally toward screen lower RIGHT, exact three-quarter front-right view. His anatomical RIGHT side is the nearer side; never turn full frontal or full side profile.' if direction=='SE' else 'SOUTHWEST facing diagonally toward screen lower LEFT, exact three-quarter front-left view. His anatomical LEFT side is the nearer side; never turn full frontal or full side profile.')
    prompt=f'''Use case: stylized-concept. Asset: one genuine native high-resolution 2D game animation frame, {direction}{frame:02d} of a 16-frame walk cycle. Render exactly ONE complete full-body character on a truly transparent RGBA background, no sheet, panels, labels or other figures.
Image 1 is the exact identity reference for 06_thunder_caster_boy. Image 2 fixes the {direction} camera direction and original proportions. Image 3 is the MAIN STYLE reference: match its bright clean, rounded full-volume Taoist chibi high-definition hand-painted finish and soft warm materials ONLY; retain image 1's identity, costume and gold/navy palette, never copy a different face or outfit from image 3.
Direction/camera: {angle} Fixed slightly overhead game camera. Head and chest both point in that travel direction. Keep smiling face and both amber eyes in this three-quarter view, far eye appropriately smaller.
This exact newly drawn locomotion phase: {PHASES[frame]} RIGHT and LEFT always mean anatomical legs, not picture sides. Show BOTH distinct boots with correct hip-to-knee-to-ankle structure and readable depth. Feet follow the same diagonal travel axis as the torso. A grounded WALK with at least one foot supporting, not running, jumping, attacking, standing idle or an artificial shifted/warped copy. Use modest natural arm counter-swing while hands retain their objects, a little robe/ribbon sway appropriate to this phase.
Identity invariants: cheerful young round-faced boy with very large brown hair mass, high brown ponytail tied by gold/teal beads and yellow trailing ribbons, round gold yin-yang forehead ornament, huge amber eyes and small open smile. Ivory and warm-gold embroidered long robe, navy lining, navy loose trousers with gold lightning trim, gold/ivory dark boots. Gold yin-yang staff stays in his anatomical RIGHT hand; separate rectangular gold yin-yang talisman stays in LEFT hand. Preserve all object identities, handedness and compact short limbs. No hat, new accessories, aura, detached lightning or extra limb. Never mirror the references or exchange hands.
Framing: square native canvas at least 1024x1024, preferably 1254x1254 or larger. Hair top at about 6% of full canvas height, lowest ground-contact boot at about 94%; fixed upper-body centerline at x=50%. Full silhouette including staff tip and all ribbons comfortably inside edges, no crop. Keep reference head/body ratio and constant camera scale. Crisp clean silhouette with no purple/magenta/colored fringe. Preserve fine painted material detail without plastic 3D shine or photoreal skin.
Background MUST be genuinely transparent alpha, no colored matte, fake checkerboard, opaque floor, ground shadow, ambient shadow blob, text, watermark or frame border. Highest visual finish via the current built-in image tool; prompt is a visual target and does not assert a model/quality selector. One original frame only.'''
    if anchors:
        prompt += '\nAdditional images 4 onward are actual selected adjacent/keyframe or edit-target references as described next. Keep their exact identity, brushwork, camera scale and costume geometry, but redraw the requested NEW distinct leg pose; never paste, translate, warp or copy an existing pose.\n' + detail
    elif detail:
        prompt += '\n' + detail
    spec=importlib.util.spec_from_file_location('archive06',TOOLS/'archive_generation.py');archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
    return archive.prepare(f'{direction}{frame:02d}-single-v{version}',prompt,refs)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('direction',choices=['SE','SW']);p.add_argument('frame',type=int,choices=range(1,17));p.add_argument('--version',type=int,default=1);p.add_argument('--anchor',action='append');p.add_argument('--detail',default='');a=p.parse_args()
    print(json.dumps(prepare(a.direction,a.frame,a.version,a.anchor,a.detail),ensure_ascii=False))
