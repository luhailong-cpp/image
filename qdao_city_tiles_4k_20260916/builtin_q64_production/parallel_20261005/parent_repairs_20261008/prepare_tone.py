from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
O=R/'west-upper-tone';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ctx=Image.new('RGB',(1254,1254));parts=[]
for tile,crop,dst in [('r08_c07',[3469,0,4096,1254],[0,0]),('r08_c08',[0,0,627,1254],[627,0])]:
 p=R/'current'/f'{tile}.png';ctx.paste(Image.open(p).crop(crop),dst)
 parts.append({'tile':tile,'file':str(p),'sha256':sha(p),'cropLTRB':crop,'pasteXY':dst})
ctx.save(O/'context.png')
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
prompt='''Use case: precise-object-edit. Image 1 is an exact 1:1 game-map crop and the edit target; image 2 is only the approved chibi painterly game style, not a layout or UI reference. Repair the accidental vertical stitch line down the exact middle of image 1: the warm gray paving surface abruptly changes brightness and texture at x627. Make each physical stone slab read as one continuous softly painted warm gray material on BOTH sides of the middle line. Do not introduce any physical grout line, step, stripe or ornament there. Keep every existing diagonal cream/gold trim, stone joint, rounded bevel, silhouette, perspective, lighting and scale exactly in place. Change only the smooth stone surface near this accidental vertical stitch, preserving the rest. Bright clean rounded game art, subtle fine stone texture, no blur, no gritty speckles, no added detail, text or UI. Return the same square framing and native detail.'''
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'parts':parts,'windowRelativeToR08C07LTRB':[3469,0,4723,1254],
 'payload':{'prompt':prompt,'referenced_image_paths':[str(O/'context.png'),str(style)],'transparent_background':False},
 'references':[{'file':str(O/'context.png'),'sha256':sha(O/'context.png'),'role':'edit target'},{'file':str(style),'sha256':sha(style),'role':'approved style only'}],
 'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'context.png.generation.json').write_text(json.dumps({'operation':'native crop and concatenate without resizing','file':str(O/'context.png'),'sha256':sha(O/'context.png'),'parts':parts},ensure_ascii=False,indent=2),encoding='utf-8')
print(str(O/'context.png'))
