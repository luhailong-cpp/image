import json,sys,hashlib,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
record_path=Path(sys.argv[1])
r=json.loads(record_path.read_text(encoding='utf-8-sig'))
dst=root/r['file']
src=Path(r['sourcePath'])
if src!=dst: shutil.copy2(src,dst)
im=Image.open(dst)
r.update(sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),width=im.width,height=im.height,format=im.format,mode=im.mode,alphaExtrema=list(im.getchannel('A').getextrema()) if im.mode=='RGBA' else None)
record_path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':r['file'],'size':im.size,'mode':im.mode,'sha256':r['sha256']},ensure_ascii=False))

