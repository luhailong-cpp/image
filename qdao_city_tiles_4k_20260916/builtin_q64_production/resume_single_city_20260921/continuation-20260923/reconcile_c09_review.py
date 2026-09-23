from pathlib import Path
import json,hashlib,datetime,sys
S=Path(__file__).resolve().parent.parent;A=S.parent.parent
sys.path.insert(0,str(S/'continuation-20260923/checkpoint-merge'))
from merge_checkpoint import WinLockedFile
T=S/'next_tile_r08_c09';p=T/'latest-candidate.json'
raw=p.read_bytes();d=json.loads(raw.decode('utf-8-sig'))
review=A/d['review']['file']
supplement=review.parent/'visual-review-supplement-internal-tone-failure.json'
def ref(p):return {'file':p.relative_to(A).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
sd=json.loads(supplement.read_text(encoding='utf-8-sig'))
assert sd['candidate']['sha256']==d['candidate']['sha256']
assert ref(review)['sha256']==d['review']['sha256']
now=datetime.datetime.now(datetime.timezone.utc)
out=review.parent/('root-reconciliation-'+now.strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir()
(out/'latest-candidate.before.json').write_bytes(raw)
combined={'schemaVersion':1,'reviewedAtUtc':now.isoformat(),'candidate':d['candidate'],'priorReview':d['review'],'latestCorrectiveSupplement':ref(supplement),'neighbor':json.loads(review.read_text(encoding='utf-8-sig'))['neighbor'],'precedence':'Corrective supplement overrides earlier same-PNG internal vertical seam pass claims; earlier observations remain historical. Root independently viewed patch03 original pixels.','internalFullSeamsReviewed':6,'internalSeamsAllPassed':False,'failedInternalSeams':[{'x':2048,'yRangeObserved':[3469,4096],'reason':'rectangular_tone_step'},{'x':3072,'yRangeObserved':[3469,4096],'reason':'rectangular_tone_step'}],'pendingInternalSeams':[{'x':1024,'reason':'broad material context requires fresh review'}],'bottomExternalEdge':'failed_material_continuity','otherExternalEdges':'pending','externalFourTileJunctions':'pending','formalAccepted':False,'runtimeAccepted':False,'actualModel':None,'actualQuality':None}
rp=out/'current-review.json';rp.write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d['review']=ref(rp)
d['reviewHistory']=[combined['priorReview']]
d['latestCorrectiveSupplement']=ref(supplement)
d['status']='selected_complete_work_in_progress_candidate_internal_tone_and_bottom_edge_failed_not_production_accepted'
d['internalSeamsAllPassed']=False
d['updatedAtUtc']=now.isoformat()
after=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
lock=WinLockedFile(p,True)
try:
    assert lock.read()==raw,'Concurrent c09 selection changed'
    lock.write(after);assert lock.read()==after
finally:lock.close()
(out/'selection-update-receipt.json').write_text(json.dumps({'beforeSha256':hashlib.sha256(raw).hexdigest(),'afterSha256':hashlib.sha256(after).hexdigest(),'candidatePixelsChanged':False},indent=2)+'\n')
print(json.dumps({'selection':ref(p),'currentReview':ref(rp)},ensure_ascii=False))
