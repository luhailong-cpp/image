from pathlib import Path
import json,sys
from PIL import Image
R=Path(__file__).resolve().parent;B=R.parent;sys.path.insert(0,str(B));import production as p
O=R/'repairs/internal';p.ROOT=O
name='floor-joint';src=O/'r08_c11-internal-candidate-v2.png';box=[1421,1933,2675,3187]
(O/'references').mkdir(exist_ok=True);(O/'prompts').mkdir(exist_ok=True);(O/'native').mkdir(exist_ok=True);(O/'evidence').mkdir(exist_ok=True)
f=O/'references'/f'{name}-input.png';Image.open(src).crop(box).save(f);p.derived(f,[src],{'method':'native exact crop','boxLTRB':box,'scale':1})
prompt='Use case: precise-object-edit. Image1 is actual1254 native map crop with broken cream paving geometry at artificial VERTICAL map patch seam x627, mainly y200..700. Image2 is PRIMARY approved painting style, no UI. Fix the paving into a coherent diagonal grid across x627: join corresponding beige recessed grooves and white rounded slab bevels smoothly; no zigzag hinge, stopped line, double bevel, missing groove or triangular mask remnant. The two half contours conflict and must be repainted into one continuous arrangement, not preserved. Keep wooden lantern support and all non-ground objects unchanged. Preserve actual outer120px endpoints and texture, identical camera/world scale/crop, slab count and broad material palette. Repaint central smooth cream stone to remove any straight material boundary or faint grey rectangular bands. No added objects, text, grain, blur, ornamental pattern or UI. Fine restrained clean Q handpainted materials. Native square same crop.'
call={'prompt':prompt,'referenced_image_paths':[f.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False}
(O/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');p.write(O/'prompts'/f'{name}.call.json',call);p.write(O/'evidence'/f'{name}-placement.json',{'source':str(src),'sha256':p.sha(src),'cropBoxLTRB':box,'nativeSize':[1254,1254]})
print(json.dumps(call))

