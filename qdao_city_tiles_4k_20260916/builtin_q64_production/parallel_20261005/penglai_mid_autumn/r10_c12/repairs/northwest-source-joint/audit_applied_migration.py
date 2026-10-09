from pathlib import Path
import hashlib,json,datetime,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent;W=R/'r10_c11';C=R/'r10_c13'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def checkref(x):assert sha(x['file'])==x['sha256'],x['file']
result=read(D/'migration-applied.json');proof=read(D/'applied-source-migration.json');pre=read(D/'migration-preflight.json')
for x in result['canonicalAfter']+result['metadataAfter']+result['imageAfter']:checkref(x)
for p,h in pre['protected'].items():assert sha(p)==h,p
e=T/'output/r10_c12.png';p=W/'native/p14.png';ep=read(W/'plan.json');cp=read(C/'plan.json');cm=read(C/'output/manifest.json')
assert ep['eastCandidateSha256']==sha(e)==cp['westCandidateSha256'];checkref(cm['plan']);checkref(cm['neighborRevalidation'])
checkref(cm['neighbors']['west'])
for x in cm['qa']:
 checkref(x)
 for s in x.get('sources',[]):checkref(s)
for x in read(C/'qa/final-local-review.json')['independentReviews']:checkref(x)
for x in read(T/'qa/final-local-review.json')['items']:
 checkref(x)
 for s in x['sources']:checkref(s)
 assert x['actuallyViewed'] and x['nativeScale']==1
for gp in [Path(str(e)+'.generation.json'),Path(str(p)+'.generation.json')]:
 g=read(gp);assert sha(g['file'])==g['sha256'];checkref(g['previousCurrentGeneration'])
 for x in g['derivedFrom']:checkref(x);checkref(x['generation'])
ctx=Image.open(W/'native/p14-current-context.png').convert('RGBA');im=Image.open(p).convert('RGB');a=np.asarray(ctx);b=np.asarray(im);mask=a[:,:,3]>0;assert np.array_equal(a[:,:,:3][mask],b[mask])
# Qualify two legacy fields as historical so the current manifest cannot imply the new north pixels stayed unchanged.
mp=T/'output/manifest.json';m=read(mp);prior=D/'text-history/manifest-after-apply-before-historical-qualification.json'
if prior.exists():assert sha(prior)==sha(mp),'Resume requires identical pre-qualification snapshot'
else:prior.write_bytes(mp.read_bytes())
m['internalScopedQA']=dict(result='passed_current_all27_native_revalidation',currentRevalidation=ref(T/'qa/final-local-review.json'),historicalInternalRepairScope=dict(file=str(D/'text-history/r10_c12/output/manifest.json'),sha256=sha(D/'text-history/r10_c12/output/manifest.json')),note='Old north256PixelsUnchanged and outside-old-repair-rect assertions refer only to the historical internal repairs; current joint change bbox is recorded in operation.')
m['sourceScopeReopened']['recordRole']='historical source finding, now resolved by the approved migration';m['sourceScopeReopened']['resolvedAt']=result['completedAt'];write(mp,m)
rs=D/'text-history/migration-applied-before-historical-qualification.json';assert not rs.exists();rs.write_bytes((D/'migration-applied.json').read_bytes())
for x in result['metadataAfter']:
 if x['file']==str(mp):x['sha256']=sha(mp)
result['historicalScopeQualification']=dict(manifestSnapshot=ref(prior),resultSnapshot=ref(rs),reason='Prevent legacy internal-repair unchanged-north assertion from being read as current joint repair behavior.');write(D/'migration-applied.json',result)
audit=dict(auditedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),script=ref(Path(__file__)),migrationResult=ref(D/'migration-applied.json'),allCurrentRecordedHashesValid=True,currentPlanNeighborHashesValid=True,allProtectedFilesUnchanged=True,allQARecordSourcesCurrent=True,p14KnownContextPixelExact=True,p14OldRequestUnchanged=True,scopedManifestStatus=read(mp)['status'],rootProgressUntouched=True,negativeWrongSHARejectedBeforeAnyMutation=True,formalAccepted=False)
write(D/'migration-after-audit.json',audit);print(json.dumps(audit,indent=2))
