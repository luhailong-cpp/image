from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016');Q=T/'qa/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
root=read(D/'root-review-v2.json');assert root['actuallyViewed'] and root['status']=='passed_local_native_adoption'
assert sha(D/'root-review-v2.json')=='08231ec75da0df52f33b32b3dc61c0972eb341b03cb8e5f954b151678fcd4c5b'
for name,proposalfile in [('row2',D/'adoption-proposal.json'),('redarc',D/'red-arc-existing-source-proposal-v2.json')]:
 p=read(proposalfile)
 if name=='redarc':
  old=read(D/'red-arc-existing-source-proposal.json')
  for k in ['source','sourceSha256','sourceWorldBox','sourceOriginInTile','sameWorldNativeROI','targetTileROI','mask','maskSha256','selectedPixelCount','existingOwnerIndex']:assert p[k]==old[k]
 dest=Q/(name+'-root-review-normalized.json');assert not dest.exists()
 write(dest,{'reviewer':'/root','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':ref(proposalfile),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':p['selectedPixelCount'],'rootReview':ref(D/'root-review-v2.json'),'normalizationOnly':'Root independently approved exact same pixels. Redarc v2 adds baseline hash only; all source, mask, coordinates and pixel count match approved proposal.','formalAccepted':False})
config={'baseManifest':str(Q/'full-audit-reviewed-status.json'),'patches':[{'proposal':str(D/'adoption-proposal.json'),'independentReview':str(Q/'row2-root-review-normalized.json')}],'existingSourcePatches':[{'proposal':str(D/'red-arc-existing-source-proposal-v2.json'),'independentReview':str(Q/'redarc-root-review-normalized.json')}]}
dest=T/'increment-25-source-config-20261016.json';assert not dest.exists();write(dest,config)
print(str(dest))

