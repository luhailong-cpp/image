"""Prepare exact r09_c15 retention scope only; never delete or mutate images."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;R=T.parent;P=T/'repairs/west-paving'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return dict(file=str(Path(p).resolve()),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(p):return str(p).replace('/','\\').lower()
def binary(p):return p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc'}
def strings(v,at='$'):
 if isinstance(v,str):yield at,v
 elif isinstance(v,dict):
  for k,w in v.items():yield from strings(w,at+'.'+k)
 elif isinstance(v,list):
  for i,w in enumerate(v):yield from strings(w,at+f'[{i}]')
def prompt_path(v):
 v=v.get('prompt')
 return v if isinstance(v,str) else v.get('file') if isinstance(v,dict) else None
final=T/'output/r09_c15-candidate.png';manifest=T/'output/manifest.json';gen=Path(str(final)+'.generation.json');m=read(manifest)
assert sha(final)==m['sha256']==read(gen)['sha256']=='818a33e706b2db98c0404701f8e3f7cbf21bf7f1f9000905a22ee59c2b5ea2ef'
assert m['completePixelCoverage'] and m['scopedLocalSeamsPassed']
assert not (T/'retention-log.json').exists()
files=[q for q in T.rglob('*') if q.is_file() and q.name not in ['retention-plan.json','retention-validation.json']]
lookup={norm(q.resolve()):q for q in files}
external=[];historical_external=[];scanned=0
for q in R.rglob('*.json'):
 if T in q.parents or R/'tools' in q.parents or R/'r10_c13' in q.parents:continue
 scanned+=1
 try:d=read(q)
 except Exception as e:raise RuntimeError('Unreadable external JSON '+str(q)) from e
 uses=[dict(location=k,file=str(lookup[norm(v)].resolve())) for k,v in strings(d) if norm(v) in lookup]
 if uses:
  rec=dict(record=ref(q),references=uses)
  if q.resolve()==(R/"r09_c14/repairs/southwest-grout/history-before-application/r09_c15/plan.json").resolve():
   rec["reason"]="Immutable archived r09_c15 plan before west-source migration; no current or in-flight runtime use. Referenced old planning PNG may retire after export while this TEXT remains."
   historical_external.append(rec)
  else:external.append(rec)
extbinary={}
for doc in external:
 for u in doc['references']:
  q=Path(u['file'])
  if binary(q):extbinary.setdefault(norm(q),[]).append(dict(record=doc['record'],location=u['location']))
protected={}
def keep(q,category,reason):
 q=Path(q).resolve();assert q.is_relative_to(T.resolve()) and q.is_file(),str(q)
 protected[norm(q)]={'category':category,'reason':reason}
keep(final,'game_candidate','Current4096 game candidate with27 required native QA passed, immutable original assembly plus approved local repair provenance.')
night=Path(read(T/'plan.json')['nightStructure']['file'])
keep(night,'current_design','Current approved unique night structure-water-fixed design; layout remains useful for ongoing tile consistency, not counted as native production.')
for q in (T/'qa/native-candidate').glob('*.png'):keep(q,'current_QA','Current standard native QA derived from818a33 final; final-local-review checks exact bytes.')
for q in (T/'qa/external-details').glob('*.png'):keep(q,'current_QA','Current unrotated actual-W context or repaired paving detail;33 covered view items use these pixels.')
keep(T/'qa/north-no-neighbor-unverified.png','current_QA','Current north boundary inspection; absent neighbor is explicitly unverified.')
for name in ['proposed-joint-v19.png','upper-perimeter-v19.png','right-perimeter-v19.png','lower-perimeter-v19.png','west-join-v19.png','lower-detail-v19.png','three-crossings-v19.png']:
 keep(P/name,'current_applied_repair_QA','Approved v19 applied region/perimeter QA; application-review proves these exact pixels reproduce the current final + true W joint.')
assembly=read(T/'output/native-assembly.json')
for patch in assembly['patches']:
 for kind,item in patch['fields'].items():
  q=Path(item['file']);assert sha(q)==item['sha256']
  keep(q,'applied_native_fields','Actual original native assembly '+kind+'; preserve the applied numerical transform/mask and immutable evidence.')
# Keep the final effective fields from the actual selected composition chain, not rejected intermediate fields.
selected=[
 'proposal-v5.flow.npy','proposal-v5.effectiveColorCorrection.npy','proposal-v5.apply-mask.png','proposal-v4.jacobian.npy',
 'proposal-v7.top-local.tone.npy','proposal-v7.lower-west-local.tone.npy',
 'top-local-paint-mask.png','lower-west-local-paint-mask.png',
 'proposal-v8.lower-local-AI-opacity.npy','proposal-v9.top-original-opacity.npy','proposal-v9.top-AI-opacity.npy']
selected += [f'proposal-v{n}.{kind}' for n in [18,19] for kind in ['flow.npy','jacobian.npy','colorCorrection.npy','alpha.npy','apply-mask.png']]
for n in selected:keep(P/n,'applied_repair_fields','Actual effective flow, bounded color, opacity, ownership or orientation field in selected v5→v9→v18→v19 composition. Duplicate requested/provisional fields and unused trials are retired.')
for key,uses in extbinary.items():
 if key not in protected:keep(lookup[key],'external_reference_hold','Still referenced by an external tile/task record. Conservatively retained until that owner is complete; not eligible for this removal list.')
completed={}
for q in T.rglob('*.png.generation.json'):
 if 'history-before-v19-application' in q.parts:continue
 d=read(q)
 if d.get('route')=='builtin':
  pp=prompt_path(d)
  if pp:completed.setdefault(norm(pp),[]).append(ref(q))
requests=[];pending=[]
for q in T.rglob('*.request.json'):
 d=read(q);pp=prompt_path(d);done=completed.get(norm(pp),[]) if pp else []
 if not done:pending.append(str(q))
 requests.append(dict(record=ref(q),prompt=pp,completionRecords=done))
assert not pending,pending
keepitems=[];remove=[]
for q in sorted(files):
 key=norm(q.resolve());common=dict(**ref(q),bytes=q.stat().st_size)
 if key in protected:keepitems.append(dict(**common,**protected[key],externalReferences=extbinary.get(key,[])))
 elif not binary(q):keepitems.append(dict(**common,category='text_provenance_or_code',reason='All prompts, calls, requests, unknown actual model/quality evidence, source hashes, reviews, generation records, historical TEXT and scripts are retained unchanged.'))
 else:
  rel=q.relative_to(T).as_posix()
  if rel.startswith('native/'):reason='Completed native raw or edit target exported into current final; no external references found.'
  elif rel.startswith(('references/','guides/')):reason='Superseded planning source, old rejected sky design, enlarged guide or generation reference; current approved night design retained.'
  elif rel.startswith('qa/'):reason='Planning/previous-stage QA, not a current final inspection image.'
  elif q.suffix.lower()=='.npy':reason='Rejected, diagnostic, duplicate requested or superseded field; actual final effective transform/color/opacity/mask fields retained.'
  elif q.suffix.lower()=='.pyc':reason='Regenerable Python bytecode, not art, runtime asset, or text provenance.'
  else:reason='Raw AI output, input context, rejected or superseded proposal/diagnostic or application crop already exported into final. Current applied-v19 QA and effective fields retained.'
  remove.append(dict(**common,category='retire_after_export',reason=reason,plannedLifecycle='retiredAfterExport only after actual successful deletion',retiredAfterExport=False,sourceImageAvailable=True))
removeset={norm(q['file']) for q in remove}
conflicts=[dict(record=d['record'],reference=u) for d in external for u in d['references'] if norm(u['file']) in removeset]
assert not conflicts
external_sources=list(m.get('currentNeighbors',{}).values())
if 'sharedDayStructure' in read(T/'plan.json'):external_sources.append(read(T/'plan.json')['sharedDayStructure'])
for src in external_sources:assert sha(src['file'])==src['sha256']
northproof=None
if tile_check := read(T/'plan.json').get('northScopedFreeze'):
 from PIL import Image
 import numpy as np
 northproof=tile_check.copy()
 north=Path(read(T/'plan.json')['northCandidate']);frozen=Path(tile_check['file'])
 assert np.array_equal(np.asarray(Image.open(north).convert('RGB'))[3776:],np.asarray(Image.open(frozen).convert('RGB')))
 northproof['frozen320MatchesCurrentNorthPixels']=True
plan=dict(preparedAt=datetime.now(timezone.utc).isoformat(),root=str(T.resolve()),status='prepared_for_root_scope_review_only_no_deletion_executed',deletionAuthorizedByThisPreparation=False,final=ref(final),finalManifest=ref(manifest),currentCandidateGeneration=ref(gen),scopedReview=ref(Path(m['scopedReview'])),executionScript=ref(T/'execute-retention.ps1'),preparationScript=ref(Path(__file__).resolve()),keep=keepitems,remove=remove,protectedExternalSources=external_sources,northFreezePixelProof=northproof,historicalExternalReferenceExemptions=historical_external,preserveAllTextRecords=True,immutableNativeAssemblyMustRemainUnchanged=ref(T/'output/native-assembly.json'),externalHostImagesNotTouched=True,otherTilesNotModified=True,blockedR10c13ScopeExcluded=True,currentSharedDayDesignOutsideScope=read(T/'plan.json')['sharedDayStructure'],referenceAudit=dict(externalJsonRecordsScanned=scanned,matchingExternalRecords=external,proposedRemovalExternalReferenceConflicts=conflicts,completedRequestRecords=requests,pendingOwnRequests=pending,temporarilyRetainedExternalBinarySources=[x for x in keepitems if x['category']=='external_reference_hold']),summary=dict(keepCount=len(keepitems),keepBytes=sum(q['bytes'] for q in keepitems),keptBinaryCount=sum(binary(Path(q['file'])) for q in keepitems),removeCount=len(remove),removeBytes=sum(q['bytes'] for q in remove)),executionRules=['Preparation and default script invocation perform validation only; no deletion.','Later explicit Execute requires exact reviewed plan hash and unchanged final/manifest/generation/review/script/keep/remove files.','All resolved exact targets must remain beneath r09_c15 with no links/reparse points. No recursive folder removal, globs, alternate-shell deletion, host-image removal or unrelated tile changes.','Recheck external references and new/changed requests before deletion; do not retire any currently used downstream source.','Historical image records remain TEXT; mark retiredAfterExport and sourceImageAvailable=false only after each deletion actually succeeds.','Save current generation/manifest TEXT before lifecycle annotation; immutable native assembly stays unchanged.','Never retry after an error or automatic approval rejection; r10_c13 blocked cleanup is excluded.'])
write(T/'retention-plan.json',plan)
print(json.dumps(dict(plan=ref(T/'retention-plan.json'),summary=plan['summary'],externalConflicts=len(conflicts),pendingOwnRequests=len(pending),externalHeldBinaries=[x['file'] for x in plan['referenceAudit']['temporarilyRetainedExternalBinarySources']],deletedFiles=0)))

