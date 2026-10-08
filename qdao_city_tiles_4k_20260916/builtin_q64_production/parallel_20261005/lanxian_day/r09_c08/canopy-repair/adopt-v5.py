from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,os
import numpy as np
from PIL import Image
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
T=ROOT/'r09_c08'; D=T/'canopy-repair'; V=D/'candidate-v5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readj(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p,role=None):
 r={'file':str(p),'path':str(p),'sha256':sha(p)}
 if role:r['role']=role
 return r
def writej(p,v):
 assert p.resolve().is_relative_to(ROOT)
 if p.exists():raise FileExistsError(p)
 tmp=p.with_name(p.name+'.adoption.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
candidate=V/'candidate1254.png';native=T/'native/r01_c03.png';ng=Path(str(native)+'.generation.json');nprompt=T/'native/r01_c03.prompt.txt'
for p in [native,ng,nprompt,D/'adoption-proof.json',V/'review.json']:assert not p.exists(),str(p)
assert sha(candidate)=='a8e8ece5cf8ea2a958536b2674e588451781b62129129750937abb55ec12a6fc'
root_review=D/'root-v5-review.json';rr=readj(root_review)
assert rr['approvedForDerivedNativeContinuation'] and rr['candidate']['sha256']==sha(candidate)
untouched=sorted((T/'jobs').glob('r01_c03*'))+[T/'prompts/r01_c03.prompt.txt',D/'bridge.receipt01.json',D/'bridge.generation01.json']
before={str(p):sha(p) for p in untouched}
baseg=T/'jobs/r01_c03.attempt04.generation.json';bg=readj(baseg);base=Path(bg['file'])
repairg=D/'bridge.generation01.json';rg=readj(repairg);receipt=D/'bridge.receipt01.json';repair=Path(readj(receipt)['sourceOutputPath'])
assert sha(base)==bg['sha256']
assert sha(repair)==rg['sha256']
m=readj(V/'manifest.json')
a=np.array(Image.open(candidate).convert('RGB'));b=np.array(Image.open(base).convert('RGB'))
north=Path(m['sourceNativeImages']['authenticNorthCore']['file']);east=Path(m['sourceNativeImages']['authenticEastNative']['file'])
n=np.array(Image.open(north).convert('RGB'));e=np.array(Image.open(east).convert('RGB'))
mask=np.array(Image.open(V/'replacement-mask.png'))>0
assert a.shape==(1254,1254,3)
assert np.array_equal(a[:115],n[3981:4096,1933:3187])
assert np.array_equal(a[115:,1139:],e[115:,115:230])
outside=~mask;outside[:115]=False;outside[115:,1139:]=False
assert np.array_equal(a[outside],b[outside])
for group in m['sourceNativeImages'].values():assert sha(Path(group['file']))==group['sha256']
roles={'replacement-mask.png':'Selected whole-crown native source copy mask','rgb-correction-mask.png':'Selected RGB support mask','rgb-continuous-alpha.png':'Continuous foliage edge alpha for RGB only','single-lobe-rgb-extension-alpha.png':'New locally authorized R64/G80/B32 lobe extension alpha','geometry-mask.png':'Selected bounded coordinate registration support','single-lobe-registration-mask.png':'Single right lobe source x+1/y-4 support','left-outline-extra-native-copy-mask.png':'Selected left outline extra native copy support','rgb-fields.npz':'Selected exact RGB delta fields, numeric color fields, per-pixel limits, alpha and native source coordinate dx/dy'}
technical=[ref(V/name,role) for name,role in roles.items()]
technical.append(ref(D/'build-candidate-v5.py','Reproducible selected local processing recipe'))
now=datetime.now(timezone.utc).isoformat()
views=['qa-short-edge220x120.png','qa-real-north1254x512.png','qa-canopy-mask-surround700x420.png','qa-right-mask-edge160x290.png','qa-bottom-mask-edge700x120.png']
review={'createdAtUtc':now,'reviewer':'c08_seam_diagnosis','status':'canopy_scope_accepted_for_derived_native_continuation','candidate':ref(candidate),'actualViews':[dict(ref(V/name),actuallyViewed=True) for name in views],'observations':['Targeted220x120: earlier short bright horizontal leaf surface no longer actionable; right lobe curve joins naturally.','Whole crown and mask surrounds: no remaining needles, detached fragments, bright columns or rectangular trunk/stone cut introduced.','Low-contrast north-ground material transition outside crown remains pending full north-strip tile QA.'],'rootReview':ref(root_review),'historyCorrection':'Earlier v3d broad-scope review missed a short right-lobe hard face. Targeted QA rejected v3d, v4, v4b and v4c. Existing historical reviews/receipts remain untouched. v5 preserves local geometry x+1/y-4 and raises color limits only for this single lobe.','sourceModelQualityUnconfirmed':True,'formalAccepted':False,'clientValidated':False,'wholeTileAccepted':False}
writej(V/'review.json',review)
processing=dict(m);processing['status']='selected_for_derived_native_continuation';processing['visualReviewPending']=False;processing['localReview']=ref(V/'review.json');processing['rootReview']=ref(root_review);processing['technicalArtifacts']=technical;processing['originalCandidateManifest']=ref(V/'manifest.json')
writej(V/'selected-processing.json',processing)
record={'schemaVersion':1,'file':str(native),'sha256':sha(candidate),'width':1254,'height':1254,'format':'PNG','mode':'RGB','cell':'r01_c03','isDerived':True,'tool':'local_native_processing','route':'local_native_processing','createdAt':now,'generatedAt':m['createdAtUtc'],'generatedAtMeaning':'Local derived candidate creation time, not an AI invocation timestamp.','adoptedAt':now,'configSnapshot':bg['configSnapshot'],'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None,'aiInvocation':False,'note':'No AI call during this derivation. Actual prompts, attachments and tool outputs remain unchanged in baseAI and repairAI evidence.'},'operation':m['operation'],'baseAI':{'image':ref(base),'generationRecord':ref(baseg),'actualReceipt':ref(T/'jobs/r01_c03.receipt.json'),'generatedAt':bg['generatedAt']},'repairAI':{'image':ref(repair),'generationRecord':ref(repairg),'actualReceipt':ref(receipt),'generatedAt':rg['generatedAt']},'nativeNeighborSources':{'northCore':ref(north),'northSourceAudit':ref(ROOT/'preflight/r09_c08-source-audit.json'),'eastNative':ref(east),'eastGenerationRecord':ref(Path(str(east)+'.generation.json'))},'candidateSource':ref(candidate),'processingEvidence':{'processing':ref(V/'selected-processing.json'),'recipe':ref(D/'build-candidate-v5.py'),'localReview':ref(V/'review.json'),'rootReview':ref(root_review),'technicalArtifacts':technical},'technicalArtifacts':technical,'geometry':{'nativePixels':[1254,1254],'coreBox':[115,115,1139,1139],'haloPixels':115,'neighborOverlapPixels':230},'status':'Adopted derived native cell for assembly; final tile north-ground QA and client validation still pending.','formalAccepted':False,'clientValidated':False,'unverifiedReason':'Local native source compositing, bounded integer registration and RGB fields used no AI call. Underlying builtin actual model/quality are undisclosed; configuration is a target only.'}
prompt_note='Derived native cell; no AI prompt was submitted for local processing. Base actual prompt/receipt: '+str(baseg)+'; repair actual prompt/receipt: '+str(repairg)+' / '+str(receipt)+'. Historical submissions are unchanged.'
nprompt.write_text(prompt_note,encoding='utf-8');record['prompt']=str(nprompt);record['promptSha256']=sha(nprompt);record['promptMeaning']='Provenance pointer for derived processing, not an AI submission prompt.'
temp=native.with_name(native.name+'.adoption.tmp');shutil.copyfile(candidate,temp);os.replace(temp,native);writej(ng,record)
assert sha(native)==record['sha256']
assert all(sha(Path(p))==digest for p,digest in before.items())
proof={'adoptedAt':now,'scope':'r09_c08/r01_c03 only','adoptedImage':ref(native),'adoptedGenerationRecord':ref(ng),'candidateSource':ref(candidate),'selectedProcessing':ref(V/'selected-processing.json'),'technicalArtifacts':technical,'rootApproval':ref(root_review),'invariants':{'nativeDimensions':[1254,1254],'coreCrop':[115,115,1139,1139],'trueNorth115Exact':True,'trueEastStrict115ExactBelowNorth':True,'allOtherBasePixelsExactOutsideMask':True,'allHistoricalJobGenerationReceiptAndPromptFilesUnchanged':True},'untouchedHistoricalFiles':[{'path':p,'sha256':h} for p,h in before.items()],'baseAI':record['baseAI'],'repairAI':record['repairAI'],'remaining':['Whole north-strip ground continuity and full tile internal/neighbor QA.'],'formalAccepted':False,'wholeTileAccepted':False}
writej(D/'adoption-proof.json',proof)
print(json.dumps({'native':str(native),'nativeSha256':sha(native),'nativeGenerationSha256':sha(ng),'adoptionProofSha256':sha(D/'adoption-proof.json'),'selectedProcessingSha256':sha(V/'selected-processing.json'),'technicalArtifactCount':len(technical),'unchangedHistoricalFileCount':len(before),'ready':True},indent=2))

