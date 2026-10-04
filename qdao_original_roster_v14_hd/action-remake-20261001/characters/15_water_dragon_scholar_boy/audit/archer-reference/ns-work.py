import json,hashlib
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[2]
m=json.loads((B/'manifest.json').read_text(encoding='utf-8-sig'))
rows=[]
for f in m['frames']:
 if f['action']=='run' and f['direction'] in ('N','S'):
  src=f['derivedFrom'];r=json.loads((B/src['generationRecord']).read_text(encoding='utf-8-sig'))
  p=B/src['path']
  if not p.exists(): p=Path(r['evidence']['hostOutput'])
  rows.append({'direction':f['direction'],'frame':f['frame'],'path':str(p),'generationRecord':src['generationRecord'],'runtime':f.get('file'), 'retainedTransform':f.get('transform')})
(B/'audit/archer-reference/ns-current-native.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False))
