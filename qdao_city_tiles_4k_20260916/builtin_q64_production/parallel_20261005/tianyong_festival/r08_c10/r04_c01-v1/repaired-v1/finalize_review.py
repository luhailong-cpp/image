from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
prep=read(OUT/'preparation.json')
for item in prep['nativeInputs']+prep['references']+[prep['retainedCandidate']]:assert sha(item['file'])==item['sha256']
for name in ['qa-bottom-left-corner.png','qa-bottom-right-corner.png']:
    write(name+'.generation.json',{'file':str(OUT/name),'sha256':sha(OUT/name),'derivedFrom':[info(OUT/'original-context.png'),info(OUT/'native.png'),info(OUT/'qa-hard-context-return.png')],'operation':'Native230-square crops arranged original / returned / hard context return horizontally; no resampling','newModelCalls':0})
review={
 'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'native':info(OUT/'native.png'),'editContext':info(OUT/'context.png'),'authoritativeOriginalContext':info(OUT/'original-context.png'),
 'viewedFiles':['context.png','layout-reference-only.png','native.png','qa-hard-context-return.png','qa-bottom-original-above-raw-below.png','qa-hard-right-x1024.png','qa-bottom-left-corner.png','qa-bottom-right-corner.png'],
 'operation':'One actual built-in localized AI redraw from restored native source context and explicit transparent repair polygons; no geometry warp',
 'materialRepair':{'improved':True,'observed':'Central middle stone face now warm ivory/beige; right-side gray/warm hard material cut is removed. Rounded corners and broad ivory cross-band remain intact.','rightMiddleFaceBox':[1024,480,1040,560],'beforeRawMinusOriginalMeanRGB':[-56.56875,-45.5984375,-23.6390625],'afterRawMinusOriginalMeanRGB':[-0.8703125,-3.65703125,-5.6484375]},
 'geometryRepair':{'accepted':False,'observed':'Lower gray slab right contour / inner edge of right ivory curve is still displaced left43..46px relative to native original. Hard return visibly steps at y1139. The smaller lower-left slab contour offset also persists.','bottomRightOffsetsByY':{'1143':-46,'1180':-44,'1220':-43,'1249':-43},'leftRightMajorEdgeOffsetsApproxPx':[0,3]},
 'textureRepair':{'improvedButIncomplete':True,'observed':'Bottom gray face is quieter than first candidate but still visibly more mottled than original smooth gray; a horizontal texture transition remains at hard return.','originalBottomGrayStdRGB':[2.1488,1.9733,1.9618],'firstCandidateBottomGrayStdRGB':[6.2330,6.1206,5.8536],'repairedBottomGrayStdRGB':[3.9067,3.8845,3.8713]},
 'corners':{'reviewedAtNativeScale':True,'bottomLeft':'Outermost left diagonal is retained, but inner slab edge and local texture still have a return difference.','bottomRight':'Relief and outer frame structures remain, with small local drift/tone differences. Original composite itself has a visible tone boundary; external original-source seam was never formally accepted.','noCornerAcceptancePromoted':True},
 'independentReview':{'agent':'registration_visual_audit','observed':'Warm middle face repair succeeds; main structure remains complete. Bottom hard return and texture still fail. Agree with a shifted generation window with more native bottom context; do not hide with40px deformation.'},
 'directNativeJoinAccepted':False,'localAccepted':False,'formalAccepted':False,'countsAsComplete4KTile':False,'joinedIntoCurrent':False,
 'newGenerationCallsThisRepair':1,'newGenerationCallsAcrossCandidateAndRepair':2,
 'resamplingApplied':False,'registrationApplied':False,'blendingApplied':False,'originalSourcesModified':False,
 'sourceHashesReverified':True,'allWritesConfinedTo':str(OUT),
 'nextRepairProposal':{'kind':'AI redraw with512px downward-shifted window and627px native lower context; no large warp','tileLocalLTRB':[-115,3469,1139,4723],'globalLTRB':[36749,32141,38003,33395],'bottomOriginalPieceY':[627,1254],'candidateOverlapOldPieceY':[512,1254],'preserve':'Warm middle slab and broad cross-band from this repaired candidate; redraw only unresolved lower gray slab and curve connection','status':'Proposal only; no further call made in this repair step'},
 'numericEvidence':[info(OUT/'comparison.json'),info(OUT/'face-diagnostics.json')],
}
write('visual-review.json',review)
write('result.json',{'native':info(OUT/'native.png'),'status':'warm_material_repaired_bottom_geometry_still_pending','localAccepted':False,'formalAccepted':False,'joinedIntoCurrent':False,'newGenerationCalls':1,'nativeDimensions':[1254,1254],'globalCropLTRB':[36749,31629,38003,32883],'tileLocalCropLTRB':[-115,2957,1139,4211],'newMissingPixelsAccepted':0,'complete4KTilesAdded':0,'visualReview':info(OUT/'visual-review.json'),'generationRecord':info(OUT/'native.png.generation.json'),'actualToolReceipt':info(OUT/'tool-response.json'),'comparison':info(OUT/'comparison.json'),'allWritesConfinedTo':str(OUT)})
(OUT/'README.md').write_text('''# r04_c01 local AI repair v1

One actual built-in repair completed from native-size edit context with431429 transparent repair pixels,603922 retained candidate pixels, and537165 restored original source pixels. Current source checkpoint was read and frozen at preparation: fragment current/v005, bottom current/v002. Input material was not warped.

`native.png` remains the exact1254x1254 host output, SHA256 d3f09e10ff865fdd7e4087b8b37fe5be04485a947bfa9023229a0f1842133ae2.

Warm central middle slab repair succeeds. Right middle material RGB mean difference improved from[-56.57,-45.60,-23.64] to[-0.87,-3.66,-5.65]. Broad ivory cross-band and all main contours remain present.

The native join is still rejected: bottom gray/right-ivory contour is43..46px left of original. Bottom gray mottling is reduced but remains stronger than original. Do not insert this candidate or apply40px mechanical deformation. Left/right/bottom and both bottom corners were inspected at native pixel scale. External original-source corner/seam acceptance is not implied.

Preserve this warm-material result for the next local redraw. A proposed window shifted512px downward would use tile-local[-115,3469,1139,4723], native1254 square, and627 true original bottom rows. That proposal has not been generated in this step.

Exact prompt/request, input hashes and crops, polygons and repair mask, actual tool output hint and host path, native generation record, contour and face diagnostics, QA, and visual review are saved here. Actual returned model/quality and generatedAt are null; configured batch target remains gpt-image-2.5-sunburst/max. Host observed completion is2026-10-05 19:43:11 UTC. No API, resampling, warp, global-state write or deletion was used.
''',encoding='utf-8')
write('artifact-manifest.json',{'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'files':[info(p) for p in sorted(OUT.iterdir()) if p.is_file()]})
print(json.dumps({'result':info(OUT/'result.json'),'review':info(OUT/'visual-review.json'),'native':info(OUT/'native.png')},ensure_ascii=False))
