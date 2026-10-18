from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent));import production_v2 as p
rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig');split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert T.name not in {t for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']}
old=T/'native/s02_01_native01.png';south=T/'native/s03_01_native01.png';p.validate_native(old,T,'s02_01');p.validate_native(south,T,'s03_01')
im=Image.open(old).convert('RGB')
im.paste(Image.open(south).convert('RGB').crop((115,115,980,230)),(115,1139))
f=T/'layout-only/s02_01_fix01.actual-core-guide.png';p.save_png(f,im)
p.write_json(f.with_suffix('.png.derivation.json'),{'role':'repair guide only, not generated art','editBase':{'file':str(old),'sha256':p.sha(old)},'nativeAnchor':{'file':str(south),'sha256':p.sha(south),'sourceBox':[115,115,980,230],'targetBox':[115,1139,980,1254],'sameWorld':True,'sourceResampled':False}},replace=False)
prompt='Edit this image IN PLACE with unchanged 1254 x 1254 canvas and camera. Fix only these local paving defects. The bottom strip y1139..1253, x115..979 is now exact existing south artwork and must stay fixed. Adjust the cream vertical border immediately above that strip to meet its bottom endpoint exactly, without a step, while retaining its existing top endpoint and width. Straighten the first diagonal seam entering from the left around x115,y388: extend its existing southwest-to-northeast direction as one straight uninterrupted line toward the top edge, removing the kink near x160,y340. Remove the short orphan diagonal groove near x110..180,y1030..1140; retain the long shallow diagonal joint across the bottom. Preserve every other slab joint, the exact left and right edges, colors, materials, light and scale. Ground is completely flat. Do not add objects, extra seams, text, blur or a frame. Output only the finished opaque square.'
args={'prompt':prompt,'referenced_image_paths':[str(f)],'transparent_background':False}
p.write_json(T/'planned/s02_01_fix01.parameters.json',args,replace=False)
p.write_json(T/'receipts/s02_01_fix01.rules-read.json',{'rulesActuallyRead':True,'agentsSha256':p.sha(p.REPO/'AGENTS.md'),'splitSha256':p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')},replace=False)
p.record_request(T.name,'s02_01_fix01',T/'planned/s02_01_fix01.parameters.json')
print(json.dumps(args))
