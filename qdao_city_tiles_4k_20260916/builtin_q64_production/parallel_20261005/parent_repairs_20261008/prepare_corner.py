from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent; P=R/'corner-left-return';P.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=json.loads((R.parent/'parent_audit_20261008/tianyong/audit.json').read_text(encoding='utf-8'))
by={i['tileId']:i for i in audit['entries']}
ctx=Image.new('RGB',(1254,1254));parts=[]
for tile,box,dst in [('r08_c07',(3469,2743,4096,3997),(0,0)),('r08_c08',(0,2743,627,3997),(627,0))]:
    e=by[tile];assert sha(e['path'])==e['sha256']
    with Image.open(e['path']) as im:ctx.paste(im.crop(box).convert('RGB'),dst)
    parts.append(dict(tile=tile,source=e,cropLTRB=box,pasteXY=dst))
ctx.save(P/'context.png')
(P/'context.png.generation.json').write_text(json.dumps(dict(file=str(P/'context.png'),sha256=sha(P/'context.png'),
    createdAt=datetime.now(timezone.utc).isoformat(),operation='Native crop and concat; no resize.',parts=parts,
    coordinatesRelativeTo='r08_c07 top-left',tileLocalWindowLTRB=[3469,2743,4723,3997]),ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['config.snapshot.json','model-verification.json']:(P/name).write_bytes((R/'west-upper'/name).read_bytes())
print(str(P/'context.png'))
