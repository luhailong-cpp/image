from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-25-source-incremental-20261016T131854187430Z-707a552b42438c12')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(Q/'manifest.json')
findings={
'internal-y1024-segment01':'Viewed complete changed native crop. Paving and curb cross the row boundary continuously; older accepted curb repair is preserved.',
'internal-x1024-segment02':'Viewed complete changed native crop. Both prior disconnected grout runs now lead into coherent fitted intersections. No relocated dead end at the core join or patch perimeter.',
'internal-y1024-segment02':'Viewed complete changed native crop. Diagonal grout, slab face and curb entry remain continuous through the row boundary.',
'internal-x1024-segment03':'Viewed complete changed native crop. New corridor bottom branch and earlier row3 repair coexist without an offset or cut-off joint.',
'internal-y2048-segment01':'Viewed complete changed native crop. Paving joints and all relief/shadow crossings remain continuous across y2048.',
'internal-y2048-segment02':'Viewed complete changed native crop. The inherited detached red arc is gone; complete red ball cap, pole and crossbar are unchanged. Existing-source native background reselection has no visible rectangle or edge cut.',
'internal-junction-x1024-y1024':'Viewed complete changed native junction. Prior curb repair remains continuous with the updated adjacent paving.',
'internal-junction-x1024-y2048':'Viewed complete changed native junction. The diagonal joint and branch corner remain connected without an axis-aligned source cut.'
}
overlay=[]
for c in m['crops']:
 if c['name'] in findings:
  assert c['incrementalCropWritten'] and sha(c['file'])==c['sha256']
  r={'name':c['name'],'file':c['file'],'sha256':c['sha256'],'pixelKey':c['pixelKey'],'actuallyViewed':True,'status':'passed','finding':findings[c['name']]}
  overlay.append(r);c.update(r)
assert len(overlay)==8
out=Q/'changed-eight-crops-review.json';assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':overlay,'fullTileInternalQAPassed':False,'formalAccepted':False})
counts={s:sum(c['status']==s for c in m['crops']) for s in sorted({c['status'] for c in m['crops']})};assert counts=={'passed':39,'needs_repair':1}
registry=read(m['sourceRegistry']['file']);sources=registry['sources']
assert len(sources)==len({s['sha256'] for s in sources})==25
assert sum(s['ownerIndex']==10 for s in sources)==1
owner10=next(s for s in sources if s['ownerIndex']==10)
assert owner10['additionalNativeSelections'][-1]['selectedPixelCount']==1235
m.update({'baseManifest':ref(Q/'manifest.json'),'finalReviewOverlay':ref(out),'reviewStatusCounts':counts,'actuallyViewedThisBuild':True,'actuallyViewedThisBuildCount':8,'exactUnchangedCropReviewsReused':32,'wholeCandidateViewedThisBuild':False,'all40CropVerdictsAvailable':True,'geometricAuditOnly':True,'sourceLevelStyleBlocked':True,'uniqueNativeSourceCount':25,'fullTileInternalQAPassed':False,'formalAccepted':False})
full=Q/'full-audit-reviewed-status.json';write(full,m)
summary={'status':'native_25_source_candidate_saved_full_crop_audit_unpassed','candidate':m['candidate'],'sourceRegistry':m['sourceRegistry'],'pixelProof':m['pixelProof'],'reviewedAudit':ref(full),'reviewOverlay':ref(out),'sourceCount':25,'uniqueNativeSourceCount':25,'owner10RegisteredOnce':True,'existingSourceReselectionPixels':1235,'selectedCoreCount':16,'provedPixels':16777216,'newSelectionPixels':964574,'newGeneratedSourceSelectedPixels':963339,'internalCropCount':33,'northCropCount':7,'totalCropCount':40,'statusCounts':counts,'internalStatusCounts':{s:sum(c['status']==s and c['group'].startswith('internal') for c in m['crops']) for s in counts},'northStatusCounts':{s:sum(c['status']==s and c['group'].startswith('north') for c in m['crops']) for s in counts},'needsRepairCropNames':[c['name'] for c in m['crops'] if c['status']=='needs_repair'],'resolvedPreviousNeedsRepairCropNames':['internal-x1024-segment02'],'knownUnclearedStyleSources':['s04_03_fix01','s04_04_fix02'],'extraNeighborQA':m['additionalNeighbors'],'formalAccepted':False,'fullTileInternalQAPassed':False}
write(Q/'checkpoint.json',summary)
print(json.dumps({'candidate':m['candidate'],'checkpoint':ref(Q/'checkpoint.json'),'reviewedAudit':ref(full),'counts':counts,'uniqueNativeSourceCount':25,'remaining':summary['needsRepairCropNames']},ensure_ascii=False))

