"""Commit the reviewed c16 candidate, preserving processing and source evidence."""
from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image
import assembly_r07_c16 as a

R=a.ROOT;T=a.TILE;D=T/'repairs/final-rail-v2'
INITIAL='2dbf08054591651fb62f3477ef79926f2d7696f773eaf26b5f8f1b18d886a06a'
def ref(p):return dict(file=str(p),sha256=a.sha(p))
def main(expected):
 c=D/'candidate.png';e=D/'extended-context.png';m=a.load_json(D/'manifest.json')
 assert a.sha(c)==expected==m['candidate']['sha256'] and a.sha(e)==m['extendedContext']['sha256']
 reviews=[]
 for name in ['review.json','independent-review.json']:
  p=D/name;r=a.load_json(p)
  assert r['candidateSha256']==expected and r['result']=='pass'
  reviews.append(ref(p))
 assert m['formalWestBound'] and m['finalNeighborRawROIValidation'] and m['allColumnsFrom780ExactlyPreserved']
 plan=a.load_json(T/'plan.json')
 for n in plan['neighbors'].values():assert n['bindingStatus']=='bound' and a.sha(n['file'])==n['sha256']
 for name in ['west','south','southwest']:
  n=m[name];assert a.sha(n['file'])==n['sha256']
 arrays,entries,missing=a.load_sources();assert not missing
 old=a.load_json(a.OUT/'assembly-manifest.json');assert a.sha(a.ART)==INITIAL==old['output']['sha256']
 a.save_json(D/'previous-assembly-manifest.json',{**old,'historicalStatus':'Superseded after reviewed repairs; textual provenance retained.'})
 final=Image.open(c).convert('RGB');ext=Image.open(e).convert('RGB')
 assert final.size==(4096,4096) and ext.size==(4326,4326)
 assert np.array_equal(np.asarray(final),np.asarray(ext)[115:4211,115:4211])
 records=['internal-color-match/manifest.json','integrated-south-v2/manifest.json','west-upper-three/manifest.json','integrated-southwest-v3/manifest.json','south-joint-color-v4/manifest.json','final-west-joint/manifest.json','final-rail-v2/manifest.json']
 chain=[ref(T/'repairs'/p) for p in records]
 for prior in m['insertionQA']:assert a.sha(prior['file'])==prior['sha256']
 fi=a.save_image(a.ART,final);ei=a.save_image(a.OUT/'extended-context.png',ext);assert fi['sha256']==expected
 south,si=a.checked_south();qa=a.write_qa(final,ext,south)
 for prior in m['insertionQA']:
  src=Path(prior['file']);dest=a.QA/src.name;shutil.copyfile(src,dest);assert a.sha(dest)==prior['sha256']
  qa.append({**prior,'file':str(dest),'kind':'reviewed-native-joint-or-insertion-QA'})
 for item in qa:item['visualInspection']='diagnostic-only' if 'halo-comparison' in item['file'] else 'passed-at-identical-final-candidate-pixels'
 params={**old['parameters'],'nativeAISeamRepairs':True,'colorCorrection':True,'boundedLocalRGBDifferenceCorrection':True,'sourcePixelsUnchangedOutsideNarrowBlendTransitions':False,'processingScope':'Recorded water overlap difference field and explicit native south/west repair masks only','registration':False,'spatialResampling':False,'imageBlur':False,'noUpscaling':True}
 coverage={**old['qaCoverage'],'inspectionStatus':'producer-and-independent-review-passed','completeWestCommonEdge':True,'completeSouthCommonEdge':True,'southwestFourTileIntersection':True}
 diagnostics=a.boundary_diagnostics(final,ext,south);diagnostics.update(southBoundaryHasNotBeenBlendedOrCorrected=False,visualReview='passed-native-pixel-inspection')
 manifest={**old,'createdAtUtc':a.utc_now(),'status':'complete-tile-visually-reviewed','formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False,'postprocessingProtected':True,'output':fi,'extendedContext':ei,'nativeSources':entries,'parameters':params,'qa':qa,'qaCoverage':coverage,'southBaseline':si,'westBaseline':plan['neighbors']['west'],'boundaryDiagnostics':diagnostics,'postprocessingChain':chain,'reviews':reviews,'commitScript':ref(Path(__file__))}
 a.save_json(a.OUT/'assembly-manifest.json',manifest)
 a.save_json(Path(str(a.ART)+'.generation.json'),dict(**fi,operation='Native1254 patch assembly and reviewed local joint repairs',assemblyManifest=ref(a.OUT/'assembly-manifest.json'),actualModel=None,actualQuality=None,postprocessingChain=chain,formalAccepted=False))
 a.save_json(a.QA/'manifest.json',dict(candidateSha256=expected,qa=qa,coverage=coverage,visualInspection='passed'))
 preview=a.save_image(a.OUT/'current-preview.png',final.resize((1024,1024),Image.Resampling.LANCZOS))
 a.save_json(a.OUT/'current-preview.json',dict(source=fi,preview=preview,scale=0.25,previewOnly=True,notNativePixelQA=True))
 state=dict(tile='r07_c16',updatedAtUtc=a.utc_now(),nativePatchesSaved=16,nativePatchesRequired=16,countsAsCompleteTile=True,status='complete-tile-visually-reviewed',output=fi,visualReview='passed',formalAccepted=False,wholeCityComplete=False)
 for name in ['progress.json','current-work.json']:a.save_json(T/name,state)
 plan.update(status=state['status'],candidate=fi,formalAccepted=False);a.save_json(T/'plan.json',plan)
 a.save_json(D/'commit.json',dict(createdAtUtc=a.utc_now(),output=fi,extendedContext=ei,immutableNeighborHashesRechecked=True,reviews=reviews,canonicalQA=str(a.QA),cleanup='Parent may remove superseded raster intermediates after current reference relocation; text evidence retained.'))
 a.save_json(T/'repairs/current-work-state.json',{**state,'canonicalExtended':ei,'activeRepairsComplete':True,'postprocessingProtected':True,'remaining':[]})
 print(json.dumps(dict(committed=fi,extendedContext=ei,status=state['status'])))
if __name__=='__main__':main(sys.argv[1])
