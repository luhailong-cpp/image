"""Commit only a doubly reviewed r07_c15 refined candidate; immutable south is checked."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import assembly_r07_c15 as a
R=a.ROOT;T=a.TILE;D=T/'repairs/unified';F=D/'refined';S=R/'r08_c15/output/r08_c15.png';SE=R/'r08_c15/output/extended-context.png'
S_SHA='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585';SE_SHA='1824c937740587c2d7fa029c43ebfe15df4380ce9d15ad204924cbbe60572c72'
OLD='3d6784d05e08447095081e0a2c425a1d11b2f7c461a7ff1dd74d9efa7644ea13'
def main(expected):
 assert a.sha(S)==S_SHA and a.sha(SE)==SE_SHA
 manifest=a.load_json(F/'manifest.json');assert a.sha(F/'candidate.png')==expected==manifest['candidate']['sha256']
 producer=a.load_json(F/'producer-review.json');independent=a.load_json(F/'root-independent-review.json')
 assert producer['candidateSha256']==expected and producer['passed'] is True
 assert independent['candidateSha256']==expected and independent['passed'] is True
 arrays,entries,missing=a.load_sources();assert not missing
 old=a.load_json(a.OUT/'assembly-manifest.json');assert a.sha(a.ART)==OLD==old['output']['sha256']
 old['historicalStatus']='Superseded after local repair. Text source evidence retained.'
 a.save_json(T/'qa/initial-assembly-manifest.json',old)
 final=Image.open(F/'candidate.png').convert('RGB');ext=Image.open(F/'extended-context.png').convert('RGB')
 assert final.size==(4096,4096) and ext.size==(4326,4326)
 assert np.array_equal(np.asarray(final),np.asarray(ext)[115:4211,115:4211])
 south,si=a.checked_south()
 info=a.save_image(a.ART,final);ei=a.save_image(a.OUT/'extended-context.png',ext);assert info['sha256']==expected
 qa=a.write_qa(final,ext,south)
 for q in qa:q['visualInspection']='passed-by-producer-and-root-at-identical-candidate-pixels' if 'halo-comparison' not in q['file'] else 'diagnostic-not-acceptance'
 coverage=old['qaCoverage'].copy();coverage['inspectionStatus']='producer-and-independent-root-passed'
 params=old['parameters'].copy();params.update({'nativeAISeamRepairs':True,'registration':True,'spatialResampling':True,'colorCorrection':True,'boundedLocalRGBDifferenceCorrection':True,'sourcePixelsUnchangedOutsideNarrowBlendTransitions':False,'localRegistration':'bounded horizontal resampling of existing object boundaries only; recorded maps and coefficients','imageBlur':False,'resampledForUpscaling':False})
 result={**old,'historicalStatus':None,'createdAtUtc':a.utc_now(),'status':'complete-tile-producer-and-root-reviewed','formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False,'output':info,'extendedContext':ei,'nativeSources':entries,'parameters':params,'southBaseline':si,'qa':qa,'qaCoverage':coverage,'localRepair':{'manifest':str(F/'manifest.json'),'sha256':a.sha(F/'manifest.json'),'producerReview':str(F/'producer-review.json'),'producerReviewSha256':a.sha(F/'producer-review.json'),'rootIndependentReview':str(F/'root-independent-review.json'),'rootIndependentReviewSha256':a.sha(F/'root-independent-review.json')},'originalAssemblyScriptSha256':old.get('script',{}).get('sha256'),'script':{'file':str(R/'assembly_r07_c15.py'),'sha256':a.sha(R/'assembly_r07_c15.py')},'commitScript':{'file':str(Path(__file__)),'sha256':a.sha(__file__)}}
 a.save_json(a.OUT/'assembly-manifest.json',result)
 a.save_json(a.QA/'manifest.json',{'qa':qa,'coverage':coverage,'candidateSha256':expected,'visualInspection':'producer-and-independent-root-passed'})
 a.save_image(a.OUT/'current-preview.png',final.resize((1024,1024),Image.Resampling.LANCZOS));a.save_json(a.OUT/'current-preview.json',{'source':info,'scale':0.25,'previewOnly':True,'notNativePixelQA':True})
 a.save_json(a.OUT/'status.json',{'status':result['status'],'output':info,'nativePatchesPresent':16,'formalAccepted':False,'wholeCityComplete':False,'southUnchanged':True})
 assert a.sha(S)==S_SHA and a.sha(SE)==SE_SHA
 a.save_json(F/'commit.json',{'createdAtUtc':a.utc_now(),'output':info,'extendedContext':ei,'southUnchanged':True,'dependentIntermediateCleanup':'deferred until all current references and parent consumers are checked'})
 print(json.dumps({'output':info,'extendedContext':ei,'status':result['status']},indent=2))
if __name__=='__main__':main(sys.argv[1])

