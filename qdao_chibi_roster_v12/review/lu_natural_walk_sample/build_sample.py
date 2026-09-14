from pathlib import Path
from PIL import Image, ImageDraw
import sys, json, hashlib, numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from process_roster import normalize, bounds, body_ground_anchor, load_processor, DEFAULT_PROCESSOR
HERE=Path(__file__).resolve().parent
OUT=HERE/'preview-eight'
OUT.mkdir(exist_ok=True)
sets=[]
for folder in ['processing-four','processing-inbetweens']:
    base=HERE/folder
    meta=json.loads((base/'pipeline-meta.json').read_text())
    clean=Image.open(base/'raw-sheet-clean.png').convert('RGBA')
    extracted=[]
    for info in meta['frames']:
        crop=clean.crop(info['source_box']).crop(info['crop_bbox'])
        pre=Image.new('RGBA',(512,512))
        pre.paste(crop.resize(tuple(info['output_size']),Image.Resampling.LANCZOS),tuple(info['paste_position']))
        result,record=normalize(pre,1.0,despill_edges=True)
        record.update(processor=folder,source_box=info['source_box'],raw_cell_scale=info['source_to_output_scale'])
        extracted.append((result,record))
    sets.append(extracted)
frames=[];records=[]
for k in range(4):
    for s in range(2):
        im,record=sets[s][k]
        i=len(frames)+1
        im.save(OUT/f'S-{i:02}.png')
        frames.append(im);records.append(record)
assert len({hashlib.sha256(f.tobytes()).hexdigest() for f in frames})==8
assert len({r['raw_cell_scale'] for r in records})==1
assert all(body_ground_anchor(f)==(256.,471) for f in frames)
strip=Image.new('RGBA',(4096,512))
for i,f in enumerate(frames):strip.paste(f,(i*512,0))
strip.save(OUT/'S-strip.png')
proc=load_processor(DEFAULT_PROCESSOR)
proc.save_transparent_gif(frames,OUT/'natural-walk-eight-transparent.gif',60)
for theme,color in [('light','#e8e3d9'),('dark','#263737')]:
    mats=[]
    for f in frames:
        im=Image.new('RGBA',(512,512),color);im.alpha_composite(f);mats.append(im.convert('RGB'))
    mats[0].save(OUT/f'natural-walk-eight-{theme}.gif',save_all=True,append_images=mats[1:],duration=60,loop=0,disposal=2)
board=Image.new('RGB',(1536,870),'#e8e3d9');d=ImageDraw.Draw(board)
for i,f in enumerate(frames):
    x=i%4*384;y=i//4*420
    thumb=f.resize((384,384),Image.Resampling.LANCZOS)
    board.paste(thumb,(x,y+45),thumb)
    d.text((x+25,y+20),f'S-{i+1:02} | 60 ms',fill='#24362f')
board.save(OUT/'contact-sheet.jpg',quality=92)
metrics=[]
for i,im in enumerate(frames):
    a=np.asarray(im.getchannel('A'));ys,xs=np.nonzero(a>128);top=int(ys.min())
    widths=[]
    # Stable upper head region, excluding long hair and sword below face.
    for y in range(top+15,top+130):
        xx=np.where(a[y]>128)[0]
        if len(xx):widths.append(int(xx[-1]-xx[0]+1))
    metrics.append({'frame':i+1,'head_top':top,'head_width_p90':float(np.percentile(widths,90)),'bounds':bounds(im)})
manifest={'status':'single_direction_style_sample_pending_user_feedback','direction':'S','frame_count':8,'duration_ms':60,'unique_rgba_frames':8,'same_raw_cell_scale':True,'shared_final_scale':1.0,'published_to_game':False,'final_contract_unchanged':'8 directions x 8 authored walk frames + 8 independent idle frames','sources':[{'file':f,'sha256':hashlib.sha256((HERE/f).read_bytes()).hexdigest()} for f in ['walk-four-keys-raw.png','walk-four-inbetweens-raw.png']],'head_metrics':metrics,'frames':records}
(OUT/'preview-meta.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['status','frame_count','unique_rgba_frames','head_metrics']},ensure_ascii=False))
