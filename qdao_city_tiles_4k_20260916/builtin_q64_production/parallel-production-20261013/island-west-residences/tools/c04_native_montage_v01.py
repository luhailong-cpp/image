import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

B = Path(__file__).resolve().parents[1]
Q = B / 'qa' / 'c04-r01-review-v01'
Q.mkdir(exist_ok=False)
S = B / 'qa' / 'assembly_r01_c04_candidate-v1_4096'
records = []
def montage(name, paths, cols):
    ims = [Image.open(p).convert('RGB') for p in paths]
    w = max(x.width for x in ims); h = max(x.height for x in ims)
    out = Image.new('RGB', (cols*w, ((len(ims)+cols-1)//cols)*h))
    for n, im in enumerate(ims): out.paste(im, ((n%cols)*w, (n//cols)*h))
    target = Q / name
    out.save(target)
    records.append({'path':target.as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'nativeScale100Percent':True,'resized':False,'sources':[p.as_posix() for p in paths]})
for r in range(1,5):
    montage(f'vertical-row{r:02d}-native-montage.png', [S/f'left-right_r{r:02d}_c{c:02d}-c{c+1:02d}_100pct.png' for c in range(1,4)], 3)
for r in range(1,4):
    montage(f'horizontal-band{r:02d}-native-montage.png', [S/f'top-bottom_r{r:02d}-r{r+1:02d}_x{x:04d}-{x+1024:04d}_100pct.png' for x in range(0,4096,1024)], 2)
montage('junctions-native-montage.png', [S/f'junction_r{r:02d}-r{r+1:02d}_c{c:02d}-c{c+1:02d}_100pct.png' for r in range(1,4) for c in range(1,4)], 3)
north = B / 'tiles/r01_c04_candidate-v1_4096.png'
south = B / 'tiles/r02_c04_candidate-v1_4096.png'
crosses=[]
with Image.open(north) as a, Image.open(south) as b:
    for x in range(0,4096,1024):
        c=Image.new('RGB',(1024,480));c.paste(a.crop((x,3856,x+1024,4096)),(0,0));c.paste(b.crop((x,0,x+1024,240)),(0,240))
        p=Q/f'r01-r02_c04_x{x:04d}-{x+1024:04d}_100pct.png'; c.save(p); crosses.append(p)
montage('r01-r02-native-border-montage.png', crosses, 2)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r01_c04','role':'native QA only, original crops pasted without resizing or art modification','candidate':{'path':north.as_posix(),'sha256':hashlib.sha256(north.read_bytes()).hexdigest()},'records':records,'status':'unreviewed','formalAccepted':False}
with (Q/'montage-index.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
print(json.dumps({'candidate':record['candidate'],'qaIndex':str(Q/'montage-index.json'),'montages':len(records)}))
