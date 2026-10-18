from pathlib import Path
from PIL import Image
import json,hashlib,sys
T=Path(__file__).resolve().parent
sel=json.loads((T/'selected-native.json').read_text(encoding='utf-8-sig'))
for a in sys.argv[1:]:
    p,n=a.split('=',1);f=T/'native'/n;j=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf-8-sig'))
    assert Image.open(f).size==(1254,1254) and hashlib.sha256(f.read_bytes()).hexdigest()==j['sha256']
    sel[p]=n
(T/'selected-native.json').write_text(json.dumps(sel,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':len(sel),'patches':sel}))
