from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
for direction in ('W','NW'):
    folder=root/'run-contact-revision-20261004'/direction
    selection=json.loads((folder/'selection.json').read_text())['slots']
    sheet=Image.new('RGB',(1760,1280),(232,232,224)); draw=ImageDraw.Draw(sheet)
    refs=[]
    for n in range(1,17):
        slot=f'run/{direction}/{n:02d}'; src=root/selection.get(slot,f'runtime/{slot}.png')
        im=Image.open(src).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
        crop=im.crop((280,690,810,975)).resize((440,237),Image.Resampling.LANCZOS)
        x=((n-1)%4)*440;y=((n-1)//4)*320
        draw.text((x+8,y+8),f'{direction} {n:02d} '+('NEW' if slot in selection else 'retained'),fill=(20,20,20))
        sheet.paste(crop,(x,y+36),crop)
        refs.append({'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    out=folder/'selected-feet-review.jpg';sheet.save(out,quality=94)
    (folder/'selected-feet-review.jpg.generation.json').write_text(json.dumps({'file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'derivedFrom':refs,'operation':'Uniform fullcanvas resize to1024 then same absolute crop at280,690,810,975 for review only; no character edit'},indent=2),encoding='utf8')
    print(direction, len(set(x['sha256'] for x in refs)), 'unique source frames')

