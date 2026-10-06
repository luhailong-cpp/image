from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
ORIG=OUT.parent
TASK=ORIG.parent.parent
ROOT=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
assert sha(ORIG/'native.png')=='168c4928c746355cb4c8474d80b3d3ecab24e4234808487a941fd33d911a3587'
cp=read(TASK/'source-checkpoint.json');assert cp['sourcePairVerified'] and cp['resumeAuthorizedByUser']
fragment=Path(cp['fragment']['file']);bottom=Path(cp['bottom']['file'])
assert sha(fragment)==cp['fragment']['sha256'] and sha(bottom)==cp['bottom']['sha256']
oldprep=read(ORIG/'preparation.json')
left=Path(oldprep['nativeInputs'][1]['file']);corner=Path(oldprep['nativeInputs'][3]['file'])
assert sha(left)==oldprep['nativeInputs'][1]['sha256'];assert sha(corner)==oldprep['nativeInputs'][3]['sha256']
box=[-115,2957,1139,4211]
originalcontext=Image.new('RGBA',(1254,1254),(0,0,0,0));used=[]
def paste(source,srcbox,role):
    lx,ty=max(box[0],srcbox[0]),max(box[1],srcbox[1]);rx,bt=min(box[2],srcbox[2]),min(box[3],srcbox[3])
    assert lx<rx and ty<bt
    im=Image.open(source).convert('RGBA');assert im.size==(srcbox[2]-srcbox[0],srcbox[3]-srcbox[1])
    crop=[lx-srcbox[0],ty-srcbox[1],rx-srcbox[0],bt-srcbox[1]];xy=(lx-box[0],ty-box[1])
    originalcontext.paste(im.crop(crop),xy)
    used.append({**info(source),'role':role,'cropLTRB':crop,'pasteXY':list(xy),'nativeScale':1})
paste(fragment,cp['fragment']['tileLocalLTRB'],'current right230 original native strip')
paste(left,[-4096,0,0,4096],'frozen left115 original native strip; required ROI verified equal to current coupled-v2')
paste(bottom,[0,4096,4096,8192],'current bottom115 original native strip')
paste(corner,[-4096,4096,0,8192],'verified bottom-left115 square')
originalcontext.save(OUT/'original-context.png')
known=np.asarray(originalcontext)[:,:,3]==255
raw=np.asarray(Image.open(ORIG/'native.png').convert('RGBA')).copy()
warm_polygon=[(561,373),(1024,433),(1024,690),(968,790),(438,659)]
lower_polygon=[(395,775),(902,916),(948,783),(1024,675),(1024,1139),(115,1139),(115,1040)]
maskimage=Image.new('L',(1254,1254),0);draw=ImageDraw.Draw(maskimage)
draw.polygon(warm_polygon,fill=255);draw.polygon(lower_polygon,fill=255)
missing=(np.asarray(maskimage)>0)&(~known)
raw[missing]=[0,0,0,0]
raw[known]=np.asarray(originalcontext)[known]
Image.fromarray(raw).save(OUT/'context.png')
Image.fromarray((missing*255).astype(np.uint8)).save(OUT/'repair-mask.png')
Image.open(ORIG/'layout-reference-only.png').save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit / localized inpainting. Repair only the transparent holes of image 1. Return the same exact1254 by1254 opaque square at the same native scale and framing. This is a local seam/material repair of existing art, NOT a new whole composition.
Image1 is the edit target. Most of its finished upper/central art, curved ivory bands and broad diagonal ivory cross-band remain visible and must be retained. The original authoritative native pixels have been restored on LEFT115 columns, RIGHT230 columns and BOTTOM115 rows, including the bottom-left115 square. The remaining opaque interior is the usable newly painted body; retain its already correct stone outlines and the broad ivory cross-band. Only the transparent central stone-face hole and lower connection hole need new paint.
Repair1: The central middle stone face around x450..1024,y380..790 MUST be warm pale ivory/beige, exactly matching the original warm native surface entering from the RIGHT edge around x1024,y480..560. That warm reference is about RGB241,221,193 in its softly lit face. It is NOT slate gray. Continue that same single warm stone face across the hole, matching its top thin joint and its boundary above the broad ivory cross-band. Do not leave a cool-gray patch against the right edge, and do not merely tint an isolated strip. Draw one coherent quiet warm stone slab surface matching the visible original material.
Repair2: In the lower hole, REDRAW the existing lower gray slab contour and the inner side of the right curved ivory band so they arrive at the exact real BOTTOM contour positions and tangents. At image row1143 the true right gray/ivory boundary is around x877, then around x858 at row1180 and x837 at row1220. Those original native pixels in the visible bottom strip are authoritative. The previous displaced contour has been removed. Join smoothly from the retained upper curved structure into these real endpoints; no sudden width change, bulge, double edge or bend at the hole boundary. Also reconnect the lower left slab contour to the exact visible original bottom edge. The lower gray face must match the quiet smooth original gray in the bottom strip (central face around RGB175,170,167), with only subtle low-contrast shading, not the pale dense clouded mottling of the previous attempt. No added new structure.
Image2 is ONLY broad canonical geometry at these exact world coordinates. It guides existing curved paving arrangement and the broad diagonal cross-band, never pixels or texture. Preserve the already rendered broad diagonal ivory cross-band and its substantial width. The real opaque pixels of image1 always overrule the low-resolution guide. Do not enlarge/copy guide pixels into the finished art.
Image3 is the approved primary STYLE reference only: clean, bright, rounded Daoist Q-version fantasy handpainting with controlled shallow bevels and restrained material texture. Do not import UI, text, frames, icons, characters or props.
All missing/opaque boundaries are invisible editing boundaries, not physical seams. Paint only their missing surfaces and reconnect all outlines to existing positions. No new buildings, motifs, borders, text, watermark, cracks or extra grout lines. No camera shift, zoom, resize, rotation, global recoloring or wholesale redraw. Preserve original lower-right relief and every real left/right/bottom landmark. Return one fully opaque1254 square with a coherent local repair and the highest finish available through the host.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('source-checkpoint-snapshot.json',cp)
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':'r04_c01','operation':'one localized AI redraw repair; no geometric warp','globalCropLTRB':[36749,31629,38003,32883],'tileLocalCropLTRB':box,'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None,'repairPixels':int(missing.sum()),'retainedOriginalNativePixels':int(known.sum()),'retainedCandidatePixels':int((~missing&~known).sum())})
write('preparation.json',{'nativeInputs':used,'retainedCandidate':info(ORIG/'native.png'),'retainedCandidateRole':'Upper/central usable artwork only; superseded portions removed by repair mask','sourceCheckpointSnapshot':info(OUT/'source-checkpoint-snapshot.json'),'originalContext':info(OUT/'original-context.png'),'references':[{**info(p),'role':r} for p,r in zip(refs,['localized repair target with original native boundaries restored','canonical geometry reference only, forbidden final pixels','approved primary style'])],'repairMask':info(OUT/'repair-mask.png'),'repairPolygons':{'warmMiddleFace':warm_polygon,'lowerGeometryMaterial':lower_polygon},'knownOriginalPixelsAlwaysOverrideMask':True,'originalContextEqualsPreviousOnKnown':bool(np.array_equal(np.asarray(originalcontext)[known],np.asarray(Image.open(ORIG/'context.png'))[known])),'nativeScale':1,'guidePixelsAllowedInFinal':False,'allWritesConfinedTo':str(OUT),'formalAccepted':False})
for p in [OUT/'original-context.png',OUT/'context.png',OUT/'repair-mask.png',OUT/'layout-reference-only.png']:
    write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(ORIG/'layout-reference-only.png')] if p.name=='layout-reference-only.png' else used+[info(ORIG/'native.png')],'operation':'reference-only canonical layout' if p.name=='layout-reference-only.png' else 'Exact native context placement plus explicit transparent local repair holes; no resampling','newModelCalls':0,'nativeScale':1,'guidePixelsAllowedInFinal':False})
shutil.copy2(ORIG/'capability-evidence.json',OUT/'capability-evidence.json')
print(json.dumps({'directory':str(OUT),'context':info(OUT/'context.png'),'repairPixels':int(missing.sum()),'retainedCandidatePixels':int((~missing&~known).sum()),'nativeInputs':used},ensure_ascii=False))
