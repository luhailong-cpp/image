from pathlib import Path
import json,hashlib,datetime
from PIL import Image
B=Path(__file__).resolve().parent
q=json.loads((B/'requests/r02_c04/s01_01-upper-wall-anchor-completion-v001.json').read_text(encoding='utf-8'))
source=B/'r02_c04/native/s01_01-v003.png'
im=Image.open(source).convert('RGB');neighbor=B/'r02_c04/native/s01_02-v003.png'
im.paste(Image.open(neighbor).convert('RGB').crop((115,115,230,1139)),(1139,115))
px=im.load()
for y in range(670,1120):
 for x in range(1040,1139):px[x,y]=(255,0,255)
slug='s01_01-east-leaf-gap-repair-v001';gp=B/'requests/r02_c04'/f'{slug}.guide.png';rp=gp.with_name(slug+'.json')
assert not gp.exists() and not rp.exists();im.save(gp)
q['prompt']='Use case: precise-object-edit. Repair ONLY the narrow MAGENTA missing-art patch in image1, x1040..1138,y670..1119. Repaint natural green leaf/branch continuations to join the existing left foliage to the sharp fixed neighboring leaves at x1139..1253. Leaf bodies and stems must connect naturally across x1139 with consistent shade and color, no vertical cut, no arbitrary crop, no dark rectangular stripe. Fill magenta with newly painted foliage. Preserve absolutely all pink blossoms, upper/right stone wall course geometry, bottom foliage and all outside pixels. Do not alter scene or lighting, do not add new branches crossing the whole picture. Same1254 square native opaque artwork. Ref2/3 are style only, NOUI/text. No magenta remains.'
q['referenced_image_paths']=[str(gp),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']
q['guide'].update(file=str(gp),sha256=hashlib.sha256(gp.read_bytes()).hexdigest(),guideOnly=True,productionNativeSource=False,editParent=str(source),editParentSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),maskedRegion=[1040,670,1139,1120])
q['createdAtUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
rp.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print(str(rp))

