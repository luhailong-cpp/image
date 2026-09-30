from pathlib import Path
import json
p=Path(__file__).resolve().parent/'selection.json'
d=json.loads(p.read_text(encoding='utf-8'))
for slot, bad in [('NE14','NE14-v1'),('NE15','NE15-v2'),('NE16','NE16-v1')]:
    if d.get(slot,{}).get('archive')==bad: del d[slot]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
