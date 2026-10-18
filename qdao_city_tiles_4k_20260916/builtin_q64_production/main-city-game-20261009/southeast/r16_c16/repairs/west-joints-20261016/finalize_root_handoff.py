from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
C=read(R/'W01-v1/compact-mask-v2/composition.json');Q=read(R/'batch-visual-qa.json')
base=Image.open(C['base']['path']).convert('RGB');region=C['tilePlacement'];regionHash=hashlib.sha256(base.crop(region).tobytes()).hexdigest()
op={k:C[k] for k in ['native','receipt','preparation','nativeCrop','tilePlacement','alpha','formula']}
M={'tile':'r16_c16','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'root_reviewed_local_best_operation_only','sourceComposition':ref(R/'W01-v1/compact-mask-v2/composition.json'),'sourceReplay':ref(R/'W01-v1/compact-mask-v2/replay-verification.json'),'originalBase':C['base'],'operations':[op],'integrationGuard':{'verifyCurrentRegionRGBSha256BeforeApplying':regionHash,'region':region,'pixelMode':'RGB','pixelOrder':'Pillow crop(...).tobytes() row-major','allowedDifferencesElsewhere':'Other workers may have edited disjoint north/right zones; never use whole trial PNG to replace those.'},'rootReview':{'reportedBy':'/root','result':'local_best_approved_with_closure_shape_and_material_watch','evidence':'Root reports independent view of compact-mask-v2 four native-sized crops: closed coping improves missing connection; no new north orphan or mask-cut line. Entire west remains not passed.'},'remainingWest':['W02_failed_deferred_after_two_attempts','W03_gold_stone_material_pending','W04_middle_grid_material_pending'],'formalAccepted':False,'noSelectionChanged':True}
p=R/'root-integration-manifest.json';assert not p.exists();p.write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
Q['previousReport']=ref(R/'batch-visual-qa.json');Q['recordedAt']=M['recordedAt'];Q['reviews'][0]['status']='root_reviewed_local_best_approved_with_closure_shape_and_material_watch';Q['reviews'][0]['rootReview']=M['rootReview'];Q['rootIntegrationManifest']=ref(p);Q['rootMergeGuidance']='Apply only root-integration-manifest operation after checking exact input region RGB hash. W01 local best approved by root; preserve closure shape/material watch. All west remains not passed. W02 both attempts unselected; retain original pixels.'
q=R/'batch-visual-qa-root-reviewed.json';assert not q.exists();q.write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'integrationManifest':ref(p),'currentQA':ref(q),'expectedInputRegionRGBSha256':regionHash,'formalAccepted':False}))
