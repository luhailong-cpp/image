"""Reference inputs only; not action frames. No final sprite pixels are edited."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image,ImageDraw
p=Path(__file__).parent
recovery=p.parents[1]
src=recovery/'10-generation/W01-v3/raw.png'
out=p/'W-upper-reference.png'
if not out.exists():
    with Image.open(src) as im: im.crop((0,0,im.width,850)).save(out)
    record={'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'recordedAt':datetime.now(timezone.utc).isoformat(),'derivedFrom':{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'generationRecord':str(src)+'.generation.json'},'operation':{'type':'upper-body reference crop','box':[0,0,1254,850],'countsAsAction':False,'newAIImage':False}}
    out.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.new('RGB',(1024,1024),'#f4f2eb')
d=ImageDraw.Draw(im)
d.text((45,25),'W09 LEG TOPOLOGY GUIDE - LEFT FACING',fill='#222222',font_size=27)
d.text((45,65),'FAR RIGHT = orange, FORWARD left, heel lands',fill='#a95c04',font_size=23)
d.text((45,100),'NEAR LEFT = cyan, BEHIND right, toe grounded',fill='#046f8b',font_size=23)
d.line((250,918,800,918),fill='#d8b174',width=2)
d.line((260,946,800,946),fill='#85c5cc',width=2)
d.ellipse((407,190,635,420),fill='#d6d2c9',outline='#57534b',width=6)
d.polygon([(411,302),(361,325),(411,340)],fill='#d6d2c9',outline='#57534b')
d.ellipse((429,283,440,299),fill='#222222')
d.rounded_rectangle((460,416,606,698),radius=45,fill='#d6d2c9',outline='#57534b',width=6)
# Far RIGHT thigh first: extends forward screen-left, behind near LEFT thigh.
d.line([(510,677),(460,792),(410,901)],fill='#bc6c13',width=59,joint='curve')
d.ellipse((386,879,431,925),fill='#bc6c13')
d.polygon([(396,891),(415,891),(419,916),(340,917),(334,903),(363,889)],fill='#e59a45',outline='#76450c')
# Near LEFT thigh overlaps front and extends rear screen-right; toe points left and contacts.
d.line([(563,686),(611,799),(660,893)],fill='#079ab2',width=66,joint='curve')
d.ellipse((638,872,684,918),fill='#079ab2')
d.polygon([(646,883),(671,894),(662,922),(629,942),(590,945),(587,932),(622,917)],fill='#44c9d7',outline='#045c73')
d.text((292,783),'FAR R',fill='#9b5609',font_size=28)
d.text((689,797),'NEAR L',fill='#036a7b',font_size=28)
d.text((279,960),'RIGHT heel',fill='#9b5609',font_size=24)
d.text((594,978),'LEFT toe',fill='#036a7b',font_size=24)
d.line((135,365,328,365),fill='#343434',width=10)
d.polygon([(135,365),(175,344),(175,386)],fill='#343434')
guide=p/'W09-pose-guide.png'
im.save(guide)
guide.with_suffix('.png.generation.json').write_text(json.dumps({'file':str(guide),'sha256':hashlib.sha256(guide.read_bytes()).hexdigest(),'operation':'original geometric pose diagram drawn from explicit joint coordinates; no source image','countsAsAction':False,'newAIImage':False},indent=2),encoding='utf-8')
