from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parent.parent;OLD=ROOT/'23_lantern_courier';C=ROOT/'candidate-stable-body/23_lantern_courier';D=['N','NE','E','SE','S','SW','W','NW']
FIX={'N':[1,5,6,7,8],'W':[1,2,4,8],'SW':[3,4,7,8],'E':[4,8],'SE':[4,8],'S':[4,8]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def js(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C.mkdir(exist_ok=True,parents=True)
if not (C/'source').exists():shutil.copytree(OLD/'source',C/'source')
if not (C/'prompts').exists():shutil.copytree(OLD/'prompts',C/'prompts')
# Candidate corrections are relative to FINAL formal raw sheets, which already include all old fixes.
# Original historic raw inputs are retained separately in the original source, never overwritten there.
shutil.copy2(OLD/'assemble_corrections.py',C/'assemble_corrections.py')
records=[];cells={};corrections={};before={str(p.relative_to(OLD)):sha(p) for p in (OLD/'source').glob('*') if p.is_file()};before['portrait.png']=sha(OLD/'portrait.png')
for d in D:
 src=OLD/f'source/walk-{d}.png';baseline=C/f'source/walk-{d}-original.png';shutil.copy2(src,baseline);im=Image.open(src).convert('RGBA');cols=2 if d in ['N','S'] else 4;out=im.copy();cells[d]=[]
 for i in range(8):
  box=[i%cols*443,i//cols*443,(i%cols+1)*443,(i//cols+1)*443];old=im.crop(box);changed=i+1 in FIX.get(d,[]);p=R/d/f'phase{i+1:02d}-final-cell.png';cell=Image.open(p).convert('RGBA') if changed else old;assert cell.size==(443,443);out.paste(cell,box[:2]);cells[d].append(cell)
  if changed:
   selected=C/f'source/natural-{d}-{i+1:02d}.png';shutil.copy2(p,selected);corrections.setdefault(d,{})[str(i+1)]={'file':selected.name}
  records.append({'direction':d,'phase':i+1,'changed':changed,'original_source':str(src),'original_sha256':sha(src),'source_box':box,'original_rgba_sha256':rgba(old),'selected_source':str(p) if changed else str(src),'selected_rgba_sha256':rgba(cell)})
 target=C/f'source/walk-{d}.png';out.save(target);js(target.with_suffix('.assembly.json'),{'version':12,'operation':'19 authored corrections inserted into final formal raw baseline; unchanged cell RGBA preserved','output_path':str(target),'output_sha256':sha(target),'baseline_source':str(src),'baseline_sha256':sha(src),'candidate_rebuild_baseline':str(baseline),'corrections_file':str(C/'corrections.json'),'cells':[q for q in records if q['direction']==d]})
js(C/'corrections.json',corrections)
for kind,ds in {'s_e':['S','E'],'n_w':['N','W'],'ne_sw':['NE','SW'],'nw_se':['NW','SE']}.items():
 out=Image.new('RGBA',(1772,1772));frames=cells[ds[0]]+cells[ds[1]]
 for i,cell in enumerate(frames):out.paste(cell,(i%4*443,i//4*443))
 p=C/f'source/{kind}.png';out.save(p);js(p.with_suffix('.assembly.json'),{'version':12,'operation':'exact 443-square row-major assembly, no per-frame body fitting','output_path':str(p),'output_sha256':sha(p),'direction_order':ds,'canonical_first_contact':'anatomical_RIGHT','sources':[{'path':str(C/f'source/walk-{d}.png'),'sha256':sha(C/f'source/walk-{d}.png')} for d in ds]})
assert sum(x['changed'] for x in records)==19
assert all(x['original_rgba_sha256']==x['selected_rgba_sha256'] for x in records if not x['changed'])
assert sha(C/'source/idle.png')==sha(OLD/'source/idle.png')
for p,h in before.items():assert sha(OLD/p)==h,p
js(R/'source-retention.json',{'status':'passed','unchanged_walk_cells':45,'unchanged_idle_cells':8,'total_unchanged_raw_cells':53,'changed_walk_cells':19,'portrait_png_sha256':sha(OLD/'portrait.png'),'idle_raw_file_sha256':sha(OLD/'source/idle.png'),'formal_source_unchanged':True,'baseline_files_sha256':before,'cells':records})
reasons={'N':'01 anatomical RIGHT/viewer-right foot leads away while right empty arm swings back; 05 opposite left contact. Hip and pant overlap agree with original prompt.','NE':'01 near right thigh leads with empty right hand back; 05 reverses right arm swing and pant overlap. Rear-facing shoe screen-side not used alone.','E':'01 near right thigh leads, near right empty arm back; 05 far left leads with near right arm forward.','SE':'01 near right thigh leads and right empty arm back; 05 far left leads and right arm forward.','S':'01 viewer-left/anatomical right leg leads and empty right arm back; 05 viewer-right left leg leads and empty right arm forward.','SW':'01 far right thigh leads and empty right hand back; 05 near left contact with opposite right-arm swing.','W':'01 far right thigh leads while near left lantern hand advances; 05 near left leads with right empty arm advancing.','NW':'01 far right thigh leads and visible far right empty hand back; 05 near left leads with right hand forward/occluded. Hip overlap and arm agree.'}
js(R/'phase-plan.json',{'character_id':C.name,'canonical_first_contact':'anatomical_RIGHT','rotation_applied':False,'order':[1,2,3,4,5,6,7,8],'directions':{d:{'first_contact':'anatomical_RIGHT','evidence':reasons[d],'source':str(OLD/f'source/walk-{d}.png'),'source_sha256':sha(OLD/f'source/walk-{d}.png')} for d in D},'note':'Existing 23 is canonical RIGHT-first; no unnecessary rotation or mirrored pixels.'})
def metric(im):
 a=np.array(im.convert('RGB')).astype(int);m=~((a[:,:,0]>150)&(a[:,:,2]>140)&(a[:,:,1]<120)&(a[:,:,0]+a[:,:,2]-2*a[:,:,1]>180));yy,xx=np.nonzero(m);x=xx[yy<yy.min()+100];return {'top':int(yy.min()),'head_upper100_width':int(x.max()-x.min()+1),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]}
ms=[]
for d in D:
 board=Image.new('RGB',(1772,914),'#26383a');dr=ImageDraw.Draw(board)
 for i in range(8):
  old=Image.open(R/d/f'original-{i+1:02d}-cell.png').convert('RGBA');new=cells[d][i];ms.append({'direction':d,'phase':i+1,'original':metric(old),'new':metric(new),'changed':i+1 in FIX.get(d,[])})
  board.paste(new,(i%4*443,28+i//4*443));dr.text((i%4*443+5,i//4*443+32),f'{d}{i+1:02d}'+(' NEW' if i+1 in FIX.get(d,[]) else ' KEPT'),fill='white')
 board.save(R/d/'candidate-all-eight-raw.png')
 for section,phases in [('low',[4,8]),('head',[x for x in FIX.get(d,[]) if x not in [4,8]])]:
  if not phases or (section=='low' and d not in ['E','SE','S','SW','W']):continue
  comp=Image.new('RGB',(886,len(phases)*443+28),'#26383a');dw=ImageDraw.Draw(comp);dw.text((8,8),f'{d} OLD / CANDIDATE',fill='white')
  for row,n in enumerate(phases):comp.paste(Image.open(R/d/f'original-{n:02d}-cell.png'),(0,28+row*443));comp.paste(cells[d][n-1],(443,28+row*443))
  comp.save(R/d/f'{section}-before-after.png')
js(R/'raw-head-metrics.json',ms)
print(json.dumps({'candidate':str(C),'changed':19,'unchanged':53,'right_first_all_directions':True,'head_widths_N':[x['new']['head_upper100_width'] for x in ms if x['direction']=='N']},indent=2))
