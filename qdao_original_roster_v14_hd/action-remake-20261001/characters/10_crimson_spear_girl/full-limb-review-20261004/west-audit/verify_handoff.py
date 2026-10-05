from pathlib import Path
import hashlib,json,collections
r=Path(__file__).resolve().parents[2];a=r/'full-limb-review-20261004/west-audit';audit=json.loads((a/'audit.json').read_text(encoding='utf-8-sig'))
print('audit frames',len(audit['frames']),'unique slots',len({x['slot'] for x in audit['frames']}))
print('audit status',dict(collections.Counter(x['status'] for x in audit['frames'])))
missing=[];mismatches=[]
for row in audit['frames']:
 p=r/row['file']
 if not p.exists():missing.append(row['slot'])
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:mismatches.append(row['slot'])
print('pre-repair snapshot currently changed slots',mismatches,'missing',missing)
h=json.loads((a/'NW09-10-selection-handoff.json').read_text(encoding='utf-8'));assert len(h['slots'])==2
for row in h['reviews']:
 p=r/row['file'];assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 print(row['slot'],row['file'],row['sha256'])
