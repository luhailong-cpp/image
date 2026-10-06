from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;P=O.parent;R=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
assert sha(P/'native.png')=='5d25e25b3e2b1c9d366c45415e6f25408bf5419affd63b2eb68ff2931ec9fcbf'
a=np.asarray(Image.open(P/'native.png').convert('RGBA')).copy();ctx=np.asarray(Image.open(P/'original-context.png').convert('RGBA'));known=ctx[:,:,3]==255
m=Image.new('L',(1254,1254),0);d=ImageDraw.Draw(m)
d.rectangle((620,805,1023,1023),fill=255)
d.polygon([(85,0),(220,0),(220,650),(210,1023),(85,1023)],fill=255)
mask=np.asarray(m)>0;a[mask]=[0,0,0,0];a[known]=ctx[known]
Image.fromarray(a).save(O/'context.png');Image.fromarray(ctx).save(O/'original-context.png');Image.fromarray(((mask&~known)*255).astype('uint8')).save(O/'repair-mask.png')
shutil.copy2(P/'layout-reference-only.png',O/'layout-reference-only.png');style=R/'designs/gameplay-ui/04-guild.png';refs=[O/'context.png',O/'layout-reference-only.png',style]
mean=ctx[1040:1120,680:950,:3].mean((0,1)).tolist()
prompt=f'''Use case: precise-object-edit. Finish ONLY the two transparent repair areas in image1, preserving the same1254x1254 framing and all opaque artwork. This is a precise material repair of a completed plaza crop, not a new composition.
REPAIR1, the lower central gray stone panel: the visible original bottom230 rows are immutable native pixels. The lower gray slab starts just below the horizontal stone joint around y780 and continues through the bottom edge. Its true source gray is visible below y1024 and has approximately RGB{[round(v) for v in mean]} in the center. Extend THAT cool medium gray upward into the hole. It must be the SAME connected stone plane and the SAME brightness as the original bottom, not a pale creamy/beige stone. The prior hole content was too light by about27 red,22 green,16 blue levels; that failed light material has been erased. Match the native bottom exactly without a horizontal tone step at y1024. Keep subtle low-contrast native texture and gentle shading. Preserve the top stone joint at y780 and the existing ivory ring. Match the original lower gray left-edge bevel endpoint at approximately x640 at y1024, following the original curve, without a narrow or jogged return.
REPAIR2, the narrow vertical hole in the left ivory slabs: create a natural quiet texture continuation from the real original left115-pixel strip into the already-painted right side. There must be NO straight rectangular texture or color boundary at x115. Use restrained pale ivory stone, gently transitioning the existing subtle surface texture; no added spots or veins. Continue the existing horizontal stone seam near y735 at precisely the same height and tangent as the original left strip, without creating a new seam at the mask edge.
The left115 pixels, right230 pixels and bottom230 pixels have been restored from actual accepted neighboring map pixels. Preserve them exactly. Keep the big ivory curved ring, other stone planes, all bevel widths and all unaffected geometry unchanged. Opaque areas are completed work. Do not redraw the entire picture.
Image2 is only a broad low-resolution canonical LOCATION guide. It does not override native plane colors or precise contour thickness. Never enlarge/copy it into finished pixels. Image3 is the approved primary STYLE reference only, bright clean rounded Daoist fantasy Q-version painting. Do not import any interface, text, character or object.
No camera movement, scaling, rotation, new stone division, blur, cracks, mosaic grain, marble veins, heavy cloudy texture, border, watermark or lettering. The transparent areas are editing holes, not physical seams. Return the opaque1254-square native crop with only these material connections repaired at highest host finish.'''
(O/'prompt.txt').write_text(prompt,encoding='utf8')
req=read(P/'request.json');write('request.json',{**req,'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'AI lower gray material and left texture seam repair','payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'repairPixels':int((mask&~known).sum())})
prep=read(P/'preparation.json');write('preparation.json',{'nativeInputs':prep['nativeInputs'],'sourceCheckpoint':prep['sourceCheckpoint'],'previousCandidate':info(P/'native.png'),'references':[{**info(p),'role':role} for p,role in zip(refs,['localized edit target with original known context restored','location only','approved primary style'])],'repairMask':info(O/'repair-mask.png'),'nativeScale':1,'guidePixelsAllowedInFinal':False,'targetGrayMeanRGB':mean,'formalAccepted':False})
for p in [O/'context.png',O/'original-context.png',O/'layout-reference-only.png',O/'repair-mask.png']:
 write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(P/'native.png'),info(P/'original-context.png')],'newModelCalls':0,'nativeScale':1 if p.name!='layout-reference-only.png' else None,'operation':'Native mask/context preparation; canonical image is reference only'})
print(json.dumps({'context':info(O/'context.png'),'repairPixels':int((mask&~known).sum()),'targetGrayMeanRGB':mean}))
