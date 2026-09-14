from pathlib import Path
from PIL import Image
import hashlib,json,sys,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'candidate-stable-body'/'24_lu_dongbin'
SRC=OUT/'source'
SRC.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p,box=None):
    p=Path(p);im=Image.open(p)
    item={'path':str(p),'sha256':sha(p),'native_size':list(im.size),'source_box':box or [0,0,*im.size]}
    for candidate in [p.with_suffix('.assembly.json'),p.with_name(p.stem.replace('-raw','')+'-assembly.json')]:
        if candidate.is_file():item['upstream']={'path':str(candidate),'sha256':sha(candidate),'data':json.loads(candidate.read_text(encoding='utf-8-sig'))}
    return item

def combine(direction,keys,evens,fix=None):
    output=Image.new('RGBA',(2508,1254),(255,0,255,255));records=[]
    for i in range(8):
        p=keys if i%2==0 else evens;im=Image.open(p).convert('RGBA');k=i//2;box=[k%2*627,k//2*627,k%2*627+627,k//2*627+627]
        assert im.size==(1254,1254),(p,im.size)
        if fix and i==5:
            p=fix;im=Image.open(p).convert('RGBA');box=[0,0,*im.size]
        cell=im.crop(box)
        if cell.size!=(627,627):cell=cell.resize((627,627),Image.Resampling.LANCZOS)
        output.paste(cell,((i%4)*627,(i//4)*627));r=info(p,box);r['output_phase']=i+1;records.append(r)
    path=SRC/f'walk-{direction}-raw.png';output.save(path)
    write(path.with_suffix('.assembly.json'),{'version':12,'operation':'whole authored cell row-major rearrangement only','output_sha256':sha(path),'output_grid':[4,2],'direction':direction,'sources':records,'synthetic_poses':False,'mirrored':False})
    return path
D=HERE/'directions'
paths={
'S':combine('S',HERE/'walk-four-keys-raw.png',HERE/'walk-four-inbetweens-raw.png'),
'N':combine('N',D/'N/keys-final-raw.png',D/'N/inbetweens-raw.png'),
'NW':combine('NW',D/'NW/keys-final-raw.png',D/'NW/inbetweens-color-raw.png'),
'SE':combine('SE',D/'SE/keys-from-E.png',D/'SE/inbetweens-from-E.png',D/'SE/fix06-arm/candidate06-cell.png'),
'E':D/'E/walk-E-refined-raw.png','W':D/'W/walk-W-raw.png','SW':D/'SW/walk-SW-raw.png','NE':D/'NE/walk-NE-canonical-raw.png'}
for kind,dirs in {'s_e':['S','E'],'n_w':['N','W'],'ne_sw':['NE','SW'],'nw_se':['NW','SE']}.items():
    subprocess.run([sys.executable,str(ROOT/'assemble_raw.py'),'--kind',kind,'--first',str(paths[dirs[0]]),'--second',str(paths[dirs[1]]),'--first-rows','2','--first-cols','4','--second-rows','2','--second-cols','4','--output',str(SRC/(kind+'-raw.png'))],check=True)
idle=Image.new('RGBA',(2508,1254),(255,0,255,255));records=[]
for i,d in enumerate(['N','NE','E','SE','S','SW','W','NW']):
    p=HERE/'idle-fixes'/d/'idle-raw.png' if d in ['S','N','E','SE'] else D/d/'idle-source-cell.png'
    im=Image.open(p).convert('RGBA'); assert im.width==im.height
    idle.paste(im.resize((627,627),Image.Resampling.LANCZOS),(i%4*627,i//4*627))
    r=info(p);r.update(direction=d,uniform_whole_cell_scale=627/im.width)
    if d not in ['S','N','E','SE']:
        r['upstream_original']=info(HERE/'idle-eight-raw.png')
    records.append(r)
p=SRC/'idle-raw.png';idle.save(p)
write(p.with_suffix('.assembly.json'),{'version':12,'operation':'whole independent authored neutral cell rearrangement; common square cell normalization','output_sha256':sha(p),'output_grid':[4,2],'sources':records,'synthetic_poses':False,'mirrored':False})
write(OUT/'candidate-source-review.json',{'status':'assembled_pending_v3_process_and_visual_review','character':'24_lu_dongbin','walk_poses':64,'idle_poses':8,'style':'young Taoist chibi; plain ivory/teal cloth; no fantasy glow','reviewed_fix06':info(D/'SE/fix06/fix06-review.json') if False else {'review':str(D/'SE/fix06/fix06-review.json'),'sha256':sha(D/'SE/fix06/fix06-review.json')},'direction_inputs':{k:info(v) for k,v in paths.items()}})
print('Candidate sources ready:',OUT)
