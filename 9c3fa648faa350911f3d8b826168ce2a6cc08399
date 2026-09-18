from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parent
source=root/'output/donghai_day_r08_c10_q64_4k_candidate.png'
im=Image.open(source).convert('RGB');assert im.size==(4096,4096)
out=root/'qa/fullseams_v1';out.mkdir(parents=True,exist_ok=True)
entries=[]
for axis in ('v','h'):
 for pos in (1024,2048,3072):
  canvas=Image.new('RGB',(1200,1024) if axis=='v' else (1024,1200))
  boxes=[]
  for k in range(4):
   box=(pos-150,k*1024,pos+150,(k+1)*1024) if axis=='v' else (k*1024,pos-150,(k+1)*1024,pos+150)
   crop=im.crop(box);canvas.paste(crop,(k*300,0) if axis=='v' else (0,k*300));boxes.append(list(box))
  p=out/f'{axis}{pos}_all4096_native.png';assert not p.exists();canvas.save(p)
  entries.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceBoxes=boxes,pixels=list(canvas.size),resized=False,kind='native_pixel_panels_full_seam',panelOrder='top_to_bottom_shown_left_to_right' if axis=='v' else 'left_to_right_shown_top_to_bottom'))
(out/'manifest.json').write_text(json.dumps(dict(source=str(source),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),entries=entries),indent=2),encoding='utf8')
print(json.dumps(dict(fullSeams=6,nativePanels=24,output=str(out))))
