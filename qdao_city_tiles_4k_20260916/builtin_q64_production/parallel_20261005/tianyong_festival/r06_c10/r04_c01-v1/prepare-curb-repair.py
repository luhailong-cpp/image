from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).parent;R=D/'curb-repair-v1';R.mkdir(exist_ok=True)
q=json.loads((D/'request.json').read_text(encoding='utf-8-sig'));a=np.array(Image.open(D/'native.png').convert('RGBA'));a[:170,:1010]=0;Image.fromarray(a).save(R/'context.png')
q['payload']['referenced_image_paths'][0]=str(R/'context.png');q['payload']['referenced_image_paths'][3]=str(D.parent/'r04_c03-v1/final-v2/joined.png')
q['payload']['prompt']='Use case: precise-object-edit. Repair only the transparent top-left band of image1. Return the SAME native 1254x1254 world crop, same scale, camera and every visible pixel. Image2 is the exact canonical layout. Image3 approved guild style; image4 nearby native map finish only, do not copy its objects. The ONLY thing in the transparent band is a SINGLE STRAIGHT HORIZONTAL white stone flowerbed curb continuing the known rightmost curb at y40..140. Its top and bottom edges run almost horizontally all the way from left to right. Absolutely NO curved curb, NO round flowerbed corner, NO second curb in front, NO crossing or overlapping stone strips. The canonical layout shows one single continuous white stone border. A short tuft of plump dark-green leaves hangs down from the top edge around x680..840; preserve this footprint. Continue its subtle soft shadow. Keep the entire already-painted paving below y170 absolutely unchanged, including all clean slab bevels, shadows and lower junctions. No cracks, triangular notches, people, writing or new objects. Bright clean rounded Daoist Q polished game painting. No warp, crop or zoom.'
q['parentNative']=str(D/'native.png');q['repairRegionLTRB']=[0,0,1010,170];q.pop('excludedUnacceptedHaloLTRB',None)
(R/'request.json').write_text(json.dumps(q,indent=2),encoding='utf8');print(json.dumps(q))
