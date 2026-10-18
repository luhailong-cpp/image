from pathlib import Path
from PIL import Image
import hashlib,json
b=Path(__file__).resolve().parent
src=b.parents[3]/'parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png'
out=b/'guides/approved-right-plaza-context-20261016-v01.png'
assert src.is_file() and not out.exists()
box=[570,930,635,1025]
im=Image.open(src);im.crop(box).resize((650,950),Image.Resampling.NEAREST).save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
Path(str(out)+'.derivation.json').write_text(json.dumps({'source':str(src),'sourceSha256':sha(src),'sourceCrop':box,'file':str(out),'sha256':sha(out),'operation':'nearest enlarged layout guidance only','gameArt':False,'resampling':True},indent=2)+'\n')
print(out)

