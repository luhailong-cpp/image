"""Check existing AI frames, create a truthful manifest and browser/contact previews."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,collections
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
CONTRACT={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
frames=[];missing=[];issues=[];groups=[]
qa=ROOT/'QA'; qa.mkdir(exist_ok=True)
for action,(count,ms) in CONTRACT.items():
 for direction in ['E','W']:
  group={'action':action,'direction':direction,'durationMs':ms,'expectedFrames':count,'frames':[]}
  for i in range(1,count+1):
   path=ROOT/'runtime'/action/direction/f'{i:02}.png'
   if not path.exists(): missing.append(path.relative_to(ROOT).as_posix());continue
   with Image.open(path) as im:
    assert im.mode=='RGBA',f'{path}: RGBA required'
    alpha=im.getchannel('A');hist=alpha.histogram(); box=alpha.point(lambda x:255 if x>16 else 0).getbbox()
    entry={'file':path.relative_to(ROOT).as_posix(),'action':action,'direction':direction,'frame':i,'durationMs':ms,'width':im.width,'height':im.height,'pivot':[0.5,0.08],'footAnchorTopLeft':[512,942],'event':'impact' if action=='attack' and i==7 else 'release' if action=='cast' and i==10 else None,'sha256':sha(path),'alpha':{'min':alpha.getextrema()[0],'max':alpha.getextrema()[1],'transparentPixels':hist[0],'partialPixels':sum(hist[1:255]),'opaquePixels':hist[255],'contentBBoxAlpha16':box},'generationRecord':f'generation/{action}/{direction}/{i:02}.generation.json','visualStatus':'pending sequence review','clientStatus':'not integrated or tested'}
    if im.size!=(1024,1024):issues.append({'file':entry['file'],'issue':'incorrect dimensions'})
    if hist[0]==0 or hist[255]==0:issues.append({'file':entry['file'],'issue':'alpha lacks fully transparent or opaque pixels'})
    if not (ROOT/entry['generationRecord']).exists():issues.append({'file':entry['file'],'issue':'generation record missing'})
    frames.append(entry);group['frames'].append(entry)
  groups.append(group)
  if group['frames']:
   size=320;cols=4;rows=(len(group['frames'])+cols-1)//cols
   sheet=Image.new('RGB',(cols*size,rows*(size+24)), '#e9e5da'); draw=ImageDraw.Draw(sheet)
   for k,frame in enumerate(group['frames']):
    x=k%cols*size;y=k//cols*(size+24)
    for yy in range(y,y+size,20):
     for xx in range(x,x+size,20):
      if ((xx-x)//20+(yy-y)//20)%2:draw.rectangle((xx,yy,xx+19,yy+19),fill='#cdd1cd')
    with Image.open(ROOT/frame['file']) as im:
     thumb=im.resize((size,size),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb)
    draw.text((x+10,y+size+4),f'{action} {direction} {frame["frame"]:02} / {ms}ms',fill='#183f36')
   sheet.save(qa/f'{action}-{direction}-contact.png')
duplicates=[paths for paths in collections.defaultdict(list).values()]
hashes=collections.defaultdict(list)
for f in frames:hashes[f['sha256']].append(f['file'])
duplicates=[v for v in hashes.values() if len(v)>1]
manifest={'character':'14-feierling','name':'绯耳灵','updatedAt':datetime.now(timezone.utc).isoformat(),'expectedFrameCount':68,'frameCount':len(frames),'directions':{'E':'front three-quarter southeast','W':'rear three-quarter northwest; independently generated'},'pivot':[0.5,0.08],'clientValidation':'not performed','frames':frames}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
check={'updatedAt':manifest['updatedAt'],'expected':68,'present':len(frames),'missing':missing,'issues':issues,'duplicateByteHashes':duplicates,'technicalChecksPassed':len(frames)==68 and not missing and not issues and not duplicates,'visualValidation':'pending, do not infer from technical result','clientValidation':'not performed'}
(qa/'technical-validation.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'SHA256SUMS.txt').write_text(''.join(f'{f["sha256"]}  {f["file"]}\n' for f in frames),encoding='utf-8')
template=(ROOT/'preview-template.html').read_text(encoding='utf-8')
(ROOT/'preview.html').write_text(template.replace('__GROUPS__',json.dumps(groups,ensure_ascii=False)),encoding='utf-8')
print(json.dumps({'present':len(frames),'missing':len(missing),'issues':issues,'duplicates':duplicates},ensure_ascii=False))
