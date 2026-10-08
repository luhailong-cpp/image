from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;O=P/'lower-repair-v1';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
ctx=Image.open(P/'original-context.png').convert('RGBA')
pros=P.parent/'r02_c02-v1/final-v2/joined.png'
assert sha(pros)=='d70d4463968ab7095ae4da862ce47ba5b69f4546b967ba2b286232bbab6e062e'
ctx.paste(Image.open(pros).convert('RGBA').crop((0,0,230,1254)),(1024,0))
ctx.save(P/'context-latest.png')
save('context-latest-source.json',{'newContext':info(P/'context-latest.png'),'derivedFrom':[info(P/'original-context.png'),info(pros)],'operation':'Replace right230 context with final-v2 prospective native return before alignment; original submitted context remains intact','formalAccepted':False})
base=Image.open(P/'native.png').convert('RGBA');a=np.asarray(ctx);known=a[:,:,3]==255;b=np.array(base);b[known]=a[known];base=Image.fromarray(b)
base.save(O/'before-repair.png')
box=[780,740,1024,1024];base.paste((0,0,0,0),box);base.save(O/'context.png')
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
prompt='''Use case: precise-object-edit. Repair only the small transparent opening in image1 near the lower right (x780..1023,y740..1023) of this exact1254x1254 native game-map crop. The visible pixels must stay identical. Complete the missing contours and surface using the real adjacent stone edges.
This is a large GRAY recessed stone slab below the single diagonal IVORY crossbar. The gray slab fills almost the whole lower central space up to its existing thin beveled RIGHT EDGE near x980 at y1024. Its actual gray bottom continuation is clearly visible from y1024 to1254. The gray slab must connect smoothly with the same WIDTH to that lower source. There must NOT be a second thick ivory upright near x910; that erroneous extra upright has been erased. The only thick ivory upright on the right already exists farther right in the visible context, near x1040..1125. Continue the single existing gray slab all the way to its true narrow bevel and the existing outer ivory upright, without adding another band, inset, column, line or panel.
Continue the single diagonal ivory crossbar from the left to its exact right endpoint, and continue the plain gray slab below it. Keep the clean broad rounded bevel and match the visible subdued gray color and low contrast painted stone texture. Do not insert a horizontal shelf at y1024 or cover the mismatch. Do not change anything outside the small opening; no rescaling, zoom, rotation, camera change, crop, text, border, watermark, cracks or extra speckles. Image2 is approved polished Daoist Q handpainting style only, no UI content. Return the completed native crop.'''
(O/'prompt.txt').write_text(prompt,encoding='utf8')
req=read(P/'request.json');req.update(preparedAtUtc=datetime.now(timezone.utc).isoformat(),repairMaskLTRB=box,payload={'prompt':prompt,'referenced_image_paths':[str(O/'context.png'),str(style)],'transparent_background':False})
save('request.json',req);save('preparation.json',{'references':[{**info(O/'context.png'),'role':'edit target with one small masked structural repair'},{**info(style),'role':'approved painting style'}],'nativeInputs':[info(P/'native.png'),info(P/'context-latest.png')],'sourceProspective':info(pros),'repairMaskLTRB':box})
for n in ['context.png','before-repair.png']:save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(P/'native.png'),info(P/'context-latest.png')],'operation':'Native1:1 composite and explicit repair mask for AI editing; not accepted final','newModelCalls':0})
print(json.dumps({'request':info(O/'request.json'),'missingPixels':(box[2]-box[0])*(box[3]-box[1])}))
