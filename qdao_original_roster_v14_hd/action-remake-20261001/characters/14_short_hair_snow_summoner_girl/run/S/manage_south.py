from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,hashlib,shutil,importlib.util
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parents[2]
OLD=Path('D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/14-delivery-preview/assets')
REPO=Path('D:/work/image')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
phases=[
'LEFT foot contacts FORWARD, right leg trails and heel rises. Left knee begins flexing; body leans into running. Anatomical RIGHT arm swings FORWARD with its palm and crystal, elbow bent around75degrees; crystal slightly in front of lower chest.',
'LEFT leg absorbs landing with knee flexed, hip lowers12px. RIGHT heel curls backward toward skirt, thigh trails. RIGHT arm passes forward peak and starts backward, palm/crystal move with forearm.',
'LEFT foot is under pelvis supporting compressed body; RIGHT bent knee passes under hips, toe clears ground. RIGHT arm passes downward beside waist; palm/crystal start moving behind the right-side waist. Slight torso counterrotation.',
'LEFT leg pushes off on its forefoot behind hips; RIGHT bent thigh drives forward. Body starts rising. RIGHT arm with its palm/crystal swings BACKWARD beside the right hip; original chest-level palm must be removed and replaced.',
'FIRST FLIGHT: BOTH boots airborne above virtual floor by25px, RIGHT thigh forward with bent knee, LEFT thigh trailing with knee curling back. Body rises24px. RIGHT elbow and palm/crystal swing BACK beside hip, not at original display position.',
'LATE FIRST FLIGHT: RIGHT lower leg reaches forward preparing landing, LEFT heel tucks behind. Both boots still clear the floor15px. Torso begins descending. RIGHT palm/crystal remain rearward beside hip, elbow soft.',
'RIGHT foot reaches forward just above ground, toe slightly up, LEFT leg stays bent back with heel raised. Body descending. RIGHT palm/crystal reach rear swing peak; shoulder protects fox and counterrotates.',
'RIGHT foot is a few pixels above contact, right knee extends softly and LEFT knee begins traveling forward beneath hips. Body nearly at landing height. RIGHT palm/crystal begin returning from rear hip, clear altered arm silhouette.',
'RIGHT foot contacts FORWARD, LEFT leg trails with heel up. Right knee begins flexing; forward run lean. Anatomical RIGHT palm/crystal remain behind right waist and begin forward swing; replace original display hand.',
'RIGHT leg absorbs landing, knee flexed; pelvis lowers12px. LEFT heel curls back behind the skirt. RIGHT arm leaves rear peak and swings forward beside waist with palm and crystal.',
'RIGHT foot under pelvis supports compressed body. LEFT bent knee passes beneath hips and toe clears ground. RIGHT arm with palm/crystal passes upward and forward; shoulder counterrotation visible.',
'RIGHT forefoot pushes off behind hips; LEFT thigh drives forward with bent knee. Body rises. RIGHT palm/crystal swing FORWARD in front of lower chest, elbow bent, wrist natural.',
'SECOND FLIGHT: BOTH boots airborne25px; LEFT thigh forward with knee bent, RIGHT thigh trailing with knee curled. Body rises24px. RIGHT palm/crystal forward in a compact running swing; LEFT arm cradles fox with counterrotating shoulder.',
'LATE SECOND FLIGHT: LEFT lower leg reaches forward preparing landing, RIGHT heel tucks behind. Both boots clear floor15px; torso begins descending. RIGHT palm/crystal remain forward, elbow soft.',
'LEFT foot reaches forward just above ground, toe a little up; RIGHT knee stays bent back. Body descends. RIGHT palm/crystal reach forward swing peak; short robe and tassels lag naturally.',
'LEFT foot almost contacts a few pixels above floor, LEFT knee softly extends and RIGHT knee starts traveling beneath hips. Torso returns toward frame01. RIGHT palm/crystal begin backward return from forward swing peak.'
]
directions={'S':'FRONT view facing camera and running toward screen BOTTOM. Anatomical LEFT is screen RIGHT (fox side); anatomical RIGHT is screen LEFT (crystal side).','SW':'FRONT-LEFT three-quarter view, running diagonally toward screen BOTTOM-LEFT, match reference camera. Left hairpin visible on near side.','SE':'FRONT-RIGHT three-quarter view, running diagonally toward screen BOTTOM-RIGHT, match reference camera. Left hairpin on far side, naturally partly occluded.'}
if sys.argv[1]=='prepare':
 d,n=sys.argv[2],int(sys.argv[3]);label=f'run-{d}-{n:02d}-v1';source=OLD/'walk'/d/f'{n:02d}.png'
 prompt='Use case: precise-object-edit. Reference1 is the exact old WALK frame to correct into a RUN; reference2 is the approved bright clean rounded Daoist chibi hand-painted finish. Change anatomical arms and legs to a genuine independent RUN pose while preserving this exact snow girl face, silver bob/furry ears/purple eyes, white-lilac fur-trimmed robe, fox buckle, ornaments, camera and scale. '+directions[d]+' EXACTLY TWO arms and TWO hands: anatomical LEFT arm securely cradles ONE white fox; the ONLY RIGHT hand is the open palm carrying ONE blue crystal. REPLACE the original right arm/palm position with the running swing, moving the crystal together; ERASE its old displayed position. Never add a third hand or fist. No girl tail. Frame'+str(n).zfill(2)+' of16,480ms run cycle: '+phases[n-1]+' Fixed1024 square, virtual floor942; preserve real body rise/fall and airborne boots; do not fit bbox or force lowest foot to floor. Full ears/boots/charms uncropped. Genuine transparent alpha, no scenery, ground disc, shadow, particles, text or collage. Fox held securely; left carrying shoulder and elbow counterrotate subtly rather than freezing both arms.'
 prompt+=' Layout ratios apply to whatever native square size is returned: virtual ground at92% canvas height; head top at8%; hip joint midpoint near(53%,70%). Keep camera distance and head size identical to reference, never zoom in. Use compact running arm swing, not wide presentation; only two sleeve openings, each belongs to its corresponding hand. Flying coat panels have straight hems, never an extra fur-ring empty cuff. '
 if n in (2,3,10,11):prompt+=' CLEAR SINGLE SUPPORT: planted foot is flat beneath pelvis at virtual floor92%, knee flexes and body compresses. The opposite boot is up beside the supporting calf, not stretched forward. '
 if n in (4,12):prompt+=' CLEAR TOE-OFF: supporting forefoot/toe touches virtual floor at92% with heel raised, ankle extends; opposite thigh reaches forward and knee is lifted, boot well clear. '
 if n in (5,6,13,14):prompt+=' CLEAR SUSPENSION: BOTH KNEES BENT, BOTH BOOTS are shortened upward into body silhouette; no straight downward leg. Both boot bottoms must end at84%-87% canvas height, with obvious empty gap to virtual floor92%. Body rises slightly rather than enlarging. '
 if d=='SW':prompt+=' In the SW image the FOX MUST stay on SCREEN RIGHT of the torso, in the same left arm as reference. The crystal hand MUST stay on SCREEN LEFT of torso. For backward swings tuck that far right elbow behind the torso and keep a small glimpse of the same right palm/crystal down beside screen-left waist; do not swap the fox and crystal across the body. '
 args={'prompt':prompt,'referenced_image_paths':[str(source),str(REPO/'designs/jubaozhai-ui/02-characters.png')],'transparent_background':True}
 req={'label':label,'generatedAt':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**args},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality selector or returned confirmation','derivedCreativeFrom':{'file':str(source),'sha256':sha(source),'priorGenerationRecord':str(source)+'.generation.json','use':'target oldwalk frame; replace incorrect gait/arm phase but retain identity/camera/costume'},'references':[{'file':p,'sha256':sha(p),'role':role}for p,role in zip(args['referenced_image_paths'],['edit-target-old-walk','approved-primary-style'])]}
 save(BASE/'provenance'/f'{label}.request.json',req)
 (BASE/'prompts'/f'{label}.txt').write_text(prompt,encoding='utf-8')
 print(json.dumps({'label':label,'args':args},ensure_ascii=False))
elif sys.argv[1]=='ingest':
 d,n,label,source=sys.argv[2:6];source=Path(source);im=Image.open(source);im.load()
 if min(im.size)<1024:raise ValueError('native below1024')
 raw=BASE/'run'/d/'native'/f'{label}.png';raw.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,raw)
 req=json.loads((BASE/'provenance'/f'{label}.request.json').read_text(encoding='utf-8-sig'))
 gen={**req,'status':'generated','file':raw.relative_to(BASE).as_posix(),'sha256':sha(raw),'width':im.width,'height':im.height,'mode':im.mode,'format':'PNG','hostOutput':str(source),'receipt':f'provenance/{label}.receipt.json','recordedAt':datetime.now(timezone.utc).isoformat()}
 save(str(raw)+'.generation.json',gen)
 dest=BASE/'run'/d/f'{int(n):02d}.png'
 if dest.exists():raise FileExistsError(dest)
 spec=importlib.util.spec_from_file_location('export',BASE/'tools/export_frame.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.run(raw,dest)
elif sys.argv[1]=='priorcontact':
 d=sys.argv[2];out=BASE/'run'/d;out.mkdir(parents=True,exist_ok=True)
 sheet=Image.new('RGB',(1024,1088),(35,41,49))
 for i in range(16):
  im=Image.open(OLD/'walk'/d/f'{i+1:02d}.png').convert('RGBA').resize((256,256))
  tile=Image.new('RGBA',(256,272),(35,41,49,255));tile.alpha_composite(im,(0,16));ImageDraw.Draw(tile).text((4,2),f'OLD WALK {d} {i+1:02d}',fill='white');sheet.paste(tile.convert('RGB'),((i%4)*256,(i//4)*272))
 sheet.save(out/'prior-walk-contact.png')
 print(str(out/'prior-walk-contact.png'))

