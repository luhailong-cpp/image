from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
report=json.loads((OUT/'overlap-diagnostics.json').read_text())
manifest=[]
for aid,bid in [('p43','p44'),('p34','p44'),('p11','p12'),('p22','p32')]:
 e=next(x for x in report['pairs'] if x['a']==aid and x['b']==bid)
 pa=ROOT/'native'/(aid+'.png');pb=ROOT/'native'/(bid+'.png')
 a=Image.open(pa).convert('RGB');b=Image.open(pb).convert('RGB')
 if e['axis']=='horizontal':a=a.crop((1024,0,1254,1254));b=b.crop((0,0,230,1254))
 else:a=a.crop((0,1024,1254,1254)).transpose(Image.Transpose.ROTATE_90);b=b.crop((0,0,1254,230)).transpose(Image.Transpose.ROTATE_90)
 split=a.copy();split.paste(b.crop((115,0,230,1254)),(115,0))
 diff=Image.fromarray(np.clip(np.abs(np.array(a).astype(int)-np.array(b).astype(int))*3,0,255).astype('uint8'))
 sheet=Image.new('RGB',(950,1282),'#333333');draw=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate([(a,aid+' overlap'),(b,bid+' overlap'),(split,'split at center'),(diff,'abs diff x3')]):
  x=i*240;sheet.paste(im,(x,28));draw.text((x+3,5),label,fill='white')
 p=OUT/(aid+'-'+bid+'-overlap-native.png');sheet.save(p)
 manifest.append(dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sources=[str(pa),str(pb)],method='Integer native overlap crops; vertical overlaps rotated90; third column split comparison only; fourth amplified difference diagnostic only. No source pixels or candidate changed.',scale='1:1',actuallyViewed=False,formalAccepted=False))
(OUT/'visual-evidence-index.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Rendered4 native-scale diagnostic boards only.')
