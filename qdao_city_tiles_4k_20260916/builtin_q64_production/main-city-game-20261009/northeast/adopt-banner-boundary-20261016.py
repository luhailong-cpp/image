from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;T=Z/'r02_c14';Q=T/'qa/banner-boundary-20261016'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
composition=read(Q/'composition-v7.json');review=read(T/'qa/local-repair-20261013/internal-review-v6.json')
review.update({'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':composition['candidate'],'candidateSha256':composition['candidateSha256'],'composition':str(Q/'composition-v7.json'),'priorFullReview':str(T/'qa/local-repair-20261013/internal-review-v6.json'),'status':'best_complete_candidate_banner_geometry_corrected_boundaries_pending','selectionReason':'Wide banner geometry restored from north native source; wrong old narrow terminus removed. New lower strip boundary and orphaned old shadow remain unpassed.','newReviewedWindows':[str(Q/'north-banner-join-v7.png'),str(Q/'new-strip-left-right-bottom-v7.png'),str(Q/'prior-strip-left-right-bottom-v6.png')]})
review['p2Issues'].append({'id':'banner-halo-bottom-boundary','detail':'At y115 of r02_c14, an orphaned triangular old banner shadow and straight willow material step remain after native halo replacement; geometry now wide swallowtail.','nativeEditAttempts':0,'status':'pending'})
save(Q/'internal-review-v7.json',review)
tp=read(T/'tile-progress.json');tp.update({'candidate':composition['candidate'],'candidateSha256':composition['candidateSha256'],'fullInternalReview':str(Q/'internal-review-v7.json'),'updatedAt':datetime.now(timezone.utc).isoformat(),'status':review['status']});tp['pendingRepairs'].append('banner-halo-bottom-boundary');save(T/'tile-progress.json',tp)
src=Z/'r01_c14/native/p42-v20261016.png';si=Image.open(src).convert('RGB');bi=Image.open(composition['candidate']).convert('RGB')
context=Image.new('RGB',(1254,1254));context.paste(si.crop((0,512,1254,1139)),(0,0));context.paste(bi.crop((909,0,2163,627)),(0,627));out=Q/'banner-boundary-repair-context-v1.png';assert not out.exists();context.save(out)
save(Q/'banner-boundary-context-sources-v1.json',{'northNative':str(src),'northNativeSha256':sha(src),'southCandidate':composition['candidate'],'southCandidateSha256':composition['candidateSha256'],'localOrigin':[909,-627],'tileBoundaryY':627,'materialStepY':742,'context':str(out),'contextSha256':sha(out),'operation':'integer native crops only'})
print(str(out))

