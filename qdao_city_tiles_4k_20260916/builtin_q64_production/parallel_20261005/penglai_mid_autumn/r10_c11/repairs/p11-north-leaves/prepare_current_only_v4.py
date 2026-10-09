from pathlib import Path
from PIL import Image
import json,hashlib,datetime
D=Path(__file__).resolve().parent/'current-only-v4';D.mkdir(exist_ok=False)
T=D.parents[2];base=D.parent/'north-leaves-v1.png';style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
plan=read(T/'plan.json');n=Path(plan['northCandidate'])
im=Image.open(base).convert('RGBA');im.paste(Image.open(n).convert('RGBA').crop((0,3469,1254,4096)),(0,0));context=D/'context.png';im.save(context)
hole=(0,627,1024,827);im.paste((0,0,0,0),hole);target=D/'target.png';im.save(target)
prompt='''Use case: precise-object-edit. Fill only the transparent rectangle in Image 1 with the missing parts of the EXISTING golden leaves. Exact native 1254 by 1254 frame. The complete upper 627 rows are finished authoritative art; copy their leaf edges, scale and lighting exactly. Every leaf cut off by the TOP edge of the hole must continue DOWNWARD in precisely the same width and color at that contact. The old top edge of this hole must disappear into continuous leaves: no ruler-straight lighting edge, clipped highlight or change of material. Match the visible LOWER leaf pieces too, completing their current contours without moving clusters or adding new centers. The warm platform and dark blue gap at the far left stay in place. Keep the leaf arrangement, rounded amber shapes, ochre shadows and subtle broad paint. Image 2 is approved art STYLE only, do not import UI or content. Do not alter any visible part of Image 1. Do not add extra flowers, leaves, veins, branches, rim glow or texture. Do not blur, rotate, reflect, enlarge, zoom out or crop. Return the same fully opaque image with the hole naturally completed.'''
pp=D/'repair.prompt.txt';pp.write_bytes(prompt.encode());call=dict(prompt=prompt,referenced_image_paths=[str(target),str(style)],transparent_background=False);write(D/'repair.call.json',call)
write(D/'repair.request.json',dict(preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=ref(context),sources=[ref(base),ref(n),ref(T/'native/p11.png'),ref(T/'native/p12.png')],plan=ref(T/'plan.json'),prompt=ref(pp),references=[ref(target),ref(style)],mapping=dict(globalFrameXYWH=[40960,36237,1254,1254],holeLTRB=list(hole),authoritativeNorthCropLTRB=[0,3469,1254,4096],authoritativeNorthPasteXY=[0,0],allowedNativeP11LTRB=[115,115,1139,515],nativePixelScale=1,sourceUpscaled=False),submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read('D:/work/image/config/image-generation.json'),actualModel=None,actualQuality=None,canonicalUnchanged=True))
print(target)
