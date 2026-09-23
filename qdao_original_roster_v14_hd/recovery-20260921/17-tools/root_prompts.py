"""Prompt preparation for root-owned S/SW slots only; no image generation."""
from pathlib import Path
import argparse, subprocess, sys, json
HERE=Path(__file__).resolve().parent
GEN=HERE.parent/'17-generation'
ROOT=HERE.parents[2]
PHASES={
1:'RIGHT foot forward initial heel contact, LEFT foot trailing toe contact; small natural stride.',
2:'Right heel has rolled nearly flat into weight acceptance; right knee begins to flex, left rear toe is just leaving the ground.',
3:'DOWN pose. Right foot flat and supporting full body weight, right knee gently flexed. Left knee bends with left heel lifting behind; head lowers only 8 pixels.',
4:'Right foot supports as torso moves above it. Left bent knee swings forward from behind to just behind the right shin, left foot low above ground.',
5:'PASSING pose. Right foot planted beneath hip, left knee and foot pass beside right leg without crossing or merging; left foot hovers low. Head at neutral height.',
6:'Right foot still supporting, heel begins to rise; left leg swings modestly forward, left knee partly extended, left boot stays low.',
7:'UP pose. Right rear heel raised and right toes grounded supporting body, left thigh forward and knee slightly flexed, left boot approaching ground ahead. Body only 6 pixels higher.',
8:'Late left forward swing: right rear toes still grounded, left knee extending and left heel lowering to just above ground. A small restrained step.',
9:'OPPOSITE CONTACT. LEFT foot forward initial heel contact, RIGHT foot trailing with heel raised and toe still touching. This is the opposite leg lead from frame01, not a mirrored image; equipment stays in original hands.',
10:'Left heel rolls nearly flat into weight acceptance; left knee begins to flex, right rear toe is just leaving the ground.',
11:'DOWN pose. Left foot flat and supporting full body weight, left knee gently flexed. Right knee bends with right heel lifting behind; head lowers only 8 pixels.',
12:'Left foot supports as torso moves above it. Right bent knee swings forward from behind to just behind the left shin, right foot low above ground.',
13:'PASSING pose. Left foot planted beneath hip, right knee and foot pass beside left leg without crossing or merging; right foot hovers low. Head at neutral height.',
14:'Left foot still supporting, heel begins to rise; right leg swings modestly forward, right knee partly extended, right boot stays low.',
15:'UP pose. Left rear heel raised and left toes grounded supporting body, right thigh forward and knee slightly flexed, right boot approaching ground ahead. Body only 6 pixels higher.',
16:'Late right forward swing completing cycle: left rear toes still grounded, right knee extending and right heel lowering to just above ground. Leads smoothly to right heel contact frame01. Do not duplicate frame01.'}
BASE='Use case: identity-preserve. Generate ONE newly painted complete standalone 2D game animation sprite, a square native image at least 1024x1024, with genuine alpha transparency. Image1 is the exact identity; Image2 is the same-direction idle defining scale, camera and costume; any additional character image is a gait continuity reference only; the last image is the approved primary hand-painted style reference. Preserve this exact 灵篆书生 boy: huge round head, short compact limbs and body, brown tousled straight hair and topknot with teal/gold yin-yang clasp, brown eyes, jade forehead diamond, ivory inner robe, charcoal-black short outer robe with antique-gold cloud trim and teal lining, yin-yang belt and jade tassels, short dark gold-trimmed boots. Anatomical RIGHT hand holds ONE black/gold/teal brush, LEFT hand holds ONE blank ivory scroll with black/gold rollers; exactly TWO cyan ink spirits close to scroll. Keep original hands and ornament arrangement. Fixed orthographic slightly elevated RPG camera. Match Image2 figure/head size exactly, no camera move or zoom: top hair at about 8% of height, lowest boots at96%, body axis50%. Full extremities and accessories inside canvas, clear margin, tassels always above lowest boot. Maintain the clean rounded finely painted Q-Daoist style and luminous restrained materials; no plastic 3D, realism or altered identity. '
END=' At least one foot always bears weight on the ground. Short relaxed ordinary walking stride; no running, jumping, high-knee march, kick, huge forward sole, crossed legs or sliding duplicated pose. Boots keep same size as idle; toe direction follows body. Adjust knees, hips, ankles, robe folds and subtle opposite torso sway coherently, with secure steady props and face. Do not alter body/head scale. Draw a unique articulated pose at this phase; no copying, mirroring, stretching or whole-sprite translation. Completely transparent empty background, no floor, cast shadow, checkerboard, halo, text, caption, numbering, UI, grid or multiple people.'

def main():
 p=argparse.ArgumentParser();p.add_argument('--direction',choices=['S','SW'],required=True);p.add_argument('--frame',type=int,required=True);p.add_argument('--attempt',type=int,default=1);p.add_argument('--continuity',type=Path);a=p.parse_args()
 d=a.direction;n=a.frame;folder=GEN/f'walk-{d}-{n:02d}-v{a.attempt}';folder.mkdir(parents=True,exist_ok=False)
 camera='S/front, face and body square toward viewer. Anatomical right leg appears on viewer LEFT, anatomical left leg on viewer RIGHT.' if d=='S' else 'SW/front-left three-quarter, face, torso and both boots consistently pointing diagonally toward lower-left of image, showing front and his left side. Do not turn pure profile or straight front.'
 prompt=BASE+f' View {camera} This is walk {d}{n:02d}, phase {(n-1)}/16 in a 16-pose cycle. REQUIRED articulated leg pose: '+PHASES[n]+END
 (folder/'prompt.txt').write_text(prompt,encoding='utf8')
 refs=[GEN/'references/identity-view-1024.png',GEN/('idle-S-v2/raw.png' if d=='S' else 'idle-SW-v1/raw.png')]
 if a.continuity: refs.append(a.continuity.resolve())
 refs.append(ROOT/'designs/jubaozhai-ui/02-characters.png')
 cmd=[sys.executable,str(HERE/'prepare_request.py'),'--archive',str(folder),'--prompt',str(folder/'prompt.txt'),'--kind','walk','--direction',d,'--frame',str(n)]
 for ref in refs:cmd+=['--reference',str(ref)]
 subprocess.run(cmd,check=True,capture_output=True,text=True)
 print(json.dumps({'archive':str(folder),'actual_request':json.loads((folder/'request.json').read_text(encoding='utf8'))['actual_request']}))
if __name__=='__main__':main()
