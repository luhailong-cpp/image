"""Read-only audit of 05 NE; all derived review outputs stay beside this script."""
from pathlib import Path
import hashlib, importlib.util, json, sys
sys.dont_write_bytecode = True
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHAR = '05_celestial_musician_girl'
NEW = ROOT / 'qdao_original_roster_v14_hd/candidate' / CHAR
OLD = ROOT / 'qdao_original_roster_v13/candidate' / CHAR
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value): (HERE/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def image(p):
    with Image.open(p) as im: return im.convert('RGBA')
def local(path):
    return ROOT / path[len('E:/work/image/'):] if path.replace('\\','/').startswith('E:/work/image/') else Path(path)

sources=read(NEW/'processing/frame-sources.json')
manifest=read(NEW/'manifest.json')
spec=importlib.util.spec_from_file_location('readonly_verify',ROOT/'qdao_original_roster_v14_hd/tools/verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
rows=[]
for key, record in sorted(sources.items()):
    receipt_path=NEW/record['generation']['receipt']['path']; receipt=read(receipt_path)
    raw_path=NEW/record['source']['path']; batch=raw_path.parent.name
    generation_dir=ROOT/'qdao_original_roster_v14_hd/generation'/CHAR/batch
    prompt=NEW/record['prompt']['path']; request=receipt.get('actual_request',{})
    refs=[{'historical':p,'local':str(local(p)),'exists':local(p).is_file(),
           'sha256':sha(local(p)) if local(p).is_file() else None}
          for p in request.get('referenced_image_paths',[])]
    try: result=verify.verify(CHAR,'NE',False,record['frame'])
    except Exception as error: result={'status':'failed','error':str(error)}
    row={'path':key,'output_sha256':sha(NEW/key),'raw_sha256':sha(raw_path),
         'receipt_sha256':sha(receipt_path),'prompt_sha256':sha(prompt),
         'raw_size':list(image(raw_path).size),'output_size':list(image(NEW/key).size),
         'prompt_exact_request_bytes':prompt.read_bytes()==request.get('prompt','').encode('utf-8'),
         'generation_raw_exists':(generation_dir/'raw.png').is_file(),
         'generation_raw_equal':(generation_dir/'raw.png').is_file() and sha(generation_dir/'raw.png')==sha(raw_path),
         'source_and_generation_prompt_equal':(generation_dir/'prompt.txt').is_file() and sha(generation_dir/'prompt.txt')==sha(prompt),
         'receipt_original_generated_file':receipt.get('original_generated_file'),
         'historical_default_original_exists_on_this_machine':Path(receipt.get('original_generated_file','')).is_file(),
         'references':refs,'generation_calls_recorded':receipt.get('generation_calls'),
         'paid_api_calls_recorded':receipt.get('paid_api_calls'),
         'actual_model_recorded':receipt.get('model_actual',receipt.get('actual_model')),
         'independent_reconstruction':result}
    rows.append(row)
    print(json.dumps({'frame':record['frame'],'status':result['status']},ensure_ascii=False),flush=True)

frames=[];metrics=[]
for number in range(1,17):
    relative=f'walk/NE/{number:02d}.png'
    path=OLD/relative if number in (1,5,9,13) else NEW/relative
    im=image(path);arr=np.asarray(im);ys,xs=np.where(arr[:,:,3]>8);scale=1024/im.width
    top=int(ys.min());height=int(ys.max()-ys.min()+1)
    axis=float(np.median(xs[ys<top+max(1,int((height-1)*.42))]))
    metrics.append({'frame':number,'source':str(path.relative_to(ROOT)).replace('\\','/'),
                    'sha256':sha(path),'pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest(),
                    'source_size':list(im.size),'preserved_legacy':number in (1,5,9,13),
                    'alpha_min':int(arr[:,:,3].min()),'alpha_max':int(arr[:,:,3].max()),
                    'alpha_bbox_native':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
                    'foot_y_world_1024':int(ys.max())*scale,'body_axis_world_1024':axis*scale,
                    'visible_height_world_1024':height*scale,
                    'preview_display_only_scale':scale})
    frames.append(im.resize((1024,1024),Image.Resampling.LANCZOS) if im.size!=(1024,1024) else im)

try: font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
except OSError: font=ImageFont.load_default()
def panel(im, number, size=384, color='#202b38'):
    tile=Image.new('RGB',(size,size+32),color);tile.paste(im.resize((size,size),Image.Resampling.LANCZOS),(0,32),im.resize((size,size),Image.Resampling.LANCZOS))
    ImageDraw.Draw(tile).text((8,4),f'NE{number:02d} '+('OLD 512' if number in (1,5,9,13) else 'NEW 1024'),font=font,fill='#f0b95c' if color!='white' else '#153c46')
    return tile
for bg,name in [('#202b38','dark'),('white','white')]:
    contact=Image.new('RGB',(1536,1664),bg)
    for n,im in enumerate(frames):contact.paste(panel(im,n+1,color=bg),((n%4)*384,(n//4)*416))
    contact.save(HERE/f'NE-16-contact-{name}.png')
    seam=Image.new('RGB',(1536,544),bg)
    for x,n in enumerate((15,16,1)):seam.paste(panel(frames[n-1],n,512,bg),(512*x,0))
    seam.save(HERE/f'NE-seam-15-16-01-{name}.png')
    keys=Image.new('RGB',(2048,544),bg)
    for x,n in enumerate((1,5,9,13)):keys.paste(panel(frames[n-1],n,512,bg),(512*x,0))
    keys.save(HERE/f'NE-keys-01-05-09-13-{name}.png')

preview=[panel(im,n+1,512) for n,im in enumerate(frames)]
preview[0].save(HERE/'NE-16-30ms.gif',save_all=True,append_images=preview[1:],duration=30,loop=0,disposal=2)
preview[0].save(HERE/'NE-16-30ms.webp',save_all=True,append_images=preview[1:],duration=30,loop=0,lossless=True)
with Image.open(HERE/'NE-16-30ms.gif') as gif:
    durations=[]
    for n in range(gif.n_frames):gif.seek(n);durations.append(gif.info['duration'])
summary={'character_id':CHAR,'audited_at_utc':datetime.now(timezone.utc).isoformat(),
         'scope':'read-only 12 native NE sources and mixed 16-frame NE preview, not full-character approval',
         'workspace':str(ROOT),'historical_repo_path':'E:/work/image','path_mapping_verified_by_reference_existence':all(x['exists'] for r in rows for x in r['references']),
         'manifest_sha256':sha(NEW/'manifest.json'),'source_mapping_sha256':sha(NEW/'processing/frame-sources.json'),
         'source_rows':rows,'mixed_sequence':metrics,'unique_mixed_pixel_hashes':len({r['pixel_sha256'] for r in metrics}),
         'independent_reconstructed_frames_passed':sum(r['independent_reconstruction']['status']=='partial_sources_pending_visual' for r in rows),
         'preview':{'frame_count':len(durations),'durations_ms':durations,'cycle_ms':sum(durations),'legacy_upscale_for_display_only':True,'synthetic_frames_created':0},
         'missing_walk':{d:list(range(1,17)) for d in ('SE','SW','W','NW')},'missing_idle':[],
         'visual_review_status':'pending_direct_inspection','client_import_performed':False,'new_generation_calls':0,'new_paid_api_calls':0}
write('NE-source-audit.json',summary)
frame_paths=[str(Path('../../../')/r['source']).replace('\\','/') for r in metrics]
data={'frames':frame_paths,'idle':'../../../qdao_original_roster_v13/candidate/'+CHAR+'/idle/NE.png'}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>05 天音少女 NE 动作审查</title><style>body{background:#f6f1e5;color:#18333c;font:16px/1.6 sans-serif;margin:24px}button{font:inherit;padding:8px 16px;margin:6px;background:#e4efec;border:1px solid #a0b2a7}canvas{width:min(60vw,512px);background:#202b38}.row{display:flex;gap:22px;align-items:start}#idle{width:300px}#timeline{max-width:900px}h1{font-size:24px}img{max-width:100%}</style><h1>05 天音少女 · NE 16 帧校阅</h1><p>30 毫秒 / 帧，480 毫秒循环。旧图 512 与新图 1024 按同世界尺寸显示；原文件保持不动。</p><button id="play">播放 / 暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><button id="background">白色 / 深色背景</button><strong id="label"></strong><div class="row"><canvas id="walk" width="1024" height="1024"></canvas><div>独立站立图<br><canvas id="idle" width="1024" height="1024"></canvas></div></div><div id="timeline"></div><p>视觉结论见 NE-VISUAL-REVIEW.md；本页不批准素材。</p><h2>15 → 16 → 01</h2><img src="NE-seam-15-16-01-dark.png"><script>const data=DATA;const walk=document.querySelector('#walk'),label=document.querySelector('#label');let phase=0,playing=false,last=performance.now(),white=false;const imgs=data.frames.map(p=>{let im=new Image;im.src=p;return im});function paint(){let n=Math.floor(phase/30)%16;let c=walk.getContext('2d');c.clearRect(0,0,1024,1024);if(imgs[n].complete)c.drawImage(imgs[n],0,0,1024,1024);label.textContent=` NE${String(n+1).padStart(2,'0')} · ${[1,5,9,13].includes(n+1)?'旧512':'新1024'}`;}const idle=new Image;idle.onload=()=>document.querySelector('#idle').getContext('2d').drawImage(idle,0,0,1024,1024);idle.src=data.idle;imgs.forEach(im=>im.onload=paint);document.querySelector('#play').onclick=()=>{playing=!playing;last=performance.now()};function frame(n){playing=false;phase=((n+16)%16)*30;paint()}document.querySelector('#prev').onclick=()=>frame(Math.floor(phase/30)-1);document.querySelector('#next').onclick=()=>frame(Math.floor(phase/30)+1);document.querySelector('#background').onclick=()=>{white=!white;document.querySelectorAll('canvas').forEach(c=>c.style.background=white?'white':'#202b38')};for(let n=0;n<16;n++){let b=document.createElement('button');b.textContent=String(n+1).padStart(2,'0');b.onclick=()=>frame(n);document.querySelector('#timeline').append(b)}function tick(t){if(playing){phase=(phase+t-last)%480;paint()}last=t;requestAnimationFrame(tick)}requestAnimationFrame(tick);</script></html>'''.replace('DATA',json.dumps(data))
(HERE/'preview.html').write_text(html,encoding='utf-8')
print(json.dumps({'audited':len(rows),'reconstructed_passed':summary['independent_reconstructed_frames_passed'],'preview_cycle_ms':sum(durations)},ensure_ascii=False))
