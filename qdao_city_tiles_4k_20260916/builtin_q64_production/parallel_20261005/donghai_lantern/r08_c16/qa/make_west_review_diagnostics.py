import json, hashlib
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
B = json.loads((ROOT/'qa/west-final-review-binding.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B['candidate']['file']) == B['candidate']['sha256']
im = Image.open(B['candidate']['file']).convert('RGB')
out = ROOT/'repairs/approved-sync/qa/west-review-diagnostics'
out.mkdir(exist_ok=True)
rects = {'upper-timber-and-blue-floor':[0,1780,900,2570], 'blue-panel-patches':[300,2490,900,2960], 'hull-blue-join-returns':[1730,2860,2360,3170], 'water-join-left-return':[2830,930,3050,1370]}
items=[]
for name, rect in rects.items():
    p=out/(name+'.png')
    im.crop(rect).save(p)
    item={'file':str(p),'sha256':sha(p),'tileRectXYXY':rect,'operation':'exact original-pixel crop','pixelScale':1,'resized':False,'source':B['candidate'],'actualVisualReview':'pending'}
    p.with_suffix('.png.generation.json').write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    items.append(item)
(out/'manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(items))
