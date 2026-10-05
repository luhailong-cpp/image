from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
a=Image.open(ROOT/'runtime/run/NE/15.png').convert('RGBA')
b=Image.open(ROOT/'generation/limbs-20261004/foot-ne15/NE15-v2.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
canvas=Image.new('RGB',(1024,1050),'#eee9db');draw=ImageDraw.Draw(canvas)
for k,im in enumerate([a,b]):
 tile=im.resize((512,512),Image.Resampling.LANCZOS);canvas.paste(tile,(k*512,25),tile)
 crop=im.crop((280,650,560,990)).resize((420,510));canvas.paste(crop,(k*512+40,540),crop)
 draw.text((k*512+10,5),'CURRENT' if k==0 else 'NE15-v2',fill='#203b32')
canvas.save(OUT/'foot15-v2-compare.jpg',quality=96)
aa=np.array(a)[:,:,3]>16;bb=np.array(b)[:,:,3]>16
r={'upper650AlphaIoU':float((aa[:650]&bb[:650]).sum()/(aa[:650]|bb[:650]).sum()),'nativeSize':[1254,1254],'fixedCanvasSize':[1024,1024],'offset':[0,0]}
for key,ar in [('current',aa),('candidate',bb)]:
 yy,xx=np.where(ar[780:1000,280:520]);r[key+'BootBounds']=[int(xx.min()+280),int(yy.min()+780),int(xx.max()+280),int(yy.max()+780)]
print(json.dumps(r));(OUT/'foot15-v2-registration.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
