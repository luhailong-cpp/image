from pathlib import Path
from PIL import Image
import json,hashlib,sys
z=Path(__file__).resolve().parents[1]
id=sys.argv[1]; x,y=map(int,sys.argv[2:4])
tile=z/'tiles/r03_c09-native-v1-20261016.png'
base=Image.open(tile).convert('RGB')
native=[32768+x,8192+y,32768+x+1254,8192+y+1254]
core=[native[0]+115,native[1]+115,native[0]+1139,native[1]+1139]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=z/'guides'/f'{id}.png';assert not g.exists();base.crop((x,y,x+1254,y+1254)).save(g)
src=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-wall-trees-v6.png')
scale=1254/57344
box=[v*scale for v in native]
lay=z/'guides'/f'{id}.layout-only.png'
Image.open(src).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(box),Image.Resampling.BICUBIC).save(lay)
d=dict(operation='exact1254 crop of selected native4K, no scale or blend',source=tile.as_posix(),sourceSha256=sha(tile),sourceCrop=[x,y,x+1254,y+1254],nativeWorldBox=native,coreWorldBox=core,coreCrop=[115,115,1139,1139],tileLocalPaste=[x+115,y+115],finalArt=False)
(g.with_suffix('.png.derivation.json')).write_text(json.dumps(d,indent=2),encoding='utf-8')
lay.with_suffix('.png.derivation.json').write_text(json.dumps(dict(source=src.as_posix(),sha256=sha(src),sourceBox=box,operation='coordinate crop enlarged only as layout authority, not final art',finalArt=False),indent=2),encoding='utf-8')
refs=[dict(file=g.as_posix(),sha256=sha(g),role='exact native edit target'),dict(file=lay.as_posix(),sha256=sha(lay),role='sole original exact coordinate topology authority'),dict(file=src.as_posix(),sha256=sha(src),role='full-map original context')]
for file in ['D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']:
 p=Path(file);refs.append(dict(file=file,sha256=sha(p),role='approved Daoist Q handpainted style only; noUI/night/people'))
(z/'prompts'/f'{id}.inputs.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
print(json.dumps(dict(id=id,native=native,core=core,refs=refs),indent=2))

