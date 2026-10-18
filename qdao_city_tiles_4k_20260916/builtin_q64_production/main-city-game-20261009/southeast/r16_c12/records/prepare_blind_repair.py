from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent.parent;R=T/'repairs/blind-grout-20261016-v1';R.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=read(T/'progress.json');C=Path(P['candidate']);im=Image.open(C).convert('RGB')
box=[2740,1000,3994,2254];target=R/'I01-target.png';im.crop(box).save(target)
refs=read(T/'records/p04_01_v20261016T220807_7dc2fcba.request.json')['referenced_image_paths'][:3]
prompt='Use case: precise-object-edit. Native Taoist chibi city-wall repair. Images 1/2/3 are approved map/material/illustration references only. Image 4 LAST is the sole actual-pixel edit target. Output exactly 1254x1254 opaque, same framing and scale. Change ONLY the false vertical grout stub at x627,y449..874 in image 4. It begins blindly in the middle of one broad limestone slab at y449 and meets the true horizontal seam at y874. ERASE that entire vertical grout, bevel, bright rim and thin dark shadow. Restore a continuous pale limestone stone face with the same adjacent irregular mineral texture; do not extend the stub upward, do not create a replacement joint. The true horizontal row boundary at y874 must remain intact and straight. Preserve all other joints, architecture, surface tones, shadows and all pixels away from the narrow repair. Do not reconstruct the scene. No text, UI, new props, foliage or extra decoration.'
req={'prompt':prompt,'referenced_image_paths':refs+[str(target)],'transparent_background':False}
(R/'I01.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
prep={'id':'I01','request':str(R/'I01.request.json'),'target':str(target),'targetSha256':sha(target),'cropBox':box,'base':{'path':str(C),'sha256':sha(C)},'baseContext':{'path':P['context'],'sha256':sha(Path(P['context']))},'status':'prepared_not_generated','actualModel':None}
(R/'preparation.json').write_text(json.dumps(prep,indent=2),encoding='utf-8')
D=T/'review/native-qa-20261016'
for q in range(4):
 im.crop((q*1024,0,(q+1)*1024,384)).save(D/f'north-own-q{q}.png')
 im.crop((0,q*1024,384,(q+1)*1024)).save(D/f'west-own-q{q}.png')
print(json.dumps(req))

