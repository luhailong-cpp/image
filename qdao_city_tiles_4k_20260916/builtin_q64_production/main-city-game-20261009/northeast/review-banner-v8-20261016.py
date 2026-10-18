from pathlib import Path
import json
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;T=Z/'r02_c14';Q=T/'qa/banner-boundary-20261016'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(Q/'composition-v8.json');r=read(Q/'internal-review-v7.json')
r.update({'candidate':m['candidate'],'candidateSha256':m['candidateSha256'],'composition':str(Q/'composition-v8.json'),'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'newReviewedWindows':[str(Q/('v8-'+x+'.png')) for x in ['north-join','bottom','left','right']],'nativeRepairCount':9,'selectionReason':'First local AI edit removed orphaned triangular shadow and main willow cutoff. Lower and left crop-border texture differences remain pending; best geometry retained.','status':'best_complete_candidate_local_boundary_repairs_pending'})
for i in r['p2Issues']:
 if i['id']=='banner-halo-bottom-boundary':i.update({'detail':'Original orphaned shadow and main willow cut resolved. Residual material boundary at x941 and y583 of new repair, weaker right leaf step near x2131.','nativeEditAttempts':1,'status':'pending'})
r['resolvedFindings'].append('Wide swallowtail north banner and old orphaned triangular shadow corrected; north join silhouette continuous.')
save(Q/'internal-review-v8.json',r)
p=read(T/'tile-progress.json');p.update({'candidate':m['candidate'],'candidateSha256':m['candidateSha256'],'fullInternalReview':str(Q/'internal-review-v8.json'),'updatedAt':datetime.now(timezone.utc).isoformat(),'status':r['status'],'inflightGeneration':None});save(T/'tile-progress.json',p)
q=Z/'r01_c14/qa/quick-20261016/row1-and-banner-review.json'
save(q,{'tile':'r01_c14','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'patches':['p11-v20261016.png','p14-v20261016.png','p42-v20261016.png'],'windows':['qa/quick-native-joins/0c2cf7977c36eb6c/p11-p21.png','qa/quick-native-joins/331c0795c09548fa/p14-p24.png','qa/quick-native-joins/aaf18894e8bd9fcf/p41-p42.png'],'findings':['Top rows contain original native foliage and stone detail; no black padding inside core.','Coping geometry coherent with south; faint material transition retained for full QA.','Wide swallowtail matches approved banner geometry. West stone joint slightly shifts around y500; assess full tile.','South neighbor adopted corrected native halo and AI repair as candidate v8; residual repair boundary remains pending.'],'internalPassed4kCount':0,'formalAcceptedCount':0})
print('Adopted v8 as unpassed best; recorded quick checks')

