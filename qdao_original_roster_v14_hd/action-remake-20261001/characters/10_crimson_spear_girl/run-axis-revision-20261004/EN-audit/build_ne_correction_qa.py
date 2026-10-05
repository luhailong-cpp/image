from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
W=R/'run-axis-revision-20261004'
selected={'15':'15-v1','16':'16-v2','01':'01-v1'}
frames=['14','15','16','01','02']
refs=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(f,after=False):
 p=W/'NE'/selected[f]/'native.png' if after and f in selected else R/'runtime/run/NE'/f'{f}.png'
 refs.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p)})
 return Image.open(p).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
sheet=Image.new('RGB',(2000,860),(31,35,44));d=ImageDraw.Draw(sheet)
for row,after in enumerate((False,True)):
 for col,f in enumerate(frames):
  im=get(f,after).crop((330,720,615,990)).resize((400,379),Image.Resampling.NEAREST)
  tile=Image.new('RGBA',im.size,(80,88,96,255));tile.alpha_composite(im)
  x,y=col*400,row*430;sheet.paste(tile.convert('RGB'),(x,y+45))
  d.text((x+12,y+12),('AFTER ' if after else 'BEFORE ')+'NE '+f,fill='white')
sheet.save(O/'NE-axis-before-after-14-15-16-01-02.jpg',quality=95)
full=Image.new('RGB',(1750,395),(55,62,70));d=ImageDraw.Draw(full)
for col,f in enumerate(frames):
 im=get(f,True).resize((350,350),Image.Resampling.LANCZOS)
 full.paste(im,(col*350,35),im);d.text((col*350+12,12),'AFTER NE '+f,fill='white')
full.save(O/'NE-axis-full-after-14-15-16-01-02.jpg',quality=95)
for name in ['NE-axis-before-after-14-15-16-01-02.jpg','NE-axis-full-after-14-15-16-01-02.jpg']:
 p=O/name
 Path(str(p)+'.generation.json').write_text(json.dumps({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'operation':'technical QA contact sheet only; full1254to1024 before fixed crop; no animation frame created','references':refs},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'qa':[str(O/'NE-axis-before-after-14-15-16-01-02.jpg'),str(O/'NE-axis-full-after-14-15-16-01-02.jpg')]}))

