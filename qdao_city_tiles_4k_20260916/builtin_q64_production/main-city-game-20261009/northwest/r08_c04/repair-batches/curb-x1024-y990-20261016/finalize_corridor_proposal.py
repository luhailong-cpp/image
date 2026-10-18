from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/curb-x1024-y990-20261016');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
base=np.array(Image.open(D/'edit-target.png').convert('RGB'));raw=np.array(Image.open(D/'native.png').convert('RGB'));trial=np.array(Image.open(D/'roi-trial-v2.png').convert('RGB'));mask=np.array(Image.open(D/'selection-mask-v2.png'))
assert set(np.unique(mask))=={0,255}
selected=mask==255
assert np.array_equal(trial[~selected],base[~selected])
assert np.array_equal(trial[selected],raw[selected])
assert int(selected.sum())==204423
proposal={'status':'passed_producer_local_review_pending_root_independent_review','source':str(D/'native.png'),'sourceSha256':sha(D/'native.png'),'sourceWorldBox':[12685,29069,13939,30323],'sourceOriginInTile':[397,397],'sameWorldNativeROI':[0,210,1254,1021],'targetTileROI':[397,607,1651,1418],'mask':str(D/'selection-mask-v2.png'),'maskSha256':sha(D/'selection-mask-v2.png'),'maskMode':'L binary 0/255 polygon; no feathering','maskPolygonXY':[[0,850],[1253,210],[1253,365],[0,1020]],'selectedPixelCount':204423,'resampled':False,'blended':False,'outsideMaskPixelIdentical':True,'insideMaskNativePixelIdentical':True,'trial':str(D/'roi-trial-v2.png'),'trialSha256':sha(D/'roi-trial-v2.png'),'formalAccepted':False}
write(D/'adoption-proposal-v2.json',proposal)
names=['v2-left-exterior','v2-right-exterior','v2-mid-upper','v2-mid-lower','v2-mid-context','v2-full-context']
review={'reviewer':'/root/resume_r08_audit_20261016','role':'producer_local_qa','actuallyViewed':True,'status':'passed_local_geometry_and_perimeter_pending_root_independent_review','proposal':ref(D/'adoption-proposal-v2.json'),'sourceSha256':proposal['sourceSha256'],'maskSha256':proposal['maskSha256'],'pixelCount':204423,'crops':[dict(ref(D/(n+'.png')),actuallyViewed=True,status='passed_local_geometry_and_perimeter') for n in names],'finding':'Curb lower edge and thin bevel now continue along one diagonal without the former central vertical step. Extended native corridor connects to original fixed endpoint geometry; both exterior frame boundaries were rendered with actual 21-source candidate context and inspected. Upper/lower corridor transitions and full native context retain continuous material with no new clipped outline. Only binary-mask pixels are proposed; unrelated old paving mismatch outside mask remains.','rejectedMask':'selection-mask-v1.png: narrow rectangle creates a new left-edge step; never adopt v1.','fullTileInternalQAPassed':False,'formalAccepted':False}
write(D/'local-visual-review.json',review)
write(D/'pixel-proof.json',{'status':'passed_exact_same_world_binary_mask_pixels','source':ref(D/'native.png'),'base':ref(D/'edit-target.png'),'trial':ref(D/'roi-trial-v2.png'),'mask':ref(D/'selection-mask-v2.png'),'selectedPixels':204423,'changedPixels':int(np.any(trial!=base,axis=2).sum()),'outsideMaskUnchanged':True,'insideMaskSourceIdentical':True,'resampled':False,'blended':False,'formalAccepted':False})
write(D/'handoff.json',{'status':'one_generation_native_repair_ready_for_root_independent_review','proposal':ref(D/'adoption-proposal-v2.json'),'localReview':ref(D/'local-visual-review.json'),'proof':ref(D/'pixel-proof.json'),'actualModel':None,'entry':'image_gen__imagegen existing built-in','generationAttempts':1,'candidateOrSelectionModified':False,'requiresIndependentReview':True,'formalAccepted':False})
print(json.dumps({'proposal':ref(D/'adoption-proposal-v2.json'),'review':ref(D/'local-visual-review.json'),'sourceSha256':proposal['sourceSha256'],'pixels':204423},ensure_ascii=False))

