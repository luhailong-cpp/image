from prepare_repair import *
D=HERE/"tone-diagnostic-separated-v2/separate-edges256"
names=["qa-north-join.png","qa-east-join.png","qa-rock-join.png","qa-north-return.png","qa-east-return.png","qa-ne-corner.png","qa-local-north-return.png","qa-local-east-return.png","proposal-native-frame.png","qa-north-wave-endpoint.png","qa-east-wave-endpoint.png"]
notes={
"qa-north-join.png":"Compared at native scale: long pure-color line reduced but shallow north cliff plane transition and wave boundary kink remain; not fully accepted.",
"qa-east-join.png":"Rectangular color edge reduced; remaining abrupt width/tangent change at wave endpoints around x1139 is geometric and is not resolved by tone.",
"qa-rock-join.png":"Rock outline and foot placement remain correct; slight horizontal material transition around y115 remains visible.",
"qa-north-return.png":"256-pixel finite return region has no new hard color cutoff or displaced contour.",
"qa-east-return.png":"256-pixel east return has no new straight cutoff or duplicated wave edge.",
"qa-ne-corner.png":"Separated estimates remove the artificial diagonal tone wedge of naive nearest-side extrapolation; residual actual joint line/curve mismatch still prevents acceptance.",
"qa-local-north-return.png":"Supplemental nearer interior check has no new straight color band.",
"qa-local-east-return.png":"Supplemental nearer east interior check has no new straight color band; inherited contour imperfections remain for separate repair.",
"proposal-native-frame.png":"Whole1254native frame actually viewed: original cliff extent retained, matte water continuity improved, no new objects. N/E endpoint deficiencies remain and production promotion is not authorized.",
"qa-north-wave-endpoint.png":"Native close crop confirms curve-shape/width behavior at north edge, not merely uniform color difference; local wave geometry needs further inspection.",
"qa-east-wave-endpoint.png":"Native close crop confirms a visible wave width/tangent step at the exact east boundary. This is a geometric mismatch; stronger tone smoothing would not fix it."}
items=[]
for n in names:
 item=dict(**ref(D/n),actuallyViewed=True,nativeScale=1,viewTool="view_image detail original",verdict="needs_repair" if n in ["qa-north-join.png","qa-east-join.png","qa-rock-join.png","qa-ne-corner.png","proposal-native-frame.png","qa-north-wave-endpoint.png","qa-east-wave-endpoint.png"] else "scoped_return_pass",review=notes[n])
 if n in ["qa-north-join.png","qa-east-join.png"]:
  old=HERE/"tone-diagnostic-separated/separate-edges256"/n
  assert sha(old)==sha(D/n)
  item["exactViewReuse"]=dict(originalViewedFile=ref(old),originalProposalSha256="79ab50f726e4d7f15330fb89af7e16f55ae78fdc1676cf53bbbb25487d0dbc45",reason="Explicit floating-point18 cap revision produced identical proposal and QA PNG bytes. These exact bytes were actually viewed from the previous diagnostic directory.",newViewClaimed=False)
 items.append(item)
diag=read(D/"diagnostic.json")
report=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),reviewer="/root/r09c14_row3_resume",proposal=ref(D/"proposal-native-frame.png"),items=items,scopedPass=False,approvedForPromotion=False,productionNativeModified=False,productionHelpersModified=False,conclusion="Local true-support tone estimation helps reduce long2-6RGB material lines but does not fix genuine water curve endpoint mismatch. Naive nearest-side sigma3 caused a diagonal corner wedge and was rejected; separate normalized finite edge estimates avoid that new wedge. Returns pass in isolation. Do not integrate or promote until remaining N/E geometry/material issues receive root review.",limitsEvidence=ref(D/"diagnostic.json"),flowNumericalTolerance="Base bounded float32 field reports6.0000004768 due floating-point rounding of6.0 cap; field is identical to baseline and not amplified.",sourceScripts=[ref(HERE/"diagnose_local_tone.py"),ref(HERE/"diagnose_separate_tone.py"),ref(HERE/"diagnose_separate_tone_v2.py")],rejectedComparisons=[dict(proposal=ref(HERE/"tone-diagnostic"/x/"proposal-native-frame.png"),actuallyViewedImages=[ref(HERE/"tone-diagnostic"/x/"qa-north-join.png")],reason="Actual native north view shows new diagonal NE corner color wedge; not accepted.",fullOtherQANotReviewed=True) for x in ["sigma3-full256","sigma3-edge96"]])
write(D/"visual-review.json",report)
write(HERE/"tone-diagnostic-result.json",dict(createdAt=datetime.now(timezone.utc).isoformat(),recommendedForRootReview=ref(D/"proposal-native-frame.png"),visualReview=ref(D/"visual-review.json"),diagnostic=ref(D/"diagnostic.json"),approvedForPromotion=False,productionInputsUnchanged=True,summary=report["conclusion"]))
status=read(HERE/"current-status.json");status.update(updatedAt=datetime.now(timezone.utc).isoformat(),latestDiagnostic=ref(D/"proposal-native-frame.png"),diagnosticResult=ref(HERE/"tone-diagnostic-result.json"),method="Paused further AI repetition; completed root-authorized isolated tone estimation comparison. Awaiting root inspection, no production integration.",approvedForPromotion=False);write(HERE/"current-status.json",status)
for q in ["native_patch.py","native_assemble.py"]:
 print(q,sha(ROOT/q))
print(json.dumps(dict(proposal=diag["proposal"],diagnostic=str(D/"diagnostic.json"),review=str(D/"visual-review.json"),scriptSHA=diag["script"]["sha256"],maxFlow=diag["actualMaxFlow"],maxTone=diag["actualMaxTone"],northToneClipped=diag["separateEdgeSupportStatistics"][0]["rawClippedSupportFraction"],eastToneClipped=diag["separateEdgeSupportStatistics"][1]["rawClippedSupportFraction"],jacobian=diag["jacobianMinimum"],nativeStillUnchanged=sha(TILE/"native/p14.png")==diag["nativeUnchanged"]["sha256"])))

