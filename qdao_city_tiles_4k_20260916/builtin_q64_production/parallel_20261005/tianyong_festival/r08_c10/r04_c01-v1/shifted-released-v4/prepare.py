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
box=[-115,3469,1139,4723];globalbox=[36749,32141,38003,33395]
original=Image.new('RGBA',(1254,1254),(0,0,0,0));used=[]
def paste(source,srcbox,role):
    lx,ty=max(box[0],srcbox[0]),max(box[1],srcbox[1]);rx,bt=min(box[2],srcbox[2]),min(box[3],srcbox[3])
    im=Image.open(source).convert('RGBA');assert im.size==(srcbox[2]-srcbox[0],srcbox[3]-srcbox[1]);assert lx<rx and ty<bt
    crop=[lx-srcbox[0],ty-srcbox[1],rx-srcbox[0],bt-srcbox[1]];xy=(lx-box[0],ty-box[1]);original.paste(im.crop(crop),xy)
    used.append({**info(source),'role':role,'cropLTRB':crop,'pasteXY':list(xy),'nativeScale':1})
paste(fragment,cp['fragment']['tileLocalLTRB'],'current right230 original native strip in upper627')
paste(left,[-4096,0,0,4096],'left115 original native strip in upper627')
paste(bottom,[0,4096,4096,8192],'bottom627 original native source across remaining1139 columns')
paste(corner,[-4096,4096,0,8192],'bottom-left115x627 original native corner source')
original.save(OUT/'original-context.png')
known=np.asarray(original)[:,:,3]==255
assert np.all(known[627:])
canvas=Image.new('RGBA',(1254,1254),(0,0,0,0))
candidate=Image.open(source).convert('RGBA')
canvas.paste(candidate.crop((600,0,850,96)),(600,0))
canvas.paste(candidate.crop((115,0,300,400)),(115,0))
arr=np.asarray(canvas).copy();arr[known]=np.asarray(original)[known];canvas=Image.fromarray(arr);canvas.save(OUT/'context.png')
missing=arr[:,:,3]==0;assert int(missing.sum())==909*627-250*96-185*400
Image.fromarray((missing*255).astype(np.uint8)).save(OUT/'repair-mask.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in globalbox)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png';assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit / native map inpainting. Complete the transparent missing regions of image1 at the exact1254x1254 framing, camera and native pixel scale. This is a local repair of a curved plaza connection.
Image1 is the edit target. The entire LOWER627 rows (y627..1253), LEFT115 columns and RIGHT230 columns are authentic original pixels at exact coordinates. They alone define the accurate curved slab geometry. A small warm-beige surface island at x600..850,y0..96 is retained as the actual material surface, not a framed panel. A stable left ivory area at x115..300,y0..400 is also retained. Do not create borders around those islands. All old uncertain right corners, cross-band endpoints and gray upper-edge outlines have been erased deliberately so they cannot force a wrong curve.
Extend the long visible ORIGINAL lower gray slab and its curved right boundary UPWARD into the missing region, preserving its native thickness, tangent and position. There are two distinct edges of the same thick bevel: near row632 the gray-face-to-dark edge is x831 and dark-to-ivory-bright edge is x876; near row877 they are x694 and x741. Keep their original45..47px separation. Do not thin the bevel or move the lower slab. Rebuild the gray slab's upper right corner and the adjoining ivory cross-band endpoint based on this true curve. The gap must reconnect at y627 with no sideways step, double line, widening bulge or angular kink. Follow the left original curve too.
Across the upper missing area, continue one warm pale ivory/beige stone face from the retained warm material island and the matching genuine warm face entering from the right edge. Rebuild its lower rounded boundary and the substantial diagonal ivory cross-band beneath it. That cross-band is visible in the broad layout, crossing approximately y140..390. It must remain a broad solid ivory stone strip, not a hairline seam. Its right corner is free to adjust to meet the true native lower curve; do not recreate the previously misplaced narrow shape.
The lower broad inset surface is smooth quiet gray, matching the actual lower native face. Match its gentle low-contrast shading and keep it free of cloudy mottling, cracks, veins or speckles. The warm upper face remains warm, not gray. Ivory curves have clean rounded golden-brown shallow bevels. Preserve all original lower relief and all genuine side and lower strips unchanged.
Image2 is ONLY a low-resolution location/arrangement reminder. It is not accurate enough for native curve position, bevel width, or stone texture. Every native contour, material and thickness in image1 takes priority. Never copy enlarged guide pixels into final artwork. Image3 is the approved bright clean rounded Daoist Q-version STYLE only; do not import its UI, text, figures, icons or frames.
No original-lower-image redraw, global recolor, zoom, resize, rotation, camera shift, new motifs, props, extra seams, text or watermark. Transparency and small retained-island boundaries are invisible editing boundaries, not physical edges. Return one fully opaque1254 square with the missing native connection genuinely redrawn, at highest available host finish.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('source-checkpoint-snapshot.json',cp)
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':'r04_c01','operation':'AI redraw after releasing old upper junction anchors; native lower627 and side strips authoritative','globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None,'repairPixels':int(missing.sum()),'retainedOriginalNativePixels':int(known.sum()),'retainedCandidatePixels':int((~known&~missing).sum())})
write('preparation.json',{'nativeInputs':used,'retainedCandidate':info(source),'retainedCandidateNativeCrops':[{'cropLTRB':[600,0,850,96],'pasteXY':[600,0],'role':'warm face interior only, no corner or border'},{'cropLTRB':[115,0,300,400],'pasteXY':[115,0],'role':'stable left ivory area'}],'sourceCheckpointSnapshot':info(OUT/'source-checkpoint-snapshot.json'),'originalContext':info(OUT/'original-context.png'),'references':[{**info(p),'role':r} for p,r in zip(refs,['localized target: lower627+side native sources, warm interior/stable left islands only, old upper junction contours released','canonical geometry only; forbidden finished pixels','approved primary style'])],'repairMask':info(OUT/'repair-mask.png'),'missingRegion':'upper627 interior except two retained native islands; see repair-mask.png','globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'nativeScale':1,'guidePixelsAllowedInFinal':False,'geometryWarpApplied':False,'allWritesConfinedTo':str(OUT),'formalAccepted':False})
for p in [OUT/'original-context.png',OUT/'context.png',OUT/'repair-mask.png',OUT/'layout-reference-only.png']:
    write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(master)] if p.name=='layout-reference-only.png' else used+[info(source)],'operation':'reference-only canonical layout' if p.name=='layout-reference-only.png' else 'Exact native crops, placement and explicit transparent local gap; no resampling','newModelCalls':0,'nativeScale':1,'guidePixelsAllowedInFinal':False})
shutil.copy2(PIECE/'capability-evidence.json',OUT/'capability-evidence.json')
print(json.dumps({'directory':str(OUT),'context':info(OUT/'context.png'),'repairPixels':int(missing.sum()),'knownOriginalPixels':int(known.sum()),'retainedCandidatePixels':int((~known&~missing).sum())},ensure_ascii=False))
