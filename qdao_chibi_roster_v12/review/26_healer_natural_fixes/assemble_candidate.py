from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,sys,numpy as np
R=Path(r'E:\work\image\qdao_chibi_roster_v12\review\26_healer_natural_fixes');ROOT=R.parent.parent;OLD=ROOT/'26_osmanthus_healer';C=ROOT/'candidate-stable-body/26_osmanthus_healer';G=Path(r'C:\Users\luyua\.codex\generated_images\01a09f27-0628-78e0-84b5-2472601dc072');D=['N','NE','E','SE','S','SW','W','NW'];FIX={d:([4,8] if d=='S' else [2,4,6,8]) for d in D};ROTATE=['N','NE','S','SW','W','NW']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def js(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Each row describes a REAL built-in image_gen call; original raw files remain in generated_images.
CALLS=[
('E','repair-raw.png','exec-acbe4355-b4bc-42b5-84cb-7b2345f9acd4.png','repair-prompt.txt','repair-reference.png','04/08 selected; rear heels refined'),
('E','rear-refine-raw.png','exec-0f38f88b-e67b-4558-b070-f085a03d8c3a.png','rear-refine-prompt.txt','repair-raw.png','02/06 selected'),
('W','repair-raw.png','exec-14b4ea9f-8f4f-40b1-86ab-3e16c35a9280.png','repair-prompt.txt','repair-reference.png','02/04/06/08 selected'),
('N','repair-v1.png','exec-0a1a4022-d3d6-4d19-b60e-4916f2b0f539.png','repair-prompt.txt','repair-reference.png','02/06/08 selected;04 wrong arm rejected'),
('N','arm04-refine-raw.png','exec-39634ca1-06a2-462b-92a5-23580afae78f.png','arm04-refine-prompt.txt','repair-v1.png','04 selected; other cells not selected'),
('NE','repair-v1.png','exec-1a4792aa-fd7a-47e0-bba0-ff3e3b242959.png','repair-prompt.txt','repair-reference.png','02/04 selected;06 heel high;08 extra shoe rejected'),
('NE','lower-row-refine-raw.png','exec-13ec5cc6-2c52-4307-8311-85b6dd2aa786.png','lower-row-refine-prompt.txt','repair-v1.png','06/08 selected'),
('NW','repair-v1.png','exec-b1dfec4f-9903-4bed-8f5c-f370e05b0109.png','repair-prompt.txt','repair-reference.png','02/06/08 selected;04 extra hand rejected'),
('NW','hand04-refine-v1.png','exec-4f7ef1c3-2d9e-42a2-9ab7-347e630681e9.png','hand04-refine-prompt.txt','repair-v1.png','rejected: extra fingers remained'),
('NW','phase04-single-raw.png','exec-5dd6da2f-52f3-4ad4-9a38-d9e325ed8088.png','phase04-single-prompt.txt','phase04-single-reference.png','single04 selected after removing extra hand'),
('SE','repair-v1.png','exec-d7ddf500-01db-41c5-b74a-e1d59c25bcce.png','repair-prompt.txt','repair-reference.png','04/08 selected;02/06 rear heel refined'),
('SE','rear-refine-v1.png','exec-33be45e1-5858-4bbc-a47b-cd737c70bed3.png','rear-refine-prompt.txt','repair-v1.png','02 selected;06 changed to forward phase and rejected'),
('SE','phase06-single-raw.png','exec-ca82565f-a770-42e7-a64e-1e7cc1ff27a1.png','phase06-single-prompt.txt','phase06-single-reference.png','single06 selected, correct rear-release and lower knee'),
('SW','repair-raw.png','exec-9420160d-14ce-481b-b8c4-f90e31ab6911.png','repair-prompt.txt','repair-reference.png','02/04/06/08 selected'),
('S','repair-raw.png','exec-8e233f5c-0473-4669-a889-7d7f2a599cb0.png','repair-prompt.txt','repair-reference.png','04/08 selected')]
calls=[]
for d,name,g,prompt,ref,status in CALLS:
 dest=R/d/name
 if not dest.exists():shutil.copy2(G/g,dest)
 assert sha(dest)==sha(G/g)
 calls.append({'direction':d,'tool':'builtin image_gen','original_generated_path':str(G/g),'saved_raw_path':str(dest),'sha256':sha(dest),'native_size':list(Image.open(dest).size),'prompt_path':str(R/d/prompt),'prompt_sha256':sha(R/d/prompt),'reference_path':str(R/d/ref),'reference_sha256':sha(R/d/ref),'reference_mechanism':'num_last_images_to_include=1 after rendered local preview','status':status})
SELECT={
'E':{2:('rear-refine-raw.png',0),4:('repair-raw.png',1),6:('rear-refine-raw.png',2),8:('repair-raw.png',3)},
'W':{n:('repair-raw.png',i) for i,n in enumerate([2,4,6,8])},
'N':{2:('repair-v1.png',0),4:('arm04-refine-raw.png',1),6:('repair-v1.png',2),8:('repair-v1.png',3)},
'NE':{2:('repair-v1.png',0),4:('repair-v1.png',1),6:('lower-row-refine-raw.png',2),8:('lower-row-refine-raw.png',3)},
'NW':{2:('repair-v1.png',0),4:('phase04-single-raw.png',None),6:('repair-v1.png',2),8:('repair-v1.png',3)},
'SE':{2:('rear-refine-v1.png',0),4:('repair-v1.png',1),6:('phase06-single-raw.png',None),8:('repair-v1.png',3)},
'SW':{n:('repair-raw.png',i) for i,n in enumerate([2,4,6,8])},
'S':{4:('repair-raw.png',0),8:('repair-raw.png',1)}}
selected=[]
for d,items in SELECT.items():
 for phase,(name,index) in items.items():
  p=R/d/name;im=Image.open(p).convert('RGBA')
  if index is None:box=(0,0,im.width,im.height)
  elif d=='S':box=(0,index*887,887,(index+1)*887)
  else:box=(index%2*627,index//2*627,(index%2+1)*627,(index//2+1)*627)
  cell=im.crop(box);assert cell.width==cell.height;native=R/d/f'oldphase{phase:02d}-native-cell.png';cell.save(native);final=cell.resize((443,443),Image.Resampling.LANCZOS);f=R/d/f'oldphase{phase:02d}-final-cell.png';final.save(f)
  selected.append({'direction':d,'old_phase':phase,'raw_path':str(p),'raw_sha256':sha(p),'raw_crop':list(box),'native_cell_path':str(native),'native_rgba_sha256':rgba(cell),'final_cell_path':str(f),'final_rgba_sha256':rgba(final),'whole_cell_uniform_scale':443/cell.width,'body_fit':False,'visual_status':'agent reviewed, parent review pending'})
assert len(selected)==30
before={str(p.relative_to(OLD)):sha(p) for p in (OLD/'source').iterdir() if p.is_file()};before['portrait.png']=sha(OLD/'portrait.png')
C.mkdir(exist_ok=True,parents=True)
if not(C/'source').exists():shutil.copytree(OLD/'source',C/'source')
if not(C/'prompts').exists():shutil.copytree(OLD/'prompts',C/'prompts')
C.joinpath('pre-natural-source').mkdir(exist_ok=True)
records=[];cells={};phaseplan={}
for d in D:
 src=OLD/f'source/walk-{d}-final.png';shutil.copy2(src,C/f'pre-natural-source/walk-{d}-final.png');im=Image.open(src).convert('RGBA');oldcells=[im.crop((i%4*443,i//4*443,(i%4+1)*443,(i//4+1)*443)) for i in range(8)];fixed=[]
 for oldphase,old in enumerate(oldcells,1):
  changed=oldphase in FIX[d];p=R/d/f'oldphase{oldphase:02d}-final-cell.png';new=Image.open(p).convert('RGBA') if changed else old;fixed.append(new)
  if changed:shutil.copy2(p,C/f'source/natural-{d}-old{oldphase:02d}.png')
  records.append({'direction':d,'old_phase':oldphase,'new_phase':((oldphase+3)%8+1) if d in ROTATE else oldphase,'changed':changed,'original_source':str(src),'original_file_sha256':sha(src),'original_rgba_sha256':rgba(old),'candidate_rgba_sha256':rgba(new),'selected_path':str(p) if changed else str(src)})
 order=[5,6,7,8,1,2,3,4] if d in ROTATE else list(range(1,9));cells[d]=[fixed[n-1] for n in order];out=Image.new('RGBA',(1772,886))
 for i,cell in enumerate(cells[d]):out.paste(cell,(i%4*443,i//4*443))
 out.save(C/f'source/walk-{d}-final.png')
 phaseplan[d]={'original_first_contact':'anatomical_LEFT' if d in ROTATE else 'anatomical_RIGHT','candidate_first_contact':'anatomical_RIGHT','candidate_order_in_old_phases':order,'rotation_only':d in ROTATE,'source':str(src),'source_sha256':sha(src),'evidence':'Observed hip/thigh overlap and opposite arms cross-checked with original direction prompts. S original prompt explicitly used PICTURE-right=anatomicalLEFT.'}
 js(C/f'source/walk-{d}-final.assembly.json',{'operation':'whole authored cell substitution then full-cycle rotation, no mirroring/geometry interpolation','output_sha256':sha(C/f'source/walk-{d}-final.png'),'direction':d,'order_in_old_phases':order,'sources':[x for x in records if x['direction']==d]})
 board=Image.new('RGB',(886,4*443+30),'#e8e5da');dr=ImageDraw.Draw(board);dr.text((8,8),f'{d} OLD / FIXED (original phases)',fill='black')
 for row,phase in enumerate(FIX[d]):board.paste(oldcells[phase-1],(0,row*443+30));board.paste(fixed[phase-1],(443,row*443+30))
 board.crop((0,0,886,len(FIX[d])*443+30)).save(R/d/'before-after.png')
for kind,ds in {'s_e':['S','E'],'n_w':['N','W'],'ne_sw':['NE','SW'],'nw_se':['NW','SE']}.items():
 out=Image.new('RGBA',(1772,1772));frames=cells[ds[0]]+cells[ds[1]]
 for i,cell in enumerate(frames):out.paste(cell,(i%4*443,i//4*443))
 p=C/f'source/pair-{kind}.png';out.save(p);js(p.with_suffix('.assembly.json'),{'operation':'exact normalized443cell assembly after canonical RIGHT-first ordering','output_sha256':sha(p),'direction_order':ds,'sources':[{'path':str(C/f'source/walk-{d}-final.png'),'sha256':sha(C/f'source/walk-{d}-final.png')} for d in ds]})
assert sum(x['changed'] for x in records)==30;assert sum(not x['changed'] for x in records)==34
assert all(x['original_rgba_sha256']==x['candidate_rgba_sha256'] for x in records if not x['changed'])
assert sha(C/'source/idle.png')==sha(OLD/'source/idle.png')
for p,h in before.items():assert sha(OLD/p)==h,p
js(R/'generation-provenance.json',{'calls':calls,'selected_cells':selected,'number_of_builtin_calls':len(calls),'raw_art_source_only':'builtin image_gen','postprocessing':'square cropping and full-cell uniform LANCZOS to443 only; no drawn art/mirroring/frame morphing'})
js(R/'source-retention.json',{'status':'passed','unchanged_walk_cells':34,'unchanged_idle_cells':8,'total_unchanged_raw_cells':42,'changed_walk_cells':30,'portrait_png_sha256':sha(OLD/'portrait.png'),'idle_raw_file_sha256':sha(OLD/'source/idle.png'),'formal_source_unchanged':True,'baseline_files_sha256':before,'cells':records})
js(R/'phase-plan.json',{'character_id':C.name,'canonical_first_contact':'anatomical_RIGHT','rotated_directions':ROTATE,'directions':phaseplan,'note':'All repairs named by ORIGINAL phase; rotate whole cycle only after independent leg/arm checks.'})
js(C/'natural-assembly-provenance.json',{'status':'pending_visual_review','repair_plan':str(R/'repair-plan.json'),'generation_provenance':str(R/'generation-provenance.json'),'generation_provenance_sha256':sha(R/'generation-provenance.json'),'retention':str(R/'source-retention.json'),'retention_sha256':sha(R/'source-retention.json'),'phase_plan':str(R/'phase-plan.json'),'phase_plan_sha256':sha(R/'phase-plan.json')})
print(json.dumps({'selected':len(selected),'builtin_calls':len(calls),'unchanged':42,'candidate':str(C),'rotated':ROTATE},indent=2))
