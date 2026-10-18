from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=Z/'tiles/connected-r05-r06-cross-v5/r06_c04_rail-ground-v1_4096.png'
rec=base.with_suffix('.cross-native-repair.json')
stem='r06_c04_internal_westmid_tip_20261016_a01'
box=[397,953,1651,2207]
crop=Z/'guides'/f'{stem}.native-crop.png';der=Z/'guides'/f'{stem}.native-crop.derivation.json'
assert not crop.exists() and not der.exists()
im=Image.open(base);assert im.size==(4096,4096)
assert sha(base)=='b5bdcb1ca9c5bcb4b7facd74ad57b9aac42aeb12e1ff0eb33f611db5525fdcd4'
im.crop(box).save(crop)
d=dict(derivedFrom=dict(path=base.as_posix(),sha256=sha(base),assemblyRecord=dict(path=rec.as_posix(),sha256=sha(rec))),cropBox=box,operation='native-coordinate crop',resizing=False,registration=False,feathering=False,colorCorrection=False,output=dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254]))
der.write_text(json.dumps(d,indent=2))
inp=dict(stem=stem,tileId='r06_c04',tileCropBox=box,globalBox=[x+y for x,y in zip(box,[12288,20480,12288,20480])],nativeSize=[1254,1254],inputs=[dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254],role='Exact native edit target; reconnect one interrupted paving groove near crop(627,627)',derivedFrom=d['derivedFrom'])],editTarget=dict(path=crop.as_posix(),sha256=sha(crop),derivationRecord=dict(path=der.as_posix(),sha256=sha(der))),operation='exact native-coordinate crop for builtin local repair',layoutPixelsForbiddenInFinal=True,isFinalArt=False)
ip=Z/'guides'/f'{stem}.input.json';ip.write_text(json.dumps(inp,indent=2))
(Z/'guides'/f'{stem}.references.json').write_text(json.dumps({'inputs':inp['inputs']},indent=2))
out=Z/'qa/r06_c04_internal_attempt_audit_20261016';out.mkdir(exist_ok=False)
hist=[
 ('southmid_grout_a01',[420,170,870,520]),('southmid_grout_a02',[420,170,870,520]),
 ('southeast_grout_a01',[1050,100,1254,420]),('southeast_tip_a01',[650,100,970,420])]
a=[]
for key,b in hist:
 p=Z/'native'/f'r06_c04_{key}.png';q=out/f'{key}_native_issue_region.png'
 Image.open(p).crop(b).save(q)
 a.append({'source':str(p),'sha256':sha(p),'cropBox':b,'output':str(q),'outputSha256':sha(q),'resize':False})
(out/'crop_derivations.json').write_text(json.dumps(a,indent=2))
print(json.dumps({'crop':str(crop),'input':str(ip),'attemptRegions':a}))

