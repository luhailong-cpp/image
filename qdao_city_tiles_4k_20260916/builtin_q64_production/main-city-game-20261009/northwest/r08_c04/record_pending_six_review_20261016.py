from pathlib import Path
import json,hashlib
Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-20-source-incremental-20261016T042147210339Z-9697cfee143fd953')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
m=read(Q/'manifest.json')
findings={
'internal-y1024-segment02':'Viewed the complete native 1024x320 crop. Blue curb and three paving grout crossings remain coherent across the row boundary; no row-aligned cut or displaced joint found.',
'internal-y1024-segment03':'Viewed the complete native 1024x320 crop. The long diagonal grout and fitted corners cross the row boundary continuously; stone face texture has no hard horizontal cut.',
'internal-y2048-segment02':'Viewed the complete native 1024x320 crop. Red pole, adjoining paving, and foreground crossbar remain continuous; no missing or shifted post/stone outline.',
'internal-y2048-segment03':'Viewed the complete native 1024x320 crop. Diagonal paving grout maintains direction through row boundary; crossbar end and background remain coherent.',
'internal-junction-x2048-y1024':'Viewed native 320x320 four-core junction. Continuous stone-face mottling and corner grout; no quadrant edge visible.',
'internal-junction-x2048-y2048':'Viewed native 320x320 four-core junction. Red hardware and paving remain continuous with no quadrant shift or abrupt material boundary.'
}
crops=[]
for c in m['crops']:
 if c['name'] in findings:
  assert c['status']=='pending'
  assert sha(c['file'])==c['sha256']
  crops.append({'name':c['name'],'file':c['file'],'sha256':c['sha256'],'pixelKey':c['pixelKey'],'actuallyViewed':True,'status':'passed','finding':findings[c['name']]})
assert len(crops)==6
out=Q/'six-pending-crops-visual-review.json';assert not out.exists()
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':crops,'fullTileInternalQAPassed':False,'formalAccepted':False})
combined=read(Q/'changed-crops-visual-review.json')['crops']+crops
write(Q/'combined-nine-crops-review.json',{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'candidate':m['candidate'],'manifest':ref(Q/'manifest.json'),'crops':combined,'underlyingReviews':[ref(Q/'changed-crops-visual-review.json'),ref(out)],'fullTileInternalQAPassed':False,'formalAccepted':False})
cp=read(Q/'checkpoint.json');cp.update({'statusCountsWithOverlay':{'passed':23,'needs_repair':2,'unpassed_source_issue_without_crop_verdict':15},'remainingPendingCropNames':[],'reviewOverlay':ref(Q/'combined-nine-crops-review.json')})
write(Q/'checkpoint-after-nine-reviewed.json',cp)
print(json.dumps({'review':ref(Q/'combined-nine-crops-review.json'),'counts':cp['statusCountsWithOverlay']},ensure_ascii=False))

