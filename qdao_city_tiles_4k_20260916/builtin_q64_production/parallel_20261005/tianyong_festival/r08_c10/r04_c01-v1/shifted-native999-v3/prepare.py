from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
PIECE=OUT.parent
TASK=PIECE.parent.parent
ROOT=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
source=PIECE/'shifted-curve-v2/native.png'
assert sha(source)=='de247dbb4b9ae0828d6881f5eb30ca234508649ce3920919e429f6bcedeb66ae'
cp=read(TASK/'source-checkpoint.json');assert cp['sourcePairVerified'] and cp['resumeAuthorizedByUser']
fragment=Path(cp['fragment']['file']);bottom=Path(cp['bottom']['file'])
assert sha(fragment)==cp['fragment']['sha256'] and sha(bottom)==cp['bottom']['sha256']
oldprep=read(PIECE/'preparation.json');left=Path(oldprep['nativeInputs'][1]['file']);corner=Path(oldprep['nativeInputs'][3]['file'])
assert sha(left)==oldprep['nativeInputs'][1]['sha256'] and sha(corner)==oldprep['nativeInputs'][3]['sha256']
box=[-115,3841,1139,5095];globalbox=[36749,32513,38003,33767]
original=Image.new('RGBA',(1254,1254),(0,0,0,0));used=[]
def paste(source,srcbox,role):
    lx,ty=max(box[0],srcbox[0]),max(box[1],srcbox[1]);rx,bt=min(box[2],srcbox[2]),min(box[3],srcbox[3])
    im=Image.open(source).convert('RGBA');assert im.size==(srcbox[2]-srcbox[0],srcbox[3]-srcbox[1]);assert lx<rx and ty<bt
    crop=[lx-srcbox[0],ty-srcbox[1],rx-srcbox[0],bt-srcbox[1]];xy=(lx-box[0],ty-box[1]);original.paste(im.crop(crop),xy)
    used.append({**info(source),'role':role,'cropLTRB':crop,'pasteXY':list(xy),'nativeScale':1})
paste(fragment,cp['fragment']['tileLocalLTRB'],'current right230 original native strip in upper255')
paste(left,[-4096,0,0,4096],'left115 original native strip in upper255')
paste(bottom,[0,4096,4096,8192],'bottom999 original native source across remaining1139 columns')
paste(corner,[-4096,4096,0,8192],'bottom-left115x999 original native corner source')
original.save(OUT/'original-context.png')
known=np.asarray(original)[:,:,3]==255
assert np.all(known[255:])
canvas=Image.new('RGBA',(1254,1254),(0,0,0,0))
canvas.paste(Image.open(source).convert('RGBA').crop((0,372,1254,436)),(0,0))
arr=np.asarray(canvas).copy();arr[known]=np.asarray(original)[known];canvas=Image.fromarray(arr);canvas.save(OUT/'context.png')
missing=arr[:,:,3]==0;assert int(missing.sum())==909*191
Image.fromarray((missing*255).astype(np.uint8)).save(OUT/'repair-mask.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in globalbox)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png';assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit / local inpainting. Fill ONLY the small transparent connection rectangle in image1. Keep the exact1254x1254 frame and native scale. This image is mostly finished ORIGINAL artwork; do not redraw it.
Image1 is the target. Rows255..1253 are999 rows of real original map pixels and must remain unchanged. Left115 and right230 columns are real original pixels too. The top64 rows are retained new artwork at the matching global coordinates. The ONLY gap is x115..1024,y64..255, a191-row connection strip. Reconnect the gray paving slab and ivory side curves across that short gap while preserving both ends exactly. The real lower999 rows define the correct geometry, bevel thickness, material and lighting. Do not shift or narrow them to resemble any other image.
At the lower edge of the gap, the true RIGHT gray-face-to-dark-bevel edge is approximately x831 at row260, and the dark-bevel-to-ivory-bright-face edge is x876. Both are clearly visible in the original lower portion. Keep their45px separation and follow their real tangents UP into the gap. The ivory band must have exactly the original width; no thin substituted bevel, added stripe or moved lower edge. Connect the retained top endpoint smoothly, without a ledge, bulge, angular kink, double contour or width jump. Reconnect the left gray slab edge to its genuine original counterpart as well.
The broad gray stone surface is smooth and quiet with very low-contrast shading, no clouds, veins or speckles. Continue its actual original color and texture. Ivory stone remains warm and clean with a shallow golden-brown bevel. Preserve all lower relief, floral carving, diagonal joints and rounded corners exactly where they are. This request only repairs the small top connection gap; it does not redesign any slab or ornament.
Image2 is a low-resolution location reminder ONLY. It cannot specify the precision contours or bevel width. Always follow the actual original native pixels of image1; never replace them with this guide, never enlarge the guide into final pixels. Image3 is the approved clean bright rounded Daoist Q-version STYLE reference only, with no UI/text/figures imported.
No resizing, zoom, camera move, rotation, global recolor, whole-image redraw, extra seams, props, motifs, frame, text or watermark. The rectangular gap boundary is invisible and must not become a physical line. Return one fully opaque1254 square with only the local191-row connection completed.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('source-checkpoint-snapshot.json',cp)
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':'r04_c01','operation':'AI connection repair with window shifted884px down; lower999 native pixels','globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None,'repairPixels':int(missing.sum()),'retainedOriginalNativePixels':int(known.sum()),'retainedCandidatePixels':int((~known&~missing).sum())})
write('preparation.json',{'nativeInputs':used,'retainedCandidate':info(source),'retainedCandidateCropLTRB':[0,372,1254,436],'retainedCandidatePasteXY':[0,0],'sourceCheckpointSnapshot':info(OUT/'source-checkpoint-snapshot.json'),'originalContext':info(OUT/'original-context.png'),'references':[{**info(p),'role':r} for p,r in zip(refs,['localized target: lower999+side native sources, upper64 retained candidate,191px missing','canonical geometry only; forbidden finished pixels','approved primary style'])],'repairMask':info(OUT/'repair-mask.png'),'missingRectangleLTRB':[115,64,1024,255],'globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'nativeScale':1,'guidePixelsAllowedInFinal':False,'geometryWarpApplied':False,'allWritesConfinedTo':str(OUT),'formalAccepted':False})
for p in [OUT/'original-context.png',OUT/'context.png',OUT/'repair-mask.png',OUT/'layout-reference-only.png']:
    write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(master)] if p.name=='layout-reference-only.png' else used+[info(source)],'operation':'reference-only canonical layout' if p.name=='layout-reference-only.png' else 'Exact native crops, placement and explicit transparent local gap; no resampling','newModelCalls':0,'nativeScale':1,'guidePixelsAllowedInFinal':False})
shutil.copy2(PIECE/'capability-evidence.json',OUT/'capability-evidence.json')
print(json.dumps({'directory':str(OUT),'context':info(OUT/'context.png'),'repairPixels':int(missing.sum()),'knownOriginalPixels':int(known.sum()),'retainedCandidatePixels':int((~known&~missing).sum())},ensure_ascii=False))
