from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,subprocess
from PIL import Image
T=Path(__file__).resolve().parent
v,src=sys.argv[1],Path(sys.argv[2])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(src) as im:
 assert im.format=='PNG' and im.size==(1254,1254)
 assert im.mode in ('RGB','RGBA')
 assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
r=T/'records'/(v+'.receipt.json')
receipt={'status':'succeeded_pending_native_seam_review','tool':'image_gen.imagegen',
 'generatedAt':datetime.now(timezone.utc).isoformat(),'originalOutput':str(src),
 'outputSha256':sha(src),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,
 'resizedAfterGeneration':False,'finalArtUpscaled':False,
 'evidence':'Builtin tool output_hint supplied original output path; original dimensions and hash measured. Timestamp records receipt save.'}
with r.open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
subprocess.run([sys.executable,'-X','utf8',str(T.parent/'production_workflow_west_extension_20261016_v2.py'),'ingest',T.name,v,str(src),str(r)],check=True)

