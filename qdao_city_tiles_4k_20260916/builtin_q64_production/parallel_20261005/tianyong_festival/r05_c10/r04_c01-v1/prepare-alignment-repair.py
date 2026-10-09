from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");R=D/'alignment-repair-v1';R.mkdir(exist_ok=True)
base=D/'final-v1/joined.png';a=np.array(Image.open(base).convert('RGBA'))
boxes=[[0,940,1254,1200],[1000,0,1200,1200],[220,460,625,1200]]
for l,t,r,b in boxes:a[t:b,l:r]=0
Image.fromarray(a).save(R/'edit-target.png')
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
prompt="""Use case: precise-object-edit. Repair only the masked transparent areas of LAST IMAGE4, a1254x1254 native game map crop. Image1 approved style; image2 nearby native foliage/material swatch only; image3 the same-world canonical layout; image4 is the SINGLE EDIT TARGET.
Preserve every opaque target pixel in its original place. Reconstruct a coherent join between the fixed interior at the top/left and the narrow fixed bottom/right outer strips. The previous output displaced the plaque edges, gold ornament, leaves and rail end by about20pixels, producing double contours; eliminate all such duplicated outlines. No blending ghosts, no translucent leaves, no duplicated gold motifs.
The vertical red festival plaque should be one clean continuous panel aligned with the ACTUAL bottom strip: its sides around x250 and600. Extend those same edges upward to the remaining curled red crown. Match its existing polished red raised rim and embossed gold cloud/floral ornaments. The actual lower panel has no long gold border; keep the panel body border RED, with no long straight gold frame. Use gold only for the existing style of centered ornamental motifs. One motif continues seamlessly from the fixed gold petals in the bottom strip. Do not write characters.
Reconnect the cropped red-orange lantern at left naturally to its fixed lower outer portion, and the stone planter, ivory rail and leafy bush at right to their fixed outer strips. Smooth continuous silhouettes; only one leaf at each edge, only one wall edge, only one gold flower. Preserve camera, scale, object footprints and roof. Clean bright rounded polished Daoist Q material and lighting. No cracks, scratches, figures, UI, watermark, resizing, geometric warp or reframing. Return the same complete opaque native1254x1254 square."""
refs=[Path(r"D:/work/image/designs/gameplay-ui/04-guild.png"),D/'nearby-native-material-swatch.png',D/'layout-reference-only.png',R/'edit-target.png']
req={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
(R/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'preparation.json').write_text(json.dumps({'base':ref(base),'masksLTRB':boxes,'references':[ref(p) for p in refs],'actualSubmittedModel':None,'actualSubmittedQuality':None,'configTarget':json.loads((D/'request.json').read_text(encoding='utf-8'))['configSnapshot']},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(req))

