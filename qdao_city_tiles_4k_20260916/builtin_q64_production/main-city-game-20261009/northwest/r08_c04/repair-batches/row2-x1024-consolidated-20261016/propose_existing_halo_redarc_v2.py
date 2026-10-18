from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
reg=json.loads((T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/source-registry.json').read_text())
entry=next(x for x in reg['sources'] if x['id']=='s03_02')
source=Path(entry['file']);assert sha(source)==entry['sha256']
assert entry['nativeOriginInTile']==[909,1933]
roi=[403,101,468,120];x0,y0,x1,y1=roi
target=[1312,2034,1377,2053]
framebox=[915,1125,980,1144]
raw=Image.open(source).convert('RGB')
mask=np.zeros((1254,1254),np.uint8);mask[y0:y1,x0:x1]=255
Image.fromarray(mask).save(D/'red-arc-existing-source-mask.png')
trial=Image.open(D/'roi-trial01.png').convert('RGB');baseline=trial.copy()
trial.paste(raw.crop(roi),framebox[:2]);trial.save(D/'roi-trial-v2.png')
a=np.array(baseline);o=np.array(trial);patch=np.zeros((1254,1254),bool);patch[1125:1144,915:980]=True
assert np.array_equal(a[~patch],o[~patch])
assert np.array_equal(o[patch],np.array(raw)[mask==255])
# Actual ball lies below the replaced strip, entirely preserved.
assert np.array_equal(a[1145:1254,870:1030],o[1145:1254,870:1030])
for name,box in {'hardware':[870,1090,1030,1254],'north':[890,1105,1005,1140],'south':[890,1132,1005,1165],'west':[895,1105,930,1165],'east':[965,1105,1000,1165],'lower':[100,650,1150,1220],'bottom':[480,1040,820,1254]}.items():trial.crop(box).save(D/('v2-'+name+'.png'))
proposal={'status':'pending_root_independent_review','type':'existing_registered_native_source_halo_reselection','source':str(source),'sourceSha256':sha(source),'existingRegistryId':'s03_02','existingOwnerIndex':entry['ownerIndex'],'uniqueNativeSourceIncrement':0,'sourceWorldBox':entry['worldBoxWithHalo'],'sourceOriginInTile':entry['nativeOriginInTile'],'sameWorldNativeROI':roi,'targetTileROI':target,'mask':str(D/'red-arc-existing-source-mask.png'),'maskSha256':sha(D/'red-arc-existing-source-mask.png'),'maskMode':'L binary 0/255','selectedPixelCount':int((mask==255).sum()),'resampled':False,'blended':False,'outsideMaskPixelIdentical':True,'insideMaskNativePixelIdentical':True,'sourceGenerationRecord':entry['generationRecord'],'originalRegistryEntry':entry,'formalAccepted':False}
write(D/'red-arc-existing-source-proposal.json',proposal)
print(json.dumps({'existingOwnerIndex':entry['ownerIndex'],'sourceSha256':sha(source),'haloPixels':int((mask==255).sum()),'ballPixelsUnchanged':True},ensure_ascii=False))

