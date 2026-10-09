from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent;R=T.parent
sys.path.insert(0,str(R/'tools'));import finalize_scoped as fs
OLD='957194bcbf888cac88f8b0a3d79d055f8ce69a76846590f174eee7e6f8b9e456'
JOINT='c6893050313a641eaab6c3df3aa6c69d46224cb27e00c7586401c9f259096c4e'
CROP='92ba6908ea5511bc0ba23039c7b295d447d2b3bba5283029bdc4c5db78e03f3a'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
candidate=T/'output/r09_c15-candidate.png';gen=Path(str(candidate)+'.generation.json');manifest=T/'output/manifest.json';assembly=T/'output/native-assembly.json'
west=Path(read(T/'plan.json')['westCandidate']);protected={str(q):sha(q) for q in [west,assembly,T/'plan.json']}
assert sha(candidate)==OLD and sha(P/'proposed-joint-v19.png')==JOINT and sha(P/'proposal-apply-crop-v19.png')==CROP
root_items=[]
for name in ['proposed-joint-v19.png','upper-perimeter-v19.png','right-perimeter-v19.png','lower-perimeter-v19.png','west-join-v19.png','lower-detail-v19.png','three-crossings-v19.png']:
 root_items.append({**ref(P/name),'actuallyViewed':True,'nativeScale':1,'verdict':'scoped_pass','review':'Root actual original-scale view: upper/middle color changes progress along diagonal bevels; all three grout geometries continue, lower segment and returns show no obvious join cutoff.'})
write(P/'root-review-v19.json',{'recordedAt':now(),'reviewer':'/root','evidence':'Direct parent authorization after viewing all7 originals; recorded by child on behalf of parent.','joint':ref(P/'proposed-joint-v19.png'),'candidateBefore':ref(candidate),'items':root_items,'scopedPass':True,'localRepairApproved':True,'applicationAuthorized':True,'applicationCandidateLTRB':[0,2840,600,3750],'finalTileAccepted':False,'issues':[]})
H=P/'history-before-v19-application';assert not H.exists();H.mkdir()
paths=[gen,manifest,assembly,T/'plan.json']
if (T/'progress.json').exists():paths.append(T/'progress.json')
paths += [q for q in (T/'qa').rglob('*') if q.is_file() and q.suffix.lower() in ['.json','.md','.txt']]
hist=[]
for q in sorted(set(paths)):
 dest=H/q.relative_to(T);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
 hist.append({'originalFile':str(q),'historicalRecord':ref(dest)})
write(H/'index.json',{'createdAt':now(),'oldCandidateSha256':OLD,'textOnly':True,'oldPNGBackedUp':False,'records':hist})
oldroot=read(H/'qa/root-review.json');proof=read(H/'qa/root-view-source-proof-957194.json')
assert len(oldroot['items'])==10
before=np.array(Image.open(candidate).convert('RGB'));joint=np.array(Image.open(P/'proposed-joint-v19.png').convert('RGB'));crop=np.array(Image.open(P/'proposal-apply-crop-v19.png').convert('RGB'))
assert np.array_equal(crop,joint[80:990,320:920])
after=before.copy();after[2840:3750,:600]=crop
owner=np.zeros((4096,4096),bool);owner[2840:3750,:600]=True
assert np.array_equal(after[~owner],before[~owner]) and np.array_equal(after[3776:],before[3776:])
# Sole guarded canonical image write; no old PNG backup.
Image.fromarray(after).save(candidate)
newsha=sha(candidate)
diff=np.any(after!=before,axis=2);ys,xs=np.nonzero(diff)
application={'appliedAt':now(),'status':'applied_pending_current_QA_and_root_finalization','canonical':str(candidate),'oldImageSha256':OLD,'newImageSha256':newsha,'oldImageStatus':'superseded_after_approved_application_no_PNG_backup','rootApproval':ref(P/'root-review-v19.json'),'proposal':ref(P/'proposal-v19.json'),'applyCrop':ref(P/'proposal-apply-crop-v19.png'),'applyCandidateLTRB':[0,2840,600,3750],'sourceJointLTRB':[320,80,920,990],'actualChangedBBoxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedPixels':int(diff.sum()),'outsideAuthorizedRegionBitExact':True,'westNeighborBitExact':True,'candidateX600PlusBitExact':True,'candidateY3750PlusBitExact':True,'candidateSouth320BitExact':True,'immutableAssembly':ref(assembly),'immutableAssemblyUnchanged':True,'textHistoryIndex':ref(H/'index.json'),'script':ref(Path(__file__).resolve()),'formalAccepted':False}
write(P/'application-v19.json',application)
prior=read(H/'output/r09_c15-candidate.png.generation.json')
generation={**ref(candidate),'createdAt':now(),'width':4096,'height':4096,'format':'PNG','operation':'Guarded approved native AI repair crop application; all other candidate pixels identical.','derivedFrom':[{'file':str(candidate),'sha256':OLD,'lifecycle':'superseded_after_approved_application','availableAtPath':False,'historicalGeneration':ref(H/'output/r09_c15-candidate.png.generation.json')},ref(P/'proposal-apply-crop-v19.png')],'nativeAssembly':ref(assembly),'application':ref(P/'application-v19.json'),'original16NativeSources':prior['derivedFrom'],'actualModel':None,'actualQuality':None,'modelEvidence':'Mechanical derivative. Each native/source AI generation record preserves target, submitted fields, and actual unknown model/quality.','productionPixels':True,'sourceUpscaled':False,'formalAccepted':False,'clientVerified':False,'navigationVerified':False}
write(gen,generation)
m=read(H/'output/manifest.json');m['sha256']=newsha;m['updatedAt']=now();m['status']='native4K_repair_applied_pending_current_QA';m['formalAccepted']=False;m['scopedLocalSeamsPassed']=False;m['postAssemblyRepairs']=[ref(P/'application-v19.json')];m['immutableSourceAssembly']=ref(assembly);m['currentGeneration']=ref(gen);m['originalAssemblyCandidateSha256']=OLD
write(manifest,m)
ctx=fs.context('r09_c15',newsha);required=fs.requirements(ctx)
records=[]
for k,r in required.items():
 path=r['path'];r['image'].save(path)
 item={**ref(path),'pixels':list(r['image'].size),'nativeScale':1,'actuallyViewed':False,'verdict':'pending_visual_QA','operation':r['operation'],'sources':[ctx['references'][role] for role in r['roles']],'currentCandidate':ref(candidate)}
 write(Path(str(path)+'.generation.json'),item);records.append(item)
write(T/'qa/native-candidate/current-index.json',{'createdAt':now(),'candidate':ref(candidate),'application':ref(P/'application-v19.json'),'items':records,'formalAccepted':False})
# Rebuild six existing true west details using exact historical reproduction coordinates.
details=[]
for q in sorted((H/'qa/external-details').glob('*.png.generation.json')):
 rec=read(q);path=Path(rec['file']);recipe=rec['reproduction'];im=fs.extra_image(ctx,path,rec);im.save(path)
 item={**rec,**ref(path),'actuallyViewed':False,'verdict':'pending_visual_QA','sources':[ref(west),ref(candidate)],'currentCandidate':ref(candidate)}
 write(Path(str(path)+'.generation.json'),item);details.append(item)
# Rebind the10 root-owned views only after exact bytes AND RGB values match the historical proof.
proofmap={r['file']:r for r in proof['items']};root=[]
for item in oldroot['items']:
 path=Path(item['file']);p=proofmap[item['file']]
 rgbsha=hashlib.sha256(Image.open(path).convert('RGB').tobytes()).hexdigest()
 assert sha(path)==item['sha256']==p['sha256'] and rgbsha==item['pixelSha256']==p['pixelSha256'],str(path)
 expected=required[fs.key(path)]['image'];assert expected.tobytes()==Image.open(path).convert('RGB').tobytes()
 it={**item,'newVisualInspectionClaimed':False,'inspectionInheritance':{'historicalReview':ref(H/'qa/root-review.json'),'historicalCandidateSha256':OLD,'historicalReviewer':item.get('reviewer'), 'exactPNGBytesUnchanged':True,'exactRGBPixelsUnchanged':True,'reproducedFromCurrentCandidate':True,'actualViewingOccurredOnIdenticalHistoricalPixels':True},'currentCandidateSha256':newsha}
 root.append(it)
write(T/'qa/root-review.json',{**oldroot,'candidate':ref(candidate),'items':root,'reboundAt':now(),'newVisualInspectionClaimed':False,'historicalReview':ref(H/'qa/root-review.json'),'rebindReason':'All10 actual-view images reproduce byte-for-byte and RGB-for-RGB unchanged after localized west repair. No fresh visual inspection claimed.','issues':[],'issueCount':0,'scopedPass':True})
write(T/'qa/root-review-rebind-v19.json',{'createdAt':now(),'candidate':ref(candidate),'historicalReview':ref(H/'qa/root-review.json'),'historicalProof':ref(H/'qa/root-view-source-proof-957194.json'),'items':root,'all10ExactBytesAndPixelsUnchanged':True,'newVisualInspectionClaimed':False})
for name,flag in [('horizontal-review.json','scopedPass'),('external-review.json','externalScopedPass')]:
 write(T/'qa'/name,{'createdAt':now(),'candidate':ref(candidate),'items':[],'issues':['Current candidate actual visual review pending'],flag:False,'historicalReview':ref(H/'qa'/name)})
write(T/'qa/native-review-index.json',{'createdAt':now(),'candidate':ref(candidate),'west':ref(west),'immutableAssembly':ref(assembly),'application':ref(P/'application-v19.json'),'standardQA':records,'unrotatedWestDetails':details,'formalAccepted':False,'sourcePixelScale':1})
for p,h in protected.items():assert sha(p)==h,p
assert sha(candidate)==newsha and len(records)==27 and len(details)==6
print(json.dumps({'candidate':ref(candidate),'application':ref(P/'application-v19.json'),'standardQA':len(records),'westDetails':len(details),'rootViewsRebound':len(root),'immutableAssemblyUnchanged':True,'finalizerApproveCalled':False}))

