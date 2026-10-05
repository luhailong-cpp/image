from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import hashlib,json
r=Path(__file__).resolve().parents[2];o=Path(__file__).resolve().parent
sources=[]
for direction in ('W','NW','SW'):
    for start in (1,9):
        for kind in ('full','upper','lower'):
            if kind=='full': size=(400,400);box=(0,0,1024,1024);cols=4
            elif kind=='upper':size=(770,460);box=(160,360,930,820);cols=2
            else:size=(580,360);box=(250,640,830,1000);cols=2
            sheet=Image.new('RGB',(cols*size[0],((8+cols-1)//cols)*(size[1]+30)),(233,231,222));d=ImageDraw.Draw(sheet);refs=[]
            for j,n in enumerate(range(start,start+8)):
                p=r/f'runtime/run/{direction}/{n:02d}.png';im=Image.open(p).convert('RGBA');sha=hashlib.sha256(p.read_bytes()).hexdigest()
                tile=im.crop(box).resize(size,Image.Resampling.LANCZOS)
                x,y=(j%cols)*size[0],(j//cols)*(size[1]+30)
                d.text((x+10,y+7),f'CURRENT {direction}{n:02d} - {kind} - fixed crop',fill=(20,20,20))
                sheet.paste(tile,(x,y+30),tile)
                refs.append({'file':str(p),'sha256':sha,'generationRecord':str(p)+'.generation.json'})
                if kind=='full':sources.append({'frame':f'run/{direction}/{n:02d}','file':str(p),'sha256':sha,'size':im.size})
            dest=o/f'{direction}-{kind}-{start:02d}-{start+7:02d}.jpg';sheet.save(dest,quality=98)
            Path(str(dest)+'.generation.json').write_text(json.dumps({'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'createdAt':datetime.now(timezone.utc).isoformat(),'operation':'Read-only fixed canvas/crop montage from current runtime; no AI or pose edit','crop':box,'derivedFrom':refs},ensure_ascii=False,indent=2),encoding='utf8')
(o/'source-snapshot.json').write_text(json.dumps({'capturedAt':datetime.now(timezone.utc).isoformat(),'sources':sources},ensure_ascii=False,indent=2),encoding='utf8')
print(f'18 QA contact sheets, {len(sources)} current frame SHA records')
