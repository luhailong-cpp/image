from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
Q=T/'qa/resume-20261016';Q.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A=T/'qa/core-baseline/49a09ec3f906ad1622fe/assembly.json';a=read(A)
cand=next(i for i in a['artifacts'] if i['kind']=='complete-4k-candidate-unreviewed')
assert sha(Path(cand['file']))==cand['sha256']
for s in a['inputs']['nativeSources']:assert sha(Path(s['file']))==s['sha256']
old=T/'qa/evidence-v20261012/first-row-visual-review-0e9feb587f4ac73c3cdc-20261012T150504303948Z.json'
issues=[
{'id':'floor-join','priority':'P1','tileBox':[990,3072,1100,4096],'finding':'p41/p42 slab grout endpoints disconnect and abruptly change angle across x1024; blocks propagation south until repaired.','priorSamePointRepairAttempts':0},
{'id':'wall-joints','priority':'P2','tileBox':[3072,1990,4096,2110],'finding':'p24/p34 masonry grout offsets at y2048; broad straight rectangular splice.','priorSamePointRepairAttempts':0},
{'id':'leaf-notch','priority':'P2','tileBox':[2030,2048,2200,2190],'finding':'p33 upper-left source context boundary has rectangular leaf truncation at x2048 and y2163.','priorSamePointRepairAttempts':0},
{'id':'window-strip','priority':'P2','tileBox':[1024,1090,1590,1180],'finding':'p22 native context boundary creates horizontal strip through lattice and wood trim near y1139.','priorSamePointRepairAttempts':0},
{'id':'wall-material','priority':'P2','tileBox':[3000,970,4096,3120],'finding':'Straight stone-wall material/tone steps at y1024 and y3072 remain although most joints are geometrically connected.','priorSamePointRepairAttempts':0},
{'id':'cream-material','priority':'P2','tileBox':[1024,1024,2600,2170],'finding':'Cream wall texture has visible quadrant changes around p22/p23/p32/p33. No structural wall hole.','priorSamePointRepairAttempts':0}
]
windows=[i for i in a['artifacts'] if i['kind']=='native-pixel-intersection-crop' or (i['kind']=='native-pixel-seam-crop' and not (Path(i['file']).name.startswith('vertical-p1')))]
review={'tile':'r07_c16','createdAt':datetime.now(timezone.utc).isoformat(),'candidate':cand['file'],'candidateSha256':cand['sha256'],'assembly':str(A),'sourceHashesReverified':True,'selectedNativeCount':16,'nativeVersionCount':18,'internalPassed':False,'formalAcceptedCount':0,'reviewedNow':windows,'inspection':'21 seam windows and 9 intersections viewed at native resolution; 4096 whole tile was displayed resized for overview only.','reusedFirstRowReview':{'file':str(old),'sha256':sha(old),'unchangedInputs':True,'seams':3},'internalPairsCovered':24,'intersectionsCovered':9,'pendingIssues':issues,'externalSeams':'Only first-row west historical pass reused; other outer edges pending.'}
save(Q/'baseline-review-v1.json',review)
p=read(T/'tile-progress.json');p.update(owner='/root/east_resume_20261016',status='complete-4k-candidate-local-repairs-pending',candidate=cand['file'],candidateSha256=cand['sha256'],complete4kCandidateCount=1,completeCandidateCount=1,internalPassed4kCount=0,internalPassed=False,formalAcceptedCount=0,pendingP1Count=1,pendingP2Count=5,localVisualReview=str(Q/'baseline-review-v1.json'),nextStep='Repair floor join and local masonry/foliage/window defects with bounded native AI repairs; retain unpassed if residual edges remain.',inflightRequests=[],unsavedSuccessfulOutputs=[],updatedAt=datetime.now(timezone.utc).isoformat())
save(T/'tile-progress.json',p)
specs=[('floor-join',[397,2842]),('wall-joints',[2842,1430]),('leaf-notch',[1480,1560]),('window-strip',[830,570])]
im=Image.open(cand['file']).convert('RGB'); reps=[]
for id,xy in specs:
 path=Q/(id+'-input-v1.png');assert not path.exists();im.crop((xy[0],xy[1],xy[0]+1254,xy[1]+1254)).save(path)
 reps.append({'id':id,'origin':xy,'file':str(path),'sha256':sha(path),'size':[1254,1254],'resized':False})
save(Q/'repair-plan-v1.json',{'tile':'r07_c16','baseCandidate':cand,'repairs':reps})
print(json.dumps({'candidate':cand['file'],'sha256':cand['sha256'],'review':str(Q/'baseline-review-v1.json'),'repairs':reps},ensure_ascii=False))

