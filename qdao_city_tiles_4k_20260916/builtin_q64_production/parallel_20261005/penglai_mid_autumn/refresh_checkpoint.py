"""Refresh truthful resumable state from current files; no art or approvals changed."""
from production import *

def ref(p):
    p=Path(p)
    return dict(file=str(p),sha256=sha(p)) if p.exists() else None

def native_count(tile):
    return sum(1 for p in (ROOT/tile/'native').glob('p[1-4][1-4].png') if Path(str(p)+'.generation.json').exists())

def main():
    d=read(ROOT/'delivery-index.json')
    completed=[]; pending=[]
    for t in d['tiles']:
        if not t.get('completePixelCoverage'): continue
        entry={k:t[k] for k in ['id','file','sha256','status']}
        if t.get('manifest'):
            m=read(t['manifest']);entry['manifest']=ref(t['manifest'])
            entry['scopedLocalSeamsPassed']=m.get('scopedLocalSeamsPassed',False)
            (completed if entry['scopedLocalSeamsPassed'] else pending).append(entry)
        else:
            entry['inheritedCandidate']=True;completed.append(entry)
    retention={}
    for tile in ['r09_c14','r10_c14']:
        p=ROOT/tile/'retention-postfinal-result.json'
        if p.exists(): retention[tile]=read(p)
    retention['r10_c13']=dict(cleanupBlocked=True,reason='Automatic approval rejected scoped PowerShell deletion: blocked by policy. No retry or bypass authorized by this continuation.',userAlreadyInformed=True,reportAgainInEventualFinal=True)
    active={
      'r09_c15':dict(stage='complete_native_pixels_west_paving_repair_pending',nativePatches=native_count('r09_c15'),candidate=ref(ROOT/'r09_c15/output/r09_c15-candidate.png'),owner='/root/r09c14_row2_resume',repairDirectory=str(ROOT/'r09_c15/repairs/west-paving'),latestReviewedProposal='v18: root actually viewed whole joint and6 native QA; lower groove and outer returns pass, upper/middle endpoint paint steps remain pending. No repair promoted.',unchangedReview=ref(ROOT/'r09_c15/qa/root-review.json')),
      'r10_c11':dict(stage='NE_native_generation_and_local_seam_repair',nativePatches=native_count('r10_c11'),owner='/root/r09c14_row3_resume',plan=ref(ROOT/'r10_c11/plan.json'),p14Promoted=True,p14CurrentReview=ref(ROOT/'r10_c11/qa/p14-joint-repair-current.json'),downstreamNativeAuthorized=True,pendingRepairs=['p11 north leaves','p24 incoming water seam'],specialP44Preparation=str(ROOT/'r10_c11/prepare_p44_with_native_post.py')),
      'r10_c12':dict(stage=read(ROOT/'r10_c12/output/manifest.json')['status'],candidate=ref(ROOT/'r10_c12/output/r10_c12.png'),jointSourceRepairApplied=True,independentAfterAudit=ref(ROOT/'r10_c12/repairs/northwest-source-joint/independent-after-audit.json'),migrationApplied=ref(ROOT/'r10_c12/repairs/northwest-source-joint/migration-applied.json'),historicalScopeReopenedThenRepaired=True),
      'r11_c13':dict(stage='native_generation_pending_assembly_QA',owner='/root/r09c14_row4_resume',northCandidate=ref(ROOT/'r10_c13/output/r10_c13-candidate.png'),nativeAuthorized=True,nativePatches=native_count('r11_c13'),plan=ref(ROOT/'r11_c13/plan.json'))
    }
    state=dict(updatedAt=now(),clientDate='2026-10-08',objective='Finish07 Penglai Mid-Autumn genuine65536x65536;256 tiles4096; no enlarged-layout substitute',scope='Write only this penglai_mid_autumn root. Day and other maps read-only. Builtin imagegen only. Actual host model/quality unknown.',wholeCityComplete=False,completePixelCandidates=d['completePixelCandidates'],missingTiles=d['missingTiles'],scopedOrInheritedAvailableCount=len(completed),formallyAcceptedTiles=0,runtimePublished=False,clientVerified=False,navigationVerified=False,completed=completed,completePixelsPendingQA=pending,active=active,retention=retention,deliveryIndex=ref(ROOT/'delivery-index.json'),genericFinalizer=ref(ROOT/'tools/finalize_scoped.py'),finalizerUsage='Read-only unless explicit --approve after all actual QA reports pass; never reapprove protected completed tiles.',previousUpdateScriptObsolete='Do not run update_checkpoint.py; it contains stale hardcoded state.')
    write(ROOT/'continuation-20261008.json',state)
    p=read(ROOT/'progress.json');p.update(updatedAt=now(),currentTile='r09_c15',parallelNextTile='r10_c11',nextStructureTile='r11_c13',completePixelCoveragePendingQA=[x['id'] for x in pending],activeTileNativePatches=16,activeTileStage='complete_pixels_under_scoped_QA',currentCandidate=str(ROOT/'r09_c15/output/r09_c15-candidate.png'));write(ROOT/'progress.json',p)
    w=read(ROOT/'current-work.json');w.update(updatedAt=now(),tile='r09_c15',stage='complete_pixels_under_scoped_QA',currentCandidate=p['currentCandidate'],internalQA='r09_c15_internal_passed_west_repair_pending',activeWork=active,next='Finish r09_c15 upper/middle west paving endpoint paint; finish r10_c11 p11/p24 repairs then native wavefront; finish r11_c13 native rows then assemble and actually inspect.');write(ROOT/'current-work.json',w)
    print(dict(fullPixelCandidates=d['completePixelCandidates'],scopedOrInheritedAvailable=len(completed),pending=[x['id'] for x in pending],missing=d['missingTiles']))

if __name__=='__main__':main()
