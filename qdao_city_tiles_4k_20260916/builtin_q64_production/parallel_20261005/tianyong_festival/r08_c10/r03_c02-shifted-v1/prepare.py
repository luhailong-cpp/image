from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
TASK=OUT.parents[1]
ROOT=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
source=TASK/'r08_c10/current/v002/r08_c10-fragment.png'
older=TASK/'r08_c10/current/v001/r08_c10-fragment.png'
assert sha(source)=='9d97cd1126d2c7edbb2df25561510fb17fb0b071a132e2bb3b0db3ace2855f88'
assert sha(older)=='2b6c3188eaaea9329507903b29ddaa74965db3e6be20a7aaa8c5ea2867467c2f'
with Image.open(source) as im:
    im.load();assert im.size==(3187,1139)
    strip=im.convert('RGBA').crop((0,0,1254,627))
with Image.open(older) as im:oldstrip=im.convert('RGBA').crop((0,0,1254,627))
assert np.array_equal(np.asarray(strip),np.asarray(oldstrip))
context=Image.new('RGBA',(1254,1254),(0,0,0,0));context.paste(strip,(0,627));context.save(OUT/'context.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
global_box=[37773,31002,39027,32256];tile_box=[909,2330,2163,3584]
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in global_box)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png';assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
prompt='''Use case: precise-object-edit / exact upward terrain outpainting.
Return one fully opaque 1254 by 1254 square, exactly image1's framing. This is a close-up continuous game plaza pavement for 五行奇谈.
IMAGE 1 is the authoritative EDIT TARGET. Its entire BOTTOM HALF, 627 rows y=627..1253, is completed native artwork. Keep this known half unchanged: exact positions, widths, curved tangents, depth and shading of the three slate-gray inset panels and all ivory/gold divider edges. Only the TOP HALF, y=0..626, is transparent and missing. Paint the missing upper half by extending the visible slab borders upward from precisely the same native contour endpoints. There is no known left strip. Do not recenter, widen, straighten or shift the visible gray columns. No replacement of the known lower half by a fresh interpretation.
IMAGE 2 is the original broad structural layout at these exact world coordinates, ONLY for the missing top half. It establishes a substantial horizontal IVORY STONE CROSS-BAND spanning the entire width at approximately y=303..393, joining the ivory vertical dividers and separating the gray upper slabs from gray lower slabs. Newly render this real broad ivory stone band with its restrained rounded bevel, and continue the original vertical structures into the bottom native half. The lower native contour positions from image1 take priority over the blurry guide: never relocate the native columns to the guide. The cross-band is broad ivory stone, NOT thin dark seams inside gray slabs. No invented extra paving divisions. Do not copy enlarged pixels, blur or grain from image2.
IMAGE 3 is the approved PRIMARY STYLE reference only: bright clean plump rounded Q/chibi Daoist fantasy handpainting, quiet warm ivory stone and restrained gold bevels, neutral slate stone, controlled sculpted shading. Do not import UI, text, figures, icons, props or decorative motifs.
The transparent boundary at y=627 is not a stone joint or object. Make one continuous surface across it without any new horizontal seam, bevel, shadow, frame or color rectangle. The true ivory cross-band is around y=303..393, well ABOVE the former transparent boundary. Preserve every known pixel as closely as possible and create crisp new native detail in the missing half only. No buildings, foliage, characters, symbols, text, watermark, border or collage. No zoom, camera move, rotation or rescaling. No extra marble veins, cracks, speckles, grunge or dense mottled texture. Highest available visual finish; output only the exact opaque terrain crop.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
roles=['edit target: exact original native lower627; upper627 transparent missing','canonical layout only; broad ivory cross-band approx y303..393; forbidden final pixels','primary approved rendering style only']
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r03_c02-shifted','version':'v1','tile':'r08_c10','globalCropLTRB':global_box,'tileLocalCropLTRB':tile_box,'knownPixels':1254*627,'missingPixels':1254*627,'knownRegionLTRB':[0,627,1254,1254],'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json')})
write('preparation.json',{'nativeInputs':[info(source)],'nativeSourceTileLTRB':[909,2957,4096,4096],'sourceCropLTRB':[0,0,1254,627],'contextPasteXY':[0,627],'v002KnownCropExactlyEqualsV001':True,'comparedPixelCount':1254*627,'priorSource':info(older),'references':[{**info(p),'role':r} for p,r in zip(refs,roles)],'master':info(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'globalCropLTRB':global_box,'tileLocalCropLTRB':tile_box,'sourceCheckpointObserved':info(TASK/'source-checkpoint.json'),'sourceCheckpointSnapshot':read(TASK/'source-checkpoint.json'),'otherTaskFilesModified':False})
write('context.png.generation.json',{'file':str(OUT/'context.png'),'sha256':sha(OUT/'context.png'),'derivedFrom':[info(source)],'operation':'Exact source crop [0,0,1254,627] pasted at [0,627] over transparent1254 canvas. No resize.','newModelCalls':0})
write('layout-reference-only.png.generation.json',{'file':str(OUT/'layout-reference-only.png'),'sha256':sha(OUT/'layout-reference-only.png'),'derivedFrom':[info(master)],'sourceCropLTRB':[v*3/32 for v in global_box],'operation':'BICUBIC reference-only sampling, forbidden as final pixels.','newModelCalls':0})
write('capability-evidence.json',{'sameProductionBatch':True,'taskCapabilityEvidence':info(TASK/'model-capability.json'),'taskCapabilitySnapshot':read(TASK/'model-capability.json'),'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'actualModel':None,'actualQuality':None})
assert sha(source)=='9d97cd1126d2c7edbb2df25561510fb17fb0b071a132e2bb3b0db3ace2855f88'
print(json.dumps({'out':str(OUT),'nativeContextPixels':1254*627,'missingPixels':1254*627,'v002EqualsV001InContext':True}))
