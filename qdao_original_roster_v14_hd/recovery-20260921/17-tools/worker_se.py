from pathlib import Path
import argparse, subprocess, sys, json

ROOT=Path(__file__).resolve().parents[3]
REC=ROOT/'qdao_original_roster_v14_hd/recovery-20260921'
GEN=REC/'17-generation'
PHASES={
1:'RIGHT forward contact. Near RIGHT heel has just touched down below screen-left hip, left rear toes remain on ground at screen-right and higher.',
2:'RIGHT load acceptance. Near RIGHT front boot screen-left settles fully flat and knee bends slightly. Far LEFT rear heel rises further at screen-right, its toe still touches behind. Moderately open stride.',
3:'RIGHT down phase. Near RIGHT boot screen-left remains firmly flat, right knee flexes to absorb weight. Far LEFT boot behind at screen-right has just left the ground, knee bends and boot tips down. Torso lowers just 5 pixels.',
4:'RIGHT mid-support approach. Near RIGHT boot screen-left is flat under near hip. Far LEFT knee bends and foot swings from rear toward the planted ankle, still a little behind and higher at screen-right. Only short low swing, no exaggerated knee.',
5:'RIGHT planted support and LEFT passing. Near RIGHT boot at screen-left is the sole weight-bearing foot, flat at lowest ground level, visibly larger and LOWER. Far LEFT boot at screen-right is LIFTED about 70 native pixels ABOVE right sole, close alongside ankle, knee flexed. Do not plant screen-right boot. Planted right boot is rooted at x48% y94%; lifted left boot x60% y88%.',
6:'RIGHT support and LEFT forward swing early. Near RIGHT foot stays planted under screen-left hip. Far LEFT knee advances forward (toward screen-right/lower-right), with left boot now in front of right ankle horizontally but still elevated 55 pixels. Gentle knee bend.',
7:'RIGHT terminal support, LEFT forward swing late. Near RIGHT boot screen-left rolls slightly toward toe and stays grounded. Far LEFT lower leg extends forward toward screen-right, toe up a little, boot still 35 pixels above its eventual far-plane ground.',
8:'RIGHT toe-off preparation, LEFT pre-contact. Near RIGHT rear boot screen-left heel slightly lifted, right toes still firmly support. Far LEFT boot screen-right nearly touches its forward ground position, heel about 10 pixels above ground. Both legs visible.',
9:'LEFT forward contact, opposite to frame01. Far LEFT leg from screen-right hip extends FORWARD toward screen-right; LEFT heel at x64% y87% just meets far-plane ground. Near RIGHT leg from screen-left hip extends BACK toward screen-left; RIGHT rear boot at x42% y94% remains LOWER and slightly larger due near-side perspective, heel raised but toe touches ground. This lower LEFT-OF-IMAGE boot is anatomical RIGHT REAR foot, not leading. Leading LEFT boot is right-of-image, a little smaller and higher. Moderate stride, do not switch these two boots.',
10:'LEFT load acceptance. Far LEFT front boot screen-right settles flat; left knee bends slightly. Near RIGHT rear boot screen-left has raised heel, rear toes contact LOW foreground ground. Foreground right rear boot stays lower than far leading left foot. Keep moderate stride.',
11:'LEFT down phase. Far LEFT boot screen-right planted supports entire weight, knee flexes. Near RIGHT leg behind screen-left bends and just lifts from ground; right toe points down, boot low but visibly airborne. Torso lowers just 5 pixels.',
12:'LEFT mid-support approach. Far LEFT boot screen-right flat planted under far hip. Near RIGHT leg screen-left swings from behind toward center, right knee bent slightly; right boot has lifted 50 pixels and approaches left ankle. Low swing not marching.',
13:'LEFT planted support and RIGHT passing. Far LEFT boot at screen-right is the single flat planted foot at x60% y94%. Near RIGHT boot at screen-left is LIFTED beside supporting ankle at x48% y87%, with visible bent knee and toe slightly downward. Do not plant screen-left boot. Modest step, no high knees.',
14:'LEFT support and RIGHT forward swing early. Far LEFT foot screen-right stays firmly grounded. Near RIGHT leg screen-left bends at knee and swings forwards toward viewer, right boot just starts advancing beyond support ankle; clearly airborne about 65 pixels, toes gently down.',
15:'LEFT terminal support, RIGHT forward swing late. Far LEFT foot screen-right rolls toward toe, still touching ground. Near RIGHT knee screen-left extends forward toward viewer/lower-right, larger right boot lowered to about 35 pixels above eventual near ground. Gentle stride, no sole aimed at viewer.',
16:'LEFT toe-off preparation, RIGHT pre-contact directly before frame01. Far LEFT boot screen-right heel raised, toe supports from rear higher plane. Near RIGHT leg screen-left extends down-forward, right heel just 10 pixels above its low near-ground landing. Moderate open stride matches frame01, no extreme sole foreshortening.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--frame',type=int,required=True);p.add_argument('--attempt',type=int,default=1);p.add_argument('--continuity',type=Path);p.add_argument('--correction',default='');a=p.parse_args()
 out=GEN/f'walk-SE-{a.frame:02d}-v{a.attempt}';out.mkdir(exist_ok=False)
 prompt=('Use case: stylized-concept. Draw ONE NEW independent complete single-frame game walking sprite for character17 Ghost Script Calligrapher Boy. Image1 locks exact identity; Image2 is exact SE standing scale and camera design; Image3 is the MAIN approved clean rounded hand-painted Daoist Q art style, ignore its UI. '
 'The character is facing SOUTHEAST, front-right three-quarter 45 degrees, diagonally down-right. Both eyes visible with far eye smaller. Mildly elevated orthographic game camera. Keep identical brown spiky bun hair, yin-yang hairpin and teal ribbon, jade forehead diamond, large brown eyes and round face, gold-cloud charcoal robe, ivory inside, teal lining, yin-yang jade belt, short pants, black gold-trimmed boots. ANATOMICAL RIGHT hand on SCREEN-LEFT holds huge brush; ANATOMICAL LEFT hand on SCREEN-RIGHT holds ivory blank scroll with black/gold rollers. Exactly TWO cyan ink spirits around scroll. The scroll MUST have its small hanging yin-yang medallion and short teal tassel, with tip ABOVE both boot soles so it never defines ground anchor. Never omit or swap equipment. '
 f'Frame {a.frame:02d} of sixteen-frame 480 ms normal walking loop. Specific physical pose: '+PHASES[a.frame]+' '
 'Near RIGHT hip is on screen-left, far LEFT hip screen-right. Boots must connect to the proper hips, never switch their side identities. Newly articulate the whole pose with natural weight-bearing hip and knee positions. At least one foot contacts ground; no flying, jump, sprint, big knees, seated pose or squatting. Small natural arm counter-swing, slight robe/tassel response. Keep head, brush, scroll, body scale and camera nearly unchanged from Image2. All toes point down-right, not outward. Whole figure including hair, brush, spirits, scroll and boots fits comfortably in one square native1024x1024 or larger canvas. Transparent alpha background. Clean soft antialiased edge, no colored fringe, no floor, no shadows, no text, grid or montage. Round bright clean high detail hand-painted volume, not plastic. Independently redraw this exact pose; do not duplicate, mirror, stretch, translate or interpolate another frame.')
 if a.correction:prompt+=' CRITICAL CORRECTION: '+a.correction
 if a.continuity:prompt+=' Image4 is continuity geometry reference. Keep that camera/body/head scale and preserve the specified leg-side topology, but newly draw the requested next physical walking phase; no copy of its pose.'
 (out/'prompt.txt').write_text(prompt,encoding='utf-8')
 refs=[GEN/'references/identity-view-1024.png',GEN/'idle-SE-v1/raw.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
 if a.continuity:refs.append(a.continuity)
 args=[sys.executable,'-B',str(Path(__file__).with_name('prepare_request.py')),'--archive',str(out),'--prompt',str(out/'prompt.txt'),'--kind','walk','--direction','SE','--frame',str(a.frame)]
 for r in refs:args+=['--reference',str(r)]
 subprocess.run(args,check=True)
 print(str(out))
if __name__=='__main__':main()
