
from pathlib import Path
import sys,json,shutil,copy
import numpy as np
from PIL import Image
BASE=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn')
sys.path.insert(0,str(BASE))
from production import sha,read,write,deriv,now
from native_assemble import make_qa
TILE=BASE/'r09_c14';OUT=TILE/'repairs/west-foliage';HISTORY=OUT/'history-before-v9-application'
candidate=TILE/'output/r09_c14-candidate.png';generation=Path(str(candidate)+'.generation.json')
expected='4644eb1abda4cea7c23d82cf72f387e9a5c97985ccf497d0149069f0a67daf07'
assert sha(candidate)==expected and not HISTORY.exists(),'Immutable application; do not repeat'
proposal=read(OUT/'proposal-v9.json');merge=Path(proposal['proposedMerge']['file']);box=proposal['proposedMerge']['candidateRectLTRB']
assert sha(merge)=='ef67d88b980473c94ac813d28594200ef158f2f7ffd38d402eee0df2eead5e65'
assert box==[0,1085,455,2269] and Image.open(merge).size==(455,1184)
plan=read(TILE/'plan.json');west=Path(plan['westCandidate']);westsha=sha(west);assert westsha==plan['westCandidateSha256']
nativeAssembly=TILE/'output/native-assembly.json';nativeAssemblySHA=sha(nativeAssembly)
oldgen=read(generation);manifest=TILE/'output/manifest.json';oldmanifest=read(manifest)
HISTORY.mkdir(parents=True)
hist=[]
for p,name in [(generation,'candidate.generation.before-v9.json'),(nativeAssembly,'native-assembly.before-v9.json'),(manifest,'pending-manifest.before-v9.json')]:
 dest=HISTORY/name;shutil.copy2(p,dest);hist.append(dict(originalFile=str(p),historicalRecordFile=str(dest),historicalRecordSha256=sha(dest)))
# Text-only history; all original QA review and image-source records remain traceable.
for p in sorted((TILE/'qa').rglob('*.json')):
 rel=p.relative_to(TILE/'qa');dest=HISTORY/'qa'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);hist.append(dict(originalFile=str(p),historicalRecordFile=str(dest),historicalRecordSha256=sha(dest)))
a=np.array(Image.open(candidate).convert('RGB'));b=a.copy();b[box[1]:box[3],box[0]:box[2]]=np.array(Image.open(merge).convert('RGB'))
changed=np.any(a!=b,axis=2);ys,xs=np.nonzero(changed);actual=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
assert actual==box and np.array_equal(a[:,800:],b[:,800:]) and np.array_equal(a[3776:],b[3776:]) and np.array_equal(a[:1085],b[:1085])
Image.fromarray(b).save(candidate);newsha=sha(candidate);assert Image.open(candidate).size==(4096,4096)
application=OUT/'application-v9.json'
record=dict(appliedAt=now(),tile='r09_c14',status='applied_pending_full_current_visual_QA',candidate=dict(file=str(candidate),sha256=newsha),baseCandidateSha256=expected,merge=dict(file=str(merge),sha256=sha(merge)),proposal=dict(file=str(OUT/'proposal-v9.json'),sha256=sha(OUT/'proposal-v9.json')),candidateRectLTRB=actual,changedPixels=int(changed.sum()),changedPixelBBoxVerified=True,fixedWestNeighbor=dict(file=str(west),sha256=westsha),fixedWestNeighborUnchanged=True,x800AndAfterBitExact=True,south320BitExact=True,north1085BitExact=True,sourcePixelScale=1,sourceUpscaling=False,wholeOriginalCandidateImageCopied=False,sourceHashMigration=dict(path=str(candidate),before=expected,after=newsha,originalBytesNoLongerAtPath=True,originalGenerationRecord=hist[0],originalAssemblyImmutable=dict(file=str(nativeAssembly),sha256=nativeAssemblySHA),nativeAssemblyDescribesHistoricalBeforeRepairBytes=True,originalPixelsStillRepresentedByNativeSourcesAndJoinCrop=True),textHistory=hist,script=dict(file=str(Path(__file__).resolve()),sha256=sha(__file__)),formalAccepted=False,clientVerified=False,navigationVerified=False)
write(application,record)
newgen=dict(file=str(candidate),sha256=newsha,createdAt=now(),width=4096,height=4096,format='PNG',derivedFrom=[dict(file=str(candidate),sha256=expected,generationRecord=str(HISTORY/'candidate.generation.before-v9.json'),historical=True,fileNoLongerContainsTheseBytes=True,replacedBySha256=newsha),dict(file=str(merge),sha256=sha(merge),generationRecord=str(merge)+'.generation.json')],operation=dict(file=str(application),sha256=sha(application)),submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,modelEvidence='Original native sources and each AI repair retain separate records; actual host-managed model/quality not disclosed.',productionPixels=True,formalAccepted=False,clientVerified=False,navigationVerified=False)
write(generation,newgen)
neighbors={'west':dict(reference=dict(file=str(west),sha256=westsha),pixels=np.array(Image.open(west).convert('RGB')))}
qa=make_qa(candidate,neighbors,TILE/'qa/native-candidate',256);assert len(qa)==26
detailRefs=[];wa=Image.open(west).convert('RGB');nb=Image.open(candidate).convert('RGB')
for i in range(4):
 y=i*1024;p=TILE/f'qa/external-details/west-segment-{i+1}.png';im=Image.new('RGB',(512,1024));im.paste(wa.crop((3840,y,4096,y+1024)),(0,0));im.paste(nb.crop((0,y,256,y+1024)),(256,0));im.save(p)
 deriv(p,[west,candidate],dict(kind='unrotated_actual_west_neighbor_seam_1_to_1',oldSourceBoxLTRB=[3840,y,4096,y+1024],candidateSourceBoxLTRB=[0,y,256,y+1024],pasteXY=[[0,0],[256,0]],nativeScale=1,tileBoundaryX=256))
 detailRefs.append(dict(file=str(p),sha256=sha(p)))
write(TILE/'qa/native-candidate/current-index.json',dict(candidate=dict(file=str(candidate),sha256=newsha),standardQA=qa,unrotatedWestDetails=detailRefs,allCurrentImagesPendingVisualReview=True))
record.update(standardQARegenerated=26,unrotatedWestDetailsRegenerated=4,qaReady=True,currentQAIndex=dict(file=str(TILE/'qa/native-candidate/current-index.json'),sha256=sha(TILE/'qa/native-candidate/current-index.json')))
write(application,record);newgen['operation']['sha256']=sha(application);write(generation,newgen)
oldmanifest.update(updatedAt=now(),sha256=newsha,status='native_AI_west_repair_applied_pending_current_visual_QA',qa=qa,scopedLocalSeamsPassed=False,repairApplication=dict(file=str(application),sha256=sha(application)),nativeAssemblyHistoricalSha256=expected,formalAccepted=False)
write(manifest,oldmanifest)
assert sha(nativeAssembly)==nativeAssemblySHA and sha(west)==westsha
print(json.dumps(dict(candidate=str(candidate),sha256=newsha,standardQA=26,westDetails=4,actualChangedBBox=actual,changedPixels=int(changed.sum()),application=str(application)),ensure_ascii=False))

