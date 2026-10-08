"""Create native water seam edit targets; final composition is performed by root."""
from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r08_c15';BASE=T/'output/r08_c15.png';STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
EXPECTED='41cd6b8daffcee9e67069688f5b3d5150fbf7576975545ee2287cac44201f50b'
S={
'g-left-insertion':([600,2842,1854,4096],[[850,2950,1600,4096]]),
'e-hull-waterline':([397,1421,1651,2675],[[850,1880,1240,2250]]),
'f-lantern-blueboard':([1421,1421,2675,2675],[[1840,1800,2630,2300]]),
'a-left-cross':([397,1950,1651,3204],[[860,2020,1200,3130],[860,2920,1590,3165]]),
'b-right-cross':([1400,2460,2654,3714],[[1460,2920,2230,3250],[1880,2670,2240,3650]]),
'c-left-bottom':([397,2842,1651,4096],[[860,3060,1200,4096]]),
'd-right-bottom':([1421,2842,2675,4096],[[1880,3540,2240,4096]])}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return dict(file=str(p),sha256=sha(p))
name=sys.argv[2];D=T/'repairs/water-seams'/name;D.mkdir(parents=True,exist_ok=True);box,rois=S[name]
if sys.argv[1]=='prepare':
 assert sha(BASE)==EXPECTED
 im=Image.open(BASE).convert('RGB').crop(box);assert im.size==(1254,1254);im.save(D/'input.png')
 refs=[dict(ref(D/'input.png'),role='exact current native water seam crop; edit target'),dict(ref(STYLE),role='confirmed rendering style only; no UI')]
 save(D/'references.json',refs);save(D/'input.png.generation.json',dict(ref(D/'input.png'),operation='native crop without resampling',derivedFrom=[ref(BASE)],sourceRectXYXY=box,rawSourceRGBSha256=hashlib.sha256(im.tobytes()).hexdigest(),intendedRepairRectsXYXY=rois))
 prompt='Use case: precise-object-edit. IMAGE 1 is an exact native crop of current Q-style fishing-village blue seawater with unwanted straight and jagged rectangular patch boundaries. Repair ONLY the artificial vertical/horizontal color and wave-pattern discontinuities in the WATER. Make broad blue and cyan wave shapes flow naturally across the seams, smoothly matching the colors on both sides. Keep the current overall daylight color and restrained broad painted wave rhythm. Do NOT brighten the water, add pale or white cellular/net-like reflections, foam, fine texture, objects or decoration. Preserve any pictured brown boat hull, cyan waterline, wooden dock, mooring post and their silhouettes exactly. Preserve existing genuine hull-cast shadows and the large overall light/dark progression; remove only seam-shaped discontinuities. Keep every outer edge, framing and scale unchanged. IMAGE 2 is the user-confirmed clean rounded hand-painted material style, no UI. One opaque native 1254x1254 image, no resize, no text, no border. Only local seam cleanup, no new painting style or global relighting.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');print(json.dumps(dict(name=name,prompt=prompt,references=[r['file'] for r in refs],sourceRectXYXY=box,intendedRepairRectsXYXY=rois)))
elif sys.argv[1]=='record':
 src=Path(sys.argv[3]);im=Image.open(src);im.load();assert im.size==(1254,1254);dst=D/'edited-native.png';assert not dst.exists();shutil.copyfile(src,dst);refs=json.loads((D/'references.json').read_text(encoding='utf-8'))
 save(Path(str(dst)+'.generation.json'),dict(ref(dst),width=1254,height=1254,format='PNG',generatedAt=datetime.now(timezone.utc).isoformat(),timestampMeaning='locally observed completion',tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[r['file'] for r in refs]),actualModel=None,actualQuality=None,unverifiedReason='Host exposes neither selectors nor actual model/quality metadata.',evidence=dict(toolResultSourcePath=str(src),toolResultSha256=sha(src)),prompt=str(D/'prompt.txt'),promptSha256=sha(D/'prompt.txt'),references=refs,resizedAfterGeneration=False,finalArtUpscaled=False,sourceRectXYXY=box,intendedRepairRectsXYXY=rois,formalAccepted=False))
 print(json.dumps(dict(name=name,**ref(dst),sourceRectXYXY=box,intendedRepairRectsXYXY=rois)))

