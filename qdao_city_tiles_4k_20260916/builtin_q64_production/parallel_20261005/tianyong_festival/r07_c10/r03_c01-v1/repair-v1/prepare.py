from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
D=Path(__file__).parent;P=D.parent
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
n=np.array(Image.open(P/'native.png').convert('RGBA'));c=np.array(Image.open(P/'context.png').convert('RGBA'))
n[1120:]=c[1120:];n[900:1120]=0;Image.fromarray(n).save(D/'context.png')
prompt='''Use case: precise-object-edit. Repair exactly the transparent horizontal band of this native 1254x1254 game-map crop. Image 1 is the target: upper 900 rows and lower 134 rows are authentic native pixels. Fill only missing rows 900 through 1119. Return opaque full square at identical scale. Join the existing downward-right ivory paving perimeter and narrow warm-gray bevel with straight continuous parallel contours and the same bevel thickness, connecting their exact upper and lower endpoints. Preserve the small cross joint between the two upper paving blocks; let it terminate naturally at the perimeter. There must be exactly one crisp upper highlight, one warm-gray bevel and its lower narrow rim: no second shadow line, ghost outlines, step, added notch or extra ledge. Preserve all visible upper and lower pixels and their colors. Blank-band boundaries are not physical seams. Image 2 is the approved style only, clean bright rounded Daoist Q handpainting; no text or UI. No crop, resize, zoom, new object, grain, cracks, marble veins or blur.'''
req=read(P/'request.json');req['preparedAtUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();req['payload']={'prompt':prompt,'referenced_image_paths':[str(D/'context.png'),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False};req['repairBandLTRB']=[0,900,1254,1120]
save(D/'request.json',req);(D/'prompt.txt').write_text(prompt,encoding='utf8')
save(D/'preparation.json',{'references':[ref(D/'context.png'),ref(Path('D:/work/image/designs/gameplay-ui/04-guild.png'))],'sources':[ref(P/'native.png'),ref(P/'context.png')],'contextNativeTopLTRB':[0,0,1254,900],'contextSourceBottomLTRB':[0,1120,1254,1254],'nativeScale':1,'noUpscale':True,'formalAccepted':False})
