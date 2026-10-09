from pathlib import Path
import json,sys,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
name,src,newprompt=sys.argv[1:]
src=Path(src); old=T/'native'/f'{name}.png'
with Image.open(src) as im:
    assert im.size==(1254,1254)
rec=json.loads(Path(str(old)+'.generation.json').read_text(encoding='utf-8'))
rec['rejectedReason']='Upper blue-gray shadowed masonry incorrectly recolored cream. Replaced before use by any generated neighbor.'
rec['originalPromptText']=(T/'prompts'/f'{name}.txt').read_text(encoding='utf-8')
rec['rejectedImageRetained']=False
d=T/'records/rejected'; d.mkdir(parents=True,exist_ok=True)
(d/f'{name}-{rec["sha256"][:12]}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
assert old.resolve().is_relative_to((T/'native').resolve())
old.unlink()
(T/'prompts'/f'{name}.txt').write_text(newprompt,encoding='utf-8')
sys.path.insert(0,str(T.parent))
import production_r10_c15 as p
p.p.record(name,src)
