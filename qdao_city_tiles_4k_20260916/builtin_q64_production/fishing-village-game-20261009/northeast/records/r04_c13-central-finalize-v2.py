from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
Z=Path(__file__).resolve().parent.parent
Q=Z/'qa/r04_c13-central-v2'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rf(p):return {'path':str(Path(p).resolve()).replace('\\','/'),'sha256':sha(p)}
def wr(p,d):
 p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(d,indent=2)+'\n')
m=rd(Q/'manifest.json');delta=rd(Q/'central-mechanical-and-delta.json')
old=rd(Z/'qa/r04_c13-central-v1/central-review-49.json')
oldby={Path(x['qa']['path']).name:x for x in old['qaItems']}
changed=set(delta['changedQA']);entries=[]
for e in m['qa']:
 p=Path(e['file']);assert sha(p)==e['sha256'];name=p.name
 if name in changed:
  status='pass';note='Direct native 1:1 review: rectangular foliage/stone imprint removed; neighboring stone courses, foliage, upright and rope meet without blocking geometry or hard rectangular edge.';method='direct_native1to1_view'
 else:
  o=oldby[name];assert sha(p)==o['qa']['sha256'];status=o['status'];note=o['note'];method='reuse_unchanged_QA_hash_and_pinned_sources'
 entries.append({'qa':rf(p),'kind':e['kind'],'status':status,'note':note,'method':method})
assert len(entries)==49
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/central_resume','reviewRole':'owner review; independent reviewer still required','candidate':rf(m['candidate']['file']),'selection':rf(m['selection']['path']),'qaItems':entries,'total':49,'pass':sum(x['status']=='pass' for x in entries),'pending':sum(x['status']=='pending' for x in entries),'changedDirectViews':6,'unchangedHashReused':43,'reuseEvidence':rf(Q/'central-mechanical-and-delta.json'),'geometryBlockingDefects':0,'formalAccepted':False,'visualPassed':False}
wr(Q/'central-review-49.json',review)
ex=rd(Q/'external-native-QA/manifest.json');exitems=[]
for e in ex['qa']:
 assert sha(e['path'])==e['sha256']
 for s in e['sources']:assert sha(s['path'])==s['sha256']
 exitems.append({'name':e['name'],'qa':rf(e['path']),'status':'pass','method':'direct_native1to1_view','note':'Stone courses, roof ribs, rail/deck lines, rope/rocks or water meet at the pinned current source boundary; no blocking break observed.'})
wr(Q/'external-native-QA/central-review.json',{'candidate':rf(m['candidate']['file']),'manifest':rf(Q/'external-native-QA/manifest.json'),'items':exitems,'total':len(exitems),'pass':len(exitems),'pending':0,'north':'not yet generated','eastRemaining':'r3/r4 neighbor absent from pinned snapshot','southwestDiagonal':'not included; diagonal selection not pinned','allExternalEdgesVerified':False,'formalAccepted':False})
handoff={'tile':'r04_c13','candidate':rf(m['candidate']['file']),'selection':rf(m['selection']['path']),'nativeSourceCount':16,'nativePixels':[1254,1254],'candidatePixels':[4096,4096],'nativeCoreBox':[115,115,1139,1139],'independentMechanicalRebuild':rf(Q/'central-mechanical-and-delta.json'),'ownerReview49':rf(Q/'central-review-49.json'),'ownerVisualPass':review['pass'],'ownerVisualPending':review['pending'],'externalReview17':rf(Q/'external-native-QA/central-review.json'),'pending':[{'qa':'h_p23_p33.native-1to1.png','detail':'Outer pillar silhouette now continuous. Fine wood face/grain line changes ~15 px around tile x2618..2648 at y2048. Nonblocking geometry, retained as visual pending.'}],'independentVisualReview':'requested from root; not yet claimed','northPropagation':'Top-row sources available, local pending at y2048 does not reach upper tile boundary. Proceed r03_c13 with pinned selection.','route':'image_gen.imagegen builtin','actualModel':None,'actualQuality':None,'complete4k':False,'formalAccepted':False,'navigationValidated':False,'clientMappingValidated':False,'capacity5000Validated':False}
wr(Z/'records/r04_c13.central-handoff-v2.json',handoff)
print(json.dumps({'candidate':handoff['candidate'],'selection':handoff['selection'],'ownerPass':review['pass'],'ownerPending':review['pending'],'externalPass':len(exitems),'handoff':rf(Z/'records/r04_c13.central-handoff-v2.json')}))
