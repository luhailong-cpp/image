from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(Q/'manifest.json')
findings={
'internal-x3072-segment01':'Viewed complete changed native strip. Prior rectangular curb notch is replaced with continuous beveled corner; all courtyard grout crossings below retain their previous coherent positions.',
'north-segment03':'Viewed complete native north-neighbor composite. Fixed north pixels and new lower corner connect with continuous curb face and stone joints; no open gap or broad horizontal shade band visible.',
'north-segment04':'Viewed complete native north-neighbor composite. The curb corner meets ivory trim and pavement continuously; north boundary has no contour step or strong material stripe.',
'north-junction3072':'Viewed complete native north junction. Physical curb bevel and dark face continue through central join; former mismatched endpoint is removed.'
}
overlay=[]
for c in m['crops']:
 if c['name'] in findings:
  assert c['incrementalCropWritten'] and sha(c['file'])==c['sha256']
  r={'name':c['name'],'file':c['file'],'sha256':c['sha256'],'pixelKey':c['pixelKey'],'actuallyViewed':True,'status':'passed','finding':findings[c['name']]}
  overlay.append(r);c.update(r)
assert len(overlay)==4
out=Q/'changed-four-crops-review.json';assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':overlay,'fullTileInternalQAPassed':False,'formalAccepted':False})
counts={s:sum(c['status']==s for c in m['crops']) for s in sorted({c['status'] for c in m['crops']})}
assert counts=={'passed':38,'needs_repair':2}
m.update({'baseManifest':ref(Q/'manifest.json'),'finalReviewOverlay':ref(out),'reviewStatusCounts':counts,'actuallyViewedThisBuild':True,'actuallyViewedThisBuildCount':4,'exactUnchangedCropReviewsReused':36,'wholeCandidateViewedThisBuild':False,'all40CropVerdictsAvailable':True,'geometricAuditOnly':True,'sourceLevelStyleBlocked':True,'fullTileInternalQAPassed':False,'formalAccepted':False})
full=Q/'full-audit-reviewed-status.json';write(full,m)
summary={'status':'native_24_source_candidate_saved_full_crop_audit_unpassed','candidate':m['candidate'],'sourceRegistry':m['sourceRegistry'],'pixelProof':m['pixelProof'],'reviewedAudit':ref(full),'reviewOverlay':ref(out),'sourceCount':24,'selectedCoreCount':16,'provedPixels':16777216,'newRepairPixels':173940,'fixedNorthNeighborUnchanged':m['actualNorthNeighbor'],'internalCropCount':33,'northCropCount':7,'totalCropCount':40,'statusCounts':counts,'internalStatusCounts':{s:sum(c['status']==s and c['group'].startswith('internal') for c in m['crops']) for s in counts},'northStatusCounts':{s:sum(c['status']==s and c['group'].startswith('north') for c in m['crops']) for s in counts},'needsRepairCropNames':[c['name'] for c in m['crops'] if c['status']=='needs_repair'],'resolvedPreviousNeedsRepairCropNames':['internal-x3072-segment01','north-junction3072'],'knownUnclearedStyleSources':['s04_03_fix01','s04_04_fix02'],'extraNeighborQA':m['additionalNeighbors'],'formalAccepted':False,'fullTileInternalQAPassed':False}
write(Q/'checkpoint.json',summary)
print(json.dumps({'candidate':m['candidate'],'checkpoint':ref(Q/'checkpoint.json'),'reviewedAudit':ref(full),'counts':counts,'remaining':summary['needsRepairCropNames']},ensure_ascii=False))

