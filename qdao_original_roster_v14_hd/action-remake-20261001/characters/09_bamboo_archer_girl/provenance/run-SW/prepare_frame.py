import json,sys,hashlib,datetime
from pathlib import Path
base=Path(__file__).resolve().parents[2]
n=int(sys.argv[1]); k=(n-1)%8
lead='RIGHT' if n<=8 else 'LEFT'; other='LEFT' if n<=8 else 'RIGHT'
phases=[
f'{lead} foot first contacts ground in front along southwest travel direction (toward camera and screen LEFT); {other} leg trails with heel high. Front shin angled naturally, not a straight marching kick.',
f'{lead} support knee compresses, pelvis lowers 12px; {other} heel lifts and knee folds for recovery.',
f'{lead} foot passes beneath pelvis in support; {other} bent knee recovers toward camera. Separate knees and boots in depth; opposite arms pass waist.',
f'{lead} supporting foot stays firmly planted at forefoot, heel starts to rise, knee moves behind the pelvis; {other} knee leads toward southwest. Show weight visibly over the grounded support foot, no floating.',
f'{lead} forefoot toes make LAST firm contact with ground and push off, heel raised; {other} knee leads forward. Pelvis rises only 8px. NOT fully airborne yet.',
f'Brief flight apex, both feet just 15px off ground, {other} front leg extends for landing, {lead} leg remains folded behind. Pelvis rises16px.',
f'Late flight: {other} front shin drops to ground, {lead} folded leg recovers. Pelvis descends but both feet still clear.',
f'{other} forefoot first touches down flat along southwest travel direction, {lead} trailing knee folded. Ground contact at y940 and pelvis only3px high. Set up the next opposite-foot loaded contact without mirrored duplication.'
]
arms1=[
'LEFT bow arm FORWARD with slightly flexed elbow, grip forward at lower rib height on SCREEN RIGHT. RIGHT empty fist BACK beside right hip at SCREEN LEFT, elbow behind.',
'LEFT bow arm begins retracting down from forward swing; RIGHT empty fist begins advancing from right hip.',
'Both elbows pass neutral beside waist, RIGHT empty fist advancing toward camera, LEFT bow grip retracts.',
'LEFT bow arm swings BACK toward screen RIGHT hip, elbow bends, grip LOW by hip. RIGHT empty arm swings FORWARD toward camera at SCREEN LEFT chest height.',
'LEFT bow hand BACK low by left hip screen RIGHT, RIGHT empty forearm FORWARD screen LEFT and raised above waist.',
'LEFT bow arm at BACK endpoint with grip LOW by hip, RIGHT empty fist at FORWARD endpoint chest height; shoulders rotate slightly in opposition to hips.',
'LEFT bow arm reverses forward smoothly from hip; RIGHT empty arm starts moving backward from chest.',
'LEFT bow arm remains behind torso near hip, RIGHT empty arm is forward and compact, ready for LEFT foot contact.'
]
arms2=[
'LEFT bow arm BACK low by left hip screen RIGHT, RIGHT empty arm FORWARD with bent elbow and fist at screen LEFT chest height.',
'LEFT bow arm starts advancing from hip, RIGHT empty arm starts retracting from chest.',
'Both elbows pass neutral at waist, LEFT bow arm advancing, RIGHT empty arm retracting.',
'LEFT bow arm FORWARD at screen RIGHT lower rib height, RIGHT empty fist BACK low by screen LEFT hip.',
'LEFT bow arm forward and slightly raised, RIGHT empty arm back with elbow bent beside hip.',
'LEFT bow arm at FORWARD endpoint, RIGHT empty arm at BACK endpoint, shoulders rotate opposite to hips.',
'LEFT bow arm starts retracting from forward swing, RIGHT empty arm starts advancing from hip.',
'LEFT bow arm FORWARD screen RIGHT with grip near lower ribs; RIGHT empty fist BACK at screen LEFT hip, matching the next RIGHT contact.'
]
prompt=f"""Use case: stylized-concept. Independently draw ONE full-body game animation sprite, run/SW/{n:02}, on genuinely transparent RGBA square canvas at least1024. No grid or sheet.
Image1 fixes exact character identity, 3/4 FRONT SOUTHWEST camera, global size, costume and physical bow. Image2 is PRIMARY APPROVED STYLE reference: clean bright round Taoist chibi hand-painted detail, ivory jade gold materials, short body and short limbs.
Same bamboo archer girl: brown high ponytail, green eyes, bamboo gold/jade leaf hair ornament, ivory-green-gold short robe, white shorts, green-white short boots, yin-yang belt. She faces diagonally TOWARD viewer and screen LEFT, exactly SW reference. BOTH eyes visible; DO NOT turn into left side profile or rear view.
Important handedness: anatomical LEFT arm appears on SCREEN RIGHT and holds ONE COMPLETE LONG BAMBOO BOW at grip. Anatomical RIGHT arm appears on SCREEN LEFT and is EMPTY; quiver stays over anatomical RIGHT shoulder on SCREEN LEFT. Never swap hands or mirror. Bow string connects both tips, no arrow in hands. Keep all bow tips, ponytail, fingers and boots inside frame with margin.
Genuine RUNNING, not walk/idle or march: lean body into southwest motion about10 degrees, actual shoulder/elbow/hip/knee/ankle motion, support compression, toe-off, brief flight, opposite foot landing. Cycle pose phase{k+1}: {phases[k]}
CRITICAL ARM COORDINATION: {(arms1 if n<=8 else arms2)[k]} Arms must have visibly distinct forward and backward positions through the cycle. Bow arm follows its shoulder and elbow, not locked at idle. Cuffs connect each hand to correct shoulder. Long bow may swing subtly but preserve its physical length, all parts and secure grip.
Fixed orthographic camera and scale, root near x470 on1024; virtual ground y940; same head width/height and body proportions as image1. No stage translation, no zoom, preserve true vertical bounce. An airborne pose must not glue both boots to ground. Flowing hair, sleeve and coat respond with small lag, never obscure all limbs.
No effects, particles, arrows, floor shadow, text, UI, extra hands/feet. Single independent drawing of this exact phase."""
refs=['D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/idle/SW.png','D:/work/image/designs/jubaozhai-ui/02-characters.png']
if 4<=n<=11:
 refs.append('D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/walk/SW/01.png')
 prompt+=' Image3 provides the OPPOSITE LEG identity: its front leg comes from the SCREEN RIGHT shorts opening, nearest the BOW. Follow which thigh is forward, NOT its static arms or exact walking joint angles. For this running phase the SCREEN LEFT thigh must fold backward, its boot behind and partly occluded. The front shorts hem must clearly originate on SCREEN RIGHT, with NO large bare forward thigh from the screen left hem.'
 prompt+=' CRITICAL silhouette change relative to frame01: Anatomical LEFT thigh (starts at SCREEN RIGHT shorts opening, on BOW side) swings FORWARD and its KNEE is clearly in front of pelvis at lower SCREEN RIGHT, with its boot closer to viewer. Anatomical RIGHT leg (SCREEN LEFT shorts opening, quiver side) travels BACK beneath/behind torso, with heel high. Do NOT repeat frame01 right-knee-forward silhouette. The EMPTY right fist is near SCREEN LEFT chest; the BOW left hand is LOW beside SCREEN RIGHT hip with elbow pointing backward, not extended outward. This opposite diagonal limb pair is essential.'
if 12<=n<=16:
 prompt+=' The opposite diagonal: anatomical RIGHT thigh from SCREEN LEFT shorts opening swings FORWARD, anatomical LEFT leg at SCREEN RIGHT folds BACK; LEFT bow arm forward, RIGHT empty fist back beside right hip. Show the actual opposite leg and arm pair, not only new coat folds.'
if n>1 and not 4<=n<=11:
 refs.append(str(base/'runtime/run/SW/01.png').replace('\\','/'))
 prompt+=' Image3 is first running frame: exact head size, body scale, palette and ground/root reference only. Do NOT copy its leg or arm pose. Draw the specified current joint positions independently.'
args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True}
thirdrole='opposite anatomical LEFT leg forward identity reference, not static arm pose' if 4<=n<=11 else 'fixed running scale only'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
p=base/'provenance/run-SW'/f'run-SW-{n:02}-{stamp}.request.json';p.parent.mkdir(exist_ok=True)
req={'slot':f'run/SW/{n:02}','phase':phases[k]+' '+(arms1 if n<=8 else arms2)[k],'requestedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**args},'references':[{'file':r,'role':role} for r,role in zip(refs,['fixed identity and SW camera','approved primary painting style',thirdrole])],'referenceMetadata':[{'file':r,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r in refs]}
p.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'request':str(p),'args':args},ensure_ascii=False))

