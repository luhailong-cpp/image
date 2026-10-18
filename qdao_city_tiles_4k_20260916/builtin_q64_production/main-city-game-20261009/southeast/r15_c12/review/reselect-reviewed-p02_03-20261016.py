from pathlib import Path
import hashlib,json,datetime
T=Path(__file__).resolve().parent.parent
O=T/'review'/'p02_03-recheck-after-upper-fix-20261016'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v='p02_03_v20261016T192951_c60a3f55'
e=read(O/'evidence.json')
for s in e['sources']+e['outputs']:assert sha(Path(s['path']))==s['sha256']
mapping=read(T/'active-native-map.json')
assert 'p02_03' not in mapping
assert mapping['p01_03']=='p01_03_v20261016T203925_nativefix_c5d5b00d'
assert mapping['p03_03']=='p03_03_v20261016T200306_01ce9fc6'
qa={'version':v,'status':'local_pass','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evidence':str(O/'evidence.json'),'evidenceSha256':sha(O/'evidence.json'),'formalAccepted':False,'mayPropagate':True,'priorQAUnchanged':str(T/'review'/'quick-qa-20261016'/v/'visual-qa.json'),'notes':'Original-size top and bottom core pairs actually viewed after upper p01_03 correction. Top red column and timber jamb continuous; removed premature upper collar resolves previous failure without regenerating this native. Bottom stair/riser and side coping join coherently, material and tread plane transitions remain watch for final tile QA. Existing right-core QA reused unchanged. Current neighbor hashes are bound by evidence; original failed QA remains preserved.'}
write(O/'visual-qa.json',qa)
write(O/'selection-before.json',mapping)
mapping['p02_03']=v
(T/'active-native-map.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
p=read(T/'progress.json');p.update(activeNativeCount=len(mapping),currentPatch='p04_03',status='seven_natives_quick_reviewed_pending_continuation',formalAccepted=False)
(T/'progress.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
report={'selectionChanged':True,'activeNativeCount':len(mapping),'nativeUnchanged':True,'selected':v,'qa':str(O/'visual-qa.json'),'qaSha256':sha(O/'visual-qa.json'),'activeMapSha256':sha(T/'active-native-map.json'),'formalAccepted':False}
write(O/'selection-after.json',report)
print(json.dumps(report))
