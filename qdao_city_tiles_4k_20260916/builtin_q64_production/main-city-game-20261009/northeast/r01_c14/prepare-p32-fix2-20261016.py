from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(__file__).resolve().parent;Q=T/'qa/quick-20261016'
a=T/'native/p32-v20261016-fix1.png';b=T/'native/p42-v20261016.png';im=Image.open(a).convert('RGB');im.paste(Image.open(b).convert('RGB').crop((0,0,1254,230)),(0,1024));out=Q/'p32-banner-actual-overlap-fix2-context.png';assert not out.exists();im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(Q/'p32-fix2-context-sources.json').write_text(json.dumps({'sources':[{'file':str(a),'sha256':sha(a)},{'file':str(b),'sha256':sha(b)}],'operation':'integer native crop-paste only','replacementROI':[0,1024,1254,1254],'context':str(out),'sha256':sha(out)},indent=2)+'\n')

