from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
from datetime import datetime,timezone
D=Path(__file__).parent;B=D.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def write(p,j):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2)
def check(r):
 p=Path(r['path']);assert sha(p)==r['sha256'],str(p);return p
finaldir=B/'qa/r12c07-resume2-r19-v1';fa=read(finaldir/'assembly.json');final=np.asarray(Image.open(finaldir/'context-native.png').convert('RGB'))
r18p=B/'qa/r12c07-resume2-r18-v1/assembly.json';r18a=read(r18p);r18ctx=r18p.parent/r18a['context']['path'];assert sha(r18ctx)==r18a['context']['sha256'];r18=np.asarray(Image.open(r18ctx).convert('RGB'))
assert r18a['proof']['mismatches']==0 and r18a['proof']['uncovered']==0
sourcechecks=[]
for s in r18a['sourceLegend']:
 p=Path(s['path']);p=p if p.is_absolute() else B/p;assert sha(p)==s['sha256'];sourcechecks.append({'sourceId':s['sourceId'],**rec(p)})
planpath=B/'repairs/r12c07-resume2-north-ai-v1/top-replay-plan-v1.json';plan=read(planpath)
spec=importlib.util.spec_from_file_location('north_replay',planpath.parent/'replay_top.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
replayed=mod.reconstruct(r18,plan);assert np.array_equal(replayed,np.asarray(Image.open(check(plan['expectedFinalContext'])).convert('RGB')))
north=checkedNorth=replayed.copy();ov=fa['repairOverlay'];mask=np.load(check(ov['mask'])).astype(bool);src=np.asarray(Image.open(check(ov['source'])).convert('RGB'));x,y,x1,y1=ov['contextBox'];replayed[y:y1,x:x1][mask]=src[mask]
assert np.array_equal(replayed,final);assert np.array_equal(final[:570],north[:570]);assert np.array_equal(final[1766:],r18[1766:]);assert np.array_equal(np.asarray(Image.open(finaldir/'r12_c07.candidate.png').convert('RGB')),final[115:4211,115:4211])
chain=[];cur=finaldir/'assembly.json'
while True:
 a=read(cur);chain.append(rec(cur));base=a.get('baseAssembly')
 if not base:break
 cur=check(base)
 assert len(chain)<50
proof={'hierarchicalFullContextReplayDifferentPixels':0,'uncoveredPixels':0,'baseR18NativeLeafReplayReused':{'assembly':rec(r18p),'proof':r18a['proof'],'sourceHashesChecked':sourcechecks},'northPlan':rec(planpath),'northDonorNativeLeafProof':rec(B/'qa/r12c07-resume2-north-review-v1/source-research-v2.json'),'top570DifferentPixelsFromNorthFinal':0,'rows1766OnwardDifferentPixelsFromR18':0,'candidateCropIdentityMismatchPixels':0,'formalAccepted':False,'noResize':True,'noBlend':True,'noBlur':True}
write(D/'final-replay-proof-v1.json',proof)
internalpath=B/'qa/r12c07-resume2-open-junction-review-v1/independent-review-v1.json';assert internalpath.exists()
northreview=B/'qa/r12c07-resume2-north-ai-v1/review-v1.json'
qa={'schemaVersion':1,'tile':'r12_c07','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'best-native-candidate-with-open-external-findings','formalAccepted':False,'currentAssembly':rec(finaldir/'assembly.json'),'currentContext':rec(finaldir/'context-native.png'),'internalNewRepairQA':[rec(B/f'qa/r12c07-resume2-r{r}-v1/visual-qa-v1.json') for r in [17,18,19]],'internalOpenJunctionReview':rec(internalpath),'northQA':rec(northreview),'reuseRules':['R19 does not alter top570; all northern actual-core join and local checks remain pixel-identical in their changed area.','Rows1766 onward equal R18 exactly; lower internal review is reusable. J2-right upper overlap changed by R19 and is covered by its bottom/left local QA.','The prior full tile is not automatically passed by a source replay proof.'],'pending':[{'id':'north-N04-far-east-texture-transition','contextBox':[3900,115,4211,275],'globalBox':[28361,45056,28672,45216],'description':'Fine/coarse sand texture shift adjoining preserved eastern vegetation shadow; improved but not passed.'},{'id':'west-R05','status':'deferred-after-two-unsuccessful-attempts','description':'Actual western core joins remain pending; R05 v1/v2 not selected. r12c06 frozen best remains read-only anchor.'},{'id':'south-external','status':'pending-neighbour-production','description':'r13c07 currently being repaired by another worker; no acceptance claimed.'},{'id':'east-external','status':'pending-not-checked','description':'No stable eastern-neighbour actual core join checked in this continuation.'}],'sourceProof':rec(D/'final-replay-proof-v1.json')}
write(D/'delivery-qa-v1.json',qa)
manifest={'schemaVersion':1,'tile':'r12_c07','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native4096-best-candidate-with-pending-qa','formalAccepted':False,'nativeCoreCount':16,'coreSize':4096,'contextSize':4326,'halo':115,'globalContextBox':[24461,44941,28787,49267],'globalCoreBox':[24576,45056,28672,49152],'candidate':rec(finaldir/'r12_c07.candidate.png'),'context':rec(finaldir/'context-native.png'),'assembly':rec(finaldir/'assembly.json'),'initialSelection':rec(B/'records/selection-r12c07-v1.json'),'qa':rec(D/'delivery-qa-v1.json'),'fullReplayProof':rec(D/'final-replay-proof-v1.json'),'orderedAssemblyChainNewestFirst':chain,'northPlan':rec(planpath),'recoveredR17':rec(D/'recovery-v1.json'),'newNativeAIImageCount':5,'recoveredNativeImageCount':1,'newRoute':'builtin','actualModel':'not returned','pending':qa['pending'],'allOriginalAndRejectedImagesRetained':True,'scripts':[rec(D/'workflow.py'),rec(__file__)]}
write(D/'delivery-manifest-v1.json',manifest)
print(json.dumps({'candidate':manifest['candidate'],'context':manifest['context'],'assembly':manifest['assembly'],'manifest':rec(D/'delivery-manifest-v1.json'),'qa':rec(D/'delivery-qa-v1.json'),'replay':rec(D/'final-replay-proof-v1.json'),'chainLength':len(chain)}))
