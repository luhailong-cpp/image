"""Native final right edge/halo repair; east may change, west remains fixed."""
from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r08_c15';D=T/'repairs/right-halo-finish';S=T/'repairs/final-integration/extended-context.png';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
EXPECTED='7b8dda0b6a1d1f3a92e4bf0ff5ecf826b406449e38ba46be2ab97d12afe432ff';BOX=[3072,2905,4326,4159];GLOBAL=[2957,2790,4211,4044]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
 assert sha(S)==EXPECTED;D.mkdir(parents=True,exist_ok=True);p=D/'input.png';assert not p.exists()
 with Image.open(S) as im:im.crop(BOX).save(p)
 js(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'source':{'file':str(S),'sha256':EXPECTED},'sourceRectInExtendedXYXY':BOX,'sourceRectInTileAndRightHaloXYXY':GLOBAL,'rawSourceRGBSha256':hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest(),'resized':False,'operation':'exact native extended-context crop; includes 115px right halo'})
 prompt='Use case: precise-object-edit. Edit IMAGE 1 only, a native crop of a Q-style fishing boat side and blue harbor water. Correct the visible artificial VERTICAL jagged patch edge near local x=900 (about three quarters across), which creates a step through the warm brown hull planks, dark lower hull and narrow cyan water-contact stripe around local y=700. Those diagonal planks and the waterline must each become ONE smooth continuous contour from the LEFT existing segment to the RIGHT existing segment, across the artificial step. Keep the boat shape, perspective, wooden post, plank divisions, exact widths of dark lower hull and narrow cyan waterline. Retain the existing proper endpoints and angle at the left and right image borders. This is a precise local contour connection repair; fix the step, do not just soften it or paint a gradient over the broken line. Material color and grain should transition naturally at the same join. Preserve the original outer 120px at left/right and 150px top/bottom as exactly as possible. Preserve all blue water as the same quiet broad soft blue/cyan fields without adding ripples, microtexture, foam, glare or caustic nets. IMAGE 2 is the confirmed rounded clean Q-style material finish reference only, no UI. No added or removed objects, no shift of the post, new planks, nails, cracks, decoration, text, border, zoom, crop, blur or global relighting. Return one opaque native 1254x1254 corrected IMAGE 1 at highest available finish.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[{'file':str(p),'sha256':sha(p),'role':'exact native extended-context edit target; preserve endpoints and connect artificial stepped contour'}, {'file':str(STYLE),'sha256':sha(STYLE),'role':'confirmed Q-style rendering/material reference only'}];js(D/'references.json',refs);print(json.dumps({'prompt':prompt,'references':[x['file'] for x in refs]}))
def record(src):
 src=Path(src);out=D/'edited-native.png';assert not out.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,out);refs=load(D/'references.json')
 js(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'No exposed host selectors or returned model/quality evidence.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceRectInExtendedXYXY':BOX,'sourceRectInTileAndRightHaloXYXY':GLOBAL,'formalAccepted':False});print(json.dumps({'file':str(out),'sha256':sha(out)}))
if sys.argv[1]=='prepare':prepare()
elif sys.argv[1]=='record':record(sys.argv[2])
