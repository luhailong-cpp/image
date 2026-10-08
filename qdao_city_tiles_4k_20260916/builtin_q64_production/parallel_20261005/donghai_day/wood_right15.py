"""Native standalone right-side material-seam repairs; never overwrites tile/native sources."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent;T=R/'r08_c15';D=T/'repairs/wood-right';S=T/'output/r08_c15.png';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
EXPECTED='41cd6b8daffcee9e67069688f5b3d5150fbf7576975545ee2287cac44201f50b'
BOXES=[[2445,1651,3699,2905],[2445,2675,3699,3929]]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def init():
 assert sha(S)==EXPECTED,'Current output no longer matches task baseline.'
 D.mkdir(parents=True,exist_ok=True)
 with Image.open(S) as im:
  assert im.size==(4096,4096)
  for i,box in enumerate(BOXES,1):
   out=D/f'w{i}-baseline.png';assert not out.exists()
   im.crop(box).save(out)
   js(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'rawRGBSha256':hashlib.sha256(Image.open(out).convert('RGB').tobytes()).hexdigest(),'operation':'exact native crop, no resize','source':{'file':str(S),'sha256':EXPECTED},'sourceRectXYXY':box,'pixels':[1254,1254],'allowedAsFinalWholeTile':False})
 print('Two exact baseline crops saved.')
def prep(i):
 baseline=D/f'w{i}-baseline.png';target=D/f'w{i}-input.png';im=Image.open(baseline).convert('RGB');inputs=[{'file':str(baseline),'sha256':sha(baseline),'role':'exact initial tile native crop'}]
 if i==2:
  previous=D/'w1.png';assert previous.is_file()
  im.paste(Image.open(previous).crop((0,1024,1254,1254)),(0,0))
  inputs.append({'file':str(previous),'sha256':sha(previous),'role':'previous repaired native top 230px overlap'})
 im.save(target)
 js(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'operation':'exact native crop with optional previous repaired overlap','derivedFrom':inputs,'sourceRectXYXY':BOXES[i-1],'resized':False})
 prompt='''Use case: precise-object-edit. Edit IMAGE 1 only, an exact native-pixel crop of the existing fishing-boat side. Remove ONLY the artificial zigzag/straight material-color stitching break near x627, where the blue painted hull board and warm brown wooden hull change abruptly between neighboring image pieces. Those blocks are one continuous blue board and one continuous wooden hull, not separate colored planks at the vertical boundary. Reconnect each existing plank contour and its highlight/shadow naturally across the image join. Match the surrounding original warm brown wood, blue painted timber, and daylight volume; keep all major object outlines, perspective, existing board boundaries, ropes, rails and posts fixed. Do not redraw the layout or add details. Do not extend a water pattern into the boat.
Preserve the outer 150 pixels at left and right as exactly as possible and preserve the whole top/bottom field of view. Any sharp top overlap is an already repaired native context: keep it and continue naturally. If blue harbor water appears, retain the same quiet low-contrast broad blue/cyan fields; remove the stitch boundary but add no ripples, white glare, foam, netlike caustics or patterned microtexture. Existing boat contact highlight must retain its narrow original width and exact contour.
IMAGE 2 is primary user-confirmed rounded clean Q-style hand-painted material quality only, no UI. No new boat parts, metal collars, ornaments, nails, grain, cracks, extra plank divisions, objects, characters, text, borders, blur, crop, zoom or global exposure change. This is a local tonal-and-contour seam correction, not a whole-scene repaint. Return only one opaque 1254x1254 corrected image 1 at highest available finish.'''
 refs=[{'file':str(target),'sha256':sha(target),'role':'native edit target, x627 artificial vertical material break; already-sharp top overlap must be preserved'}, {'file':str(STYLE),'sha256':sha(STYLE),'role':'primary confirmed rounded Q-style and materials, no UI'}]
 (D/f'w{i}.txt').write_text(prompt,encoding='utf-8');js(D/f'w{i}.references.json',refs)
 print(json.dumps({'name':f'w{i}','prompt':prompt,'references':[x['file'] for x in refs]}))
def record(i,src):
 src=Path(src);out=D/f'w{i}.png';assert not out.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,out);refs=load(D/f'w{i}.references.json')
 js(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'timestampMeaning':'locally observed tool completion','tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no exposed selectors or returned model/quality metadata.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(D/f'w{i}.txt'),'promptSha256':sha(D/f'w{i}.txt'),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'baselineTile':{'file':str(S),'sha256':EXPECTED},'baselineCrop':{'file':str(D/f'w{i}-baseline.png'),'sha256':sha(D/f'w{i}-baseline.png')},'sourceRectXYXY':BOXES[i-1],'integrationStatus':'independent patch only; parent must validate source ROI after water reassembly before integration','formalAccepted':False})
 print(json.dumps({'file':str(out),'sha256':sha(out),'rect':BOXES[i-1]}))
if sys.argv[1]=='init':init()
elif sys.argv[1]=='prepare':prep(int(sys.argv[2]))
elif sys.argv[1]=='record':record(int(sys.argv[2]),sys.argv[3])
