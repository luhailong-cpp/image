"""Finish two genuinely authored south precontacts; preserve every other source cell."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
B=Path(r'E:\work\image\qdao_chibi_roster_v12\review\27_ranger_natural_fixes\six-direction-gait');p=B/'S'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(i):return hashlib.sha256(i.convert('RGBA').tobytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=p/'low-precontact-raw.png';native=Image.open(raw).convert('RGBA');assert native.size==(1254,1254)
original=Path(r'C:\Users\luyua\.codex\generated_images\01a0ad26-598c-71d1-a642-318f1486ea5c\exec-4df6dcb5-75b0-481f-92a1-32f7d3e25583.png');assert sha(original)==sha(raw)
chosen={4:2,8:3};out=Image.new('RGBA',(1772,886),(255,0,255,255));records=[]
for ph in range(1,9):
 old=p/'original'/f'{ph:02d}.png';cell=Image.open(old).convert('RGBA');rec={'output_phase':ph,'original_source_phase':ph,'replacement':ph in chosen,'upstream_cell_path':str(old),'upstream_cell_sha256':sha(old),'phase_preserved':True,'no_mirror':True,'no_bbox_fit':True,'no_part_scaling':True}
 if ph in chosen:
  j=chosen[ph];box=[j%2*627,j//2*627,j%2*627+627,j//2*627+627];piece=native.crop(box);a=np.asarray(piece)[:,:,3];ys,xs=np.where(a>20)
  assert xs.min()>0 and ys.min()>0 and xs.max()<626 and ys.max()<626
  cell=piece.resize((443,443),Image.Resampling.LANCZOS);original_rgba=np.array(cell);clean_rgba=original_rgba.copy();noise=(clean_rgba[:,:,3]>0)&(clean_rgba[:,:,3]<=3);clean_rgba[:,:,3][noise]=0;assert np.array_equal(clean_rgba[:,:,:3],original_rgba[:,:,:3]);assert np.array_equal(clean_rgba[original_rgba[:,:,3]>3],original_rgba[original_rgba[:,:,3]>3]);cell=Image.fromarray(clean_rgba);cp=p/f'{ph:02d}-low-precontact-cell.png';cell.save(cp);rec.update(alpha_noise_cleanup={'maximum_removed_alpha':3,'pixels_cleared':int(noise.sum()),'rgb_unchanged':True,'alpha_gt3_unchanged':True,'reason':'faint generated background alpha 1-3 linked to sheet edges; all actual subject alpha>8 is inset >=2px'})
  rec.update(source='built-in image_gen',raw_path=str(raw),raw_sha256=sha(raw),raw_size=list(native.size),raw_source_box=box,builtin_original_path=str(original),builtin_original_sha256=sha(original),native_alpha_gt3_preserved=True,cell_path=str(cp),cell_sha256=sha(cp),whole_square_to443_scale=443/627,prompt_path=str(p/'prompt-low-precontact.txt'),prompt_sha256=sha(p/'prompt-low-precontact.txt'),robust_alpha_gt20_bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],transparent_noise_max_alpha_at_top=int(a[0].max()))
 else:rec['source']='unchanged original normalized whole-sheet443cell'
 xy=((ph-1)%4*443,(ph-1)//4*443);out.paste(cell,xy);rec['target_box']=[*xy,xy[0]+443,xy[1]+443];rec['output_cell_rgba_sha256']=rgba(cell);records.append(rec)
f=p/'final-sheet.png';out.save(f)
for rec in records:
 c=Image.open(f).convert('RGBA').crop(rec['target_box']);assert rgba(c)==rec['output_cell_rgba_sha256']
 if not rec['replacement']:assert rgba(c)==rgba(Image.open(rec['upstream_cell_path']))
board=Image.new('RGB',(1024,560),'#30343b');draw=ImageDraw.Draw(board)
for i,rec in enumerate(records):
 c=out.crop(rec['target_box']);bg=Image.new('RGBA',c.size,(255,0,255,255));bg.alpha_composite(c);board.paste(bg.convert('RGB').resize((256,256)),(i%4*256,i//4*280+24));draw.text((i%4*256+5,i//4*280+5),f'S {i+1:02d} '+('EDIT' if rec['replacement'] else 'kept'),fill='white')
board.save(p/'final-eight-review.jpg',quality=92)
write(p/'final-sheet.assembly.json',{'direction':'S','status':'pending_root_visual_review','output':str(f),'output_sha256':sha(f),'output_size':[1772,886],'output_grid':[4,2],'cell_size':[443,443],'source_phase_order':list(range(1,9)),'phase_rotation':False,'canonical_phase01':'RIGHT contact','replacement_count':2,'protected_original_phases':[1,2,3,5,6,7],'protected_original_cells_pixel_exact':True,'native_generated_alpha_gt3_preserved':True,'no_pose_pixels_painted_by_script':True,'frames':records,'sealed':False,'published':False})
print(json.dumps({'output':str(f),'sha256':sha(f),'selected_native_cells':[3,4],'protected_cells':6}))
