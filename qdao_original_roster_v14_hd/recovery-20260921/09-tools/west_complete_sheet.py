from PIL import Image,ImageDraw
from pathlib import Path
b=Path(__file__).resolve().parents[1]
ids=['W08-b','W08-guide-a','W11-b','W11-guide-a','W12-b','W12-guide-a','NW01-guide-a','NW11-a','NW11-guide-a','NW14-a','NW14-guide-a','NW15-a','NW16-a']
out=Image.new('RGB',(1800,1800),'#eee9dd')
for n,id in enumerate(ids):
 im=Image.open(b/'09-generation'/id/'raw.png').convert('RGBA'); im.thumbnail((345,550))
 x=n%5*360;y=n//5*600
 out.paste(im,(x,y+25),im);ImageDraw.Draw(out).text((x+5,y+5),id,fill='black')
out.save(b/'09-delivery-preview'/'west-complete-raws.jpg')
