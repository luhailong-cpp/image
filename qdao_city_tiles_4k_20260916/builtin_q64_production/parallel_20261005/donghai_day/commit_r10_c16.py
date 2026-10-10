"""Commit exactly reviewed pixels and keep complete processing provenance."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
from qa_r10_pair import probes
R=Path(__file__).resolve().parent;D=a.TILE/'repairs/west-color-v1'
EXPECTED='5089cf2e5fd0d00fdc5d73eac046bf41b9b816b3200523593f21f0f1fc9c9d87'
INITIAL='76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7'
def proof(path):return {'file':str(path),'sha256':a.sha(path)}
def main():
 a.require(a.sha(D/'candidate.png')==EXPECTED,'Candidate changed')
 a.require(a.sha(a.ART)==INITIAL,'Canonical was already changed; no blind overwrite')
 review=D/'root-final-external-review.json';rv=a.load_json(review)
 a.require(rv.get('candidateSha256')==EXPECTED and rv.get('result')=='pass','Final external review missing')
 west=R/'r10_c15/output/r10_c15.png';a.require(a.sha(west)==rv['west']['sha256'],'Final reviewed west changed')
 plan=a.load_json(a.TILE/'plan.json');a.require(plan['neighbors']['west']['bindingStatus']=='bound' and plan['neighbors']['west']['sha256']==a.sha(west),'Final west unbound')
 report_paths=[a.TILE/'repairs/north-integrated-color-v3/root-north-review.json',a.TILE/'repairs/north-integrated-color-v3/independent-internal-review.json',D/'root-west-scope-review.json',D/'independent-west-internal-review.json',review]
 for rp in report_paths:a.require(a.load_json(rp).get('result')=='pass','Report not passed: '+str(rp))
 arrays,entries,missing=a.load_sources();a.require(not missing,'Incomplete natives')
 old=a.load_json(a.OUT/'assembly-manifest.json');a.require(old['output']['sha256']==INITIAL,'Initial manifest mismatch')
 with Image.open(D/'candidate.png') as im:final=im.convert('RGB')
 with Image.open(D/'extended-context.png') as im:ext=im.convert('RGB')
 a.require(final.size==(4096,4096) and ext.size==(4326,4326),'Wrong dimensions')
 a.require(np.array_equal(np.asarray(final),np.asarray(ext)[115:4211,115:4211]),'Core/context mismatch')
 old['historicalStatus']='Superseded initial raster; native inputs and original masks retained for reconstruction'
 a.save_json(a.TILE/'qa/initial-assembly-manifest.json',old)
 fi=a.save_image(a.ART,final);ei=a.save_image(a.OUT/'extended-context.png',ext);a.require(fi['sha256']==EXPECTED,'Commit changed pixels')
 north,ni=a.checked_north();qa=a.write_qa(final,ext,north)
 for q in qa:
  original=D/'qa/assembly'/Path(q['file']).name
  a.require(a.sha(original)==q['sha256'],'Final internal QA differs from reviewed candidate')
  q['visualInspection']='diagnostic-only' if 'halo-comparison' in q['file'] else 'passed-with-exact-pixel-review-chain'
 probes(west,a.ART,a.TILE/'qa/external-final')
 pair=a.load_json(a.TILE/'qa/external-final/external-manifest.json')
 for q in pair['sheets']:q.update(visualInspection='passed',kind='native-external-common-boundary',pixelScale=1)
 qa+=pair['sheets']
 manifests=[a.TILE/'repairs/internal-final-v2/manifest.json',a.TILE/'repairs/north-integrated/manifest.json',a.TILE/'repairs/north-integrated-color-v3/manifest.json',D/'manifest.json']
 diag=a.boundary_diagnostics(final,ext,north);diag['northBoundaryHasNotBeenBlendedOrCorrected']=False;diag['visualReview']='passed-with-linked-native-QA'
 manifest={**old,'historicalStatus':None,'createdAtUtc':a.utc_now(),'status':'complete-tile-producer-and-independent-reviewed','output':fi,'extendedContext':ei,'nativeSources':entries,'northBaseline':ni,'westBaseline':{'file':str(west),'sha256':a.sha(west)},'parameters':{**old['parameters'],'nativeLocalRepairs':True,'boundedRGBDifferenceFields':True,'colorCorrection':True,'sourcePixelsUnchangedOutsideNarrowBlendTransitions':False,'geometryWarp':False,'imageBlur':False,'sourceUpscaling':False},'postprocessing':{'manifests':[proof(p) for p in manifests],'reviews':[proof(p) for p in report_paths],'candidate':proof(D/'candidate.png')},'postprocessingProtected':True,'qa':qa,'qaCoverage':{**old['qaCoverage'],'inspectionStatus':'passed','completeWestCommonEdge':True,'northwestFourTileIntersection':True},'boundaryDiagnostics':diag,'formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False}
 a.save_json(a.OUT/'assembly-manifest.json',manifest);a.save_json(a.TILE/'qa/final-review-index.json',{'candidate':fi,'reviews':[proof(p) for p in report_paths],'qa':qa,'formalAccepted':False})
 preview=a.save_image(a.OUT/'current-preview.png',final.resize((1024,1024),Image.Resampling.LANCZOS));a.save_json(a.OUT/'current-preview.json',{'source':fi,'preview':preview,'previewOnly':True,'scale':0.25})
 state={'tile':'r10_c16','updatedAtUtc':a.utc_now(),'nativePatchesSaved':16,'nativePatchesRequired':16,'countsAsCompleteTile':True,'status':'complete-tile-producer-and-independent-reviewed','output':fi,'visualReview':'passed','formalAccepted':False,'wholeCityComplete':False}
 for n in ['progress.json','current-work.json']:a.save_json(a.TILE/n,state)
 plan.update(status=state['status'],candidate=fi,formalAccepted=False);a.save_json(a.TILE/'plan.json',plan)
 a.save_json(D/'commit.json',{'committedAtUtc':a.utc_now(),'output':fi,'extendedContext':ei,'manifest':proof(a.OUT/'assembly-manifest.json'),'formalAccepted':False})
 print(json.dumps({'committed':fi,'formalAccepted':False}))
if __name__=='__main__':main()
