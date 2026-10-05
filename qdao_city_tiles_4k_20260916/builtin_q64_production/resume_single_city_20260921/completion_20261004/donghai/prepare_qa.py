from pathlib import Path
from PIL import Image
import hashlib,json,datetime
R=Path(__file__).resolve().parent;BASE=R.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
batch=json.loads((BASE/'builtin_q64_production/current-batch.json').read_text(encoding='utf-8-sig'))
sources=[];outputs=[];loaded={}
for e in batch['candidates']:
 if e['appearance'] not in ('donghai_day','donghai_lantern'):continue
 p=BASE/e['file'];im=Image.open(p).convert('RGB');assert im.size==(4096,4096) and sha(p)==e['sha256']
 sources.append({'appearance':e['appearance'],'tile':e['tile'],'file':str(p),'sha256':sha(p),'pixels':im.size,'indexShaVerified':True})
 loaded[(e['appearance'],e['tile'])]=im
 O=R/'baseline'/e['appearance']/e['tile'];Q=O/'qa';Q.mkdir(parents=True,exist_ok=True)
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(O/'overview-reference-only.png')
 for axis in ('x','y'):
  for line in (1024,2048,3072):
   sheet=Image.new('RGB',(1024,1280));crops=[]
   for s in range(4):
    box=(line-160,s*1024,line+160,(s+1)*1024) if axis=='x' else (s*1024,line-160,(s+1)*1024,line+160)
    piece=im.crop(box)
    if axis=='x':piece=piece.transpose(Image.Transpose.ROTATE_90)
    sheet.paste(piece,(0,s*320));crops.append({'sourceLTRB':box,'sheetLTRB':[0,s*320,1024,(s+1)*320],'rotation':90 if axis=='x' else 0})
   path=Q/f'{axis}{line}-full.png';sheet.save(path);outputs.append({'file':str(path),'sha256':sha(path),'pixels':sheet.size,'source':str(p),'sourceSha256':sha(p),'nativePixelCropping':True,'crops':crops})
  
 sheet=Image.new('RGB',(1536,1536));crops=[]
 for ri,y in enumerate((1024,2048,3072)):
  for ci,x in enumerate((1024,2048,3072)):
   box=(x-256,y-256,x+256,y+256);sheet.paste(im.crop(box),(ci*512,ri*512));crops.append({'sourceLTRB':box,'sheetLTRB':[ci*512,ri*512,(ci+1)*512,(ri+1)*512]})
 path=Q/'nine-junctions.png';sheet.save(path);outputs.append({'file':str(path),'sha256':sha(path),'pixels':sheet.size,'source':str(p),'sourceSha256':sha(p),'nativePixelCropping':True,'crops':crops})
for app in ('donghai_day','donghai_lantern'):
 for c in (8,9):
  left=loaded[(app,f'r08_c{c:02}')];right=loaded[(app,f'r08_c{c+1:02}')]
  pair=Image.new('RGB',(512,4096));pair.paste(left.crop((3840,0,4096,4096)),(0,0));pair.paste(right.crop((0,0,256,4096)),(256,0))
  sheet=Image.new('RGB',(1024,2048));crops=[]
  for s in range(4):
   box=(0,s*1024,512,(s+1)*1024);sheet.paste(pair.crop(box).transpose(Image.Transpose.ROTATE_90),(0,s*512));crops.append({'pairLTRB':box,'sheetLTRB':[0,s*512,1024,(s+1)*512],'rotation':90})
  p=R/'baseline'/app/f'common-c{c:02}-c{c+1:02}-full.png';sheet.save(p);outputs.append({'file':str(p),'sha256':sha(p),'pixels':sheet.size,'leftTile':f'r08_c{c:02}','rightTile':f'r08_c{c+1:02}','nativePixelCropping':True,'crops':crops})
(R/'baseline/source-and-qa-manifest.json').write_text(json.dumps({'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':sources,'qa':outputs,'formalAccepted':False,'visualReviewPending':True},indent=2),encoding='utf-8')
print(json.dumps({'sources':sources,'qaCount':len(outputs)}))
