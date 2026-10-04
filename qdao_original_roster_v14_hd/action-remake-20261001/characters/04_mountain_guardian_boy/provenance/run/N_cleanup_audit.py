from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];protected=set()
for sc in (ROOT/'frames').rglob('*.generation.json'):
 d=json.loads(sc.read_text(encoding='utf-8-sig'))
 ns=d.get('nativeSource',{}).get('path')
 if ns:protected.add((ROOT/ns).resolve())
 for r in d.get('references',[]):
  if r.get('path'):protected.add(Path(r['path']).resolve())
ev=[(p,p.read_text(encoding='utf-8-sig')) for p in list((ROOT/'provenance/run').glob('N_*.json'))+list((ROOT/'frames/run/N').glob('*.generation.json'))]
cand=[]
for p in (ROOT/'provenance/run').glob('N_*.png'):
 if p.resolve() in protected or 'contact' in p.name:continue
 sha=hashlib.sha256(p.read_bytes()).hexdigest();e=[q.relative_to(ROOT).as_posix() for q,t in ev if sha in t]
 if e:cand.append({'path':p.as_posix(),'sha256':sha,'size':p.stat().st_size,'retainedEvidence':e})
out=ROOT/'provenance/run/N_cleanup_plan.json';out.write_text(json.dumps({'scope':'run/N only','reason':'superseded native images, current nativeSource and current references protected','files':cand},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'eligible':len(cand),'files':[Path(x['path']).name for x in cand]}))
