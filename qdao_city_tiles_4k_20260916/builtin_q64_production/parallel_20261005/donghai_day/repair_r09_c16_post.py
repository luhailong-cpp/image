"""Single native edit for the small lantern backing-post joint."""
from pathlib import Path
import json,sys,shutil,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r09_c16';D=T/'repairs/post-tonal-fix'
BASE=T/'repairs/color-match-v2/candidate.png'
EXPECTED='093589a138671f1112dc25835f7857871bccbc44bf5a9df3a835e12cf63c6f96'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
BOX=[1536,2470,2790,3724]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
 assert sha(BASE)==EXPECTED and not (D/'edited-native.png').exists()
 D.mkdir(parents=True,exist_ok=True)
 target=D/'input.png'
 with Image.open(BASE) as im:im.crop(BOX).save(target)
 save(str(target)+'.generation.json',{'file':str(target),'sha256':sha(target),'operation':'unresized native crop','source':str(BASE),'sourceSha256':EXPECTED,'sourceRectXYXY':BOX,'pixels':[1254,1254]})
 prompt='Use case: precise-object-edit. IMAGE1 is the exact1254 square edit target, IMAGE2 is the approved bright rounded hand-painted Q-style material reference. Repair only the tiny seam defect in the brown wooden vertical backing post behind the red hanging banner at local x599..635,y605..685: a jagged diagonal color cutoff and a dark edge segment begin abruptly there. Make that brown wood face and its existing straight edge continue cleanly through this tiny join with the surrounding wood shading and grain. Also straighten the existing RED BANNER LEFT OUTLINE around local x462,y680 where it has a2-to3pixel step; keep the original silhouette and position, only remove the tiny splice kink. Preserve the exact red banner, lanterns, painted gold emblems, posts, water, perspective, all dimensions, lighting and palette. Do not add, remove, move, simplify or resize any lantern, motif, rope, timber, banner or other object. The seam is an accidental splice, not a plank boundary or new shadow. Do not repaint the rest of the crop. Keep all outer250 pixels unchanged. No new texture, lines, ripple, blur, crop, zoom, text or border. Output one opaque native1254x1254 image.'
 refs=[{'file':str(target),'sha256':sha(target),'role':'native local edit target'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'approved bright rounded hand-painted style only'}]
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');save(D/'references.json',refs)
 print(json.dumps({'prompt':prompt,'references':[x['file'] for x in refs]}))
def record(src):
 src=Path(src);out=D/'edited-native.png';assert not out.exists()
 with Image.open(src) as im:im.load();assert im.size==(1254,1254)
 refs=read(D/'references.json')
 for v in refs:assert sha(v['file'])==v['sha256']
 shutil.copyfile(src,out)
 save(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R.parents[3]/'config/image-generation.json'),
 'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},
 'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in tool exposes neither selectors nor returned version/quality metadata.',
 'evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':refs,'sourceRectXYXY':BOX,'resizedAfterGeneration':False,'finalArtUpscaled':False})
 print(json.dumps({'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='record':record(sys.argv[2])
