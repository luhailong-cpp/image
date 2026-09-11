from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
SMALL=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
paths=sorted((ROOT/'character_move_8dir').glob('*.png'))+sorted((ROOT/'qdao_chibi_pets_v1').glob('*transparent*.png'))+[ROOT/'qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png']
records=[]

def comp(im,bg):
    x=Image.new('RGBA',im.size,bg); x.alpha_composite(im); return x.convert('RGB')

for p in paths:
    im=Image.open(p).convert('RGBA'); a=np.array(im)
    # Candidate locator only; no aesthetic judgement follows from this threshold.
    mask=(a[:,:,0].astype(int)-a[:,:,1]>35)&(a[:,:,2].astype(int)-a[:,:,1]>35)&(a[:,:,3]>15)
    yy,xx=np.where(mask)
    records.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'bbox':list(im.getbbox() or ()),'candidate_pixels':int(mask.sum()),'candidate_bbox':[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None})

for page in range(4):
    canvas=Image.new('RGB',(1320,830),(229,226,214)); d=ImageDraw.Draw(canvas)
    subset=paths[page*8:page*8+8]
    for j,p in enumerate(subset):
        im=Image.open(p).convert('RGBA'); im=im.crop(im.getbbox()); im.thumbnail((318,365),Image.Resampling.LANCZOS)
        x=(j%4)*330+(330-im.width)//2;y=(j//4)*415+36+(367-im.height)//2
        canvas.paste(comp(im,(241,238,223,255)),(x,y));d.text(((j%4)*330+8,(j//4)*415+8),p.stem,font=FONT,fill=(30,40,34))
    canvas.save(OUT/f'walk-{page+1:02d}.jpg',quality=96)

canvas=Image.new('RGB',(1600,860),(229,226,214));d=ImageDraw.Draw(canvas)
for j,p in enumerate(paths[32:]):
    im=Image.open(p).convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((780,375),Image.Resampling.LANCZOS)
    x=j%2*800+(800-im.width)//2;y=j//2*430+42+(380-im.height)//2
    canvas.paste(comp(im,(241,238,223,255)),(x,y));d.text((j%2*800+10,j//2*430+8),p.stem,font=FONT,fill=(30,40,34))
canvas.save(OUT/'pets.jpg',quality=97)
(OUT/'inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
