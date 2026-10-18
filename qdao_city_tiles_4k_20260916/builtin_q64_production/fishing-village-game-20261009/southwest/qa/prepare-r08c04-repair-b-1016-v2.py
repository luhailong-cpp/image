import json,hashlib,sys,datetime
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';n=z/'native';stem='r08_c04_repair_b_1016_v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,o):assert not p.exists();p.write_text(json.dumps(o,indent=2),encoding='utf-8')
tr=q/'repair-r08c04-1016-v2-trace.json';a=json.loads(tr.read_text());b=[2445,397,3699,1651];src=q/(stem+'-source-1254.png');assert not src.exists();Image.open(a['candidate']['path']).crop(b).save(src)
p=n/(stem+'.prompt.txt');prompt='Use case: precise-object-edit. Make ONE strictly local correction to this exact native 1254x1254 painterly stone staircase image. Near x=460,y=720 there is an unnatural notch where two sections of ONE stone stair front lip fail to align. Repair only the small rectangle x=340..620,y=600..850: reconnect that interrupted single stair nosing, its shadow under the lip, and the riser immediately beneath it into a coherent continuous edge, matching the exact entry and exit positions at both sides of this rectangle. Do not shift the rest of this step, do not straighten or redraw the entire staircase, do not change adjacent slab joints, foliage, paving or the left stair side. All pixels outside this small repair rectangle, especially the outer 250-pixel border, must remain unchanged. Keep the exact original 1254x1254 canvas and framing, native fine stone detail and daylight palette. No resize, blur, repaint of large areas or new objects.'
assert not p.exists();p.write_text(prompt,encoding='utf-8')
req={'stem':stem,'tile':'r08_c04','patch':'repair_b','prompt':p.as_posix(),'tool':'image_gen__imagegen','route':'builtin','references':[{'path':src.as_posix(),'sha256':sha(src),'role':'exact native repair target','dimensions':[1254,1254]}],'coordinates':{'tileContextBox':b,'globalContextBox':[12288+b[0],28672+b[1],12288+b[2],28672+b[3]],'sourceCoreBox':[115,115,1139,1139],'repairBounds':[320,580,650,880]},'submittedParameters':{'transparent_background':False,'model':None,'quality':None,'referenced_image_paths':[src.as_posix()]},'actualModel':None,'baseTrace':{'path':tr.as_posix(),'sha256':sha(tr)}}
wr(n/(stem+'.request.json'),req);wr(Path(str(src)+'.derivation.json'),{'source':a['candidate'],'box':b,'operation':'integer crop, no resize'})

