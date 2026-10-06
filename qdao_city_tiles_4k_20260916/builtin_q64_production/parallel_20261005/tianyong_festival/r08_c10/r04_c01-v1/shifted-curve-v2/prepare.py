from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;PIECE=OUT.parent;PREV=PIECE/'shifted-v1';TASK=PIECE.parent.parent;ROOT=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
    with (OUT/n).open('x',encoding='utf-8') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
assert sha(PREV/'native.png')=='4af4f0d4e5cfc7fb10065fac96ab409f90ae8231f9c145dfdcf07604a3c49839'
prep=read(PREV/'preparation.json');cp=read(TASK/'source-checkpoint.json')
for item in prep['nativeInputs']:assert sha(item['file'])==item['sha256']
assert sha(cp['fragment']['file'])==cp['fragment']['sha256'] and sha(cp['bottom']['file'])==cp['bottom']['sha256']
original=np.asarray(Image.open(PREV/'original-context.png').convert('RGBA'))
fbox=cp['fragment']['tileLocalLTRB'];fi=Image.open(cp['fragment']['file']).convert('RGBA');newright=np.asarray(fi.crop((909-fbox[0],3469-fbox[1],1139-fbox[0],4096-fbox[1])))
assert np.array_equal(newright,original[:627,1024:])
bi=np.asarray(Image.open(cp['bottom']['file']).convert('RGBA'))[:627,:1139]
assert np.array_equal(bi,original[627:,115:])
known=original[:,:,3]==255;raw=np.asarray(Image.open(PREV/'native.png').convert('RGBA')).copy()
polygon=[(950,100),(1024,100),(1024,627),(750,627),(850,400)]
mi=Image.new('L',(1254,1254),0);ImageDraw.Draw(mi).polygon(polygon,fill=255)
missing=(np.asarray(mi)>0)&(~known);raw[missing]=[0,0,0,0];raw[known]=original[known]
Image.fromarray(raw).save(OUT/'context.png');Image.fromarray(original).save(OUT/'original-context.png');Image.fromarray((missing*255).astype(np.uint8)).save(OUT/'repair-mask.png')
shutil.copy2(PREV/'layout-reference-only.png',OUT/'layout-reference-only.png');shutil.copy2(PREV/'capability-evidence.json',OUT/'capability-evidence.json')
style=ROOT/'designs/gameplay-ui/04-guild.png';refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit. Inpaint ONLY the narrow transparent curved connection corridor in image1. Return the same native1254 by1254 opaque square without moving, resizing or restyling any opaque artwork.
This is a surgical repair of the RIGHT EDGE of the large lower gray stone slab and the adjacent ivory curved strip. The warm slab, broad diagonal cross-band, smooth gray interior, left curve and floral relief are already finished. Preserve all of them. The entire lower627 rows, from y627 to1253, and left/right boundary strips in image1 have been restored from the genuine original map at EXACT coordinates. They are immutable geometry, not a loose reference.
Fill the small transparent corridor by extending the TRUE ORIGINAL lower curve UPWARD, with its existing thick bevel and tangent, then connect to the upper cross-band. Match BOTH distinct edges, not just one: at row632 the original gray-face-to-dark-bevel edge is x831, and the dark-bevel-to-bright-ivory edge is x876. The dark/bevel structure between these two is about45 pixels wide and must NOT be thinned to32px. At row877 those corresponding original edges are approximately x694 and x741. These original lower edges are fully visible in image1. Leave them exactly where they are and follow them upward into the gap. The failed curve has been erased in the gap; do not shift the intact lower edge toward the prior upper position.
At y627, the right contour must meet the original native endpoint at x877, not x848. The gray inset must have the original width. The gap should become a single continuous original-style bevel and ivory boundary with no jog, narrowing, flare, bulge, double outline or new seam. Preserve the cross-band's already correct bulk and shape; repair only its far-right connection into this true curve. The lower gray face must remain quiet smooth gray, matching the adjacent original pixels; no cloudy mottling, cracks or added shading stripe.
Image2 is only a rough low-resolution LOCATION reminder. It is not precise enough to specify the repaired curve or bevel width. DO NOT use its thinner curve to override image1. All shape, thickness and color of the repaired connection come from image1's real native lower curve. No reference-guide pixels may be copied/enlarged into the result.
Image3 is the approved overall STYLE reference only: bright clean rounded Daoist Q-version fantasy paint. Do not add its UI, text, characters, icons or frames. The actual native map material in image1 takes priority for this seam repair.
The transparency is just an editing hole. Do not add a line at its boundary. No whole-image redraw, camera shift, zoom, rotation, global recolor, resizing, new stone seams, motifs, text, watermark or border. Keep the exact1254-square framing and only repair the missing connection at highest host quality.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8');payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('source-checkpoint-snapshot.json',cp)
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'AI redraw of narrow right curve corridor; original lower627 restored','globalCropLTRB':[36749,32141,38003,33395],'tileLocalCropLTRB':[-115,3469,1139,4723],'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None,'repairPixels':int(missing.sum())})
write('preparation.json',{'nativeInputs':prep['nativeInputs'],'previousCandidate':info(PREV/'native.png'),'previousOriginalContext':info(PREV/'original-context.png'),'currentCheckpoint':info(OUT/'source-checkpoint-snapshot.json'),'currentRightAndBottomRequiredROIMatchesFrozenOriginal':True,'repairPolygon':polygon,'repairMask':info(OUT/'repair-mask.png'),'references':[{**info(p),'role':role} for p,role in zip(refs,['edit target; only narrow curve corridor missing','location reminder only, never override original native edge thickness','approved style'])],'nativeScale':1,'geometryWarpApplied':False,'guidePixelsAllowedInFinal':False,'allWritesConfinedTo':str(OUT)})
for p in [OUT/'context.png',OUT/'original-context.png',OUT/'repair-mask.png',OUT/'layout-reference-only.png']:
    write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(PREV/'native.png'),info(PREV/'original-context.png')] if p.name!='layout-reference-only.png' else [info(PREV/'layout-reference-only.png')],'newModelCalls':0,'nativeScale':1,'operation':'Exact native composite and transparent mask; no warp' if p.name!='layout-reference-only.png' else 'Copied location-only reference; no final pixels'})
print(json.dumps({'context':info(OUT/'context.png'),'repairPixels':int(missing.sum())}))
