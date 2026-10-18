from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-23-source-incremental-20261016T070108286530Z-20aa64f66666c666')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(Q/'manifest.json')
findings={
'internal-x1024-segment01':('passed','Viewed complete changed native strip. Repaired lower curb edge now crosses x1024 continuously; all existing grout crossings and curb top retain their original arrangement.'),
'internal-y1024-segment01':('passed','Viewed complete changed native strip. The repaired curb corridor and left curb joint retain continuous bevel, shadow, and outline across the row boundary.'),
'internal-x1024-segment02':('needs_repair','Viewed complete changed native strip. Curb at top is improved, but the two pre-existing paving grout paths still terminate/change phase near x160 at upper and lower crossings. These lie outside the adopted curb ROI and remain deferred after two prior failed repairs.'),
'internal-y1024-segment02':('passed','Viewed complete changed native strip. Curb edge entering upper-left and all diagonal paving grout crossings remain continuous.'),
'internal-x1024-segment03':('passed','Viewed complete changed native strip. Prior row3 repair remains intact; new lower paving extension connects without a dangling endpoint or added source-edge step.'),
'internal-x1024-segment04':('passed','Viewed complete changed native strip. Previous top dead-end near y3090 is now a continuous diagonal; the already repaired middle pair of stone corners stays coherent.'),
'internal-y3072-segment01':('passed','Viewed complete changed native strip. Diagonal paving joins and stone relief cross the row boundary continuously.'),
'internal-y3072-segment02':('passed','Viewed complete changed native strip. New paving line meets its side joint in a fitted corner; gold ornament, cloth and stitching remain unchanged. Paving approval does not claim any unrelated banner-edge defect was repaired.'),
'internal-junction-x1024-y1024':('passed','Viewed complete changed native junction. Former curb step is removed; lower front edge and bevel form one continuous diagonal through the central source join.'),
'internal-junction-x1024-y3072':('passed','Viewed complete changed native junction. Former pointed grout dead end is replaced by a complete fitted intersection; shadow and bevel remain continuous.')
}
overlay=[]
for c in m['crops']:
 if c['name'] in findings:
  assert c['incrementalCropWritten'] and sha(c['file'])==c['sha256']
  status,finding=findings[c['name']]
  r={'name':c['name'],'file':c['file'],'sha256':c['sha256'],'pixelKey':c['pixelKey'],'actuallyViewed':True,'status':status,'finding':finding}
  overlay.append(r);c.update(r)
assert len(overlay)==10
out=Q/'changed-ten-crops-review.json';assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':overlay,'fullTileInternalQAPassed':False,'formalAccepted':False})
counts={s:sum(c['status']==s for c in m['crops']) for s in sorted({c['status'] for c in m['crops']})}
assert counts=={'passed':36,'needs_repair':4}
m.update({'baseManifest':ref(Q/'manifest.json'),'finalReviewOverlay':ref(out),'reviewStatusCounts':counts,'actuallyViewedThisBuild':True,'actuallyViewedThisBuildCount':10,'exactUnchangedCropReviewsReused':30,'wholeCandidateViewedThisBuild':False,'all40CropVerdictsAvailable':True,'geometricAuditOnly':True,'sourceLevelStyleBlocked':True,'fullTileInternalQAPassed':False,'formalAccepted':False})
full=Q/'full-audit-reviewed-status.json';write(full,m)
summary={'status':'native_23_source_candidate_saved_full_crop_audit_unpassed','candidate':m['candidate'],'sourceRegistry':m['sourceRegistry'],'pixelProof':m['pixelProof'],'reviewedAudit':ref(full),'reviewOverlay':ref(out),'sourceCount':23,'selectedCoreCount':16,'provedPixels':16777216,'newRepairPixels':579323,'internalCropCount':33,'northCropCount':7,'totalCropCount':40,'statusCounts':counts,'internalStatusCounts':{s:sum(c['status']==s and c['group'].startswith('internal') for c in m['crops']) for s in counts},'northStatusCounts':{s:sum(c['status']==s and c['group'].startswith('north') for c in m['crops']) for s in counts},'needsRepairCropNames':[c['name'] for c in m['crops'] if c['status']=='needs_repair'],'resolvedPreviousNeedsRepairCropNames':['internal-x1024-segment01','internal-junction-x1024-y1024','internal-x1024-segment04','internal-junction-x1024-y3072'],'knownUnclearedStyleSources':['s04_03_fix01','s04_04_fix02'],'extraNeighborQA':m['additionalNeighbors'],'formalAccepted':False,'fullTileInternalQAPassed':False}
write(Q/'checkpoint.json',summary)
print(json.dumps({'candidate':m['candidate'],'checkpoint':ref(Q/'checkpoint.json'),'reviewedAudit':ref(full),'counts':counts,'remaining':summary['needsRepairCropNames']},ensure_ascii=False))

