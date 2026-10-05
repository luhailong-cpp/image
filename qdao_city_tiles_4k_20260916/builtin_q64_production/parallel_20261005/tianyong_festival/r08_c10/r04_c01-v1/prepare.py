from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
TASK=OUT.parent.parent
ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/completion_20261004/c08/adjacent-qa'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
assert not (OUT/'request.json').exists()
cp=read(TASK/'source-checkpoint.json')
assert cp['sourcePairVerified'] and cp['resumeAuthorizedByUser']
fragment=Path(cp['fragment']['file']);bottom=Path(cp['bottom']['file'])
assert sha(fragment)==cp['fragment']['sha256'] and sha(bottom)==cp['bottom']['sha256']
left=BASE/'coupled-v1/r08_c09.png'
corner=BASE/'coupled-v2/r09_c09.png'
assert sha(left)=='cf26fe97c8707b5b11576b3f697f140482e832fa3627759da243729439efdfec'
assert sha(corner)=='db9d416d01b5ae0d094a505fef43446bc67e3911c7dd1a7c656584bfae966025'
for p in [left,corner,bottom]:assert Image.open(p).size==(4096,4096)
leftpixels=np.asarray(Image.open(left).convert('RGB'))
newleftpixels=np.asarray(Image.open(BASE/'coupled-v2/r08_c09.png').convert('RGB'))
cornerpixels=np.asarray(Image.open(corner).convert('RGB'))
oldcornerpixels=np.asarray(Image.open(BASE/'coupled-v1/r09_c09.png').convert('RGB'))
assert np.array_equal(leftpixels[:,-115:],newleftpixels[:,-115:])
assert np.array_equal(cornerpixels[:,-115:],oldcornerpixels[:,-115:])
cornercrop=cornerpixels[:115,3981:4096]
assert hashlib.sha256(cornercrop.tobytes()).hexdigest()=='cffcf635a83efcdcf915ab5ce67e63a5268fd5a956a9538b298459af619ccbad'
write('source-checkpoint-snapshot.json',cp)
write('corner-source-evidence.json',{'left':info(left),'corner':info(corner),'selection':info(BASE/'current-selection.json'),'selectionSnapshot':read(BASE/'current-selection.json'),'leftV2':info(BASE/'coupled-v2/r08_c09.png'),'cornerV1':info(BASE/'coupled-v1/r09_c09.png'),'v1V2Rightmost115FullHeightIdentical':True,'cornerCropLTRB':[3981,0,4096,115],'cornerRawRGBByteSha256':hashlib.sha256(cornercrop.tobytes()).hexdigest(),'scope':'Verified genuine source and required ROI equality only; external corner and r09_c09/r09_c10 seam have no formal acceptance evidence','formalAccepted':False})

box=[-115,2957,1139,4211];globalbox=[36749,31629,38003,32883]
canvas=Image.new('RGBA',(1254,1254),(0,0,0,0))
used=[]
def paste(source,srcbox,role):
    lx,ty=max(box[0],srcbox[0]),max(box[1],srcbox[1]);rx,bt=min(box[2],srcbox[2]),min(box[3],srcbox[3])
    assert lx<rx and ty<bt
    im=Image.open(source).convert('RGBA');assert im.size==(srcbox[2]-srcbox[0],srcbox[3]-srcbox[1])
    crop=[lx-srcbox[0],ty-srcbox[1],rx-srcbox[0],bt-srcbox[1]];xy=[lx-box[0],ty-box[1]]
    canvas.paste(im.crop(crop),xy)
    used.append({**info(source),'role':role,'sourceTileLocalBox':srcbox,'cropLTRB':crop,'pasteXY':xy[:2],'pasteLTRB':xy,'nativeScale':1})
paste(fragment,cp['fragment']['tileLocalLTRB'],'right230 original native strip')
paste(left,[-4096,0,0,4096],'left115 original native strip')
paste(bottom,[0,4096,4096,8192],'bottom115 original native strip except lower-left corner')
paste(corner,[-4096,4096,0,8192],'bottom-left115 square original native corner')
canvas.save(OUT/'context.png')
known=np.asarray(canvas)[:,:,3]==255
expected=np.ones((1254,1254),bool);expected[:1139,115:1024]=False
assert np.array_equal(known,expected)
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in globalbox)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit / outpainting. Produce one exact1254 by1254 opaque native-detail square crop of the Chinese Daoist Q-version fantasy game plaza. Keep the exact framing and pixel scale of image1.
Image1 is the EDIT TARGET. Authentic original map pixels are visible on LEFT115 columns, RIGHT230 columns, and BOTTOM115 rows. The bottom-left115 square is also genuine native artwork, already present. The central transparent missing rectangle is x115..1024 and y0..1139. Paint that missing rectangle as one coherent continuation of the surrounding plaza surface. Preserve all opaque original contours, curve tangents, bevel widths, depth, material, scale, texture density and illumination. Match every contour that enters the missing region at exactly its visible endpoint. Do not move the left, right or bottom reference pixels. Do not create an edge at x115, x1024 or y1139 because the edit mask ends there.
Image2 is a broad canonical GEOMETRY reference only, sampled at these same global coordinates from the original city layout. Use it only to understand the large stone/ivory arrangement that connects the real image1 edges. Its enlarged pixels, blur, incidental marks and texture must never become finished image pixels. Authentic image1 geometry takes priority wherever the two differ. This is a close crop of an existing curved stone plaza pattern, with broad ivory/gold bands and gray inset paving and gentle rounded bevels. Continue only the existing features; do not invent buildings, trees, props, inscriptions or decorative motifs.
Image3 is the approved PRIMARY STYLE reference only: clean, bright, rounded, full Q-version Daoist fantasy handpainted materials with controlled shallow bevel lighting and restrained fine surface detail. Do not copy any UI, lettering, icons, characters or frames from it.
Render the missing region sharply at the same native scale as the visible artwork. Keep quiet broad stone surfaces and low-contrast texture, no new cracks, marbling, speckles or noisy mosaic. No extra panel boundaries, fake seams, rectangular color patches, gaps, doubled contours or shadows at the transparency boundaries. Do not zoom, rotate, rescale, shift the camera, add a border, text or watermark. Return one opaque1254 square, seamlessly continuing the real pixels on three sides. Highest visual finish available through the host.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':'r04_c01','globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'knownPixels':int(known.sum()),'missingPixels':int((~known).sum()),'configSnapshot':read(ROOT/'config/image-generation.json'),'payload':payload,'submittedModel':None,'submittedQuality':None,'submittedSize':None})
write('preparation.json',{'sourceCheckpointSnapshot':info(OUT/'source-checkpoint-snapshot.json'),'nativeInputs':used,'references':[{**info(p),'role':r} for p,r in zip(refs,['edit target with native left/right/bottom context','canonical geometry only; forbid final pixels','approved primary rendering style only'])],'master':info(master),'cornerEvidence':info(OUT/'corner-source-evidence.json'),'globalCropLTRB':globalbox,'tileLocalCropLTRB':box,'nativeScale':1,'guidePixelsAllowedInFinal':False,'allWritesConfinedTo':str(OUT),'formalAccepted':False})
for p in refs[:2]:write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'newModelCalls':0,'derivedFrom':used if p.name=='context.png' else [info(master)],'operation':'Exact native pixel crops and transparent missing region' if p.name=='context.png' else 'Reference-only enlarged canonical crop; forbidden as final output pixels'})
shutil.copy2(TASK/'model-capability.json',OUT/'capability-evidence.json')
Image.fromarray(np.asarray(canvas)[1024:1254,:230]).save(OUT/'qa-source-bottom-left230.png')
print(json.dumps({'directory':str(OUT),'knownPixels':int(known.sum()),'missingPixels':int((~known).sum()),'nativeInputs':used,'context':info(OUT/'context.png')},ensure_ascii=False))
