from pathlib import Path
from PIL import Image
import hashlib,json
R=Path(__file__).resolve().parent;S=R.parents[1]
source=S/'continuation_20261004/c09-pair-v2/r08_c09.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='67e10d4bc80a9d4b39a90827e2b06217a3226b54a6f3152168bb206f7136180c'
out=R/'native2304-probe';out.mkdir(exist_ok=True)
with Image.open(source) as im:im.crop((0,0,2304,2304)).save(out/'context-2304.png')
(out/'crop.json').write_text(json.dumps({'source':str(source),'sha256':sha(source),'cropLTRB':[0,0,2304,2304],'nativePixels':[2304,2304],'resized':False,'role':'input reference only'},ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out/'context-2304.png'))
