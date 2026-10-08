from prepare_repair import *
d=HERE/"geometry-combined-v1";proposal=ref(d/"proposal-p14.png");meta=read(d/"proposal.json")
items=[]
comments={
"proposal-p14.png":("pending","Combined frame preserves the approved east geometry repair and uses disjoint north wave/rock repairs. Overall approval pending because a fine horizontal contact remains discernible near the upper-right y115 boundary."),
"qa-north-join.png":("pending","North wave endpoint and local rock plane improved; upper-right horizontal contact around y115 still needs root judgement/repair."),
"qa-east-join.png":("pending","East local wave geometry and return are continuous; top NE old source contact remains visible."),
"qa-ne-corner.png":("pending","Straight y115 tone/material contact remains discernible across the current quadrant and extends into immutable NE/E support; source-only strip supplied, not claimed as an excuse for current-side pixels."),
"qa-rock-join.png":("pass_local","Rock silhouette and pale corner highlight are connected; broad face has no conspicuous rectangular fill or new horizontal ledge. Local sigma1 tone uses actual north only, within18."),
"qa-north-wave-endpoint.png":("pass_local","Original thin detached dark/cyan fragment at y115 is healed into one broad clean curve; current north-wave-v2 only, not its rejected rock."),
"qa-north-return.png":("pass_local","No new horizontal color step or doubled shoreline at the finite north return."),
"qa-east-return.png":("pass_local","No straight vertical return line or waveform discontinuity in current reviewed return strip."),
"qa-east-wave-endpoint.png":("pass_local","True east wave width and tangent connect smoothly through current-side repaired geometry; root also explicitly viewed and passed source local proposal."),
"qa-east-local-return.png":("pass_local","No rectangular return edge or hard outline double from local AI composition."),
"qa-rock-local-return.png":("pass_local","Original rock planes remain coherent at lower/right local return; no cutout boundary."),
"qa-north-wave-local-return.png":("pass_local","Blue cell surface blends back without a rectangular edit boundary."),
"qa-old-y742.png":("pass_local","Old y742 shifted-canvas return line remains healed; no horizontal join visible."),
"qa-old-ne-e-only.png":("observed_frozen_support","Exactly the 115-pixel real NE/E strip, no current tile pixels. Existing source transition visible at y115; recorded for correct boundary ownership, neighbors unchanged.")
}
for name,(verdict,review) in comments.items():items.append(dict(**ref(d/name),actuallyViewed=True,nativeScale=1,verdict=verdict,review=review))
metrics=[]
for part in meta["parts"]:
 folder=Path(part["source"]["file"]).parent
 flow=np.load(folder/"flow.npy");tone=np.load(folder/"tone.npy");alpha=np.load(folder/"alpha.npy")
 x0,y0,x1,y1=part["cropLTRB"];sel=np.zeros((1254,1254),bool);sel[y0:y1,x0:x1]=alpha[y0:y1,x0:x1]>0
 dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv
 metrics.append(dict(role=part["role"],actualMaxFlowInSelectedPixels=float(np.linalg.norm(flow[sel],axis=1).max()),actualMaxToneInSelectedPixels=float(np.abs(tone[sel]).max()),jacobianMinimumInSelectedPixels=float(jac[sel].min()),selectedPixels=int(sel.sum()),fieldFiles=[ref(folder/"flow.npy"),ref(folder/"tone.npy"),ref(folder/"alpha.npy")]))
write(d/"visual-review.json",dict(candidate=proposal,reviewedAt=datetime.now(timezone.utc).isoformat(),items=items,scopedPass=False,approvedForPromotion=False,issueCount=1,issues=[dict(area="upper-right north contact and NE junction",coordinate="native y115, approximately x780..1139 in current side; real support x1139..1254 separately recorded",review="Fine straight horizontal contact remains discernible; whole-frame approval withheld pending root review. Local wave/rock and old y742 return checks are recorded independently.")],selectedRegionMetrics=metrics,sourceProductionNativeUnchanged=sha(TILE/"native/p14.png")=="e5029514592962bfbf3e5a565ac2a9d0de37d91e4f9bc7986fc2354ed5d5f9f3",sourceNeighborsUnchanged=True,productionRecheckIdentical=meta["productionRecheck"]["pixelIdentical"]))
write(d/"root-east-local-authorization.json",dict(receivedAt=datetime.now(timezone.utc).isoformat(),authority="parent /root",exactMessage="Root 已实际看 geometry-east-v3/bounded/qa-east-endpoint.png 和 qa-local-return.png，局部波线衔接与回归通过。保留这一东侧修补，继续北侧局部修补；整张 p14 需合成后重新核验 N/E/NE、回归区及 y742 等旧问题，无整体批准。",sourceCandidate=ref(HERE/"geometry-east-v3/bounded/proposal-p14.png"),localOnly=True,wholeFrameApproved=False))
for folder,reviewed,reason in [
("geometry-east-v1/bounded-v2",["qa-east-endpoint.png","qa-local-return.png"],"Wave width step at actual E remains; failed."),
("geometry-east-v2/bounded",["qa-east-endpoint.png","qa-local-return.png"],"Cross-boundary inpaint reorganized cells and cannot match immutable E within6; failed."),
("geometry-north-v1/bounded",["qa-north-wave.png","qa-rock-join.png","qa-rock-return.png","qa-wave-return.png","qa-north-whole.png"],"North thin detached stroke remains; only later sigma1 rock subset considered."),
("geometry-north-v2/bounded",["qa-north-wave.png","qa-rock-join.png","qa-north-whole.png","qa-rock-return.png","qa-wave-return.png"],"North wave local subset improved and selected. Rock has visible bright block and outline shift at y115, rejected; full proposal not passed.")]:
 f=HERE/folder;write(f/"visual-review.json",dict(candidate=ref(f/"proposal-p14.png"),items=[dict(**ref(f/n),actuallyViewed=True,nativeScale=1,verdict="fail_full_proposal",review=reason) for n in reviewed],scopedPass=False,approvedForPromotion=False))
write(HERE/"geometry-local-result.json",dict(currentProposal=proposal,review=ref(d/"visual-review.json"),threeDisjointLocalAIProposals=meta["parts"],selectedRegionMetrics=metrics,pending="Root review of north rock/wave and remaining upper-right north contact. Native unmodified; no downstream NE generation released.",approvedForPromotion=False))
print(json.dumps(dict(proposal=proposal,metrics=metrics,report=ref(d/"visual-review.json"))))

