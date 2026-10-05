from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=read(R/'audit/video-axis-S-SE-SW-review.json');assert a['status']=='static_repairs_complete_pending_root_preview'
for f in a['frames']:assert sha(Path(f['file']))==f['sha256']
for n in (7,14):
 p=R/f'run/SE/{n:02}.png';m=read(Path(str(p)+'.generation.json'))
 assert m['sha256']==sha(p) and m['registrationTransform']['globalScale']==1.0 and m['registrationTransform']['inheritedCharacterScale']==.8
 src=R/m['derivedFrom']['file'];assert sha(src)==m['derivedFrom']['sha256']
 native=read(Path(str(src)+'.generation.json'));assert native['actualModel'] is None and native['actualQuality'] is None
 for rel in ('audit/contact-SE-review.json','run/SE/grounding-review.json'):
  f=next(f for f in read(R/rel)['frames'] if f['file']==f'run/SE/{n:02}.png')
  assert f['sha256']==sha(p) and f['nativeSource']['sha256']==sha(src)
print(json.dumps({'checked48':True,'SE_source_and_audit_sync':True,'noExtraScale':True,'status':a['status']}))

