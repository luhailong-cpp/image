from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime,sys
R=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
fp=Path(sys.argv[1]) if len(sys.argv)>1 else R/'tiles/r08_c11-candidate.png'
out=Path(sys.argv[2]) if len(sys.argv)>2 else R/'qa/native-initial'
out.mkdir(parents=True,exist_ok=True)
im=Image.open(fp).convert('RGB');records=[]
for axis in ['x','y']:
 for pos in [1024,2048,3072]:
  sheet=Image.new('RGB',(1024,1152),(30,30,30));d=ImageDraw.Draw(sheet);boxes=[]
  for i in range(4):
   box=(pos-128,i*1024,pos+128,(i+1)*1024) if axis=='x' else (i*1024,pos-128,(i+1)*1024,pos+128)
   crop=im.crop(box)
   if axis=='x':crop=crop.transpose(Image.Transpose.ROTATE_90)
   d.text((8,i*288+4),f'{axis}{pos} segment {i+1}; native pixels, vertical strips rotated 90',fill='white')
   sheet.paste(crop,(0,i*288+26));boxes.append(box)
  dst=out/f'{axis}{pos}-full-native.png';sheet.save(dst);records.append({'file':str(dst),'sourceSha256':sha(fp),'boxesLTRB':boxes,'resize':False,'rotation90':axis=='x'})
sheet=Image.new('RGB',(1200,1284),(30,30,30));d=ImageDraw.Draw(sheet)
for r,y in enumerate([1024,2048,3072]):
 for c,x in enumerate([1024,2048,3072]):
  d.text((c*400+6,r*428+4),f'{x},{y}',fill='white');sheet.paste(im.crop((x-200,y-200,x+200,y+200)),(c*400,r*428+26))
dst=out/'nine-junctions-native.png';sheet.save(dst);records.append({'file':str(dst),'resize':False,'nineCenters':[1024,2048,3072],'radius':200})
sfp=Path(sys.argv[3]) if len(sys.argv)>3 else R.parent/'tiles/current/region-v6/r09_c11-candidate.png';south=Image.open(sfp).convert('RGB')
sheet=Image.new('RGB',(1024,1376),(30,30,30));d=ImageDraw.Draw(sheet)
for i in range(4):
 strip=Image.new('RGB',(1024,320));strip.paste(im.crop((i*1024,3936,(i+1)*1024,4096)),(0,0));strip.paste(south.crop((i*1024,0,(i+1)*1024,160)),(0,160))
 d.text((8,i*344+4),f'South shared boundary segment {i+1}, native pixels',fill='white');sheet.paste(strip,(0,i*344+24))
dst=out/'south-shared-full-native.png';sheet.save(dst);records.append({'file':str(dst),'southSource':str(sfp),'southSourceSha256':sha(sfp),'resize':False,'halfHeight':160})
(out/'crop-record.json').write_text(json.dumps({'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(fp),'sourceSha256':sha(fp),'records':records,'visualReviewPending':True},indent=2),encoding='utf8')
print(out)

