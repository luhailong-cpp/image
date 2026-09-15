from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
r=Path(r'E:\work\image\qdao_chibi_roster_v12');p=r/'review/27_ranger_natural_fixes';dest=r/'candidate-stable-body/27_ink_kite_ranger/source';dest.mkdir(parents=True,exist_ok=True)
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def metrics(im):
 a=np.array(im.convert('RGB'));fg=~((a[:,:,0]>165)&(a[:,:,1]<120)&(a[:,:,2]>150)&(a[:,:,0]>a[:,:,1]*1.5));ys,xs=np.where(fg)
 return {'height':int(ys.max()-ys.min()+1),'top':int(ys.min()),'bottom':int(ys.max()),'width':int(xs.max()-xs.min()+1)}
report={}
for d in ['NE','NW']:
 src=p/(d+'-size-gait-candidate-raw.png');native=Image.open(src).convert('RGBA');im=native.resize((1772,886),Image.Resampling.LANCZOS);records=[]
 orig=r/'27_ink_kite_ranger/source'/('walk-'+d+'.png');base=Image.open(orig).convert('RGBA')
 cells=[]
 for i in range(8):
  box=[i%4*443,i//4*443,i%4*443+443,i//4*443+443];chosen=orig if d=='NE' and i==2 else src
  cell=(base if chosen==orig else im).crop(box);cells.append(cell)
  if chosen==orig:im.paste(cell,(box[0],box[1]))
  records.append({'output_phase':i+1,'source':str(chosen),'sha256':sha(chosen),'native_size':list(Image.open(chosen).size),'grid':[4,2],'grid_index':i+1,'normalized_sheet_size':[1772,886],'normalized_cell_box':box,'full_cell_resolution_normalization':chosen!=orig,'authored_pose':True,'preserved_original':chosen==orig})
 out=dest/('walk-'+d+'-final.png');im.save(out);out.with_suffix('.assembly.json').write_text(json.dumps({'direction':d,'output_sha256':sha(out),'phase_order':'RIGHT-first canonical unchanged original order','grid':[4,2],'source_cells':records,'synthetic_poses':False,'mirrored':False,'per_pose_bbox_fit':False},indent=2)+'\n')
 idle=Image.open(p/(d+'-idle-reference.png')).convert('RGBA');poses=[idle]+cells
 board=Image.new('RGB',(900,960),'#ff00ff');dr=ImageDraw.Draw(board)
 for i,pose in enumerate(poses):board.paste(pose.resize((300,300)),(i%3*300,i//3*320+20));dr.text((i%3*300+6,i//3*320+3),d+' '+('IDLE' if i==0 else str(i)),fill='black')
 board.save(p/(d+'-final-source-contact.jpg'),quality=92)
 report[d]={'idle':metrics(idle),'walk':[metrics(c) for c in cells],'file':str(out),'sha256':sha(out)}
(p/'NE-NW-selected-source-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

