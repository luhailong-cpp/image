from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
ctx=Image.open(P/'final-registration-v1/joined.png').convert('RGBA')
ctx.paste((0,0,0,0),(230,0,620,300));ctx.save(O/'context.png')
prompt="""Use case: precise-object-edit.
Asset type: exact native-resolution 1254x1254 patch of a continuous painted Daoist Q-style game plaza.
Input1 is the edit target: its transparent rectangle x230..620,y0..300 is the only missing repair; every opaque pixel is finished neighbor artwork that must stay exactly where it is. Input2 is the prior assembled patch, structural guidance for the missing rectangle but its upper-left return contains incorrect bevel thickness; do not preserve that defect. Input3 is the canonical crop, layout guidance only. Input4 is the user-approved primary art-style reference: clean, bright, rounded, warm ivory/gold detailed handpainted Daoist Q game art; borrow paint finish only, no UI or lettering.
Repair the transparent upper rectangle at the exact same camera, crop and native dimensions. Continue the top horizontal ivory stone edge from the left fixed boundary at x230 with the SAME cream/gold bevel thickness, color, and smooth upper and lower contour; carry that edge naturally into the existing top stone forms to the right. Continue the long gray inset below that edge with clean rounded bevels, matching the existing vertical left rim and the intact gray surface at y300. The left corner must be a continuous finished stone junction, not a pasted step. Supply native crisp painted stone surfaces, no blur or enlargement.
Preserve all other finished artwork, especially the crossband around y700..790, the cloud relief on the right and the lower strips. No extra joints or secondary shadow ledges. No changes to layout, perspective, structures or illumination. No text, UI, labels, symbols, watermarks, tiny cracks or photorealistic noisy veins. Return the full opaque completed1254x1254 image."""
refs=[O/'context.png',P/'final-registration-v1/joined.png',P/'layout-reference-only.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'references':[info(p) for p in refs],'referenceRoles':['edit target current v010 context with repair opening','geometry current assembled candidate; left top bevel is repair target','canonical layout only','approved primary painting style'],'configSnapshot':json.loads(Path(r'D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'repairMaskLTRB':[230,0,620,300],'windowTileLocalLTRB':[1933,1933,3187,3187],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
(O/'prompt.txt').write_text(prompt,encoding='utf-8');(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(req['payload']))

