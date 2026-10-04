from pathlib import Path
import json,hashlib,datetime,sys
base=Path(__file__).parent.parent.resolve()
allowed={'run-W-work','run-NW-work','run-SW-first-work'}
protected=set()
def collect(v):
 if isinstance(v,dict):
  for x in v.values():collect(x)
 elif isinstance(v,list):
  for x in v:collect(x)
 elif isinstance(v,str) and v.lower().endswith('.png'):
  p=Path(v);p=(p if p.is_absolute() else base/p).resolve()
  if p.is_relative_to(base):protected.add(p)
for name in ['manifest.json','source-selection.json']:
 p=base/name
 if p.exists():collect(json.loads(p.read_text(encoding='utf-8-sig')))
for directory in sys.argv[1:]:
 if directory not in allowed:raise ValueError(directory)
 d=(base/directory).resolve();assert d.parent==base
 selection=json.loads((d/'selection.json').read_text(encoding='utf8'));keep={(base/f).resolve() for f in selection['slots'].values()}
 assert all(p.is_file() for p in keep)
 removed=[]
 for p in d.glob('run-*.png'):
  p=p.resolve();assert p.parent==d and p.is_relative_to(base)
  if p in keep or p in protected:continue
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  removed.append({'file':p.relative_to(base).as_posix(),'sha256':digest,'reason':'Rejected or superseded image; current selected unique native exists; preserve textual provenance only'})
  meta=p.with_name(p.name+'.generation.json')
  if meta.exists():
   m=json.loads(meta.read_text(encoding='utf8'));m['retention']={'imagePresent':False,'disposition':'Rejected/superseded PNG removed by explicit user retention policy','removedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};meta.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
  p.unlink()
 out=d/'retention-cleanup.json'
 previous=json.loads(out.read_text(encoding='utf8')) if out.exists() else {'removed':[]}
 previous['removed']+=removed;previous.update({'scope':str(d),'keptSelected':len(keep),'currentReferencesVerified':True,'time':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 out.write_text(json.dumps(previous,ensure_ascii=False,indent=2),encoding='utf8')
 print(directory,'removed',len(removed),'kept',len(keep))

