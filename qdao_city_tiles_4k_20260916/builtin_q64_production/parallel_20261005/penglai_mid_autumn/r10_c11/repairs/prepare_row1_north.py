from pathlib import Path
from PIL import Image
import json,hashlib,datetime,sys
T=Path(__file__).resolve().parent.parent;R=T.parent;col=int(sys.argv[1]);version=sys.argv[2];label=f'p1{col}'
D=T/'repairs/row1-north'/label/version;D.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
plan=read(T/'plan.json');src=T/'native'/(label+'.png');east=Path(sys.argv[3]) if len(sys.argv)>3 else T/'native'/f'p1{col+1}.png';north=Path(plan['northCandidate']);style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
assert col in [2,3];x0=(col-1)*1024-115;im=Image.new('RGBA',(1254,1254));im.paste(Image.open(north).convert('RGBA').crop((x0,3469,x0+1254,4096)),(0,0));im.paste(Image.open(src).convert('RGBA').crop((0,115,1254,742)),(0,627));im.paste(Image.open(east).convert('RGBA').crop((0,115,230,742)),(1024,627));context=D/'context.png';im.save(context)
hole=[0,627,1024,847];im.paste((0,0,0,0),hole);target=D/'target.png';im.save(target)
content='rounded green foliage and blue-purple cliff rock' if col==3 else 'rounded golden leaves, adjacent green foliage and blue-purple cliff rock'
prompt=f'''Use case: precise-object-edit. Image 1 is an exact native 1254 by 1254 crop from a completed game map. Fill ONLY its transparent horizontal rectangle with the missing continuation of the EXISTING {content}. Every visible pixel above and beside the hole is fixed, authoritative art. The complete upper 627 rows show the true northern image; the right 230 columns show the already-finished eastern continuation. Complete each leaf and rock plane cut by the TOP of the hole, maintaining its exact contour endpoint, width, color and lighting at contact. The top edge of the hole must disappear into coherent surfaces, with no straight tone step or rectangular light/shadow stripe. Join precisely to the visible right and lower pieces, keeping existing leaf-cluster positions and the same rock silhouette, facets, cracks and highlights. Do not add leaf centers or move foliage, round the rock differently, add a new object or alter the broad cliff planes. Keep the clean rounded Daoist chibi paint, strong but controlled colors and night lighting. Image 2 is approved STYLE only; do not import UI or decorations. Do not retouch any visible area. Do not blur, sharpen, rotate, reflect, zoom or change the physical crop. Return the exact fully opaque frame.'''
pp=D/'repair.prompt.txt';pp.write_bytes(prompt.encode());call=dict(prompt=prompt,referenced_image_paths=[str(target),str(style)],transparent_background=False);write(D/'repair.call.json',call)
records=[T/'plan.json',src,Path(str(src)+'.generation.json'),north,east,Path(str(east)+'.generation.json')]
history=D/'text-history';history.mkdir();historical=[]
for p in [T/'plan.json',Path(str(src)+'.generation.json'),T/'native'/(label+'.request.json'),T/'native'/(label+'.call.json'),T/'native'/(label+'.prompt.txt')]:
 if p.exists(): q=history/p.name;q.write_bytes(p.read_bytes());historical.append(dict(source=ref(p),snapshot=ref(q)))
write(D/'repair.request.json',dict(preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=ref(context),sources=[ref(p) for p in records],plan=ref(T/'plan.json'),prompt=ref(pp),references=[ref(target),ref(style)],mapping=dict(globalFrameXYWH=[40960+x0,36237,1254,1254],northCropLTRB=[x0,3469,x0+1254,4096],nativeSourceCropLTRB=[0,115,1254,742],nativePasteXY=[0,627],eastCropLTRB=[0,115,230,742],eastPasteXY=[1024,627],holeLTRB=hole,allowedNativeOwnedY=[115,515],bottom230Immutable=True,sourcePixelScale=1),authorization=dict(reviewer='root',scope='NE p13 then p12 then p11 north repair; current tile y0..400; true north/p14 and native bottom230 immutable; proposals only before root key QA.'),textHistory=historical,submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read('D:/work/image/config/image-generation.json'),actualModel=None,actualQuality=None,canonicalUnchanged=True))
for p in [context,target]:write(Path(str(p)+'.generation.json'),dict(**ref(p),derivedFrom=[ref(src),ref(north),ref(east)],operation=ref(D/'repair.request.json'),actualModel=None,actualQuality=None,nativeScale=1))
print(D)
