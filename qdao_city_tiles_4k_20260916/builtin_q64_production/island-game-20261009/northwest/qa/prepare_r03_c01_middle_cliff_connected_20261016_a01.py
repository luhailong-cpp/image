from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");stem='r03_c01_middle_cliff_connected_20261016_a01';box=[1350,2300,2604,3554]
def pin(p):return dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
base=Z/'tiles/r03_c01_candidate-v6_4096.png';record=base.with_suffix('.native-repair.json')
assert pin(base)['sha256']=='0fad4d4bc608ad65dbbe8ca644e1649a470e48a5d0c9a190bbfe3b7d51514dbb'
assert pin(record)['sha256']=='8004ae7308c53c8b69614ee91960310e10f573b942a42e28038bb318cee5b5cf'
crop=Z/'guides'/f'{stem}.native-crop.png';der=Z/'guides'/f'{stem}.native-crop.derivation.json'
ip=Z/'guides'/f'{stem}.input.json';rp=Z/'guides'/f'{stem}.references.json'
assert all(not x.exists() for x in [crop,der,ip,rp])
im=Image.open(base);assert im.size==(4096,4096);im.crop(box).save(crop)
derived={**pin(base),'assemblyRecord':pin(record)}
d=dict(derivedFrom=derived,cropBox=box,operation='native-coordinate crop',resizing=False,registration=False,feathering=False,colorCorrection=False,output={**pin(crop),'nativeSize':[1254,1254]})
der.write_text(json.dumps(d,indent=2))
refs=[{**pin(crop),'nativeSize':[1254,1254],'role':'exact native edit target; repair one vertical cliff silhouette clipping discontinuity; preserve same layout and coordinates','derivedFrom':derived}]
i=dict(stem=stem,tileId='r03_c01',tileCropBox=box,globalBox=[1350,10492,2604,11746],nativeSize=[1254,1254],inputs=refs,editTarget={**pin(crop),'derivationRecord':pin(der)},operation='exact native-coordinate crop for builtin local repair',layoutPixelsForbiddenInFinal=True,isFinalArt=False)
ip.write_text(json.dumps(i,indent=2));rp.write_text(json.dumps(dict(inputs=refs),indent=2))
print(json.dumps({'crop':pin(crop),'input':pin(ip)}))

