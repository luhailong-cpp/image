"""Build an exact r09_c14 retention plan only. No deletion, no image mutation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
T=Path(__file__).resolve().parent;ROOT=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return dict(file=str(Path(p).resolve()),sha256=sha(p))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s):return str(s).replace('/','\\').lower()
def strings(v,where='$'):
 if isinstance(v,str):yield where,v
 elif isinstance(v,dict):
  for k,x in v.items():yield from strings(x,where+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from strings(x,where+f'[{i}]')
def binary(p):return p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc'}
final=T/'output/r09_c14-candidate.png';manifest=T/'output/manifest.json';gen=Path(str(final)+'.generation.json')
m=read(manifest);g=read(gen)
assert sha(final)==m['sha256']==g['sha256']=='26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc'
assert m['completePixelCoverage'] and m['scopedLocalSeamsPassed']
scoped=Path(m['scopedReview']);assert scoped.exists()
allfiles=[p for p in T.rglob('*') if p.is_file() and p.name not in ['retention-plan.json','retention-validation.json']]
assert not (T/'retention-log.json').exists()
files_by_norm={norm(p.resolve()):p for p in allfiles}
external=[];scanned=0
# Explicitly leave the unrelated previously blocked r10_c13 retention scope untouched.
for p in ROOT.rglob('*.json'):
 if T in p.parents or ROOT/'tools' in p.parents or ROOT/'r10_c13' in p.parents:continue
 d=read(p);scanned+=1
 matches=[]
 for key,value in strings(d):
  if norm(value) in files_by_norm:
   matches.append(dict(location=key,file=str(files_by_norm[norm(value)].resolve()),value=value))
 if matches:external.append(dict(record=ref(p),references=matches))
external_binary={}
for record in external:
 for match in record['references']:
  p=Path(match['file'])
  if binary(p):external_binary.setdefault(norm(p),[]).append(dict(record=record['record'],location=match['location']))
protected={}
def keep(p,category,reason):
 p=Path(p).resolve();assert p.is_relative_to(T.resolve()) and p.is_file(),str(p)
 protected[norm(p)]=dict(category=category,reason=reason)
keep(final,'game_candidate','Exported native 4096 game candidate; current internal/west scoped QA passed, and r10_c14/current delivery consumes this image.')
keep(T/'references/structure.png','current_design','Current unique same-frame night structural design with shared daytime geometry; kept for ongoing design consistency. This planning image is not counted as native production.')
# Preserve every actual current review PNG, including absent neighbor edge strips as explicitly unverified.
for p in (T/'qa/native-candidate').glob('*.png'):keep(p,'current_QA','Current QA regenerated from the final candidate; final review checks this exact image/hash.')
for p in (T/'qa/external-details').glob('*.png'):keep(p,'current_QA','Current unrotated full-west seam detail from the final candidate and immutable actual neighbor.')
keep(T/'qa/north-no-neighbor-unverified.png','current_QA','Current final north boundary inspection; absent north neighbor remains unverified.')
for p in (T/'repairs/west-foliage/applied-perimeter-qa').glob('*.png'):keep(p,'current_QA','Actually viewed final applied repair perimeter/leaf-contact QA; application-review records exact current bytes.')
asm=read(T/'output/native-assembly.json')
for patch in asm['patches']:
 for kind,item in patch['fields'].items():
  p=Path(item['file']);assert sha(p)==item['sha256']
  keep(p,'applied_native_fields','Actual applied native assembly '+kind+' retained as transform/mask evidence with immutable assembly.')
proposal=read(T/'repairs/west-foliage/proposal-v9.json')
for item in proposal['masks']+[proposal['colorField']]:
 p=Path(item['file']);assert sha(p)==item['sha256']
 keep(p,'applied_repair_fields','Actual selected v9 repair mask or finite background color field retained; unused registration proposals are not included.')
for key,uses in external_binary.items():
 p=files_by_norm[key]
 if key not in protected:
  keep(p,'active_downstream_reference','Still referenced outside this tile by current native generation/repair records. Keep until downstream work is exported and its retention is reviewed; not eligible for this removal list.')
keepitems=[];remove=[]
for p in sorted(allfiles):
 key=norm(p.resolve())
 common=dict(**ref(p),bytes=p.stat().st_size)
 if key in protected:
  keepitems.append(dict(**common,**protected[key],externalReferences=external_binary.get(key,[])))
 elif not binary(p):
  keepitems.append(dict(**common,category='text_provenance_or_code',reason='Preserve all model/quality/source/prompt/call/request/review/history records and supporting code. Current final metadata may later gain lifecycle annotations with exact prior text preserved.'))
 else:
  rel=p.relative_to(T).as_posix()
  if rel.startswith('native/'):reason='Completed native AI source or preparation context already exported into final game candidate; not currently referenced outside this tile.'
  elif rel.startswith('guides/') or rel.startswith('references/'):reason='Superseded planning enlargement, generation guide, collage target or copied neighbor context; unique current night design and completed final remain.'
  elif rel.startswith('qa/'):reason='Older planning or superseded pre-final QA image; final current QA and all historical text records are retained.'
  elif p.suffix=='.npy':reason='Rejected or superseded numerical proposal field not used by selected v9 application; actual applied fields remain.'
  elif p.suffix=='.pyc':reason='Regenerable Python bytecode cache, not design, game pixels or provenance.'
  else:reason='AI input, rejected source, superseded proposal/diagnostic or selected processing crop already exported into final candidate; actual applied masks/fields and current QA remain.'
  remove.append(dict(**common,category='retire_after_export',reason=reason,plannedLifecycle='retiredAfterExport only after actual successful deletion',retiredAfterExport=False,sourceImageAvailable=True))
remove_set={norm(x['file']) for x in remove}
conflicts=[dict(record=record['record'],reference=x) for record in external for x in record['references'] if norm(x['file']) in remove_set]
assert not conflicts
# Verify all historical request prompts have a returned AI generation record before declaring this tile finished.
ai_records=[(p,read(p)) for p in T.rglob('*.generation.json') if 'history-before-v9-application' not in p.parts]
completed_prompts={}
for p,d in ai_records:
 if d.get('route')=='builtin':
  key=norm(d.get('prompt',''));completed_prompts.setdefault(key,[]).append(ref(p))
pending=[]
requests=[]
for p in T.rglob('*.request.json'):
 d=read(p);pp=d.get('prompt')
 if not isinstance(pp,str) or norm(pp) not in completed_prompts:pending.append(str(p))
 requests.append(dict(record=ref(p),prompt=pp,completionRecords=completed_prompts.get(norm(pp),[])))
assert not pending,pending
# Prove the only actual neighboring crop needed downstream is independently frozen in r10_c14.
from PIL import Image
import numpy as np
frozen=ROOT/'r10_c14/references/north-native320.png'
assert np.array_equal(np.array(Image.open(final).convert('RGB'))[3776:],np.array(Image.open(frozen).convert('RGB')))
text_bytes=sum(x['bytes'] for x in keepitems if x['category']=='text_provenance_or_code')
plan=dict(preparedAt=datetime.now(timezone.utc).isoformat(),root=str(T.resolve()),status='prepared_for_review_only_no_deletion_executed',deletionAuthorizedByThisPreparation=False,final=ref(final),finalManifest=ref(manifest),currentCandidateGeneration=ref(gen),scopedReview=ref(scoped),executionScript=ref(T/'execute-retention.ps1'),preparationScript=ref(Path(__file__).resolve()),keep=keepitems,remove=remove,preserveAllTextRecords=True,immutableNativeAssemblyMustRemainUnchanged=ref(T/'output/native-assembly.json'),externalHostImagesNotTouched=True,otherTilesNotModified=True,blockedR10c13ScopeExcluded=True,currentSharedDayDesignOutsideScope=dict(file=str(ROOT.parent/'penglai_day/r09_c14/references/structure.png'),untouched=True,retainedByOwningTask=True),referenceAudit=dict(checkedAt=datetime.now(timezone.utc).isoformat(),externalJsonRecordsScanned=scanned,matchingExternalRecords=external,proposedRemovalExternalReferenceConflicts=conflicts,completedRequestRecords=requests,pendingOwnRequests=pending,r10c14South320Freeze=ref(frozen),frozen320PixelsMatchCurrentFinal=True,temporarilyRetainedNativeSources=[x for x in keepitems if x['category']=='active_downstream_reference']),summary=dict(keepCount=len(keepitems),keepBytes=sum(x['bytes'] for x in keepitems),keptBinaryCount=sum(binary(Path(x['file'])) for x in keepitems),keptTextBytes=text_bytes,removeCount=len(remove),removeBytes=sum(x['bytes'] for x in remove)),executionRules=['Default script invocation validates only; no image deletion is authorized during preparation.','A later explicitly requested Execute invocation requires this exact reviewed plan hash.','Before removal, validate all exact normalized absolute file paths stay inside r09_c14; reject links, missing files, changed hashes, new requests or any new external reference.','Never recurse-delete a directory, delete text, touch external host outputs or invoke another shell for filesystem deletion.','Keep immutable assembly and acquisition text unchanged. Save current candidate-generation/manifest text before adding actual retirement annotations.','Mark retiredAfterExport=true and sourceImageAvailable=false only for files confirmed absent after successful exact-file deletion; retain original path/hash/bytes in ledger.','Never retry automatically after errors or auto-review rejection.'])
write(T/'retention-plan.json',plan)
print(json.dumps(dict(plan=str(T/'retention-plan.json'),sha256=sha(T/'retention-plan.json'),summary=plan['summary'],externalConflicts=0,pendingOwnRequests=0,deferredNative=[x['file'] for x in plan['referenceAudit']['temporarilyRetainedNativeSources']],deletedFiles=0)))

