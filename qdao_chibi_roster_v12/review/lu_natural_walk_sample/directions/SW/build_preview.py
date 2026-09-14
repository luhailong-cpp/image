from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,hashlib,numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from process_roster import run_sheet,normalize,body_ground_anchor,bounds,compose,load_processor,DEFAULT_PROCESSOR
frames,meta,source,errors=run_sheet(HERE/'walk-SW-raw.png','SW',HERE/'processing',padding=0,rows=2,cols=4)
if errors: raise ValueError(errors)
OUT=HERE/'preview';OUT.mkdir(exist_ok=True)
records=[];final=[]
for i,frame in enumerate(frames):
 im,record=normalize(frame,1.0,despill_edges=True)
 im.save(OUT/f'SW-{i+1:02}.png');final.append(im);records.append(record)
assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in final})==8
assert all(body_ground_anchor(im)==(256.,471) for im in final)
compose(final,8).save(OUT/'SW-strip.png');compose(final,4).save(OUT/'SW-sheet.png')
proc=load_processor(DEFAULT_PROCESSOR);proc.save_transparent_gif(final,OUT/'SW-transparent.gif',60)
for label,color in [('light','#e8e3d9'),('dark','#263737')]:
 mats=[]
 for im in final:
  mat=Image.new('RGBA',(512,512),color);mat.alpha_composite(im);mats.append(mat.convert('RGB'))
 mats[0].save(OUT/f'SW-{label}.gif',save_all=True,append_images=mats[1:],duration=60,loop=0,disposal=2)
board=Image.new('RGB',(1536,870),'#e8e3d9');d=ImageDraw.Draw(board)
for i,im in enumerate(final):
 x=i%4*384;y=i//4*420
 thumb=im.resize((384,384),Image.Resampling.LANCZOS);board.paste(thumb,(x,y+45),thumb);d.text((x+25,y+20),f'SW-{i+1:02} | 60 ms',fill='#24362f')
board.save(OUT/'contact-sheet.jpg',quality=92)
metrics=[]
for i,im in enumerate(final):
 a=np.asarray(im.getchannel('A'));ys,xs=np.nonzero(a>128);top=int(ys.min());widths=[]
 for y in range(top+15,top+130):
  xx=np.where(a[y]>128)[0]
  if len(xx):widths.append(int(xx[-1]-xx[0]+1))
 metrics.append({'frame':i+1,'head_top':top,'head_width_p90':float(np.percentile(widths,90)),'bounds':bounds(im)})
manifest={'status':'numeric_pass_pending_root_visual_review','direction':'SW','frame_count':8,'duration_ms':60,'unique_rgba_frames':8,'same_raw_cell_scale':True,'shared_final_scale':1.0,'published_to_game':False,'source':source,'numeric_qc':meta['direction_qc'],'head_metrics':metrics,'frames':records}
(OUT/'preview-meta.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':manifest['status'],'head_metrics':metrics,'numeric_qc':meta['direction_qc']},ensure_ascii=False,indent=2))
