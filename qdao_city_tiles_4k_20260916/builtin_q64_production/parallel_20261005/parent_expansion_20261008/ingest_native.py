from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
R=Path(__file__).resolve().parent
name,host,request=sys.argv[1:4]
O=R/name;O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads(Path(request).read_text(encoding='utf-8-sig'))
if not req.get('configSnapshot'):
    req['configSnapshot']=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
if not req.get('references'):
    req['references']=[{'file':p,'sha256':sha(p)} for p in req['payload']['referenced_image_paths']]
receipt=json.loads((O/'tool-response.json').read_text(encoding='utf-8'))
out=O/'native.png';shutil.copy2(host,out)
with Image.open(out) as im: width,height=im.size;fmt=im.format
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'prompt.txt').write_text(req['payload']['prompt'],encoding='utf-8')
rec=dict(file=str(out),sha256=sha(out),generatedAt=None,observedAt=receipt['ended'],generationWindow={'start':receipt['started'],'end':receipt['ended']},
    width=width,height=height,format=fmt,tool='image_gen.imagegen',route='builtin',configSnapshot=req.get('configSnapshot'),
    submittedParameters={'model':None,'quality':None,'size':None,'transparent_background':False},actualModel=None,actualQuality=None,
    evidence={'toolResponse':str(O/'tool-response.json'),'hostSavedOriginal':host,'copiedByteIdentical':sha(host)==sha(out)},
    unverifiedReason='Host did not disclose exact model, quality or server generation timestamp; clock times record request window.',
    prompt=str(O/'prompt.txt'),references=req.get('references'),referenceRoles=req.get('referenceRoles'),sourceRequest=request)
(O/'native.png.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':rec['sha256'],'size':[width,height]}))
