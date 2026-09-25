from pathlib import Path
import json,hashlib,datetime,sys
S=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(S/'continuation-20260923/checkpoint-merge'))
from merge_checkpoint import WinLockedFile
T=S/'next_tile_r08_c07';p=T/'handoff-state.json'
raw=p.read_bytes();d=json.loads(raw.decode('utf-8-sig'))
out=T/'continuation-20260923'/('handoff-reconcile-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir()
(out/'handoff-state.before.json').write_bytes(raw)
d['historicalFieldsBeforeCurrentExport']={k:d.get(k) for k in ['missingOrNeedsRegeneration','suggestedNextOrder','full4KCandidateCreated','plan','planUnchangedByHandoff','selectedPatches','rejectedOrSuperseded','sourceRetention']}
d.update(updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),missingOrNeedsRegeneration=[],suggestedNextOrder=[],full4KCandidateCreated=True,fullInternalSeamReviewPassed=True,fullInternalSeamReviewScope='Exact repaired-v1 six internal full seams; see currentCandidate review SHA; no whole-city gate',fullExternalSeamReviewPassed=False,fourTileJunctionReviewPassed=False,planUnchangedByHandoff=False,currentRemaining=['three outer neighbors and four external four-tile junctions','whole-city layout/navigation and client acceptance'])
plan=T/'plan.json'
d['plan']={'file':str(plan),'sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),'role':'consumed native production plan; sources retired after verified export'}
for row in d.get('selectedPatches',[]):row['status']='historical_input_exported_then_deleted_by_user_not_currently_reverified'
for row in d.get('rejectedOrSuperseded',[]):row['status']='historical_rejected_input_deleted_by_user_not_currently_reverified'
d['sourceRetention']={**d['sourceRetention'],'currentSelectedPngCount':0,'currentSelectedPngCountMeaning':'retained native inputs, not selected 4096 candidate count','currentSelected4KCandidateCount':1,'currentRetainedImagesIncludingDesignAndQA':12,'latestCleanup':d['currentRetention'],'sourceRecordsAndHashesPreserved':True}
after=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
lock=WinLockedFile(p,True)
try:
    assert lock.read()==raw,'Concurrent c07 handoff-state change'
    lock.write(after);assert lock.read()==after
finally:lock.close()
(out/'receipt.json').write_text(json.dumps({'file':str(p),'beforeSha256':hashlib.sha256(raw).hexdigest(),'afterSha256':hashlib.sha256(after).hexdigest(),'correctedLegacyCurrentFields':True},indent=2)+'\n')
print(str(out))
