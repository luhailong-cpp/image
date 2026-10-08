"""Default read-only; --apply performs root-authorized TEXT metadata correction only."""
from pathlib import Path
import argparse,json,shutil,sys
OUT=Path(__file__).resolve().parent;F=OUT.parent;T=F.parents[1];ROOT=T.parent;S=ROOT/'r10_c14'
sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
def ref(p):return dict(file=str(p),sha256=sha(p))
def check():
    plan=read(OUT/'retention-plan.json');checks=[];preserve=[]
    for row in plan['currentMetadataChecks']:
        p=Path(row['manifestBefore']['file']);assert sha(p)==row['manifestBefore']['sha256']
        tile=p.parent.parent;proposed=OUT/(tile.name+'-manifest.proposed.json');d=read(proposed)
        assert sha(d['file'])==d['sha256']==row['candidate']['sha256']
        assert d['scopedLocalSeamsPassed'] is True
        assert d['plan']['sha256']==sha(d['plan']['file'])
        for v in d['currentNeighbors'].values():assert sha(v['file'])==v['sha256']
        for q in d['qa']:assert sha(q['file'])==q['sha256'];preserve.append(ref(Path(q['file'])))
        preserve.extend([ref(Path(d['file'])),ref(tile/'output/native-assembly.json'),ref(Path(d['currentCandidateGeneration']['file'])),ref(Path(d['scopedReview']))])
        checks.append(dict(canonical=str(p),beforeSha256=sha(p),proposal=ref(proposed)))
    ledger=read(T/'retention-log.json')
    assert len(ledger['removed'])==115 and all(not Path(v['file']).exists() for v in ledger['removed'])
    return checks,preserve
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args();checks,preserved=check()
    if args.apply:
        log=OUT/'metadata-application.json';history=OUT/'actual-current-text-history'
        assert not log.exists() and not history.exists(),'Single-use metadata correction; inspect journal rather than rerun.'
        history.mkdir();records=[]
        for row in checks:
            p=Path(row['canonical']);dest=history/(p.parent.parent.name+'-manifest.before-correction.json');shutil.copyfile(p,dest);assert sha(dest)==row['beforeSha256'];records.append(ref(dest))
        record=dict(startedAt=now(),authorization='Direct parent /root message authorized precise metadata fixes and verification; no generic helper edit or deletion.',status='text_history_complete',history=records,changes=checks,deletionExecuted=False,immutableAssemblyModified=False)
        write(log,record)
        for row in checks:shutil.copyfile(row['proposal']['file'],row['canonical']);assert sha(row['canonical'])==row['proposal']['sha256']
        for v in preserved:assert sha(v['file'])==v['sha256']
        record.update(completedAt=now(),status='metadata_corrected_verified',currentManifests=[ref(Path(v['canonical'])) for v in checks],preservedImagesReviewAndAssembly=preserved)
        write(log,record)
    print(json.dumps(dict(applied=args.apply,deletionExecuted=False,canonicalManifests=[ref(Path(v['canonical'])) for v in checks])))
