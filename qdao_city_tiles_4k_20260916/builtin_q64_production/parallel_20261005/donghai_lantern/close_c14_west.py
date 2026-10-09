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
FINAL=ROOT/'r08_c14/west-final'

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
    for e in new['qa']:
        previous=prior[Path(e['file']).name]
        cw.check(e['file'],e['sha256']);cw.check(previous['file'],previous['sha256'])
        cw.require(e['pairRectXYXY']==previous['pairRectXYXY'],'QA coordinates changed')
        cw.require(np.array_equal(cw.rgb(e['file'],tuple(e['pixels'])),cw.rgb(previous['file'],tuple(previous['pixels']))),'Final QA pixels differ from actually viewed pixels')
        proofs.append({'final':cw.info(e['file']),'actuallyViewedPrior':cw.info(previous['file']),'pixels':e['pixels'],'pairRectXYXY':e['pairRectXYXY'],'pixelArrayExactlyIdentical':True,'fileBytesExactlyIdentical':e['sha256']==previous['sha256']})
    old_outputs={e['id']:e for e in old['outputs']}
    outputs={e['id']:e for e in new['outputs']}
    cw.require(outputs['r08_c13']['sha256']==old_outputs['r08_c13']['sha256'],'Final water substitution changed c13 unexpectedly')
    for e in new['outputs']:cw.check(e['file'],e['sha256'])
    report={**old_review,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'method':'The 21 final QA images are verified pixel-for-pixel identical to the actual original-detail visual inspection recorded in pre-water/qa/review.json. Final baseline substitution affects only disjoint c14 water regions. This is inherited scoped visual evidence plus fresh current-pixel verification, not a second full visual inspection.',
        'manifest':cw.info(new_manifest),'outputs':new['outputs'],'priorVisualReview':cw.info(old_review_path),'reviewedImages':[{k:e[k] for k in ('file','sha256','pixels','pairRectXYXY')} for e in new['qa']],
        'priorQAEqualityProofs':proofs,'waterRepairStatus':'present in final east base; water region QA remains owned by the water-repair review, not this common-edge review',
        'finalBaseBinding':cw.read(ROOT/'r08_c14/repairs/west-common-edge/final-base.json'),'finalC13MatchesActuallyReviewedPreWaterC13':True,'result':'pass-within-common-edge-scope','formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False}
    path=FINAL/'qa/review.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'review':str(path),'qaImagesExactlyMatchActualInspection':len(proofs),'outputs':new['outputs']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
