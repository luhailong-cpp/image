from pathlib import Path
import sys,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent
direction,a,b,prefix=sys.argv[1:]
A=Image.open(a).convert('RGB').crop((115,115,1139,1139));C=Image.open(b).convert('RGB').crop((115,115,1139,1139))
if direction=='horizontal':
    out=Image.new('RGB',(320,1024));out.paste(A.crop((864,0,1024,1024)),(0,0));out.paste(C.crop((0,0,160,1024)),(160,0))
elif direction=='vertical':
    out=Image.new('RGB',(1024,320));out.paste(A.crop((0,864,1024,1024)),(0,0));out.paste(C.crop((0,0,1024,160)),(0,160))
else:raise ValueError(direction)
path=Path(prefix+'.png');assert path.resolve().is_relative_to(B) and not path.exists();path.parent.mkdir(parents=True,exist_ok=True);out.save(path)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
data={'file':str(path),'direction':direction,'firstSource':a,'firstSHA256':sha(a),'secondSource':b,'secondSHA256':sha(b),'method':'Exact native core crops juxtaposed at 100%; no scaling/blending','visualVerdict':'PENDING','formalAccepted':False}
path.with_suffix('.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data))
