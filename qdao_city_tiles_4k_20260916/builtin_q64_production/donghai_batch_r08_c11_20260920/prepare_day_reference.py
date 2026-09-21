from pathlib import Path
from PIL import Image
import json, hashlib
P=Path(__file__).resolve().parent; PROD=P.parent; T=PROD/'donghai_day/r08_c11'
assert not T.exists()
for d in ('guides','native','prompts','reference'): (T/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
left=PROD/'donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c10-extended-context.png'
base=P/'guides/donghai_day-c11-layout-only.png'
canvas=Image.open(base).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
canvas.paste(Image.open(left).convert('RGB').crop((4096,0,4326,4326)),(0,0))
target=T/'reference/local-layout-input.png';canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(target)
style=T/'reference/left-neighbor-style.png';Image.open(left).convert('RGB').resize((1254,1254),Image.Resampling.LANCZOS).save(style)
inputs=[dict(imageIndex=1,path=str(target),sha256=sha(target),role='exact local composition target; far-left strip inherits selected c10'),dict(imageIndex=2,path=str(style),sha256=sha(style),role='left neighbor appearance and native detail style; not target composition')]
(T/'reference/local-layout-inputs.json').write_text(json.dumps(dict(referenced_image_paths=[e['path'].replace('\\','/') for e in inputs],actualInputReferences=inputs,sourcePaths=[dict(path=str(p),sha256=sha(p)) for p in (base,left)],referenceResamplingOnly=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(str(T))
