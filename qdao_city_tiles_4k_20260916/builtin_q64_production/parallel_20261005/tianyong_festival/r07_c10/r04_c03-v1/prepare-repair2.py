from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).parent;R=D/'repair-v2';R.mkdir(exist_ok=True)
A=np.array(Image.open(D/'repair-v1/target.png').convert('RGBA'))
A[760:1120,40:660]=0
Image.fromarray(A).save(R/'context.png')
prompt='''Use case: precise-object-edit / inpainting. Return the SAME 1254x1254 square, no zoom or scale change. Image 1 is the precise edit target. Paint ONLY the transparent rectangle x40..660, y760..1120. All other pixels define the exact required geometry. Image 2 is style only, no UI.
The hole crosses a diagonal narrow ivory stone bevel strip, separating two broad stone paving slabs. Complete the exact strip that emerges from the TOP of the hole and continues into the existing BOTTOM of the hole. The bottom edge endpoints and the rounded junction at y1140..1175 are authoritative and must stay at their exact positions. The upper-right tan side of this strip should align with x528 at y1130, and extrapolate to approximately x447 at y1030, not the obsolete x420 location. Extend its connected left bright edge naturally with constant strip width. Render ONE clear edge each side, no duplicated shadows. Preserve the narrow diagonal crossing groove toward the bottom. All stone slabs remain continuous, no rectangular added seams at the transparency boundary. Match the native warm ivory, smooth rounded Q-game architecture and subtle existing handpainted material. Paint the missing structure sharply; no blur, no altered tiles outside the hole, no new decoration.'''
base=json.loads((D/'request.json').read_text(encoding='utf8'))
req={'payload':{'prompt':prompt,'referenced_image_paths':[str(R/'context.png'),r'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False},'configSnapshot':base['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None}
(R/'request.json').write_text(json.dumps(req,indent=2),encoding='utf8')
(R/'prompt.txt').write_text(prompt,encoding='utf8')
print(json.dumps(req))
