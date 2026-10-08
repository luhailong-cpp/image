from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,io
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn/r09_c14')
ROOT=T.parent;R=T/'repairs/west-foliage';E=T/'evidence'
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools/deps'))
import native_assemble as na
import cv2 as cv
sys.stdout.reconfigure(encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
cache={}
def sha(p):
 p=Path(p)
 if p not in cache:cache[p]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[p]
def ref(p):return {'file':str(p),'sha256':sha(p)}
def pngsha(a):
 b=io.BytesIO();Image.fromarray(a).save(b,format='PNG');return hashlib.sha256(b.getvalue()).hexdigest()
P=T/'output/r09_c14-candidate.png';A=T/'output/native-assembly.json'
app=read(R/'application-v9.json');asm=read(A)
assert sha(P)==app['candidate']['sha256']
assert sha(A)==app['sourceHashMigration']['originalAssemblyImmutable']['sha256']
# Rebuild old assembly exclusively in memory from stored native inputs/fields.
layout=na.Layout()
neighbor_pixels={k:np.array(Image.open(v['file']).convert('RGB')) for k,v in asm['neighbors'].items()}
canvas,known,_=na.seed_neighbors(layout,**neighbor_pixels)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
fieldchecks=[]
for p in asm['patches']:
 raw=np.array(Image.open(p['source']['file']).convert('RGB'))
 assert sha(p['source']['file'])==p['source']['sha256']
 assert sha(p['generation']['file'])==p['generation']['sha256']
 for v in p['fields'].values():assert sha(v['file'])==v['sha256']
 owner=np.array(Image.open(p['fields']['mask']['file']))>0
 support=np.array(Image.open(p['fields']['support-mask']['file']))>0
 flow=np.load(p['fields']['flow']['file']);tone=np.load(p['fields']['colorCorrection']['file'])
 aligned=cv.remap(raw,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
 matched=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
 x,y=p['canvasXY'];context=canvas[y:y+1254,x:x+1254]
 assert np.array_equal(support,known[y:y+1254,x:x+1254])
 canvas[y:y+1254,x:x+1254]=np.where(owner[:,:,None],matched,context)
 known[y:y+1254,x:x+1254]=True
 dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1])
 jac=(1+dxu)*(1+dyv)-dyu*dxv
 fieldchecks.append({'id':p['id'],'flowMax':float(np.linalg.norm(flow,axis=2).max()),'colorMaxRGB':np.abs(tone).max((0,1)).tolist(),'jacobianMinimumInOwner':float(jac[owner].min()),'hashesVerified':True})
old=canvas[115:4211,115:4211].copy()
oldsha=pngsha(old);assert oldsha==app['baseCandidateSha256'],oldsha
new=np.array(Image.open(P).convert('RGB'));changed=np.any(old!=new,axis=2)
ys,xs=np.where(changed);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
assert bbox==app['candidateRectLTRB']
assert int(changed.sum())==app['changedPixels']
assert not changed[:,800:].any() and not changed[-320:].any() and not changed[:1085].any()
# Verify original repair crop against reproducible old candidate and immutable old neighbor.
target=np.array(Image.open(R/'edit-target.png').convert('RGB'))
assert np.array_equal(target[:,:320],neighbor_pixels['west'][1050:2304,3776:4096])
assert np.array_equal(target[:,320:],old[1050:2304,:934])
v9=np.array(Image.open(R/'proposed-joint-preview-v9.png').convert('RGB'))
assert np.array_equal(v9[:,:320],target[:,:320])
assert np.array_equal(new[1085:2269,:455],v9[35:1219,320:775])
# Enumerate textual source hash pairs, recording known immutable historical references separately.
errors=[];resolved=[];checks=0;allrecords=[];ai=[]
hist=R/'history-before-v9-application'
oldqa={(str(Path(q['file'])).lower(),q['sha256']) for q in asm['qa']}
historyfiles={str(Path(h['historicalRecordFile'])).lower() for h in app['textHistory']}
historyhashes={h['historicalRecordSha256'] for h in app['textHistory']}
for h in app['textHistory']:
 assert sha(h['historicalRecordFile'])==h['historicalRecordSha256']
oldp43sha='0611c97173ca1f51d3c15cb30153f113a8b4a0286e36c6e3e58a08aed6b4d7ad'
def hashcheck(path,expected,rec,location):
 global checks
 if not isinstance(path,str) or not isinstance(expected,str) or len(expected)!=64:return
 checks+=1;p=Path(path)
 actual=sha(p) if p.is_file() else None
 if actual==expected:return
 reason=None;resolver=None
 if p==P and expected==oldsha:
  reason='historical pre-v9 candidate exactly reconstructed in memory from unchanged native sources and stored fields'
  resolver=str(R/'application-v9.json')
 elif p==T/'native/p43.png' and expected==oldp43sha and sha(T/'repairs/p43-crate/input.png')==expected:
  reason='original p43 AI generation archived by content at repair input before corrected native promotion'
  resolver=str(T/'repairs/p43-crate/input.png')
 elif (str(p).lower(),expected) in oldqa and (str(rec).lower() in historyfiles or sha(rec) in historyhashes or rec.name in ['native-assembly.json','native-assembly-before-repair.json']):
  reason='immutable old assembly/history QA refers to the pre-v9 candidate; QA images regenerated for new hash'
  resolver=str(R/'application-v9.json')
 item={'record':str(rec),'location':location,'file':str(p),'expectedSha256':expected,'actualSha256':actual}
 if reason:resolved.append(dict(item,reason=reason,resolver=resolver))
 else:errors.append(item)
def walk(d,rec,location='$'):
 if isinstance(d,dict):
  for f,h in [('file','sha256'),('sourceOutputPath','sourceOutputSha256'),('prompt','promptSha256'),('historicalRecordFile','historicalRecordSha256')]:
   if f in d and h in d:hashcheck(d[f],d[h],rec,location+'.'+f)
  for k,v in d.items():walk(v,rec,location+'.'+k)
 elif isinstance(d,list):
  for i,v in enumerate(d):walk(v,rec,location+f'[{i}]')
for p in sorted(T.rglob('*.json')):
 if E in p.parents:continue
 if hist in p.parents:continue
 if p.name in ['manifest.json','horizontal-review.json','root-review.json','final-local-review.json']:continue
 d=read(p);allrecords.append(ref(p));walk(d,p)
 if d.get('route')=='builtin' or str(d.get('tool','')).startswith('image_gen'):
  ai.append((p,d))
airows=[];supplements=[]
for p,d in ai:
 prompt=Path(d['prompt']);pt=prompt.read_text(encoding='utf-8-sig').strip()
 submitted=d['submittedParameters']
 assert pt==submitted['prompt'].strip(),str(p)
 callpath=Path(str(prompt).replace('.prompt.txt','.call.json'))
 call=read(callpath)
 expect={k:v for k,v in submitted.items() if k not in ['model','quality']}
 assert call==expect,(str(p),'call differs')
 reqpath=Path(str(prompt).replace('.prompt.txt','.request.json'))
 request=read(reqpath) if reqpath.exists() else None
 if request:
  assert request['submittedParameters']==submitted
  assert request['configSnapshot']==d['configSnapshot']
 assert d['configSnapshot']['model']=='gpt-image-2.5-sunburst'
 assert d['configSnapshot']['quality']=='max'
 assert d['configSnapshot']['verified_on']=='2026-10-04'
 assert submitted['model'] is None and submitted['quality'] is None
 assert d['actualModel'] is None and d['actualQuality'] is None
 assert [str(Path(x['file'])).lower() for x in d['references']]==[str(Path(x)).lower() for x in submitted['referenced_image_paths']]
 assert any(Path(x['file']).name=='04-guild.png' for x in d['references'])
 for x in d['references']:assert sha(x['file'])==x['sha256']
 assert d['evidence']['sourceOutputSha256']==d['sha256']
 assert sha(d['evidence']['sourceOutputPath'])==d['sha256']
 dims=Image.open(d['evidence']['sourceOutputPath']).size
 assert dims==(1254,1254)
 if 'promptSha256' not in d:supplements.append({'record':ref(p),'prompt':ref(prompt),'reason':'Original structure generation metadata has prompt text and call evidence but omits promptSha256; computed here without rewriting immutable records.'})
 airows.append({'record':ref(p),'outputSha256':d['sha256'],'prompt':ref(prompt),'call':ref(callpath),'request':ref(reqpath) if reqpath.exists() else None,'requestMissingButSubmittedParametersRecorded':request is None,'configTargetModel':d['configSnapshot']['model'],'configTargetQuality':d['configSnapshot']['quality'],'actualModel':None,'actualQuality':None,'nativePixels':list(dims),'hostSourceShaVerified':True,'allReferencesAndStyleHashesVerified':True,'callExactlyMatchesSubmittedParameters':True})
result={'checkedAt':datetime.now(timezone.utc).isoformat(),'candidate':ref(P),'auditScope':'current r09_c14 candidate, immutable native assembly, west repair chain and all original AI generation records; no candidate/manifest/root review mutation','status':'draft_pending_mismatch_classification' if errors else 'pass','candidateRebuiltOldSha256':oldsha,'candidateReconstructionInMemoryOnly':True,'noImageWrites':True,'changeBBox':bbox,'changedPixels':int(changed.sum()),'x800AndAfterBitExact':not bool(changed[:,800:].any()),'south320BitExact':not bool(changed[-320:].any()),'north1085BitExact':not bool(changed[:1085].any()),'oldRepairInputExactlyMatchesReconstructedOldCandidate':True,'candidateMergeExactlyMatchesApprovedV9':True,'fixedNeighborLeft320BitExact':True,'nativeFieldChecks':fieldchecks,'jsonRecordsScanned':len(allrecords),'sourceHashPairsChecked':checks,'aiGenerationRecordCount':len(airows),'uniqueAIOutputCount':len(set(x['outputSha256'] for x in airows)),'aiRecords':airows,'metadataSupplements':supplements,'resolvedHistoricalReferences':resolved,'unresolved':errors,'excludedMutableRootOwnedReports':['output/manifest.json','qa/horizontal-review.json','qa/root-review.json','qa/final-local-review.json'],'formalAccepted':False,'clientVerified':False,'navigationVerified':False}
result['lifecycleNotes']=[
 'Generation, proposal and request status fields describe their timestamps. Application-v9 and the current application review establish later selected usage; historical proposal/AI status fields are preserved, not silently rewritten.',
 'The original structure call has exact submitted call/prompt/returned host source evidence but no separately named .request.json; submitted parameters and batch config are preserved in its generation record.',
 'Original structure promptSha256 is supplemented in this audit, without changing its earlier generation record or invalidating recorded reference hashes.',
 'West-foliage repair-native, upper-return-native and leaf-contact-inpaint-native are used in selected v9; upper-inpaint-native and registration proposals v7/v8 are retained rejected production attempts and not applied.',
 'Acquisition records keep actualModel/actualQuality unknown. Batch configuration is a target, not evidence of the service actual model or quality.'
]
result['script']=ref(Path(__file__).resolve())
out=E/'current-provenance-audit.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(out),'status':result['status'],'aiRecords':len(airows),'uniqueAIOutputs':result['uniqueAIOutputCount'],'hashPairs':checks,'historicalResolved':len(resolved),'unresolved':errors},ensure_ascii=False))

