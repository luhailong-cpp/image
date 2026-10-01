"""Offline packaging only. Never synthesizes, mirrors or interpolates poses."""
import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
DIRS=['N','NE','E','SE','S','SW','W','NW']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 config=json.loads((ROOT/'export-config.json').read_text(encoding='utf-8'))
 frames=[]; problems=[]
 for direction in DIRS:
  selected=config['selectedSources'].get(direction,{})
  for n in range(1,17):
   key=f'{n:02}'
   if key not in selected:continue
   src=(ROOT/selected[key]).resolve()
   if not src.is_relative_to(ROOT):raise ValueError('source must be inside role')
   recpath=Path(str(src)+'.generation.json');rec=json.loads(recpath.read_text(encoding='utf-8'))
   im=Image.open(src);im.load()
   if min(im.size)<1024 or im.mode!='RGBA':raise ValueError('native HD/RGBA requirement failed: '+str(src))
   if sha(src)!=rec['sha256']:raise ValueError('source changed')
   # This one global full-canvas transform never uses current-frame alpha bounds.
   # It is established once against the reference and remains identical for every pose.
   scale=config['normalizedScale'];size=round(1024*scale)
   tile=im.resize((size,size),Image.Resampling.LANCZOS)
   out=Image.new('RGBA',(1024,1024));out.alpha_composite(tile,tuple(config['translationPx']))
   dest=ROOT/'candidate/walk'/direction/(key+'.png');dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
   a=out.getchannel('A');bbox=a.point(lambda v:255 if v>8 else 0).getbbox()
   item={'direction':direction,'frame':n,'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'width':1024,'height':1024,'mode':'RGBA','nativeWidth':im.width,'nativeHeight':im.height,'source':src.relative_to(ROOT).as_posix(),'sourceSha256':rec['sha256'],'generationRecord':recpath.relative_to(ROOT).as_posix(),'alphaExtrema':a.getextrema(),'bboxAlphaGt8':bbox,'pixelSha256':hashlib.sha256(out.tobytes()).hexdigest(),'operation':{'type':'uniform_full_canvas_downscale_and_constant_translation','scale':size/im.width,'translationPx':config['translationPx'],'framewiseBoundingBoxAlignment':False,'poseSynthesis':False},'rootPx':[512,942],'pivotUnity':[0.5,0.08],'visualStatus':'pending_dynamic_review'}
   dump(Path(str(dest)+'.generation.json'),{'file':item['file'],'sha256':item['sha256'],'derivedFrom':{'file':item['source'],'sha256':item['sourceSha256'],'generationRecord':item['generationRecord']},'operation':item['operation'],'actualModel':rec['actualModel'],'actualQuality':rec['actualQuality']})
   if not bbox or min(bbox[:2])<=0 or max(bbox[2:])>=1024:problems.append({'frame':item['file'],'problem':'empty_or_clipped'})
   if a.getextrema()!=(0,255):problems.append({'frame':item['file'],'problem':'alpha_range'})
   frames.append(item)
 expected=[{'direction':d,'frame':i,'file':f'candidate/walk/{d}/{i:02}.png'} for d in DIRS for i in range(1,17)]
 have={(r['direction'],r['frame']) for r in frames}
 missing=[e for e in expected if (e['direction'],e['frame']) not in have]
 manifest={'schemaVersion':1,'character':'02_fire_talisman_boy','status':'candidate_incomplete' if missing else 'candidate_pending_dynamic_review','frameDurationMs':30,'cycleDurationMs':480,'targetFrameCount':128,'exportedFrameCount':len(frames),'frames':frames,'missingFrames':missing,'exportConfig':'export-config.json','rootPx':[512,942],'pivotUnity':[0.5,0.08],'suggestedRunPixelsPerUnit':104,'clientIntegrated':False,'runtimeAccepted':False}
 dump(ROOT/'manifest.json',manifest)
 dump(ROOT/'validation.json',{'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exportedCount':len(frames),'missingCount':len(missing),'problems':problems,'scope':'file_geometry_alpha_hash_only_not_art_acceptance'})
 for d in DIRS:
  rows=[r for r in frames if r['direction']==d]
  if not rows:continue
  contact=Image.new('RGB',(1024,4*288),(40,48,49));draw=ImageDraw.Draw(contact)
  for i,r in enumerate(rows):
   thumb=Image.open(ROOT/r['file']).resize((256,256),Image.Resampling.LANCZOS)
   x=(i%4)*256;y=(i//4)*288
   contact.paste(thumb,(x,y),thumb);draw.text((x+8,y+260),f'{d}/{r["frame"]:02}',fill='white')
  path=ROOT/'preview'/(d+'-contact.png');path.parent.mkdir(parents=True,exist_ok=True);contact.save(path)
  dump(Path(str(path)+'.generation.json'),{'derivedFrom':[{'file':r['file'],'sha256':r['sha256']}for r in rows],'operation':'contact_sheet_downscale_for_review_only','newGeneration':False})
  if len(rows)==16:
   for duration,name in [(30,'normal'),(120,'slow')]:
    ims=[]
    for r in rows:
     im=Image.open(ROOT/r['file']).resize((400,400),Image.Resampling.LANCZOS);bg=Image.new('RGBA',(400,400),(40,48,49,255));bg.alpha_composite(im);ims.append(bg)
    path=ROOT/'preview'/f'{d}-{name}.png'
    ims[0].save(path,save_all=True,append_images=ims[1:],duration=duration,loop=0,format='PNG')
    dump(Path(str(path)+'.generation.json'),{'derivedFrom':[{'file':r['file'],'sha256':r['sha256']}for r in rows],'operation':'animated_png_review_only','frameDurationMs':duration})
 print(json.dumps({'exported':len(frames),'missing':len(missing),'problems':problems}))
if __name__=='__main__':main()

