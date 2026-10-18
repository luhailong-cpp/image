from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent/'repairs/local-seams-20261016-v1';key,source=sys.argv[1:3];source=Path(source);dst=R/(key+'-native.png');assert not dst.exists()
im=Image.open(source);assert im.size==(1254,1254) and im.format=='PNG'
if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
shutil.copyfile(source,dst)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'id':key,'status':'succeeded_pending_local_visual_QA','tool':'image_gen.imagegen','route':'builtin','receivedAt':datetime.now(timezone.utc).isoformat(),'originalOutputPath':str(source),'path':str(dst),'sha256':sha(dst),'originalSha256':sha(source),'actualSize':list(im.size),'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'request':str(R/(key+'.request.json')),'requestSha256':sha(R/(key+'.request.json')),'formalAccepted':False}
(R/(key+'.receipt.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
