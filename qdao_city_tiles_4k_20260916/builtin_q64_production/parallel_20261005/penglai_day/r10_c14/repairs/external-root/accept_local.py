from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
D=R/'joint-v5';rec=p.read(D/'integration.json')
review={'createdAt':p.stamp(),'reviewer':'root','status':'local_internal_shared_edges_c13_corner_and_returns_visual_review_passed','nativeScale':True,'initialWholeStripParts':[str(R/'joint-v1/qa'/f'{d}-s{i}.png')for d in ['north','west']for i in range(1,5)],'finalNativeChecks':[str(R/'joint-v4/qa'/f'{d}-junction{i}.png')for d in ['north','west']for i in range(1,4)]+[str(R/'joint-v4/qa'/f'{d}-corner-return.png')for d in ['north','west']]+[str(R/'joint-v4/qa/four-corner-final-native.png'),str(R/'joint-v4/qa/n-return3-final-native.png'),str(D/'wood-return-final-composite.png')]+[str(R/'joint-v2'/f'{x}-composite.png')for x in ['n-return1','n-return2','w-return1','w-return2']],'findings':['North paving cut-off stubs, cap micro-step and wood returns repainted continuously.','West table bevel, false hanging mortar, timber and water tone joined; last horizontal table pigment band repaired locally.','Central four-tile corner preserved and reconstructed at native1254.','Internal-v5 delta is disjoint from root shared-edge modifications; exact masks verify no unrelated overwrites.'],'formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False,'remaining':'Other neighbors and c14/c15 future four-tile corner, whole-city/runtime acceptance pending.'}
p.write(D/'visual-review.json',review)
ovpath=B/'tiles/current/current-overrides.json';ov=p.read(ovpath)
for tile,item in rec['outputs'].items():
    assert p.sha(item['file'])==item['sha256']
    if tile in ['r09_c14','r10_c13']:assert ov['tiles'][tile]['sha256']==item['baseSha256'],tile
    ov['tiles'][tile]={'file':item['file'],'sha256':item['sha256'],'status':'local_candidate_visual_review_passed','integrationRecord':str(D/'integration.json'),'visualReview':str(D/'visual-review.json')}
ov['updatedAt']=p.stamp();p.write(ovpath,ov)
rec['status']=review['status'];rec['visualReview']=str(D/'visual-review.json');p.write(D/'integration.json',rec)
print({k:v['sha256'] for k,v in rec['outputs'].items()})

