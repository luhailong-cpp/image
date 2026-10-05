from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
out=b/'review'/'axis-NE-E';out.mkdir(parents=True,exist_ok=True)
meta=[]
for dr in ['E','NE']:
    whole=Image.new('RGB',(960,1080),(215,220,212)); dw=ImageDraw.Draw(whole)
    for batch in [0,1]:
        box=(120,610,1000,1010) if dr=='E' else (170,610,930,1010)
        width=660 if dr=='E' else 570
        sheet=Image.new('RGB',(width*2,330*4),(215,220,212));d=ImageDraw.Draw(sheet)
        for j in range(8):
            n=batch*8+j+1;p=b/'runtime'/'run'/dr/f'{n:02}.png'
            im=Image.open(p).convert('RGBA')
            crop=im.crop(box).resize((width,300),Image.Resampling.LANCZOS)
            x=j%2*width;y=j//2*330
            sheet.paste(crop,(x,y),crop);d.text((x+8,y+304),f'{dr} {n:02}  fixed crop {box}',fill=(20,35,26))
            xw=(n-1)%4*240;yw=(n-1)//4*270
            th=im.resize((240,240),Image.Resampling.LANCZOS)
            whole.paste(th,(xw,yw),th);dw.text((xw+8,yw+245),f'{dr} {n:02}',fill=(20,35,26))
            meta.append({'slot':f'run-{dr}-{n:02}','file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'diagnosticOnly':True})
        sheet.save(out/f'{dr}-feet-{batch*8+1:02}-{batch*8+8:02}.jpg',quality=95)
    whole.save(out/f'{dr}-whole-240.jpg',quality=95)
(out/'sources.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')

