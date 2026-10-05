from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
r=Path(__file__).resolve().parents[2];o=Image.new('RGB',(1530,920),(238,238,230));d=ImageDraw.Draw(o);sources=[]
items=[('07-v2',(376,510),(401.5,550),(649.5,990)),('09-v4',(378,500),(403,540),(657,945)),('10-v3',(378.5,500),(403.5,540),(663,945))]
for i,(name,p1,p2,q) in enumerate(items):
 p=r/'full-limb-review-20261004/run-NW'/name/'native.png';im=Image.open(p);canvas=Image.new('RGBA',im.size,(238,238,230,255));canvas.alpha_composite(im);dr=ImageDraw.Draw(canvas)
 slope=(p2[0]-p1[0])/(p2[1]-p1[1]);end=(p1[0]+slope*(1150-p1[1]),1150)
 dr.line([p1,end],fill=(10,160,200,230),width=2)
 for point in [p1,p2]:dr.ellipse((point[0]-5,point[1]-5,point[0]+5,point[1]+5),outline=(10,160,200,255),width=2)
 dr.ellipse((q[0]-6,q[1]-6,q[0]+6,q[1]+6),outline=(220,30,100,255),width=3)
 tile=canvas.crop((280,400,870,1220)).resize((510,850),Image.Resampling.LANCZOS);o.paste(tile,(i*510,55));d.text((i*510+8,7),name+' cyan: upper actual rod extrapolation',fill=(0,0,0));d.text((i*510+8,24),'magenta: visible lower black rod centre',fill=(0,0,0));sources.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'upperPoints':[p1,p2],'lowerPoint':q})
fp=r/'full-limb-review-20261004/west-audit/NW-black-rod-projection-evidence.jpg';o.save(fp,quality=97)
fp.with_suffix('.jpg.generation.json').write_text(json.dumps({'kind':'QA-annotation','method':'Pillow crop/resize and point/line overlay for review only; not game asset or imagegen target','sources':sources},indent=2),encoding='utf-8')
