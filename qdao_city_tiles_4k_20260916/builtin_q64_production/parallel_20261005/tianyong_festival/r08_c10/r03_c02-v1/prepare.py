from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

OUT = Path(__file__).resolve().parent
TASK = OUT.parents[1]
ROOT = Path('D:/work/image')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
info = lambda p: {'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(name, obj):
    p = OUT / name
    assert p.resolve().is_relative_to(OUT)
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')

checkpoint_file = TASK / 'source-checkpoint.json'
checkpoint = read(checkpoint_file)
fragment = Path(checkpoint['fragment']['file'])
assert checkpoint['sourcePairVerified'] and checkpoint['resumeAuthorizedByUser']
assert checkpoint['fragment']['tileLocalLTRB'] == [909,2957,3187,4096]
assert sha(fragment) == checkpoint['fragment']['sha256'] == '2b6c3188eaaea9329507903b29ddaa74965db3e6be20a7aaa8c5ea2867467c2f'
global_box = [37773,30605,39027,31859]
tile_box = [909,1933,2163,3187]
with Image.open(fragment) as im:
    im.load()
    assert im.size == (2278,1139)
    strip = im.convert('RGBA').crop((0,0,1254,230))
context = Image.new('RGBA',(1254,1254),(0,0,0,0))
context.paste(strip,(0,1024))
context.save(OUT/'context.png')
master = ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master) == 'aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:
    im.load()
    assert im.size == (6144,6144)
    im.convert('RGB').resize((1254,1254), Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in global_box)).save(OUT/'layout-reference-only.png')
style=ROOT/'designs/gameplay-ui/04-guild.png'
assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
roles=['edit target: actual native context exists ONLY in the BOTTOM 230 rows; upper 1024 rows transparent and missing','canonical broad layout at same world coordinates only; enlarged guide pixels forbidden as final pixels','primary user-approved rendering style only; no UI, text, characters, symbols or layout imported']
refs=[OUT/'context.png',OUT/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit / outpainting.
Asset: one exact native terrain crop of the original game 五行奇谈, r08_c10 internal patch r03_c02. Return one complete opaque 1254 by 1254 square, exactly the framing of image 1.
Image 1 is the EDIT TARGET. Authentic completed native artwork exists ONLY in its BOTTOM 230 rows (y=1024 through 1253). The upper 1024 rows are transparent missing map area. Keep the bottom artwork unchanged: exact stone boundaries, curved band tangents, bevel thickness, contour positions, material, shadows, lighting and scale. Extend the existing shapes upward into the transparency from the exact endpoints and tangents. Do not relocate, reinterpret, duplicate or erase the known bottom contours. There is no known left strip.
Image 2 is a separate broad canonical layout reference for this exact same world crop. Use it to determine the continuation of the large plaza stone slabs and curved bands only. The exact native geometry of image 1 has priority where the references differ. Never copy or enlarge the blurry pixels, tiny marks or texture of image 2. Render new crisp native detail for the missing area.
Image 3 is the user-confirmed PRIMARY STYLE reference only: bright clean, full rounded Q/chibi Daoist fantasy handpainted forms, restrained precise contour shading, smooth warm ivory stone, subtle gold trim and neutral slate stone. Do not import its UI, characters, lettering, frame, props or layout.
Continue a single continuous plaza surface, with the original curved paving bands and broad smooth stone planes. The straight transparency boundary is not an object or stone joint: no new line, bevel, rectangular panel, inset, shadow, color band or extra paving division at y=1024. No invented building, plant, character, emblem or ornament. Quiet low-contrast broad mineral shading only; no marble veins, noise, cracks, speckles, dirt, mottled polygons, exaggerated outlines or blur. Do not zoom, rotate, move the camera or change scale. Preserve all existing known pixels as closely as possible; paint the transparent upper area. Highest visual finish available through the host. Output only the exact opaque square scene crop, no text, watermark or border.'''
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r03_c02','tile':'r08_c10','globalCropLTRB':global_box,'tileLocalCropLTRB':tile_box,'knownPixels':1254*230,'missingPixels':1254*1024,'knownRegionLTRB':[0,1024,1254,1254],'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json')})
write('preparation.json',{'taskLocalSourceCheckpoint':info(checkpoint_file),'checkpointSnapshot':checkpoint,'nativeInputs':[info(fragment)],'master':info(master),'references':[{**info(p),'role':role} for p,role in zip(refs,roles)],'nativeScale':1,'guidePixelsAllowedInFinal':False,'sourceFragmentCropLTRB':[0,0,1254,230],'contextPasteXY':[0,1024],'globalCropLTRB':global_box,'tileLocalCropLTRB':tile_box,'nativeContextBottomOnly':True,'otherTaskFilesModified':False})
write('context.png.generation.json',{'file':str(OUT/'context.png'),'sha256':sha(OUT/'context.png'),'width':1254,'height':1254,'derivedFrom':[info(fragment)],'operation':'Exact crop [0,0,1254,230], paste [0,1024] over transparent 1254 square. No resizing.','newModelCalls':0,'nativeScale':1})
write('layout-reference-only.png.generation.json',{'file':str(OUT/'layout-reference-only.png'),'sha256':sha(OUT/'layout-reference-only.png'),'width':1254,'height':1254,'derivedFrom':[info(master)],'operation':'Reference-only BICUBIC sampling of canonical6144 source box [v*3/32 for v in globalCropLTRB]. Forbidden in final artwork.','sourceCropLTRB':[v*3/32 for v in global_box],'newModelCalls':0,'guidePixelsAllowedInFinal':False})
write('capability-evidence.json',{'sameProductionBatch':True,'taskCapabilityEvidence':info(TASK/'model-capability.json'),'taskCapabilitySnapshot':read(TASK/'model-capability.json'),'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'sizeSelectorAvailable':False,'actualModel':None,'actualQuality':None})
assert sha(fragment)==checkpoint['fragment']['sha256']
print(json.dumps({'out':str(OUT),'globalCropLTRB':global_box,'knownPixels':1254*230,'missingPixels':1254*1024}))
