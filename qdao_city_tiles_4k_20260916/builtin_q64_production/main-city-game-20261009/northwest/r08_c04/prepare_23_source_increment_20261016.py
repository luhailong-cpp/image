from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/paving-x1024-y3090-20261016');C=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/curb-x1024-y990-20261016')
Q=T/'qa/native-21-source-incremental-20261016T051437643050Z-4c25acc467787266'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=read(D/'adoption-proposal.json');out=Q/'paving3090-independent-local-review.json';assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':ref(D/'adoption-proposal.json'),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':p['selectedPixelCount'],'rootReview':ref(D/'root-local-review.json'),'crops':[dict(ref(D/(n+'.png')),actuallyViewed=True,status='passed_local_geometry_and_perimeter') for n in ['detail','north','south','west','east']],'finding':'Complete local detail and all four perimeter crops independently viewed. Previously dead-ending main grout is extended into a fitted corner; the two subordinate joints remain aligned. No new step at mask boundaries. Existing red-banner silhouette transition is outside this native mask and is not cleared by this paving-only approval.','fullTileInternalQAPassed':False,'formalAccepted':False})
p=read(C/'adoption-proposal-v2.json');root=read(C/'root-independent-local-review.json')
assert root['actuallyViewed'] and root['status']=='approved_local_roi_adoption'
assert root['sourceSHA256']==p['sourceSha256'] and root['selectedPixels']==p['selectedPixelCount']
curb_review=Q/'curb990-root-approval-normalized.json';assert not curb_review.exists()
write(curb_review,{'reviewer':'/root','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':ref(C/'adoption-proposal-v2.json'),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':p['selectedPixelCount'],'rootReview':ref(C/'root-independent-local-review.json'),'normalizationOnly':'Schema adapter of root independent approval; no visual verdict added or changed.','finding':root['finding'],'fullTileInternalQAPassed':False,'formalAccepted':False})
config={'baseManifest':str(Q/'full-audit-reviewed-status.json'),'patches':[
{'proposal':str(C/'adoption-proposal-v2.json'),'independentReview':str(curb_review)},
{'proposal':str(D/'adoption-proposal.json'),'independentReview':str(out)}
]}
dest=T/'increment-23-source-config-20261016.json';assert not dest.exists()
write(dest,config);print(str(dest))

