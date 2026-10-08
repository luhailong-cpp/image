from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08')
cell=sys.argv[1];assert cell in ('r01_c01','r01_c02')
p=T/'ready-cell-qa'/cell/'north.png';o=T/'ready-cell-qa'/cell/'north-detail';o.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(p).convert('RGB');items=[]
boxes=([('orange-rim',[0,196,280,356]),('wood-board',[250,196,640,356]),('stone-post',[600,176,820,376]),('foliage',[800,176,1024,376])] if cell=='r01_c02' else [('left-foliage',[0,176,130,376]),('stone-post',[0,176,310,376]),('stone-rail',[160,176,700,376]),('orange-rim',[650,176,1024,376])])
for name,box in boxes:
 patch=im.crop(box);target=o/(name+'.png');assert not target.exists();patch.save(target)
 items.append({'file':str(target),'sha256':sha(target),'pixels':list(patch.size),'source':str(p),'sourceSha256':sha(p),'sourceBoxXYXY':box,'rawRGBSha256':hashlib.sha256(patch.tobytes()).hexdigest(),'resampling':'none'})
(o/'manifest.json').write_text(json.dumps({'createdAt':datetime.now(timezone.utc).isoformat(),'cell':cell,'purpose':'Actual north-neighbor join focused structure QA, no resampling. In source north.png true junction is y256.','scopes':items,'actuallyViewed':False},indent=2),encoding='utf-8')
print(json.dumps({'checks':len(items),'files':[x['file'] for x in items]}))

