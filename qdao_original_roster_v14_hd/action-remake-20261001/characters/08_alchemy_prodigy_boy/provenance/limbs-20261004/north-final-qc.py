from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
metrics=[]
for d in ['E','NE']:
    canvas=Image.new('RGB',(1024,1128),'#eee9db');draw=ImageDraw.Draw(canvas)
    for n in range(1,17):
        p=ROOT/'runtime'/'run'/d/f'{n:02d}.png'
        selected=n in [3,11]
        q=ROOT/'generation/limbs-20261004/run-north'/f'{d}{n:02d}-v1.png' if selected else p
        a=Image.open(p).convert('RGBA');b=Image.open(q).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
        x=((n-1)%4)*256;y=((n-1)//4)*282
        tile=b.resize((256,256),Image.Resampling.LANCZOS)
        canvas.paste(tile,(x,y+24),tile);draw.text((x+5,y+4),f'{d}/{n:02d} '+('candidate' if selected else 'current'),fill='#203b32')
        if selected:
            aa=np.asarray(a)[:,:,3]>16;bb=np.asarray(b)[:,:,3]>16
            result={'slot':f'run/{d}/{n:02d}','source':q.relative_to(ROOT).as_posix(),'sourceSHA256':hashlib.sha256(q.read_bytes()).hexdigest(),'nativeSize':list(Image.open(q).size),'fixedWholeCanvasExport':[1024,1024],'offset':[0,0]}
            for title,s in [('headAbove450',slice(0,450)),('legsBelow760',slice(760,1024))]:
                x1=aa[s];x2=bb[s];result[title+'AlphaIoU']=round(float((x1&x2).sum()/(x1|x2).sum()),5)
            result['runtimeInputSHA256']=hashlib.sha256(p.read_bytes()).hexdigest()
            metrics.append(result)
    canvas.save(OUT/f'north-{d}-selected-contact.jpg',quality=96)
(OUT/'north-candidate-registration.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
