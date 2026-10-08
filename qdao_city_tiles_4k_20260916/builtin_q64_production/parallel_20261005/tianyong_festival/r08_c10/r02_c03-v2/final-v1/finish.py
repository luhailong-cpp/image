from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent;P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((D/'source-checkpoint-input.json').read_text(encoding='utf-8'))
assembly=json.loads((D/'assembly.json').read_text(encoding='utf-8'))
finding={'id':'r02c02-coupled-x2163-y1975-1983','status':'closed-in-prospective-candidate','tile':'r08_c10','findingTileLocalLTRB':[2133,1933,2250,2040],'specificFormerDiscontinuity':'x2163, y1975..1983','repairSource':info(P/'left-lower-repair-v1/native.png'),'repairReadNativeLTRB':[150,900,620,1160],'repairReadTileLocalLTRB':[2083,1809,2553,2069],'before':info(D/'qa'/'foot-finding-before.png'),'after':info(D/'qa'/'foot-finding.png'),'evidenceCropTileLocalLTRB':[2063,1909,2558,2109],'visualConclusion':'The old ivory inset cap ending abruptly at x2163 is gone. Warm-gray ring channel now continues down to a single rounded foot across x2163 through y1975..1983, with one connected ivory side bevel and continuous slate joint below. The same actual AI repair includes the complete adjacent ivory foot; native return strips show no second seam at x2358 (former crop cutoff) or at the bottom of the repair.','nativeScale':1,'noGeometricWarp':True,'noRescale':True,'wholeCityAccepted':False}
(D/'finding-closure.json').write_text(json.dumps(finding,ensure_ascii=False,indent=2),encoding='utf-8')
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'image':info(D/'joined.png'),'localAccepted':True,'formalAccepted':False,'reviewedAtNativeScale':['whole1254','top','left','right','bottom','top-left','bottom-right','left-lower','foot-finding','top-return','left-return','right-return','bottom-return','out-left-lower'],'findings':['Original native body preserves continuous ivory ring courses and cross-joints. Exact known edge source is recovered outside the declared return mask.','Existing actual native AI repair removes the lower-left wrong ivory panel and clipped highlight head; complete gray foot and adjacent ivory foot are integrated together.','Initial narrow repair sampling ended mid-foot and produced a small right-edge step. Taking the complete same-source foot through x620 removes it, without additional generation, shape warping or upscaling.','All four native return strips and bottom corners reviewed; no artificial boundary line, duplicated edge or abrupt width change remains at patch returns.','No geometric resampling, scaling, sharpening or tone adjustment was used. Only explicit native-source compositing masks.'],'findingClosure':info(D/'finding-closure.json'),'reviewer':'close_c03','noFormalAcceptanceClaim':True}
(D/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
j=Image.open(D/'joined.png')
specs=[('new-core',[230,230,1024,1024],None),('top-return',[150,150,1104,230],cp['fragment']),('left-return',[150,230,230,1024],cp['fragment']),('right-return',[1024,230,1104,1024],cp['fragment']),('bottom-return',[150,1024,1104,1160],cp['fragment'])]
patches=[];coverage=np.zeros((1254,1254),bool)
for name,b,prior in specs:
 out=D/f'{name}.png';j.crop(b).save(out);coverage[b[1]:b[3],b[0]:b[2]]=True
 p={'name':name,'asset':info(out),'cropFromJoinedLTRB':b,'destinationTile':'r08_c10','destinationTileLTRB':[b[0]+1933,b[1]+909,b[2]+1933,b[3]+909],'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True}
 patches.append(p)
 (D/f'{name}.png.generation.json').write_text(json.dumps({'derivation':'exact native crop','parent':info(D/'joined.png'),'cropLTRB':b,'nativeScale':1,'file':str(out),'sha256':sha(out),'destinationTileLTRB':p['destinationTileLTRB'],'formalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((1933,909,3187,2163)))
ja=np.array(j)
assert np.array_equal(ja[~coverage],c[:,:,:3][~coverage])
assert np.sum(c[:,:,3]==0)==630436
assert np.all(coverage[c[:,:,3]==0])
proof={'sourceCandidate':cp['fragment'],'unchangedPixelsOutsideFiveDeclaredROIs':True,'missingBefore':630436,'newCoreArea':794*794,'allMissingPixelsFilled':True,'maxAbsDx':0,'maxAbsDy':0,'maxAbsToneRGB':0,'noResize':True,'returnedNativeSourceDimensions':[[1254,1254],[1254,1254]],'sourceKnownPixelCount':int(np.sum(c[:,:,3]==255))}
(D/'roi-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r08_c10','nativeScale':1,'windowTileLocalLTRB':[1933,909,3187,2163],'windowGlobalLTRB':[38797,29581,40051,30835],'joined':info(D/'joined.png'),'visualReview':info(D/'visual-review.json'),'assembly':info(D/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':info(D/'source-checkpoint-input.json'),'findingClosure':info(D/'finding-closure.json'),'roiProof':info(D/'roi-proof.json'),'note':'All five crops must apply together; exact prior-source ROI verification mandatory. No root publication by subagent. Whole4K and wholecity acceptance requires remaining tile work and full seam audit.'}
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'joined.png.generation.json').write_text(json.dumps({'derivation':'native-source-composite','file':str(D/'joined.png'),'sha256':sha(D/'joined.png'),'nativeScale':1,'nativeSources':assembly['sources'],'actualModel':None,'actualQuality':None,'assembly':info(D/'assembly.json'),'formalAccepted':False,'findingClosure':info(D/'finding-closure.json')},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'manifest':info(D/'manifest.json'),'joined':info(D/'joined.png'),'newPixels':630436}))
