from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json

HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parents[1]
ROOT=HERE.parents[3]
PHASES={
1:'Anatomical LEFT boot is forward in the walking direction, heel-first initial ground contact; anatomical RIGHT leg trails back with toe still touching ground and heel raised. Brief double support, left leading. Both feet remain on their own hip-width tracks.',
2:'Anatomical LEFT forward boot has just flattened on the ground and left knee softly flexes to take weight. Anatomical RIGHT trailing heel rises higher, its toe at the last moment of ground contact before toe-off. Left main support; slightly lower body than phase01.',
3:'Anatomical LEFT boot is flat and firmly supporting all weight, left knee beginning to extend. Anatomical RIGHT trailing toe has just lifted clear of ground, knee bends mildly as the boot begins recovery forward from behind. Left single support. Right boot visibly low but airborne behind.',
4:'Anatomical LEFT support boot remains planted and is moving under body center relative to torso. Anatomical RIGHT knee bends mildly, boot swings low forward toward the left support ankle, on its own track, without crossing. Left single support. Right boot still behind the passing point.',
5:'Anatomical LEFT boot is firmly flat on the ground directly beneath body center, bearing all weight. Anatomical RIGHT leg passes beside it under the body, knee mildly bent and boot slightly above ground. Left mid-stance, right passing. Show two separate knees and low airborne right boot, not an idle pose.',
6:'Anatomical LEFT boot remains planted but is now slightly behind the torso. Anatomical RIGHT low airborne boot has passed the support foot and swings a little forward. Left single support, right forward swing nearing completion. Short stride.',
7:'Anatomical LEFT trailing heel begins rising, left forefoot grounded and bearing weight. Anatomical RIGHT leg reaches gently forward with knee extending and boot lowering toward the ground, sole downward. Right not yet grounded; short stride, no kick.',
8:'Anatomical LEFT trailing toe remains on the ground and supports weight. Anatomical RIGHT forward boot is immediately above its coming heel contact, only a tiny clearance, not yet bearing weight. Short stride, definitely no both-feet airborne.',
9:'Anatomical RIGHT boot is forward in the walking direction, heel-first initial ground contact; anatomical LEFT leg trails back with toe still touching ground and heel raised. Brief double support, right leading. This is the opposite leading leg to phase01, no mirror or copy.',
10:'Anatomical RIGHT forward boot has just flattened on the ground and right knee softly flexes to take weight. Anatomical LEFT trailing heel rises higher, its toe at the last moment of ground contact before toe-off. Right main support; slightly lower body than phase09.',
11:'Anatomical RIGHT boot is flat and firmly supporting all weight, right knee beginning to extend. Anatomical LEFT trailing toe has just lifted clear of ground, knee bends mildly as the boot begins recovery forward from behind. Right single support. Left boot visibly low but airborne behind.',
12:'Anatomical RIGHT support boot remains planted and is moving under body center relative to torso. Anatomical LEFT knee bends mildly, boot swings low forward toward the right support ankle, on its own track, without crossing. Right single support. Left boot still behind the passing point.',
13:'Anatomical RIGHT boot is firmly flat on the ground directly beneath body center, bearing all weight. Anatomical LEFT leg passes beside it under the body, knee mildly bent and boot slightly above ground. Right mid-stance, left passing. Opposite support leg to phase05. Show two separate knees, no standing.',
14:'Anatomical RIGHT boot remains planted but is now slightly behind the torso. Anatomical LEFT low airborne boot has passed the support foot and swings a little forward. Right single support, left forward swing nearing completion. Short stride.',
15:'Anatomical RIGHT trailing heel begins rising, right forefoot grounded and bearing weight. Anatomical LEFT leg reaches gently forward with knee extending and boot lowering toward the ground, sole downward. Left not yet grounded; short stride, no kick.',
16:'Anatomical RIGHT trailing toe remains on the ground and supports weight. Anatomical LEFT forward boot is immediately above its coming heel contact, only a tiny clearance, not yet bearing weight. Natural preceding phase for left contact01. Definitely no both-feet airborne.',
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('direction',choices=['N','NE']);parser.add_argument('frame');parser.add_argument('--version',default='v1')
    parser.add_argument('--correction',default='');parser.add_argument('--direction-reference',type=Path)
    parser.add_argument('--omit-front-reference',action='store_true')
    args=parser.parse_args();idle=args.frame=='idle';frame=None if idle else int(args.frame)
    assert idle or frame in PHASES
    slot=args.direction+('idle' if idle else f'{frame:02d}')
    out=RECOVERY/'10-generation'/f'{slot}-{args.version}';out.mkdir(parents=True,exist_ok=False)
    refs=[RECOVERY/'10-work/references/identity-inspection-1024.png',ROOT/'designs/jubaozhai-ui/02-characters.png',RECOVERY/'10-generation/S01-v2/raw.png']
    roles=['authoritative-character-identity','confirmed-main-style','front-action-proportion-and-spear-grip-reference']
    if args.omit_front_reference:
        assert not args.direction_reference, 'Do not combine omitted front reference and direction reference'
        refs=refs[:2];roles=roles[:2]
    if args.direction_reference:
        refs.append(args.direction_reference.resolve());roles.append('same-direction-consistency-reference-not-pose-copy')
    facing=('NORTH directly away from viewer, exact straight rear view. Show back of head, both buns and back costume; NO face or eyes. Anatomical LEFT is screen LEFT, RIGHT is screen RIGHT. Forward points screen UP into distance: forward boot is farther away and slightly higher on the canvas than the trailing boot.' if args.direction=='N' else
            'NORTHEAST diagonally away toward screen upper-right, exact 45-degree right-rear three-quarter view. Show the back and her right side, not a front or front-three-quarter face. Anatomical LEFT leg is the far leg projecting upper-left of the near right hip; anatomical RIGHT leg is near. Forward foot moves along screen UPPER-RIGHT, rear foot is screen LOWER-LEFT. Never swap which knee belongs to which hip.')
    phase=('Independent IDLE: both complete boot soles grounded, feet naturally slightly apart on their own hip tracks, knees relaxed, weight evenly centered. Hair/ribbons/sleeves relaxed with small stable arcs. This is an independently drawn resting pose, not any walk frame.' if idle else f'WALK PHASE {frame:02d} of 16 (one complete alternating left-right cycle, 30ms per frame): '+PHASES[frame])
    prompt=' '.join([
      'Use case: stylized-concept. Create ONE original complete production movement sprite for 10_crimson_spear_girl, slot '+slot+'. Single square native frame at least 1024x1024, genuinely transparent alpha. No sheet, duplicate body, label, UI, checkerboard, floor, shadow, colored matte or effects.',
      'Input Image1 is authoritative identity: faithfully retain brown double buns and long twin tails, red ribbons, ornate gold and pale turquoise hair ornaments, amber eyes when visible, red/gold forehead jewel when visible, red/ivory/gold layered costume, gold trim and waist beads, red-white-gold boots, and exactly the same long dark shaft spear with ornate crimson crystal blade, gold guard and red tassels.',
      'Image2 is the confirmed MAIN STYLE: clean bright rounded Daoist chibi hand-painted materials, delicate warm shading, crisp finished edges. Do not copy its UI, portraits or alter this character colors. '+('Independently draw the requested new viewpoint and leg pose, while preserving Image1 original head-to-body ratio, outfit details, gear construction and two-hand grip. The portrait pose is not the target pose.' if args.omit_front_reference else 'Image3 is the front-action scale and weapon construction reference, not this new view: preserve its chibi head/body proportions, outfit details, gear scale and consistent two-hand grip, then draw the correct new view and specified leg phase.'),
      ('Image4 fixes the same-direction camera, silhouette size, costume back construction and spear orientation; genuinely redraw the requested different leg phase, do not reproduce its pose.' if args.direction_reference else ''),
      'Facing '+facing,
      'Keep fixed slightly elevated game camera, no camera roll, same rounded short-limb proportion as the character reference. Center grounded body around x512, contact-root around y942 on a 1024 canvas (scale fractions if native resolution differs). Entire head, twin tails, red ribbons, wide sleeves, spear tip, spear butt and both boots inside canvas with margin; match the character reference relative subject scale.',
      'Her anatomical LEFT hand always grips higher on the shaft nearer the blade at chest level; anatomical RIGHT hand grips lower near waist. This order is fixed in character coordinates as the view turns, not fixed screen sides. One single straight unbroken dark shaft through both hands. Rear-view arms and shaft can naturally occlude behind the torso; do not put a second weapon on her back. In straight N, blade projects toward screen upper-left and butt toward screen lower-right, opposite the front reference screen projection.',
      phase,
      'Gentle short-step grounded walk with minimal vertical bob; stable upright torso. Hair, skirt, ribbons and tassels react subtly, not wildly. At least one foot supports the ground in every walk. Knees and feet stay on two distinct anatomical tracks, no crossed legs, twisted feet, wide splits, jumping, running, attack, high-knee portrait pose, or large sole facing viewer. Highest visual finish, clean alpha edges without purple/magenta fringe.',
      args.correction,
    ])
    (out/'prompt.txt').write_bytes(prompt.encode('utf-8'))
    now=datetime.now(timezone.utc).isoformat()
    request={'status':'prepared_for_submission','character':'10_crimson_spear_girl','slot':slot,'startedAt':now,'tool':'image_gen__imagegen',
      'actual_request':{'prompt':prompt,'referenced_image_paths':[p.as_posix() for p in refs]},
      'submittedParameters':{'model':None,'quality':None},'configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8')),
      'referenceRoles':roles,'reference_bindings_at_start':[{'path':p.as_posix(),'sha256':sha(p),'purpose':role} for p,role in zip(refs,roles)]}
    (out/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'archive':out.as_posix(),'actual_request':request['actual_request']},ensure_ascii=False))

if __name__=='__main__':main()
