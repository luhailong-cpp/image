from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((909,909,2163,2163)))
raw=np.array(Image.open(P/'native.png').convert('RGBA'))
raw[c[:,:,3]==255]=c[c[:,:,3]==255]
raw[600:1024]=0
Image.fromarray(raw).save(O/'context.png')
prompt="""Use case: precise-object-edit. The first reference is an exact1254x1254 native paintedgame map edit target. Only its transparent middle-lower strip y600..1023 is missing; the other visible pixels are fixed original artwork. Complete this missing strip as a seamless continuation. Return same1254x1254 opaque image with no crop/scale/camera changes.
The upper part has an ivory cloud relief panel and diagonally curving concentric ivory stone courses. The bottom230rows are the authoritative lower neighbor: a large single broad plain ivory panel with a bevel whose RIGHT SIDE is at aboutx1190,y1024, then the established three gray inset columns belowy1085. Connect the upper diagonal ivory courses smoothly and naturally to those exact visible bottom endpoints. The central broad ivory panel must reach the full existing width of the lower neighbor. The right course continues outward toward the right frame edge as it descends. Join the left slanted frame to its lower endpoint nearx120,y1024. Continue the existing single crossbar at the upper edge of the opening if needed.
Absolutely no new horizontal ledge alongy1024, no strip obscuring a structural mismatch, no missing verticalcourses, no disconnected stone edges. No new gray tiles within the missing strip. Preserve every visible opaque stone edge, relief and shadow. Do not add any new joint or decoration.
The second input is the approved primary painting-style reference. Use its clean bright rounded full Daoist Q handpainted finish, warmivory and quiet gold. NoUI/text, no cracks/noisy veins/grunge, no blur. Newly render actualnative detail."""
refs=[O/'context.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'references':[info(p) for p in refs],'referenceRoles':['edit target with native bottom/sourceowned top','approvedprimarypaintingstyle'],'sourceCheckpoint':info(T/'source-checkpoint.json'),'sourceCandidate':cp['fragment'],'configSnapshot':json.loads((P/'request.json').read_text(encoding='utf-8'))['configSnapshot'],'repairMaskLTRB':[0,600,1254,1024],'windowTileLocalLTRB':[909,909,2163,2163]}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8');(O/'prompt.txt').write_text(prompt,encoding='utf-8');print(json.dumps(req['payload']))


