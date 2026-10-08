from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,os
import numpy as np
from PIL import Image
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
T=ROOT/'r09_c08'; D=T/'r04c04-east-repair'; V=D/'registered-v1'
assert D.resolve().is_relative_to(ROOT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def readj(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p): return {'path':str(p),'sha256':sha(p)}
def writej(p,v):
 assert p.resolve().is_relative_to(ROOT)
 temp=p.with_name(p.name+'.adoption.tmp'); temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); os.replace(temp,p)
native=T/'native/r04_c04.png'; ng=Path(str(native)+'.generation.json'); orig=D/'original/native/r04_c04.png'; og=Path(str(orig)+'.generation.json'); candidate=V/'candidate1254.png'
assert sha(native)==sha(orig)=='a116f105c7e0cb962f10dca5e1d8f9f797866928551bec8ffe6e69f952491468'
assert sha(ng)==sha(og)
assert sha(candidate)=='ed735ab2f955688d8eb55e443eb831f62844dfc1a7bf38fc2db34a19110d8f40'
untouched=[T/'jobs/r04_c04.json',T/'jobs/r04_c04.receipt.json',T/'native/r04_c04.prompt.txt',T/'prompts/r04_c04.prompt.txt']
before={str(p):sha(p) for p in untouched}
request=T/'jobs/r04_c04.actual-request.json'
if request.exists():
 target=D/'original/jobs/r04_c04.actual-request.json'
 if not target.exists(): shutil.copy2(request,target)
 assert sha(request)==sha(target)
old=readj(og); derived=readj(V/'candidate1254.png.generation.json'); processing=readj(V/'processing.json')
a=np.asarray(Image.open(orig).convert('RGB')); b=np.asarray(Image.open(candidate).convert('RGB'))
assert b.shape==(1254,1254,3)
assert np.array_equal(a[:115],b[:115]); assert np.array_equal(a[:,:640],b[:,:640])
east=ROOT/'r09_c09/selected/extended4326.png'; ep=np.asarray(Image.open(east).convert('RGB'))
assert np.array_equal(b[115:,1139:],ep[3187:4326,115:230])
core=Image.fromarray(b).crop((115,115,1139,1139)); assert core.size==(1024,1024)
accepted=datetime.now(timezone.utc).isoformat()
record=dict(derived)
record.update(file=str(native),sha256=sha(candidate),cell='r04_c04',isDerived=True,tool='local_native_processing',route='local_native_processing',width=1254,height=1254,format='PNG',mode='RGB',generatedAt=derived['createdAt'],generatedAtMeaning='Time this derived candidate record was created; not an AI invocation timestamp.',adoptedAt=accepted,actualModel=None,actualQuality=None,status='Adopted derived native cell for assembly; whole-tile visual/client acceptance still pending.',submittedParameters={'model':None,'quality':None,'aiInvocation':False,'note':'No model prompt or image parameters were submitted for this local registration/compositing operation. AI prompts and tool receipts remain in the original and repair AI generation records.'})
record['historicalOriginal']={'image':ref(orig),'generationRecord':ref(og),'actualJob':ref(D/'original/jobs/r04_c04.json'),'actualReceipt':ref(D/'original/jobs/r04_c04.receipt.json'),'actualPrompt':ref(D/'original/native/r04_c04.prompt.txt'),'warning':'These historical AI submission records describe the original pre-repair PNG, never the derived adopted image.'}
record['baseAI']={'image':ref(orig),'generationRecord':ref(og),'generatedAt':old['generatedAt']}
record['repairAI']={'image':ref(D/'ai-attempt01/native/r04_c04.png'),'generationRecord':ref(D/'ai-attempt01/native/r04_c04.png.generation.json'),'actualReceipt':ref(D/'attempt01.receipt.json'),'actualJob':ref(D/'attempt01.job.json'),'generatedAt':readj(D/'ai-attempt01/native/r04_c04.png.generation.json')['generatedAt']}
record['processingEvidence']={'processing':ref(V/'processing.json'),'flow':ref(V/'registration-fields.npz'),'mask':ref(V/'ai-patch-mask.png'),'localReview':ref(V/'review.json'),'rootObservation':'Root actually viewed east-row4 and patch-full, confirmed original 9px step / sharp V eliminated. Mild oblique material and bevel value variation remains, without the prior geometric step.'}
record['candidateSource']=ref(candidate)
record['unverifiedReason']='This derived image used no AI call. Underlying original / repair builtin generation model and quality are host-managed and undisclosed; actualModel and actualQuality remain null. Configuration is a target snapshot, not returned model evidence.'
temp=native.with_name(native.name+'.adoption.tmp'); shutil.copy2(candidate,temp); os.replace(temp,native); writej(ng,record)
assert sha(native)==record['sha256']
assert all(sha(p)==before[str(p)] for p in untouched)
proof={'adoptedAt':accepted,'scope':'r09_c08/r04_c04 only','adoptedImage':ref(native),'adoptedGenerationRecord':ref(ng),'candidateSource':ref(candidate),'originalImage':ref(orig),'originalGenerationRecord':ref(og),'rootApproval':'Root explicitly authorized adoption after actual original-pixel views of east-row4 and patch-full.','rootObservation':record['processingEvidence']['rootObservation'],'invariants':{'dimensions':[1254,1254],'nativeCoreCrop':[115,115,1139,1139],'nativeCoreDimensions':[1024,1024],'top115Unchanged':True,'left640Unchanged':True,'right115MatchesExactEastBelowTop115':True,'originalActualJobReceiptAndNativePromptUnmodified':True},'unchangedHistoricalPaths':[{'path':str(p),'sha256':before[str(p)]} for p in untouched],'newLocalReview':ref(V/'review.json'),'processing':ref(V/'processing.json'),'formalAccepted':False,'wholeTileAccepted':False}
writej(D/'adoption-proof.json',proof)
early=T/'early-east-qa'; historic=readj(early/'review.json')
writej(early/'superseded-by-r04c04-repair.json',{'recordedAt':accepted,'historicalReview':ref(early/'review.json'),'historicalManifest':ref(early/'manifest.json'),'historyPreserved':True,'previousNativeSha256':sha(orig),'currentNativeSha256':sha(native),'historicalPixelsSupersededScopes':['east-r04','guide-x3981-r04','internal-y3072-c04','guide-y3187-c04'],'historicalUnchangedScopeCount':10,'note':'Original QA remains a truthful record of prior pixels. Its row4 9px-step finding is resolved by the replacement proof and new actual-view review; do not count affected old views as current candidate validation.','replacementReview':ref(V/'review.json'),'adoptionProof':ref(D/'adoption-proof.json')})
print(json.dumps({'nativeSha256':sha(native),'nativeGenerationSha256':sha(ng),'adoptionProofSha256':sha(D/'adoption-proof.json'),'earlyStatusSha256':sha(early/'superseded-by-r04c04-repair.json'),'allInvariantsVerified':True},indent=2))
