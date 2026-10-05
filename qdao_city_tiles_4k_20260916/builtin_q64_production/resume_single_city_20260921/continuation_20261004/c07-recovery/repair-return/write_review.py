import datetime,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;V=R/'candidate-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
repair=json.loads((V/'repair.json').read_text(encoding='utf-8'))
candidate=V/'r08_c07.png'
with Image.open(candidate) as im:im.load();assert im.size==(4096,4096)
assert sha(candidate)=='322b8fab526479bf3eff208bc5ed7bf96296877d172187a8fbef56b731c5937c'
source=Path(repair['derivedFrom'][0]['file']);assert sha(source)==repair['derivedFrom'][0]['sha256']
before=np.array(Image.open(source).convert('RGB'));after=np.array(Image.open(candidate).convert('RGB'))
x0,y0,x1,y1=repair['cropLTRB'];mask=np.array(Image.open(V/'mask.png'));allowed=np.zeros((4096,4096),bool);allowed[y0:y1,x0:x1]=mask>0
assert np.array_equal(before[~allowed],after[~allowed])
evidence=[{'id':'context-after',**info(V/'context-after.png'),'pixels':[1254,1254],'resized':False}]+repair['qa']
review={'schemaVersion':1,'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':info(candidate),'repairRecord':info(V/'repair.json'),
 'scope':'1254 native repair of first recovery window upper framing bends and adjacent x2048 artificial material seam, plus four complete local return strips and two targeted native crops.',
 'method':'Actual view_image detail=original of native result, context-after, four return strips, frame-bends-repaired and upper-grid-junction.',
 'evidence':evidence,
 'localFindings':[
 {'id':'frame-bends-repaired','status':'local_visual_pass','note':'Former paired bends in the ivory frame and dark inset near global x approximately2220/2320,y approximately2540..2600 are now smooth, single contours. The 454x454 original-pixel target crop shows no added double border.'},
 {'id':'upper-grid-junction','status':'local_visual_pass','note':'The x2048/y2048 junction in the repaired portion has continuous stone tone and gold edge; the previous vertical material split and small horizontal step are removed in this viewed crop.'},
 {'id':'return-top','status':'no_new_double_contours_observed','note':'Viewed complete1510x256 strip. Frame bevels, gold channels and carved slab border join without an obvious new doubled contour.'},
 {'id':'return-left','status':'old_seam_remains_outside_repair','note':'No new double contour seen along the repair attachment; the original horizontal y2048 and y3072 line remains on the gold strip farther left, outside the repair region.'},
 {'id':'return-right','status':'old_seam_remains_outside_repair','note':'Viewed complete256x1510 strip. Native frame and stone remain single-edged, but the old y3072 step persists at the bottom, preserved near the outer attachment.'},
 {'id':'return-bottom','status':'old_seam_remains_near_outer_attachment','note':'Viewed complete1510x256 strip. Existing y3072 frame offset and stone tone line remain towards right x approximately2675 onward. No claim of full horizontal seam pass.'}
 ],
 'nativeMaterialObservation':'Blue-gray slab detail is a consistent fine texture in the newly repaired central area; no strong rectangular material split is visible in the two targeted inspection crops.',
 'overallStatus':'targeted_return_bends_fixed_with_scoped_local_pass_full_tile_still_unfinished','newImagegenCalls':1,'allowedMaximumImagegenCalls':2,
 'sourceUnchanged':True,'outsideMaskPixelsUnchanged':True,'nativeInputsUpscaled':False,'globalSelectionUpdated':False,
 'formalAccepted':False,'runtimeAccepted':False,'fullInternalSeamsPassedAdded':0,'completeTileAcceptedAdded':0,
 'nextIssue':'Continue y3072 near/right of x2675 and remaining 4096 seam lengths. The earlier six-seam failures cannot be cleared by these two local passes alone.',
 'modelEvidence':info(R/'native.png.generation.json'),'prompt':info(R/'prompt.txt'),'route':'builtin'}
with (R/'visual-review.json').open('x',encoding='utf-8') as f:json.dump(review,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'review':str(R/'visual-review.json'),'candidate':str(candidate),'sha256':sha(candidate),'status':review['overallStatus']},ensure_ascii=False))
