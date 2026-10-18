from pathlib import Path
from PIL import Image
import json,hashlib,datetime
T=Path(__file__).parent;Q=T/'qa/core-baseline/1368c15ca794536c2a6b';O=T/'qa/local-repair-20261016';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
candidate=Q/'r08_c09-core-baseline.candidate.png';im=Image.open(candidate).convert('RGB');assert im.size==(4096,4096)
issues=[
 {'id':'upper-right-paving','priority':2,'location':'tile y1024 x3072..4096; p14/E external also retained','detail':'Diagonal slab grout endpoints displaced at p14/p24 join; external east endpoints remain pending','attemptsThisCycle':0},
 {'id':'blue-band-step','priority':2,'location':'tile x3072 near y1800..2050','detail':'Ivory margin and blue-gray inlay have a false step at p23/p24; internal source context boundary copied into paving','attemptsThisCycle':0},
 {'id':'p32-context-boundary','priority':2,'location':'tile x1933 near y2163','detail':'Rectangular walkway grout changes height at former context boundary, retained for later local correction','attemptsThisCycle':0},
 {'id':'p33-p34-context-boundaries','priority':2,'location':'tile y2957 and x3981','detail':'Artificial horizontal/vertical material cuts inside selected native cores; not a valid layout seam','attemptsThisCycle':0},
 {'id':'p42-east-phase','priority':2,'location':'tile x2048 y3072..4096','detail':'Diagonal grout phase mismatch retained; best p42 v2; two previous failed repairs already exhausted','attemptsAfterInitial':2,'status':'deferred_unpassed'}]
review={'tile':T.name,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':str(candidate),'candidateSha256':sha(candidate),'assembly':str(Q/'assembly.json'),'inputSignature':'1368c15ca794536c2a6b0b1ce38604bf187f0d35777d197488ad86b081468bfa','sourcesVerifiedUnchanged':True,'reviewedInternalPairs':24,'reviewedIntersections':9,'reviewEvidence':'24 native 384x1024/1024x384 joins in 8 native-scale sheets; all 9 intersections separately viewed at 900x900. Whole4096 overview only. Prior quick review retained, full review supersedes narrow provisional views.','internalPassed':False,'formalAcceptedCount':0,'pendingP2':issues,'stableRegions':['stairs across p11 p12 p13','left upper walkway','most true p31/p32/p33 joins and outer east lower joins'],'actualModel':None}
save(T/'qa/review-20261016/internal-review-v1.json',review)
progress=json.loads((T/'tile-progress.json').read_text(encoding='utf8'));progress.update(status='native_16_complete_internal_QA_unpassed',completeCandidateCount=1,candidate=str(candidate),candidateSha256=sha(candidate),visualReview=str(T/'qa/review-20261016/internal-review-v1.json'),reviewedInternalPairs=24,reviewedCompleteIntersections=9,pendingP2=issues,updatedAt=review['reviewedAt']);save(T/'tile-progress.json',progress)
plans=[]
for name,origin in [('upper-right-paving',[2842,397]),('blue-band-step',[2320,1400])]:
 dest=O/(name+'-input-v1.png');assert not dest.exists();x,y=origin;im.crop((x,y,x+1254,y+1254)).save(dest)
 plans.append({'id':name,'origin':origin,'target':str(dest),'targetSha256':sha(dest),'sourceCandidate':str(candidate),'sourceCandidateSha256':sha(candidate),'operation':'integer1254 crop, no resampling'})
save(O/'plan-v1.json',{'tile':T.name,'repairs':plans});print(json.dumps(plans,indent=2))
