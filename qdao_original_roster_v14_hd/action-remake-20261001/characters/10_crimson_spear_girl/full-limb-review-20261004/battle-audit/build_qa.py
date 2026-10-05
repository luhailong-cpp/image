from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(name,paths,crop,size):
    w,h=size; rows=(len(paths)+3)//4
    canvas=Image.new('RGB',(w*4,(h+28)*rows),(207,216,220));d=ImageDraw.Draw(canvas)
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGBA');im=im.crop(crop) if crop else im
        im.thumbnail((w,h),Image.Resampling.LANCZOS)
        x=(i%4)*w;y=(i//4)*(h+28)
        canvas.paste(im,(x,y+28),im);d.text((x+8,y+6),p.parent.parent.name+'/'+p.parent.name+'/'+p.stem,fill=(20,20,20))
    out=OUT/name;canvas.save(out,quality=94)
    meta={'file':str(out.relative_to(ROOT)),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'operation':{'type':'technical-review-contact-sheet','fixedCrop':crop,'cellSize':size,'alphaBackground':[207,216,220]},'derivedFrom':[{'file':str(p.relative_to(ROOT)),'sha256':sha(p),'generationRecord':str(p.relative_to(ROOT))+'.generation.json'} for p in paths]}
    Path(str(out)+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
for action,count in [('hit',6),('attack',12),('cast',16)]:
    for direction in ['E','W']:
        paths=[ROOT/'runtime'/action/direction/f'{n:02}.png' for n in range(1,count+1)]
        for start in range(0,count,4):
            group=paths[start:start+4];label=f'{action}-{direction}-{start+1:02}-{start+len(group):02}'
            emit(label+'-full.jpg',group,None,(500,500))
            emit(label+'-hands.jpg',group,(170,410,850,830),(680,420))
            emit(label+'-feet.jpg',group,(200,700,830,990),(630,290))
print('Generated 54 fixed-frame inspection sheets for 68 runtime frames')
