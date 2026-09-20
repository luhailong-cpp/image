from pathlib import Path
from PIL import Image
import hashlib,json,sys
P=Path(__file__).resolve().parent
src=P/'output_resume_20260918/tianyong_r09_c08_q64_4k_candidate.png'
qa=P/'qa_resume_20260918/fullseams';qa.mkdir(parents=True,exist_ok=False)
im=Image.open(src).convert('RGB');assert im.size==(4096,4096)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for axis in ('vertical','horizontal'):
 for pos in (1024,2048,3072):
  board=Image.new('RGB',(1280,1024) if axis=='vertical' else (1024,1280));boxes=[]
  for i in range(4):
   box=(pos-160,i*1024,pos+160,(i+1)*1024) if axis=='vertical' else (i*1024,pos-160,(i+1)*1024,pos+160)
   board.paste(im.crop(box),(i*320,0) if axis=='vertical' else (0,i*320));boxes.append(list(box))
  dest=qa/f'{axis}_{pos}.png';board.save(dest)
  board.save(dest.with_suffix('.jpg'),quality=95,subsampling=0)
  items.append({'file':str(dest),'sha256':sha(dest),'axis':axis,'coordinate':pos,'boxesLTRB':boxes,'pixelScale':1,'lengthCovered':4096,'visualReview':'pending'})
im.resize((1024,1024),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=95)
(qa/'crops.json').write_text(json.dumps({'source':str(src),'sourceSha256':sha(src),'nativePixelScale':True,'items':items},indent=2),encoding='utf8')
print(json.dumps({'fullSeams':len(items),'directory':str(qa)}))
