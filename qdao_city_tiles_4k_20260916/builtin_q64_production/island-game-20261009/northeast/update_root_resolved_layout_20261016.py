from native_work import *
p=ZONE/'selection-r03_c09.json';s=read(p)
old=[v for v in s.get('pendingIssues',[]) if v.startswith('2026-10-16 layout context audit:')]
s['pendingIssues']=[v for v in s.get('pendingIssues',[]) if v not in old]
s.setdefault('resolvedIssues',[]).append('Original-layout identity correction completed for p01_02_v3 hanging lantern, p01_01_v2 column/terrace and p02_01_v2 column footing/retaining platform; all current left architectural joins checked. Prior incorrect sources preserved unselected.')
s['internalReview']='partial_native_coverage_local_material_repairs_pending'
s['updatedAtUtc']=now();write(p,s)
cp=ZONE/'qa/root-r03c09-checkpoint-20261013.json'
c=read(cp);c.update(currentIds=['r03_c09_p03_01_v2','r03_c09_p04_02'],state='two_independent_native_generations_running',selectedCoreIds=s['cores'],selectedCoreCount=sum(bool(x) for row in s['cores'] for x in row),pendingIssues=s['pendingIssues'],pendingCandidate=None,recordedAtUtc=now());write(cp,c)
print(json.dumps({'selected':13,'currentIds':c['currentIds'],'pendingIssues':len(s['pendingIssues'])}))

