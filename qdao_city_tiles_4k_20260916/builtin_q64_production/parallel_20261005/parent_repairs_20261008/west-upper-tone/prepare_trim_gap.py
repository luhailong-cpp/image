from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent;O=R/'trim-gap';O.mkdir(exist_ok=True)
im=Image.open(R/'joined.png').convert('RGBA');im.paste((0,0,0,0),(572,201,692,321));im.save(O/'context.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
prompt='''Use case: precise-object-edit / inpainting. Image1 is the exact edit target, a game paving crop with ONE small transparent rectangle cut out near its upper center. Fill ONLY this small transparent rectangle. Continue the thin white diagonal highlight straight through the missing section with exactly the same width and tangent as its two existing endpoints. It is a continuous straight diagonal edge, with NO vertical step, corner, notch, kink or bump inside the missing section. Continue the adjacent gold flat face and softly shaded gold bevel naturally. Preserve every existing opaque pixel in place, including the stone face and relief. Image2 is style only, not layout/UI. Same square framing, clean rounded painterly native game art. Return the image fully opaque after filling the small hole, no checkerboard, no text, no new joints or objects.'''
req={'payload':{'prompt':prompt,'referenced_image_paths':[str(O/'context.png'),str(style)],'transparent_background':False},'references':[{'file':str(O/'context.png'),'sha256':sha(O/'context.png'),'role':'small masked edit target'},{'file':str(style),'sha256':sha(style),'role':'approved style only'}],'derivedFrom':{'file':str(R/'joined.png'),'sha256':sha(R/'joined.png'),'operation':'prepare transparent rectangular editing mask; no repainting, resize or warp','maskLTRB':[572,201,692,321]}}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8');(O/'context.png.generation.json').write_text(json.dumps(req['derivedFrom'],ensure_ascii=False,indent=2),encoding='utf-8')
