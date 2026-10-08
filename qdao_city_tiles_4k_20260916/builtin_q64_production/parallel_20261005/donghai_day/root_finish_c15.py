from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r08_c15';D=T/'repairs/root-finishing'
P=T/'repairs/consolidated/candidate.png'
EXPECTED='da5d4547ccff249545efc387f6fd0b4ebb88519dc98cbda1c4943b7fc8f13c1f'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
S={'roof':([1421,0,2675,1254],[[1840,0,2290,630]]),'left-insertion':([1900,1651,3154,2905],[[2340,1720,2670,2840]])}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
name=sys.argv[2];F=D/name;F.mkdir(parents=True,exist_ok=True);box,rois=S[name]
if sys.argv[1]=='prepare':
 assert sha(P)==EXPECTED
 im=Image.open(P).convert('RGB').crop(box);im.save(F/'input.png')
 save(F/'input.png.generation.json',{'file':str(F/'input.png'),'sha256':sha(F/'input.png'),'operation':'exact native crop of frozen candidate','source':{'file':str(P),'sha256':sha(P)},'sourceRectXYXY':box,'rawSourceRGBSha256':hashlib.sha256(im.tobytes()).hexdigest(),'intendedRepairRectsXYXY':rois,'resized':False})
 refs=[{'file':str(F/'input.png'),'sha256':sha(F/'input.png'),'role':'native candidate crop edit target'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'primary user-confirmed material and rendering style, no UI'}]
 prompt='Edit IMAGE 1 only. Correct only the artificial narrow vertical join around x627 in the blue-painted timber surface and any adjoining wooden grain. Match the same materials and daylight continuously from both sides of that seam. Remove stepped/jagged image-patch boundaries and abrupt rectangular tonal switches. Preserve all real board contours, bevels, grain direction, cream ropes, golden wood, lanterns, windows and their exact pixel positions. Real cast shadows must remain at the same location and darkness, and no real diagonal shadow edge should be removed. Keep the outer150 pixels as close as possible to source colors. Do not globally relight, add objects, move edges, or create new plank joints. Image2 is only the confirmed clean rounded hand-painted style. Opaque native1254 square, same crop, no blur/resize/text/UI.'
 (F/'prompt.txt').write_text(prompt,encoding='utf-8');save(F/'references.json',refs)
 print(json.dumps({'name':name,'prompt':prompt,'references':[r['file'] for r in refs]}))
elif sys.argv[1]=='record':
 src=Path(sys.argv[3]);im=Image.open(src);im.load();assert im.size==(1254,1254);dst=F/'edited-native.png';assert not dst.exists();shutil.copyfile(src,dst)
 refs=json.loads((F/'references.json').read_text(encoding='utf-8'));prompt=F/'prompt.txt'
 save(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((R.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['file'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'No model/quality selector or returned metadata.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(prompt),'promptSha256':sha(prompt),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceRectXYXY':box,'intendedRepairRectsXYXY':rois})
 print(json.dumps({'file':str(dst),'sha256':sha(dst)}))
