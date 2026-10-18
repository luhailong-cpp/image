from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');Q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-26-source-incremental-20261016T151921117369Z-8cf9a2f4d2262fd8');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/wood-post-style-20261016')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(Q/'manifest.json');im=Image.open(m['candidate']['file']).convert('RGB')
assert m['changedCropNames']==[] and m['unchangedCropFilesReused']==40
validated=[]
boxes={'post-full':[230,790,610,1139],'top':[240,800,590,950],'left':[240,820,320,1139],'right':[520,820,595,1139],'bottom-edge':[240,1105,595,1139]}
for name,box in boxes.items():
 target=[box[0]+2140,box[1]+2957,box[2]+2140,box[3]+2957]
 pic=im.crop(target);prior=Image.open(D/(name+'.png')).convert('RGB')
 assert np.array_equal(np.array(pic),np.array(prior)),name
 validated.append({'name':name,'candidateLTRB':target,'reviewedCrop':ref(D/(name+'.png')),'savedCandidatePixelsExactlyMatchViewedCrop':True,'noResample':True})
write(Q/'wood-interior-saved-candidate-check.json',{'candidate':m['candidate'],'status':'passed_saved_candidate_matches_all_five_independently_viewed_native_post_crops','crops':validated,'localReview':ref(T/'qa/native-25-source-incremental-20261016T131854187430Z-707a552b42438c12/wood-post-independent-local-review.json'),'woodMaterialScopePassed':True,'southNeighborNotVerified':True,'fullTileInternalQAPassed':False,'formalAccepted':False})
reg=read(m['sourceRegistry']['file']);assert len(reg['sources'])==len({r['sha256'] for r in reg['sources']})==26
assert sum(r['ownerIndex']==10 for r in reg['sources'])==1
assert m['reviewStatusCounts']=={'needs_repair':1,'passed':39}
m.update({'baseManifest':ref(Q/'manifest.json'),'actuallyViewedThisBuild':False,'actuallyViewedThisBuildCount':0,'exactUnchangedCropReviewsReused':40,'localMaterialReviewCropCount':5,'localMaterialSavedCandidateVerification':ref(Q/'wood-interior-saved-candidate-check.json'),'wholeCandidateViewedThisBuild':False,'all40CropVerdictsAvailable':True,'sourceLevelStyleBlocked':True,'resolvedLocalStyleScopes':[{'source':'s04_03_fix01','scope':'Wood cylinder material only','approvedNativeMaskPixels':85627,'review':ref(T/'qa/native-25-source-incremental-20261016T131854187430Z-707a552b42438c12/wood-post-independent-local-review.json')}],'remainingStyleScopes':['s04_03 stone coping material','s04_04 stone material'],'uniqueNativeSourceCount':26,'fullTileInternalQAPassed':False,'formalAccepted':False})
full=Q/'full-audit-reviewed-status.json';write(full,m)
summary={'status':'native_26_source_candidate_saved_wood_local_style_passed_whole_tile_unpassed','candidate':m['candidate'],'sourceRegistry':m['sourceRegistry'],'pixelProof':m['pixelProof'],'reviewedAudit':ref(full),'sourceCount':26,'uniqueNativeSourceCount':26,'owner10RegisteredOnce':True,'selectedCoreCount':16,'provedPixels':16777216,'newWoodNativePixels':85627,'internalCropCount':33,'northCropCount':7,'totalCropCount':40,'statusCounts':{'passed':39,'needs_repair':1},'internalStatusCounts':{'passed':32,'needs_repair':1},'northStatusCounts':{'passed':7,'needs_repair':0},'changedSeamQACrops':0,'exactUnchangedCropReviewsReused':40,'needsRepairCropNames':['internal-x3072-segment04'],'resolvedLocalStyleScopes':['Wood cylinder material only'],'remainingStyleScopes':['s04_03 stone coping material','s04_04 stone material'],'localWoodSavedCandidateCheck':ref(Q/'wood-interior-saved-candidate-check.json'),'extraNeighborQA':m['additionalNeighbors'],'formalAccepted':False,'fullTileInternalQAPassed':False}
write(Q/'checkpoint.json',summary)
print(json.dumps({'candidate':m['candidate'],'checkpoint':ref(Q/'checkpoint.json'),'reviewedAudit':ref(full),'counts':summary['statusCounts'],'uniqueNativeSourceCount':26,'woodCropPixelMatchCount':5},ensure_ascii=False))

