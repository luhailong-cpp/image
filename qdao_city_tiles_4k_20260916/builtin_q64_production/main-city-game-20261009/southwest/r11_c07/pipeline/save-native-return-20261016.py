import json,sys,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parents[2]
d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
assert d['tile'].startswith('r') and d['tile'].endswith(('c07','c08'))
t=B/d['tile']
src=Path(d['sourceOutputPath'])
assert src.is_file()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
dest=t/'pipeline'/'returned-originals'/(d['patch']+'.'+d['attempt']+'.png')
dest.parent.mkdir(parents=True,exist_ok=True)
assert not dest.exists()
shutil.copy2(src,dest)
assert sha(src)==sha(dest)
with Image.open(dest) as im:
 d.update(nativePixels=list(im.size),format=im.format,mode=im.mode,opaque=im.mode!='RGBA' or im.getextrema()[3]==(255,255))
d.update(tool='image_gen.imagegen',status='returned_image',recordedAtUtc=datetime.now(timezone.utc).isoformat(),sourceOutputSha256=sha(src),savedUnmodifiedOriginal=str(dest),savedUnmodifiedOriginalSha256=sha(dest),actualModel=None,actualQuality=None,paidApiUsed=False,resizedAfterGeneration=False,internalAccepted=False,formalAccepted=False)
d['requestSha256']=sha(Path(d['request']))
out=t/'pipeline'/'receipts'/(d['patch']+'.'+d['attempt']+'.receipt.json')
assert not out.exists()
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':str(out),'saved':str(dest),'sha256':sha(dest),'size':d['nativePixels']},ensure_ascii=False))
