from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
z=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
name='r04_c09-native-v2-20261017'
tile=z/'tiles'/f'{name}.png'
q=z/'qa'/f'{name}-final'
s=read(z/'selection-r04_c09.json')
pending_core={
 (1,2):'Garden left curb now about y930 instead of original-layout y1030; much improved but layout extent still pending.',
 (1,4):'Existing upper-left straight material transition at native y230 remains after two prior repairs.',
 (4,3):'Mineral-mottled native surface and grass tone differ from adjacent diamond-speckle surfaces; visible transitions remain.',
 (4,4):'Lantern expanded from x900 to x440, original-layout left boundary aboutx330 remains unmet; east rim/motif join also pending.'
}
pending_seams={
 'horizontal-3-segment-3':'Grout geometry continuous; p04_03_v2 face texture changes from regular diamond speckle to mineral mottling.',
 'vertical-2-segment-4':'Grass and slab boundary continuous; p04_03_v2 material and grass tone transition visible.',
 'vertical-3-segment-4':'Slab lines meet; p04_03_v2 mineral surface visibly changes to p04_04_v3 regular speckle.'
}
pending_cross={
 (3,2):'Continuous intersecting geometry; lower-right mineral face texture differs.',
 (3,3):'Continuous intersecting geometry; lower-left mineral face texture differs.'
}
checks=[]
for r in range(1,5):
 for c in range(1,5):
  p=q/f'core-{r}-{c}-100pct.png';ident=s['cores'][r-1][c-1]
  checks.append(dict(id=f'core-{r}-{c}',kind='core',file=p.as_posix(),sha256=sha(p),source=ident,sourceSha256=sha(z/'native'/f'{ident}.png'),inspectionScale=1,status='pending_not_passed' if (r,c) in pending_core else 'passed',note=pending_core.get((r,c),'Native core inspected: original local content, crisp detail, continuous large-scale geometry; no blank pixels or new propagation blocker.'),evidenceMethod='new outputs inspected full native1254; existing cores inspected exact1024 crop; unchanged prior quick checks hash-verified'))
for kind in ['horizontal','vertical']:
 for i in range(1,4):
  for j in range(1,5):
   ident=f'{kind}-{i}-segment-{j}';p=q/f'{ident}-100pct.png'
   checks.append(dict(id=ident,kind='internal_seam',file=p.as_posix(),sha256=sha(p),inspectionScale=1,status='pending_not_passed' if ident in pending_seams else 'passed',note=pending_seams.get(ident,'Native outlines and material meet without visible seam discontinuity in this exact256px strip.'),evidenceMethod='unscaled1024square QA board, each source strip unchanged'))
for r in range(1,4):
 for c in range(1,4):
  p=q/f'cross-{r}-{c}-100pct.png'
  checks.append(dict(id=f'cross-{r}-{c}',kind='cross',file=p.as_posix(),sha256=sha(p),inspectionScale=1,status='pending_not_passed' if (r,c) in pending_cross else 'passed',note=pending_cross.get((r,c),'Four-way native intersection continuous; no gaps, doubled grout or object cutoff.'),evidenceMethod='unscaled512square crop in QA board'))
assert len(checks)==49
counts={k:sum(x['status']==k for x in checks) for k in ['passed','pending_not_passed']}
qa_record=dict(tileId='r04_c09',candidate=tile.as_posix(),candidateSha256=sha(tile),reviewedAtUtc=now,checkpointCount=49,counts=counts,coverage=dict(nativeCoreCount=16,nativeSize=[1254,1254],coreCrop=[115,115,1139,1139],tileSize=[4096,4096],uncoveredPixels=0,resized=False,blending=False),checks=checks,boardManifest=(z/'qa'/f'{name}-boards/manifest.json').as_posix(),status='internal_49_reviewed_pending_repairs',formalAccepted=False,externalSeams='not whole-tile accepted; repaired east lantern join specifically failed',actualModel=None,actualQuality=None)
qa_path=z/'qa'/f'{name}-49QA.json'
assert not qa_path.exists()
write(qa_path,qa_record)
ext=z/'qa/r04_c09_p04_04_v3__r04_c10_p04_01.json'
e=read(ext);e.update(status='pending_not_passed',reviewedAtUtc=now,geometryChecks=dict(shaftTopContinuous=True,capGoldRimContinuous=False,paperMotifContinuous=False),note='At joinx256 in512wide strip, gold rim and lower band step vertically; cloud/floral paper motif changes. Do not propagate as accepted external boundary.')
write(ext,e)
s.update(internalReview='internal_49_reviewed_pending_repairs',internalQa=qa_path.as_posix(),internalQaCounts=counts,formalAccepted=False,updatedAtUtc=now,externalSeams='pending; east lantern rim/motif mismatch recorded')
s['pendingIssues'][-1]['issue']='Broad lantern restored x900 to440; upper shaft restored x1050. Original width targetx330 still unmet. East join to r04_c10_p04_01 has gold rim/band vertical step and cut paper motif. Two repairs used; retain bestv3 pending; no external acceptance.'
write(z/'selection-r04_c09.json',s)
d=read(tile.with_suffix('.png.derivation.json'));d.update(status='complete_native_coverage_internal_49_reviewed_pending_repairs',internalReview=s['internalReview'],internalQa=qa_path.as_posix(),internalQaCounts=counts,formalAccepted=False,externalSeams=s['externalSeams']);write(tile.with_suffix('.png.derivation.json'),d)
new_ids=['r04_c09_p01_02_v2','r04_c09_p01_02_v3','r04_c09_p02_02','r04_c09_p01_01','r04_c09_p02_01','r04_c09_p04_04_v2','r04_c09_p04_04_v3']
for r in range(1,5):
 for c in range(1,5):
  ident=s['cores'][r-1][c-1];p=z/'native'/f'{ident}.png.generation.json';a=read(p)
  a['internalCoreReview']='pending_not_passed' if (r,c) in pending_core else 'passed'
  a['internalCoreQa']=qa_path.as_posix();a['formalAccepted']=False;write(p,a)
checkpoint=dict(tileId='r04_c09',completedAtUtc=now,route='builtin image_gen.imagegen',actualModel=None,actualQuality=None,newGeneratedCount=len(new_ids),newGenerated=[dict(id=i,file=(z/'native'/f'{i}.png').as_posix(),sha256=sha(z/'native'/f'{i}.png'),receipt=(z/'receipts'/f'{i}.tool.json').as_posix(),prompt=(z/'prompts'/f'{i}.prompt.txt').as_posix()) for i in new_ids],selectedCoreCount=16,candidate=tile.as_posix(),candidateSha256=sha(tile),internalQa=qa_path.as_posix(),counts=counts,formalAccepted=False,recoveryAudit='Oldsession01a1432a ended after p01_02_v2 preflight with408; no imagegen invocation or returned v2 existed. Seven actual new calls completed in this restart.',pendingIssues=s['pendingIssues'],nextStep='Independent work may continue; coordinate remaining garden extent, old p01_04 transition, p04_03 material and broad lantern/east join repairs. Do not claim formal acceptance.',sharedGitMutated=False,wholeZoneProgressMutated=False)
write(z/'qa/r04_c09-restart-20261017.json',checkpoint)
print(json.dumps(dict(candidate=tile.as_posix(),sha256=sha(tile),selected=16,qa=qa_path.as_posix(),counts=counts,newGeneratedCount=len(new_ids),formalAccepted=False)))

