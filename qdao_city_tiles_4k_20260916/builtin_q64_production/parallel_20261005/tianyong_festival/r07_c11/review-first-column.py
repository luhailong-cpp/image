from pathlib import Path
from PIL import Image
import json,hashlib
N=Path(__file__).parent;D=N/'review-first-column-v1';D.mkdir(exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'file':str(p),'sha256':sha(p)}
cp=read(N/'local-source-checkpoint.json');first=read(N/'r04_c01-v1/preparation.json');L=Image.open(first['sources']['r07_c10']['file']).convert('RGBA')
for p in cp['externalReturnDependencies']:
 if p['destinationTile']=='r07_c10':L.paste(Image.open(p['asset']['file']),tuple(p['destinationTileLTRB'][:2]))
F=Image.open(cp['fragment']['file']).convert('RGBA');full=Image.new('RGBA',(1439,4096));full.paste(L.crop((3796,0,4096,4096)),(0,0));full.paste(F.crop((0,0,1139,4096)),(300,0));ix=[]
for i,y in enumerate([0,1000,2000,2842]):
 p=D/f'column-{i+1}.png';full.crop((0,y,1439,y+1254)).save(p);ix.append({**ref(p),'tileLocalLTRB':[-300,y,1139,y+1254],'nativeScale':1})
(D/'index.json').write_text(json.dumps({'source':cp['fragment'],'chain':cp['manifestChain'],'nativeScale':1,'images':ix,'coveredCurrentColumnPixels':1139*4096,'visualReviewPending':True},indent=2),encoding='utf-8')
print(json.dumps(ix))
