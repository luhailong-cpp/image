import json,sys,hashlib,datetime
from pathlib import Path
base=Path(__file__).resolve().parents[2]
action,n,direction=sys.argv[1],int(sys.argv[2]),sys.argv[3]
instruction=Path(sys.argv[4]).read_text(encoding='utf-8')
refs=[str(base/'runtime'/action/direction/f'{n:02}.png').replace('\\','/'),'D:/work/image/designs/jubaozhai-ui/02-characters.png']
if action=='cast' and n==6 and direction=='W':
 refs[0]=str(base/'runtime/cast/W/05.png').replace('\\','/')
if action=='run' and n==8:
 refs[0]=str(base/'runtime/run/SW/09.png').replace('\\','/')
if action=='run' and n==5:
 refs[0]=str(base/'runtime/run/SW/06.png').replace('\\','/')
if action=='run' and n==4:
 refs[0]=str(base/'runtime/run/SW/05.png').replace('\\','/')
if action=='run' and n in (4,12,13):
 refs.append(str(base/'runtime/run/SW'/f'{n-1:02}.png').replace('\\','/'))
 instruction+=' Image3 is the immediately previous corrected phase. Advance its leg/arm joints into the requested next support/toe-off phase while retaining which leg supports. Do not copy or mirror Image3.'
if action=='run' and n in (8,9):
 refs.append(str(base/'runtime/run/SW/10.png').replace('\\','/'))
 instruction+=' Image3 is the later LEFT-foot support/compression frame10. It identifies which leg is planted and the real ground contact level, but draw the earlier contact phase requested here, not its compression pose.'
prompt='Use case: precise-object-edit. Image1 is the exact edit target; image2 is approved PRIMARY painting style. Make ONE full-body transparent RGBA sprite, native at least1024. Preserve camera, character face/head, hair, costume, scale and overall root position. Correct only the specified joints/object details by independently drawing them. Never mirror or deform the picture. No text, particles, floor shadow or extra appendages. '+instruction
args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True}
group='run-SW' if action=='run' else 'combat-W'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
p=base/'provenance'/group/f'{action}-{direction}-{n:02}-repair-{stamp}.request.json'
req={'slot':f'{action}/{direction}/{n:02}','phase':instruction,'requestedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**args},'references':[{'file':r,'role':role} for r,role in zip(refs,['exact edit target','approved primary painting style','previous corrected support phase'])],'referenceMetadata':[{'file':r,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r in refs]}
p.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'request':str(p),'args':args},ensure_ascii=False))
