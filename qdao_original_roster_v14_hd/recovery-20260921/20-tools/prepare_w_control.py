from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,sys
from prepare_n_ne_request import PHASES
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3]
REC=ROOT/'qdao_original_roster_v14_hd/recovery-20260921'
p=argparse.ArgumentParser();p.add_argument('frame');p.add_argument('--version',type=int,default=1);p.add_argument('--extra',default='');a=p.parse_args()
idle=a.frame=='idle';n=0 if idle else int(a.frame);name=f'idle-W-v{a.version}' if idle else f'W-{n:02d}-v{a.version}'
dest=REC/'20-generation'/name;dest.mkdir(parents=True,exist_ok=False)
refs=[REC/'20-generation/W-01-v2/raw.png',REC/'20-reference/identity-inspection-1024.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
pose='Independent relaxed standing pose. Both feet grounded side by side below pelvis, knees straight but relaxed; no step, no stride. Fresh dedicated idle drawing.' if idle else PHASES[n]
prompt=f'''Create ONE complete transparent-alpha full-body animation sprite, 20_star_formation_master_girl, native square at least 1024x1024. ONE pose only, no sheet.
Image 1 is the PRIMARY VIEW/CAMERA/PROPORTION reference: preserve its precise PURE LEFT SIDE profile of the whole character, narrow side torso, one near shoulder, hands close together ahead of chest. DO NOT turn torso toward viewer. Image 2 is original identity: keep her face, crown, long straight hair, black/red/ivory/gold robe, boots. Image 3 is the approved PRIMARY PAINTING STYLE: bright clean rounded refined hand-painted Daoist chibi materials, no UI.
Independently articulate this new frame; image1 provides view and identity, NOT the leg pose. Requested {'IDLE' if idle else f'WALK phase {n:02d}/16'}: {pose}
W direction means both boot toes and nose point SCREEN LEFT. Anatomical LEFT is the NEAR leg facing camera; anatomical RIGHT is the FAR leg away from camera. Show real alternating leg articulation, at least one supporting foot, no run/jump. Keep near leg contours in front of far leg wherever they overlap; do not swap which leg is near. Let hem move to expose both complete boots.
RIGHT/far hand holds the same circular gold/black star astrolabe. LEFT/near hand holds exactly three star cards. Keep hands close overlapping before torso as image1, no open frontal portrait pose. Preserve calm hair and tassels, consistent crown and body scale, warm lighting. Body axis x512, grounded sole baseline y942, crown top near y65 proportional to a 1024 square. Full equipment/crown/hair/toes with clear margin.
Real alpha transparency, no floor, shadow, background, checkerboard, text, glow, color fringe. Not a mirror, warp, interpolation or copied pose. {a.extra}'''
(dest/'prompt.txt').write_bytes(prompt.encode('utf-8'))
refs=[str(x).replace('\\','/') for x in refs]
config=json.loads((REC/'20-generation/idle-S-v1/request.json').read_text(encoding='utf-8'))['configSnapshot']
request={'character_id':'20_star_formation_master_girl','slot':'idle/W.png' if idle else f'walk/W/{n:02d}.png','attempt':name,'source_is_single_frame':True,'route':'builtin','started_at':datetime.now(timezone.utc).isoformat(),'configSnapshot':config,'submittedParameters':{'model':None,'quality':None},'actual_request':{'prompt':prompt,'referenced_image_paths':refs},'reference_roles':dict(zip(refs,['pure side camera and proportion, not pose','original identity','approved primary painting style'])),'reference_bindings_at_start':[{'path':x,'sha256':hashlib.sha256(Path(x).read_bytes()).hexdigest()} for x in refs]}
(dest/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'attempt':str(dest),'prompt':prompt,'referenced_image_paths':refs},ensure_ascii=False))
