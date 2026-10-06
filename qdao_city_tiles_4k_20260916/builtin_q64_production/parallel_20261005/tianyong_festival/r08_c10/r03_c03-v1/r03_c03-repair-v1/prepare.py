from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;S=O.parent;R=next(p for p in S.parents if (p/'config/image-generation.json').is_file())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
im=Image.open(S/'registration-v3/joined.png').convert('RGBA')
cx=Image.open(S/'registration-v3/context-v005.png').convert('RGBA')
a=np.array(im);c=np.array(cx);known=c[:,:,3]==255;a[known]=c[known]
mask=[230,540,470,920]
a[540:920,230:470,:]=0
Image.fromarray(a).save(O/'context.png')
prompt='''Use case: precise-object-edit. Repair a narrow existing stone bevel junction in the original game 五行奇谈.
Return one opaque1254 by1254 image with exactly the same framing and scale as IMAGE1. Fill only its transparent rectangle x230..469,y540..919. Everything else is an already finished native painting and must remain identical. The left230 pixels contain the fixed exact neighbor; the bottom and right also contain authoritative finished neighboring pixels. Their coordinates and silhouettes must not change.
Within the transparent gap, join the broad horizontal ivory cross-band, its top bevel and shaded contact edge, and the quiet ivory stone surface to the exact visible pixels on BOTH sides. The left neighbor has a slightly deeper upper bevel than the right side; paint one naturally continuous gently varying bevel and shadow between the fixed endpoints. The lower edge of the horizontal band already aligns, so keep its established level and continue it without a step. Preserve the visible upper and lower vertical ivory dividers and gray inset panel contours at the gap boundaries. The repair must be actual freshly rendered stone detail: do not shift or stretch entire bands, add a new joint, duplicate an edge, add another step or create a rectangular shadow along the transparent border.
IMAGE2 is only the canonical broad layout at the identical global crop. It is not a material or exact-detail authority; never use its blurred pixels as final artwork. Exact visible endpoints in IMAGE1 take precedence. IMAGE3 is the user's approved primary drawing STYLE: clean bright rounded full Daoist Q fantasy handpainting, controlled contours, warm ivory stone, restrained gold edging, quiet soft volumes. Borrow only its rendering finish; no UI, writing, characters or icons.
Keep the same light direction, clean broad stone planes and controlled bevel highlights. No cracks, marble veins, grunge, sharp glowing halos, overly soft blur or extra ornament. No text, watermark, new object, camera change, resize or transparent output. Highest visual finish available through the host.'''
(O/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=[O/'context.png',S/'layout-reference-only.png',R/'designs/gameplay-ui/04-guild.png']
payload={'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False}
save(O/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'repairMaskLTRB':mask,'payload':payload,'references':[info(x) for x in refs],
 'referenceRoles':['edit target: fixed exact v005 known pixels, registered native elsewhere, transparent repair rectangle','canonical broad layout only, no guide pixels in final art','approved primary drawing style only'],
 'configSnapshot':json.loads((R/'config/image-generation.json').read_text()),'actualModel':None,'actualQuality':None})
save(O/'context.png.generation.json',{'output':info(O/'context.png'),'derivedFrom':[info(S/'registration-v3/joined.png'),info(S/'registration-v3/context-v005.png')],
 'operation':'Exact known context restored; transparent repair rectangle[230,540,470,920]. Preparation only, no generated artwork.','newModelCalls':0})
print(json.dumps({'request':str(O/'request.json'),'context':info(O/'context.png')}))
