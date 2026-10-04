import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
r=Path(__file__).resolve().parents[2]
out={'reviewer':'ne_finish independent static review','createdAt':datetime.now(timezone.utc).isoformat(),'dynamicVerified':False,'directions':{}}
for d in ['N','NW']:
 p=r/f'generation/run/{d}/selection-middle4-side2-20261004.json'
 data=json.loads(p.read_text(encoding='utf-8-sig')); rows=data['frames'] if isinstance(data,dict) else data
 frames=[]
 for row in rows:
  src=r/row['source']; digest=hashlib.sha256(src.read_bytes()).hexdigest(); im=Image.open(src)
  assert digest==row.get('sha256',row.get('sourceSha256')); assert im.size==(1254,1254) and im.mode=='RGBA'
  frames.append({'frame':row['frame'],'source':row['source'],'sourceSha256':digest,'supportFoot':row['supportFoot'],'position':row.get('position',row.get('supportPositionAlongRun'))})
 assert len(set(f['sourceSha256'] for f in frames))==16
 out['directions'][d]={'selection':p.relative_to(r).as_posix(),'selectionSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frames':frames,'hardStaticDefects':[],'staticDecision':'no high-confidence hard defect found; support and silhouette accepted with perspective limitations','actualInspection':['full16 fixed-canvas sheet','all16 lower-body sheet']+(['native08-v4 for rear contact and hand occlusion'] if d=='N' else ['native grounding-01-v5 for right front stance','native grounding-08-v1 for right rear contact']),'observations':(['01-08 right stance and09-16 left stance preserved; shoe heel/sole perspective changes support a front-to-rear progression.','03-06 and11-14 are middle support; recovery knees advance across each group.','Left gourd remains in left hand. Empty right arm moves from rear through side to forward during right support, then returns during left support.','No newly observed toe outward rotation; posterior toe-contact tips are partially hidden by heel in pure back view.'] if d=='N' else ['Right01-08 / left09-16 support identities are readable from thigh overlap.','Front01-02 and09-10 shoes lie ahead along NW axis; middle03-06 and11-14 have sole under hip; rear07-08 and15-16 show posterior forefoot contact.','Left hand continuously holds gourd, empty right arm swings and is correctly occluded at forward extreme.','Boot axes follow NW travel, without abrupt sideways toe rotation.']),'limitations':['Transparent sprites do not calibrate the world ground plane.','No browser/client dynamic playback observed; static acceptance cannot verify slipping during world displacement.']}
(r/'review/grounding-fourframes/N-NW-independent-static-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('N/NW independent static source integrity passed: 32 native unique images; no high-confidence hard static defect found')
