"""Read selected W/NW frames into source-bound offline review sheets."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1]
OUT=R/'15-review';OUT.mkdir(exist_ok=True)
for direction in ('W','NW'):
    rows=[]
    for n in range(1,17):
        p=R/'15-delivery-preview/runtime/walk'/direction/f'{n:02d}.png'
        if p.exists():rows.append((n,p))
    for bg,name in [((240,234,220),'light'),((24,34,44),'dark')]:
        full=Image.new('RGB',(1024,1120),bg);dr=ImageDraw.Draw(full)
        feet=Image.new('RGB',(1600,1280),bg);df=ImageDraw.Draw(feet)
        seam=Image.new('RGB',(2048,540),bg);ds=ImageDraw.Draw(seam)
        for n,p in rows:
            im=Image.open(p).convert('RGBA');x=(n-1)%4*256;y=(n-1)//4*280
            sm=im.resize((256,256),Image.Resampling.LANCZOS);full.paste(sm,(x,y+24),sm);dr.text((x+8,y+4),f'{direction}{n:02d}',fill=(80,160,180))
            crop=im.crop((280,650,680,970));xf=(n-1)%4*400;yf=(n-1)//4*320;feet.paste(crop,(xf,yf),crop);df.text((xf+8,yf+5),f'{direction}{n:02d}',fill=(80,160,180))
            if n in (15,16,1,2):
                idx=(15,16,1,2).index(n);sm=im.resize((512,512),Image.Resampling.LANCZOS);seam.paste(sm,(idx*512,28),sm);ds.text((idx*512+8,8),f'{direction}{n:02d}',fill=(80,160,180))
        full.save(OUT/f'{direction}-candidates-{name}.png');feet.save(OUT/f'{direction}-feet-{name}.png');seam.save(OUT/f'{direction}-seam-{name}.png')
    (OUT/f'{direction}-sources.json').write_text(json.dumps([{'frame':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in rows],indent=2),encoding='utf-8')
    print(direction,len(rows))
