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
source=PIECE/'repaired-v1/native.png'
assert sha(source)=='d3f09e10ff865fdd7e4087b8b37fe5be04485a947bfa9023229a0f1842133ae2'
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
canvas.paste(Image.open(source).convert('RGBA').crop((0,512,1254,767)),(0,0))
arr=np.asarray(canvas).copy();arr[known]=np.asarray(original)[known];canvas=Image.fromarray(arr);canvas.save(OUT/'context.png')
missing=arr[:,:,3]==0;assert int(missing.sum())==909*372
Image.fromarray((missing*255).astype(np.uint8)).save(OUT/'repair-mask.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in globalbox)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png';assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit / localized inpainting. Complete only the transparent rectangular gap of image1. Return the same1254 by1254 opaque image at unchanged native pixel scale, framing and camera.
Image1 is the EDIT TARGET with highly constrained native geometry. Its entire LOWER HALF, rows627..1253, is authentic finished original map art, not a suggestion. All of that lower627px is exactly positioned and must stay geometrically unchanged. The LEFT115 and RIGHT230 columns are also genuine original art. The TOP255 rows retain the useful newly rendered warm ivory middle slab and diagonal ivory cross-band. The only missing rectangle is x115..1024,y255..627. Paint only that gap to connect the upper painted form into the actual lower original map.
Geometry priority: the lower original gray slab, its left and right bevels, and both curved ivory bands define the only correct trajectories. Follow the long visible curves of the entire lower627px upward into the gap. Do not move the existing lower curves to fit the upper artwork. At the lower connection, the inner gray/right-ivory contour is at x877 around row631 and x858 around row668; continue its existing tangent precisely. Keep the broad ivory diagonal cross-band visible near the top complete, and connect its lower/right end smoothly into the original curve. No wrong-width ivory band, no widening bulge, no double contour, no angular kink. All these structures already exist; this is only a local repair of their connection.
Material priority: the upper retained middle slab is warm pale ivory/beige and must remain warm. The lower broad slab is quiet smooth gray; copy its actual lower native material character, about RGB175,170,167 near its top central face, and subtle broad shading rather than dense pale cloudy mottling. Ivory curves remain bright warm stone with restrained golden bevel shadow. Continue the original visible texture and lighting. No new cloudy pattern, cracks, mosaic or fine marbling.
Image2 is canonical broad GEOMETRY reference only at the exact same coordinates. It shows the general curved plaza arrangement, never finished pixels or texture. The actual native contours in image1 override this low-resolution guide. Never upscale/copy guide pixels into the finished artwork.
Image3 is the approved primary STYLE reference: clean, bright, full rounded Q-version Daoist fantasy handpainting. Use its finish and material discipline only. Do not import UI, lettering, icons, figures or decorative frames.
Keep all original lower-half imagery including any relief or ornament exactly in place. Preserve every opaque border strip and top retained form. No global recoloring, camera movement, zoom, rotation, cropping, resize, new motifs, buildings, border, text or watermark. Transparent boundaries are edit-mask boundaries, not real seams: no new edge at y255 or y627 or x115 or x1024. Return a fully opaque1254 square with only the local missing connection redrawn at the highest host finish.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('source-checkpoint-snapshot.json',cp)
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':'r04_c01','operation':'AI connection repair with window shifted512px down; lower627 native pixels','globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None,'repairPixels':int(missing.sum()),'retainedOriginalNativePixels':int(known.sum()),'retainedCandidatePixels':int((~known&~missing).sum())})
write('preparation.json',{'nativeInputs':used,'retainedCandidate':info(source),'retainedCandidateCropLTRB':[0,512,1254,767],'retainedCandidatePasteXY':[0,0],'sourceCheckpointSnapshot':info(OUT/'source-checkpoint-snapshot.json'),'originalContext':info(OUT/'original-context.png'),'references':[{**info(p),'role':r} for p,r in zip(refs,['localized target: lower627+side native sources, upper255 warm repair,372px missing','canonical geometry only; forbidden finished pixels','approved primary style'])],'repairMask':info(OUT/'repair-mask.png'),'missingRectangleLTRB':[115,255,1024,627],'globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'nativeScale':1,'guidePixelsAllowedInFinal':False,'geometryWarpApplied':False,'allWritesConfinedTo':str(OUT),'formalAccepted':False})
for p in [OUT/'original-context.png',OUT/'context.png',OUT/'repair-mask.png',OUT/'layout-reference-only.png']:
    write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(master)] if p.name=='layout-reference-only.png' else used+[info(source)],'operation':'reference-only canonical layout' if p.name=='layout-reference-only.png' else 'Exact native crops, placement and explicit transparent local gap; no resampling','newModelCalls':0,'nativeScale':1,'guidePixelsAllowedInFinal':False})
shutil.copy2(PIECE/'capability-evidence.json',OUT/'capability-evidence.json')
print(json.dumps({'directory':str(OUT),'context':info(OUT/'context.png'),'repairPixels':int(missing.sum()),'knownOriginalPixels':int(known.sum()),'retainedCandidatePixels':int((~known&~missing).sum())},ensure_ascii=False))
