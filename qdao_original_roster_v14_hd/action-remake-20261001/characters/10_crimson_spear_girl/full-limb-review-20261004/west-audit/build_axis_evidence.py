from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
r=Path(__file__).resolve().parents[2];o=Path(__file__).resolve().parent
p=r/'runtime/run/NW/05.png'
im=Image.open(p).convert('RGBA');sheet=Image.new('RGB',(1600,1024),(234,233,224));sheet.paste(im,(0,0),im);d=ImageDraw.Draw(sheet)
# Manually observed centers of EXPOSED BLACK SHAFT, not ornaments or hands.
top=((307,405),(339,454));tail=((690,786),(711,808))
d.line([top[0],top[1]],fill=(0,155,230),width=4)
xend=top[0][0]+(950-top[0][1])*(top[1][0]-top[0][0])/(top[1][1]-top[0][1])
d.line([top[1],(xend,950)],fill=(0,155,230),width=2)
d.line([tail[0],tail[1]],fill=(220,40,40),width=4)
for x,y in top:d.ellipse((x-5,y-5,x+5,y+5),outline=(0,155,230),width=2)
for x,y in tail:d.ellipse((x-5,y-5,x+5,y+5),outline=(220,40,40),width=2)
d.text((1030,20),'NW05 CURRENT runtime / black shaft centerlines',fill=(0,0,0))
d.text((1030,45),'BLUE: visible upper black shaft + straight extrapolation',fill=(0,100,160))
d.text((1030,70),'RED: visible lower black shaft (above gold tail)',fill=(180,20,20))
for i,(box,label) in enumerate([((275,375,370,500),'upper exposed shaft'),((650,750,755,845),'tail exposed shaft')]):
    crop=im.crop(box).resize((420,420),Image.Resampling.NEAREST)
    y=110+i*445;sheet.paste(crop,(1040,y),crop);d.text((1040,y+423),label,fill=(0,0,0))
dest=o/'NW05-black-shaft-evidence.jpg';sheet.save(dest,quality=98)
Path(str(dest)+'.generation.json').write_text(json.dumps({'file':str(dest),'operation':'Read-only QA crop/annotation; manually observed exposed black rod centers; no sprite edit','derivedFrom':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}],'upperPoints':top,'lowerPoints':tail,'expectedUpperLineXAtLowerY786':top[0][0]+(786-top[0][1])*(top[1][0]-top[0][0])/(top[1][1]-top[0][1])},ensure_ascii=False,indent=2),encoding='utf8')
