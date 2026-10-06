from pathlib import Path
from PIL import Image
import json,hashlib,datetime,re,collections
R=Path(__file__).resolve().parent;C=R.parent.parent;P=C.parent.parent/'parallel_20261005';O=R/'cleanup_20261005';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
norm=lambda p:str(Path(p).resolve()).replace('\\','/').lower()
stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
refs=collections.defaultdict(list);scanned=[]
files=[C/'current-work.json',R/'current-selection.json']+list(P.rglob('*.json'))
for f in files:
 try:d=json.loads(f.read_text(encoding='utf-8-sig'))
 except (UnicodeDecodeError,json.JSONDecodeError):continue
 scanned.append({'file':str(f),'sha256':sha(f)})
 for v in strings(d):
  if v.lower().endswith('.png'):
   vv=Path(v)
   possibilities=[vv] if vv.is_absolute() else [f.parent/vv,P/vv,C/vv,C.parent.parent.parent/vv]
   for q in possibilities:
    if q.exists():refs[norm(q)].append(str(f))
selection=json.loads((R/'current-selection.json').read_text());finals=selection['sources']
for v in finals.values():assert sha(v['file'])==v['sha256'] and Image.open(v['file']).size==(4096,4096)
current_tree=R/'coupled-v2'
# Restrict candidates to own proven superseded adjacent seam workspace and three rejected size probes.
scope=[R,C/'c07/full-native-attempt',C/'c08/full-native',C/'c09/native2304-probe']
candidates=[];protected=[]
for directory in scope:
 for f in directory.rglob('*.png'):
  if current_tree in f.parents or O in f.parents:continue
  assert C.resolve() in f.resolve().parents
  reasons=refs.get(norm(f),[])
  historical_probe_refs=[]
  if ('full-native' in str(f) or 'native2304-probe' in str(f)) and reasons and all(Path(x).name=='remaining-production-inventory.json' for x in reasons):
   # Inspected inventory directLargerSquareProbesRechecked: historical size verification, not an active source.
   historical_probe_refs=reasons;reasons=[]
  if reasons:
   protected.append({'file':str(f.resolve()),'sha256':sha(f),'reason':'Referenced by parent/current parallel task metadata; conservatively retained even when mention may be historical.','references':sorted(set(reasons))});continue
  rel=str(f.relative_to(C)).replace('\\','/')
  if '/full-native' in rel or '/native2304-probe/' in rel:
   reason='Rejected native size probe or its edit context; returned1254 square could not satisfy requested4096/2304; not merged.'
   evidence=str(C/'c07/full-native-attempt/rejection.json') if rel.startswith('c07/') else str(C/'c08/full-native/rejected-size.native.png.generation.json') if rel.startswith('c08/') else str(C/'c09/native2304-probe/review.json')
  else:
   reason='Superseded native repair/context/composite/QA or six-tile candidate, fully consolidated in current coupled-v2 selection; current QA retained.'
   evidence=str(R/'coupled-v2-bindings.json')
  candidates.append({'absolutePath':str(f.resolve()),'withinBoundary':str(C.resolve()),'sha256':sha(f),'bytes':f.stat().st_size,'pixels':list(Image.open(f).size),'reason':reason,'evidence':evidence,'replacementSelection':str(R/'current-selection.json'),'replacementOutputs':finals,'historicalProbeAuditReferences':historical_probe_refs,'historicalProbeAuditMeaning':'Prior point-in-time size verification retained as text; no active edit input or source checkpoint uses this rejected probe.' if historical_probe_refs else None,'generationRecord':str(f)+'.generation.json' if Path(str(f)+'.generation.json').exists() else None})
manifest={'createdAtUtc':stamp(),'status':'planned_not_deleted','rootBoundary':str(C.resolve()),'authority':'User retention preference and explicit root delegation after parent current-work adoption. No image backups requested.','strictScope':[str(x.resolve()) for x in scope],'excluded':'All other directories, all text records, coupled-v2 final six tiles/currentQA/masks/fields, current parallel references, and host cache.','parentCurrentWork':{'file':str(C/'current-work.json'),'sha256':sha(C/'current-work.json')},'referenceScan':scanned,'currentSelection':{'file':str(R/'current-selection.json'),'sha256':sha(R/'current-selection.json')},'currentArtifactsProtected':[{'file':str(f),'sha256':sha(f)} for f in current_tree.rglob('*') if f.is_file()],'protectedReferencedSources':protected,'deleteCandidates':candidates,'totals':{'files':len(candidates),'bytes':sum(x['bytes'] for x in candidates),'referencedSourcesRetained':len(protected)}}
dump(O/'manifest.json',manifest)
print(json.dumps({'manifest':str(O/'manifest.json'),'totals':manifest['totals'],'protected':[x['file'] for x in protected],'groups':dict(collections.Counter(str(Path(v['absolutePath']).relative_to(C)).replace('\\','/').split('/')[0] for v in candidates))},indent=2))
