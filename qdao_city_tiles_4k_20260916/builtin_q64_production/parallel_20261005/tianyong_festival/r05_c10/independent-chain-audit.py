from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
B=Path(__file__).parent
R=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
cache={}
def H(p):
 p=Path(p)
 if str(p) not in cache:cache[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[str(p)]
def ref(p):return {'file':str(p),'sha256':H(p)}
def refs(o):
 if isinstance(o,dict):
  if 'file' in o and 'sha256' in o:yield o
  for v in o.values():yield from refs(v)
 elif isinstance(o,list):
  for v in o:yield from refs(v)
def verify_refs(o):
 a=list(refs(o))
 for r in a:assert H(r['file'])==r['sha256'],r
 return len(a)
def A(p):return np.array(Image.open(p).convert('RGBA'))
cp=R(B/'local-source-checkpoint.json')
verify_refs(cp)
cur=np.zeros((4096,4096,4),dtype=np.uint8)
bot=None
prev=None
entries=[]
ai={}
notes=[]
findings=[]
for row in [4,3,2,1]:
 for col in ([4,3,2,1] if row in [4,2] else [1,2,3,4]):
  D=B/f'r{row:02}_c{col:02}-v1'
  req=R(D/'request.json');F=D/req.get('selectedFinalDirectory','final-v1')
  mp=F/'manifest.json';m=R(mp);verify_refs(m)
  assert m['requiresPriorManifest']==prev
  asm=R(m['assembly']['file']);verify_refs(asm)
  assert asm['nativeScale']==1 and asm['noUpscale'] and not asm['registrationApplied'] and not asm['toneCorrectionApplied']
  assert asm['actualModel'] is None and asm['actualQuality'] is None
  joined=A(m['joined']['file']);wx,wy,wr,wb=m['windowTileLocalLTRB']
  assert joined.shape[:2]==(wb-wy,wr-wx)
  assert m['windowGlobalLTRB']==[wx+36864,wy+16384,wr+36864,wb+16384]
  before=cur.copy()
  if bot is not None:botbefore=bot.copy()
  else:botbefore=None
  own=np.zeros((4096,4096),bool);bown=own.copy()
  crop_entries=[]
  for p in m['patches']:
   crop=p['cropFromJoinedLTRB'];l,t,r,b=p['destinationTileLTRB'];src=p['requiredPriorSource'];asset=A(p['asset']['file'])
   assert asset.shape==(b-t,r-l,4)
   assert np.array_equal(asset,joined[crop[1]:crop[3],crop[0]:crop[2]])
   destGlobal=[l+36864,t+(16384 if p['destinationTile']=='r05_c10' else 20480),r+36864,b+(16384 if p['destinationTile']=='r05_c10' else 20480)]
   sourceGlobal=[crop[0]+wx+36864,crop[1]+wy+16384,crop[2]+wx+36864,crop[3]+wy+16384]
   assert sourceGlobal==destGlobal,(str(mp),p['name'],sourceGlobal,destGlobal)
   if p['destinationTile']=='r05_c10':target=cur;mask=own
   else:
    assert p['destinationTile']=='r06_c10'
    if bot is None:bot=A(src['file']);botbefore=bot.copy()
    target=bot;mask=bown
   if src:assert np.array_equal(target[t:b,l:r],A(src['file'])[t:b,l:r])
   else:assert np.all(target[t:b,l:r,3]==0)
   assert np.all(asset[:,:,3]==255)
   target[t:b,l:r]=asset;mask[t:b,l:r]=True
   crop_entries.append({'name':p['name'],'destinationTile':p['destinationTile'],'destinationTileLTRB':[l,t,r,b],'cropFromJoinedLTRB':crop,'exactNativeCrop':True,'globalCoordinatesMatch':True})
  assert np.array_equal(cur,A(F/'r05_c10-fragment.png'))
  assert np.array_equal(before[~own],cur[~own])
  if row==4:
   assert np.array_equal(bot,A(F/'r06_c10-coupled.png'))
   assert np.array_equal(botbefore[~bown],bot[~bown])
  # All selected assembly native AI sources plus primary source must have native generation records.
  nat={str(D/'native.png')}
  nat.update(r['file'] for r in refs(asm) if Path(r['file']).name=='native.png')
  for n in nat:
   gp=Path(n+'.generation.json');g=R(gp);verify_refs(g)
   for k in ['actualSubmittedModel','actualSubmittedQuality','actualReturnedModel','actualReturnedQuality']:
    assert k in g and g[k] is None,(str(gp),k)
   assert g['actualReturnedPixels']==[1254,1254]
   assert tuple(Image.open(n).size)==(1254,1254)
   assert g['output']==ref(n)
   assert g['configTarget']['model']=='gpt-image-2.5-sunburst' and g['configTarget']['quality']=='max'
   if not any(k in g for k in ['observedCompletionAtUtc','utc','observedAtUtc','completedAtUtc','createdAtUtc']):
    if not any(x.get('record')==str(gp) for x in findings):findings.append({'kind':'missing per-image timestamp','record':str(gp)})
   # Nested preparation/request references preserve actual auxiliary-image ancestry.
   for k in ['preparation','request']:
    if k in g and isinstance(g[k],dict) and 'file' in g[k]:
     verify_refs(R(g[k]['file']))
   ai[n]={'native':ref(n),'generationRecord':ref(gp),'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'nativePixels':[1254,1254]}
  if D.name in ['r02_c03-v1','r03_c03-v1']:
   end=1700 if D.name=='r02_c03-v1' else 1460
   bp=next(p for p in m['patches'] if p['name']=='bottom-return')
   assert bp['cropFromJoinedLTRB'][3]==end
   prior=A(bp['requiredPriorSource']['file'])
   assert np.array_equal(joined[end:,0:1200],prior[wy+end:wb,wx:wx+1200]),D.name+' tail mismatch'
   # Tail plus right outside must be carried without cropping off changed content.
   assert np.array_equal(joined[end:,:],prior[wy+end:wb,wx:wr]),D.name+' full tail mismatch'
   notes.append({'assembly':m['assembly'],'legacyBaseStageField':'contextExactBeyond1200=true','clarification':'Field inherited from base 1254 composite; final extended assembly is governed by native repair source, placement, ownership mask, explicit final tail boundary and manifest. Independent pixel proof below checks final tail.','finalTailExactFromMainY':end})
  if D.name=='r04_c01-v1':
   bp=next(p for p in m['patches'] if p['destinationTile']=='r06_c10')
   assert bp['destinationTileLTRB']==[0,0,1139,1045]
   assert bp['cropFromJoinedLTRB']==[115,1139,1254,2184]
   prior=A(bp['requiredPriorSource']['file'])
   assert np.array_equal(bot[1045:],prior[1045:])
   assert np.array_equal(bot[:,1139:],prior[:,1139:])
   verify_refs(R(F/'expanded-return-proof.json'))
  prev=ref(mp)
  entries.append({'patch':D.name,'selectedFinalDirectory':F.name,'manifest':prev,'joined':m['joined'],'coveragePixels':int((cur[:,:,3]==255).sum()),'patches':crop_entries,'priorROIsExact':True,'candidateReconstructionExact':True,'outsideOwnedRectanglesUnchanged':True})
assert np.all(cur[:,:,3]==255) and np.array_equal(cur,A(cp['fragment']['file']))
assert np.array_equal(bot,A(cp['coupledBottom']['file']))
assert cp['manifest']==prev and cp['coveragePixels']==16777216
add=R(B/'r02_c04-v1/pending-review-addendum.json');verify_refs(add)
assert add['openInternalFindings']==[] and add['status'].startswith('closed')
assert add['resolutionManifest']==ref(B/'r02_c03-v1/final-v2/manifest.json')
out={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'auditor':'/root/continue_north/audit05','scope':'Independent read-only metadata, provenance, native crop, chain and pixel audit. No visual QA duplicated; existing root/current/source state not modified.','passed':True,'tile':'r05_c10','localSourceCheckpoint':ref(B/'local-source-checkpoint.json'),'finalFragment':cp['fragment'],'finalCoupled06':cp['coupledBottom'],'manifestCount':len(entries),'nativeAIGenerationRecordsVerified':len(ai),'fullOpaquePixelCoverage':16777216,'nativeScale':1,'allManifestAssetHashesVerified':True,'allSelectedAssemblyReferencesHashVerified':True,'allAssetsExactJoinedCrops':True,'allWorldCoordinatesMatch':True,'sequentialPixelReconstructionExact':True,'allPriorROIsExact':True,'allOutsideOwnedRectanglesUnchanged':True,'modelQualityNotClaimedAsConfirmed':True,'extendedReturnsNotCropped':{'r04_c01_r06BottomEndY':1045,'r03_c03_mainBottomEndY':1460,'r02_c03_mainBottomEndY':1700},'bannerFindingClosure':ref(B/'r02_c04-v1/pending-review-addendum.json'),'entries':entries,'nativeAISources':list(ai.values()),'metadataClarifications':notes,'openAuditFindings':[],'visualAcceptance':'Not assessed here; parent performs native-panel QA.','formalAccepted':False,'rootPublished':False}
p=B/'independent-full-chain-audit.json'
out['passed']=not findings
out['openAuditFindings']=findings
assert not p.exists()
p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'audit':ref(p),'manifestCount':len(entries),'nativeAIGenerationRecordsVerified':len(ai),'uniqueReferencedFilesHashVerified':len(cache),'final':cp['fragment']}))

