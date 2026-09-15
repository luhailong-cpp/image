from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,sys,argparse
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
OUT=ROOT/'candidate-natural-body'/'29_he_xiangu';SRC=OUT/'source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');parser.add_argument('--process',action='store_true');parser.add_argument('--idle-only',action='store_true');args=parser.parse_args()
plans={
'S':{'keys':'keys-raw.png','evens':'inbetweens-arm-fixed-raw.png'},
'E':{'sheet':'walk-final-raw.png'},
'SE':{'keys':'keys-raw.png','evens':'inbetweens-raw.png','fix04':True},
'N':{'keys':'keys-final-raw.png','evens':'inbetweens-original-raw.png','even_order':[0,3,2,1]},
'W':{'keys':'keys-final-raw.png','evens':'inbetweens-final-raw.png'},
'SW':{'keys':'keys-final-raw.png','evens':'inbetweens-refined-raw.png','fix04':True},
'NE':{'keys':'keys-final-raw.png','evens':'inbetweens-final-raw.png'},
'NW':{'keys':'keys-final-raw.png','evens':'inbetweens-final-raw.png'}}
def cell(src,cols,rows,index):
 im=Image.open(src).convert('RGBA');native=list(im.size)
 norm=im.resize((cols*627,rows*627),Image.Resampling.LANCZOS) if im.size!=(cols*627,rows*627) else im
 box=[index%cols*627,index//cols*627,index%cols*627+627,index//cols*627+627]
 info={'path':str(src),'sha256':sha(src),'native_size':native,'native_grid':[cols,rows],'native_grid_index':index+1,'normalized_sheet_size':list(norm.size),'normalized_cell_box':box,'operation':'whole uniform sheet resolution normalization and exact complete-cell extraction; no body bbox scaling or pose warp'}
 a=src.with_suffix('.assembly.json')
 if a.exists():info['upstream_assembly']={'path':str(a),'sha256':sha(a),'data':json.loads(a.read_text(encoding='utf-8-sig'))}
 return norm.crop(box),info
paths={};allrecords={};missing=[]
for d,plan in plans.items():
 if args.idle_only:
  dest=SRC/f'walk-{d}-raw.png';data=json.loads(dest.with_suffix('.assembly.json').read_text());assert sha(dest)==data['output_sha256'];paths[d]=dest;allrecords[d]=data['sources'];continue
 required=[P/'directions'/d/name for k,name in plan.items() if k in ('keys','evens','sheet')]
 if any(not p.exists() for p in required):missing.append(d);continue
 im=Image.new('RGBA',(2508,1254),(255,0,255,255));records=[]
 for i in range(8):
  if plan.get('fix04') and i==3:
   p=P/'precontact-fixes/precontact-final-raw.png';pose,record=cell(p,2,1,['SE','SW'].index(d))
  elif 'sheet' in plan:pose,record=cell(P/'directions'/d/plan['sheet'],4,2,i)
  else:
   k=i//2
   if i%2:k=plan.get('even_order',[0,1,2,3])[k]
   p=P/'directions'/d/plan['evens' if i%2 else 'keys'];pose,record=cell(p,2,2,k)
  im.paste(pose,(i%4*627,i//4*627));record.update(direction=d,output_phase=i+1);records.append(record)
 dest=SRC/f'walk-{d}-raw.png';dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)
 write(dest.with_suffix('.assembly.json'),{'direction':d,'output_grid':[4,2],'output_sha256':sha(dest),'sources':records,'synthetic_poses':False,'mirrored':False,'interpolated':False})
 paths[d]=dest;allrecords[d]=records
write(OUT/'candidate-source-review.json',{'status':'art_sources_assembled_pending_full_visual_verification','character':'29_he_xiangu','style':'plain sage ivory Taoist cloth robes, long trousers and ivory flats; young low bun He Xiangu, no fantasy effects','phase_contract':['RIGHT contact','RIGHT support LEFT release','RIGHT support LEFT low pass','LEFT precontact','LEFT contact','LEFT support RIGHT release','LEFT support RIGHT low pass','RIGHT precontact'],'directions_available':list(paths),'directions_missing':missing,'source_cells':allrecords,'independent_idle_original':{'path':str(P/'idle-eight-raw.png'),'sha256':sha(P/'idle-eight-raw.png')}})
if missing:
 print('Prepared directions:',','.join(paths),'Missing:',','.join(missing))
 if not args.partial:raise SystemExit(2)
 raise SystemExit(0)
for kind,dirs in {'s_e':['S','E'],'n_w':['N','W'],'ne_sw':['NE','SW'],'nw_se':['NW','SE']}.items():
 if args.idle_only:continue
 subprocess.run([sys.executable,str(ROOT/'assemble_raw.py'),'--kind',kind,'--first',str(paths[dirs[0]]),'--second',str(paths[dirs[1]]),'--first-rows','2','--first-cols','4','--second-rows','2','--second-cols','4','--output',str(SRC/(kind+'-raw.png'))],check=True)
idle=Image.new('RGBA',(2508,1254),(255,0,255,255));records=[]
overrides=json.loads((P/'idle-overrides.json').read_text()) if (P/'idle-overrides.json').exists() else {}
for i,d in enumerate(['N','NE','E','SE','S','SW','W','NW']):
 if d in overrides:
  o=overrides[d];p=Path(o['path']);pose,record=cell(p,o['cols'],o['rows'],o['index']);record['revision']='independently redrawn neutral idle matched to same-direction walk03 head size'
 else:
  p=P/'directions'/d/'idle-source-cell.png';pose,record=cell(p,1,1,0)
 idle.paste(pose,(i%4*627,i//4*627));record.update(direction=d);records.append(record)
dest=SRC/'idle-raw.png';idle.save(dest);write(dest.with_suffix('.assembly.json'),{'output_sha256':sha(dest),'output_grid':[4,2],'sources':records,'upstream_idle_extraction':json.loads((P/'idle-source-extraction.json').read_text()),'synthetic_poses':False,'mirrored':False})
if args.process:
 cmd=[sys.executable,'-X','utf8',str(ROOT/'process_roster.py'),'--character-dir',str(OUT),'--alignment-version','3','--common-scale','1.0','--portrait-raw',str(P/'master-raw.png'),'--despill-magenta-edge','--despill-radius','4']
 for kind in ['s_e','n_w','ne_sw','nw_se','idle']:cmd+=['--'+kind.replace('_','-'),str(SRC/(kind+'-raw.png'))]
 print('Processing complete source set',flush=True);subprocess.run(cmd,check=True)
print('Assembled 64 authored walk and8 independent idle source cells.')

