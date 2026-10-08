import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
P=T/'output/r08_c14.png';digest=sha(P);Q=T/'qa/assembly'
names=['internal-vertical-x2048-full.png','internal-vertical-x3072-full.png','internal-horizontal-y1024-full.png','internal-horizontal-y2048-full.png','intersection-x2048-y1024.png','intersection-x2048-y2048.png','intersection-x3072-y1024.png','intersection-x3072-y2048.png','overview-preview-1024.png']
items=[{'file':str(Q/n),'sha256':sha(Q/n),'nativePixelScale':0.25 if n.startswith('overview') else 1,'viewed':True} for n in names]
for d in ['water-join','water-join-east']:
 for p in (T/'repairs'/d).glob('*-qa.png'):items.append({'file':str(p),'sha256':sha(p),'nativePixelScale':1,'viewed':True,'scope':'repair insertion boundaries'})
review={'tile':'r08_c14','candidate':{'file':str(P),'sha256':digest,'pixels':[4096,4096]},'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_water14','scope':'Targeted correction of upper third-column gray-green water and discontinuities at x2048/x3072. Rechecked all four affected full native seam bands, four affected intersections, insertion edges and full overview.','findings':{'grayGreenVerticalBand':'resolved','brightWhiteNetlikeCaustics':'absent in reviewed upper water','ropePostBannerGeometry':'visually preserved and continuous','affectedInternalSeams':'no actionable discontinuity in reviewed bands and intersections','waterMaterial':'quiet bright cyan/azure broad hand-painted shapes'},'nativeValidation':{'validatedPatches':16,'missing':[],'historicalInputs':'Superseded edit inputs validated through archived generation records only; not asserted to match current path pixels.'},'viewedEvidence':items,'formalAccepted':False,'wholeCityComplete':False,'runtimeIntegrationVerified':False,'unreviewedScope':'Other tiles, external common edges, navigation and full-city coverage are not accepted by this repair review.'}
save(T/'qa/water-repair-final-review.json',review)
manifest=read(T/'output/assembly-manifest.json');latestqa=read(T/'qa/assembly/manifest.json');manifest.update(qa=latestqa['qa'],status='complete-pixel-candidate-water-repair-reviewed-external-edges-pending',targetedVisualReview={'file':str(T/'qa/water-repair-final-review.json'),'sha256':sha(T/'qa/water-repair-final-review.json')},assemblyParametersApplyToBase=True,postAssemblyRepairChain=[{'file':str(T/'repairs'/d/'integration.json'),'sha256':sha(T/'repairs'/d/'integration.json')} for d in ['water-join','water-join-east']]);save(T/'output/assembly-manifest.json',manifest)
cleanup_path=T/'rejected/water-graygreen-20261008/cleanup-record.json'
cleanup=read(cleanup_path).get('deleted',[]) if cleanup_path.exists() else []
for old in (T/'rejected/water-graygreen-20261008').glob('*.generation.json'):
 rec=read(old);p=Path(rec['evidence']['toolResultSourcePath']).resolve();allowed=Path('C:/Users/luyua/.codex/generated_images').resolve()
 assert p.is_relative_to(allowed)
 if p.exists():
  assert sha(p)==rec['sha256'];p.unlink();cleanup.append({'file':str(p),'sha256':rec['sha256'],'reason':'rejected gray-green image superseded; textual generation record preserved','deleted':True})
 elif not any(e['file']==str(p) for e in cleanup):
  cleanup.append({'file':str(p),'sha256':rec['sha256'],'reason':'rejected gray-green raw image deleted earlier during this repair; preserved generation record identifies it','deleted':True})
save(T/'rejected/water-graygreen-20261008/cleanup-record.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'deleted':cleanup,'noImageBackupsCreated':True,'currentNativeSourcesAndRepairDependenciesRetained':True})
for name in ['progress.json','current-work.json']:
 s=read(T/name);s.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),nativePatchesSaved=16,countsAsCompleteTile=True,completePixelCandidate=True,formalAccepted=False,phase='water_repair_complete_external_edge_review_pending',candidateFile=str(P),candidateSha256=digest,waterRepairReview=str(T/'qa/water-repair-final-review.json'));save(T/name,s)
print(json.dumps({'candidate':str(P),'sha256':digest,'review':str(T/'qa/water-repair-final-review.json'),'deletedRejectedRawImages':len(cleanup)}))
