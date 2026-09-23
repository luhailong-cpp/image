"""Summarize only this continuation; never promote work in progress to accepted art."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ROOT = Path(__file__).resolve().parent
ART = ROOT.parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def entry(p):
    with Image.open(p) as im:
        im.verify()
    with Image.open(p) as im:
        im.load()
        pixels = list(im.size)
    return {'file': p.relative_to(ART).as_posix(), 'sha256': sha(p), 'pixels': pixels}

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    cleanup = ART/'cleanup-current-assets/deletion-receipt.json'
    cleanup_record = read(cleanup) if cleanup.exists() else None
    deleted = {}
    if cleanup_record:
        assert cleanup_record['status']=='completed', 'Finish or inspect partial cleanup before refreshing'
        deleted = {Path(x['file']).resolve():x['sha256'] for x in
                   (json.loads(line) for line in (cleanup.parent/'deleted-files.jsonl').read_text(encoding='utf-8-sig').splitlines())}
    records = []
    tile_dirs=sorted(ROOT.glob('next_tile_r??_c??'))
    native_dirs=[ROOT/'tools/sessions/tianyong_festival/r09_c09/native']+[p/sub for p in tile_dirs for sub in ('native','references')]
    seen_native=set()
    for base in native_dirs:
        if base.exists():
            for p in sorted(list(base.glob('*.record.json'))+list(base.glob('*.generation.json'))):
                native_name=p.name.replace('.record.json','.png').removesuffix('.generation.json')
                if not native_name.endswith('.png'):
                    native_name += '.png'
                native = p.with_name(native_name)
                if native.resolve() in seen_native:
                    continue
                if native.exists():
                    seen_native.add(native.resolve())
                    r = read(p)
                    item = entry(native)
                    item['record'] = {'file': p.relative_to(ART).as_posix(), 'sha256': sha(p)}
                    item['role'] = 'reference_only' if 'style-reference' in p.name else 'native_detail_source_not_production_tile'
                    item['actualModel'] = r.get('actualModel')
                    item['backendModelVerified'] = False
                    records.append(item)
    repairs = []
    repair_paths = list((ROOT/'tools/repairs/versions').glob('*/repair.json'))
    for tile_dir in tile_dirs:
        repair_paths += list((tile_dir/'repairs/versions').glob('*/repair.json'))
    for p in sorted(repair_paths):
        r = read(p)
        original = p.parent/'repair-native-1254.png'
        if not original.exists() and original.resolve() in deleted:
            continue  # Explicitly retired bytes, not a retained native source.
        item = entry(original)
        item['record'] = {'file': p.relative_to(ART).as_posix(), 'sha256': sha(p)}
        item['role'] = 'native_repair_source_not_production_tile'
        item['actualModel'] = r.get('actualModel')
        item['actualQuality'] = r.get('actualQuality')
        item['outsideMaskPixelsUnchanged'] = r.get('outsideMaskPixelsUnchanged',r.get('outsideAllowedMaskPixelsUnchanged'))
        item['resampling'] = r.get('resampling',r.get('registration',{}).get('sourceResampling'))
        repairs.append(item)
    candidates = []
    first = ROOT/'tools/sessions/tianyong_festival/r09_c09/output_resume_20260921/tianyong_r09_c09_q64_4k_candidate.png'
    versions = sorted((ROOT/'tools/repairs/versions').glob('r09_c09_repair_v*/r09_c09.png'))
    if first.exists() or versions:
        p = versions[-1] if versions else first
        candidates.append(dict(entry(p), tile='r09_c09', status='pending_or_failed_visual_acceptance', accepted=False))
    second = ROOT/'next_tile_r09_c10/output/r09_c10.candidate.png'
    child_versions = [p for p in (ROOT/'next_tile_r09_c10/repairs/versions').glob('*/repair.json') if (p.parent/'r09_c10.png').exists()]
    if child_versions:
        def repair_time(p):
            record = read(p)
            if record.get('createdAtUtc'):
                return record['createdAtUtc']
            receipt = p.parent/'request-receipt.json'
            return read(receipt).get('completedAtUtc','') if receipt.exists() else ''
        latest = max(child_versions, key=repair_time)
        second = latest.parent/'r09_c10.png'
    for p in [second] if second.exists() else []:
        with Image.open(p) as im:
            size=im.size
        if size == (4096,4096):
            candidates.append(dict(entry(p), tile='r09_c10', status='pending_or_failed_visual_acceptance', accepted=False))
    for latest_pointer in sorted(ROOT.glob('next_tile_r??_c??/latest-candidate.json')):
        tile_id=latest_pointer.parent.name.removeprefix('next_tile_')
        pointer = read(latest_pointer)
        def pointer_path(value):
            p = Path(value['file'])
            if not p.is_absolute():
                base = ART.parent if p.parts[0]==ART.name else (ART if value.get('pathBase')=='art_root' else ROOT)
                p = base/p
            assert p.resolve().is_relative_to(ART.resolve()), 'Pointer outside city art directory'
            assert sha(p)==value['sha256'], 'Pointer SHA mismatch: '+str(p)
            return p
        candidate_file = pointer_path(pointer)
        assert sha(candidate_file)==pointer['sha256'], 'Latest candidate pointer SHA mismatch'
        selected = dict(entry(candidate_file), tile=tile_id, status=pointer.get('status','pending_or_failed_visual_acceptance'), accepted=False)
        for key in ('record','qa','scopedLocalContinuityPassed','reviewedNeighborTiles','reviewedJunctionIds'):
            if key in pointer:
                if key in ('record','qa'):
                    selected[key]={'file':pointer_path(pointer[key]).relative_to(ART).as_posix(),'sha256':pointer[key]['sha256']}
                else:
                    selected[key] = pointer[key]
        candidates = [c for c in candidates if c['tile']!=tile_id]+[selected]
    for candidate in candidates:
        row, col = int(candidate['tile'][1:3]), int(candidate['tile'][5:7])
        candidate['role']='candidate_not_production_tile'
        candidate['finalPixelRectXYWH']=[(col-1)*4096,(row-1)*4096,4096,4096]
        candidate['worldRect']={'x':50+(col-1)*18.75,'z':300-row*18.75,'width':18.75,'height':18.75}
        p = ART/candidate['file']
        source_record = p.parent/'repair.json'
        if source_record.exists():
            candidate['record']={'file':source_record.relative_to(ART).as_posix(),'sha256':sha(source_record)}
    state = {
      'schemaVersion':1,'updatedAtUtc':datetime.now(timezone.utc).isoformat(),
      'purpose':'art_work_in_progress_not_production_delivery','activeAppearance':'tianyong_festival',
      'target':{'mapPixels':[65536,65536],'rows':16,'columns':16,'tilePixels':[4096,4096],'tileCount':256},
      'scopePolicy':'Complete this city appearance before other appearances; client integration belongs to another window.',
      'baselineSelectedLocalCandidates':6,'productionAcceptedTiles':0,'completeCityDeliveries':0,
      'candidateCoordinateCountIncludingWorkInProgress':6+len({c['tile'] for c in candidates}),
      'coordinatesWithoutAny4KCandidate':256-6-len({c['tile'] for c in candidates}),
      'allAppearanceCandidateCoordinateCountIncludingWorkInProgress':24+len({c['tile'] for c in candidates}),
      'baselineAudit':'audit/current_input_inventory.json',
      'baselineCoverageLedger':'audit/tianyong_festival_coverage_ledger.json',
      'coverageLedger':'current-coverage-ledger.json',
      'modelCapabilityEvidence':'model-capability.json',
      'perImageProvenanceDirectory':'provenance',
      'latestR09C09VisualReview':'audit/r09_c09_review_v5/visual-review-v6.json',
      'newNativeDetailCount':sum(r['role'].startswith('native_detail') for r in records),
      'newReferenceCount':sum(r['role']=='reference_only' for r in records),
      'newNativeRepairCount':len(repairs),
      'allAppearanceRetainedNativeKnownCountExcludingReferences':502+4+sum(r['role'].startswith('native_detail') for r in records)+len(repairs),
      'historicalNativeFilesMissingFromBaselineIndex':4,
      'layoutSourceAudit':'tools/layout-source-audit.json',
      'nativeRecords':records,'repairRecords':repairs,'workInProgressCandidates':candidates,
      'sourceArtUpscaled':False,'allVisualChecksPassed':False,'runtimePublished':False,
      'deliveryReady':False,'formalManifestProduced':False,
      'remaining':['complete all 256 native-detail tile coordinates','resolve every failed internal and external seam','all 480 adjacent seams and 225 junctions','whole-city layout/navigation and foreground evidence','contract-bound art acceptance before client handoff'],
      'repositoryActivity':'This task performed no git add, commit, push, reset or deletion. Concurrent commit 06bfca2a included some in-progress files and is preserved; Git inclusion is not art acceptance.'
    }
    if cleanup_record:
        historical = read(ROOT/'audit/current_input_inventory.json')
        retained_known = {(ART/e['native']).resolve() for e in historical['indexedNativeEvidence'] if (ART/e['native']).is_file()}
        retained_known.update((ART/e['file']).resolve() for e in records+repairs if e['role']!='reference_only')
        retained_known.update(p.resolve() for p in (ART/'builtin_q64_production/tianyong_festival/r09_c09/native').glob('*.png'))
        state['allAppearanceRetainedNativeKnownCountExcludingReferences'] = len(retained_known)
        state['sourceRetention'] = {'policy':'User requested final selected art/design only; obsolete originals and rollback images deleted',
          'cleanupReceipt':str(cleanup.relative_to(ART)),'cleanupReceiptSha256':sha(cleanup),
          'deletedFiles':cleanup_record['deletedFiles'],'deletedBytes':cleanup_record['deletedBytes'],
          'historicalGenerationCountsAreNotRetainedByteCounts':True,'sourceRecordsAndHashesPreserved':True,
          'deletedOriginalsAvailableForReplay':False}
        state['repositoryActivity'] = 'User explicitly authorized obsolete city-original/rollback media deletion; see cleanup receipt. No git add, commit, push or reset performed by this window.'
    review_path = ROOT/state['latestR09C09VisualReview']
    if review_path.exists():
        review = read(review_path)
        for candidate in candidates:
            if candidate['sha256'] == review['candidateSha256']:
                candidate['status'] = review['status']
                candidate['scopedLocalContinuityPassed'] = review['scopedLocalContinuityPassed']
                candidate['review'] = {'file':review_path.relative_to(ART).as_posix(),'sha256':sha(review_path)}
    ledger = read(ROOT/state['baselineCoverageLedger'])
    ledger['updatedAtUtc'] = state['updatedAtUtc']
    ledger['baselinePreservedAt'] = state['baselineCoverageLedger']
    indexed = {c['tile']: c for c in candidates}
    for tile in ledger['tiles']:
        if tile['tile'] in indexed:
            tile['candidate'] = indexed[tile['tile']]
            tile['candidateExists'] = True
            tile['status'] = indexed[tile['tile']]['status']
    present = {t['tile'] for t in ledger['tiles'] if t['candidateExists']}
    state['candidateCoordinateCountIncludingWorkInProgress']=len(present)
    state['coordinatesWithoutAny4KCandidate']=256-len(present)
    state['allAppearanceCandidateCoordinateCountIncludingWorkInProgress']=24+len(present)-6
    scoped_pairs={}
    scoped_junctions={}
    for candidate in candidates:
        if candidate.get('scopedLocalContinuityPassed') and candidate.get('qa'):
            for neighbor in candidate.get('reviewedNeighborTiles',[]):
                scoped_pairs['|'.join(sorted([candidate['tile'],neighbor]))]=candidate['qa']
            for junction_id in candidate.get('reviewedJunctionIds',[]):
                scoped_junctions[junction_id]=candidate['qa']
    for seam in ledger['seams']:
        seam['bothCandidatesPresent'] = all(t in present for t in seam['tiles'])
        if seam['bothCandidatesPresent'] and seam['status']=='pending_missing_neighbor':
            seam['status']='candidates_present_visual_review_pending'
        if review_path.exists() and indexed.get('r09_c09',{}).get('scopedLocalContinuityPassed') and seam['id'] in ['r09_c08|r09_c09','r09_c09|r10_c09']:
            seam['status']='scoped_local_continuity_review_passed_whole_city_gate_pending'
            seam['currentScopedReview']=indexed['r09_c09']['review']
            seam['freshVisualReviewPerformedByThisAudit']=True
        if indexed.get('r09_c10',{}).get('scopedLocalContinuityPassed') and seam['id'] in ['r09_c09|r09_c10','r09_c10|r10_c10']:
            seam['status']='scoped_local_continuity_review_passed_whole_city_gate_pending'
            seam['currentScopedReview']=indexed['r09_c10']['qa']
            seam['freshVisualReviewPerformedByThisAudit']=True
        if seam['id'] in scoped_pairs:
            assert seam['bothCandidatesPresent'], 'Reviewed seam has missing candidate'
            seam['status']='scoped_local_continuity_review_passed_whole_city_gate_pending'
            seam['currentScopedReview']=scoped_pairs[seam['id']]
            seam['freshVisualReviewPerformedByThisAudit']=True
    for junction in ledger['junctions']:
        junction['allCandidatesPresent'] = all(t in present for t in junction['tiles'])
        if junction['allCandidatesPresent'] and junction['status']=='pending_missing_neighbor':
            junction['status']='candidates_present_visual_review_pending'
        if indexed.get('r09_c09',{}).get('scopedLocalContinuityPassed') and junction['id']=='junction_r09_c08':
            junction['status']='scoped_local_continuity_review_passed_whole_city_gate_pending'
            junction['currentScopedReview']=indexed['r09_c09']['review']
            junction['freshVisualReviewPerformedByThisAudit']=True
        if indexed.get('r09_c10',{}).get('scopedLocalContinuityPassed') and junction['id']=='junction_r09_c09':
            junction['status']='scoped_local_continuity_review_passed_whole_city_gate_pending'
            junction['currentScopedReview']=indexed['r09_c10']['qa']
            junction['freshVisualReviewPerformedByThisAudit']=True
        if junction['id'] in scoped_junctions:
            assert junction['allCandidatesPresent'], 'Reviewed junction has missing candidate'
            junction['status']='scoped_local_continuity_review_passed_whole_city_gate_pending'
            junction['currentScopedReview']=scoped_junctions[junction['id']]
            junction['freshVisualReviewPerformedByThisAudit']=True
    ledger['counts'].update(candidateTiles=len(present),missingCandidates=256-len(present),seamsWithBothCandidates=sum(s['bothCandidatesPresent'] for s in ledger['seams']),junctionsWithAllCandidates=sum(j['allCandidatesPresent'] for j in ledger['junctions']))
    ledger['counts']['freshScopedLocalSeamsPassed']=sum(s['status']=='scoped_local_continuity_review_passed_whole_city_gate_pending' for s in ledger['seams'])
    ledger['counts']['freshScopedLocalJunctionsPassed']=sum(j['status']=='scoped_local_continuity_review_passed_whole_city_gate_pending' for j in ledger['junctions'])
    ledger_path=ROOT/state['coverageLedger']
    ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    state['coverageLedgerSha256']=sha(ledger_path)
    target=ROOT/'session-state.json'
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:state[k] for k in ['newNativeDetailCount','newReferenceCount','newNativeRepairCount','productionAcceptedTiles','deliveryReady']},ensure_ascii=False))

if __name__=='__main__': main()
