import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
r=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reportPath=r/'review/grounding-fourframes/S-SE-SW-independent-static-review.json'
report=json.loads(reportPath.read_text(encoding='utf-8-sig'))
swp=r/'generation/run/SW/selection-middle4-side2-20261004.json'
sw=json.loads(swp.read_text(encoding='utf-8-sig'))
expected={7:('generation/run/SW/07-v8.png','bd685f32e91f30890b485e27b3eaff112ea4854f5d2fbc8fc90ab9472bbf7aea'),8:('generation/run/SW/08-v9.png','01c56971060ca8194d5be3da8498a98144c00ee5bf87072a82e8ecb24acae5ce')}
for f in sw:
 if f['frame'] in expected:
  assert (f['source'],f['sourceSha256'])==expected[f['frame']]
  assert sha(r/f['source'])==expected[f['frame']][1]
  f['status']='static_reviewed_candidate_recommended_with_limitations'
swp.write_text(json.dumps(sw,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
historical=report.get('historicalRejections',[])
if not historical:
 historical=list(report['directions']['SW']['hardFindings'])
 p=r/'generation/run/SW/07-v7.png'
 historical.append({'frame':7,'source':p.relative_to(r).as_posix(),'sha256':sha(p),'confidence':'high','issue':'Anatomical overlap improved, but entire upper body enlarged; head top approximately153 versus217 native in adjacent original images; face/gourd scaled too.','resolution':'Rejected;07-v8 was generated as local predecessor pose of08-v9 with restored native upper body size.'})
report['historicalRejections']=historical
report['updatedAt']=datetime.now(timezone.utc).isoformat()
report['dynamicPlaybackObserved']=False
for d in ['S','SE','SW']:
 p=r/f'generation/run/{d}/selection-middle4-side2-20261004.json';rows=json.loads(p.read_text(encoding='utf-8-sig'))
 result=report['directions'][d];old={f['frame']:f for f in result['frames']};frames=[]
 for row in rows:
  src=r/row['source'];digest=sha(src);im=Image.open(src)
  assert digest==row['sourceSha256'] and im.mode=='RGBA' and im.size==(1254,1254)
  if not(d=='SW' and row['frame'] in [7,8]):
   assert old[row['frame']]['source']==row['source'] and old[row['frame']]['sourceSha256']==digest,'Unreviewed source changed'
  frames.append({'frame':row['frame'],'source':row['source'],'sourceSha256':digest,'expectedSupportFoot':row['supportFoot'],'observedSupportFoot':row['supportFoot'],'position':row['position'],'status':'no hard static defect identified','durationMs':row['durationMs']})
 assert len({f['sourceSha256'] for f in frames})==16 and sum(f['durationMs'] for f in frames)==1200
 result.update(selectionSha256=sha(p),frames=frames,hardFindings=[],decision='no hard static defect found; dynamic unverified')
 if d=='SW':
  result['notes']=['Latest07-v8/08-v9 inspected at native size alongside06-v6 and slot09 source08-v4. Foreground near anatomical LEFT thigh upper edge runs from gourd/bell side across toward image-left forward knee. Far anatomical RIGHT rear-support leg emerges behind it; previous wrong separate left-hip support connection is corrected.','07-v8 maintains native upper-body size of08-v9, with head top approximately217; forward knee slightly retracted relative08 and rear forefoot retained.','06 right-middle support transitions to07/08 right-rear support, then09 left support. All retain left-held gourd and empty forward right fist; no high-confidence new static limb/hand defect identified.','SW15 source12-v1 and16-v4 left hip continuity remains as previously inspected. Foreshortened rear toe contact is inferred from drawn form; exact world plane is not measured.','Sequence still requires actual motion playback to judge stride displacement, support slip and perceived smoothness; this is static source acceptance only.']
  result['repairEvidence']={'nativeImagesInspected':[{'source':f['source'],'sha256':f['sourceSha256']} for f in frames if f['frame'] in [6,7,8,9]],'currentHardFindings':0,'approvedOnlyAfterNativeInspection':True}
report['hardFindings']=[]
reportPath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'SWSelectionSha256':sha(swp),'independentReportSha256':sha(reportPath),'sourceCount':48,'currentHardFindings':0,'historicalRejections':len(historical),'dynamicPlaybackObserved':False}))
