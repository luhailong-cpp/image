from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-21-source-incremental-20261016T051437643050Z-4c25acc467787266')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(Q/'manifest.json')
updates={
'internal-x1024-segment04':{'status':'needs_repair','finding':'Viewed changed complete native strip. New row4 ROI fixes the middle two phase mismatches around tile y3447-3692. Separate pointed grout dead end remains at strip top around tile (1024,3090), outside adopted ROI; keep entire crop unpassed.','issueApproxCandidateLTRB':[[989,3047,1094,3137]],'localRepairEffect':'Middle two joints improved; separate pre-existing top endpoint remains.'},
'internal-x1024-segment01':{'status':'needs_repair','finding':'Reopened from prior passed status after independent junction evidence and direct reinspection. The blue-gray curb lower edge steps at tile x1024 around y984-1000, visible at the bottom of this complete strip.','issueApproxCandidateLTRB':[[989,959,1069,1029]],'reopenedFromPassed':True}
}
overlay=[]
for c in m['crops']:
 if c['name'] in updates:
  assert sha(c['file'])==c['sha256']
  rec={'name':c['name'],'file':c['file'],'sha256':c['sha256'],'pixelKey':c['pixelKey'],'actuallyViewed':True,**updates[c['name']]}
  overlay.append(rec)
  c.update(rec)
out=Q/'changed-and-reopened-crops-review.json'
assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':overlay,'additionalViewedUnchangedEvidence':['internal-junction-x1024-y3072','internal-junction-x1024-y1024'],'fullTileInternalQAPassed':False,'formalAccepted':False})
counts={s:sum(c['status']==s for c in m['crops']) for s in sorted({c['status'] for c in m['crops']})}
assert counts=={'passed':32,'needs_repair':8}
style=[ref(T/'qa/source-review'/s/'review.json') for s in ['s04_03_fix01','s04_04_fix02']]
m.update({'baseManifest':ref(Q/'manifest.json'),'finalReviewOverlay':ref(out),'reviewStatusCounts':counts,'actuallyViewedThisBuild':True,'wholeCandidateViewedThisBuild':False,'all40CropVerdictsAvailable':True,'geometricAuditOnly':True,'sourceLevelStyleBlocked':True,'unclearedStyleReviewEvidence':style,'fullTileInternalQAPassed':False,'formalAccepted':False})
full=Q/'full-audit-reviewed-status.json';write(full,m)
summary={'status':'native_21_source_candidate_saved_full_crop_audit_unpassed','candidate':m['candidate'],'sourceRegistry':m['sourceRegistry'],'pixelProof':m['pixelProof'],'reviewedAudit':ref(full),'reviewOverlay':ref(out),'sourceCount':21,'selectedCoreCount':16,'provedPixels':16777216,'internalCropCount':33,'northCropCount':7,'totalCropCount':40,'statusCounts':counts,'internalStatusCounts':{s:sum(c['status']==s and c['group'].startswith('internal') for c in m['crops']) for s in counts},'northStatusCounts':{s:sum(c['status']==s and c['group'].startswith('north') for c in m['crops']) for s in counts},'needsRepairCropNames':[c['name'] for c in m['crops'] if c['status']=='needs_repair'],'knownUnclearedStyleSources':['s04_03_fix01','s04_04_fix02'],'extraNeighborQA':m['additionalNeighbors'],'formalAccepted':False,'fullTileInternalQAPassed':False}
write(Q/'checkpoint.json',summary)
suggestions={'candidate':m['candidate'],'newIndependentProblemsNotLocallyAttemptedInCurrentRepairBatchDirectories':[
{'priority':1,'problem':'Row3/4 paving grout dead end at x1024 near y3090; separate from adopted row4 y3447-3692 repair.','affectedCrops':['internal-x1024-segment04','internal-junction-x1024-y3072'],'approxProblemCandidateLTRB':[989,3047,1094,3137],'approxProblemWorldLTRB':[13277,31719,13382,31809],'suggestedNativeFrameOriginInTile':[397,2445],'suggestedNativeWorldBox':[12685,31117,13939,32371],'attemptEvidence':'Current repair folders contain row3 joint mask ending y3004 and row4 mask y3447-3692; neither covers this y3090 junction.','instruction':'Read current 21-source candidate for edit target; previous row3 repair exists within the context. Do not reuse earlier pre-repair frame. Only adopt a verified same-world ROI.'},
{'priority':2,'problem':'Blue-gray curb lower edge step at x1024 near y990. Newly reopened native-crop evidence.','affectedCrops':['internal-x1024-segment01','internal-junction-x1024-y1024'],'approxProblemCandidateLTRB':[989,959,1069,1029],'approxProblemWorldLTRB':[13277,29631,13357,29701],'suggestedNativeFrameOriginInTile':[397,397],'suggestedNativeWorldBox':[12685,29069,13939,30323],'attemptEvidence':'No local repair-batch folder targets this curb point; historical passed source evidence is superseded by visible step.','instruction':'Preserve curb position and paving depth; repair the local lower edge only, keeping both endpoints and stone grain.'}
],'deferredDoNotRepeatNow':['row2 x1024 two joint repairs already failed twice','row4 x3072 coping geometry and coarse material had two targeted attempts'],'separateNorthCornerStillUnpassed':['internal-x3072-segment01','north-junction3072'],'formalAccepted':False}
write(Q/'remaining-repair-suggestions.json',suggestions)
print(json.dumps({'checkpoint':ref(Q/'checkpoint.json'),'reviewedAudit':ref(full),'counts':counts,'suggestions':ref(Q/'remaining-repair-suggestions.json')},ensure_ascii=False))

