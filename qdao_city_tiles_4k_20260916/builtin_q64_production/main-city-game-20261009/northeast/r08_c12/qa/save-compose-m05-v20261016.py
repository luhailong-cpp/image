from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');src=Path(r'C:\Users\luyua\.codex\generated_images\01a142ed-202a-7243-b7b1-095dbd534429\exec-0092c967-a492-494c-bb5b-02ae01ff206c.png');name='m05-joints-v20261016'
out=p/'native/repairs'/f'{name}.png';out.parent.mkdir(exist_ok=True);assert not out.exists()
assert Image.open(src).size==(1254,1254);shutil.copy2(src,out)
h=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
req=json.loads((p/'prompts'/f'{name}.request.json').read_text(encoding='utf-8-sig'))
record={'createdAt':datetime.now(timezone.utc).isoformat(),'sourceOutputPath':str(src),'workspaceFile':str(out),'sha256':h(out),'nativeSize':[1254,1254],'tool':'image_gen','route':'builtin','actualModel':None,'actualQuality':None,'request':str(p/'prompts'/f'{name}.request.json'),'receipt':str(p/'receipts'/f'{name}.receipt.json'),'references':[{'file':f,'sha256':h(f)} for f in req['referenced_image_paths']],'editTargetOriginTile':[397,397],'originalsPreserved':True}
Path(str(out)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=p/'qa/repair-m05-20261016';base=p/'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png'
im=Image.open(base).convert('RGBA')
roi=[115,115,1139,1139];dest=[512,512,1536,1536]
im.paste(Image.open(out).crop(roi),(512,512))
cand=p/'candidates/r08_c12.m05-v20261016.png';assert not cand.exists();im.save(cand)
im.crop((397,397,1651,1651)).save(q/'m05-composed-v1.png')
for k,b in {'top':[352,352,1696,672],'bottom':[352,1376,1696,1696],'left':[352,672,672,1376],'right':[1376,672,1696,1376]}.items():im.crop(b).save(q/f'm05-{k}-outer-v1.png')
bind={'candidate':str(cand),'sha256':h(cand),'base':str(base),'baseSha256':h(base),'repairNative':str(out),'repairNativeSha256':h(out),'sourceCrop':roi,'destinationBox':dest,'operation':'integer native pixels crop/paste only','actualModel':None,'status':'unreviewed'}
(q/'composition-v1.json').write_text(json.dumps(bind,indent=2)+'\n',encoding='utf-8')
print(json.dumps(bind))

