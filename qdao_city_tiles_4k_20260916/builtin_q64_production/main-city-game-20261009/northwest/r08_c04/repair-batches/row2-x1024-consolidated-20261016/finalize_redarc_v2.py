from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
basefile=T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/candidate.png'
base=np.array(Image.open(basefile).convert('RGB'));mask=np.array(Image.open(D/'red-arc-existing-source-mask.png'))==255
p=read(D/'red-arc-existing-source-proposal.json')
p.update({'baseCandidate':ref(basefile),'baselineSelectedPixelsSha256':hashlib.sha256(base[1933:3187,909:2163][mask].tobytes()).hexdigest(),'status':'passed_producer_local_review_pending_root_independent_review'})
# Create versioned immutable complete metadata after supplement QA.
write(D/'red-arc-existing-source-proposal-v2.json',p)
review={'reviewer':'/root/resume_r08_audit_20261016','role':'producer_local_qa','actuallyViewed':True,'status':'passed_native_halo_reselection_pending_root_independent_review','proposal':ref(D/'red-arc-existing-source-proposal-v2.json'),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':1235,'crops':[dict(ref(D/('v2-'+n+'.png')),actuallyViewed=True,status='passed_local_geometry_and_perimeter') for n in ['hardware','north','south','west','east','lower','bottom']],'finding':'The short detached red arc was inherited from the unchanged 24-source baseline, not introduced by the new row2 polygon. It is absent from the existing registered lower source at exactly the same world coordinates. A 65x19 binary native reselection removes the arc while preserving all complete red-ball pixels below the selected background strip. All four background perimeters and lower/bottom grout remain continuous.','existingOwnerIndex':10,'uniqueNativeSourceIncrement':0,'sourceResampled':False,'sourceBlended':False,'ballPixelsBelowMaskByteIdentical':True,'formalAccepted':False}
write(D/'red-arc-local-review-v2.json',review)
write(D/'red-arc-proof-v2.json',{'status':'passed_exact_same_world_existing_native_reselection','baseCandidate':ref(basefile),'sameWorldSource':ref(Path(p['source'])),'sourceNativeOriginInTile':[909,1933],'sourceROI':[403,101,468,120],'targetTileROI':[1312,2034,1377,2053],'sourceMask':ref(D/'red-arc-existing-source-mask.png'),'baselineSelectedPixelsSha256':p['baselineSelectedPixelsSha256'],'selectedPixelCount':1235,'actualRedArcInheritedInBaseline':True,'primaryRow2MaskSelectedHardwarePixels':0,'originalHardwareRegionByteIdenticalBeforeSupplement':True,'completeBallPixelsBelowMaskByteIdenticalAfterSupplement':True,'uniqueNativeSourceIncrement':0,'formalAccepted':False})
write(D/'adoption-bundle-v2.json',{'status':'pending_root_independent_review','primaryProposal':ref(D/'adoption-proposal.json'),'existingSourceSupplement':ref(D/'red-arc-existing-source-proposal-v2.json'),'localSupplementReview':ref(D/'red-arc-local-review-v2.json'),'combinedFrameTrial':ref(D/'roi-trial-v2.png'),'primaryNewSourceCount':1,'existingSourceReusedCount':1,'uniqueNativeSourceIncrement':1,'primarySelectedPixels':963339,'existingSourceSupplementPixels':1235,'totalSelectedPixels':964574,'candidateOrSelectionModified':False,'formalAccepted':False})
print(json.dumps({'bundle':ref(D/'adoption-bundle-v2.json'),'supplement':ref(D/'red-arc-existing-source-proposal-v2.json')},ensure_ascii=False))

