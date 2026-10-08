from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
import repair_r09_c16_post as p
p.D=p.T/'repairs/post-tonal-masked'
def prepare():
 p.D.mkdir(parents=True,exist_ok=True)
 target=p.D/'input.png';composition=p.D/'composition-reference.png'
 assert p.sha(p.BASE)==p.EXPECTED and not (p.D/'edited-native.png').exists()
 with Image.open(p.BASE) as im:im.crop(p.BOX).save(composition)
 v=np.array(Image.open(composition).convert('RGBA'));v[545:740,590:665,:]=0;v[620:735,430:492,:]=0
 Image.fromarray(v).save(target)
 p.save(str(target)+'.generation.json',{'file':str(target),'sha256':p.sha(target),'sourceRectXYXY':p.BOX,
 'source':str(p.BASE),'sourceSha256':p.EXPECTED,'operation':'unresized native crop with two transparent repair windows',
 'repairWindowsXYXY':[[590,545,665,740],[430,620,492,735]],'composition':{'file':str(composition),'sha256':p.sha(composition)},'resized':False})
 prompt='Use case: precise-object-edit / fill missing region. IMAGE1 is an exact1254 square native image with TWO SMALL TRANSPARENT HOLES. Fill ONLY the holes to restore existing artwork. IMAGE2 is the same unmasked image showing accidental seam defects for object identity. IMAGE3 is approved bright rounded hand-painted Q-style material reference. The narrow brown wood face behind the red banner has a dark side strip: its width differs immediately above and below the hole. Join those EXACT opaque endpoints in the hole as a continuous gently shaded wood face, retaining the original thin dark strip above and broader dark strip below, with no abrupt new starting segment. Do not erase or change the existing strip below the hole. At the second tiny hole on the RED BANNER LEFT EDGE, connect the existing upper and lower outline endpoints continuously, without a2pixel kink. Every opaque pixel is a fixed anchor: preserve all lanterns, emblems, banner shape, timber edge positions, water, color, shading and scale. No new details or objects, no overall recoloring, no blur, cropping, zoom or border. Output opaque1254x1254 with only the missing holes filled.'
 (p.D/'prompt.txt').write_text(prompt,encoding='utf-8')
 refs=[{'file':str(q),'sha256':p.sha(q),'role':role} for q,role in [(target,'masked native target; edit only the two transparent holes'),(composition,'unaltered composition with faulty splice; fixed geometry reference'),(p.STYLE,'approved style only')]]
 p.save(p.D/'references.json',refs)
 print(json.dumps({'prompt':prompt,'references':[v['file'] for v in refs]}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='record':p.record(sys.argv[2])
