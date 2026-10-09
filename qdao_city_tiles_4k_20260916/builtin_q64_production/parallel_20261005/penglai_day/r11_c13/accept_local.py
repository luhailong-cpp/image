import helper as h
from PIL import Image
import numpy as np
R=h.ROOT;p=h.p;B=R.parent;D=R/'repairs/north/joint-v3';record=p.read(D/'integration.json');idx=B/'tiles/current/current-overrides.json';current=p.read(idx)
assert current['tiles']['r10_c13']['sha256']==record['tiles']['r10_c13']['sourceSha256']
for tid,item in record['tiles'].items():
    assert p.sha(item['file'])==item['sha256'];assert p.sha(item['source'])==item['sourceSha256'];a=np.asarray(Image.open(item['file']));base=np.asarray(Image.open(item['source']));assert a.shape==(4096,4096,3)
    assert np.array_equal(a[:3469],base[:3469]) if tid=='r10_c13' else np.array_equal(a[627:],base[627:])
review={'at':p.stamp(),'reviewer':'root','scope':'local internal contours, shared north boundary and patch returns only','nativeActuallyViewed':['internal v1 six 4096px seam strips and nine junctions','internal v2 five full1254 repair composites, three horizontal seam strips and nine junctions','north joint-v1 four full1024x1254 pieces','north joint-v2 three full1254 repair composites','north joint-v3 nr3-final-native1254'],'findings':'Blue canopy stripe/rim step removed; crate upright notch repaired; water horizontal band repaired; foreground quay bevel and gray groove continuous. Local scene and native scale retained.','result':'local_candidate_visual_review_passed','formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False,'tiles':record['tiles']}
p.write(D/'visual-review.json',review)
internal=p.read(R/'repairs/internal/integration-v2.json');internal['visualReview']='root actual1254 composites, affected horizontal seams and nine junctions passed';internal['reviewedAt']=p.stamp();p.write(R/'repairs/internal/integration-v2.json',internal)
record['review']=str(D/'visual-review.json');p.write(D/'integration.json',record)
for tid,item in record['tiles'].items():current['tiles'][tid]={'file':item['file'],'sha256':item['sha256'],'status':'local_candidate_visual_review_passed','integrationRecord':str(D/'integration.json'),'visualReview':str(D/'visual-review.json')}
current['updatedAt']=p.stamp();p.write(idx,current)
h.update('local_candidate_complete_north_shared_review_passed')
p.write(R/'handoff-final.json',{'at':p.stamp(),'tile':'r11_c13','candidate':record['tiles']['r11_c13'],'northNeighbor':record['tiles']['r10_c13'],'review':str(D/'visual-review.json'),'sourceIndex':str(B/'asset-index.json'),'next':'Adjacent r11 columns12/14 and row12 candidates still absent; their future shared boundaries require native review.','formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False})
print('Accepted local native shared boundary, whole-city pending')
