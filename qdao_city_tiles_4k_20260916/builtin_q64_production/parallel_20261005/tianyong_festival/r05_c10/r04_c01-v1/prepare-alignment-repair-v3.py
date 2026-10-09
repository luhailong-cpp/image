from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");old=D/'alignment-repair-v2';R=D/'alignment-repair-v3';R.mkdir(exist_ok=True)
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
a=np.array(Image.open(old/'native.png').convert('RGBA'));src=np.array(Image.open(old/'source-composite.png').convert('RGBA'));a[789:,115:]=src[789:,115:];a[:789,1024:]=src[:789,1024:]
Image.fromarray(a).save(R/'source-composite.png')
mask=np.zeros((1254,1254),np.uint8);boxes=[[220,640,650,940],[630,700,1035,865],[960,0,1050,789]]
for l,t,r,b in boxes:mask[t:b,l:r]=255
target=a.copy();target[mask==255]=0;Image.fromarray(target).save(R/'edit-target.png');Image.fromarray(mask).save(R/'mask.png')
prompt="""Use case: precise-object-edit. This is a SMALL SEAM REPAIR on LAST IMAGE3 only, not a new outpaint or layout generation. Image1 approved Daoist Q style; image2 a nearby native foliage/material swatch, no composition. Image3 is the edit target.
Fill ONLY its three thin transparent gaps. Preserve ALL other opaque pixels exactly. Return identical1254x1254 crop with no reframing. The image already contains every correct object, position, material and shadow.
In the lower central gap, join the RED PLAQUE between its fixed top body and fixed bottom body. Its upper body is slightly left of its lower body: make a single smooth continuous silhouette joining those precise positions, with no double edges or translucency. The true lower accepted plaque left edge is x254 and right edge606, and its gold motifs are centered near x442. These lower positions are immovable. Let the repaired edge above meet them smoothly. The small gold floral motif must connect to the existing fixed portions, without a second ghost copy or misplaced petals. Keep the plaque edge red; no gold straight border. Do not replace the full plaque or move its bottom.
Other thin gaps join the existing stone planter, floor/soft cast shadow, ivory railing and bush. Bridge their existing contours, preserving every fixed leaf, wall and stone boundary on each side. No new plant, object, text, diagonal scratch, crack, bevel line, grunge or UI. Same polished bright rounded Q handpainted detail, no geometry warp, scaling or rotation. Keep all opaque pixels literally unchanged; repair only gaps."""
refs=[Path(r"D:/work/image/designs/gameplay-ui/04-guild.png"),D/'nearby-native-material-swatch.png',R/'edit-target.png']
req={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False};(R/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'preparation.json').write_text(json.dumps({'globalCropLTRB':[36749,19691,38003,20945],'sourceComposite':ref(R/'source-composite.png'),'sourceAI':ref(old/'native.png'),'sourceFixed':ref(old/'source-composite.png'),'masksLTRB':boxes,'references':[ref(p) for p in refs],'canonicalLayoutRetainedFrom':ref(old/'layout-reference-only.png'),'actualSubmittedModel':None,'actualSubmittedQuality':None,'configTarget':json.loads((D/'request.json').read_text(encoding='utf-8'))['configSnapshot']},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(req))

