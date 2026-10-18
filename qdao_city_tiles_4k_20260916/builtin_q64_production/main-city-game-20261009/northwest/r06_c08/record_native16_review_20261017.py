from pathlib import Path
from datetime import datetime,timezone
import sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
Q=T/'qa/native16-restart-20261017-v1';m=p.read(Q/'manifest.json');cr=[]
for c in m['crops']:
 prior=c['matchingPriorReviews']
 if prior:
  bad=[r for r in prior if r['status']=='needs_repair'];status='needs_repair' if bad else 'passed'
  cr.append(dict(name=c['name'],file=c['file'],sha256=c['sha256'],kind=c['kind'],status=status,actuallyViewed=False,reusedActualVisualReview=True,matchingRGBPixelSHA256=c['rgbPixelSHA256'],evidence=bad or prior))
 else:
  assert c['name']=='north_seg1'
  cr.append(dict(name=c['name'],file=c['file'],sha256=c['sha256'],kind=c['kind'],status='passed',actuallyViewed=True,reusedActualVisualReview=False,finding='Exact actual north s04_01_native02 and selected r06_c08 top core joined crop viewed. Gold diagonal ridge outline and adjacent teal tile courses cross the boundary without displacement.'))
counts={kind:{s:sum(c['kind']==kind and c['status']==s for c in cr) for s in ['passed','needs_repair']} for kind in ['internal','external']}
r=dict(recordedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='/root/resume_r06_c08_20261017',candidate=m['candidate'],candidateWholeActuallyViewed=True,wholeViewPurpose='layout/material overview only; resized viewer is not native proof',cropReviews=cr,counts=counts,totalCount=len(cr),pixelHashReusedCount=sum(c['reusedActualVisualReview'] for c in cr),newActuallyViewedCount=sum(c['actuallyViewed'] for c in cr),internalQAPassed=False,formalAccepted=False,unavailableExternal=m['unavailableExternal'],pending=[c['name'] for c in cr if c['status']=='needs_repair'])
p.write_json(Q/'reviewed-status.json',r,replace=False)
cm=p.read(T/'candidate/native16-restart-20261017-v1/manifest.json')
p.write_json(T/'resume-checkpoint-20261017-v02.json',dict(recordedAtUtc=datetime.now(timezone.utc).isoformat(),tile='r06_c08',worker='/root/resume_r06_c08_20261017',selectedCoreCount=16,requiredCoreCount=16,missing=[],candidate=m['candidate'],candidateManifest=str(T/'candidate/native16-restart-20261017-v1/manifest.json'),sameWorldNativePixels=cm['pixelProof']['totalPixels'],nativeSourcesSelected=16,nativeSourceVersionCount=len(list((T/'native').glob('*.png'))),qaReview=dict(file=str(Q/'reviewed-status.json'),sha256=p.sha(Q/'reviewed-status.json')),counts=counts,completeCandidateProduced=True,internalQAPassed=False,formalAccepted=False,builtinGenerationResumedSuccessfully=True,actualModel=None,actualModelEvidence='Built-in tool returned no actual model metadata',newSelectedSourceIds=['s03_01_fix02','s04_04_fix02','s01_04_native01'],pending=['internal_y2048_seg1','west_seg3','west_joint2048'],unavailableExternal=m['unavailableExternal'],northGenerationCoordination='s01_04 generated from W/S/SW actual anchors after no s04_04 north selected source existed; actual top core source supplied to /root/continue_r07_c07 for its future south anchor. Northern seam still requires true neighbor review.',nextStep='Use north r05_c08 s04_04 actual selected core when available; then review only changed north cuts and resolve retained blue glaze issue in concentrated repair. No whole-tile/global pass is asserted.'),replace=False)
print({'counts':counts,'qaSha256':p.sha(Q/'reviewed-status.json'),'candidateSha256':m['candidate']['sha256']})

