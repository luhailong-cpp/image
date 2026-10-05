"""Read-only pixel inspection boards; never edits a runtime sprite."""
import json, hashlib
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent/'combat-qa'
OUT.mkdir(parents=True,exist_ok=True)
rows=[]
for action,n in [('hit',6),('attack',12),('cast',16)]:
    for d in ['E','W']:
        group=[]
        for f in range(1,n+1):
            p=ROOT/'runtime'/action/d/f'{f:02}.png'
            im=Image.open(p).convert('RGBA')
            cell=Image.new('RGB',(450,340),(237,233,216))
            draw=ImageDraw.Draw(cell)
            draw.text((7,3),f'{action}/{d}/{f:02}: hands, then legs',(12,42,38))
            for box,y in [((80,385,980,715),22),((80,715,980,1005),194)]:
                crop=im.crop(box).resize((450,(box[3]-box[1])//2),Image.Resampling.LANCZOS)
                cell.paste(crop,(0,y),crop)
            group.append(cell)
            rows.append({'slot':f'{action}/{d}/{f:02}','file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size)})
        for start in range(0,n,8):
            cells=group[start:start+8]
            sheet=Image.new('RGB',(900,340*((len(cells)+1)//2)),(237,233,216))
            for j,c in enumerate(cells):sheet.paste(c,((j%2)*450,(j//2)*340))
            sheet.save(OUT/f'{action}-{d}-{start+1:02}-{start+len(cells):02}.jpg',quality=94)
(OUT/'inspected-source-index.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(rows),'uniqueSHA256':len({r['sha256'] for r in rows}),'boards':[p.name for p in OUT.glob('*.jpg')]},indent=2))
