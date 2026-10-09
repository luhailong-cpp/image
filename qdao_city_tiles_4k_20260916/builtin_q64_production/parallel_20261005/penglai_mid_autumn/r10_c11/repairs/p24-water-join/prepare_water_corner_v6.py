from pathlib import Path
from PIL import Image
import json,hashlib,datetime
D=Path(__file__).resolve().parent/'water-corner-v6';D.mkdir(exist_ok=False);T=D.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(T/'plan.json');base=D.parent/'east-thin-v5/local-tone-sigma3/p24-proposal.png';north=T/'native/p14.png';east=Path(plan['eastCandidate']);style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
im=Image.new('RGBA',(1254,1254));im.paste(Image.open(north).convert('RGBA').crop((0,512,1254,1254)),(0,0));im.paste(Image.open(base).convert('RGBA').crop((0,230,1254,742)),(0,742));im.paste(Image.open(east).convert('RGBA').crop((0,397,115,1651)),(1139,0))
context=D/'context.png';im.save(context)
sources=[ref(base),ref(north),ref(east)]
mapping=dict(globalFrameXYWH=[43917,37261,1254,1254],nativeP24FrameXYWH=[43917,37773,1254,1254],nativeP24OffsetXY=[0,512],trueNorthOwnerBoundaryY=627,trueNorthOverlapEndY=742,trueEastBoundaryX=1139,operations=[dict(source=str(north),cropLTRB=[0,512,1254,1254],pasteXY=[0,0]),dict(source=str(base),cropLTRB=[0,230,1254,742],pasteXY=[0,742]),dict(source=str(east),cropLTRB=[0,397,115,1651],pasteXY=[1139,0])],holesLTRB=[[850,742,1139,860],[850,860,1015,1010]],realNorthAndEastNotMasked=True,sourceUpscaling=False)
write(str(context)+'.generation.json',dict(**ref(context),derivedFrom=sources,operation=mapping,actualModel=None,actualQuality=None,nativeScale=1,approvedForPromotion=False))
for box in mapping['holesLTRB']:im.paste((0,0,0,0),tuple(box))
target=D/'target.png';im.save(target);write(str(target)+'.generation.json',dict(**ref(target),derivedFrom=[ref(context)],operation=dict(clearRGBAHolesLTRB=mapping['holesLTRB'],allOtherPixelsUnchanged=True),actualModel=None,actualQuality=None,nativeScale=1,approvedForPromotion=False))
prompt='Use case: precise-object-edit. Fill ONLY the two small connected transparent patches in Image1, in this exact1254x1254 crop. These are a small section of cobalt water and the very edge of existing dark green leaves near the right side. Preserve the entire upper742rows exactly: these are the actual finished north neighbor. Preserve the entire right115px exactly: these are the actual finished east neighbor. Continue the visible cyan ripple edges smoothly downward and sideways through the missing area, without a little triangular arrow, a flat clipped wave tip, a ruler-straight seam, blue haze, or fuzzy patch over the leaf edge. The gap should be quiet painted water whose color and wave width match the immediate surrounding real water. Continue any partially cut leaf along its existing contour, without enlarging the tree or adding leaves. Everything outside the tiny transparent area is authoritative; keep all existing water-cell shapes, foliage and rock unchanged. Image2 is approved clean rounded hand-painted game STYLE only. Do not copy UI/text. No camera or crop change, no blur/glow/noise/extra detail. Fully opaque1254x1254 output.'
pp=D/'repair.prompt.txt';pp.write_text(prompt,encoding='utf8')
refs=[dict(**ref(target),role='native frame with deep true p14 north and actual c12 east fixed; only current-side L-gap transparent'),dict(**ref(style),role='approved painted style')]
call=dict(prompt=prompt,referenced_image_paths=[r['file'] for r in refs],transparent_background=False)
write(D/'repair.call.json',call);write(D/'repair.request.json',dict(preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=ref(context),sources=sources,sourceGeneration=ref(str(base)+'.generation.json'),plan=ref(T/'plan.json'),prompt=ref(pp),references=refs,mapping=mapping,submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read(Path('D:/work/image/config/image-generation.json')),actualModel=None,actualQuality=None,canonicalUnchanged=True))
print(target)
