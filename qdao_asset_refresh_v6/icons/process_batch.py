"""Deterministic slicing of generated compact icon grids; no creative drawing."""
import argparse,pathlib,json,hashlib,subprocess,sys,shutil
import numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[2]
ICONROOT=ROOT/'q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600'
SKILL=pathlib.Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--batch',type=int,required=True);ap.add_argument('--rows',type=int,default=4);ap.add_argument('--cols',type=int,default=4);ap.add_argument('--prompt',required=True);ap.add_argument('--publish',action='store_true');a=ap.parse_args()
 raw=pathlib.Path(a.raw);im=Image.open(raw).convert('RGB');arr=np.asarray(im);mag=(arr[:,:,0]>160)&(arr[:,:,2]>160)&(arr[:,:,1]<100)
 def bounds(axis,count):
  ink=(~mag).sum(axis=axis);n=len(ink);cuts=[0]
  for k in range(1,count):
   mid=n*k/count;zone=range(max(0,int(mid-n/count*.20)),min(n,int(mid+n/count*.20)))
   zero=[i for i in zone if ink[i]==0]
   if not zero:raise ValueError(f'No clear magenta separator on axis{axis} boundary{k}; regenerate')
   runs=[];start=last=zero[0]
   for v in zero[1:]:
    if v>last+1:runs.append((start,last));start=v
    last=v
   runs.append((start,last));lo,hi=max(runs,key=lambda p:p[1]-p[0]);cuts.append((lo+hi)//2)
  cuts.append(n);return cuts
 xb=bounds(0,a.cols);yb=bounds(1,a.rows);cell=max(max(np.diff(xb)),max(np.diff(yb)))+32
 normalized=Image.new('RGB',(cell*a.cols,cell*a.rows),(255,0,255))
 for row in range(a.rows):
  for col in range(a.cols):
   crop=im.crop((xb[col],yb[row],xb[col+1],yb[row+1]));normalized.paste(crop,(col*cell+(cell-crop.width)//2,row*cell+(cell-crop.height)//2))
 taskroot=pathlib.Path(__file__).resolve().parent;work=taskroot/'.work'/f'batch{a.batch:02d}';work.mkdir(parents=True,exist_ok=True);norm=work/'normalized-source.png';normalized.save(norm)
 args=[sys.executable,str(SKILL),'process','--input',str(norm),'--target','asset','--mode','prop_pack_4x4','--rows',str(a.rows),'--cols',str(a.cols),'--output-dir',str(work/'processed'),'--cell-size','600','--fit-scale','0.91','--align','center','--scale-strategy','fit','--component-mode','largest','--min-component-area','30','--strict-qc','--prompt-file',a.prompt]
 subprocess.run(args,check=True)
 record={'batch':a.batch,'raw_generation_path':str(raw),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'raw_native_size':list(im.size),'grid':[a.rows,a.cols],'separator_x':xb,'separator_y':yb,'normalization':'Find full-magenta separator bands; preserve every pixel in each subject; center padded source cells without drawing or resampling. Then skill cleanup/split/fit to600px.','processor':str(SKILL),'processor_args':args,'prompt':a.prompt,'native_resolution_note':'Final600x600is a clean export, not native AI600px per cell.','published':False}
 if a.publish:
  sources=sorted((ICONROOT/'west_eight_immortals_redrawn_100_600x600').glob('*.png'))+sorted((ICONROOT/'character_artifacts_redrawn_24_600x600').glob('*.png'))
  targets=sources[(a.batch-1)*16:(a.batch-1)*16+a.rows*a.cols]
  if len(targets)!=a.rows*a.cols:raise ValueError('Target count mismatch')
  record['outputs']=[]
  for i,dst in enumerate(targets,1):
   src=work/'processed'/f'prop_pack_4x4-{i}.png';frame=Image.open(src)
   if frame.size!=(600,600) or frame.mode!='RGBA':raise ValueError('Bad final frame')
   pixels=np.array(frame);spill=(pixels[:,:,0]>160)&(pixels[:,:,2]>160)&(pixels[:,:,1]<100)&(pixels[:,:,3]>0);pixels[spill]=(0,0,0,0);frame=Image.fromarray(pixels);frame.save(dst,optimize=True);record['outputs'].append({'path':dst.relative_to(ROOT).as_posix(),'size':[600,600],'mode':'RGBA','alpha_range':list(frame.getchannel('A').getextrema()),'alpha_bbox':list(frame.getchannel('A').getbbox()),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'cell_index':i-1,'final_key_spill_pixels_removed':int(spill.sum())})
  qc=json.loads((work/'processed'/'pipeline-meta.json').read_text(encoding='utf8'));(taskroot/'records'/f'batch{a.batch:02d}.qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n',encoding='utf8');record['published']=True
 (taskroot/'records'/f'batch{a.batch:02d}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('NORMALIZED',xb,yb,'OUTPUT',work/'processed')
if __name__=='__main__':main()
