"""Audit and preview the independently generated sprites; never synthesizes a pose."""
from pathlib import Path
import argparse, hashlib, json, math
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parent
SPEC={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def record_path(a,d,n):
 p=R/f'runtime/{a}/{d}/{n}.png.generation.json'
 return p if p.exists() else R/f'evidence/{a}/{d}/{n}.generation.json'
def native_path(j):
 return (j.get('native') or {}).get('path') or (j.get('derivedFrom') or {}).get('path') or j.get('sourcePath')
parser=argparse.ArgumentParser();parser.add_argument('--final-export',action='store_true');args=parser.parse_args()
frames=[];missing=[];errors=[];seen={};pixels={};groups=[]
preview=R/'preview';preview.mkdir(exist_ok=True)
for a,(count,ms) in SPEC.items():
 for d in 'EW':
  group=[]
  for i in range(1,count+1):
   n=f'{i:02d}';p=R/f'runtime/{a}/{d}/{n}.png';rp=record_path(a,d,n)
   if not p.exists(): missing.append(p.relative_to(R).as_posix());continue
   if not rp.exists(): errors.append('missing record '+str(p));continue
   j=json.loads(rp.read_text(encoding='utf-8-sig'))
   if args.final_export:
    src=Path(native_path(j));im=Image.open(src).convert('RGBA');original_sha=sha(p)
    # One identical transform per direction, shared by all three actions.
    # No per-frame bbox or foot alignment. Source canvas is always square.
    scaled=im.resize((922,922),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(1024,1024));offset=(24,55) if d=='E' else (30,55)
    canvas.alpha_composite(scaled,offset);canvas.save(p)
    j['preFinalExportSha256']=original_sha;j['finalExport']={'sourceNativePath':str(src),'sourceNativeSha256':sha(src),'sourceNativeSize':list(im.size),'scaledCanvasSize':[922,922],'offset':list(offset),'targetCanvasSize':[1024,1024],'direction':d,'sharedAcrossActions':True,'perFrameAlignment':False,'mirror':False,'createdPose':False,'filter':'LANCZOS'}
    j['sha256']=sha(p);j['width']=1024;j['height']=1024
    rp.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
   im=Image.open(p);alph=im.getchannel('A') if im.mode=='RGBA' else None;h=sha(p);ph=hashlib.sha256(im.tobytes()).hexdigest();bbox=alph.point(lambda v:255 if v>16 else 0).getbbox() if alph else None
   rel=p.relative_to(R).as_posix()
   if h!=j.get('sha256'):errors.append('record SHA mismatch '+rel)
   if im.size!=(1024,1024) or im.mode!='RGBA':errors.append('size/mode '+rel)
   if alph is None or alph.getextrema()!=(0,255):errors.append('alpha '+rel)
   if h in seen:errors.append('duplicate file '+rel+' / '+seen[h])
   if ph in pixels:errors.append('duplicate pixels '+rel+' / '+pixels[ph])
   seen[h]=rel;pixels[ph]=rel
   prompt=Path(j['prompt']);prompt=prompt if prompt.is_absolute() else R/prompt
   if not prompt.exists():errors.append('missing prompt '+rel)
   entry={'file':rel,'action':a,'direction':d,'frame':i,'durationMs':ms,'width':1024,'height':1024,'pivot':[0.5,0.08],'anchorTopOrigin':[512,942],'event':('impact' if a=='attack' and i==7 else 'cast_release' if a=='cast' and i==10 else None),'sha256':h,'pixelSha256':ph,'generationRecord':rp.relative_to(R).as_posix(),'alphaExtrema':list(alph.getextrema()) if alph else None,'visibleBBoxAlphaAbove16':bbox,'visualStatus':'pending-final-sequence-review','actualModel':j.get('actualModel'),'actualQuality':j.get('actualQuality')}
   frames.append(entry);group.append(entry)
  groups.append({'action':a,'direction':d,'expectedCount':count,'durationMs':ms,'frames':group})
  if group:
   thumb=320;cols=4 if count>6 else 3;rows=math.ceil(len(group)/cols);sheet=Image.new('RGB',(cols*thumb,rows*(thumb+28)),(224,228,220));draw=ImageDraw.Draw(sheet)
   anim=[]
   for k,f in enumerate(group):
    im=Image.open(R/f['file']).convert('RGBA');small=im.resize((thumb,thumb),Image.Resampling.LANCZOS);x=(k%cols)*thumb;y=(k//cols)*(thumb+28);sheet.paste(small,(x,y),small);draw.text((x+10,y+thumb+5),f'{a} {d} {f["frame"]:02d} / {ms}ms',fill=(25,50,40));anim.append(im.resize((512,512),Image.Resampling.LANCZOS))
   sheet.save(preview/f'{a}-{d}-all-frames.jpg',quality=94)
   if len(group)==count:
    for label,mul in [('normal',1),('slow',4)]:anim[0].save(preview/f'{a}-{d}-{label}.webp',save_all=True,append_images=anim[1:],duration=ms*mul,loop=0,lossless=True)
manifest={'character':'芽铃童','slug':'13-yalingtong','createdAt':datetime.now(timezone.utc).isoformat(),'expectedFrames':68,'frameCount':len(frames),'noMovementAnimations':True,'clientVerified':False,'actualModel':None,'actualQuality':None,'groups':groups,'frames':frames}
(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'SHA256SUMS.txt').write_text('\n'.join(f['sha256']+'  '+f['file'] for f in frames)+'\n',encoding='utf-8')
audit={'checkedAt':datetime.now(timezone.utc).isoformat(),'expectedFrames':68,'actualFrames':len(frames),'missing':missing,'errors':errors,'passed':len(frames)==68 and not missing and not errors,'uniqueFileHashes':len(seen),'uniquePixelHashes':len(pixels),'clientVerified':False,'visualAcceptance':'separate from technical audit'}
(R/'technical-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
(preview/'data.js').write_text('window.SPRITE_MANIFEST='+json.dumps(manifest,ensure_ascii=False)+';',encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False))
