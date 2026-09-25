from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
OUT=Path(__file__).resolve().parent;REV=OUT.parents[1]/'05-delivery-preview/revisions/complete-review-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(im,path,refs,operation):
 im.save(path)
 path.with_name(path.name+'.generation.json').write_text(json.dumps({'file':str(path),'sha256':sha(path),'operation':operation,'generationCalls':0,'derivedFrom':[{'file':str(p),'sha256':sha(p)} for p in refs]},indent=2),encoding='utf-8')
for d in ['N','E','S','NW']:
 refs=[REV/f'runtime/walk/{d}/{n:02d}.png' for n in range(1,17)]
 for bg,col,ink in [('light','#f0eee4','black'),('dark','#202b38','white')]:
  sheet=Image.new('RGB',(1600,1400),col)
  for i,p in enumerate(refs):
   im=Image.open(p).convert('RGBA')
   box=(300,730,700,1050) if d=='NW' else (145,335,345,495)
   crop=im.crop(box).resize((400,320),Image.Resampling.NEAREST)
   x=i%4*400;y=i//4*350;sheet.paste(crop,(x,y+30),crop);ImageDraw.Draw(sheet).text((x+8,y+8),f'{d}{i+1:02d} native legs / '+('1x' if d=='NW' else '2x'),fill=ink)
  save(sheet,OUT/f'{d}-legs-{bg}.png',refs,'inspection-only crop; old512 legs nearest2x for review; no runtime pixel modified')
dirs=['N','NE','E','SE','S','SW','W','NW'];refs=[REV/f'runtime/idle/{d}.png' for d in dirs]
for bg,col,ink in [('light','#f0eee4','black'),('dark','#202b38','white')]:
 sheet=Image.new('RGB',(2048,1088),col)
 for i,p in enumerate(refs):
  im=Image.open(p).convert('RGBA');x=i%4*512;y=i//4*544;sheet.paste(im,(x,y+32),im);ImageDraw.Draw(sheet).text((x+12,y+8),dirs[i]+' idle 512 native',fill=ink)
 save(sheet,OUT/f'idle-all-{bg}.png',refs,'inspection-only composite, native512, no runtime pixel modified')
 for page in [0,1]:
  sheet=Image.new('RGB',(1600,1600),col)
  for j in range(4):
   i=page*4+j;im=Image.open(refs[i]).convert('RGBA').crop((56,52,456,436)).resize((800,768),Image.Resampling.NEAREST)
   x=j%2*800;y=j//2*800;sheet.paste(im,(x,y+32),im);ImageDraw.Draw(sheet).text((x+12,y+8),dirs[i]+' idle 2x inspection crop',fill=ink)
  save(sheet,OUT/f'idle-enlarged-{page+1}-{bg}.png',refs[page*4:page*4+4],'inspection-only nearest2x crop, no runtime pixel modified')
print(OUT)
