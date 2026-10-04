from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for d in ('S','SE','SW'):
 s=json.loads((R/f'review/run-{d}-selection.json').read_text('utf-8-sig'))
 images=[];refs=[]
 sheet=Image.new('RGB',(1024,1120),'#e5e1d9');draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(s['frames']):
  p=R/f['candidatePath'];assert sha(p)==f['candidateSha256']
  im=Image.open(p).convert('RGBA');assert im.size==(1024,1024)
  images.append(im.resize((256,256),Image.Resampling.LANCZOS))
  refs.append({'path':f['candidatePath'],'sha256':f['candidateSha256'],'sourcePath':f['sourcePath'],'sourceSha256':f['sha256']})
  screenshot=Image.open(R/f'review/south-{d}-step-{i+1:02}.png').convert('RGB')
  if screenshot.size!=(256,256):screenshot=screenshot.resize((256,256),Image.Resampling.LANCZOS)
  x=(i%4)*256;y=(i//4)*280;sheet.paste(screenshot,(x,y+24));draw.text((x+8,y+5),f'{d} {i+1:02} / {Path(f["sourcePath"]).stem}',fill='#25272b')
 out=R/f'review/south-{d}-1x-1200ms.webp'
 images[0].save(out,save_all=True,append_images=images[1:],duration=[75]*16,loop=0,lossless=True)
 with Image.open(out) as test:assert test.n_frames==16
 sheet.save(R/f'review/south-{d}-browser-step-contact.png')
 record={'kind':'derived_fullcanvas_animation_preview','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':out.relative_to(R).as_posix(),'sha256':sha(out),'canvasSize':[256,256],'frameDurationsMs':[75]*16,'cycleMs':1200,'operation':'Full 1024 RGBA canvas uniformly resized to256; lossless WebP. No crop, mirror, pose edit, interpolation or figure alignment.','derivedFrom':refs,'actualModel':None,'actualQuality':None,'modelEvidence':'See each bound native generation record; host did not disclose model or quality.'}
 Path(str(out)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated three final-source animations and browser step contact sheets.')
