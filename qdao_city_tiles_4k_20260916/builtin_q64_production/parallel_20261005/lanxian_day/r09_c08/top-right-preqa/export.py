from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day')
T=R/'r09_c08';O=T/'top-right-preqa';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(im):return hashlib.sha256(im.tobytes()).hexdigest()
ctx=json.loads((T/'regional/context.json').read_text(encoding='utf-8'))
north=Path(ctx['northCore']['file']);own=T/'native/r01_c04.png'
assert sha(north)==ctx['northCore']['sha256']
rec=json.loads(Path(str(own)+'.generation.json').read_text(encoding='utf-8'));assert sha(own)==rec['sha256']
with Image.open(north) as im: a=im.convert('RGB').crop((3072,3840,4096,4096))
with Image.open(own) as im: b=im.convert('RGB').crop((115,115,1139,371))
board=Image.new('RGB',(1024,512));board.paste(a,(0,0));board.paste(b,(0,256))
out=O/'north-join-c04-1024x512.png'
assert not out.exists();board.save(out)
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'image':str(out),'sha256':sha(out),'rawRgbPixelSha256':rgb(board),'pixels':[1024,512],'operation':'Exact integer crops and paste only; no resize, correction or resampling. Boundary at y256.','sources':[{'file':str(north),'sha256':sha(north),'sourceBoxXYXY':[3072,3840,4096,4096],'destinationBoxXYXY':[0,0,1024,256],'rawRgbPixelSha256':rgb(a)},{'file':str(own),'sha256':sha(own),'sourceBoxXYXY':[115,115,1139,371],'destinationBoxXYXY':[0,256,1024,512],'rawRgbPixelSha256':rgb(b)}],'scope':'Only r09_c08 cell r01_c04 external north join; not whole-tile acceptance.','visuallyReviewed':False,'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest))

