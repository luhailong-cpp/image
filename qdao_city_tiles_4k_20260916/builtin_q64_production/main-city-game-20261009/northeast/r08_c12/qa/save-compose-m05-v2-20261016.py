from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');src=Path(r'C:\Users\luyua\.codex\generated_images\01a142ed-202a-7243-b7b1-095dbd534429\exec-9fb956ed-9507-4273-86ac-300b2c826439.png');name='m05-joints-v2-20261016'
out=p/'native/repairs'/f'{name}.png';assert not out.exists()
assert Image.open(src).size==(1254,1254);shutil.copy2(src,out)
h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
req=json.loads((p/'prompts'/f'{name}.request.json').read_text(encoding='utf-8-sig'))
rec={'createdAt':datetime.now(timezone.utc).isoformat(),'sourceOutputPath':str(src),'workspaceFile':str(out),'sha256':h(out),'nativeSize':[1254,1254],'route':'builtin','actualModel':None,'request':str(p/'prompts'/f'{name}.request.json'),'receipt':str(p/'receipts'/f'{name}.receipt.json'),'references':[{'file':f,'sha256':h(f)} for f in req['referenced_image_paths']],'editTargetOriginTile':[397,397],'originalsPreserved':True}
Path(str(out)+'.generation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
base=p/'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png';im=Image.open(base).convert('RGBA');im.paste(Image.open(out).crop((115,115,1139,1139)),(512,512))
cand=p/'candidates/r08_c12.m05-v2-20261016.png';assert not cand.exists();im.save(cand)
q=p/'qa/repair-m05-20261016';im.crop((397,397,1651,1651)).save(q/'m05-composed-v2.png')
bind={'candidate':str(cand),'sha256':h(cand),'base':str(base),'baseSha256':h(base),'repairNative':str(out),'repairNativeSha256':h(out),'sourceCrop':[115,115,1139,1139],'destinationBox':[512,512,1536,1536],'operation':'integer native crop/paste only','status':'unreviewed'}
(q/'composition-v2.json').write_text(json.dumps(bind,indent=2)+'\n',encoding='utf-8')
print(json.dumps(bind))

