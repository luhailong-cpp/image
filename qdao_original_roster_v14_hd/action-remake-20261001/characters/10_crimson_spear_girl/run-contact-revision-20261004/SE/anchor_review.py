from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parents[2]
out=Image.new('RGB',(1200,900),(230,230,230))
for col,name in enumerate(['07-v7','07-v8']):
 im=Image.open(root/f'run-contact-revision-20261004/SE/{name}/native.png').convert('RGBA')
 box=(400,350,1000,1100);im=im.crop(box)
 panel=Image.new('RGB',im.size,(220,220,220));panel.paste(im,(0,0),im);d=ImageDraw.Draw(panel)
 for x in range(0,601,50):d.line((x,0,x,750),fill='#7291a0');d.text((x+2,2),str(x+400),fill='black')
 for y in range(0,751,50):d.line((0,y,600,y),fill='#7291a0');d.text((2,y+2),str(y+350),fill='black')
 out.paste(panel,(col*600,30));ImageDraw.Draw(out).text((col*600,5),name,fill='black')
out.save(root/'run-contact-revision-20261004/SE/anchor-review.jpg')
