from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve();T=ROOT/'r09_c08';D=T/'material-transition-review';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def native(r,c):
 p=T/'native'/f'r{r:02d}_c{c:02d}.png';g=Path(str(p)+'.generation.json')
 record=json.loads(g.read_text(encoding='utf-8-sig'));assert sha(p)==record['sha256']
 return p,Image.open(p).convert('RGB'),g
outputs=[]
for name,rows,cols in [('partial-r02-r03-c02-c04',[2,3],[2,3,4]),('partial-r02-r04-c03-c04',[2,3,4],[3,4])]:
 canvas=Image.new('RGB',(1024*len(cols),1024*len(rows)));sources=[]
 for iy,r in enumerate(rows):
  for ix,c in enumerate(cols):
   p,im,g=native(r,c);canvas.paste(im.crop((115,115,1139,1139)),(1024*ix,1024*iy));sources.append({'file':str(p),'sha256':sha(p),'generationRecord':str(g),'generationSha256':sha(g),'sourceBox':[115,115,1139,1139],'destinationXY':[1024*ix,1024*iy]})
 raw=D/(name+'.native.png');assert not raw.exists();canvas.save(raw)
 preview=D/(name+'.preview-only.png');canvas.resize((canvas.width//2,canvas.height//2),Image.Resampling.LANCZOS).save(preview)
 outputs.append({'file':str(raw),'sha256':sha(raw),'pixels':list(canvas.size),'resampling':'none','sources':sources,'previewFile':str(preview),'previewSha256':sha(preview),'previewResampling':'LANCZOS 0.5; partial QA preview only; never final art'})
p,O,g=native(4,3);pn,N,gn=native(3,3);pe,E,ge=native(4,4)
for name,size,pieces in [('r04c03-north1024x512',(1024,512),[(N,(115,883,1139,1139),(0,0)),(O,(115,115,1139,371),(0,256))]),('r04c03-east512x1024',(512,1024),[(O,(883,115,1139,1139),(0,0)),(E,(115,115,371,1139),(256,0))])]:
 im=Image.new('RGB',size)
 for src,box,xy in pieces:im.paste(src.crop(box),xy)
 dest=D/(name+'.png');assert not dest.exists();im.save(dest);outputs.append({'file':str(dest),'sha256':sha(dest),'pixels':list(size),'resampling':'none','sources':[{'file':str(z),'sha256':sha(z)} for z in [p,pn,pe]]})
m={'createdAt':datetime.now(timezone.utc).isoformat(),'purpose':'Independent material transition assessment; PARTIAL PREVIEW ONLY','finalArt':False,'outputs':outputs}
(D/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print(D)

