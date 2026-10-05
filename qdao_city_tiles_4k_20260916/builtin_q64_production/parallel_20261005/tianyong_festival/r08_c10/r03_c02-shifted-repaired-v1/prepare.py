from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
FIRST=OUT.parent/'r03_c02-shifted-v1'
ROOT=Path('D:/work/image')
TASK=OUT.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
raw_path=FIRST/'native.png'
source=TASK/'r08_c10/current/v002/r08_c10-fragment.png'
assert sha(raw_path)=='b94982ca3f36457d5eb59716f06b1d27d5ca8c76618622958c54ed7f1a9d48f1'
assert sha(source)=='9d97cd1126d2c7edbb2df25561510fb17fb0b071a132e2bb3b0db3ace2855f88'
raw=Image.open(raw_path).convert('RGBA');native=Image.open(source).convert('RGBA')
context=Image.new('RGBA',(1254,1254),(0,0,0,0))
context.paste(raw.crop((0,0,1254,395)),(0,0))
context.paste(native.crop((0,0,1254,627)),(0,627))
context.save(OUT/'context.png')
guide=Image.open(FIRST/'layout-reference-only.png');guide.save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
prompt='''Use case: precise-object-edit / narrow terrain inpainting.
Return one opaque1254 by1254 square with image1's exact framing. Repair ONLY the transparent horizontal band in IMAGE1 at y395..626 (232 pixels high). Everything above y395 and below y627 is already drawn and is to remain unchanged.
The top region of IMAGE1 contains the rendered wide ivory stone cross-band around y290..400. The bottom627 rows y627..1253 are the authoritative original native game pavement, with three slate-gray inset columns, ivory/gold vertical dividers and the lower stone border. Preserve the lower half exactly, especially all six gray slab side contours and their widths, curvature, scale and shadows. The lower native image is the controlling endpoint geometry. Preserve the wide upper ivory cross-band instead of replacing it with seams.
In the transparent232-row gap, render the upper ends of the three lower gray stone inset panels and continue their side contours from the original bottom region upward to the underside of the broad cross-band. Match each original contour endpoint and tangent exactly. Do not widen, recenter, straighten, shift, split or duplicate the three lower inset columns. This is actual newly painted geometry repair, not a new layout. The missing band's bottom at y627 must become a smooth invisible continuation of the known native contours, with no step or doubled line. Do not introduce a new horizontal stone joint at y627. The upper edge of the gap belongs at the underside of the real cross-band, not a new decorative frame.
IMAGE2 is the same-world canonical broad layout only; use it to confirm the broad ivory cross-band and three inset columns, but never use its blurred lower edge positions to displace the exact native lower half in image1. Never copy enlarged guide pixels.
IMAGE3 is the user-approved rendering STYLE only: bright clean rounded Q/chibi Daoist fantasy handpainting, warm ivory, restrained gold and neutral slate. Do not import UI, lettering, characters, props or icons. No new objects, ornaments, cracks, grunge, dense texture, white halos, blur, text, watermark or frame. Do not repaint the known top or bottom, move the camera, zoom, rotate or rescale. Fill only the transparent gap with crisp native details at the highest host visual finish.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
roles=['edit target: upper395 newly rendered structure and lower627 original native pixels; only y395..627 is missing','canonical broad layout ONLY; native lower geometry in image1 remains authoritative','primary approved rendering style ONLY']
first_req=read(FIRST/'request.json')
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r03_c02-shifted-repaired','version':'v1','tile':'r08_c10','globalCropLTRB':first_req['globalCropLTRB'],'tileLocalCropLTRB':first_req['tileLocalCropLTRB'],'knownPixels':1254*(395+627),'missingPixels':1254*232,'knownRegionsLTRB':[[0,0,1254,395],[0,627,1254,1254]],'missingRegionLTRB':[0,395,1254,627],'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'configSnapshot':read(ROOT/'config/image-generation.json')}
write('request.json',req)
write('preparation.json',{'nativeInputs':[info(raw_path),info(source)],'upperSourceRole':'new native rendering with usable cross-band only; bottom drift excluded','upperSourceCropLTRB':[0,0,1254,395],'originalLowerSourceCropLTRB':[0,0,1254,627],'originalLowerPasteXY':[0,627],'references':[{**info(p),'role':r} for p,r in zip(refs,roles)],'nativeScale':1,'guidePixelsAllowedInFinal':False,'globalCropLTRB':req['globalCropLTRB'],'tileLocalCropLTRB':req['tileLocalCropLTRB'],'otherTaskFilesModified':False,'knownOriginalBottomMatchesFirstContext':bool(np.array_equal(np.asarray(context)[627:],np.asarray(Image.open(FIRST/'context.png').convert('RGBA'))[627:]))})
write('context.png.generation.json',{'file':str(OUT/'context.png'),'sha256':sha(OUT/'context.png'),'derivedFrom':[info(raw_path),info(source)],'operation':'Exact native top395 and originalnative bottom627 with transparent232 middle; no resampling.','newModelCalls':0})
write('layout-reference-only.png.generation.json',{'file':str(OUT/'layout-reference-only.png'),'sha256':sha(OUT/'layout-reference-only.png'),'derivedFrom':[info(FIRST/'layout-reference-only.png')],'operation':'Same-world reference-only guide; not output pixels','newModelCalls':0})
write('capability-evidence.json',read(FIRST/'capability-evidence.json'))
print(json.dumps({'out':str(OUT),'knownPixels':req['knownPixels'],'missingPixels':req['missingPixels']}))
