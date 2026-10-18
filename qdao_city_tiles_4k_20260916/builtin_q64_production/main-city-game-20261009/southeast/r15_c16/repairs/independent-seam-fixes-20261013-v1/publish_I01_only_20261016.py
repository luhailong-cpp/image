from pathlib import Path
import json,hashlib,datetime,shutil
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'I01-only-reviewed-20261016';T=D.parents[1];C=T/'candidate'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def wr(p,j,replace=False):
 assert replace or not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rgb(p):return np.array(Image.open(p).convert('RGB'))
co=rd(O/'composition.json');latest=rd(C/'latest-assembly.json');assert latest['candidate']['sha256']==co['base']['sha256']
proof=rd(O/'visual-qa.json')
qa=dict(schemaVersion=1,reviewer='/root',recordedBy='/root/assembly_resume',recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),authority='Direct /root collaboration message: ROOT已实际看完I01-only变化4段+trial-v1的4条mask边界，短断缝消失且无新断线，局部通过。',reviewedCore=co['core'],evidence=proof['newEvidence'],localStatus='passed',W01Status='failed_pending_two_native_attempts_unaccepted',formalAccepted=False)
wr(O/'root-independent-qa-20261016.json',qa)
core=C/'r15_c16-4k-I01-grout-repaired-20261016-root-reviewed.png';ctx=C/'r15_c16-context-4326-I01-grout-repaired-20261016-root-reviewed.png'
for old,new in [(co['core'],core),(co['context'],ctx)]:
 assert sha(old['path'])==old['sha256'];assert not new.exists();shutil.copyfile(old['path'],new);assert sha(new)==old['sha256']
base=rgb(co['base']['path']);out=rgb(core);context=rgb(ctx)
assert np.array_equal(out[3712:],base[3712:]) and np.array_equal(out[:,:384],base[:,:384])
assert np.array_equal(context[115:4211,115:4211],out)
manifest=C/'r15_c16-assembly-I01-grout-repaired-20261016-root-reviewed.json'
wrapper=dict(schemaVersion=1,tile='r15_c16',status='candidate_internal_passed_west_W01_pending',baseAssembly=latest['manifest'],baseAssemblyIdentitySha256=latest['assemblyIdentitySha256'],operation='Actual native local I01 repair via stored integer crop, minimum-error paths and alpha; no resize or procedural detail generation',repairComposition=ev(O/'composition.json'),localQA=ev(O/'visual-qa.json'),rootIndependentQA=ev(O/'root-independent-qa-20261016.json'),repairReview=ev(D/'repair-review-20261016.json'),candidate=dict(**ev(core),size=[4096,4096]),context=dict(**ev(ctx),size=[4326,4326]),internalArtQA='passed',northSeamQA='passed_reused_unchanged',westSeamQA='failed_W01_q3_other_quarters_passed',south384PixelsExact=True,west384PixelsExact=True,activeNativeSourcesUnchanged=True,formalAccepted=False)
wr(manifest,wrapper)
wr(O/'previous-latest-assembly-before-publish.json',latest)
progress=rd(T/'progress.json');wr(O/'previous-progress-before-publish.json',progress)
newlatest=dict(schemaVersion=1,tile='r15_c16',status=wrapper['status'],manifest=ev(manifest),candidate=wrapper['candidate'],context=wrapper['context'],baseAssemblyIdentitySha256=latest['assemblyIdentitySha256'],internalArtQA='passed',externalNeighborSeamQA='west_W01_pending_north_passed_south_join_separate',formalAccepted=False)
wr(C/'latest-assembly.json',newlatest,True)
progress.update(status=wrapper['status'],updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate=str(core),candidateSha256=sha(core),context=str(ctx),contextSha256=sha(ctx),assemblyManifest=str(manifest),internalArtQA='passed',externalNeighborSeamQA='west_W01_pending_north_passed_south_join_separate',localRepairQA=str(O/'visual-qa.json'),rootIndependentQA=str(O/'root-independent-qa-20261016.json'),pendingRepairRecord=str(D/'repair-review-20261016.json'),nextStep='W01 remains failed after two native attempts; preserve exact south384 anchor. Continue other independent tiles; south true-core join handled separately.',formalAccepted=False)
wr(T/'progress.json',progress,True)
print(json.dumps(dict(candidate=wrapper['candidate'],context=wrapper['context'],manifest=ev(manifest),rootQA=ev(O/'root-independent-qa-20261016.json'),progress=ev(T/'progress.json'))))

