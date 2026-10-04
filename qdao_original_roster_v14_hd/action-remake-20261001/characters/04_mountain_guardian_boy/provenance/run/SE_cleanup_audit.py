from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
protected=set()
for sc in (ROOT/'frames').rglob('*.generation.json'):
 d=json.loads(sc.read_text(encoding='utf-8-sig'))
 ns=d.get('nativeSource',{}).get('path')
 if ns: protected.add((ROOT/ns).resolve())
 for r in d.get('references',[]):
  if r.get('path'):protected.add(Path(r['path']).resolve())
sources=list((ROOT/'provenance'/'cast').glob('*.png'))+list((ROOT/'provenance'/'run').glob('SE_*.png'))
evidence=[]
for p in list((ROOT/'provenance'/'cast').glob('*.json'))+list((ROOT/'provenance'/'run').glob('SE_*.json'))+list((ROOT/'frames'/'cast').rglob('*.generation.json'))+list((ROOT/'frames'/'run'/'SE').glob('*.generation.json')):
 evidence.append((p,p.read_text(encoding='utf-8-sig')))
candidates=[]
for p in sources:
 if p.resolve() in protected or 'contact' in p.name:continue
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 es=[q.relative_to(ROOT).as_posix() for q,t in evidence if sha in t]
 if es:candidates.append({'path':p.as_posix(),'relativePath':p.relative_to(ROOT).as_posix(),'sha256':sha,'size':p.stat().st_size,'retainedEvidence':es})
out=ROOT/'provenance'/'run'/'SE_cast_cleanup_plan.json'
out.write_text(json.dumps({'scope':'cast and SE only','reason':'superseded images not current nativeSource or current image input; generation prose retained','protectedCurrentSourcesAndInputs':len(protected),'files':candidates},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'deleteEligible':len(candidates),'files':[x['relativePath'] for x in candidates]},ensure_ascii=False))
