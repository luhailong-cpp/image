"""Assemble actual image_gen leg edits, then rotate complete cycles to RIGHT contact first."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
B=Path(__file__).resolve().parent
ROOT=B.parents[1]
OUT=ROOT/'candidate-stable-body/30_han_xiangzi'
FORMAL=ROOT/'30_han_xiangzi'
GEN=Path(r'C:\Users\luyua\.codex\generated_images\01a09f27-47ad-7342-9c26-85f9c1e456c1')
DIRS=['N','NE','E','SE','S','SW','W','NW']
ORDER={'s_e':['S','E'],'n_w':['N','W'],'ne_sw':['NE','SW'],'nw_se':['NW','SE'],'idle':DIRS}
PHASES=[5,6,7,8,1,2,3,4]
HEADS=[('N',1),('NE',1),('SE',1),('SE',3),('W',1),('NW',1)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
assert OUT.resolve().is_relative_to((ROOT/'candidate-stable-body').resolve()) and OUT.name=='30_han_xiangzi'
sources=read(B/'baseline/sources.json')
source_dir=OUT/'source';source_dir.mkdir(parents=True,exist_ok=True)
saved_assemblies=B/'baseline/assemblies';saved_assemblies.mkdir(exist_ok=True)
for kind in ORDER:
 p=source_dir/(kind+'.assembly.json')
 if p.exists() and not (saved_assemblies/p.name).exists():shutil.copy2(p,saved_assemblies/p.name)
p=source_dir/'assembly-summary.json'
if p.exists() and not (saved_assemblies/p.name).exists():shutil.copy2(p,saved_assemblies/p.name)
origin_by_hash={sha(p):str(p) for p in GEN.glob('*.png')}
selection={d:read(B/'directions'/d/'selection-pending.json') for d in DIRS}
generation_records=[]
for d in DIRS:
 folder=B/'directions'/d
 for raw in sorted(folder.glob('*raw.png')):
  raw_sha=sha(raw);selected=[p for p,s in selection[d].items() if s['raw']==raw.name]
  prompts=sorted({selection[d][p]['prompt'] for p in selected})
  if not prompts:
   if raw.name.startswith('attempt02') and d=='W':prompts=['prompt-four-refine.txt']
   elif raw.name.startswith('attempt02') and d=='E':prompts=['prompt-revision02.txt']
   elif raw.name[:2].isdigit():prompts=['prompt-'+raw.name[:2]+'-single.txt']
   else:prompts=['prompt.txt']
  prompt_records=[{'path':str(folder/p),'sha256':sha(folder/p)} for p in prompts if (folder/p).exists()]
  assert raw_sha in origin_by_hash,raw
  generation_records.append({'direction':d,'raw_path':str(raw),'raw_sha256':raw_sha,'raw_size':list(Image.open(raw).size),'builtin_imagegen_original':origin_by_hash[raw_sha],'builtin_original_sha256':raw_sha,'prompts':prompt_records,'selected_source_phases':[int(p) for p in selected],'status':'selected_in_part_or_whole' if selected else'rejected_or_superseded_not_assembled','only_postprocessing':'exact square cell crop and one whole-cell LANCZOS resize to443; no bbox fit, body part scaling, deformation, mirroring or procedural new pose'})
write(B/'generation-provenance.json',generation_records)
summary={'character':'30_han_xiangzi','status':'candidate_pending_root_visual_review','approved_for_publication':False,'leg_edits':[],'unchanged_original_cells':0,'canonical_contact':'anatomical RIGHT contact first','cycle_source_phase_order':PHASES,'canonical_phase_mapping':{str(i+1):v for i,v in enumerate(PHASES)},'rotation_evidence':str(B/'review/contacts-01-05-before-rotation.jpg'),'rotation_rationale':'Each direction visually checked by hip-knee-shoe connection AND opposite arm swing: original01 LEFT contact, original05 RIGHT contact. Whole cycle rotation only, not based on shoe Y.','original_six_head_repairs_preserved':[],'common_scale_cli_string':'1.024390243902439','component_padding':0,'additional_edge_despill':False,'portrait_path':str(FORMAL/'portrait.png'),'portrait_sha256':sha(FORMAL/'portrait.png'),'sheets':{}}
for item in sources:
 kind=item['kind'];src=Path(item['immutable_baseline']);assert sha(src)==item['sha256']
 original=Image.open(src).convert('RGB');work=original.copy();dest=source_dir/(kind+'.png')
 oldassembly=saved_assemblies/(kind+'.assembly.json')
 cols,rows=(4,2) if kind=='idle' else(4,4)
 asm={'version':12,'output_path':str(dest),'output_size':list(original.size),'output_grid':[cols,rows],'native_cell_size':[443,443],'direction_order':ORDER[kind],'output_phase_order':'canonical RIGHT contact first','source_phase_order_per_direction':PHASES if kind!='idle' else None,'phase_order_changed':kind!='idle','phase_order_change':'whole cycle rotate05..08,01..04; no individual pose reassignment' if kind!='idle' else None,'body_bbox_fit':False,'part_scaling':False,'mirrored_frames':False,'new_poses_generated_by_script':False,'upstream_source_path':str(src),'upstream_source_sha256':sha(src),'upstream_assembly_path':str(oldassembly),'upstream_assembly_sha256':sha(oldassembly),'generation_provenance_path':str(B/'generation-provenance.json'),'generation_provenance_sha256':sha(B/'generation-provenance.json'),'sources':[]}
 for out_index in range(cols*rows):
  d=ORDER[kind][out_index] if kind=='idle' else ORDER[kind][out_index//8]
  output_phase=0 if kind=='idle' else out_index%8+1
  source_phase=0 if kind=='idle' else PHASES[output_phase-1]
  src_index=out_index if kind=='idle' else (out_index//8)*8+source_phase-1
  srcbox=[src_index%4*443,src_index//4*443,(src_index%4+1)*443,(src_index//4+1)*443]
  dstbox=[out_index%4*443,out_index//4*443,(out_index%4+1)*443,(out_index//4+1)*443]
  cell=original.crop(srcbox);old_cell_hash=rgba(cell)
  selected=selection[d].get(f'{source_phase:02d}') if kind!='idle' else None
  rec={'direction':d,'action':'idle' if kind=='idle' else'walk','phase':output_phase,'original_source_phase':source_phase,'target_grid_row_col':[out_index//4,out_index%4],'target_box_xyxy':dstbox,'upstream_source_path':str(src),'upstream_source_sha256':sha(src),'upstream_source_box_xyxy':srcbox,'upstream_cell_rgba_sha256':old_cell_hash,'authored_anatomical_phase_preserved':True,'output_cycle_rotation_only':kind!='idle','replacement':bool(selected)}
  if selected:
   folder=B/'directions'/d;cp=folder/selected['cell'];rp=folder/selected['raw'];pp=folder/selected['prompt']
   raw=Image.open(rp).convert('RGB');box=selected['source_box'];assert box[2]-box[0]==box[3]-box[1]
   expected=raw.crop(box).resize((443,443),Image.Resampling.LANCZOS);cell=Image.open(cp).convert('RGB');assert expected.tobytes()==cell.tobytes(),cp
   rec.update(source='built-in image_gen leg edit',source_path=str(cp),source_sha256=sha(cp),raw_source_path=str(rp),raw_source_sha256=sha(rp),raw_size=list(raw.size),raw_source_box_xyxy=box,whole_raw_square_scale_to_cell=443/(box[2]-box[0]),builtin_imagegen_original=origin_by_hash[sha(rp)],prompt_path=str(pp),prompt_sha256=sha(pp))
   summary['leg_edits'].append({'direction':d,'original_source_phase':source_phase,'canonical_output_phase':output_phase,'sheet':kind,'source_path':str(cp),'sha256':sha(cp)})
  else:
   rec['source']='pixel-exact original baseline cell, possibly whole-cycle rotated';summary['unchanged_original_cells']+=1
  if(d,source_phase) in HEADS:
   assert not selected
   head=ROOT/'review/han_xiangzi_proportion_fixes'/f'{d}-{source_phase:02d}'/'final-cell.png'
   assert cell.tobytes()==Image.open(head).convert('RGB').tobytes()
   summary['original_six_head_repairs_preserved'].append({'direction':d,'original_phase':source_phase,'output_phase':output_phase,'head_repair_source':str(head),'sha256':sha(head),'pixel_exact':True})
  work.paste(cell,(dstbox[0],dstbox[1]));rec['output_cell_rgba_sha256']=rgba(cell);asm['sources'].append(rec)
 if kind=='idle':assert work.tobytes()==original.tobytes();shutil.copyfile(src,dest)
 else:work.save(dest)
 actual=Image.open(dest).convert('RGB')
 for rec in asm['sources']:assert rgba(actual.crop(rec['target_box_xyxy']))==rec['output_cell_rgba_sha256']
 if actual.width>443*cols:assert actual.crop((443*cols,0,actual.width,actual.height)).tobytes()==original.crop((443*cols,0,actual.width,actual.height)).tobytes()
 if actual.height>443*rows:assert actual.crop((0,443*rows,actual.width,actual.height)).tobytes()==original.crop((0,443*rows,actual.width,actual.height)).tobytes()
 asm['output_sha256']=sha(dest);write(dest.with_suffix('.assembly.json'),asm)
 summary['sheets'][kind]={'output':str(dest),'output_sha256':sha(dest),'assembly_sha256':sha(dest.with_suffix('.assembly.json')),'unselected_source_cells_pixel_equal_after_rotation':True}
assert len(summary['leg_edits'])==32 and summary['unchanged_original_cells']==40
assert len(summary['original_six_head_repairs_preserved'])==6
write(source_dir/'assembly-summary.json',summary);write(B/'candidate-assembly-evidence.json',summary)
print(json.dumps({'leg_edits':len(summary['leg_edits']),'unchanged_original_cells':summary['unchanged_original_cells'],'six_head_repairs_pixel_exact':len(summary['original_six_head_repairs_preserved']),'canonical_source_order':PHASES,'portrait_unchanged_source':sha(FORMAL/'portrait.png'),'status':summary['status']},indent=2))


