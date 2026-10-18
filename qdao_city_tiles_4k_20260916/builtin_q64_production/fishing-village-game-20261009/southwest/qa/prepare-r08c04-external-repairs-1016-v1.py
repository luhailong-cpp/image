import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';n=z/'native'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,o):assert not p.exists();p.write_text(json.dumps(o,indent=2),encoding='utf-8')
tr=q/'join-r08c04-1016-v4-trace.json';trace=json.loads(tr.read_text());ar={t['tile']:np.asarray(Image.open(t['candidate']['path']).convert('RGB')) for t in trace['tiles']}
se=q/'west-corner-r08r09c04c05-v3-r09_c05-candidate-4096.png';ar['r09_c05']=np.asarray(Image.open(se).convert('RGB'))
specs=[('d',[3469,700,4723,1954],'Repair the mismatched stone staircase across x=627. The entire RIGHT half x>=627 is a fixed accepted neighbouring image and MUST remain unchanged. Repaint only the LEFT half x<627 to connect EACH matching tread and riser smoothly into the right half. Preserve the stair count of the accepted right side, parallel straight nosings, coherent uniform riser height and perspective, quiet pale stone. Remove the jagged vertical splice and all step-height jumps. Do not disguise mismatches as broken stone, cracks or shadows. Continue the left side back into the unchanged outermost 100-pixel left border and keep top and bottom 100 pixels anchored. No curved treads, tapering, splitting or merged steps.'),
('e',[3469,1600,4723,2854],'Repair mismatched paving and stair foot around x=627,y=150..700. The entire RIGHT half x>=627 is a fixed accepted neighbour and MUST remain unchanged. Repaint only LEFT x<627,y=80..850 to join the lowest stair nosing, diagonal pavement joints and wall top coherently to the right half. Remove zigzag seams, interrupted or doubled joints and any flat vertical tone boundary. Preserve stone size, quiet natural pale grey palette, shadows, wall silhouette, foliage and water. Keep outermost 100-pixel left border and top/bottom 100 pixels unchanged.'),
('f',[3469,3469,4723,4723],'Repair only the UPPER LEFT quadrant x<627,y<627 to join the THREE already accepted other quadrants. All pixels where x>=627 OR y>=627 are fixed references and MUST remain unchanged. Remove the rectangular light/dark boundary along x=627 and y=627, continue the existing wall-base stone courses and diagonal pavement slab joints from right and below naturally into the upper-left. Keep wall silhouette and existing plants, give paving a coherent daylight texture and leaf shadows. No new stones, slab pattern restyling, artificial rectangle, color cast, blurry seam or doubled grout. Preserve outermost 100-pixel top and left borders of upper-left quadrant; edit only inside the new upper-left quadrant.')]
for key,box,detail in specs:
 stem='r08_c04_repair_'+key+'_external_1016_v1';src=q/(stem+'-source-1254.png');out=np.zeros((1254,1254,3),np.uint8)
 for tile,(tx,ty) in {'r08_c04':(0,0),'r08_c05':(4096,0),'r09_c04':(0,4096),'r09_c05':(4096,4096)}.items():
  l=max(box[0],tx);t=max(box[1],ty);r=min(box[2],tx+4096);b=min(box[3],ty+4096)
  if l<r and t<b:out[t-box[1]:b-box[1],l-box[0]:r-box[0]]=ar[tile][t-ty:b-ty,l-tx:r-tx]
 assert not src.exists();Image.fromarray(out).save(src)
 prompt='Use case: precise-object-edit. Edit this exact native 1254x1254 hand-painted daylight game-art crop. Do not move, resize, zoom, crop or reframe any image. '+detail+' Keep the existing detailed rounded Q Daoist game-map style. Do not add text, UI, figures, props, smoothing or sharpened artifacts. Output exactly native 1254x1254.'
 pp=n/(stem+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
 req={'stem':stem,'tile':'r08_c04','patch':'repair_'+key,'prompt':pp.as_posix(),'tool':'image_gen__imagegen','route':'builtin','coordinates':{'tileContextBox':box,'globalContextBox':[12288+box[0],28672+box[1],12288+box[2],28672+box[3]],'sourceCoreBox':[115,115,1139,1139]},'references':[{'path':src.as_posix(),'sha256':sha(src),'role':'exact native joined edit target; only r08_c04 quadrant may change','dimensions':[1254,1254]}],'submittedParameters':{'transparent_background':False,'model':None,'quality':None,'referenced_image_paths':[src.as_posix()]},'actualModel':None,'baseTrace':{'path':tr.as_posix(),'sha256':sha(tr)}}
 wr(n/(stem+'.request.json'),req);wr(Path(str(src)+'.derivation.json'),{'operation':'integer core mosaic crop only, no resize','inputTrace':req['baseTrace'],'extraCornerSource':{'path':se.as_posix(),'sha256':sha(se)},'output':req['references'][0],'tileContextBox':box})

