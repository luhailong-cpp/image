"""Heuristic dark-hair main component measurement for scale review, not acceptance."""
from pathlib import Path
from collections import deque
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1];out=R/'15-review';allrows=[]
for d in ('W','NW'):
    sheet=Image.new('RGB',(1600,1440),(225,225,215));draw=ImageDraw.Draw(sheet)
    for n in range(1,17):
        p=R/'15-delivery-preview/runtime/walk'/d/f'{n:02d}.png'
        if not p.exists():continue
        im=Image.open(p).convert('RGBA');arr=np.array(im);rgb=arr[:,:,:3].astype(float);hi=rgb.max(2);lo=rgb.min(2)
        mask=(arr[:,:,3]>128)&(hi<145)&(lo>10)&((hi-lo)<hi*.6)&(rgb[:,:,2]>=rgb[:,:,0]*.9)
        mask[500:]=False;mask[:,:220]=False;mask[:,800:]=False
        yy,xx=np.where(mask);largest=[]
        for y,x in zip(yy,xx):
            if not mask[y,x]:continue
            q=deque([(int(x),int(y))]);mask[y,x]=False;pts=[]
            while q:
                x0,y0=q.popleft();pts.append((x0,y0))
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xn,yn=x0+dx,y0+dy
                    if 0<=xn<1024 and 0<=yn<500 and mask[yn,xn]:mask[yn,xn]=False;q.append((xn,yn))
            if len(pts)>len(largest):largest=pts
        points=np.array(largest);x0,y0=points.min(0);x1,y1=points.max(0)
        row={'direction':d,'frame':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'darkHairMainComponentBox':[int(x0),int(y0),int(x1+1),int(y1+1)],'estimatedWidth':int(x1-x0+1),'estimatedHeight':int(y1-y0+1),'pixelCount':len(largest),'note':'Heuristic thresholded largest dark component; hair highlight and ponytail connections affect result. Use marked image for visual check, not blind normalization.'};allrows.append(row)
        crop=im.crop((250,80,750,530));canvas=Image.new('RGBA',crop.size,(225,225,215,255));canvas.alpha_composite(crop);dc=ImageDraw.Draw(canvas);dc.rectangle((int(x0)-250,int(y0)-80,int(x1)-250,int(y1)-80),outline=(230,70,30),width=2)
        cell=canvas.resize((400,360),Image.Resampling.LANCZOS);sx=(n-1)%4*400;sy=(n-1)//4*360;sheet.paste(cell.convert('RGB'),(sx,sy));draw.text((sx+5,sy+5),f'{d}{n:02d} dark hair {row["estimatedWidth"]} x {row["estimatedHeight"]}',fill=(20,20,20))
    sheet.save(out/f'{d}-head-scale-candidates.png')
(out/'W-NW-head-scale-candidates.json').write_text(json.dumps({'method':'largest 4-connected RGB dark low saturation component, alpha>128, x220:800 y0:500; manual review required','frames':allrows},indent=2),encoding='utf-8')
print([(r['direction'],r['frame'],r['estimatedWidth'],r['estimatedHeight']) for r in allrows])
