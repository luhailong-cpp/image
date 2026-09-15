from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parent
CELL=627
DIRECTION=ROOT.name

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pixels(im):return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()
def write(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
config=json.loads((ROOT/"phase-selection.json").read_text(encoding="utf8"))["phases"]
frames={};records={};upstream={}
for phase in range(1,9):
 source=config[str(phase)];path=ROOT/source["source"];im=Image.open(path).convert("RGBA")
 cw,ch=im.width//source["cols"],im.height//source["rows"];index=source["index"]
 box=(index%source["cols"]*cw,index//source["cols"]*ch,(index%source["cols"]+1)*cw,(index//source["cols"]+1)*ch)
 assert cw==ch
 cell=im.crop(box);factor=CELL/cw
 if cell.size!=(CELL,CELL):cell=cell.resize((CELL,CELL),Image.Resampling.LANCZOS)
 existing=Image.open(ROOT/f"phase{phase:02}-cell.png").convert("RGBA")
 assert existing.tobytes()==cell.tobytes(),f"Whole-cell reconstruction mismatch phase {phase}"
 frames[phase]=cell
 recordpath=ROOT/source["generation_record"]
 record={"direction":DIRECTION,"canonical_phase":phase,"source_path":str(path),"source_sha256":sha(path),"source_native_size":list(im.size),"source_grid":[source["cols"],source["rows"]],"source_index":index,"source_crop_box":list(box),"whole_cell_uniform_scale":factor,"output_cell_size":[CELL,CELL],"output_rgba_sha256":pixels(cell),"per_subject_bbox_fit":False,"mirror":False,"synthetic_pose_or_interpolation":False,"generation_record_path":str(recordpath),"generation_record_sha256":sha(recordpath)}
 records[phase]=record;upstream[str(path)]=sha(path);upstream[str(recordpath)]=sha(recordpath)
assert len({pixels(im) for im in frames.values()})==8
for name,phases in (("keys-final-raw",[1,3,5,7]),("inbetweens-final-raw",[2,4,6,8])):
 sheet=Image.new("RGBA",(1254,1254),(255,0,255,255));mapping=[]
 for index,phase in enumerate(phases):
  x,y=index%2*CELL,index//2*CELL;sheet.paste(frames[phase],(x,y));mapping.append({**records[phase],"output_index":index,"output_cell_box":[x,y,x+CELL,y+CELL]})
 path=ROOT/(name+".png");sheet.save(path)
 write(path.with_suffix(".assembly.json"),{"operation":"exact full authored cells; singles whole-canvas downscaled0.5 and627native cells retained1.0","art_source":"builtin image_gen","direction":DIRECTION,"canonical_phases":phases,"output_path":str(path),"output_sha256":sha(path),"output_size":[1254,1254],"output_grid":[2,2],"cell_size":[627,627],"sources":mapping,"new_poses_generated_by_script":False,"per_subject_fit":False,"mirroring":False,"repeated_or_interpolated_pose":False})
walk=Image.new("RGBA",(2508,1254),(255,0,255,255))
for i in range(8):walk.paste(frames[i+1],(i%4*CELL,i//4*CELL))
walkpath=ROOT/f"walk-{DIRECTION}-raw.png";walk.save(walkpath)
write(walkpath.with_suffix(".assembly.json"),{"operation":"exact full-cell eight-phase preview assembly","output_path":str(walkpath),"output_sha256":sha(walkpath),"output_size":[2508,1254],"output_grid":[4,2],"phases":list(range(1,9)),"sources":[records[p] for p in range(1,9)],"per_frame_fit":False,"mirroring":False})
idle=Image.open(ROOT/"idle-source-cell.png").convert("RGBA").resize((CELL,CELL),Image.Resampling.LANCZOS)
allframes=[idle]+[frames[p] for p in range(1,9)];board=Image.new("RGBA",(CELL*3,(CELL+20)*3),(255,0,255,255));draw=ImageDraw.Draw(board);metrics=[]
for i,im in enumerate(allframes):
 x,y=i%3*CELL,i//3*(CELL+20);board.paste(im,(x,y+20));draw.text((x+8,y),f"{DIRECTION} "+("IDLE" if i==0 else f"{i:02}"),fill="black")
 a=np.array(im);fg=(a[:,:,1]>50)|(a[:,:,0]<180)|(a[:,:,2]<180);ys,xs=np.where(fg);top=int(ys.min());bottom=int(ys.max());hair=(a[:,:,0]<145)&(a[:,:,1]<145)&(a[:,:,2]<145);hair[280:,:]=False;widths=[]
 for row in hair[top:top+240]:
  xx=np.where(row)[0]
  if len(xx):widths.append(int(xx.max()-xx.min()+1))
 metrics.append({"phase":"idle" if i==0 else i,"head_top":top,"subject_bottom":bottom,"subject_height":bottom-top+1,"dark_head_width_p90":float(np.percentile(widths,90))})
board.convert("RGB").save(ROOT/"raw-nine-contact-review.jpg",quality=93)
write(ROOT/"raw-metrics.json",metrics)
write(ROOT/"cell-source-map.json",[records[p] for p in range(1,9)])
for p in ROOT.glob("*.txt"):upstream[str(p)]=sha(p)
upstream[str(ROOT/"idle-source-cell.png")]=sha(ROOT/"idle-source-cell.png")
write(ROOT/"upstream-inventory-sha256.json",[{"path":p,"sha256":h} for p,h in sorted(upstream.items())])
print(json.dumps({"direction":DIRECTION,"status":"assembled_raw_candidate_pending_parent_full_direction_review","unique_true_poses":8,"keys_phases":[1,3,5,7],"even_phases":[2,4,6,8],"head_metrics":metrics,"keys_sha256":sha(ROOT/"keys-final-raw.png"),"inbetweens_sha256":sha(ROOT/"inbetweens-final-raw.png")},ensure_ascii=False))
