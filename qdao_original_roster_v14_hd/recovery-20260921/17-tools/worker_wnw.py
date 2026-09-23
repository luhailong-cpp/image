"""Prepare exact prompts for this worker's W/NW single-frame built-in calls."""
import argparse, json
from common import *

PHASES = {
1: 'RIGHT leg reaches forward in travel direction and the right heel just contacts the ground. LEFT leg is extended behind with left toe contacting the ground. Both are grounded, normal short stride, no airborne jump.',
2: 'RIGHT front heel rolls down slightly toward a flat sole and accepts weight. LEFT rear heel rises slightly, toe still on ground. This is a small progression after frame01.',
3: 'RIGHT leg is now the planted load-bearing front leg, knee softly bends under body weight. LEFT trailing toe has just released the ground and starts its forward swing.',
4: 'RIGHT foot remains planted as the torso progresses over it. LEFT knee bends and the left foot lifts low, coming from behind toward the right ankle, no crossing of anatomical leg lanes.',
5: 'RIGHT foot is the sole supporting foot under the body. LEFT knee and boot pass beside it at low height, left foot advancing toward the travel direction. Head stays at constant anatomical size.',
6: 'RIGHT supporting heel starts to rise while right toes keep contact. LEFT swinging boot has passed the supporting ankle and moves forward, the left knee starts opening.',
7: 'RIGHT back foot pushes from its toe, toe still grounded. LEFT leg swings forward with softly bent knee, left boot ahead and low, no large exposed shoe sole.',
8: 'RIGHT toe remains the ground support behind. LEFT knee nearly opens and the left heel lowers immediately before ground contact, distinct from frame09.',
9: 'LEFT leg reaches forward in travel direction and left heel just contacts the ground. RIGHT leg is extended behind with right toe touching ground. It is the opposite anatomical contact from frame01.',
10: 'LEFT front heel rolls down toward a flat sole and accepts weight. RIGHT rear heel rises slightly with toe still grounded. Small progression after frame09.',
11: 'LEFT leg is the planted load-bearing front leg, knee softly bent. RIGHT trailing toe releases the ground and starts forward swing.',
12: 'LEFT foot stays planted as torso progresses above it. RIGHT knee bends and right boot lifts low, moving from behind toward the supporting left ankle without crossing leg lanes.',
13: 'LEFT foot is the sole supporting foot under body. RIGHT knee and boot pass beside it at low height, advancing forward. Maintain short chibi limb lengths.',
14: 'LEFT supporting heel starts to rise while left toes remain grounded. RIGHT swing foot has passed the support ankle and moves forward, right knee opening.',
15: 'LEFT rear foot pushes from its toe, toe stays grounded. RIGHT leg swings forward with softly bent knee, right boot ahead and low. Never make both feet airborne.',
16: 'LEFT toe remains ground support behind. RIGHT leg completes forward swing, knee opens and right heel lowers almost to its frame01 contact position. This near-contact pose must join frame01 smoothly without body size change.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--direction', choices=('W', 'NW'), required=True)
    parser.add_argument('--kind', choices=('idle', 'walk'), required=True)
    parser.add_argument('--frame', type=int)
    parser.add_argument('--version', type=int, default=1)
    parser.add_argument('--idle-version', type=int, help='Explicit selected directional idle; defaults W2/NW1')
    parser.add_argument('--key-references', action='store_true', help='Use explicitly chosen current four-key candidates as pose references')
    args = parser.parse_args()
    key = slot(args.kind, args.direction, args.frame)
    name = f'idle-{args.direction}-v{args.version}' if args.kind == 'idle' else f'walk-{args.direction}-{args.frame:02d}-v{args.version}'
    archive = archive_path(GEN / name)
    require(not archive.exists(), 'Use a fresh version')
    archive.mkdir(parents=True)
    references = [GEN / 'references/identity-view-1024.png', GEN / 'idle-S-v2/raw.png', IMAGE_ROOT / 'designs/jubaozhai-ui/02-characters.png']
    role = 'Image1 fixes the original character identity. Image2 fixes approved front-view body/head/boot proportions and scale only, not camera direction. Image3 is the main approved project STYLE reference for bright, rounded, polished fine hand-painted rendering; do not copy its UI or people.'
    idle_version = args.idle_version or (2 if args.direction == 'W' else 1)
    idle = GEN / f'idle-{args.direction}-v{idle_version}/raw.png'
    if args.kind == 'walk' and idle.is_file():
        references.append(idle)
        role += ' Image4 locks this exact directional camera, costume and scale; draw the requested new leg action rather than copying the idle.'
    camera = ('Absolute WEST camera: the boy faces exactly SCREEN LEFT in a pure side profile, nose and both boots point left; show only one eye, never a three-quarter front view. The anatomical LEFT side is the near side and left hand holds the scroll; anatomical RIGHT hand holds the brush on the far side, partly visible. Do not exchange held objects.' if args.direction == 'W' else
        'Absolute NORTHWEST camera: the boy faces diagonally AWAY toward SCREEN UPPER LEFT, rear-left 45-degree view showing his back and a narrow left cheek at most. No frontal chest or frontal belt buckle on his back. Preserve anatomical LEFT hand holding the scroll on the near/left side and anatomical RIGHT hand holding brush on the far/right side; do not exchange objects.')
    action = 'Independent relaxed standing pose, both feet fully grounded in a natural parallel stance, no stride or walking phase.' if args.kind == 'idle' else 'True WALK frame ' + f'{args.frame:02d}/16. ' + PHASES[args.frame]
    prompt = ('Use case: identity-preserve. Create ONE native complete character animation frame for 17 ghost-script calligrapher boy. ' + role + ' ' + camera + ' ' + action +
        ' Keep the exact boy: very large rounded head and short body/limbs; spiky dark brown hair with high topknot, jade-gold hairpin and small taiji hair ornament, teal flowing ribbon, warm brown eyes when visible, small jade diamond forehead mark when visible. Charcoal-black robe with precise warm gold scrolling embroidery, ivory inner layers and loose dark trousers, teal lining and tassels, jade beads, black-gold short boots. Right anatomical hand always grips a large black/jade/gold calligraphy brush with white bristles downward; left anatomical hand always grips the ivory scroll with black-gold rollers and its hanging taiji charm. Two small pale cyan ghost wisps remain near the scroll and are carried consistently, no new equipment. Do not place the FRONT waist taiji disk on the back of the robe. Slight natural cloth/tassel following of the stated pose, no pose substitution by moving a frozen sprite. Keep fixed anatomical proportions, fixed camera and stable head height; no stretching, flying, running or broad leaps. Whole character and every prop including tassels and brush fit with safe margin; same full-figure size as image2, approximately92 percent canvas height, top around4 percent and foot bottom around96 percent. Native single square canvas at least1024x1024, preferably1254x1254. Genuine transparent RGBA background, zero floor/shadow, clean naturally colored antialiased edges, no chromatic red/cyan halo, no magenta backing, no checkerboard, no text, no labels, no sheet, no duplicate figures. Finely painted clean rounded Daoist chibi style matching the approved reference, highest visual fidelity. This must be a newly drawn complete action, never mirrored, warped, translated, duplicated or interpolated from another pose.')
    if args.kind == 'walk':
        references = [idle, GEN / 'references/identity-view-1024.png', IMAGE_ROOT / 'designs/jubaozhai-ui/02-characters.png']
        geometry = ('The near side leg is anatomical LEFT; the far leg is anatomical RIGHT. Forward travel is SCREEN LEFT. Maintain the pure side torso and thin edge of the front waist buckle from Image1.' if args.direction == 'W' else
            'Near leg is anatomical LEFT, far leg anatomical RIGHT. Forward travel is diagonally UPPER LEFT. In right-leading first-half gait, right boot advances up-left below robe while left leg trails DOWN-RIGHT toward viewer; do not always draw the left boot leading. Keep back gold knot/sash from Image1.')
        prompt = ('Use case: identity-preserve. Draw ONE native new ' + args.direction + ' walk frame ' + f'{args.frame:02d}/16. '
            'Image1 fixes the exact directional camera, character scale, head/torso/boot proportions, held objects and costume. Image2 fixes original identity. Image3 is the main approved hand-painted STYLE. '
            + camera + ' Gait requirement: ' + PHASES[args.frame] + ' ' + geometry +
            ' Keep the short chibi anatomy and body size exactly stable, both legs connected to their own hips, normal grounded tiny walking stride, never flying. Clothing and ribbons follow this new phase subtly. Right hand holds black-jade-gold brush and white bristles down, left hand ivory scroll with black-gold rollers, two cyan ghosts beside scroll; never switch or mirror equipment. Brown topknot, teal ribbons/jade beads, black-gold embroidered robe and ivory lining all unchanged. Full figure same scale as Image1 about92% square height; preserve safe margins around all props. Native1254x1254 square or greater, minimum1024, genuine transparent RGBA with clean naturally colored edges, no chromatic halo, no floor/shadow/text/checkerboard/grid. One newly hand-painted complete action; no mirror, warp, interpolation, repeated idle or translated frozen pose.')
        if args.key_references:
            versions = {1: 2, 5: 1, 9: 1, 13: 2} if args.direction == 'W' else {1: 4, 5: 2, 9: 4, 13: 2}
            pair = (1, 5) if args.frame < 5 else (5, 9) if args.frame < 9 else (9, 13) if args.frame < 13 else (13, 1)
            for keyframe in pair:
                path = GEN / f'walk-{args.direction}-{keyframe:02d}-v{versions[keyframe]}/raw.png'
                require(path.is_file(), 'Selected key reference not yet available: ' + str(path))
                references.append(path)
            depth = ('RIGHT far leg supports forward; smaller right boot is forward screen-left/high. LEFT near leg is trailing screen-right/low and larger, then lifting into swing.' if args.frame < 5 else
                     'RIGHT far smaller boot supports from behind; LEFT near larger boot swings FORWARD screen-left at low height and gradually descends toward its contact.' if args.frame < 9 else
                     'LEFT near larger boot is grounded forward screen-left/LOWER, supporting weight. RIGHT far smaller boot trails screen-right/HIGHER and lifts into swing.' if args.frame < 13 else
                     'LEFT near larger boot supports from behind screen-right/LOWER. RIGHT far smaller boot swings forward toward screen-left/HIGHER and gradually lowers into contact.')
            prompt += (f' Image4 is the existing phase{pair[0]:02d} and Image5 is phase{pair[1]:02d}, both are pose-scale guides only. '
                       'Draw this requested NEW phase, not either reference pose. Preserve correct near/far depth: ' + depth +
                       ' Near LEFT thigh occludes FAR right thigh where they overlap. Boot physical size stays consistent with idle, only modest near/far perspective, never giant boots. Keep at least one genuine support foot grounded, no both-feet-off-floor pose.')
    (archive / 'prompt.txt').write_bytes(prompt.encode('utf-8'))
    bindings = [{'path': str(path.resolve()), 'sha256': sha(path)} for path in references]
    request = {'schema': 1, 'character_id': CHAR, 'kind': args.kind, 'direction': args.direction, 'frame': args.frame,
        'slot': key, 'tool': 'built-in image_gen', 'route': 'builtin', 'configSnapshot': read(CONFIG),
        'actual_request': {'prompt': prompt, 'referenced_image_paths': [r['path'] for r in bindings], 'started_at': now()},
        'submittedParameters': {'model': None, 'quality': None}, 'reference_bindings_at_start': bindings,
        'status': 'request_prepared_not_yet_submitted', 'paid_api_calls': 0}
    save_new(archive / 'request.json', request)
    print(json.dumps({'archive': str(archive), **request['actual_request']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
