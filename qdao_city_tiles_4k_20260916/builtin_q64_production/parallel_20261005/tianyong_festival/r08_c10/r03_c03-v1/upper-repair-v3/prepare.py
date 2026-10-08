from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;P=O.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
ctx=Image.open(P/'final-registration-v1/joined.png').convert('RGBA');ctx.paste((0,0,0,0),(230,0,340,240));ctx.save(O/'context.png')
prompt="""Use case: precise-object-edit.
The first input is an exact1254x1254 painted-game-map repair target. Only its thin transparent vertical rectangle x230..340,y0..240 is missing. Fill ONLY that small hole; preserve every opaque pixel, all stone joints and all geometry outside it.
The second input is the same exact image before this small hole was opened: its upper-left stone return x230 had a pasted step and mismatched bevel thickness that must be repaired. Preserve the multiple distinct ivory slabs and the narrow upright stone separators along the top. Do not combine them into one horizontal slab.
Paint a continuous ivory/gold top bevel and gray inset corner through the small hole, joining the exact contours, shading, surface colors and thickness already visible on BOTH the left and right sides. Lower in the thin hole continue the existing gray inset face and its vertical beveled boundary. Crisp native painted edges, rounded polished warm clean Daoist Q-style stone. The third input is the approved primary painting-style sample; borrow finish only, no UI, text or decorations.
Keep original camera/crop and1254x1254 dimensions. No perspective changes, invented lines, extra shadow ledges, missing joints, blur, resizing, noisy cracks or texture noise. The already completed crossband, right cloud relief and lower field must remain unchanged. Return complete opaque image."""
refs=[O/'context.png',P/'final-registration-v1/joined.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'references':[info(p) for p in refs],'referenceRoles':['edit target native1254 smallupperleftopening','current assembledcandidate geometry withupperleftbeveldefect','approved primary paintingstyle'],'configSnapshot':json.loads(Path(r'D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'repairMaskLTRB':[230,0,340,240],'windowTileLocalLTRB':[1933,1933,3187,3187],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
(O/'prompt.txt').write_text(prompt,encoding='utf-8');(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(req['payload']))

