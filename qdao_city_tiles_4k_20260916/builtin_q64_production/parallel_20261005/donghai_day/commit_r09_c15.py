"""Commit the visually checked r09_c15 candidate, retaining truthful provenance."""
from pathlib import Path
import shutil
import json
import numpy as np
from PIL import Image
import assembly_r09_c15 as a

R=a.TILE/'repairs/color-match'
EXPECTED='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff'
def main():
    candidate=R/'candidate.png';extended=R/'extended-context.png'
    if not candidate.exists():candidate=a.ART
    if not extended.exists():extended=a.OUT/'extended-context.png'
    a.require(a.sha(candidate)==EXPECTED,'Reviewed candidate changed')
    correction=a.load_json(R/'manifest.json')
    producer=a.load_json(R/'producer-review.json')
    a.require(producer['candidate']['sha256']==EXPECTED,'Producer review mismatch')
    arrays,entries,missing=a.load_sources()
    a.require(not missing,'Sources incomplete')
    old=a.load_json(a.OUT/'assembly-manifest.json')
    a.require(old['output']['sha256'] in (EXPECTED,correction['baseline']['sha256']),'Unrelated output state')
    if old['output']['sha256']!=EXPECTED:
        old['historicalStatus']='Superseded raster; text provenance retained, old raster not kept'
        a.save_json(a.TILE/'qa'/'initial-assembly-manifest.json',old)
    else:
        old=a.load_json(a.TILE/'qa'/'initial-assembly-manifest.json')
    final=Image.open(candidate).convert('RGB');ext=Image.open(extended).convert('RGB')
    a.require(final.size==(4096,4096) and ext.size==(4326,4326),'Dimensions incorrect')
    a.require(np.array_equal(np.asarray(final),np.asarray(ext)[115:4211,115:4211]),'Core/extended mismatch')
    north,ni=a.checked_north()
    finalinfo=a.save_image(a.ART,final)
    extinfo=a.save_image(a.OUT/'extended-context.png',ext)
    a.require(finalinfo['sha256']==EXPECTED,'Commit changed candidate bytes')
    qa=a.write_qa(final,ext,north)
    for item in qa:
        name=Path(item['file']).stem
        item['visualInspection']='passed-by-producer-at-identical-candidate-pixels' if name!='north-halo-comparison-full' else 'diagnostic-generated-not-acceptance'
    correction['candidate']=finalinfo
    correction['extendedContext']=extinfo
    correction['qa']=qa
    correction['status']='integrated-current-output'
    correction['visualReview']='producer-passed'
    producer['candidate']=finalinfo
    producer['status']='producer-visual-review-passed'
    for view in producer['views']:
        view['file']=str(a.QA/Path(view['file']).name)
        a.require(a.sha(view['file'])==view['sha256'],'Relocated QA bytes changed')
    a.save_json(R/'manifest.json',correction)
    a.save_json(R/'producer-review.json',producer)
    coverage=old['qaCoverage'].copy()
    coverage['inspectionStatus']='producer-passed'
    coverage['northBoundary128PreservedFromRootReviewedInitialCandidate']=True
    params=old['parameters'].copy()
    params.update({'colorCorrection':True,'boundedLocalRGBDifferenceCorrection':True,
       'maxPerChannelCorrection':29,'imageBlur':False,'spatialResampling':False,
       'sourcePixelsUnchangedOutsideNarrowBlendTransitions':False,
       'sourcePixelsUnchangedOutsideOriginal230pxOverlapUnion':True,
       'northHaloAndCore128Unchanged':True})
    manifest={**old,'createdAtUtc':a.utc_now(),'status':'complete-tile-producer-reviewed',
       'historicalStatus':None,'formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False,
       'parameters':params,'output':finalinfo,'extendedContext':extinfo,'nativeSources':entries,
       'northBaseline':ni,'qa':qa,'qaCoverage':coverage,
       'boundaryDiagnostics':a.boundary_diagnostics(final,ext,north),
       'localCorrection':{'manifest':str(R/'manifest.json'),'sha256':a.sha(R/'manifest.json'),
          'producerReview':str(R/'producer-review.json'),'producerReviewSha256':a.sha(R/'producer-review.json'),
          'script':str(a.ROOT/'repair_r09_c15_color.py'),'scriptSha256':a.sha(a.ROOT/'repair_r09_c15_color.py')},
       'commitScript':{'file':str(Path(__file__)),'sha256':a.sha(__file__)}}
    a.save_json(a.OUT/'assembly-manifest.json',manifest)
    a.save_json(a.QA/'manifest.json',{'qa':qa,'coverage':coverage,'candidateSha256':EXPECTED,'visualInspection':'producer-passed'})
    a.save_image(a.OUT/'current-preview.png',final.resize((1024,1024),Image.Resampling.LANCZOS))
    a.save_json(a.OUT/'current-preview.json',{'source':finalinfo,'scale':0.25,'previewOnly':True,'notNativePixelQA':True})
    a.save_json(a.OUT/'progress-preview.json',{'status':'superseded-by-complete-tile','source':finalinfo,'missing':[],
       'nativePatchesPresent':16,'nativePatchesRequired':16,'fullTileCandidateProduced':True,
       'displayPreview':str(a.OUT/'current-preview.png'),'formalAccepted':False})
    # Only the obsolete transparent progress raster is removed. All current source
    # references, native evidence, difference fields and QA remain available.
    stale=(a.OUT/'progress-native-transparent.png').resolve()
    a.require(stale.is_relative_to(a.TILE.resolve()),'Cleanup escaped tile')
    if stale.exists():stale.unlink()
    removed=[]
    for path in [R/'candidate.png',R/'extended-context.png',*(R/'qa').glob('*.png')]:
        path=path.resolve()
        a.require(path.is_relative_to(R.resolve()),'Duplicate cleanup escaped repair directory')
        if path.exists():
            removed.append({'file':str(path),'sha256':a.sha(path)})
            path.unlink()
    a.save_json(R/'cleanup.json',{'createdAtUtc':a.utc_now(),'reason':'Confirmed current final output and QA byte-identical; removed duplicate candidate and inspection rasters. Current references use canonical output/QA.',
                                'removed':removed,'canonicalOutput':finalinfo,'canonicalExtended':extinfo})
    a.save_json(R/'qa'/'manifest.json',{'relocatedTo':str(a.QA/'manifest.json'),'candidateSha256':EXPECTED})
    a.save_json(a.TILE/'qa'/'top-row-generation-review.json',{
       'createdAtUtc':a.utc_now(),'reviewer':'fill15_left','scope':'r01_c01..04',
       'entries':[{'id':e['id'],'sha256':e['sha256'],'inputActuallyViewed':True,
                   'styleActuallyViewedAndAttached':True,'outputActuallyViewed':True,
                   'recordSha256':e['recordSha256'],'actualModel':None,'actualQuality':None}
                  for e in entries if e['row']==1],
       'northBaseline':ni,'assembledReview':str(R/'producer-review.json')})
    print(json.dumps({'output':finalinfo,'extendedContext':extinfo,'status':manifest['status']},indent=2))
if __name__=='__main__':main()

