"""Build NW-only static review sheets from distinct native generated frames."""
from pathlib import Path
import argparse,hashlib,json,math
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parents[2]/'05-tools';GEN=HERE.parent/'05-generation';OUT=GEN/'NW-review'
VERSIONS={1:2,4:2,6:2,7:3,8:2,9:6,10:2,11:2}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--complete',action='store_true');a=p.parse_args();OUT.mkdir(exist_ok=True)
 rows=[];images=[]
 for n in range(1,17):
  archive=GEN/f'NW{n:02d}-single-v{VERSIONS.get(n,1)}';candidate=archive/'staging/candidate/05_celestial_musician_girl';output=candidate/f'walk/NW/{n:02d}.png'
  if not output.exists():continue
  im=Image.open(output).convert('RGBA');arr=np.asarray(im);yy,xx=np.where(arr[:,:,3]>8);top=int(yy.min());bottom=int(yy.max());height=bottom-top+1;axis=float(np.median(xx[yy<top+int((height-1)*.42)]))
  assert im.size==(1024,1024) and bottom==942 and abs(axis-512)<=.5
  rec=json.loads((candidate/'processing/frame-sources.json').read_text())[f'walk/NW/{n:02d}.png'];assert rec['common_scale']==.84 and rec['chroma_thresholds']==[50,75]
  rows.append({'frame':n,'slot':f'walk/NW/{n:02d}.png','output':str(output),'sha256':sha(output),'raw':str(archive/'raw.png'),'rawSha256':sha(archive/'raw.png'),'generationRecord':str(archive/'raw.png.generation.json'),'prompt':str(archive/'prompt.txt'),'receipt':str(archive/'generation-receipt.json'),'sourceMapping':str(candidate/'processing/frame-sources.json'),'validation':str(candidate/f'review/validation-NW-{n:02d}.json'),'nativeSize':rec['source']['native_size'],'outputSize':[1024,1024],'alphaBbox':[int(xx.min()),top,int(xx.max()+1),bottom+1],'visibleHeight':height,'anchor':[axis,bottom],'pixelSha256':hashlib.sha256(im.tobytes()).hexdigest(),'commonScale':.84,'chromaThresholds':[50,75],'actualModel':None,'actualQuality':None,'visualReview':'static_pending_root_loop'})
  images.append((n,im))
 if a.complete:assert len(rows)==16,'All 16 NW frames are required'
 for name,color,ink in [('dark','#202b38','white'),('light','#f0eee4','black')]:
  for kind in ['normal','legs']:
   tilew,tileh=(256,288) if kind=='normal' else (490,290)
   sheet=Image.new('RGB',(tilew*4,tileh*math.ceil(len(images)/4)),color)
   for i,(n,im) in enumerate(images):
    content=im.resize((256,256),Image.Resampling.LANCZOS) if kind=='normal' else im.crop((220,720,710,980))
    x=(i%4)*tilew;y=(i//4)*tileh;sheet.paste(content,(x,y+30),content);ImageDraw.Draw(sheet).text((x+8,y+8),f'NW{n:02d} / v{VERSIONS.get(n,1)}',fill=ink)
   dest=OUT/f'contact-{kind}-{name}.png';sheet.save(dest)
   write(dest.with_name(dest.name+'.generation.json'),{'file':str(dest),'sha256':sha(dest),'operation':'static-review-contact-sheet-only','derivedFrom':[{'file':r['output'],'sha256':r['sha256'],'generationRecord':r['generationRecord']} for r in rows],'generationCalls':0})
 report={'character':'05_celestial_musician_girl','direction':'NW','at':datetime.now(timezone.utc).isoformat(),'frameCount':len(rows),'frameDurationMs':30,'complete':len(rows)==16,'sourceDistinctCount':len({r['rawSha256'] for r in rows}),'pixelDistinctCount':len({r['pixelSha256'] for r in rows}),'rows':rows,'approval':False,'status':'static_candidates_pending_root_loop','canonicalModified':False}
 write(OUT/'snapshot.json',report)
 if a.complete:
  frames=[]
  for n,im in images:
   frame=Image.new('RGB',(512,544),'#202b38');small=im.resize((512,512),Image.Resampling.LANCZOS);frame.paste(small,(0,32),small);ImageDraw.Draw(frame).text((12,10),f'NW{n:02d} / 30ms',fill='white');frames.append(frame)
  for ext in ['gif','webp']:
   frames[0].save(OUT/f'NW-16-30ms.{ext}',save_all=True,append_images=frames[1:],duration=30,loop=0,**({'disposal':2} if ext=='gif' else {'lossless':True}))
  for name,color in [('dark','#202b38'),('light','#f0eee4')]:
   seam=Image.new('RGB',(2048,544),color)
   for x,n in enumerate((15,16,1,2)):
    im=dict(images)[n].resize((512,512),Image.Resampling.LANCZOS);seam.paste(im,(x*512,32),im);ImageDraw.Draw(seam).text((x*512+12,12),f'NW{n:02d}',fill='white' if name=='dark' else 'black')
   seam.save(OUT/f'seam-15-16-01-02-{name}.png')
 print(json.dumps({'frames':len(rows),'heights':[r['visibleHeight'] for r in rows],'distinctRaw':report['sourceDistinctCount'],'preview':str(OUT)},ensure_ascii=False))
if __name__=='__main__':main()
