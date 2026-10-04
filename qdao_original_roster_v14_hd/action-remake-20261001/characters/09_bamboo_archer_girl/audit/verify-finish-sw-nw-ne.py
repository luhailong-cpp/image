from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1]
rows=[]
for s in [r/'selection/run-SW.json',r/'selection/run-north.json']:
 for f in json.loads(s.read_text(encoding='utf-8'))['frames']:
  if f.get('direction') in ['SW','NW'] or (f.get('direction')=='NE' and f['frame'] in [9,10]):
   h=hashlib.sha256((r/f['file']).read_bytes()).hexdigest()
   assert h==f['sha256'],f['file']
   g=r/f['generationRecord']
   assert hashlib.sha256(g.read_bytes()).hexdigest()==f['generationRecordSha256'],str(g)
   rows.append(f['file'])
print(len(rows),'selected frames and generation record hashes verified')

