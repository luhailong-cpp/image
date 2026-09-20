from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,sys
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True);im=Image.open(src).convert('RGB');font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
entries=[]
for axis in ('x','y'):
 for coordinate in (1024,2048,3072):
  size=(1200,1060) if axis=='x' else (1024,1320);sheet=Image.new('RGB',size,'white');draw=ImageDraw.Draw(sheet);draw.text((4,4),f'{src.stem} {axis}={coordinate}; 1:1 segments 0..3',fill='black',font=font);rects=[]
  for s in range(4):
   rect=(coordinate-147,s*1024,coordinate+147,(s+1)*1024) if axis=='x' else (s*1024,coordinate-147,(s+1)*1024,coordinate+147)
   sheet.paste(im.crop(rect),(s*300,36) if axis=='x' else (0,36+s*321));rects.append(rect)
  f=out/f'{axis}{coordinate}.png';sheet.save(f);sheet.save(out/f'{axis}{coordinate}.jpg',quality=90)
  entries.append({'axis':axis,'coordinate':coordinate,'file':str(f),'segmentsXYXY':rects,'resized':False})
(out/'manifest.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'entries':entries,'review':'pending'},indent=2),encoding='utf-8')
print('Full 6 seams ready',src)