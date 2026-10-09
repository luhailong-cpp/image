from pathlib import Path
import sys,json,shutil,datetime
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import ai_helper as h
import quilt as q
O=h.O;T=O.parent.parent
p=O/'r09_c15-local-candidate-final-v2.png';dest=T/'tiles/r09_c15-candidate-final.png';shutil.copy2(p,dest);h.derived(dest,[p],{'method':'byte-identical final4096 local candidate, no scaling','globalRectXYWH':[57344,32768,4096,4096],'formalAccepted':False,'globalFourCornersPending':True})
q.qa(np.asarray(Image.open(dest).convert('RGB')),'final',dest)
preview=T/'preview-final.png';Image.open(dest).resize((1254,1254),Image.Resampling.LANCZOS).save(preview);h.derived(preview,[dest],{'method':'review-only downscale; never final pixels'})
raw=T/'tiles/r09_c15-candidate.png';a=np.asarray(Image.open(raw).convert('RGB'));b=np.asarray(Image.open(dest).convert('RGB'));mask=Image.fromarray((np.any(a!=b,axis=2)*255).astype('uint8'));mp=T/'tiles/final-changes-from-raw-mask.png';mask.save(mp);h.derived(mp,[raw,dest],{'method':'exact changed pixels'})
native=[];issues=[]
for n in sorted((T/'native').glob('p??.png')):
 rec=json.loads(Path(str(n)+'.generation.json').read_text(encoding='utf8'));assert Image.open(n).size==(1254,1254);assert rec['sha256']==h.sha(n);native.append({'file':str(n),'sha256':h.sha(n),'size':[1254,1254]})
m=json.loads((O/'merge-manifest-final2.json').read_text(encoding='utf8'))
for part in m['tiles']:
 aa=np.asarray(Image.open(part['base']).convert('RGB'));bb=np.asarray(Image.open(part['candidate']).convert('RGB'));mm=np.asarray(Image.open(part['mask']).convert('L'))>0
 part['changedPixels']=int(np.any(aa!=bb,axis=2).sum());part['changedOutsideMask']=int(np.any(aa!=bb,axis=2)[~mm].sum());assert part['changedOutsideMask']==0
records=[];ai=[]
for f in sorted(T.rglob('*.png')):
 rec=Path(str(f)+'.generation.json')
 if not rec.exists():issues.append(str(f))
 else:
  d=json.loads(rec.read_text(encoding='utf-8-sig'));records.append({'file':str(f),'sha256':h.sha(f),'generationRecord':str(rec)})
  if d.get('tool')=='image_gen.imagegen':ai.append(str(f));assert d.get('actualModel') is None and d.get('actualQuality') is None
assert len(native)==16
handoff={'tile':'r09_c15','candidate':str(dest),'sha256':h.sha(dest),'dimensions':[4096,4096],'globalRectXYWH':[57344,32768,4096,4096],'nativeCount':16,'nativeSources':native,'AIImageCount':len(ai),'AIImages':ai,'actualModel':None,'actualQuality':None,'modelEvidence':str(T/'evidence/model-verification.json'),'styleActuallyAttached':'D:/work/image/designs/gameplay-ui/04-guild.png','internalRepair':'230px overlap binary ownership and boundedRGB fields; three native AI geometry/color repairs; no source scaling/warping/blur. Post outlines use narrow nativeAI ownership corridors extending to natural endpoints after rejected rectangular masks.','internalFinal':str(O/'r09_c15-internal-candidate-v8.png'),'westernJoint':m,'changeMaskFromRaw':str(mp),'changeMaskSha256':h.sha(mp),'QA':{'sixLines':'final-x/y1024/2048/3072.png','nineJunctions':str(O/'final-junctions.png'),'visualInspection':'6 lines / 9 junctions initial; changed cliff/posts, 4 western full-size crops, 3 overlap returns, final rail/leaves/bevel native detail reviewed; final6lines9junctions and both post-outline crops reviewed','sourceHashesVerified':True,'outsideWesternMasksIdentical':True,'newImageMissingRecords':issues},'globalFourCornersPending':True,'formalAccepted':False,'integrationInstruction':'Use entire new r09c15 local candidate. Western r09c14 proposal must merge by exact left mask onto root current, never replace entire newer r09c14. Parent owns bottom-left four-corner againstnew r10c14.','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(T/'handoff-final.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf8')
(T/'generation-record-index.json').write_text(json.dumps(records,indent=2),encoding='utf8')
prog=json.loads((T/'progress.json').read_text(encoding='utf8'));prog.update(stage='local_candidate_complete_global_integration_pending',candidate=str(dest),candidateSha256=h.sha(dest),nativeDetailPatches=16,completePixelCandidateTiles=1,formalAccepted=0);(T/'progress.json').write_text(json.dumps(prog,indent=2),encoding='utf8')
print(json.dumps({'candidate':str(dest),'sha256':h.sha(dest),'AI':len(ai),'native':len(native),'missingRecords':issues,'western':m['tiles']},indent=2))


