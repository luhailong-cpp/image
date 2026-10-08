from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
from PIL import Image
D=Path(sys.argv[1]);src=Path(sys.argv[2]);ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');assert not (D/'native.png').exists();assert Image.open(src).size==(1254,1254);shutil.copy2(src,D/'native.png');req=read(D/'request.json')
save(D/'native.png.generation.json',{'operation':'builtin AI outpaint','observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'generatedAt':None,'configTarget':req['configSnapshot'],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'actualReturnedPixels':list(Image.open(src).size),'source':ref(src),'output':ref(D/'native.png'),'references':read(D/'preparation.json')['references'],'nativeScale':1,'noUpscale':True,'formalAccepted':False});print(json.dumps(ref(D/'native.png')))
