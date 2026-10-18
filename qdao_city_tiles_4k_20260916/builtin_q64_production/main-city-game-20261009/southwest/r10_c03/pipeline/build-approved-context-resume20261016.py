from pathlib import Path
from PIL import Image
import hashlib,json
B=Path(__file__).resolve().parents[2]
src=B.parents[1]/'parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png'
assert src.exists(),src
dst=B/'r10_c03/pipeline/guides/approved-context-resume20261016.png';assert not dst.exists()
box=[170,670,250,780]
with Image.open(src) as im: im.crop(box).resize((560,770),Image.Resampling.NEAREST).save(dst)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d={'source':str(src),'sourceSha256':sha(src),'cropBox':box,'file':str(dst),'sha256':sha(dst),'resampling':'nearest only for geometry guidance','finalArt':False,'qaOnly':True}
Path(str(dst)+'.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dst)
