from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import hashlib, json
OUT=Path(__file__).resolve().parent
REV=OUT.parents[1]/'05-delivery-preview/revisions/complete-review-v1'
dirs=['N','NE','E','SE','S','SW','W','NW']
data={'snapshot':str(REV),'files':{},'nw_extremely_faint_points':{}}
for d in ['N','E','S','NW']:
 for n in range(1,17):
  p=REV/f'runtime/walk/{d}/{n:02d}.png';im=Image.open(p).convert('RGBA');a=np.asarray(im)[:,:,3];ys,xs=np.where(a>8)
  data['files'][f'{d}/{n:02d}']={'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bbox_alpha_gt8':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]}
for n,points in [(1,[(706,832),(804,810)]),(7,[(704,835),(704,836)])]:
 im=Image.open(REV/f'runtime/walk/NW/{n:02d}.png').convert('RGBA')
 data['nw_extremely_faint_points'][str(n)]={str(pt):list(im.getpixel(pt)) for pt in points}
for bg,col,ink in [('light','#f0eee4','black'),('dark','#202b38','white')]:
 sheet=Image.new('RGB',(1600,640),col)
 for i,d in enumerate(dirs):
  p=REV/f'runtime/idle/{d}.png';im=Image.open(p).convert('RGBA');crop=im.crop((156,370,356,510)).resize((400,280),Image.Resampling.NEAREST)
  x=i%4*400;y=i//4*320;sheet.paste(crop,(x,y+32),crop);ImageDraw.Draw(sheet).text((x+12,y+8),f'{d} idle feet 2x inspection',fill=ink)
 sheet.save(OUT/f'idle-feet-2x-{bg}.png')
data['manifest_sha256']=hashlib.sha256((REV/'manifest.json').read_bytes()).hexdigest()
(OUT/'measurement.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'NW11':data['files']['NW/11'],'NW12':data['files']['NW/12'],'NW16':data['files']['NW/16'],'NW01':data['files']['NW/01'],'faint':data['nw_extremely_faint_points']},indent=2))
