from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=Image.open(D/'edit-target.png').convert('RGB');native=Image.open(D/'native.png').convert('RGB')
poly=[(425,661),(490,627),(750,665),(880,627),(900,700),(790,755),(640,865),(425,745)]
mask=Image.new('L',(1254,1254),0);ImageDraw.Draw(mask).polygon(poly,fill=255)
mask.save(D/'selection-mask-v2.png');trial=Image.composite(native,base,mask);trial.save(D/'roi-trial-v2.png')
m=np.array(mask);a=np.array(base);out=np.array(trial);s=np.array(native)
assert not m[:627].any() and np.array_equal(out[m==0],a[m==0]) and np.array_equal(out[m==255],s[m==255])
for name,box in [('detail',[360,580,950,905]),('north',[400,595,930,705]),('south',[565,785,715,905]),('west',[385,630,485,795]),('east',[830,595,955,780])]:trial.crop(box).save(D/('v2-'+name+'.png'))
p=json.loads((D/'adoption-proposal.json').read_text());bb=list(mask.getbbox());p.update(status='pending_visual_review',sameWorldNativeROI=bb,targetTileROI=[bb[0]+2445,bb[1]-627,bb[2]+2445,bb[3]-627],mask=str(D/'selection-mask-v2.png'),maskSha256=sha(D/'selection-mask-v2.png'),maskPolygonXY=poly,selectedPixelCount=int((m==255).sum()),trial=str(D/'roi-trial-v2.png'),trialSha256=sha(D/'roi-trial-v2.png'),northNeighborPixelsChanged=0)
(D/'adoption-proposal-v2.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
print({'selectedPixels':p['selectedPixelCount']})

