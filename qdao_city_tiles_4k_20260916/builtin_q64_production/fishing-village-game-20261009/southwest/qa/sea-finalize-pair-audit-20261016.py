import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v2=read(Q/'pair-r14c06-r14c07-v2-trace.json');trial=read(Q/'pair-r14c06-r14c07-v3trial-trace.json');t=read(Q/'pair-r14c06-r14c07-v3-trace.json')
checks=[]
for i,a in enumerate(t['qa']):
 viewed=trial['qa'][i] if i==2 else t['qa'][i] if i==3 else v2['qa'][i]
 assert sha(a['path'])==a['sha256']==viewed['sha256']
 checks.append({'file':a['path'],'sha256':a['sha256'],'status':'passed','viewedAtNativeResolution':True,'identicalViewedFile':viewed['path'],'notes':'Continuous organic water ripples and white highlights; previous vertical tone wall absent; no gap or rectangular edge.'})
for i,a in enumerate(t['repairs']):
 viewed=trial['repairs'][i]['after'] if i==2 else v2['repairs'][i]['after']
 assert sha(a['after']['path'])==a['after']['sha256']==viewed['sha256']
 checks.append({'file':a['after']['path'],'sha256':a['after']['sha256'],'status':'passed','viewedAtNativeResolution':True,'identicalViewedFile':viewed['path'],'notes':'Repair perimeter and crossing water contours continuous; existing foam and rocks remain coherent.'})
left,right=[rgb(x['context']['path']) for x in t['tiles']]
assert np.array_equal(left[:,4096:4326],right[:,:230])
for r in t['provenance']: assert sha(r['path'])==r['sha256']
a={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed','scope':'r14_c06 and r14_c07 internal native artwork and mutual shared edge; global outer joins and runtime not accepted','trace':ref(Q/'pair-r14c06-r14c07-v3-trace.json'),'tiles':t['tiles'],'nativeChecks':checks,'internalAuditsReusedOutsideChangedSharedEdge':[ref(Q/'r14_c06-internal-visual-audit-v1.json'),ref(Q/'r14_c07-internal-visual-audit-v2.json')],'changedRegionCoverage':'Four full native 1254 repair after-crops plus five final native shared-edge crops cover repaired water, both perimeters and all segment intersections. Unchanged interior source pixels retain previous internal visual approvals.','improvements':['Removed four-segment vertical water tone/ripple-scale discontinuity with native AI repairs.','Moved water3 top hard-seam selection band below a small angular mismatch at the water2/water3 crossing; same native input sources, no resampling or blending.'],'mechanicalValidation':t['validation']|{'shared230PixelHaloExactEquality':True,'reusedViewedCropsHashIdentical':True,'allProvenanceHashesUnchanged':True},'unresolvedIssues':[],'externalJoins':{'north':'pending final neighboring contexts from delegated owner','r14_c06_west':'pending adjacent artwork','r14_c07_east':'pending adjacent artwork','south':'map exterior; no adjacent world tile'},'runtimeValidation':'not performed','formalMapAcceptance':False}
p=Q/'pair-r14c06-r14c07-v3-art-audit-v1.json';write(p,a)
write(Q/'sea-finish-20261016-handoff-v1.json',{'createdAtUtc':a['createdAtUtc'],'worker':'/root/sea_finish_1016','status':'current_two_tile_batch_complete_internal_and_mutual_join','tiles':t['tiles'],'trace':a['trace'],'audit':ref(p),'inflight':None,'readyForRootVersionedExport':True,'sharedIndexLedgerProgressWritten':False,'next':'Await root coordinate allocation to prevent conflicts.'})
print(json.dumps({'trace':a['trace'],'audit':ref(p),'tiles':t['tiles'],'qaCount':len(checks),'sharedHaloExact':True}))

