from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw

TILE=Path(__file__).resolve().parent.parent
BASE=TILE.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
present=[]; missing=[]
preview=Image.new('RGB',(1024,1024),'#3b4551')
draw=ImageDraw.Draw(preview)
for r in range(1,5):
 for c in range(1,5):
  cell=f'r{r:02d}_c{c:02d}'; p=TILE/'native'/f'{cell}.png'; rec=Path(str(p)+'.generation.json')
  if not p.exists() or not rec.exists():
   missing.append(cell); draw.text(((c-1)*256+12,(r-1)*256+12),f'{cell} pending',fill='white'); continue
  j=read(rec); h=sha(p); assert h==j['sha256']
  with Image.open(p) as im:
   assert im.size==(1254,1254)
   thumb=im.convert('RGB').crop((115,115,1139,1139)).resize((256,256),Image.Resampling.LANCZOS)
  preview.paste(thumb,((c-1)*256,(r-1)*256))
  present.append({'cell':cell,'file':p.as_posix(),'sha256':h,'record':rec.as_posix()})
out=TILE/'in-progress'; out.mkdir(exist_ok=True)
preview.save(out/'native-coverage-preview.png')
state={'updatedAtUtc':now,'tile':'r08_c11','nativePresent':len(present),'nativeRequired':16,'missing':missing,'sources':present,'previewOnly':True,'previewOperation':'1024 cores downsampled to256 for display only; not production','qualifiedComplete4KCandidate':False,'formalAccepted':False}
write(out/'native-coverage.json',state)
for name in ('progress.json','current-work.json'):
 p=BASE/name; j=read(p); j.update(updatedAtUtc=now,currentTile='r08_c11',currentPhase='native_detail_generation',currentNativePresent=len(present),currentNativeRequired=16,nextAction='Complete 16 native pieces, assemble and review internal, west and south seams before candidate selection.'); write(p,j)
print(json.dumps({'nativePresent':len(present),'missing':missing,'candidateCountUnchanged':True}))
