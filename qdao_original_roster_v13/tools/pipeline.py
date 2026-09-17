"""Generic original-Q roster V13 deterministic processing. No code-generated artwork."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,re,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]; DIRS=('N','NE','E','SE','S','SW','W','NW')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def save(im,p):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def imread(p):
 with Image.open(p) as im:return im.convert('RGBA')
def mod(name):
 p=ROOT/'tools/vendor'/f'{name}.py';s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
KEYER=mod('generate2dsprite'); EDGE=mod('edge_despill')
def require(value,message):
 if not value:raise ValueError(message)
def cropbox(im,threshold=8):
 y,x=np.where(np.asarray(im)[:,:,3]>threshold);require(len(x)>0,'Empty frame');return [int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]
def axis(im):
 y,x=np.where(np.asarray(im)[:,:,3]>8);require(len(x)>0,'Empty frame');top=int(y.min());height=int(y.max())-top;return float(np.median(x[y<top+max(1,int(height*.42))])),int(y.max())
def body_scale(im):
 a=np.asarray(im)[:,:,3];w=im.width;half=max(1,round(w*.25));return math.sqrt(np.count_nonzero(a[:,w//2-half:w//2+half])/(im.width*im.height))
def edge_touch(im):
 a=np.asarray(im)[:,:,3];return any(np.any(e) for e in (a[0],a[-1],a[:,0],a[:,-1]))
def copy_once(src,dst):
 dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():require(sha(src)==sha(dst),f'Immutable source path already has different bytes: {dst}')
 else:shutil.copy2(src,dst)
def output(character):
 require(re.fullmatch(r'[A-Za-z0-9_-]+',character),'Invalid character ID');return ROOT/'candidate'/character

def import_sheet(a):
 out=output(a.character);kind='walk' if a.command=='import-walk' else 'idle';rows,cols=((a.rows or 4),(a.cols or 4)) if kind=='walk' else (2,4)
 require((rows,cols) in ((2,2),(2,4),(4,4)),'Walk sources must be 2x2 pose group, 2x4 half-cycle or 4x4 full-cycle')
 require(kind=='idle' or a.start_frame in (1,9) and (rows==2 or a.start_frame==1),'Use start-frame1 for4x4; start-frame1 or9 for2x4')
 output_frames=[int(v.strip()) for v in a.output_frames.split(',')] if kind=='walk' and a.output_frames else list(range(a.start_frame,a.start_frame+rows*cols)) if kind=='walk' else [0]*(rows*cols)
 if kind=='walk':
  require((rows,cols)!=(2,2) or a.output_frames,'2x2 pose groups require explicit --output-frames')
  require(len(output_frames)==rows*cols and len(set(output_frames))==len(output_frames) and all(1<=v<=16 for v in output_frames),'--output-frames must map each source cell to a distinct final frame1..16')
 require(a.source and a.prompt,'--source and --prompt are required');require(a.source.is_file() and a.prompt.is_file(),'Source image or exact prompt file missing')
 profile_path=out/'processing/scale-profile.json';scale=float(a.common_scale if a.common_scale is not None else load(profile_path)['common_scale'] if profile_path.exists() else 1.0)
 require(math.isfinite(scale) and scale>0,'Invalid character-wide scale')
 profile={'whole_cell_normalization':'512/max(native_cell_width,native_cell_height)','common_scale':scale,'per_subject_bbox_scaling':False,'root_px':[256,471],'alignment_version':2,'horizontal':'upper_body_alpha_median_42_percent','vertical':'lowest_alpha_gt_8'}
 if profile_path.exists():require(load(profile_path)==profile,'Every direction/idle of one character must use one common_scale. Do not scale individual frames.')
 else:write(profile_path,profile)
 bid=a.batch_id or f'{kind}-{a.direction or "8dir"}-{a.start_frame if kind=="walk" else 0:02d}-{sha(a.source)[:12]}'
 require(re.fullmatch(r'[A-Za-z0-9_-]+',bid),'Invalid batch ID')
 source_dir=out/'source'/bid;copy_once(a.source,source_dir/'raw.png');copy_once(a.prompt,source_dir/'prompt.txt')
 if a.receipt:copy_once(a.receipt,source_dir/'generation-receipt.json')
 raw=imread(source_dir/'raw.png');cw=raw.width/cols;ch=raw.height/rows;factor=512/max(cw,ch)*scale
 records=load(out/'processing/frame-sources.json') if (out/'processing/frame-sources.json').exists() else {};selected=[];work=out/'processing/batches'/bid
 for index in range(rows*cols):
  d=a.direction if kind=='walk' else DIRS[index];frame=output_frames[index] if kind=='walk' else 0;r,c=divmod(index,cols)
  box=[round(c*cw),round(r*ch),round((c+1)*cw),round((r+1)*ch)];cell=raw.crop(box);keyed=KEYER.remove_bg_magenta(cell.copy(),100,150)
  require(not edge_touch(keyed),f'{d}/{frame:02d}: original cell touches boundary; regenerate rather than hide clipping')
  size=(round(cell.width*factor),round(cell.height*factor));normal=keyed.resize(size,Image.Resampling.LANCZOS) if keyed.size!=size else keyed.copy()
  clean,cleanup=EDGE.despill(normal,radius=4,reference_radius=12);ax,ay=axis(clean);delta=[round(256-ax),471-ay];b=cropbox(clean,0)
  moved=[b[0]+delta[0],b[1]+delta[1],b[2]+delta[0],b[3]+delta[1]]
  require(min(moved[:2])>=1 and max(moved[2:])<=511,f'{d}/{frame:02d}: aligned frame would clip {moved}; correct generation or one common character-wide scale')
  final=Image.new('RGBA',(512,512));final.paste(clean,tuple(delta));relative=f'walk/{d}/{frame:02d}.png' if kind=='walk' else f'idle/{d}.png'
  stages={}
  for name,im in [('cell',cell),('keyed',keyed),('normalized',normal),('cleaned',clean),('final',final)]:
   p=work/d/f'{frame:02d}-{name}.png';save(im,p);stages[name]={'path':p.relative_to(out).as_posix(),'sha256':sha(p)}
  receipt=source_dir/'generation-receipt.json'
  rec={'kind':kind,'direction':d,'frame':frame,'source':{'path':(source_dir/'raw.png').relative_to(out).as_posix(),'sha256':sha(source_dir/'raw.png'),'native_size':list(raw.size),'grid':[rows,cols],'cell_index':index,'sequence_start_frame':a.start_frame if kind=='walk' else 0,'output_frame_map':output_frames if kind=='walk' else None,'cell_xyxy':box},'prompt':{'path':(source_dir/'prompt.txt').relative_to(out).as_posix(),'sha256':sha(source_dir/'prompt.txt')},'generation':{'tool':'built-in image_gen','model_requested':'GPT Image 2','model_actual':'not asserted by this processor','receipt':{'path':receipt.relative_to(out).as_posix(),'sha256':sha(receipt)} if receipt.exists() else None,'status':'unreviewed'},'whole_cell_scale':factor,'common_scale':scale,'normalized_size':list(size),'chroma_thresholds':[100,150],'cleanup':cleanup,'despill_radius':4,'translation_px':delta,'alignment_version':2,'anchor_after_px':list(axis(final)),'stages':stages,'output':relative,'output_sha256':stages['final']['sha256'],'visual_review':'pending'}
  records[relative]=rec;selected.append(rec)
 source_keys=[(rec['source']['sha256'],tuple(rec['source']['cell_xyxy'])) for rec in records.values()]
 require(len(source_keys)==len(set(source_keys)),'One actual source cell is assigned to more than one final pose; reject reuse')
 # Commit the entire direction only after every original source cell passes.
 for rec in selected:
  dst=out/rec['output'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/rec['stages']['final']['path'],dst)
 write(work/'selected.json',selected);write(out/'processing/frame-sources.json',records)
 print(json.dumps({'character':a.character,'imported':len(selected),'kind':kind,'direction':a.direction,'common_scale':scale,'status':'pending_visual_review'}))
 review(a.character)

def portrait(a):
 out=output(a.character);require(a.source and a.source.is_file(),'--source is required');im=imread(a.source)
 require(im.size==(4096,4096),'Portrait source must be the restored original 4096 x 4096 image')
 dest=out/'source/original-portrait-4096.png';copy_once(a.source,dest);result=im.resize((1024,1024),Image.Resampling.LANCZOS);save(result,out/'portrait.png')
 write(out/'processing/portrait-source.json',{'source_path':str(a.source.resolve()),'preserved_source':'source/original-portrait-4096.png','source_sha256':sha(a.source),'source_size':[4096,4096],'output_size':[1024,1024],'processing':'whole_image_LANCZOS_downsample_no_crop','output_sha256':sha(out/'portrait.png')})
 review(a.character)

def review(character):
 out=output(character);sources=load(out/'processing/frame-sources.json') if (out/'processing/frame-sources.json').exists() else {};directions={};errors=[];means=[]
 for d in DIRS:
  paths=[out/f'walk/{d}/{i:02d}.png' for i in range(1,17)]
  if not all(p.exists() for p in paths):
   available=[(i+1,imread(p)) for i,p in enumerate(paths) if p.exists()]
   directions[d]={'status':'incomplete','available_frames':len(available)}
   if available:
    rows=math.ceil(len(available)/4);sheet=Image.new('RGB',(2048,rows*544),(38,44,45));draw=ImageDraw.Draw(sheet)
    for slot,(number,im) in enumerate(available):
     x=(slot%4)*512;y=(slot//4)*544;sheet.paste(im,(x,y),im);draw.text((x+12,y+514),f'{d} / {number:02d} [partial]',fill='white')
    save(sheet,out/f'review/{d}-partial-contact.png')
   continue
  frames=[imread(p) for p in paths];strip=Image.new('RGBA',(8192,512))
  for i,im in enumerate(frames):strip.paste(im,(i*512,0))
  save(strip,out/f'walk/{d}/strip.png')
  idle=imread(out/f'idle/{d}.png') if (out/f'idle/{d}.png').exists() else None
  display=([idle] if idle is not None else [])+frames;sheet=Image.new('RGB',(2048,5*544 if idle else 4*544),(38,44,45));draw=ImageDraw.Draw(sheet)
  for i,im in enumerate(display):
   x=(i%4)*512;y=(i//4)*544;sheet.paste(im,(x,y),im);draw.text((x+12,y+514),f'{d} / '+('idle' if idle is not None and i==0 else f'{i if idle else i+1:02d}'),fill='white')
  save(sheet,out/f'review/{d}-contact.png')
  heights=[cropbox(im)[3]-cropbox(im)[1] for im in frames];mean=float(np.mean(heights));means.append(mean);scales=[body_scale(im) for im in frames];cv=float(np.std(scales)/np.mean(scales));unique=len({hashlib.sha256(im.tobytes()).hexdigest() for im in frames});drift=abs((cropbox(idle)[3]-cropbox(idle)[1])/mean-1) if idle else None
  problems=[]
  if cv>.08:problems.append('body_scale_cv')
  if unique!=16:problems.append('duplicate_frames')
  if drift is not None and drift>.08:problems.append('idle_walk_height_drift')
  if idle is not None and idle.tobytes() in [im.tobytes() for im in frames]:problems.append('idle_copied_walk')
  for im in frames+([idle] if idle else []):
   x,y=axis(im)
   if abs(x-256)>.5 or y!=471:problems.append('body_axis_or_feet_anchor')
  directions[d]={'status':'failed' if problems else 'passed_numeric_pending_visual','frame_count':16,'unique_frames':unique,'body_scale_cv':cv,'subject_height_mean':mean,'idle_walk_height_drift':drift,'errors':problems};errors.extend(f'{d}: {e}' for e in problems)
 ratio=max(means)/min(means) if means else None
 if ratio and ratio>1.1:errors.append('cross_direction_mean_height_ratio')
 expected=['portrait.png',*[f'idle/{d}.png' for d in DIRS],*[f'walk/{d}/{i:02d}.png' for d in DIRS for i in range(1,17)],*[f'walk/{d}/strip.png' for d in DIRS]]
 files=[{'path':p,'sha256':sha(out/p)} for p in expected if (out/p).exists()];status='failed' if errors else ('passed_numeric_pending_visual' if len(files)==145 else 'incomplete')
 qc={'status':status,'visual_review':'pending','directions':directions,'cross_direction_mean_height_ratio':ratio,'errors':errors,'gates':{'body_scale_cv_max':.08,'idle_walk_height_drift_max':.08,'cross_direction_height_ratio_max':1.10,'unique_frames_per_direction':16,'horizontal_axis_error_px':.5,'foot_y':471}}
 write(out/'qc.json',qc)
 manifest={'version':13,'character_id':character,'status':status,'visual_review':'pending','art_source':'built-in image_gen for every new walk/idle; original restored portrait','directions':list(DIRS),'frame_count':16,'frame_duration_ms':30,'cycle_duration_ms':480,'dedicated_idle':True,'contact_frame':0,'alignment':load(out/'processing/scale-profile.json') if (out/'processing/scale-profile.json').exists() else None,'sources_path':'processing/frame-sources.json','sources_sha256':sha(out/'processing/frame-sources.json') if sources else None,'files':files,'generated_walk_count':sum(r['kind']=='walk' for r in sources.values()),'generated_idle_count':sum(r['kind']=='idle' for r in sources.values())}
 write(out/'manifest.json',manifest);preview();print(json.dumps({'character':character,'status':status,'pngs':len(files),'errors':errors}))

def preview():
 inventory=[]
 for path in sorted((ROOT/'candidate').glob('*/manifest.json')):
  m=load(path);inventory.append({'id':m['character_id'],'status':m['status'],'directions':{d:(path.parent/f'walk/{d}/16.png').exists() for d in DIRS}})
 write(ROOT/'preview-index.json',inventory)
 template=ROOT/'tools/preview.html'
 if template.exists():shutil.copy2(template,ROOT/'index.html')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['import-walk','import-idle','portrait','review','preview']);p.add_argument('--character');p.add_argument('--direction',choices=DIRS);p.add_argument('--source',type=Path);p.add_argument('--prompt',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--batch-id');p.add_argument('--common-scale',type=float,default=None);p.add_argument('--rows',type=int,choices=(2,4));p.add_argument('--cols',type=int,choices=(2,4));p.add_argument('--output-frames',help='Comma-separated final frame number for each source cell in row-major order');p.add_argument('--start-frame',type=int,choices=(1,9),default=1);a=p.parse_args()
 if a.command=='preview':preview();return
 require(a.character,'--character is required')
 if a.command=='import-walk':require(a.direction,'--direction is required');import_sheet(a)
 elif a.command=='import-idle':import_sheet(a)
 elif a.command=='portrait':portrait(a)
 else:review(a.character)
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'status':'blocked','error':str(e)}),file=sys.stderr);sys.exit(1)
