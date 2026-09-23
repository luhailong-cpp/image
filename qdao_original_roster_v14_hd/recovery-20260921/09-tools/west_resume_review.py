from PIL import Image,ImageDraw
from pathlib import Path
base=Path(r'D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/recovery-20260921/')
ids=['W01-a','W02-a','W05-a','W06-a','W09-e','W13-c','Widle-a','NW01-b','NW05-a','NW09-d','NW13-b','NWidle-a']
out=Image.new('RGB',(1800,1200),'#e8e4d8')
for n,id in enumerate(ids):
 im=Image.open(base/'09-generation'/id/'raw.png').convert('RGBA'); im.thumbnail((295,550))
 x=(n%6)*300; y=(n//6)*600
 out.paste(im,(x,y+30),im)
 ImageDraw.Draw(out).text((x+10,y+8),id,fill='black')
out.save(base/'09-delivery-preview'/'west-resume-review.jpg')

