from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
H=Path(r'C:/Users/luyua/.codex/generated_images/01a100fd-8609-7732-bf3e-64986ee86f77')
bases={"S":["exec-75ca1b62-88f1-458f-af00-444903886e70.png","exec-5262e05a-cc1a-44fd-9338-1f1b57a578cc.png"],"SW":["exec-40bd1bb9-6e2b-4e03-b51b-99da2b7d04cc.png","exec-9a7bb81b-8e4e-445a-bb26-0f63fcf65c93.png"],"SE":["exec-020bc2b6-78fd-4936-8fe5-be93ee46ec02.png","exec-f7245916-df41-4bad-bd58-1f3f63a05316.png"]}
jobs=[]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for d in ('S','SW','SE'):
 for n in (4,5,6,7,8,12,13,14,15,16):
  half=0 if n<=8 else 1; p=n if half==0 else n-8; leg='LEFT' if half==0 else 'RIGHT'
  support={'S':('screen-right','screen-left'),'SW':('far-side, screen-right hip','near-side, screen-left hip'),'SE':('near-side, screen-right hip','far-side, screen-left hip')}[d][half]
  axis={'S':'toward viewer, straight down the image','SW':'diagonally toward lower left','SE':'diagonally toward lower right'}[d]
  rear={'S':'higher in the image along depth, NOT sideways','SW':'upper right along the ground plane','SE':'upper left along the ground plane'}[d]
  phase={4:'P2b: the support sole is directly beneath the pelvis and fully bears weight. Knee has begun extending after compression, still softly flexed. Other knee passes closely in front while its boot stays lifted.',
   5:'P3a: support contact has moved a little BEHIND the pelvis along the travel axis. Full forefoot and heel remain grounded, support shin tilts forward, hip has passed the planted ankle. Other knee advances forward, boot lifted.',
   6:'P3b: support foot is visibly farther behind the pelvis than P3a, still solidly weight-bearing with the full forefoot grounded; heel only just starts to release. Support knee extends; opposite knee rises a little farther forward.',
   7:'P4a: support contact lies well behind the pelvis, leg extends backward to push. Heel is raised but the ball and toe visibly press the ground; ankle plantar-flexes. Other leg extends forward with its boot still suspended, preparing next landing.',
   8:'P4b: the SAME support toes remain on the ground at the rearmost contact. Heel higher, leg pushes through final toe contact, not airborne. Opposite heel reaches forward/down almost to next landing, still separate from ground.'}[p]
  arm={4:'low and slightly behind the torso',5:'at the rear swing extreme, elbow softly bent',6:'beginning to swing down/forward beside waist',7:'swinging forward, forearm bent',8:'near forward extreme with palm carrying the crystal'}[p]
  if half: arm={4:'forward with elbow softly bent',5:'at the forward extreme',6:'beginning to swing downward/back',7:'swinging backward near the waist',8:'near the rear extreme, elbow softly bent'}[p]
  prompt=f'Precise local pose edit of IMAGE 1, a game sprite. Preserve its exact cranium and face width, eye size, fox, torso proportions, white/pale-lilac colors and canvas framing. Do not enlarge or resaturate the head or zoom the figure. Render one new distinct walking/running contact pose, direction {d}, moving {axis}. The anatomical {leg} leg ({support}) is the ONLY WEIGHT-BEARING SUPPORT LEG for this frame. {phase} Behind means {rear}; no lateral splay. Both boot long axes and knees follow {axis}, never toe-out. Make the support knee/ankle and planted flattened sole/pressing forefoot unambiguously show weight on an invisible ground plane. Keep the support foot connected to its correct thigh; never switch legs or float both feet. There is NO flight interval in this cycle. Keep upper body at image1 size and position; redraw lower limbs anatomically, not shifting the whole character to force contact. Anatomical LEFT arm continues to cradle the single fox. Exactly one RIGHT arm, connected shoulder-sleeve-wrist, holds the single crystal {arm}; move this one sleeve with the arm, no extra empty sleeve. Image2 is the bamboo girl movement-direction and aligned shoe-axis reference only; do not copy her flight or clothing. Image3 is approved painting style. Transparent square native at least1024, no floor, shadow, labels or text. Only one sprite.'
  label=f'south-bamboo-contact-{d}-{n:02}-v1'
  args={'prompt':prompt,'referenced_image_paths':[str(H/bases[d][half]),str(R.parent/f'09_bamboo_archer_girl/runtime/run/{d}/{n:02}.png'),'D:/work/image/designs/jubaozhai-ui/02-characters.png'],'transparent_background':True}
  meta=json.loads((R/f'run/{d}/{n:02}.png.generation.json').read_text(encoding='utf-8-sig'))
  reg=json.loads((R/f'run/{d}/registration.json').read_text(encoding='utf-8-sig'))
  baseNum=3 if half==0 else 11
  baseRow=next(x for x in reg['frames'] if x['file']==f'run/{d}/{baseNum:02}.png')
  req={'label':label,'recordedAt':datetime.now(timezone.utc).isoformat(),'direction':d,'frame':n,'supportLeg':leg,'phase':phase,'sourceMode':'accepted_native_local_contact_pose_edit','targetNative':args['referenced_image_paths'][0],'baseNeighbor':f'run/{d}/{baseNum:02}.png','suggestedSourceRoot':baseRow['srcRoot'],'previousGenerationRecord':meta['derivedFrom']['generationRecord'],'previousOfficialSha':sha(R/f'run/{d}/{n:02}.png'),'referenceRoles':['14 accepted original native edit target; upper body appearance/canvas locked','09 actual same-direction movement/shoe axis guide, not flight phase','approved painting style'],'submittedParameters':{'model':None,'quality':None,**args}}
  (R/f'provenance/{label}.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
  (R/f'prompts/{label}.txt').write_text(prompt,encoding='utf-8')
  jobs.append({'label':label,'args':args})
(R/'run/staging/south-bamboo-contact-jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(jobs))

