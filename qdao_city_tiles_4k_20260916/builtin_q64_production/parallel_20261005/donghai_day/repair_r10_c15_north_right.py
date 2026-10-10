from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/north-right-joint'
BASE=T/'repairs/north-integrated-v2/candidate.png';EXPECTED='56aa9499341914dbf11e50fe2d405e768c5874120ee873dc8a4763ae00db40a7'
NORTH=R/'r09_c15/output/r09_c15.png';NSHA='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png';BOX=[2842,-627,4096,627];ROI=[3180,0,4096,627]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def prepare():
 assert sha(BASE)==EXPECTED and sha(NORTH)==NSHA;D.mkdir(parents=True,exist_ok=True)
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(NORTH).convert('RGB').crop([2842,3469,4096,4096]),(0,0));im.paste(Image.open(BASE).convert('RGB').crop([2842,0,4096,627]),(0,627));im.save(D/'input.png')
 masked=im.convert('RGBA');masked.paste((0,0,0,0),(300,627,1254,947));masked.save(D/'input-masked.png')
 save(D/'input.png.generation.json',{'file':str(D/'input.png'),'sha256':sha(D/'input.png'),'operation':'exact native north/core adjoining rectangles; no resize','sources':[{'file':str(NORTH),'sha256':NSHA,'sourceRect':[2842,3469,4096,4096],'destination':[0,0]},{'file':str(BASE),'sha256':EXPECTED,'sourceRect':[2842,0,4096,627],'destination':[0,627]}],'sourceRectXYXY':BOX,'rawSourceRGBSha256':hashlib.sha256(im.tobytes()).hexdigest(),'resized':False,'intendedRepairRectsXYXY':[ROI]})
 save(D/'input-masked.png.generation.json',{'file':str(D/'input-masked.png'),'sha256':sha(D/'input-masked.png'),'operation':'transparent repair gap cut from exact source; no resize','source':str(D/'input.png'),'sourceSha256':sha(D/'input.png'),'transparentLocalRectXYXY':[300,627,1254,947]})
 prompt='Use case: precise-object-edit. IMAGE 1 is the exact native 1254x1254 edit target with a transparent gap. IMAGE 2 is approved rounded clean Q-style hand-painted material reference only; copy no UI. Fill the transparent gap with the missing continuation of the EXISTING wooden vertical pier post and slanted bridge railing, and the small adjacent blue stone edge. The top 627 rows belong to a finished neighboring map tile and are the authoritative existing shape: continue its wooden pillar grooves, light/shadow faces and diagonal rail endpoints down into the lower part with exactly continuous silhouettes and smooth original material colors. The lower existing railing and pillar must join cleanly to those real upper endpoints, with no horizontal flat cutoff, step, extra cap or detached small beam at the gap top. Correct only the lower/new-tile area if necessary to connect those existing endpoints; keep the top finished area pixel-identical in composition. Preserve the existing turquoise water, brown capstone, blue-gray wall blocks, board count, grain direction, warm bright light, camera and original layout. Retain broad clean hand-painted shading, no extra grain, objects or grooves. The untouched lower and left surroundings determine the same material and geometry. Return the identical opaque 1254x1254 native crop with the hole completely filled; no transparency in result, resizing, global recolor, blur, text or frame.'
 refs=[{'file':str(D/'input-masked.png'),'sha256':sha(D/'input-masked.png'),'role':'native masked joint target; finished north627 authoritative, edit lower new tile only'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'approved rounded bright clean Q hand-painted material style'}]
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');save(D/'references.json',refs);print(json.dumps({'prompt':prompt,'references':[r['file'] for r in refs]}))
def record(src):
 src=Path(src);dst=D/'edited-native.png';assert not dst.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,dst);refs=read(D/'references.json')
 save(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['file'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; model and quality selectors and return metadata unavailable.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceRectXYXY':BOX,'intendedRepairRectsXYXY':[ROI]})
 print(json.dumps({'file':str(dst),'sha256':sha(dst)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='record':record(sys.argv[2])
