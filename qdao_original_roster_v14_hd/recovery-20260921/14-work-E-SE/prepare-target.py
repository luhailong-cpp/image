from pathlib import Path
import json,sys,subprocess
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'14-tools'))
from prepare import PHASES
d,f,version=sys.argv[1:4]; n=int(f)
anchor=R/'14-generation'/f'{d}01-v2/raw.png'
subprocess.run([sys.executable,str(R/'14-tools/prepare.py'),d,f,'--version',version,'--anchor',str(anchor)],check=True,stdout=subprocess.DEVNULL)
qdir=R/'14-generation'/f'{d}{n:02d}-{version}'; q=json.loads((qdir/'request.json').read_text())
extra=sys.argv[4] if len(sys.argv)>4 else ''
if not extra:
 if d=='SE':
  extra='RIGHT NEAR leg starts at screen-LEFT hip and always stays on SCREEN-LEFT track. LEFT FAR leg starts at screen-RIGHT hip and stays on SCREEN-RIGHT track. '
  if n<=8: extra+='LEFT FAR boot on SCREEN-RIGHT supports weight on ground; RIGHT NEAR boot on SCREEN-LEFT performs the described swing. '
  else: extra+='RIGHT NEAR boot on SCREEN-LEFT supports weight on ground; LEFT FAR boot on SCREEN-RIGHT performs the described swing. '
 else:
  extra='In right-facing profile forward is SCREEN-RIGHT, backward is SCREEN-LEFT. RIGHT leg is NEAR camera and must overlap far leg where they pass. '
  if n<=8: extra+='LEFT FAR leg carries body weight on ground, RIGHT NEAR leg swings in FOREGROUND. '
  else: extra+='RIGHT NEAR leg carries body weight on ground, LEFT FAR leg swings BEHIND it. '
 extra+='Follow the exact heel/toe lift and knee bend for this phase; make it distinct from the stride in target image 3. Keep skirt, fox and palm locations stable, without new wind-blown cloth.'
view='strict RIGHT-facing one-eye profile' if d=='E' else 'front-right view, nose and all toes aiming lower-right'
prompt=f'''Use case: identity-preserve. Asset: ONE single native >=1024x1024 transparent RGBA game WALK frame.
Image 1 is the immutable original identity and costume. Image 2 is approved bright clean rounded Daoist chibi hand-painted rendering style, do not copy any UI. Image 3 is the EDIT TARGET and exact camera/framing/upper-body anchor.
Edit Image 3 into independently drawn walk frame {n:02d}/16. KEEP THE ENTIRE UPPER BODY from ears through sash and fox buckle identical in size, angle, expression, fox position, snowflake position, side assignment and costume; only newly draw the two LEGS with the precise gait below and subtly adjust lower skirt hem as needed. Do not enlarge, translate or mirror the sprite. No identity redesign or arm swing. Camera remains {view}. The viewer sees her anatomical RIGHT side nearer and anatomical LEFT side farther. The LEFT hair ornament stays on the far temple; LEFT arm carries fox on far side; RIGHT near palm carries snowflake.
POSE: {PHASES[n-1]}
RIGHT leg is the NEAR leg. LEFT leg is the FAR leg. Both feet stay on separate parallel tracks; do not cross the knees. Keep exactly TWO short legs and two matching white fur boots. One supporting foot always touches ground, no jumping. Natural compact walking, no running. Grounded sole stays near y=942 at 1024 scale. Head position, body scale and camera remain unchanged. {extra}
Keep the original silver-white short bob, purple eyes, white furry ears, pale lilac embroidered fur robes and short white boots. No new objects or missing accessories. Whole sprite with clean margins. Absolutely transparent alpha background, no white/black background, floor, cast shadow, grid, sheet, labels or text. One frame only. New genuine leg articulation, not duplication or interpolated pose. Highest available hand-painted finish.'''
q['actual_request']['prompt']=prompt; q['intent']='edit target image 3, independently articulate legs; preserve upper body'
(qdir/'prompt.txt').write_text(prompt,encoding='utf-8');(qdir/'request.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'archive':str(qdir),'request':q['actual_request']}))
