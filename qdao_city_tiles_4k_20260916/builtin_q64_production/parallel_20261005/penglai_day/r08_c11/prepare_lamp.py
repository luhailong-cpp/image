from pathlib import Path
import json,sys
from PIL import Image
R=Path(__file__).resolve().parent;B=R.parent;sys.path.insert(0,str(B));import production as p
O=R/'repairs/internal';name='lamp-join';src=O/'r08_c11-internal-candidate-v3.png';box=[850,2445,2104,3699]
f=O/'references'/f'{name}-input.png';Image.open(src).crop(box).save(f);p.derived(f,[src],{'method':'native exact crop','boxLTRB':box,'scale':1})
prompt='Use case: precise-object-edit. Image1 is actual native1254 crop of a Taoist Q fantasy map with a long red framed yellow lantern and wood post. Image2 PRIMARY painting style, no UI. Correct the tiny abrupt steps and straight horizontal paint breaks at y627 across the lantern vertical red frame and the tall wooden post; make each vertical silhouette straight and continuous, one consistent material with no horizontal patch division. Keep the exact width, original position, square perspective, warm colors and framing, all ground seams and outside objects unchanged. The correction should be local near y400..850 on these two vertical objects. Preserve top/bottom180px and left/right180px near-identical; do not add details or move anything. Native crisp clean rounded Q handpainting. No text, UI, blur or grain.'
call={'prompt':prompt,'referenced_image_paths':[f.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False};(O/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');p.write(O/'prompts'/f'{name}.call.json',call);p.write(O/'evidence'/f'{name}-placement.json',{'source':str(src),'sha256':p.sha(src),'cropBoxLTRB':box,'nativeSize':[1254,1254]});print(json.dumps(call))

