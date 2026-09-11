from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
records=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
def comp(im,bg):
    x=Image.new('RGBA',im.size,bg);x.alpha_composite(im);return x.convert('RGB')
items=[]
for i,r in enumerate(records):
    im=Image.open(ROOT/r['path']).convert('RGBA');a=np.array(im)
    rr=a[:,:,0].astype(int);gg=a[:,:,1].astype(int);bb=a[:,:,2].astype(int);alpha=a[:,:,3]
    if i<32:
        score=((rr-gg>35)&(bb-gg>35)&(alpha>15)).astype('uint8')
        score[330:,:]=0
        # Locate the 80x80 cluster in crown area for manual inspection.
        scores=Image.fromarray(score*255).filter(ImageFilter.BoxBlur(40))
        sy,sx=np.unravel_index(np.array(scores).argmax(),score.shape)
        box=(int(sx)-40,int(sy)-40,int(sx)+40,int(sy)+40)
        r['edge_crop']=list(box)
        items.append((r['path'],im.crop(box),box))
    else:
        # Find edge candidates excluding opaque interior fur to avoid natural lavender bias.
        edge=np.array(im.getchannel('A').filter(ImageFilter.MinFilter(7)))<25
        mask=(rr-gg>35)&(bb-gg>35)&(alpha>15)&edge
        work=mask.astype('uint8')
        boxes=[]
        for k in range(2):
            scores=np.array(Image.fromarray(work*255).filter(ImageFilter.BoxBlur(40)))
            sy,sx=np.unravel_index(scores.argmax(),work.shape)
            box=(max(0,int(sx)-40),max(0,int(sy)-40),min(1254,int(sx)+40),min(1254,int(sy)+40))
            boxes.append(list(box));items.append((r['path']+f' #{k+1}',im.crop(box),box))
            work[max(0,sy-120):sy+120,max(0,sx-120):sx+120]=0
        r['edge_crops']=boxes

for page in range(5):
    canvas=Image.new('RGB',(1984,610),(218,215,204));d=ImageDraw.Draw(canvas)
    for j,(label,im,box) in enumerate(items[page*8:page*8+8]):
        x=j%4*496;y=j//4*305
        d.text((x+5,y+4),Path(label).name.replace('-transparent_1254.png',''),font=FONT,fill='black')
        d.text((x+5,y+26),str(box)+' | native pixels x3',font=FONT,fill='black')
        for k,bg in enumerate([(241,238,223,255),(23,42,37,255)]):
            c=comp(im,bg).resize((240,240),Image.Resampling.NEAREST)
            canvas.paste(c,(x+4+k*244,y+56))
    canvas.save(OUT/f'edges-{page+1:02d}.png')
(OUT/'inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('created five crop comparison pages')
