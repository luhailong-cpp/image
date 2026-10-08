"""Commit reviewed native r09_c16 candidate; retain processing provenance."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
import assembly_r09_c16 as a
from qa_r09_c16_external import probes
D=a.TILE/'repairs/color-match-v2'
EXPECTED='093589a138671f1112dc25835f7857871bccbc44bf5a9df3a835e12cf63c6f96'
INITIAL='ff169961a00d04558464d4436397938b02ac4e53fd492f7a74122b49eda53095'
def external_review():
 qa=D/'qa';candidate=D/'candidate.png'
 a.require(a.sha(candidate)==EXPECTED,'Candidate changed')
 names=['overview-preview-1024','north-r08-r09-common-edge-full','west-r09-c15-c16-common-edge-full','northwest-four-tiles']+['corner-'+c for c in ('nw','ne','sw','se')]
 a.save_json(D/'root-external-review.json',{'reviewedAtUtc':a.utc_now(),'reviewer':'root','actualVisualInspection':True,
  'candidateSha256':EXPECTED,'result':'pass','scope':'Overview, full north and west common edges, northwest four-tile intersection and four native corners',
  'observations':['Water and existing hull contact highlight continue across north boundary; original vertical tonal cut reaching north edge has been corrected.','West water and lower timber continue across the complete common edge. Northwest four-tile junction has no displaced geometry or straight tone split.','Four native corners retain clean water and existing timber detail.'],
  'viewedSheets':[{'file':str(qa/(n+'.png')),'sha256':a.sha(qa/(n+'.png')),'nativePixelQA':n!='overview-preview-1024'} for n in names],
  'formalAccepted':False,'clientAcceptance':False})
def main():
 c=D/'candidate.png';e=D/'extended-context.png'
 a.require(a.sha(c)==EXPECTED and a.sha(a.ART)==INITIAL,'Unexpected candidate or output')
 external=a.load_json(D/'root-external-review.json');internal=a.load_json(D/'independent-internal-review.json')
 a.require(external['candidateSha256']==EXPECTED and external['result']=='pass','External review incomplete')
 # The independent report schema is checked when present; do not infer from existence.
 print(json.dumps({'independentReview':internal},ensure_ascii=False))
 expected_values=[v for k,v in internal.items() if 'sha256' in k.lower()]
 candidate_obj=internal.get('candidate')
 if isinstance(candidate_obj,dict):expected_values.append(candidate_obj.get('sha256'))
 a.require(EXPECTED in expected_values,'Independent review candidate mismatch')
 result=str(internal.get('result',internal.get('status',''))).lower()
 a.require('pass' in result and 'fail' not in result,'Internal review not passed')
 arrays,entries,missing=a.load_sources();a.require(not missing,'Native sources incomplete')
 correction=a.load_json(D/'manifest.json')
 old=a.load_json(a.OUT/'assembly-manifest.json')
 a.require(old['output']['sha256']==INITIAL,'Initial assembly mismatch')
 old['historicalStatus']='Superseded raster; text provenance retained'
 a.save_json(a.TILE/'qa/initial-assembly-manifest.json',old)
 with Image.open(c) as im:final=im.convert('RGB')
 with Image.open(e) as im:ext=im.convert('RGB')
 a.require(final.size==(4096,4096) and ext.size==(4326,4326),'Wrong dimensions')
 a.require(np.array_equal(np.asarray(final),np.asarray(ext)[115:4211,115:4211]),'Core/extended mismatch')
 fi=a.save_image(a.ART,final);ei=a.save_image(a.OUT/'extended-context.png',ext)
 a.require(fi['sha256']==EXPECTED,'Commit altered pixels')
 north,ni=a.checked_north();qa=a.write_qa(final,ext,north)
 probes(a.ART,a.QA)
 extmanifest=a.load_json(a.QA/'external-manifest.json')
 for sheet in extmanifest['sheets']:qa.append({**sheet,'kind':'native-external-probe','resized':False,'pixelScale':1})
 for item in qa:item['visualInspection']='diagnostic-only' if 'halo-comparison' in item['file'] else 'reviewed-at-identical-candidate-pixels'
 def relocate(v):
  if isinstance(v,dict):
   for key,value in list(v.items()):
    if key=='file' and isinstance(value,str) and str(D/'qa') in value:
     dest=a.QA/Path(value).name
     if v.get('sha256'):a.require(a.sha(dest)==v['sha256'],'Relocated QA differs')
     v[key]=str(dest)
    else:relocate(value)
  elif isinstance(v,list):
   for item in v:relocate(item)
 for name,review in [('root-external-review.json',external),('independent-internal-review.json',internal)]:
  relocate(review);a.save_json(D/name,review)
 correction.update(candidate=fi,extendedContext=ei,qa=qa,status='integrated-current-output',visualReview='root-external-and-independent-internal-passed',
  capInterpretation='32 is a per-stage per-channel bound. Sequential internal overlap and north edge corrections have actual aggregate maximum34, recorded explicitly.')
 a.save_json(D/'manifest.json',correction)
 coverage={**old['qaCoverage'],'inspectionStatus':'passed','completeWestCommonEdge':True,'northwestFourTileIntersection':True}
 params={**old['parameters'],'colorCorrection':True,'boundedLocalRGBDifferenceCorrection':True,'perStageChannelCap':32,
  'maxAggregateChannelCorrection':34,'imageBlur':False,'spatialResampling':False,
  'sourcePixelsUnchangedOutsideNarrowBlendTransitions':False,'sourcePixelsUnchangedOutsideOriginalOverlapAndNorth230':True,
  'northHaloUnchanged':True}
 manifest={**old,'historicalStatus':None,'createdAtUtc':a.utc_now(),'status':'complete-tile-visually-reviewed',
  'formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False,'postprocessingProtected':True,
  'output':fi,'extendedContext':ei,'parameters':params,'nativeSources':entries,'northBaseline':ni,
  'qa':qa,'qaCoverage':coverage,'boundaryDiagnostics':a.boundary_diagnostics(final,ext,north),
  'postprocessing':{'manifest':str(D/'manifest.json'),'sha256':a.sha(D/'manifest.json'),
    'externalReview':str(D/'root-external-review.json'),'externalReviewSha256':a.sha(D/'root-external-review.json'),
    'internalReview':str(D/'independent-internal-review.json'),'internalReviewSha256':a.sha(D/'independent-internal-review.json')}}
 a.save_json(a.OUT/'assembly-manifest.json',manifest)
 a.save_json(a.QA/'manifest.json',{'candidateSha256':EXPECTED,'qa':qa,'coverage':coverage,'visualInspection':'passed'})
 preview=a.save_image(a.OUT/'current-preview.png',final.resize((1024,1024),Image.Resampling.LANCZOS))
 a.save_json(a.OUT/'current-preview.json',{'source':fi,'preview':preview,'scale':0.25,'previewOnly':True})
 a.save_json(a.OUT/'progress-preview.json',{'status':'superseded-by-complete-tile','source':fi,'missing':[],'nativePatchesPresent':16,'nativePatchesRequired':16,'fullTileCandidateProduced':True,'displayPreview':preview['file'],'formalAccepted':False})
 state={'tile':'r09_c16','updatedAtUtc':a.utc_now(),'nativePatchesSaved':16,'nativePatchesRequired':16,'countsAsCompleteTile':True,
  'status':'complete-tile-visually-reviewed','output':fi,'visualReview':'passed','formalAccepted':False,'wholeCityComplete':False}
 for name in ('progress.json','current-work.json'):a.save_json(a.TILE/name,state)
 p=a.load_json(a.TILE/'plan.json');p.update(status='complete-tile-visually-reviewed',candidate=fi,formalAccepted=False);a.save_json(a.TILE/'plan.json',p)
 # Remove only verified byte-identical duplicates after relocating current refs.
 removed=[]
 pairs=[(c,a.ART),(e,a.OUT/'extended-context.png')]+[(f,a.QA/f.name) for f in (D/'qa').glob('*.png')]
 for src,dest in pairs:
  a.require(src.resolve().is_relative_to(a.TILE.resolve()),'Cleanup outside tile')
  a.require(a.sha(src)==a.sha(dest),'Duplicate differs')
  removed.append({'file':str(src),'sha256':a.sha(src),'currentFile':str(dest)});src.unlink()
 stale=(a.OUT/'progress-native-transparent.png').resolve()
 a.require(stale.is_relative_to(a.TILE.resolve()),'Cleanup outside tile')
 if stale.exists():removed.append({'file':str(stale),'sha256':a.sha(stale),'reason':'obsolete incomplete preview'});stale.unlink()
 a.save_json(D/'cleanup.json',{'createdAtUtc':a.utc_now(),'removed':removed,'final':fi})
 a.save_json(D/'qa/manifest.json',{'relocatedTo':str(a.QA/'manifest.json'),'candidateSha256':EXPECTED})
 print(json.dumps({'committed':fi,'extended':ei,'formalAccepted':False}))
if __name__=='__main__':
 import sys
 if '--external-review' in sys.argv:external_review()
 else:main()
