from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c02-v1/lower-repair-v3');D.mkdir(exist_ok=True)
P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((909,909,2163,2163)))
first=np.array(Image.open(P/'native.png').convert('RGBA'))
raw=np.array(Image.open(P/'lower-repair-v2/native.png').convert('RGBA'))
raw[:900]=first[:900]
raw[:230]=c[:230]
raw[1170:]=c[1170:]
raw[875:1170,:560]=0
Image.fromarray(raw).save(D/'context.png')
prompt="""Use case: precise-object-edit. Fill ONLY the transparent lower-left rectangle x0..559,y875..1169 of this 1254x1254 native painted game map. Keep all visible original pixels fixed, do not scale, crop, change camera, add new stones or shift any outlines.
In the opening continue the narrow ivory frame seen entering at x75..165 along its TOP boundary y875. This is ONE SINGLE narrow diagonal ivory frame, width about65pixels, with its right edge progressing from x163,y875 to approximately x205,y1095. To its right is one plain broad ivory panel, with NO EXTRA PARALLEL VERTICAL FRAME. Its lower edge is the existing thin horizontal beveled edge continuing from the visible panel at x560,y1080. The lower edge and narrow left frame meet cleanly in a single rounded corner. Under that panel are the exact three slate gray inset stones and narrow ivory bars already visible below the opening. Extend these lower stones up to the single separating horizontal stone joint at roughlyy1095, matching exact visible columns below. No new horizontal ledge, rail, stripe, covering bar, or extra vertical ivory pillar. Make just the one coherent original panel frame and clean gray stone insets. Preserve original warm ivory, gray inset colors, shadows, highlights, sculpted finish. No words, UI, objects or symbols. Second image is painting-style reference only."""
refs=[D/'context.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'references':[info(p) for p in refs],'sourceCheckpoint':info(T/'source-checkpoint.json'),'sourceCandidate':cp['fragment'],'configSnapshot':json.loads((P/'request.json').read_text(encoding='utf-8'))['configSnapshot'],'repairMaskLTRB':[0,875,560,1170],'windowTileLocalLTRB':[909,909,2163,2163]}
(D/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps(req))

