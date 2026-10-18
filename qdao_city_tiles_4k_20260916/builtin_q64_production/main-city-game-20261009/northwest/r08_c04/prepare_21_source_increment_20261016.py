from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row4-x1024-cross-20261013');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-20-source-incremental-20261016T042147210339Z-9697cfee143fd953')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=read(D/'adoption-proposal.json')
cr=[dict(ref(D/(n+'.png')),actuallyViewed=True,status='passed_local_geometry_and_perimeter') for n in ['detail','north','south','west','east']]
out=Q/'row4-native-local-review.json'
assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':ref(D/'adoption-proposal.json'),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':p['selectedPixelCount'],'rootReview':ref(D/'root-local-review.json'),'crops':cr,'finding':'Independently viewed complete detail and all four perimeter crops. Upper dangling joint closes into the stone corner; lower junction and crossing relief/shadows remain continuous. This local ROI does not cover the separate row3/4 junction around tile y3090.','fullTileInternalQAPassed':False,'formalAccepted':False})
mixed=T.parent/'r06_c03/independent-reviews/r08_c04-20261016/mixed-source-crops-review.json'
assert sha(mixed)=='827e0bd804b6f7b978fa5d96e864df804385f67ed057ef05d6c9a81a8e96d9b7'
data=read(mixed);assert all(c['actuallyViewed'] for c in data['crops'])
normalized=Q/'independent-mixed-review-overlay.json'
assert not normalized.exists()
data.update({'actuallyViewed':True,'originalReview':ref(mixed),'normalizationOnly':'Added top-level actuallyViewed from all 15 individually viewed crop records; no verdict changed.'})
write(normalized,data)
config={'baseManifest':str(Q/'manifest.json'),'reviewOverlays':[str(Q/'combined-nine-crops-review.json'),str(normalized)],'patches':[{'proposal':str(D/'adoption-proposal.json'),'independentReview':str(out)}]}
configfile=T/'increment-21-source-config-20261016.json';assert not configfile.exists()
write(configfile,config)
print(json.dumps({'config':str(configfile),'independentRow4Review':ref(out)}))

