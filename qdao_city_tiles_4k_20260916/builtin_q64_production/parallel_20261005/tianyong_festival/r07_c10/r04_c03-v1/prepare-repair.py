from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;R=D/'repair-v1';R.mkdir(exist_ok=True)
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
N=np.array(Image.open(D/'native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
N[C[:,:,3]==255]=C[:,:,:3][C[:,:,3]==255]
Image.fromarray(N).save(R/'target.png')
prompt='''Use case: precise-object-edit. Fix one narrow diagonal stone bevel in this exact 1254 by 1254 image. Image 1 is the edit target. Image 2 is only approved painting style. Preserve the exact camera, pixel scale, broad paving shapes, lighting and all other grooves.
There is a visible mismatch in the lower-left diagonal ivory strip, within x230..590 and y860..1170: at y1024 its upper-right tan shadow edge and lower-left bright beveled edge step sideways because the lower part is the correct original. Redraw this single diagonal strip and its immediate two stone edges into a perfectly smooth constant-width continuation. The correct final lower end, its rounded corner and its crossing horizontal diagonal groove below y1130 MUST remain exactly in place; adapt the upper part smoothly to those lower endpoints. Do not keep a doubled parallel shadow line or the ghost of the old edge. Preserve the rest of the image identically, including the entire right-hand curved ring and right vertical context. No added seams, no retiled floor, no texture changes. Correct the structural edge by painting, not blur. Native crisp rounded Daoist Q stone relief, warm ivory, matching existing tonal finish. No text or border. Same 1254 square, no crop, no zoom.'''
req={'payload':{'prompt':prompt,'referenced_image_paths':[str(R/'target.png'),r'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False},'configSnapshot':json.loads((D/'request.json').read_text(encoding='utf8'))['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None},'sourceReferences':[ref(D/'native.png'),ref(D/'context.png')],'actualModel':None,'actualQuality':None}
(R/'request.json').write_text(json.dumps(req,indent=2),encoding='utf8');(R/'prompt.txt').write_text(prompt,encoding='utf8')
(R/'target.png.generation.json').write_text(json.dumps({'output':ref(R/'target.png'),'operation':'Exact known source overlay for single-band structural repair; hard boundaries intentionally visible as edit target','sources':req['sourceReferences'],'newModelCalls':0,'nativeScale':1,'formalAccepted':False},indent=2),encoding='utf8')
print(json.dumps(req))
