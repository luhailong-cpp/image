from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for v,ver in [('lanxian_day','v4'),('lanxian_spring','v5')]:
 d=P/v/'pair_r08_c06_c07';src=d/f'output/{v}_r08_c07_q64_4k_candidate_pair_{ver}.png';a=Image.open(src).convert('RGB');out=d/'qa/full-seams-c07';out.mkdir(exist_ok=True);entries=[]
 for axis in ('x','y'):
  for coordinate in (1024,2048,3072):
   strips=[];rects=[]
   for s in range(4):
    rect=(coordinate-147,s*1024,coordinate+147,(s+1)*1024) if axis=='x' else (s*1024,coordinate-147,(s+1)*1024,coordinate+147)
    strips.append(a.crop(rect));rects.append(list(rect))
   size=(1200,1060) if axis=='x' else (1024,1320)
   sheet=Image.new('RGB',size,'white');draw=ImageDraw.Draw(sheet)
   draw.text((4,4),f'{v} c07 {axis}={coordinate}; 1:1 pixel strips; segments 0..3',fill='black',font=font)
   for s,b in enumerate(strips):
    pos=(s*300,36) if axis=='x' else (0,36+s*321)
    sheet.paste(b,pos)
   f=out/f'{axis}{coordinate}-full-seam.png';sheet.save(f)
   sheet.save(out/f'{axis}{coordinate}-full-seam.jpg',quality=70)
   entries.append({'axis':axis,'coordinate':coordinate,'file':str(f),'segmentsXYXY':rects,'resized':False,'sourcePixelCoverage':'all 4096 pixels of this internal grid boundary, including 294px-wide overlap band'})
 (out/'manifest.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'entries':entries,'review':'pending'},indent=2))
print('12 full-length seam sheets ready')
