import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';n=z/'native'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=q/'full-tile-r08_c04-1016-v1-assembly.json';record=json.loads(a.read_text());base=Path(record['output']['path']);im=Image.open(base)
bad=['h1024-part01','v3072-part02','h1024-part04','h1024-part05','h2048-part05','intersection-x1024-y1024','intersection-x3072-y1024']
audit={'status':'repair_required','tile':'r08_c04','candidate':record['output'],'assembly':{'path':a.as_posix(),'sha256':sha(a)},'all39NativeCropsViewed':True,'checked':[dict(file=t['file'],sha256=t['sha256'],status='repair_required' if any(Path(t['file']).stem.endswith(v+'-100pct') for v in bad) else 'pass') for t in record['qa']],'issues':[{'id':'a','tileBox':[260,850,800,1120],'issue':'double or interrupted pavement grout at row1/row2 join'}, {'id':'b','tileBox':[2880,730,3960,1250],'issue':'stair nosing notch and doubled edge where horizontal/vertical seams cross'}, {'id':'c','tileBox':[3050,1800,3990,2250],'issue':'flat horizontal material boundary and misjoined stone joints at foot of steps'}],'externalJoins':'pending'}
wr(q/'r08c04-1016-v1-internal-art-audit.json',audit)
specs=[('a',[0,397,1254,1651],[230,440,820,750],'Repair only the small broken and doubled stone paving joints across the central horizontal band, approximately y=500..720. Each existing diagonal grout line should join smoothly once with consistent slab shape, with no short parallel ghost lines or zigzag splice. Preserve the adjacent gold foliage silhouette, existing paving positions, daylight shadows and exact image framing. No new objects.'),
('b',[2788,397,4042,1651],[100,330,1150,850],'Repair only the discontinuous stair nosing edges and ghost seams in central band x=100..1150,y=330..850. Continue each existing pale stone step as one straight uninterrupted nosing with same slope, height, tread width and riser shadow. Remove the central sharp notch and doubled shifted lip; no change of step count or perspective. Preserve all existing slab joints elsewhere, all lighting and exact framing.'),
('c',[2842,1421,4096,2675],[180,400,1150,830],'Repair only the unnatural straight horizontal splice and misjoined slab edges around the foot of the lowest stair, central band x=180..1150,y=400..830. Continue the existing stair lip and stone paving grout as single clean coherent lines; remove cut-off edges and horizontal tone seam while preserving existing stair silhouette, shadow and foliage. Do not move the stair foot or leaves.')]
for key,box,bounds,detail in specs:
 stem='r08_c04_repair_'+key+'_1016_v1';src=q/(stem+'-source-1254.png');assert not src.exists();im.crop(box).save(src)
 coords={'tileContextBox':box,'globalContextBox':[12288+box[0],28672+box[1],12288+box[2],28672+box[3]],'sourceCoreBox':[115,115,1139,1139],'repairBounds':bounds,'expectedNativeDimensions':[1254,1254]}
 refs=[{'path':src.as_posix(),'sha256':sha(src),'role':'exact native edit target, preserve framing and all pixels outside repair area','dimensions':[1254,1254]}]
 prompt='Use case: precise-object-edit. Edit this exact native 1254x1254 daylight painterly game-art crop. Keep its canvas, object layout, scale and perspective unchanged. Make only the local seam repair described here; keep every other area unchanged. '+detail+' Maintain the existing rounded Q Daoist hand-painted style and quiet pale grey natural stone. Do not crop, resize, shift, sharpen, blur, add text, UI, symbols or watermark. Return native 1254x1254.'
 pp=n/(stem+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
 req={'stem':stem,'tile':'r08_c04','patch':'repair_'+key,'route':'builtin','tool':'image_gen__imagegen','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':coords,'references':refs,'submittedParameters':{'transparent_background':False,'model':None,'quality':None,'referenced_image_paths':[src.as_posix()]},'actualModel':None,'baseAssembly':{'path':a.as_posix(),'sha256':sha(a)},'nativeCropFromCandidate':{'path':base.as_posix(),'sha256':sha(base),'box':box},'nativePixelsResampled':False}
 wr(n/(stem+'.request.json'),req);wr(Path(str(src)+'.derivation.json'),{'source':req['nativeCropFromCandidate'],'output':refs[0],'operation':'integer crop only, no resize or paint','globalContextBox':coords['globalContextBox']})
 print(stem)

