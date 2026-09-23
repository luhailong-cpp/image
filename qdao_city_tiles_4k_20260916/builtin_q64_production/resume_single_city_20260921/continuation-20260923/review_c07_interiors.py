from pathlib import Path
from PIL import Image
import hashlib, json, datetime

SESSION = Path(__file__).resolve().parent.parent
TILE = SESSION / 'next_tile_r08_c07'
SRC = TILE / 'continuation-20260923/qa-repair-20260923/repaired-v1/r08_c07.png'
EXPECTED = '7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC) == EXPECTED
out = TILE / 'continuation-20260923/qa-repair-20260923/interiors-current'
out.mkdir(exist_ok=False)
im = Image.open(SRC).convert('RGB')
assert im.size == (4096,4096)
items=[]
for r in range(4):
    for c in range(4):
        box = [c*1024,r*1024,(c+1)*1024,(r+1)*1024]
        dst = out / f'r{r+1:02}_c{c+1:02}.png'
        im.crop(box).save(dst)
        items.append({'id':dst.stem,'file':str(dst),'sha256':sha(dst),'boxLTRB':box,'pixelScale':'1:1','reviewStatus':'pending'})
record={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':{'file':str(SRC),'sha256':EXPECTED},'items':items,'formalAccepted':False,'runtimeVerified':False}
(out/'index.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'directory':str(out),'crops':len(items)}))
