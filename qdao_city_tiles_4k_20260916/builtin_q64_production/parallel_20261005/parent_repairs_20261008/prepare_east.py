from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib
R=Path(__file__).resolve().parent
P=R/'east-lower'; P.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=json.loads((R.parent/'parent_audit_20261008/tianyong/audit.json').read_text(encoding='utf-8'))
by={x['tileId']:x for x in audit['entries']}
ctx=Image.new('RGB',(1254,1254));parts=[]
for tile,box,dst in [('r09_c08',(3469,1173,4096,2427),(0,0)),('r09_c09',(0,1173,627,2427),(627,0))]:
    e=by[tile];assert sha(e['path'])==e['sha256']
    with Image.open(e['path']) as im:ctx.paste(im.crop(box).convert('RGB'),dst)
    parts.append(dict(tile=tile,source=e,cropLTRB=box,pasteXY=dst))
ctx.save(P/'context.png')
record=dict(file=str(P/'context.png'),sha256=sha(P/'context.png'),createdAt=datetime.now(timezone.utc).isoformat(),
    operation='Native crops concatenated; no resampling.',coordinatesRelativeTo='r09_c08 top-left',tileLocalWindowLTRB=[3469,1173,4723,2427],parts=parts)
(P/'context.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['config.snapshot.json','model-verification.json']:(P/name).write_bytes((R/'west-upper'/name).read_bytes())
print(str(P/'context.png'))
