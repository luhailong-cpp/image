from workflow import *
from PIL import Image
tid='r14_c13';pid=tid+'_repair_p32edge';v='v01';x,y=1306,1933
src=ROOT/'tiles/r14_c13.candidate-right-full-20261016-v02.png';g=ROOT/'guides'/f'{pid}_{v}.candidate-only.png';assert not g.exists()
Image.open(src).convert('RGB').crop((x,y,x+1254,y+1254)).save(g)
prompt='Use case: precise-object-edit. Edit only the accidental straight vertical material boundary in this exact native 1254 by 1254 sea-water crop. The boundary is near x627, especially y500 to1024: the caustic pattern abruptly changes density across a straight line. Remove that ruler-straight line by connecting the existing wave network continuously through it, preserving natural local wave sizes and detailed painting. Keep all existing wave positions and hues away from this narrow problem. Preserve the outer 150 pixel frame exactly to permit stitching. No blurring, no rectangular patch, no new objects or reflections, no text, borders, zoom, shift or rescale. Return the same opaque 1254 square with native detail.'
write(ROOT/'prompts'/f'{pid}_{v}.registered.json',{'id':pid,'tile':tid,'tileRelativeOrigin':[x,y],'nativeGlobalBox':[49152+x,53248+y,49152+x+1254,53248+y+1254],'sourceCore':[115,115,1139,1139],'destinationCore':[x+115,y+115,x+1139,y+1139],'derivedFromCandidate':str(src),'candidateSha256':sha(src),'operation':'exact native candidate crop; no resize; guide only'})
write(ROOT/'prompts'/f'{pid}_{v}.corner.args.json',{'prompt':prompt,'referenced_image_paths':[str(g)],'transparent_background':False})
print(g)

