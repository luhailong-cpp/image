from pathlib import Path
Z=Path(__file__).resolve().parents[1]
p=Z/'refresh_live_progress_v2_20261016.py';assert not p.exists()
s=(Z/'refresh_live_progress_20261016.py').read_text()
s=s.replace("if entry.get('internalClosure'):adopted['internalClosure']=pinned(entry['internalClosure'])", """if entry.get('internalClosure'):adopted['internalClosure']=pinned(entry['internalClosure'])
 for key in ('internalGeometryClosurePassed','materialStatus','materialPending','repairStatus','internalPassScope'):
  if key in entry:adopted[key]=entry[key]
 for key in ('internalReview','geometryClosure'):
  if isinstance(entry.get(key),dict) and 'path' in entry[key]:adopted[key]=pinned(entry[key])""")
s=s.replace("ww.get('completedTiles',[])+([ww['currentTile']]", "ww.get('completedTiles',[])+ww.get('geometryClosedTiles',[])+([ww['currentTile']]")
s=s.replace("full={x['tileId'] for x in d['tiles']}","""# Current connected projections override older per-owner candidates only by explicit hash-bound manifest.
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
full={x['tileId'] for x in d['tiles']}""")
s=s.replace("d.update(updatedAtUtc=now,assembledCandidateTileCount", "geometry=sum(bool(x.get('internalGeometryClosurePassed',x.get('internalClosurePassed',x.get('internalClosurePassedBeforeFreeze',False)))) for x in d['tiles'])\nd.update(internalGeometryPassed4kCount=geometry,updatedAtUtc=now,assembledCandidateTileCount")
s=s.replace("latest4kCandidate=d['partialTiles']['r07_c03']['candidate']['path']", "latest4kCandidate=d['partialTiles'][active_root]['candidate']['path']")
s=s.replace("nextStep='Complete r07c04 v6 changed-native checks and r06c02 remaining cores; continue r03c01 coastline. r07c03 one eave offset deferred after two ineffective attempts. Cross r05/r06 geometry17 passed, paving material and r06/r07 outer boundary pending.'", "nextStep='Finish r03c01 coastline local repairs; continue r07c02 and r05c05 missing native cores. r07c04 v6 and r06c02 v2 internal geometry passed, material pending. Cross v7 internal131/132 and shared17/17 geometry passed; one r6c4 point deferred after two attempts. Whole zone incomplete.'")
s=s.replace("internalPassMeaning=f'{internal} current candidates have passed internal checks; shared/outer acceptance remains incomplete.'", "internalGeometryPassed4kCount=geometry,internalPassMeaning=f'{internal} current candidates have full prior internal visual pass; {geometry} have internal geometry pass including those full passes. Material and shared/outer acceptance remain separately tracked.'")
s=s.replace("candidateQA='Current owner-pinned candidates recorded; r05c02 v5 internal33 independently passed. r07c03 eave offset, r06c04 paving material, and connected outer boundaries remain pending. r07c04 and r06c02 advance per explicit owner pins.'", "candidateQA='Current explicit owner pins and connected v7 adopted. Full internal and geometry-only results are separated; material pending and deferred geometry remain incomplete.',internalGeometryPassed4kCount=geometry")
s=s.replace("'internalPass':internal,", "'internalPass':internal,'internalGeometryPass':geometry,'retainedTargetTiles':retained,")
p.write_text(s,encoding='utf8')
print(p)
