from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).parent;D=R.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
N=np.array(Image.open(D/'repair-v1/native.png').convert('RGBA'));C=np.array(Image.open(D/'context.png').convert('RGBA'));K=C[:,:,3]==255
N[K]=C[K];Image.fromarray(N).save(R/'seam-target.png')
prompt='''Use case: precise-object-edit. Repair only edge-continuity defects in the1254-square painted paving crop in image1. This is a REAL native-detail game map crop, not a whole scene. Image1 contains a hard-pasted exact authentic right230 columns and bottom115 rows. Image2 separately shows these exact authenticated edge pixels with transparent interior. Image3 is approved painting style only.
The tile geometry is complete, but there are small kinks where the inner painting meets the authentic edge. Redraw the nearby inner contours to match those exact right and bottom endpoints smoothly. On the right, the upper long ivory rail and the muted beige inset below it must meet the existing right edge at their precise positions and widths. The middle diagonal rail must keep its single highlight and groove. At the bottom, the slate-gray stone top-right bevel and the adjacent diagonal ivory rail must connect continuously into the visible exact bottom strip; remove the diagonal step without changing rail width or inventing another groove. The lower-left inset MUST remain one slate-gray stone, all the way to its real diagonal frame: no tan triangle, no horizontal ledge.
Keep the final outer54 pixels along the right and bottom absolutely unchanged as positional anchors. Preserve the central and upper-left stone arrangement and all real stone seams. Adjust only nearby continuous contours and local shading to bridge the supplied native pixels. Do not blur away a seam, double any edge, change scale/camera, or introduce cracks, noise, text, objects or extra decoration. Retain bright clean rounded Daoist Q handpainted ivory and slate stone. Return opaque1254 by1254 pixels, same exact crop.'''
(R/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(R/'seam-target.png'),str(D/'context.png'),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False}
(R/'request.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'seam-target.png.generation.json').write_text(json.dumps({'file':str(R/'seam-target.png'),'sha256':sha(R/'seam-target.png'),'operation':'1:1 hard placement of authenticated context over repaired native AI pixels, for AI seam redrawing only','derivedFrom':[{'file':str(p),'sha256':sha(p)} for p in (D/'repair-v1/native.png',D/'context.png')],'newModelCalls':0,'nativeScale':1,'formalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
(D/'final-v1/review-rejected.json').write_text(json.dumps({'localVisualAccepted':False,'image':{'file':str(D/'final-v1/joined.png'),'sha256':sha(D/'final-v1/joined.png')},'findings':['Upper-right bands show small double/kink from unregistered native profiles.','Bottom diagonal slate bevel shows visible step within nativey1139..1200. Requires AI redrawing before any assembly acceptance.'],'proposedNext':'actual AI seam redraw using exact context'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(payload))
