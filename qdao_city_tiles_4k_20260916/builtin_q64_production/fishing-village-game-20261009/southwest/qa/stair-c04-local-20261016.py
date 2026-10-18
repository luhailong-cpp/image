import sys,json,hashlib,importlib.util
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
sys.dont_write_bytecode=True
Z=Path(__file__).resolve().parent.parent;R=Z.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
sp=importlib.util.spec_from_file_location('stair_local',Z/'production.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
write=p.write;p.write=lambda path,obj:None if path.name=='progress.json' else write(path,obj)
if sys.argv[1]=='record':p.record(sys.argv[2]);sys.exit()
patch,version=sys.argv[2:4];stem='r11_c04_'+patch+'_'+version;rp=Z/'native'/(stem+'.request.json')
assert not rp.exists(),rp
split=read(R/'docs/MAP_PARALLEL_SPLIT_20261013.json');assert not any('r11_c04' in b['tiles'] for b in split['batches'] if b.get('status')=='allocated_root_reserved')
p.prepare('r11_c04',patch,version)
r=read(rp);box=r['coordinates']['globalContextBox'];base=Z/'layout-only'/('r11_c04_'+patch+'.png')
if patch in ['p02_01','p02_02','p03_03']:base=Z/'native'/('r11_c04_'+patch+'_v1.png')
canvas=Image.open(base).convert('RGB');sources=[]
excluded=['r11_c04_p02_01_v1.png','r11_c04_p02_02_v1.png','r11_c04_p03_02_v1.png','r11_c04_p03_03_v1.png']
for x in r['overlaps']:
 if Path(x['path']).name in excluded:continue
 b=x['globalOverlapBox'];src=read(Path(x['path']+'.generation.json'))['coordinates']['globalContextBox']
 with Image.open(x['path']) as im:canvas.paste(im.crop((b[0]-src[0],b[1]-src[1],b[2]-src[0],b[3]-src[1])),(b[0]-box[0],b[1]-box[1]))
 sources.append(x)
anchors=[]
for tile,source in [('r10_c04','block2x2-r09r10c03c04-v1-r10_c04-context-native.png'),('r11_c03','pair-r11c02-c03-v1-r11_c03-context-native.png'),('r11_c05','block2x2-r10r11c05c06-v1-r11_c05-context-native.png')]:
 rr,cc=int(tile[1:3]),int(tile[5:7]);b=[(cc-1)*4096-115,(rr-1)*4096-115,cc*4096+115,rr*4096+115];i=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
 if i[2]<=i[0] or i[3]<=i[1]:continue
 src=Z/'qa'/source
 with Image.open(src) as im:canvas.paste(im.crop((i[0]-b[0],i[1]-b[1],i[2]-b[0],i[3]-b[1])),(i[0]-box[0],i[1]-box[1]))
 anchors.append({**ref(src),'tile':tile,'globalOverlapBox':i,'targetBox':[i[0]-box[0],i[1]-box[1],i[2]-box[0],i[3]-box[1]]})
dst=Path(r['references'][0]['path']);canvas.save(dst);r['overlaps']=sources;r['currentFinalAnchors']=anchors;r['excludedConflictingGeometrySources']=excluded;r['rulesReadBeforeRequest']=[ref(R/'AGENTS.md'),ref(R/'docs/MAP_PARALLEL_SPLIT_20261013.json')];p.write(rp,r)
p.write(Path(str(dst)+'.derivation.json'),{'file':dst.as_posix(),'sha256':sha(dst),'role':'layout only with native overlaps; not final art','operation':'integer crop and paste; no resampling native pixels','baseGuide':ref(base),'nativeSources':sources,'currentFinalAnchors':anchors})
print(json.dumps({'stem':stem,'guide':dst.as_posix(),'rules':r['rulesReadBeforeRequest']}))
