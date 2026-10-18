from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
d=Path(sys.argv[1]);s=Path(sys.argv[2]);h=hashlib.sha256(s.read_bytes()).hexdigest();p=d/('actual-native-'+h[:16]+'.png')
assert Image.open(s).size==(1254,1254) and not p.exists()
shutil.copy2(s,p)
with (d/'receipt.json').open('x',encoding='utf-8') as f:json.dump({'savedAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'originalOutput':str(s),'native':str(p),'sha256':h,'actualSize':[1254,1254],'outputHintObserved':True,'byteCopyExact':s.read_bytes()==p.read_bytes(),'resized':False,'formalAccepted':False},f,indent=2)
print(json.dumps({'native':str(p),'sha256':h}))
