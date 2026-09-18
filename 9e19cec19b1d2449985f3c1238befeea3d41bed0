from pathlib import Path
from PIL import Image
import json,hashlib
r=Path(r'E:\work\image\qdao_original_roster_v13');id='04_mountain_guardian_boy';p=r/'baseline/q_daoist_character_pack_4096'/f'{id}_transparent_4096.png'
d=r/'references'/id;d.mkdir(parents=True,exist_ok=True)
im=Image.open(p).convert('RGBA');im=im.resize((768,768),Image.Resampling.LANCZOS);bg=Image.new('RGBA',im.size,(255,0,255,255));bg.alpha_composite(im);bg.convert('RGB').save(d/'original-reference.jpg',quality=90)
print(json.dumps({'id':id,'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reference':str(d/'original-reference.jpg')}))
