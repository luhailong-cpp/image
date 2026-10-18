from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
b=Path(__file__).resolve().parent
src=b.parent/'native/p01_03.png'
out=b/'guides/p01_03.approved-crossbar-20261016-v04.guide.png'
assert not out.exists()
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
d.rectangle((75,350,1253,454),fill=(173,175,178))
d.rectangle((174,347,1253,349),fill=(153,151,146))
d.rectangle((174,455,1253,457),fill=(239,235,226))
im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
Path(str(out)+'.derivation.json').write_text(json.dumps({'source':str(src),'sourceSha256':sha(src),'file':str(out),'sha256':sha(out),'operation':'Mechanical GUIDE ONLY overlays approved grey horizontal inlay y350..455 connecting actual native vertical inlay x75..165. Approved layout source is p01_03.layout-only.png and wider approved-right-plaza-context. New model repaint required; guide not final game art.','sourceResampling':False,'gameArt':False},indent=2)+'\n')
print(out)

