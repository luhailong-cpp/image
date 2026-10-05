"""Record observed QA, source identities and inherited equal-pixel evidence."""
import datetime,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;S=R.parents[1];V=R/'full-rect-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
source=S/'next_tile_r08_c07/continuation-20260923/qa-repair-20260923/repaired-v1/r08_c07.png'
assert sha(source)=='7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6'
candidate=V/'r08_c07.png'
with Image.open(candidate) as im:im.load();assert im.size==(4096,4096)
equal=[]
for old,new in [('context-after.png','context-after.png'),('qa/return-top.png','return-top.png'),('qa/return-bottom.png','return-bottom.png'),('qa/return-left.png','return-left.png'),('qa/return-right.png','return-right.png')]:
 p=R/old;q=V/'cross-2048-3072'/new
 assert np.array_equal(np.array(Image.open(p)),np.array(Image.open(q)))
 equal.append({'originalViewed':info(p),'currentEvidence':info(q),'decodedPixelsEqual':True})
gen1=S/'continuation_20260928T081700Z/repairs/c07-cross-2048-3072.native.png.generation.json'
gen2=S/'continuation_20261004/c07-cross-3072-1024/native.png.generation.json'
review={'schemaVersion':1,'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':info(candidate),'repair':info(V/'repair.json'),
 'nativeGenerationRecords':[info(gen1),info(gen2)],'scope':'Two 1254-square local repairs and four full native return strips around each; not six complete 4096 seams or full city.',
 'inspectionMethod':'view_image detail=original; each context and each return strip shown at native image resolution; no visual passes inferred from SHA',
 'views':{'firstPatch':['context-after','return-top','return-bottom','return-left','return-right'],'secondPatch':['context-after','return-top','return-bottom','return-left','return-right']},
 'firstPatchEvidenceInheritedByExactPixels':equal,
 'localFindings':[
 {'patch':'cross-2048-3072','cropLTRB':[1421,2445,2675,3699],'centerStatus':'locally_improved','note':'Central dark-stone cross tone jump is removed, and center frame and gold path no longer have the old abrupt horizontal step. Center uses original native repair pixels.'},
 {'patch':'cross-2048-3072','area':'upper return transition','status':'failed_requires_further_repair','note':'Near patch-local x approximately 800/900 and y approximately 100..160, limited registration produces small bends in dark inset framing. The original vertical x2048 tone split remains beyond the repair window and returns through the outer fade.'},
 {'patch':'cross-2048-3072','area':'left/right and bottom returns','status':'failed_for_full_seam_continuity','note':'Original y3072 frame/stone discontinuity remains near left and right crop edges; x2048 straight tone division remains beyond the bottom crop. Local center improvement does not complete either 4096 seam.'},
 {'patch':'cross-3072-1024','cropLTRB':[2445,397,3699,1651],'centerStatus':'locally_improved','note':'Ornamental slab center is continuous with native detail; former rectangular cross discontinuity is removed in the central repair region.'},
 {'patch':'cross-3072-1024','area':'top/left/right returns','status':'failed_for_full_seam_continuity','note':'Old x3072 tone split remains above the repair, and y1024 tone split remains on the left gold strip and broad right-hand ivory slab outside the repair fade. No claim that these full lines pass.'},
 {'patch':'cross-3072-1024','area':'bottom return','status':'no_obvious_new_hard_seam_in_viewed_strip','note':'Viewed entire 1510x256 return strip; contours broadly continue. This narrow observation is not formal tile or seam acceptance.'}
 ],
 'otherAttempts':[{'candidate':info(R/'r08_c07.png'),'status':'single_patch_diagnostic_superseded_by_two_patch_candidate'},
 {'candidate':info(R/'cross-masks-v2/r08_c07.png'),'status':'rejected_visual_double_contours_at_mask_returns','note':'Narrow cross masks caused doubled inset borders and bright frame edges; not selected.'}],
 'overallStatus':'partial_local_improvement_unfinished_candidate_requires_further_seam_repairs','recommendedCurrentWorkFile':str(candidate),
 'globalSelectionUpdated':False,'formalAccepted':False,'runtimeAccepted':False,'fullSeamsPassedAdded':0,'fullJunctionsPassedAdded':0,
 'nextRepairTargets':['Continue x2048 and y3072 outside first 1254 window and inspect upper frame-return bends.','Continue x3072 and y1024 outside second 1254 window.','After local repair, regenerate all six complete internal seams and nine junctions; retain previously recorded south-edge failure until actually repaired.'],
 'retention':'No source image or diagnostic version deleted; parent explicitly requested preservation during this scoped integration.'}
with (R/'visual-review.json').open('x',encoding='utf-8') as f:json.dump(review,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'review':str(R/'visual-review.json'),'candidate':str(candidate),'sha256':sha(candidate),'sourceUnchanged':True}))
