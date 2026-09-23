"""Make upper-body-only reference crops; never actions. Source pixels unchanged."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
from PIL import Image
out=Path(__file__).parent
recovery=out.parents[1]
items=[('identity',recovery/'10-work/references/identity-inspection-1024.png',690),('S01',recovery/'10-generation/S01-v2/raw.png',850),('E09',recovery/'10-generation/E09-v1/raw.png',850),('SW01',recovery/'10-generation/SW01-v2/raw.png',850)]
for name,src,bottom in items:
    dest=out/(name+'-upper-reference.png')
    if dest.exists(): continue
    with Image.open(src) as im:
        im.crop((0,0,im.width,bottom)).save(dest)
        rec={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'recordedAt':datetime.now(timezone.utc).isoformat(),'operation':{'type':'rectangular crop only','box':[0,0,im.width,bottom],'purpose':'upper-body identity/proportion reference, avoids reusing source leg stance','countsAsAction':False,'newAIImage':False},'derivedFrom':{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'generationRecord':str(src)+'.generation.json'},'nativeGeneration':False}
    dest.with_suffix('.png.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
