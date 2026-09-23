"""Prepare one exact built-in request for character 14. No API calls."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / 'qdao_original_roster_v14_hd/recovery-20260921'
VIEWS = {
 'S':'front view, facing toward the camera, moving toward screen bottom',
 'SE':'front-right three-quarter view, facing and moving toward screen bottom-right',
 'E':'strict right profile, facing and moving toward screen right',
 'NE':'rear-right three-quarter view, facing and moving toward screen top-right',
 'N':'straight rear view, facing away from camera, moving toward screen top',
 'NW':'rear-left three-quarter view, facing and moving toward screen top-left',
 'W':'strict left profile, facing and moving toward screen left',
 'SW':'front-left three-quarter view, facing and moving toward screen bottom-left',
}
PHASES = [
 'LEFT heel contacts forward, LEFT knee nearly straight; RIGHT leg extended behind on its toe; clear moderate stride separation.',
 'LEFT foot rolls down from heel, LEFT knee starts flexing to accept weight; RIGHT heel rises behind, toe still touches ground.',
 'LEFT foot planted forward with weight and bent knee (low/recoil); RIGHT toes lift from behind and RIGHT knee begins forward swing.',
 'LEFT leg supports body near center; RIGHT knee flexes more and travels forward from behind, RIGHT boot visibly off ground.',
 'LEFT foot supports directly under pelvis (passing); RIGHT bent knee and lifted boot pass beside the supporting leg, feet not crossed.',
 'LEFT leg straightens while its planted foot trails slightly; RIGHT bent knee advances ahead of pelvis, RIGHT foot still lifted.',
 'LEFT heel begins to lift behind, weight stays on LEFT forefoot; RIGHT shin extends ahead, RIGHT heel lowered close to ground.',
 'LEFT toe supports at rear; RIGHT leg nearly extended forward with heel hovering just above ground immediately before contact.',
 'RIGHT heel contacts forward, RIGHT knee nearly straight; LEFT leg extended behind on its toe; clear moderate stride separation.',
 'RIGHT foot rolls down from heel, RIGHT knee starts flexing to accept weight; LEFT heel rises behind, toe still touches ground.',
 'RIGHT foot planted forward with weight and bent knee (low/recoil); LEFT toes lift from behind and LEFT knee begins forward swing.',
 'RIGHT leg supports body near center; LEFT knee flexes more and travels forward from behind, LEFT boot visibly off ground.',
 'RIGHT foot supports directly under pelvis (passing); LEFT bent knee and lifted boot pass beside the supporting leg, feet not crossed.',
 'RIGHT leg straightens while its planted foot trails slightly; LEFT bent knee advances ahead of pelvis, LEFT foot still lifted.',
 'RIGHT heel begins to lift behind, weight stays on RIGHT forefoot; LEFT shin extends ahead, LEFT heel lowered close to ground.',
 'RIGHT toe supports at rear; LEFT leg nearly extended forward with heel hovering just above ground immediately before frame 01 contact.',
]

def main():
 p=argparse.ArgumentParser();p.add_argument('direction',choices=VIEWS);p.add_argument('frame',help='01..16 or idle');p.add_argument('--version',default='v1');p.add_argument('--anchor',type=Path);p.add_argument('--correction',default='');a=p.parse_args()
 idle=a.frame=='idle';f=None if idle else int(a.frame);assert idle or 1<=f<=16
 key=a.direction+('idle' if idle else f'{f:02d}')
 out=REC/'14-generation'/f'{key}-{a.version}';out.mkdir(parents=True,exist_ok=False)
 refs=[str(REC/'14-reference/identity-1024.png'),str(ROOT/'designs/jubaozhai-ui/02-characters.png')]
 if a.anchor:refs.append(str(a.anchor.resolve()))
 pose='Independent neutral standing pose: both white boots planted comfortably under hips, relaxed knees and balanced weight; not a walk frame.' if idle else f'Exactly frame {f:02d} of a 16-frame cyclic natural WALK, phase {(f-1)*22.5:g} degrees. Anatomical LEFT and RIGHT are the character\'s own limbs. '+PHASES[f-1]
 prompt=f'''Use case: stylized-concept.
Asset type: one complete high definition 2D game character animation frame for Five Elements Tales, character 14 snow summoner girl.
Input image 1 is the sole identity and costume reference (a faithful downsized copy of the original portrait). Image 2 is the approved main rendering-style reference: match its clean bright rounded Chinese Daoist chibi hand-painted finish and soft detailed materials; do not copy its UI, text, other characters or colors onto this girl.'''
 if a.anchor:prompt+=' Image 3 is the same character direction and framing anchor: preserve her exact size, camera, costume structure and rendering, changing the gait pose as requested.'
 prompt+=f'''
Identity invariants: silver-white short bob hair with lavender shadows and small top curl; two white furry animal ears with lavender interiors; large purple eyes, round youthful smiling face; silver-blue crystalline snowflake hair ornament on her anatomical LEFT temple with purple tassels. White and pale lilac layered short robe/skirt, wide lavender sleeves with white fur trim, dark purple sash with silver fox-face buckle and blue crystal pendants, bare knees, short white fur-trimmed purple-detailed boots. Her anatomical LEFT arm cradles the small fluffy white fox with purple eyes and lavender ear interiors against her left ribs; her anatomical RIGHT palm carries the small hovering blue snowflake crystal. Keep fox, sleeves, charms, and snowflake attached to the same anatomical side even in rear/profile views; hidden features stay naturally occluded. No new weapon, staff, backpack or tail on the girl. Preserve the portrait's head/body proportion about 2.3 heads tall, no adult proportions.
Camera and facing: {VIEWS[a.direction]}. Fixed mild elevated orthographic RPG camera, not perspective camera, no camera tilt. Head, chest, pelvis and planted foot direction agree. Do not turn head toward viewer in rear views.
Action: {pose}
This is walking with alternating leg articulation and weight transfer, never hopping, running, marching, skating or dancing. At least one foot is grounded at every phase. Maintain moderate short-limbed steps and gentle counter-rotation; carrying arms remain stable, robe hem and tassels react subtly. Both legs must remain anatomically separate; never invent extra limbs, reverse knees, or show the undersides of both boots. Keep torso and head scale stable, with only tiny natural vertical weight shift.
Composition: exactly ONE full-body girl with her carried white fox, isolated on a genuinely transparent RGBA background; square native image at least 1024x1024, ideally 1024x1024. No sheet, grid, collage, labels, frame number, border, cast shadow, floor, backdrop or painted checkerboard. All ears, hair ornament, snowflake, fingers, sleeve tassels and boots fully inside the canvas. At 1024 scale place ear tips near y=80 and lowest grounded sole near y=942; pelvis centered around x=512; comfortable clear margins. The sprite fills about 84 percent of image height. Bright clean soft hand-painted shading with readable white fur and lilac fabric, no glare, no color fringe.
Render a new independently drawn exact pose; do not duplicate, mirror, warp or translate the reference to simulate motion. Highest available visual finish. Deliver the transparent image only.'''
 if idle:
  prompt=prompt.replace('This is walking with alternating leg articulation and weight transfer, never hopping, running, marching, skating or dancing. At least one foot is grounded at every phase. Maintain moderate short-limbed steps and gentle counter-rotation; carrying arms remain stable, robe hem and tassels react subtly.', 'This is a still neutral STANDING pose, not any walking phase. BOTH boots support equal weight at the same depth, feet close and parallel, knees straight and relaxed. No staggered step or raised heel. Carrying arms remain stable, robe hem hangs quietly.')
 if a.correction:prompt+='\nTargeted correction: '+a.correction
 (out/'prompt.txt').write_text(prompt,encoding='utf-8')
 request={'tool':'image_gen__imagegen','route':'builtin','started_at':datetime.now(timezone.utc).isoformat(),'slot':{'kind':'idle' if idle else 'walk','direction':a.direction,'frame':f},'actual_request':{'prompt':prompt,'referenced_image_paths':refs},'submittedParameters':{'model':None,'quality':None},'configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig')),'referenceBindings':[{'path':r,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r in refs]}
 (out/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'archive':str(out),'request':request['actual_request']},ensure_ascii=False))

if __name__=='__main__':main()
