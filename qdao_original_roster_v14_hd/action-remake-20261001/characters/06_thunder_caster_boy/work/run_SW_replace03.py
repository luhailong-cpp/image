import json,hashlib,shutil
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[1]
out=B/'runtime/run/SW/03.png'
source=B/'work/run_SW_03_v3.png'
rec=source.with_name(source.name+'.generation.json')
r=json.loads(rec.read_text(encoding='utf-8'))
assert source.resolve().is_relative_to(B.resolve())
assert Image.open(source).size==(1254,1254)
old=out.with_name(out.name+'.generation.json')
shutil.copy2(old,B/'records/run_SW_03_v2_runtime_superseded.json')
Image.open(source).resize((1024,1024),Image.Resampling.LANCZOS).save(out)
d=json.loads(old.read_text(encoding='utf-8'))
d.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),derivedFrom=[{'file':r['file'],'sha256':r['sha256'],'generationRecord':rec.relative_to(B).as_posix()}],native=r['native'],visualReview=r['visualReview'],generatedAt=r['generatedAt'])
old.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r.update(exported=True,exportPath=out.relative_to(B).as_posix())
rec.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SW03 replaced with v3')

