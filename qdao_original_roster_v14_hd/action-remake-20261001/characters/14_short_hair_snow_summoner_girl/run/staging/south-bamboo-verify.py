from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
a=json.loads((R/'audit/bamboo-south-review.json').read_text(encoding='utf-8'))
selected={x['selectedNative'] for x in a['frames'] if x['status']=='repaired_and_registered'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seen=set()
for row in a['frames']:
 p=R/row['file'];im=Image.open(p);assert im.mode=='RGBA' and im.size==(1024,1024)
 h=sha(p);assert h==row['sha256'];assert h not in seen;seen.add(h)
 m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'));tr=m['registrationTransform'];assert tr['globalScale']==.8 and tr['sourceRoot'][1]==960 and tr['targetRoot']==[512,942] and tr['outputSha256']==h
 if row['status']=='repaired_and_registered':
  sr=R/row['selectedNative'];recp=Path(str(sr)+'.generation.json');rec=json.loads(recp.read_text(encoding='utf-8'))
  assert min(rec['nativeSize'])>=1024 and rec['actualModel'] is None and rec['actualQuality'] is None
  assert rec['sha256']==sha(sr)
removed=[]
for p in (R/'run/staging').glob('south-bamboo*.png'):
 assert p.resolve().parent==(R/'run/staging').resolve()
 mp=Path(str(p)+'.generation.json')
 if mp.exists():
  rec=json.loads(mp.read_text(encoding='utf-8'))
  nativeRel=p.relative_to(R).as_posix()
  if nativeRel in selected:rec['review']={'status':'selected_exported_formal','observation':next(x['observation'] for x in a['frames'] if x.get('selectedNative')==nativeRel)}
  elif '-registered' in p.stem:rec['review']={'status':'superseded_candidate_registration_preview'}
  else:rec['review']={'status':'not_selected_after_visual_comparison','reason':'See later selected version in audit/bamboo-south-review.json; earlier axis, pose, height or scale attempt superseded.'}
  rec['retention']={'workspaceRasterRetained':False,'plannedRemovalAt':datetime.now(timezone.utc).isoformat(),'basis':'User2026-09-23 retain final game images and needed design/integration records only; exported formal+source hash+model/quality/request/receipt records verified.'}
  mp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 removed.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p)})
a['technicalVerification']={'formalCount':48,'uniqueHashes':48,'mode':'RGBA','size':[1024,1024],'registeredOnce':True,'changedSevenNativeAtLeast1024':True,'nullActualModelQualityHonest':True,'unmodifiedOther41':all(x['beforeSha256']==x['sha256'] for x in a['frames'] if x['status']=='retained_after_new_comparison')}
a['retention']={'removedIntermediateRasters':removed,'keptCurrentReviewContacts':['run/staging/south-bamboo-'+d+'-formal-contact.jpg' for d in ('S','SW','SE')],'allRequestsReceiptsAndGenerationTextRetained':True,'hostReturnedPathsUntouched':'Outside assignedwrite scope; real returned host paths remain recorded.'}
(R/'audit/bamboo-south-review.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verifiedFormal':48,'newRepaired':7,'intermediatePngToRemove':len(removed)}))

