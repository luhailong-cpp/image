import json,sys,hashlib,shutil
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
rec=Path(sys.argv[1]); r=json.loads(rec.read_text(encoding='utf-8-sig'))
src=Path(r['sourcePath']); dst=root/r['file']
shutil.copy2(src,dst)
im=Image.open(dst)
r.update(sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode,alphaExtrema=list(im.getchannel('A').getextrema()) if im.mode=='RGBA' else None)
for ref in r['references']:
 p=Path(ref['path']); ref['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
rec.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'file':r['file'],'size':im.size,'mode':im.mode,'sha256':r['sha256']},ensure_ascii=False))
