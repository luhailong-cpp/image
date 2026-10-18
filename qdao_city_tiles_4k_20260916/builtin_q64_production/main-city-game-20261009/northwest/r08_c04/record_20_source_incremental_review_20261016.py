from pathlib import Path
import json,hashlib
Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-20-source-incremental-20261016T042147210339Z-9697cfee143fd953')
R=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
m=R(Q/'manifest.json')
findings={
'internal-x1024-segment03':'Viewed native 320x1024 crop: the repaired diagonal joint now crosses the core seam without a step; both other grout crossings remain aligned. Broader existing stone-face pattern is retained; this verdict does not approve whole-tile style or the separate bottom-right railing.',
'internal-y3072-segment01':'Viewed native 1024x320 crop: lower corridor endpoint and all grout crossings remain continuous across the row seam; no new clipped edge or rectangular patch boundary seen.',
'internal-x3072-segment02':'Viewed native 320x1024 crop: former dangling grout now joins at a fitted corner, with continuous bevel/shadow across the core seam and no new clipped branch.'
}
crops=[]
for c in m['crops']:
 if c['name'] in findings:
  assert c['incrementalCropWritten']
  crops.append({'name':c['name'],'file':c['file'],'sha256':c['sha256'],'pixelKey':c['pixelKey'],'actuallyViewed':True,'status':'passed','finding':findings[c['name']]})
review={'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'scope':'Only three changed full audit crops; unchanged crops reuse prior evidence','candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':crops,'fullTileInternalQAPassed':False,'formalAccepted':False}
out=Q/'changed-crops-visual-review.json'
assert not out.exists()
out.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
counts=dict(m['reviewStatusCounts']);counts['pending']-=3;counts['passed']+=3
checkpoint={'status':'native_20_source_candidate_saved_partial_qa_not_accepted','candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'reviewOverlay':ref(out),'sourceCount':20,'selectedCoreCount':16,'provedPixels':16777216,'fullAuditCropCount':40,'statusCountsWithOverlay':counts,'remainingMixedSourceCropNames':[c['name'] for c in m['crops'] if c['status']=='unpassed_source_issue_without_crop_verdict'],'remainingPendingCropNames':[c['name'] for c in m['crops'] if c['status']=='pending' and c['name'] not in findings],'fullTileInternalQAPassed':False,'formalAccepted':False}
(Q/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checkpoint,ensure_ascii=False))

