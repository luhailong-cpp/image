from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
prep=read(OUT/'preparation.json')
for item in prep['nativeInputs']+prep['references']:assert sha(item['file'])==item['sha256']
raw=np.asarray(Image.open(OUT/'native.png').convert('RGB'),dtype=float)
ctx=np.asarray(Image.open(OUT/'context.png').convert('RGB'),dtype=float)
faces=[]
for label,box in [('right_middle_face',[1024,480,1040,560]),('bottom_gray_face',[350,1145,700,1240]),('left_ivory_face',[40,400,110,750])]:
    x0,y0,x1,y1=box;a=ctx[y0:y1,x0:x1];b=raw[y0:y1,x0:x1]
    faces.append({'name':label,'pieceBox':box,'contextMeanRGB':a.mean((0,1)).tolist(),'rawMeanRGB':b.mean((0,1)).tolist(),'rawMinusContextMeanRGB':(b-a).mean((0,1)).tolist(),'contextStdRGB':a.std((0,1)).tolist(),'rawStdRGB':b.std((0,1)).tolist(),'meanAbsRGB':np.abs(b-a).mean((0,1)).tolist()})
write('face-diagnostics.json',{'regions':faces,'note':'Native pixels, unregistered. Texture standard deviation is descriptive only; no automated pass or adjustment.'})
review={
 'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'native':info(OUT/'native.png'),'context':info(OUT/'context.png'),
 'viewedFiles':['context.png','layout-reference-only.png','native.png','qa-hard-context-return.png','qa-bottom-original-above-raw-below.png','qa-hard-left-x115.png','qa-hard-right-x1024.png'],
 'canonicalStructurePresent':True,
 'structureObservations':'Both curved ivory side bands, upper/middle/lower inset stone faces, broad diagonal ivory cross-band, upper thinner transverse seam and right lower relief are present. No missing main structure requiring invention was identified.',
 'directNativeJoinAccepted':False,'localAccepted':False,'formalAccepted':False,'countsAsComplete4KTile':False,'joinedIntoCurrent':False,
 'defects':[
  {'location':'bottom y1139; lower central gray slab right contour / inside edge of right ivory curve','kind':'geometry','observed':'Raw contour is40..42px left of the original context; hard return creates an obvious step.','measurementEvidence':info(OUT/'comparison.json')},
  {'location':'bottom y1139; lower central gray slab left contour','kind':'geometry','observed':'Smaller approximately6..12px offset; some gradient measurements select different bevel subedges.'},
  {'location':'lower gray slab across y1139','kind':'texture','observed':'Generated pale mottling is more pronounced than the smooth original gray face; geometry correction alone will not guarantee a seamless material return.'},
  {'location':'right x1024, approximately y460..670','kind':'material','observed':'Gray generated face meets a warmer beige native face; requires actual tone/material inspection after any geometry correction.'},
  {'location':'left x115','kind':'material','observed':'Light color/texture step; main original edge endpoints appear aligned.'}
 ],
 'independentVisualReview':{'agent':'registration_visual_audit','filesActuallyViewed':['context.png','layout-reference-only.png','native.png','qa-hard-context-return.png','qa-bottom-original-above-raw-below.png','qa-hard-right-x1024.png'],'conclusion':'All structures exist, but current hard join is rejected. Bottom geometry and material require local repair. The prior24px registration experiment is insufficient for approximately40px offset. Preserve the newly rendered body; consider more original bottom context for a targeted repair rather than treating the whole structure as failed.'},
 'registrationApplied':False,'toneCorrectionApplied':False,'blendingApplied':False,
 'registrationAssessment':{'potentiallyEligible':True,'reason':'Existing side contours correspond one-to-one, so mechanical research may be legitimate; it cannot invent missing geometry.','requiredBottomRightCorrectionApproxPx':[40,42],'risks':['Only115px original bottom context currently constrains the long curved edge.','A correction must extend over a long unknown span and fade continuously; short boundary-only flow risks a width bulge.','Clouded gray texture and warm/cool face mismatch can persist after contour correction.'],'notAnApproval':True},
 'newCalls':1,'maxCallsAuthorizedForThisStep':1,
 'sourceScope':'All references have frozen file hashes. Coupled-v2 corner and coupled-v1 left strip are identical to their opposite version within required right115px ROI. Wider external corner/seams remain unaccepted WIP.',
 'allSourceHashesReverified':True,'allWritesConfinedTo':str(OUT),
 'faceDiagnostics':info(OUT/'face-diagnostics.json'),
}
write('visual-review.json',review)
write('result.json',{'native':info(OUT/'native.png'),'status':'native_candidate_needs_local_bottom_repair','localAccepted':False,'formalAccepted':False,'joinedIntoCurrent':False,'newGenerationCalls':1,'nativeDimensions':[1254,1254],'globalCropLTRB':[36749,31629,38003,32883],'tileLocalCropLTRB':[-115,2957,1139,4211],'knownPixels':537165,'missingPixelsRendered':1035351,'newMissingPixelsAccepted':0,'complete4KTilesAdded':0,'visualReview':info(OUT/'visual-review.json'),'generationRecord':info(OUT/'native.png.generation.json'),'actualToolReceipt':info(OUT/'tool-response.json'),'comparison':info(OUT/'comparison.json'),'allWritesConfinedTo':str(OUT)})
readme='''# r08_c10 / r04_c01 v1

One built-in image generation completed. Native1254x1254 original bytes are saved as `native.png`; SHA256168c4928c746355cb4c8474d80b3d3ecab24e4234808487a941fd33d911a3587.

Tile-local crop `[-115,2957,1139,4211]`; global crop `[36749,31629,38003,32883]`. Source context contains genuine native left115, right230 and bottom115 strips, including a verified bottom-left115 square from coupled-v2/r09_c09.537165 known pixels and1035351 newly painted missing pixels. The prepared checkpoint snapshot froze current/v004 at the actual preparation time; source details and exact crops are in `preparation.json`.

Both curved ivory bands and the broad diagonal cross-band are present. This is a candidate awaiting local repair, not an accepted join. Bottom gray/ivory right contour is40..42px left of original. Smaller left-bottom offset and stronger gray mottling also need repair; right middle face has a warm/cool mismatch. Direct hard return visibly steps. No registration, tone correction, blend or current write was performed.

Native evidence: `native.png.generation.json`, `prompt.txt`, `request.json`, `tool-response.json`, `preparation.json`, `comparison.json`, `face-diagnostics.json`, `visual-review.json`. Source bytes and all input hashes were reverified. Inspect `qa-hard-context-return.png` and side/bottom native QA crops.

Generation used the host-managed built-in image_gen path with the approved04-guild style image actually viewed and attached. Batch target is gpt-image-2.5-sunburst/max. Submitted model/quality/size selectors and actual returned model/quality are null because the host tool exposes none. generatedAt is null; observedCompletionAt is2026-10-05 18:45:50 UTC. Actual output hint and host path are preserved. No API route or additional generation was used.

All new files stay in this piece directory. No current/progress/source-checkpoint or cross-directory image was modified; no artwork was deleted. This candidate contributes zero accepted new pixels and zero complete4096 tiles until reviewed repair is completed.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
write('artifact-manifest.json',{'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'files':[info(p) for p in sorted(OUT.iterdir()) if p.is_file()]})
print(json.dumps({'result':info(OUT/'result.json'),'review':info(OUT/'visual-review.json'),'native':info(OUT/'native.png'),'faces':faces},ensure_ascii=False))
