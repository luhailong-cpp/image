from pathlib import Path
import sys,json,hashlib,numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from process_roster import run_sheet, normalize, body_ground_anchor, bounds, compose, load_processor, DEFAULT_PROCESSOR, sha
names=['phase01-single.png','agent-phase02-single.png','agent-phase03-single.png','agent-phase04-single.png','agent-phase05-swapped.png','agent-phase06-single.png','agent-phase07-single.png','agent-phase08-single.png']
raw=Image.new('RGB',(2508,1254),(255,0,255))
records=[]
for i,name in enumerate(names):
 p=HERE/name;im=Image.open(p).convert('RGB')
 assert im.size==(1254,1254),(name,im.size)
 raw.paste(im.resize((627,627),Image.Resampling.LANCZOS),(i%4*627,i//4*627))
 records.append({'frame':i+1,'source':str(p),'source_sha256':sha(p),'source_box':[0,0,1254,1254],'whole_cell_scale':0.5,'operation':'all eight complete square raw canvases resized by same 0.5 resolution ratio, never bbox fitting'})
rawpath=HERE/'walk-NE-agent-raw.png';raw.save(rawpath)
rawpath.with_suffix('.assembly.json').write_text(json.dumps({'output_sha256':sha(rawpath),'frames':records},indent=2),encoding='utf-8')
frames,meta,source,errors=run_sheet(rawpath,'NE',HERE/'agent-processing',padding=0,rows=2,cols=4)
assert not errors,errors
OUT=HERE/'agent-preview';OUT.mkdir(exist_ok=True)
aligned=[];norms=[]
for i,f in enumerate(frames):
 im,r=normalize(f,1.0,despill_edges=True)
 im.save(OUT/f'NE-{i+1:02}.png');aligned.append(im);norms.append(r)
compose(aligned,8).save(OUT/'NE-strip.png')
compose(aligned,4).save(OUT/'NE-sheet.png')
proc=load_processor(DEFAULT_PROCESSOR)
proc.save_transparent_gif(aligned,OUT/'NE-transparent.gif',60)
for theme,c in [('light','#e8e3d9'),('dark','#263737')]:
 mats=[]
 for im in aligned:
  mat=Image.new('RGBA',(512,512),c);mat.alpha_composite(im);mats.append(mat.convert('RGB'))
 mats[0].save(OUT/f'NE-{theme}.gif',save_all=True,append_images=mats[1:],duration=60,loop=0,disposal=2)
board=Image.new('RGB',(1536,870),'#e8e3d9');d=ImageDraw.Draw(board)
metrics=[]
for i,im in enumerate(aligned):
 x=i%4*384;y=i//4*420;th=im.resize((384,384),Image.Resampling.LANCZOS)
 board.paste(th,(x,y+45),th);d.text((x+25,y+20),f'NE-{i+1:02} | 60 ms | feet anchor',fill='#24362f')
 a=np.asarray(im.getchannel('A'));yy,xx=np.nonzero(a>128);top=int(yy.min());widths=[]
 for y0 in range(top+15,top+130):
  x0=np.where(a[y0]>128)[0]
  if len(x0):widths.append(int(x0[-1]-x0[0]+1))
 metrics.append({'frame':i+1,'head_top':top,'head_width_p90':float(np.percentile(widths,90)),'bounds':bounds(im)})
board.save(OUT/'contact-sheet.jpg',quality=92)
manifest={'status':'candidate_pending_visual_and_anchor_review','direction':'NE','frame_count':8,'duration_ms':60,'unique_rgba_frames':len({hashlib.sha256(im.tobytes()).hexdigest() for im in aligned}),'same_raw_cell_scale':True,'shared_final_scale':1.0,'published_to_game':False,'raw_source':source,'head_metrics':metrics,'frames':norms,'processor_qc':meta['direction_qc']}
(OUT/'preview-meta.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'errors':errors,'head_metrics':metrics,'processor_qc':meta['direction_qc']},ensure_ascii=False))

