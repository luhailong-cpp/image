"""Validate current DAY common-edge geometry without touching upstream pixels."""
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.dont_write_bytecode=True
import json
import numpy as np
from PIL import Image
import compose_west as cw

ROOT=Path(__file__).resolve().parent
DAY=ROOT.parent/'donghai_day'
DEST=ROOT/'r08_c14/repairs/west-common-edge'
MANIFEST=DAY/'tiles/west-integration-r08_c14-manifest.json'

def main():
    m=cw.read(MANIFEST)
    cw.DAY_MANIFEST=MANIFEST;cw.DAY_MANIFEST_SHA=cw.sha(MANIFEST)
    cw.EXPECTED_PARAMETERS=m['parameters']
    cw.require(m['tile']=='r08_c14','Wrong shared-edge tile')
    cw.require(m['parameters']['stripPairRectXYXY']==[3469,0,4723,4096],'Wrong repair strip')
    cw.require(m['parameters']['patchYStarts']==[0,1024,2048,2842],'Wrong native positions')
    cw.require(len(m['nativeRepairSources'])==4,'Need four native repair inputs')
    _,contract,masks,seams=cw.load_day_contract()
    for i,e in enumerate(m['nativeRepairSources']):
        cw.check(e['file'],e['sha256']);cw.check(e['recordFile'],e['recordSha256'])
        rec=cw.read(e['recordFile']);cw.require(rec['sha256']==e['sha256'],'Native record SHA disagrees')
        cw.require(e['globalRectXYXY']==[52621,28672+cw.STARTS[i],53875,29926+cw.STARTS[i]],'Wrong native global rectangle')
        cw.rgb(e['file'],(1254,1254))
    current=m['outputs'][1]
    cw.check(current['file'],current['sha256'])
    current_record=Path(current['file']+'.generation.json')
    cr=cw.read(current_record);cw.require(cr['sha256']==current['sha256'],'Current DAY c14 has additional unreviewed replacement')
    # Existing water repairs precede this strip and are outside c14's west 627px.
    water=[]
    for name in ('water-join','water-join-east'):
        p=DAY/'r08_c14/repairs'/name/'integration.json';d=cw.read(p)
        rect=d['changedPixelsRestrictedToRect'];cw.require(rect[0]>=627,'Water repair intersects joint source context')
        water.append({**cw.info(p),'rectXYXY':rect,'order':'before current west shared-edge integration','intersectsFestivalWest627Columns':False})
    review_path=DAY/'r08_c14/repairs/west-common-edge/integration-qa/review.json'
    review=cw.read(review_path)
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'dayManifest':contract,'dayNativeSources':m['nativeRepairSources'],'verifiedNativeCount':4,'verifiedOwnershipMasks':seams,'verifiedMaskCount':5,'currentDayC14MatchesSharedEdgeManifest':True,'waterRepairs':water,'upstreamReview':{'record':cw.info(review_path),'data':review},'additionalPostSharedEdgeRepairDetected':False,'spatialResampling':False,'noUpscaling':True,'formalAccepted':False,'onlyReadUpstream':True,'awaitingFestivalEastToneBase':True}
    DEST.mkdir(parents=True,exist_ok=True)
    out=DEST/'day-source-preflight.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'report':str(out),'dayManifestSha256':cw.sha(MANIFEST),'nativeSources':4,'maskCount':5,'waterRepairs':water,'currentDayC14Sha256':current['sha256']},ensure_ascii=False))

if __name__=='__main__':main()
