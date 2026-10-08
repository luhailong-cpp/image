from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c03-v2/left-lower-repair-v1');D.mkdir(exist_ok=True);P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((P/'source-checkpoint-v015.json').read_text(encoding='utf-8'))
c=np.array(Image.open(P/'context-v015.png').convert('RGBA'))
n=np.array(Image.open(P/'native.png').convert('RGBA'))
n[c[:,:,3]==255]=c[c[:,:,3]==255]
n[900:1160,150:425]=0
Image.fromarray(n).save(D/'context.png')
prompt="""Use case: precise-object-edit. Fill only the single transparent rectangle x150..424,y900..1159 in this exact1254x1254 image. All visible pixels are fixed original artwork. Maintain exact scale, framing, camera and stone geometry. This is a native-painted top-down DaoistQ game plaza cropped close to ivory ring courses and warm gray recessed channel.
The missing lower-left rectangle contains the continuation of the SAME gray recessed vertical-curving channel from the top. Its broad gray surface must reach its rounded beveled FOOT near y1090 and join the top of the existing slategray inset row below. The surface must stay GRAY, matching the channel visible at the top and on the left. There is NO ivory plaque or cap across that gray channel, no extra horizontal cover strip, and no discontinuous highlighted square head. Continue its fine ivory bevel along the right side smoothly to the foot, and continue the narrow warm beige channel beside that bevel to the exact existing lower end. The adjacent broad ivory ring course to the right is already correct and should stay fixed. Match the left visible endpoint of the gray channel and foot near x150,y1090, then smoothly match the lower slate inset edge and separating ivory bar. Retain the three gray/ivory lower inset shapes exactly. Render only the small missing surface and smooth structural continuation. Do not add lines, ledges, ornaments, text, UI, new pavers or shadows. Second input is approved painting-style reference only. Bright clean rounded DaoistQ ivory/slate painted finish, actual native detail."""
refs=[D/'context.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'references':[info(p) for p in refs],'sourceCheckpoint':info(P/'source-checkpoint-v015.json'),'sourceCandidate':cp['fragment'],'configSnapshot':json.loads((P/'request.json').read_text(encoding='utf-8'))['configSnapshot'],'repairMaskLTRB':[150,900,425,1160],'windowTileLocalLTRB':[1933,909,3187,2163]}
(D/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8');(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps(req))

