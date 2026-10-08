from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c02-v1/lower-repair-v2');D.mkdir(exist_ok=True)
P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
assert sha(T/'source-checkpoint.json')=='be5236befc3ae8bbb65a66bc7304cb6827a53d730fb630ba9e2a63ebaad1dbf2'
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((909,909,2163,2163)))
raw=np.array(Image.open(P/'native.png').convert('RGBA'))
raw[:230]=c[:230]
raw[1120:]=c[1120:]
raw[900:1120]=0
Image.fromarray(raw).save(D/'context.png')
prompt="""Use case: precise-object-edit. Complete only the missing transparent horizontal strip y900..1119 in the first 1254x1254 image, using the second image only as a composition guide and third as painting-style reference. Keep exactly the same framing, canvas, scale, perspective, stone colors and every visible original edge.
This is a cropped top-down Chinese Daoist Q game plaza. Smooth rounded clean warm ivory sculpted stone, soft golden beige shadows, slate gray insets. At the top-left the existing cloud relief and transverse frame are finished and must not change. The broad plain ivory panel below the cloud is bounded on its right by a narrow dark recessed joint, then a separate vertical curving ivory ring course, then a broad warm gray concentric channel at the right. Continue all these courses DOWNWARD through the missing strip with exactly their existing curvature, width and tangent. The plain panel right edge is approximately x900 at y900, and smoothly reaches about x980 near y1060. DO NOT expand the central panel across the right ivory course. Preserve the separate ring course around x990..1180 at the bottom and the outer channel near the right edge.
The missing strip ends in the existing row of THREE gray stone insets below y1120. Connect the upper curved courses and ivory panel smoothly to the exact top corners and separating narrow ivory bars of those visible gray insets. A single horizontal stone joint at around y1085 separates the entire upper courses from the gray insets. No extra covering ledge across the panel, no horizontal strip hiding missing vertical structure. Keep the exact visible lower gray stone columns and their colors. No text, UI, symbols, added ornaments, noise or blur. Native painted detail; no resize or sharpened low-resolution texture."""
refs=[D/'context.png',P/'layout-reference-only.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'references':[info(p) for p in refs],'sourceCheckpoint':info(T/'source-checkpoint.json'),'sourceCandidate':cp['fragment'],'configSnapshot':json.loads((P/'request.json').read_text(encoding='utf-8'))['configSnapshot'],'repairMaskLTRB':[0,900,1254,1120],'windowTileLocalLTRB':[909,909,2163,2163],'oldRepairRejectedReason':'v1 would deform correct rings to incompatible old lower panel; no generation result exists'}
(D/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps(req['payload']))

