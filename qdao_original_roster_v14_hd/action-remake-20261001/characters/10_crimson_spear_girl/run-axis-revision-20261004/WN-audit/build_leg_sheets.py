from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl");out=root/'run-axis-revision-20261004/WN-audit';out.mkdir(parents=True,exist_ok=True)
for d in ('W','NW'):
  for start in (1,9):
    sheet=Image.new('RGB',(2000,760),(235,234,224));draw=ImageDraw.Draw(sheet);refs=[]
    for j,n in enumerate(range(start,start+8)):
      p=root/f'runtime/run/{d}/{n:02d}.png'; im=Image.open(p).convert('RGBA')
      crop=im.crop((250,640,830,1000)).resize((500,310),Image.Resampling.LANCZOS)
      x=(j%4)*500;y=(j//4)*380
      draw.text((x+12,y+12),f'{d} {n:02d} - runtime, fixed crop x250..830 y640..1000',fill=(20,20,20))
      sheet.paste(crop,(x,y+45),crop)
      refs.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':str(p)+'.generation.json'})
    dest=out/f'{d}-legs-{start:02d}-{start+7:02d}.jpg';sheet.save(dest,quality=97)
    (Path(str(dest)+'.generation.json')).write_text(json.dumps({'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operation':'Read-only audit crop and montage, uniform size; no AI generation or sprite edit','derivedFrom':refs},ensure_ascii=False,indent=2),encoding='utf8')
    print(dest)

