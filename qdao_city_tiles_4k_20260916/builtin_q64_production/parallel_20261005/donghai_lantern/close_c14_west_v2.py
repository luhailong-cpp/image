"""Bind the already viewed joint QA to final water-repaired bases by exact pixels."""
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.dont_write_bytecode=True
import json
import numpy as np
from PIL import Image
import compose_west as cw

ROOT=Path(__file__).resolve().parent
PRE=ROOT/'r08_c14/west-pre-water'
FINAL_V2='--final-v2' in sys.argv
FINAL_BASE_NAME='final-base-v2.json' if FINAL_V2 else 'final-base.json'
FINAL=ROOT/('r08_c14/west-final-v2' if FINAL_V2 else 'r08_c14/west-final')

def main():
    old_manifest=PRE/'output/west-final-manifest.json'
    new_manifest=FINAL/'output/west-final-manifest.json'
    old=cw.read(old_manifest);new=cw.read(new_manifest)
    old_review_path=PRE/'qa/review.json';old_review=cw.read(old_review_path)
    cw.require(old_review['result']=='pass-within-common-edge-scope','No completed prior visual review')
    cw.check(old_manifest,old_review['manifest']['sha256'])
    cw.require(new['waterRepairsAppliedToEastBase'] is True,'Final base still lacks water repairs')
    cw.require(len(old['qa'])==len(new['qa'])==len(old_review['reviewedImages'])==21,'QA set changed')
    prior={Path(e['file']).name:e for e in old['qa']}
    proofs=[]
    new_actual_path=FINAL/'qa/rebound-changed-qa-review.json'
    new_actual=cw.read(new_actual_path) if new_actual_path.exists() else {'reviewedImages':[]}
    actual_by_name={Path(e['file']).name:e for e in new_actual['reviewedImages']}
    changed=[]
    for e in new['qa']:
        previous=prior[Path(e['file']).name]
        cw.check(e['file'],e['sha256']);cw.check(previous['file'],previous['sha256'])
        cw.require(e['pairRectXYXY']==previous['pairRectXYXY'],'QA coordinates changed')
        same_pixels=np.array_equal(cw.rgb(e['file'],tuple(e['pixels'])),cw.rgb(previous['file'],tuple(previous['pixels'])))
        if not same_pixels:
            changed.append(Path(e['file']).name)
            actual=actual_by_name.get(Path(e['file']).name)
            cw.require(actual is not None and actual.get('sha256')==e['sha256'] and actual.get('result')=='pass','Changed QA requires fresh actual original-detail view: '+Path(e['file']).name)
        proofs.append({'final':cw.info(e['file']),'actuallyViewedPrior':cw.info(previous['file']),'pixels':e['pixels'],'pairRectXYXY':e['pairRectXYXY'],'pixelArrayExactlyIdentical':bool(same_pixels),'fileBytesExactlyIdentical':e['sha256']==previous['sha256'],'freshActualVisualReview':cw.info(new_actual_path) if not same_pixels else None})
    old_outputs={e['id']:e for e in old['outputs']}
    outputs={e['id']:e for e in new['outputs']}
    cw.require(outputs['r08_c13']['sha256']==old_outputs['r08_c13']['sha256'],'Final water substitution changed c13 unexpectedly')
    for e in new['outputs']:cw.check(e['file'],e['sha256'])
    report={**old_review,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'method':f'{21-len(changed)} final QA images are verified pixel-for-pixel identical to the prior original-detail actual visual inspection. {len(changed)} attachment windows changed due to disjoint internal local wood repair and have fresh original-detail actual views bound by exact current hashes. Common-edge insert and c13 pixels remain identical. This is scoped inherited evidence plus fresh inspection of changed attachment windows.',
        'manifest':cw.info(new_manifest),'outputs':new['outputs'],'priorVisualReview':cw.info(old_review_path),'reviewedImages':[{k:e[k] for k in ('file','sha256','pixels','pairRectXYXY')} for e in new['qa']],
        'priorQAEqualityProofs':proofs,'changedQaActualReview':cw.info(new_actual_path) if changed else None,'changedQaNames':changed,'waterRepairStatus':'present in final east base; water region QA remains owned by the water-repair review, not this common-edge review',
        'finalBaseBinding':cw.read(ROOT/'r08_c14/repairs/west-common-edge'/FINAL_BASE_NAME),'finalC13MatchesActuallyReviewedPreWaterC13':True,'result':'pass-within-common-edge-scope','formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False}
    path=FINAL/'qa/review.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'review':str(path),'qaImagesExactlyMatchPriorActualInspection':len(proofs)-len(changed),'qaImagesFreshActuallyViewed':len(changed),'outputs':new['outputs']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
