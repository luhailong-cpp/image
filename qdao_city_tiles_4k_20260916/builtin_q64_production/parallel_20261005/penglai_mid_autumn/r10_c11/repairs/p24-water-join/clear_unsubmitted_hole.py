from pathlib import Path
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parent;p=D/'target.png';q=D/'repair.request.json';r=json.loads(q.read_text(encoding='utf-8'));assert not (D/'host-result.png').exists();im=Image.open(p).convert('RGBA');im.paste((0,0,0,0),(0,185,1139,450));im.save(p);r['references'][0]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();r['transparentHoleRGBZeroed']=True;q.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
