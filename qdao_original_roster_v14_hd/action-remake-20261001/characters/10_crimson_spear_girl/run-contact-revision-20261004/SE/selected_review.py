from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
root=Path(__file__).parents[2]
for direction in (sys.argv[1:] or ['SE']):
 selpath=root/f'run-contact-revision-20261004/{direction}/selection.json'
 sel=json.loads(selpath.read_text())['slots'] if selpath.exists() else {}
 for crop in [False,True]:
  size=(400,280) if crop else (320,335)
  out=Image.new('RGB',(size[0]*4,size[1]*4),(210,212,219));d=ImageDraw.Draw(out)
  for idx in range(1,17):
   slot=f'run/{direction}/{idx:02d}'
   p=root/sel.get(slot,f'runtime/{slot}.png')
   im=Image.open(p).resize((1024,1024))
   if crop:im=im.crop((260,600,810,990)).resize(size)
   else:im=im.resize((320,320))
   x=((idx-1)%4)*size[0];y=((idx-1)//4)*size[1]
   out.paste(im,(x,y),im);d.text((x+8,y+8),f'{direction} {idx:02d}'+('*' if slot in sel else ''),fill='black')
  out.save(root/f'run-contact-revision-20261004/{direction}/selected-{"feet" if crop else "full"}.jpg')
