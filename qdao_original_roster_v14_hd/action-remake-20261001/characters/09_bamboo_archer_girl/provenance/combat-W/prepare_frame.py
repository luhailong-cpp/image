import json,sys,hashlib,datetime
from pathlib import Path
base=Path(__file__).resolve().parents[2]
n=int(sys.argv[1]); action=sys.argv[2] if len(sys.argv)>2 else 'cast'
plan=json.loads(Path('D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/09_bamboo_archer_girl/production/animation-plan.json').read_text(encoding='utf-8-sig'))
f=next(g for g in plan['groups'] if g['action']==action and g['direction']=='W')['frames'][n-1]
tmpl=json.loads((base/'provenance/combat-W/cast-W-03.request.json').read_text(encoding='utf-8-sig'))
prompt=tmpl['submittedParameters']['prompt'].split('Image3 is preceding continuity reference.')[0]
prompt+='Image3 is preceding animation frame for joint continuity, but Image1 remains the fixed identity/style and scale reference. Keep body, head, bow size, camera angle, feet baseline consistent. Animate actual joints only.\\n'
prompt+=f"Animation {action}/W/{n:02}, phase {f['phase']}. Pose: {f['pose']} Transition from previous: {f['deltaFromPrevious']} Transition to next: {f['transitionToNext']}\\n"
if action=='cast' and 5<=n<=9:
 prompt+='Archery mechanics critical: Exactly ONE arrow points to screen LEFT. Its nock, the anatomical RIGHT fingertips, and the vertex where the two bowstring segments meet are EXACTLY the same single point. Upper string connects upper bow tip to this nock; lower string connects lower tip to the SAME nock. No extra vertical string remains between bow tips while drawing. Left hand holds grip at arrow rest; do not let fingers overlap wrong hand.\\n'
if action=='cast' and n>=10:
 prompt+='After release: NO arrow in either hand or beside bow, no detached projectile. String has returned to a straight line connecting both bow tips, no longer attached to right hand.\\n'
if n==4: prompt+='RIGHT fingers pinch the rear nock of ONE arrow taken from RIGHT shoulder, arrow shaft angles over shoulder, not yet nocked. No arrow emerging from fingers wrong-way.\\n'
if n==5: prompt+='Very shallow draw only: right hand and arrow nock close to left grip; do NOT jump to cheek/full draw.\\n'
if n==6: prompt+='Quarter draw only: right hand and arrow nock between left grip and face but still distinctly ahead of face. The preceding reference05 is too deep: DO NOT preserve its hand position. On 1024 canvas LEFT grip x=230,y=485, RIGHT pinching fingertips with nock x=330,y=485; face stays around x=460. Right forearm reaches FORWARD to screen left across upper chest, not backward to cheek. String V is very shallow. Upper/lower string endpoints x about300, V vertex x330. Arrow nock at x330 and its tip to screen left.\\n'
if n==7: prompt+='Half draw: right hand and nock about halfway from extended left grip to cheek; distinct gradual movement from frame06.\\n'
if n==8: prompt+='Three-quarter draw, right fingertips just forward of cheek, not yet full anchor.\\n'
if n==9: prompt+='Full draw, right fingertips anchor at cheek. Left shoulder down, wrist neutral, short legs firmly supporting the body.\\n'
if n>=13: prompt+='Keep right hand descending toward waist naturally; do NOT begin reaching for another arrow. Left hand returns long bow to upright idle, its physical length unchanged.\\n'
prompt+='One independent actual animation pose. Preserve proportions and original short limbs. Fully transparent canvas, no text, shadows, effects, particles or duplicate appendages. Full bow tips and boots inside canvas.'
refs=[tmpl['submittedParameters']['referenced_image_paths'][0],tmpl['submittedParameters']['referenced_image_paths'][1],str(base/'runtime'/action/'W'/f'{n-1:02}.png').replace('\\','/')]
args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True}
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
p=base/'provenance/combat-W'/f'{action}-W-{n:02}-{stamp}.request.json'
req={'slot':f'{action}/W/{n:02}','phase':f['phase'],'requestedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**args},'references':[{'file':r,'role':role} for r,role in zip(refs,['fixed identity and W camera','approved primary painting style','previous pose continuity only'])],'referenceMetadata':[{'file':r,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r in refs]}
p.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'request':str(p),'args':args},ensure_ascii=False))

