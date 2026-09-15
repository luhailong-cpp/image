"""Assemble one reviewed ranger direction from actual imagegen edits, never alter poses in code."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,hashlib,json
B=Path(__file__).resolve().parent
GEN=Path(r'C:\Users\luyua\.codex\generated_images\01a09f27-47ad-7342-9c26-85f9c1e456c1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parser=argparse.ArgumentParser();parser.add_argument('--direction',required=True,choices=['N','E','SE','S','SW','W']);parser.add_argument('--generated-root',type=Path,default=GEN);args=parser.parse_args();GEN=args.generated_root
d=args.direction;folder=B/d;plan=read(B/'gait-plan.json')[d];sel=read(folder/'selection-pending.json');source=read(folder/'native-source.json')
assert sorted(int(p) for p in sel)==plan['replace_source_phases']
origins={sha(p):str(p) for p in GEN.glob('*.png')}
im=Image.new('RGB',(1772,886),(255,0,255));contact=Image.new('RGB',(1024,560),(45,50,57));draw=ImageDraw.Draw(contact);frames=[]
for ph in range(1,9):
 old=folder/'original'/f'{ph:02d}.png';cell=Image.open(old).convert('RGB');rec={'direction':d,'original_source_phase':ph,'output_phase':ph,'phase_preserved':True,'upstream_cell_path':str(old),'upstream_cell_sha256':sha(old),'replacement':f'{ph:02d}' in sel,'no_bbox_fit':True,'no_mirror':True,'no_part_scaling':True}
 if rec['replacement']:
  q=sel[f'{ph:02d}'];rp=folder/q['raw'];cp=folder/q['cell'];pp=folder/q['prompt'];raw=Image.open(rp).convert('RGB');box=q['raw_box'];assert box[2]-box[0]==box[3]-box[1]
  cell=Image.open(cp).convert('RGB');expect=raw.crop(box).resize((443,443),Image.Resampling.LANCZOS);assert cell.tobytes()==expect.tobytes()
  assert sha(rp) in origins
  rec.update(source='built-in image_gen',raw_path=str(rp),raw_sha256=sha(rp),raw_size=list(raw.size),raw_source_box=box,builtin_original_path=origins[sha(rp)],builtin_original_sha256=sha(rp),cell_path=str(cp),cell_sha256=sha(cp),whole_square_to443_scale=443/(box[2]-box[0]),prompt_path=str(pp),prompt_sha256=sha(pp))
 else:rec['source']='unchanged original normalized whole-sheet443cell';assert ph in plan['protected_source_phases']
 x=(ph-1)%4*443;y=(ph-1)//4*443;box=[x,y,x+443,y+443];im.paste(cell,(x,y));rec['target_box']=box;rec['output_cell_rgba_sha256']=rgba(cell);frames.append(rec)
 cx=(ph-1)%4*256;cy=(ph-1)//4*280;contact.paste(cell.resize((256,256),Image.Resampling.LANCZOS),(cx,cy+24));draw.text((cx+8,cy+5),d+f' phase{ph:02d}'+(' EDIT' if rec['replacement'] else' kept'),fill='white')
out=folder/'final-sheet.png';im.save(out)
assert Image.open(out).size==(1772,886)
for rec in frames:
 actual=Image.open(out).convert('RGB').crop(rec['target_box']);assert rgba(actual)==rec['output_cell_rgba_sha256']
 if not rec['replacement']:assert actual.tobytes()==Image.open(rec['upstream_cell_path']).convert('RGB').tobytes()
contact.save(folder/'final-eight-review.jpg',quality=93)
assembly={'direction':d,'status':'art_candidate_pending_root_assembly_and_full_visual_review','output':str(out),'output_sha256':sha(out),'output_size':[1772,886],'output_grid':[4,2],'cell_size':[443,443],'source_phase_order':[1,2,3,4,5,6,7,8],'phase_rotation':False,'canonical_phase01':'RIGHT contact','upstream_native_source':source,'replacement_count':len(sel),'protected_original_phases':plan['protected_source_phases'],'protected_original_cells_pixel_exact':True,'bbox_fit':False,'part_scaling':False,'new_poses_generated_by_script':False,'source_art_workflow':'builtin imagegen raw; exact square crop and common whole-cell resize only; raw N/S2x4 packed row-major into final4x2 without phase rotation','frames':frames,'review':str(folder/'final-eight-review.jpg'),'sealed':False,'published':False}
write(folder/'final-sheet.assembly.json',assembly)
print(json.dumps({'direction':d,'output':str(out),'sha256':sha(out),'replacement_count':len(sel),'protected_pixel_exact':True},indent=2))

