from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/internal-wall'
BASE=T/'repairs/color-match/candidate.png';EXPECTED='a047f7b73c7890e6c0bf75e0d99c822508424e75ab091d12f1ca3814146003e5'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png';BOX=[350,2842,1604,4096];ROI=[730,2960,1480,4096]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def prepare():
 assert sha(BASE)==EXPECTED;D.mkdir(parents=True,exist_ok=True)
 im=Image.open(BASE).convert('RGB').crop(BOX);im.save(D/'input.png')
 save(D/'input.png.generation.json',{'file':str(D/'input.png'),'sha256':sha(D/'input.png'),'operation':'exact native source crop','source':{'file':str(BASE),'sha256':EXPECTED},'sourceRectXYXY':BOX,'rawSourceRGBSha256':hashlib.sha256(im.tobytes()).hexdigest(),'resized':False,'intendedRepairRectsXYXY':[ROI]})
 prompt='Use case: precise-object-edit. Edit IMAGE1 only. Repair the existing blue-gray masonry wall: an artificial perfectly vertical brightness/color cut runs near local x789 from roughly y250 downward through wall and blue water. There are also tiny jagged double-edge artifacts along the diagonal dark mortar joint in the upper third. These are IMAGE PATCH ERRORS, not real shapes. Remove that vertical division and those jagged mortar-edge pixels, making every existing stone face a continuous smooth controlled blue-gray painted volume and each existing diagonal mortar edge clean and continuous. Preserve exact positions and geometry of every original block, bevel, existing wooden post, water contact rim and cast shadow. Do not add or remove stone joints. All wall stone remains BLUE-GRAY as shown; do not recolor stone cream, white or golden. Retain original light direction and broad value gradient from the surrounding original image. Leave wooden post at left fixed; no new objects. Keep quiet blue water, with no additional ripple, foam, grid or texture. IMAGE2 is approved rounded bright clean Q-style hand-painted style only, no UI. Return opaque native1254x1254 identical crop, no resizing, blur filter, global relighting, text or border.'
 refs=[{'file':str(D/'input.png'),'sha256':sha(D/'input.png'),'role':'native wall edit target with fixed geometry'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'confirmed rounded hand-painted material style; no UI'}]
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');save(D/'references.json',refs)
 print(json.dumps({'prompt':prompt,'references':[r['file'] for r in refs]}))
def record(src):
 src=Path(src);dst=D/'edited-native.png';assert not dst.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,dst);refs=read(D/'references.json')
 save(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['file'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host exposes no model/quality selectors or returned version metadata.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceRectXYXY':BOX,'intendedRepairRectsXYXY':[ROI]})
 print(json.dumps({'file':str(dst),'sha256':sha(dst)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='record':record(sys.argv[2])
