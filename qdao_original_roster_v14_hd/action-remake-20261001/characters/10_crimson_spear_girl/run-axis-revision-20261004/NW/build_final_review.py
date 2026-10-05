from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
r=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
sel={10:'10-v1',11:'11-v3',12:'12-v1'}
sheet=Image.new('RGB',(2500,730),(236,235,226));d=ImageDraw.Draw(sheet);refs=[]
for row in range(2):
    for j,n in enumerate(range(9,14)):
        src=(out/sel[n]/'native.png') if row and n in sel else r/f'runtime/run/NW/{n:02d}.png'
        im=Image.open(src).convert('RGBA')
        if im.size!=(1024,1024):im=im.resize((1024,1024),Image.Resampling.LANCZOS)
        crop=im.crop((310,650,840,1000)).resize((500,330),Image.Resampling.LANCZOS)
        x,y=j*500,row*365
        d.text((x+10,y+10),f'NW{n:02d} - '+('SELECTED' if row else 'PRIOR RUNTIME'),fill=(15,15,15))
        sheet.paste(crop,(x,y+30),crop)
        refs.append({'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'generationRecord':str(src)+'.generation.json'})
dest=out/'NW09-13-before-after.jpg';sheet.save(dest,quality=98)
Path(str(dest)+'.generation.json').write_text(json.dumps({'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operation':'Read-only fixed-canvas 1254-to1024 uniform resample if needed, constant crop and montage; no pose alteration','derivedFrom':refs},ensure_ascii=False,indent=2),encoding='utf8')
print(dest)
