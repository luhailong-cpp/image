import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
checked={}
def check(r):
 p=Path(r['path']);k=p.as_posix()
 if k not in checked:checked[k]=ref(p)['sha256']
 assert checked[k]==r['sha256'],k
 return p
def rgb(r):return np.asarray(Image.open(check(r)).convert('RGB')).copy()
def refs(x):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str):check(x)
  for k,v in x.items():
   if k not in ['hardMaskPaths','hardSeamPathIn230Overlap']:refs(v)
 elif isinstance(x,list):
  for v in x:refs(v)
def write(name,d):
 p=Q/name
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
 return ref(p)
def box(a,b):
 y,x=np.where(np.any(a!=b,axis=2))
 return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
v=read(Q/'pair-r13c05-r14c05-v3-trace.json')
h=read(Q/'pair-r14c05-r14c06-v3-trace.json')
va=read(Q/'pair-r13c05-r14c05-v3-art-audit-v1.json')
ha=read(Q/'pair-r14c05-r14c06-v2-art-audit-v1.json')
oldh=read(Q/'pair-r14c05-r14c06-v2-trace.json')
for x in [v,h,va,ha,oldh]:refs(x)
assert va['trace']==ref(Q/'pair-r13c05-r14c05-v3-trace.json')
assert va['status']=='passed_native_pair_visual_qa'
assert ha['status']=='passed_native_pair_visual_qa'
base=read(check(v['basePairTrace']))
replay=rgb(base['context'])
receipts=[]
for a in v['repairs']:
 l,t,r,b=a['contextBox'];mask=np.load(check(a['mask'])).astype(bool);native=rgb(a['repair'])
 assert native.shape==(1254,1254,3)
 replay[t:b,l:r][mask]=native[mask]
 gen=read(check(a['generationRecord']))
 assert gen['sha256']==a['repair']['sha256'] and gen['width']==1254 and gen['height']==1254
 assert gen['actualModel'] is None
 rp=Path(gen['evidence']['receipt']);receipt=read(rp);default=Path(receipt['sourceDefaultPath'])
 if default.exists():assert ref(default)['sha256']==a['repair']['sha256']
 assert Path(gen['prompt']).exists()
 receipts.append({'id':a['id'],'native':a['repair'],'generationRecord':a['generationRecord'],'receipt':ref(rp),'defaultSourcePresent':default.exists(),'actualModel':None})
assert np.array_equal(replay,rgb(v['context']))
vimgs={}
for a in v['tiles']:
 l,t,r,b=a['contextBox'];ctx=rgb(a['context']);cand=rgb(a['candidate'])
 assert ctx.shape==(4326,4326,3) and cand.shape==(4096,4096,3)
 assert np.array_equal(ctx,replay[t:b,l:r]) and np.array_equal(cand,ctx[115:4211,115:4211])
 vimgs[a['tile']]=ctx
hreplay=rgb(oldh['context']);hreplay[:,:4326]=vimgs['r14_c05']
assert np.array_equal(hreplay,rgb(h['context']))
himgs={}
for a in h['tiles']:
 l,t,r,b=a['contextBox'];ctx=rgb(a['context']);cand=rgb(a['candidate'])
 assert ctx.shape==(4326,4326,3) and cand.shape==(4096,4096,3)
 assert np.array_equal(ctx,hreplay[t:b,l:r]) and np.array_equal(cand,ctx[115:4211,115:4211])
 himgs[a['tile']]=ctx
assert np.array_equal(himgs['r14_c05'],vimgs['r14_c05'])
assert np.array_equal(himgs['r14_c05'][:,-230:],himgs['r14_c06'][:,:230])
stable13=rgb(v['inputs'][0]['context'])
assert np.array_equal(vimgs['r13_c05'][:230],stable13[:230])
east=rgb(ref(Q/'pair-r14c06-r14c07-v3-r14_c06-context-native.png'))
assert np.array_equal(himgs['r14_c06'][:,-230:],east[:,-230:])
reused=[]
for i in range(1,5):
 assert h['qa'][i]['sha256']==oldh['qa'][i]['sha256']
 assert np.array_equal(rgb(h['qa'][i]),rgb(oldh['qa'][i]))
 reused.append(h['qa'][i])
for a in h['qa']:
 l,t,r,b=a['contextBox'];assert np.array_equal(rgb(a),hreplay[t:b,l:r])
l,t,r,b=h['cornerQa']['contextBox']
assert np.array_equal(rgb(h['cornerQa']['image']),hreplay[t:b,l:r])
unpassed={'id':'r14c06-north-halo-water-cut','status':'not_passed_pending_reserved_neighbor','tile':'r14_c06','nativeContextApproxIssueBox':[200,0,260,80],'pairContextApproxIssueBox':[4296,0,4356,80],'globalApproxIssueBox':[20565,53133,20625,53213],'description':'Upper halo shows a vertical water/foam contrast discontinuity near context x230, y0..60; conservative issue box extends to y80. It is outside the exported core starting at y115. Must be resolved with r13_c06 north neighbor; do not claim full-map or complete halo pass.','coreAffected':False,'reservedNeighbor':'r13_c06','ownerWorker':'01a1338b-8e38-7080-b600-1e3781939ec2','evidence':h['cornerQa']['image']}
validation={'sourceHashesChecked':len(checked),'verticalNativeReplayExact':True,'horizontalPropagationExact':True,'allCoreCropsExact':True,'allSourceDimensionsMatch':True,'c05c06Shared230Exact':True,'r13c05North230Preserved':True,'r14c06East230Preserved':True,'noResampling':True,'noBlending':True,'noProceduralPainting':True}
now=datetime.now(timezone.utc).isoformat()
ver=write('sea-resume-1017-verification-v1.json',{'schemaVersion':1,'createdAtUtc':now,'status':'passed_source_verification','validation':validation,'sourceRefsVerified':[{'path':p,'sha256':s} for p,s in checked.items()],'generatedRepairs':receipts,'resumedWithoutNewGeneration':True})
ha_new=write('pair-r14c05-r14c06-v3-art-audit-v1.json',{'schemaVersion':1,'createdAtUtc':now,'status':'art_passed','scope':'Native 4096 cores and c05/c06 shared edge; external north halo explicitly not passed.','trace':ref(Q/'pair-r14c05-r14c06-v3-trace.json'),'freshNativeWindowsViewed':[h['qa'][0],h['cornerQa']['image']],'unchangedQaReused':reused,'reusedAudit':ref(Q/'pair-r14c05-r14c06-v2-art-audit-v1.json'),'sharedWindowsPassed':5,'findings':['Updated core-edge section shows connected rounded rocks, foam and water without a visible seam.','Four other shared windows exactly retain previously passed hashes.','The top halo has a water contrast cut requiring the reserved north neighbor; it is outside y115 core start and remains not passed.'],'validation':validation,'unpassedExternalIssues':[unpassed],'formalAcceptance':False,'wholeMapAccepted':False})
tiles=[v['tiles'][0],h['tiles'][0],h['tiles'][1]]
tr=write('sea-r13r14c05-c06-export-trace-1017-v1.json',{'schemaVersion':1,'createdAtUtc':now,'status':'reviewed_native_core_candidates','tiles':tiles,'provenance':[ref(Q/'pair-r13c05-r14c05-v3-trace.json'),ref(Q/'pair-r14c05-r14c06-v3-trace.json')],'verification':ver,'sourcePixelIdentity':True,'nativePixelsResampled':False,'formalAcceptance':False,'unpassedExternalIssues':[unpassed]})
aud=write('sea-r13r14c05-c06-export-audit-1017-v1.json',{'schemaVersion':1,'createdAtUtc':now,'status':'art_passed','scope':'4096 native core art candidates and inspected c05 north/south + c05/c06 joins; not complete external halo or full-map acceptance.','trace':tr,'reusedVerticalAudit':ref(Q/'pair-r13c05-r14c05-v3-art-audit-v1.json'),'horizontalAudit':ha_new,'verification':ver,'validation':validation,'reviewedTiles':[a['tile'] for a in tiles],'unpassedExternalIssues':[unpassed],'pendingOtherExternalJoins':['r13_c05 east to r13_c06','r13_c05 west to r13_c04','r14_c05 west to r14_c04','r14_c06 north to r13_c06'],'formalAcceptance':False,'wholeMapAccepted':False})
handoff=write('sea-resume-1017-handoff-v1.json',{'schemaVersion':1,'createdAtUtc':now,'status':'ready_for_root_versioned_core_export_with_explicit_external_issue','exportTrace':tr,'exportAudit':aud,'tiles':tiles,'unpassedExternalIssues':[unpassed],'rootOnlyMutation':['art-delivery-index.json','progress.json','current-tile-ledger.json','tiles/ exports'],'gitModified':False,'newGenerationCount':0})
print(json.dumps({'trace':tr,'audit':aud,'handoff':handoff,'validation':validation,'tiles':[{'tile':a['tile'],'candidate':a['candidate'],'context':a['context']} for a in tiles]}))

