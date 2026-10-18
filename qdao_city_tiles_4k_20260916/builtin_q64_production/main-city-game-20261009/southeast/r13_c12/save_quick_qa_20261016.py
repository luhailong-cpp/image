from pathlib import Path
import json,sys,datetime
T=Path(__file__).resolve().parent
v,status,detail=sys.argv[1:4]
assert status in ('pass','failed','pending_local')
r=T/'review'/('quick-'+v)
q=json.loads((r/'evidence.json').read_text(encoding='utf-8-sig'))
q.update(reviewStatus='root_actual_native_and_core_joins_viewed',geometryStatus='local_geometry_pass' if status=='pass' else ('pending_local_repair' if status=='pending_local' else 'failed'),notes=detail,formalAccepted=False,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (r/'root-visual-qa.json').open('x',encoding='utf-8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
if status=='failed':
 p=T/'active-native-map.json';a=json.loads(p.read_text(encoding='utf-8-sig'))
 patch=v.split('_v')[0]
 assert a[patch]==v
 with (r/'active-before-unselect.json').open('x',encoding='utf-8') as f:json.dump(a,f,indent=2)
 del a[patch];p.write_text(json.dumps(a,indent=2),encoding='utf-8')
 p=T/'progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
 d.update(activeNativeCount=len(a),status=patch+'_retained_failed_pending_repair',formalAccepted=False)
 p.write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps({'version':v,'status':status,'formalAccepted':False}))

