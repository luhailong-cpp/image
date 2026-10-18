from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent
q=json.loads((B/'requests/r02_c04/s01_01-wallbase-leaf-rebuild-v001.json').read_text(encoding='utf-8'))
im=Image.open(B/'r02_c04/native/s01_01-v002.png').convert('RGB')
w=q['coordinates']['worldBoxWithHalo']
lay=Image.open(q['guide']['layout']).convert('RGB')
blur=lay.transform((1254,1254),Image.Transform.EXTENT,tuple(v*lay.width/65536 for v in w),resample=Image.Resampling.BICUBIC)
px=im.load();bp=blur.load()
for y in range(600):
 for x in range(750,1139):
  r,g,b=px[x,y]
  if not (g>r*.96 and g>b*1.3 and g>35):px[x,y]=bp[x,y]
for p in q['guide']['nativeContextPastes']:im.paste(Image.open(p['source']['file']).convert('RGB').crop(p['sourceCropLTRB']),tuple(p['guidePasteXY'][:2]))
slug='s01_01-upper-wall-anchor-completion-v001'
gp=B/'requests/r02_c04'/f'{slug}.guide.png';rp=gp.with_name(slug+'.json');assert not gp.exists() and not rp.exists()
im.save(gp)
q['prompt']='Use case: precise-object-edit. Complete the small BLURRED wall patch in the upper-right of image1, x750..1139,y0..600, connecting to sharp actual-neighbor pixels on right x1139..1253. Mortar first horizontal line MUST be y215, second y420; continue both LEFT from right anchor at exactly those heights behind the green leaves. Remove the old y180 line entirely. Preserve all blossoms, leaves, branches and the whole lower image. Only the stone visible between/above leaves in the upper-right needs repainting. Repair any cut green leaves precisely at x1139 into the sharp right-neighbor strip, preserving leaf shapes. Smooth stone material across x1139; sparse hand brush texture, no checkerboard/honeycomb. Do NOT redraw the whole image or change tree shape. Same1254 square opaque native artwork, no blur in finished result, no new objects/text. Reference2/3 style only.'
q['referenced_image_paths']=[str(gp),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']
q['guide'].update(file=str(gp),sha256=hashlib.sha256(gp.read_bytes()).hexdigest(),productionNativeSource=False,guideOnly=True,editParent=str(B/'r02_c04/native/s01_01-v002.png'),maskedRegion=[750,0,1139,600],maskPreservesGreenLeaves=True)
rp.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(rp))

