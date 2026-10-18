from pathlib import Path
import hashlib,json,argparse
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;W=Path('D:/work/image')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p): return {'path':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'workspaceRelativePath':p.relative_to(W).as_posix()}
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pinned(item):
 p=Path(item['path']);assert p.is_file() and sha(p)==item['sha256'],f'Explicit selection hash mismatch: {p}';return rec(p)
def adopt_owner_tile(tile_id,entry,source):
 image=entry.get('candidate');record=entry.get('record')
 if not image or not record:return
 image=pinned(image);record=pinned(record)
 existing=next((x for x in d['tiles'] if x['tileId']==tile_id),None)
 adopted={'tileId':tile_id,'image':image,'record':record,'selectionBasis':rec(source),'internalClosurePassed':bool(entry.get('internalClosurePassed',False)),'formalAccepted':False}
 if entry.get('internalClosure'):adopted['internalClosure']=pinned(entry['internalClosure'])
 for key in ('internalGeometryClosurePassed','materialStatus','materialPending','repairStatus','internalPassScope'):
  if key in entry:adopted[key]=entry[key]
 for key in ('internalReview','geometryClosure'):
  if isinstance(entry.get(key),dict) and 'path' in entry[key]:adopted[key]=pinned(entry[key])
 if existing:existing.update(adopted)
 else:d['tiles'].append(adopted)
ap=argparse.ArgumentParser();ap.add_argument('--r06candidate');ap.add_argument('--r06record');ap.add_argument('--r06closure');args=ap.parse_args()
split=read(W/'docs/MAP_PARALLEL_SPLIT_20261013.json')
reserved={t for b in split['batches'] if b.get('owner')=='01a1216d-5a60-7332-b4ee-8acad0d64dba' and b.get('status')=='allocated_root_reserved' for t in b['tiles']}
retained=49-len(reserved)
ownership={'originalTargetTileCount':49,'retainedOwnerTargetTileCount':retained,'reservedElsewhereTiles':sorted(reserved),'allocationManifest':rec(W/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'countsScope':'retained owner scope; external workers excluded'}
now=datetime.now(timezone.utc).isoformat();current=Z/'current-adopted-20261012.json';d=read(current)
mf=Z/'r06_c03.candidate-v1.manifest.json';m=read(mf)
cells=[]
for row in m['patchMatrix']:
 for x in row:
  q=Z/x['path'];stem=q.stem
  cells.append({'stem':stem,'image':rec(q),'generationRecord':rec(Z/x['generationRecord']),'receipt':rec(Z/'receipts'/f'{stem}.receipt.json'),'selection':'explicit_manifest_candidate_pending_internal_QA'})
d['partialTiles']['r06_c03']={'selectedCount':16,'requiredCount':16,'cells':cells,'assembled4k':True,'internalClosurePassed':False}
existing=next((x for x in d['tiles'] if x['tileId']=='r06_c03'),None)
tile=Path(args.r06candidate) if args.r06candidate else Path(existing['image']['path']) if existing else Z/'tiles/r06_c03_candidate-v1_4096.png'
r=Path(args.r06record) if args.r06record else Path(existing['record']['path']) if existing else tile.with_suffix('.assembly.json')
if not any(x['tileId']=='r06_c03' for x in d['tiles']):
 d['tiles'].append({'tileId':'r06_c03','image':rec(tile),'record':rec(r),'selectionBasis':rec(mf),'internalClosurePassedBeforeFreeze':False,'internalClosurePassed':False,'formalAccepted':False})
elif args.r06candidate:
 existing.update(image=rec(tile),record=rec(r),internalClosurePassed=False,formalAccepted=False)
if args.r06closure:
 cl=read(Path(args.r06closure));assert cl.get('internalVisualAccepted') is True or (cl.get('status')=='internal_native_seam_geometry_pass_shared_object_pending' and cl.get('nativeSeamGeometryPassed')==33 and cl.get('nativePixelCountVerified')==16777216)
 assert cl.get('base',{}).get('sha256',sha(tile))==sha(tile) and cl.get('record',{}).get('sha256',sha(r))==sha(r)
 if cl.get('visualReview'):pinned(cl['visualReview'])
 existing=next(x for x in d['tiles'] if x['tileId']=='r06_c03');existing.update(internalClosurePassed=True,internalClosure=rec(Path(args.r06closure)))
 existing['internalPassScope']='native seam geometry; shared railing, residual fine grain and connected boundaries remain pending'
d['partialTiles']['r06_c03']['internalClosurePassed']=next(x for x in d['tiles'] if x['tileId']=='r06_c03').get('internalClosurePassed',False)
root_selection=Z/'root-current-selection-20261012.json'
if root_selection.exists():
 root_tiles=read(root_selection)['tiles'];d['partialTiles'].update(root_tiles)
 for tile_id,entry in root_tiles.items():
  if entry.get('assembled4k') is True:adopt_owner_tile(tile_id,entry,root_selection)
right=Z/'right-current-selection-20261012.json'
if right.exists():
 rr=read(right)
 if 'partialTiles' in rr: d['partialTiles'].update(rr['partialTiles'])
 elif isinstance(rr.get('tiles'),dict): d['partialTiles'].update(rr['tiles'])
 elif 'cells' in rr and rr.get('tileId')=='r06_c04':d['partialTiles']['r06_c04']=rr
 for tile_id,entry in rr.get('tiles',{}).items():
  if entry.get('assembled4k') is True:adopt_owner_tile(tile_id,entry,right)
west=Z/'west-current-selection-20261012.json'
if west.exists():
 ww=read(west)
 for entry in ww.get('completedTiles',[])+ww.get('geometryClosedTiles',[])+([ww['currentTile']] if isinstance(ww.get('currentTile'),dict) else []):
  if entry.get('candidate') and entry.get('record'):adopt_owner_tile(entry['tileId'],entry,west)
 for entry in ww.get('partialTiles',[]):
  stems=entry.get('selectedNativeStems',[])
  for stem in stems:
   assert (Z/'native'/f'{stem}.png.generation.json').exists() and (Z/'receipts'/f'{stem}.receipt.json').exists()
  d['partialTiles'][entry['tileId']]={**entry,'selectedCount':len(stems),'requiredCount':16,'assembled4k':False,'internalClosurePassed':False}
# Current connected projections override older per-owner candidates only by explicit hash-bound manifest.
cross_manifest=Z/'qa/connected-r05-r06-current-v7.manifest.json'
cross_closure=Z/'qa/r05r06_v7_internal_delta_closure_material_pending_20261016.json'
assert sha(cross_manifest)=='4fb275d128a7880ec031968384e987a7ba32fc65dd7b5e79a946957c6cec7808'
assert sha(cross_closure)=='299c503ff53d1dd1a157e45009d3854baa44a719fac35f072f17f6f0f42e33a3'
cross=read(cross_manifest);cl=read(cross_closure);by={x['tileId']:x for x in cl['tiles']}
assert pinned(cl['manifest'])['sha256']==sha(cross_manifest)
for x in cross['tiles']:
 checked=by[x['tileId']];assert checked['current']['image']==x['image'] and checked['current']['record']==x['record']
 entry=next(y for y in d['tiles'] if y['tileId']==x['tileId'])
 entry.update(image=pinned(x['image']),record=pinned(x['record']),selectionBasis=rec(cross_manifest),internalClosurePassed=checked['internalClosurePassed'],internalGeometryClosurePassed=checked['internalGeometryClosurePassed'],internal33GeometryPassed=checked['internal33GeometryPassed'],materialStatus=checked['materialStatus'],internalReview=rec(cross_closure),internalPassScope='native seam geometry is separate from material and full visual acceptance',formalAccepted=False)
 full_entry=d['partialTiles'].get(x['tileId'])
 if isinstance(full_entry,dict):full_entry.update(candidate=entry['image'],record=entry['record'],internalClosurePassed=entry['internalClosurePassed'],internalGeometryClosurePassed=entry['internalGeometryClosurePassed'],materialStatus=entry['materialStatus'])
d['currentConnectedManifest']=rec(cross_manifest);d['currentConnectedClosure']=rec(cross_closure)
full={x['tileId'] for x in d['tiles']}
assert not full.intersection(reserved)
d['ownershipScope']=ownership
selected=len(full)*16+sum(v['selectedCount'] for k,v in d['partialTiles'].items() if k not in full)
internal=sum(bool(x.get('internalClosurePassed',x.get('internalClosurePassedBeforeFreeze',False))) for x in d['tiles'])
geometry=sum(bool(x.get('internalGeometryClosurePassed',x.get('internalClosurePassed',x.get('internalClosurePassedBeforeFreeze',False)))) for x in d['tiles'])
d.update(internalGeometryPassed4kCount=geometry,updatedAtUtc=now,assembledCandidateTileCount=len(full),internalPassed4kCount=internal,formalAcceptedCount=0,wholeZoneComplete=False,selectedNativeCoordinateCount=selected,missingNativeCoordinateCount=retained*16-selected);write(current,d)
active_root='r03_c01'
remaining_summary={'scope':'northwest rows1..7 cols1..7; unique coordinate tiles only','deduplicatedTargetTileCount':retained,'originalContractTileCount':49,'reservedElsewhereCount':len(reserved),'all16Native4kCandidateCount':len(full),'internalSeamCheckedTileCount':internal,'tilesStillMissingNativePatches':retained-len(full),'assembledTilesStillPendingInternalRepairOrCheck':len(full)-internal,'sharedAndOuterAcceptanceTrackedSeparately':True,'partialTileSelectedCounts':{k:v.get('selectedCount',0) for k,v in d['partialTiles'].items() if k not in full and v.get('selectedCount',0)>0}}
p=read(Z/'progress.json');p['ownershipScope']=ownership;p.update(status='resumed_production_candidates_pending_QA',generatedNativeCount=len(list((Z/'native').glob('*.png'))),assembledCandidateTileCount=len(full),fullyCovered4kCount=len(full),internalPassed4kCount=internal,candidateCoordinateCount=selected,missingNativeCoordinateCount=retained*16-selected,currentTile=active_root,currentPatch=active_root+'_native_continuation_and_QA',latest4kCandidate=d['partialTiles'][active_root]['candidate']['path'],nextStep='Finish r03c01 coastline local repairs; continue r07c02 and r05c05 missing native cores. r07c04 v6 and r06c02 v2 internal geometry passed, material pending. Cross v7 internal131/132 and shared17/17 geometry passed; one r6c4 point deferred after two attempts. Whole zone incomplete.',updatedAtUtc=now,generationHold=False,internalGeometryPassed4kCount=geometry,internalPassMeaning=f'{internal} current candidates have full prior internal visual pass; {geometry} have internal geometry pass including those full passes. Material and shared/outer acceptance remain separately tracked.');write(Z/'progress.json',p)
s=read(Z/'production-resume-20261012.json');s.update(updatedAtUtc=now,currentAdoptedIndex=rec(current),assembledCandidateTileCount=len(full),internalPassed4kCount=internal,selectedNativeCoordinateCount=selected,missingNativeCoordinateCount=retained*16-selected,candidateQA='Current explicit owner pins and connected v7 adopted. Full internal and geometry-only results are separated; material pending and deferred geometry remain incomplete.',internalGeometryPassed4kCount=geometry,newConnectedClosure={'path':'qa/connected-r04-r05-final-v1/closure.json','sha256':sha(Z/'qa/connected-r04-r05-final-v1/closure.json')} if (Z/'qa/connected-r04-r05-final-v1/closure.json').exists() else None);write(Z/'production-resume-20261012.json',s)
p['remainingWorkSummary']=remaining_summary;write(Z/'progress.json',p)
print(json.dumps({'candidateTiles':len(full),'internalPass':internal,'internalGeometryPass':geometry,'retainedTargetTiles':retained,'selectedNativeCoordinates':selected,'rawNativePngs':p['generatedNativeCount'],'wholeZoneComplete':False},ensure_ascii=False))
