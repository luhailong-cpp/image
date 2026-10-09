from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/east-guide-joint'
BASE=T/'repairs/north-integrated-v2/candidate.png';EXPECTED='56aa9499341914dbf11e50fe2d405e768c5874120ee873dc8a4763ae00db40a7'
EAST=R/'r10_c16/repairs/north-integrated-color-v3/candidate.png';ESHA='38f9ab047e8dccca8e49e2db392465f42d9447b5edcf4b2aa4d9432ea94304a4'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png';BOX=[3340,2842,4594,4096];ROI=[3780,3300,4096,4096]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def prepare():
 assert sha(BASE)==EXPECTED and sha(EAST)==ESHA;D.mkdir(parents=True,exist_ok=True)
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(BASE).convert('RGB').crop([3340,2842,4096,4096]),(0,0));im.paste(Image.open(EAST).convert('RGB').crop([0,2842,498,4096]),(756,0));im.save(D/'input.png')
 save(D/'input.png.generation.json',{'file':str(D/'input.png'),'sha256':sha(D/'input.png'),'operation':'exact native adjoining source rectangles; no resize','sources':[{'file':str(BASE),'sha256':EXPECTED,'sourceRect':[3340,2842,4096,4096],'destination':[0,0]},{'file':str(EAST),'sha256':ESHA,'sourceRect':[0,2842,498,4096],'destination':[756,0]}],'sourceRectXYXY':BOX,'rawSourceRGBSha256':hashlib.sha256(im.tobytes()).hexdigest(),'resized':False,'intendedRepairRectsXYXY':[ROI]})
 prompt='Use case: precise-object-edit. IMAGE 1 is the exact native 1254 by 1254 edit target. IMAGE 2 is the approved clean rounded Q-style hand-painted material reference only; do not copy its UI. In IMAGE 1 an artificial perfectly vertical splice at local x641 cuts through the lower blue-gray stone wall, from about local y400 to the bottom. This is an image patch fault, not a real joint: flat stone faces change tone abruptly there, and the existing slanted mortar grooves have small kinks where they cross that same vertical line. Repair only this fault within local x440..756 and y458..1254. Continue each existing blue-gray stone face smoothly across that vertical line, and connect each existing mortar groove into one clean continuous original curve without notches. Preserve every stone block, bevel, corner, highlight, original broad painted shading and all original geometry. Keep the rest of the image fixed, especially local x756..1254 on the right (neighboring map tile), the wooden post, rope, all cream paving, and top 350 pixels. Do not invent new blocks, grooves, cracks, grain, ornaments or objects. Do not recolor blue-gray stone cream. No global relighting or blur. Return the same opaque native 1254x1254 crop, no resize, no frame, no text.'
 refs=[{'file':str(D/'input.png'),'sha256':sha(D/'input.png'),'role':'native adjacent-tile edit target; right498 reference-only locked neighbor'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'approved rounded bright clean Q hand-painted material style'}]
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
