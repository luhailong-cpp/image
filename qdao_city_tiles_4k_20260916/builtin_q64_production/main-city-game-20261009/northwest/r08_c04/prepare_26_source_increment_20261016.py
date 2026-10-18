from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/wood-post-style-20261016');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-25-source-incremental-20261016T131854187430Z-707a552b42438c12')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
assert sha(D/'root-review.json')=='fb0efec2e75a29048a7be0e1909ca8d831bd84666cd965b80d0c70d1b9c11438'
assert sha(Q/'root-review-overlay.json')=='a79704880b7f8b1ccf7e08358d7978413ef0e07ca8590bff92d03160ad5de91d'
p=read(D/'adoption-proposal.json')
out=Q/'wood-post-independent-local-review.json';assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':ref(D/'adoption-proposal.json'),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':p['selectedPixelCount'],'rootReview':ref(D/'root-review.json'),'crops':[dict(ref(D/(n+'.png')),actuallyViewed=True,status='passed_local_wood_style_and_perimeter') for n in ['post-full','top','left','right','bottom-edge']],'originalSilhouetteEvidence':ref(Q/'wood-before-outline.png'),'finding':'Independently viewed all five native post crops and the original contour. Cylinder silhouette, top ellipse, position and lighting are preserved. Photographic cracks and coarse grain have been replaced with smoother painted wood planes and simplified growth rings, matching the intended illustrated material. Top/left/right native mask boundaries are coherent. Adopted bottom stops exactly at tile y4096; old bottom halo is context only and no south-neighbor continuity is claimed.','passedScope':'Wood material inside the 85627-pixel mask only.','stillUnpassed':['s04_03 stone coping material','s04_04 stone material','internal-x3072-segment04 coping geometry','unverified other external boundaries'],'fullTileInternalQAPassed':False,'formalAccepted':False})
cfg={'baseManifest':str(Q/'full-audit-reviewed-status.json'),'reviewOverlays':[str(Q/'root-review-overlay.json')],'patches':[{'proposal':str(D/'adoption-proposal.json'),'independentReview':str(out)}]}
dest=T/'increment-26-source-config-20261016.json';assert not dest.exists();write(dest,cfg)
print(str(dest))

