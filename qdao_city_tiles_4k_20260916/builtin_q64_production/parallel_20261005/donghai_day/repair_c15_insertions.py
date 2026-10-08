"""Prepare and record native corrections to observed insertion-boundary defects."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;T=R/'r08_c15';S=T/'repairs/consolidated/candidate.png';D=T/'repairs/insertion-boundaries';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
EXPECTED='da5d4547ccff249545efc387f6fd0b4ebb88519dc98cbda1c4943b7fc8f13c1f'
BOXES={'right-upper':[2842,2048,4096,3302],'right-lower':[2842,2842,4096,4096],'water-right':[1600,2842,2854,4096],'water-left-horizontal':[0,2642,1254,3896]}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prep(name):
 assert sha(S)==EXPECTED
 d=D/name;d.mkdir(parents=True,exist_ok=True);target=d/'input.png';assert not target.exists()
 with Image.open(S) as im:im.crop(BOXES[name]).save(target)
 js(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'source':{'file':str(S),'sha256':EXPECTED},'sourceRectXYXY':BOXES[name],'rawSourceRGBSha256':hashlib.sha256(Image.open(target).convert('RGB').tobytes()).hexdigest(),'operation':'exact native crop of reviewed candidate; no resize','pixels':[1254,1254]})
 defect=('The artificial jagged vertical boundary lies around local x=700 to 840. It crosses the continuous blue painted board and warm brown hull. Unify only that artificial boundary; reconnect each existing board tone and grain naturally across it. Do not remove legitimate diagonal board contours, narrow blue bevels, dark boat contact strip or shadows.' if name.startswith('right') else 'The artificial jagged vertical boundary lies around local x=530 to 640. It divides the continuous quiet water into light/dark blocks. Unify only that artificial boundary with smoothly continuous broad soft water fields. Keep the existing broad directional water reflections, but remove the vertical patch border. Add absolutely no small ripples or caustics.')
 if name=='water-left-horizontal':defect='The artificial straight HORIZONTAL water stitch is around local y545, extending from the left side toward x900. The upper bright broad wave stops at an implausibly straight horizontal cutoff. Reconnect the existing broad soft water reflections naturally across this horizontal cutoff without changing their general positions or adding waves. The whole region must remain quiet blue water with broad low-contrast soft fields. Do not add fine texture, micro ripples, foam, white glare or netlike caustics. Preserve every wooden post and dock silhouette exactly. Only correct the thin horizontal water stitch; all outer context should stay identical.'
 prompt='Use case: precise-object-edit. IMAGE 1 is the exact native 1254x1254 edit target. '+defect+' The repair must be local: retain the original pixels, colors, exposure, shapes and all objects on both sides outside a roughly 200-pixel-wide strip around the defect. The outermost 200 pixels on all sides must match IMAGE 1 exactly; do not globally repaint or lighten any material. The existing blue water, if visible, remains quiet with broad soft low-contrast shapes. Preserve every boat edge, post, rope, rail and narrow waterline contour in its exact location and width. No new details, textures, nails, plank boundaries, ornaments, reflections, microtexture, foam, text or crop. IMAGE 2 is confirmed Q-style material reference only, do not copy UI. Return a single opaque 1254x1254 corrected IMAGE 1. Highest available finish. Do not change the whole picture: only make the visible jagged material patch edge disappear.'
 (d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[{'file':str(target),'sha256':sha(target),'role':'exact native edit target; preserve entire outer 200px and correct only local boundary'}, {'file':str(STYLE),'sha256':sha(STYLE),'role':'confirmed rounded clean Q-style finish only'}];js(d/'references.json',refs)
 print(json.dumps({'prompt':prompt,'references':[x['file'] for x in refs]}))
def record(name,src):
 d=D/name;out=d/'edited-native.png';src=Path(src);assert not out.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,out);refs=load(d/'references.json');meta=load(Path(str(d/'input.png')+'.generation.json'))
 js(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality selector or returned evidence exposed.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'baselineCandidate':meta['source'],'sourceRectXYXY':BOXES[name],'formalAccepted':False})
 print(json.dumps({'file':str(out),'sha256':sha(out)}))
if sys.argv[1]=='prepare':prep(sys.argv[2])
elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])
