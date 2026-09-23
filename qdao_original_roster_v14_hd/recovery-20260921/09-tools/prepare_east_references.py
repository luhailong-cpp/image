from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1]
src=B/'09-generation/NE01-v3/raw.png'
out=B/'09-generation/reference-previews/NE-upper-only.png'
if not out.exists():
    im=Image.open(src).convert('RGBA');box=(0,0,1254,880);im.crop(box).save(out)
    out.with_suffix('.source.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'operation':{'crop':box,'purpose':'Upper-body-only equipment reference, exclude walking legs so correct target legs are not overridden. No final frame uses this cropped image.'},'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
