from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
r=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent/'inputs'
out.mkdir(exist_ok=True)
for n in (11,12):
    src=r/f'runtime/run/NW/{n:02d}.png'
    dest=out/f'original{n:02d}-1254.png'
    Image.open(src).convert('RGBA').resize((1254,1254),Image.Resampling.LANCZOS).save(dest)
    meta={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'createdAt':datetime.now(timezone.utc).isoformat(),'operation':'Full canvas uniform resize 1024 to 1254; no translation/crop/anatomy edit; tool edit target retains original runtime composition','derivedFrom':[{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'generationRecord':str(src)+'.generation.json'}]}
    Path(str(dest)+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
    print(dest)
