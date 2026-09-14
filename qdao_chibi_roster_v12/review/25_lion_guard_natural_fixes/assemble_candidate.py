from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,numpy as np
R=Path(__file__).resolve().parent; ROOT=R.parent.parent; OLD=ROOT/'25_lion_drum_guard'; CAND=ROOT/'candidate-stable-body/25_lion_drum_guard'
DIRS=['N','NE','E','SE','S','SW','W','NW']; CHANGED=['E','SE','S','SW','W']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def savej(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
CAND.mkdir(parents=True,exist_ok=True)
if not (CAND/'source').exists():shutil.copytree(OLD/'source',CAND/'source')
if not (CAND/'prompts').exists() and (OLD/'prompts').exists():shutil.copytree(OLD/'prompts',CAND/'prompts')
# This is source-grid composition only. Unchanged raw cells must have identical RGBA bytes.
records=[]; allcells={}; before={str(p.relative_to(OLD)):sha(p) for p in (OLD/'source').glob('*') if p.is_file()}; before['portrait.png']=sha(OLD/'portrait.png')
for d in DIRS:
 p=OLD/f'source/walk-{d}-final.png'; im=Image.open(p).convert('RGBA'); cells=[]
 for i in range(8):
  box=[i%2*443,i//2*443,(i%2+1)*443,(i//2+1)*443]; old=im.crop(box); cell=old
  replacement=R/d/f'phase{i+1:02d}-final-cell.png'; changed=d in CHANGED and i in [3,7]
  if changed:cell=Image.open(replacement).convert('RGBA');assert cell.size==(443,443)
  elif rgba(cell)!=rgba(old):raise ValueError('unchanged pixels altered')
  records.append({'kind':'walk','direction':d,'phase':i+1,'original_source':str(p),'original_file_sha256':sha(p),'source_box':box,'original_cell_rgba_sha256':rgba(old),'changed':changed,'selected_source':str(replacement) if changed else str(p),'selected_cell_rgba_sha256':rgba(cell)})
  cells.append(cell)
 out=Image.new('RGBA',(886,1772));
 for i,cell in enumerate(cells):out.paste(cell,(i%2*443,i//2*443))
 target=CAND/f'source/walk-{d}-final.png';out.save(target);savej(target.with_suffix('.assembly.json'),{'version':12,'operation':'exact 443-square cell replacement only; no mirror, warp or per-frame fit','output_path':str(target),'output_sha256':sha(target),'cells':[x for x in records if x['direction']==d]})
 allcells[d]=cells
for name,ds in [('s-e',['S','E']),('n-w',['N','W']),('ne-sw',['NE','SW']),('nw-se',['NW','SE'])]:
 out=Image.new('RGBA',(1772,1772));cells=allcells[ds[0]]+allcells[ds[1]]
 for i,cell in enumerate(cells):out.paste(cell,(i%4*443,i//4*443))
 target=CAND/f'source/paired-{name}.png';out.save(target);savej(target.with_suffix('.assembly.json'),{'version':12,'operation':'row-major rearrangement of exact 443-square candidate directional cells','output_path':str(target),'output_sha256':sha(target),'output_grid':[4,4],'direction_order':ds,'sources':[{'path':str(CAND/f'source/walk-{d}-final.png'),'sha256':sha(CAND/f'source/walk-{d}-final.png')} for d in ds]})
p=OLD/'source/idle.png';im=Image.open(p).convert('RGBA');out=im.copy();idlemeta=json.loads((OLD/'processing/idle/pipeline-meta.json').read_text());idlecells=[]
for i,d in enumerate(DIRS):
 box=idlemeta['frames'][i]['source_box'];old=im.crop(box);changed=d in ['NE','NW','W'];replace=R/f'idle-{d}/final-cell.png';cell=Image.open(replace).convert('RGBA') if changed else old
 assert cell.size==old.size==(443,443)
 out.paste(cell,box[:2]);idlecells.append(cell);records.append({'kind':'idle','direction':d,'original_source':str(p),'original_file_sha256':sha(p),'source_box':box,'original_cell_rgba_sha256':rgba(old),'changed':changed,'selected_source':str(replace) if changed else str(p),'selected_cell_rgba_sha256':rgba(cell)})
target=CAND/'source/idle.png';out.save(target);savej(target.with_suffix('.assembly.json'),{'version':12,'operation':'3 exact cell replacements; other 5 cells and original outer remainder copied','output_path':str(target),'output_sha256':sha(target),'cells':[x for x in records if x['kind']=='idle']})
assert all(x['original_cell_rgba_sha256']==x['selected_cell_rgba_sha256'] for x in records if not x['changed'])
assert len([x for x in records if not x['changed']])==59
for rel,digest in before.items():assert sha(OLD/rel)==digest,rel
savej(R/'source-retention.json',{'status':'passed','unchanged_raw_cells':59,'repainted_walk_cells':10,'repainted_idle_cells':3,'original_files_unchanged':True,'portrait_png_sha256':sha(OLD/'portrait.png'),'baseline_files_sha256':before,'cells':records})
# Raw-cell QA evidence with equal whole-cell scale; no subject-based fitting.
def metrics(im):
 a=np.asarray(im.convert('RGB')).astype(int); bg=(a[:,:,0]>150)&(a[:,:,2]>140)&(a[:,:,1]<120)&((a[:,:,0]+a[:,:,2]-2*a[:,:,1])>180); m=~bg; yy,xx=np.nonzero(m); top=int(yy.min()); xs=xx[yy<top+100]
 return {'top':top,'head_upper100_width':int(xs.max()-xs.min()+1),'bbox':[int(xx.min()),top,int(xx.max()+1),int(yy.max()+1)]}
ms=[]
for d in CHANGED:
 sheet=Image.new('RGB',(443*4,443*2+28),'#202a2b');dr=ImageDraw.Draw(sheet)
 for col,i in enumerate([2,3,6,7]):
  old=Image.open(OLD/f'source/walk-{d}-final.png').crop((i%2*443,i//2*443,(i%2+1)*443,(i//2+1)*443));new=allcells[d][i];sheet.paste(old,(col*443,28));sheet.paste(new,(col*443,471));dr.text((col*443+8,8),f'{d}{i+1:02d} ORIGINAL / CANDIDATE',fill='white');ms.append({'direction':d,'phase':i+1,'original':metrics(old),'candidate':metrics(new)})
 sheet.save(R/d/'before-after-03-04-07-08.png')
idleview=Image.new('RGB',(443*3,443*3+28),'#202a2b');dr=ImageDraw.Draw(idleview)
for col,d in enumerate(['NE','NW','W']):
 old=Image.open(R/f'idle-{d}/original-idle-cell.png');new=idlecells[DIRS.index(d)];walk=allcells[d][0]
 for row,cell in enumerate([old,new,walk]):idleview.paste(cell,(col*443,28+row*443))
 dr.text((col*443+8,8),f'{d} OLD IDLE / NEW IDLE / WALK01',fill='white');ms.append({'direction':d,'kind':'idle','original':metrics(old),'candidate':metrics(new),'walk01':metrics(walk)})
idleview.save(R/'idle-before-after-walk.png');savej(R/'raw-head-metrics.json',ms)
print(json.dumps({'candidate':str(CAND),'unchanged_cells':59,'changed_cells':13,'head_metrics':ms},indent=2))
