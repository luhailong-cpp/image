from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(__file__).resolve().parent
a=T/'native/p32-v20261016-fix2.png';b=T/'native/p42-v20261016.png';q=T/'qa/quick-20261016/p32-fix2-south-join.png';im=Image.new('RGB',(1024,384));im.paste(Image.open(a).convert('RGB').crop((115,947,1139,1139)),(0,0));im.paste(Image.open(b).convert('RGB').crop((115,115,1139,307)),(0,192));assert not q.exists();im.save(q)

