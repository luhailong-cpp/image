import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
stem=sys.argv[1]
p=ROOT/'work'/(stem+'.png.generation.json')
r=json.loads(p.read_text(encoding='utf-8'))
refs=[('q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png','authoritative identity'),('qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/'+sys.argv[2]+'.png','direction camera and proportion'),('designs/jubaozhai-ui/02-characters.png','approved primary painted style')]
if len(sys.argv)>3:
 refs.extend((x,'new run frame continuity reference') for x in sys.argv[3:])
r['references']=[{'path':str((REPO/x).resolve()),'role':role,'sha256':hashlib.sha256((REPO/x).read_bytes()).hexdigest()} for x,role in refs]
r['submittedParameters']['referenced_image_paths']=[x['path'].replace('\\','/') for x in r['references']]
r['submittedParameters']['prompt']=(ROOT/r['prompt']).read_text(encoding='utf-8')
r['evidence']['toolOutputHint']='Generated images saved to '+r['evidence']['hostOutputPath']
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p)
