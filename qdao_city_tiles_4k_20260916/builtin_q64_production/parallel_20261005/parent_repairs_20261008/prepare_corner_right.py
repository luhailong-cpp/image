from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;P=R/'corner-right-return';P.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
progress=json.loads((R.parent/'tianyong_festival/progress.json').read_text(encoding='utf-8-sig'))
selection=Path(progress['candidateSet']); entries=json.loads(selection.read_text(encoding='utf-8-sig'))['candidates']
by={e.get('tile',Path(e['file']).stem):e for e in entries}
ctx=Image.new('RGB',(1254,1254));parts=[]
for tile,box,dst in [('r08_c08',(3469,2682,4096,3936),(0,0)),('r08_c09',(0,2682,627,3936),(627,0))]:
    e=by[tile];assert sha(e['file'])==e['sha256']
    with Image.open(e['file']) as im:ctx.paste(im.crop(box).convert('RGB'),dst)
    parts.append(dict(tile=tile,source={'path':e['file'],'sha256':e['sha256'],'generationRecord':e.get('generationRecord'),'selectionSource':str(selection)},cropLTRB=box,pasteXY=dst))
ctx.save(P/'context.png')
(P/'context.png.generation.json').write_text(json.dumps(dict(file=str(P/'context.png'),sha256=sha(P/'context.png'),
    createdAt=datetime.now(timezone.utc).isoformat(),operation='Native crop and concat; no resize.',parts=parts,
    coordinatesRelativeTo='r08_c08 top-left',tileLocalWindowLTRB=[3469,2682,4723,3936]),ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['config.snapshot.json','model-verification.json']:(P/name).write_bytes((R/'west-upper'/name).read_bytes())
print(str(P/'context.png'))
