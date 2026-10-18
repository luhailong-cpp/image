from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,sys
from PIL import Image
T=Path(__file__).resolve().parent
v='p04_03_v20261014T035620_3cd24fb4'
s=Path('C:/Users/luyua/.codex/generated_images/01a12076-19f9-7f00-8135-01e1b5fb7007/exec-73b80947-8424-4d8d-8f23-4db55fc71e3c.png')
r=T/'records'/(v+'.receipt.json')
assert not r.exists()
im=Image.open(s);assert im.size==(1254,1254) and im.format=='PNG'
d={'status':'succeeded_pending_native_seam_review','tool':'image_gen.imagegen','recoveredAtUtc':datetime.now(timezone.utc).isoformat(),'originalOutput':str(s),'outputSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'finalArtUpscaled':False,'generatedAt':None,'fileModifiedAtUtc':datetime.fromtimestamp(s.stat().st_mtime,timezone.utc).isoformat(),'evidence':'Builtin cell86 returned this PNG output_hint and displayed p04_03 before interruption. Cell no longer available on resume; saved original matched that exact path. No new generation. Generation timestamp/model not returned.'}
with r.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
subprocess.run([sys.executable,str(T.parent/'production_workflow.py'),'ingest',T.name,v,str(s),str(r)],check=True)
