"""Compose an isolated SW review preview from all sixteen real preserved/new frames."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,base64
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CHAR='04_mountain_guardian_boy'
OUT=HERE/'preview'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
OUT.mkdir(exist_ok=False)
rows=[];frames=[]
for n in range(1,17):
 if n in (1,5,9,13):source=ROOT.parent/f'qdao_original_roster_v13/candidate/{CHAR}/walk/SW/{n:02d}.png';kind='preserved V13 512'
 elif n in (14,15,16):source=HERE/f'candidate/{CHAR}/walk/SW/{n:02d}.png';kind='isolated new V14 1024'
 else:source=ROOT/f'candidate/{CHAR}/walk/SW/{n:02d}.png';kind='existing V14 candidate 1024'
 im=Image.open(source).convert('RGBA');native=list(im.size)
 world=im.resize((1024,1024),Image.Resampling.LANCZOS) if im.size!=(1024,1024) else im.copy();frames.append(world)
 a=np.asarray(world)[:,:,3];ys,xs=np.where(a>8);top=ys.min();axis=float(np.median(xs[ys<top+max(1,int((ys.max()-top)*.42))]))
 rows.append({'frame':n,'source':str(source),'sha256':sha(source),'native_output_size':native,'source_kind':kind,'display_only_equal_world_scale':True,'world_subject_height':int(ys.max()-ys.min()+1),'world_axis':axis,'world_foot_y':int(ys.max()),'body_scale':float(np.sqrt(np.count_nonzero(a[:,256:768])/(1024*1024))), 'image':'data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode('ascii')})
checks=[]
for name,color in [('dark',(30,38,46)),('light',(240,238,228))]:
 text='white' if name=='dark' else 'black';sheet=Image.new('RGB',(2048,2240),color);draw=ImageDraw.Draw(sheet);loops=[]
 for i,im in enumerate(frames):
  display=Image.new('RGB',(1024,1024),color);display.paste(im,(0,0),im);small=display.resize((512,512),Image.Resampling.LANCZOS);x=i%4*512;y=i//4*560;sheet.paste(small,(x,y+32));draw.text((x+10,y+8),f'SW{i+1:02d} / {rows[i]["native_output_size"][0]}px / pending',fill=text);loops.append(small)
 sheet.save(OUT/f'SW-contact-{name}.png')
 gif=OUT/f'SW-30ms-{name}.gif';loops[0].save(gif,save_all=True,append_images=loops[1:],duration=[30]*16,loop=0,optimize=False,disposal=2)
 decoded=Image.open(gif);duration=[]
 for i in range(decoded.n_frames):decoded.seek(i);duration.append(decoded.info['duration'])
 assert decoded.n_frames==16 and duration==[30]*16
 checks.append({'path':gif.name,'sha256':sha(gif),'frames':16,'duration_ms':duration,'cycle_ms':sum(duration)})
 seam=Image.new('RGB',(3072,600),color);sd=ImageDraw.Draw(seam)
 feet=Image.new('RGB',(6144,440),color);fd=ImageDraw.Draw(feet)
 for col,n in enumerate((12,13,14,15,16,1)):
  im=frames[n-1];small=im.resize((512,512),Image.Resampling.LANCZOS);seam.paste(small,(col*512,48),small);sd.text((col*512+12,16),f'SW{n:02d}',fill=text);patch=im.crop((0,650,1024,1024));feet.paste(patch,(col*1024,48),patch);fd.text((col*1024+12,16),f'SW{n:02d}',fill=text)
 seam.save(OUT/f'SW-seam12-13-14-15-16-01-{name}.png');feet.save(OUT/f'SW-feet12-13-14-15-16-01-{name}.png')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>04 SW 16帧审计</title><style>body{background:#eee9dc;color:#173833;font:16px system-ui;margin:24px}button,select{font:inherit;margin:6px;padding:8px}canvas{background:#20262e;display:block;width:min(80vw,720px);height:auto}#frames{max-width:850px}pre{white-space:pre-wrap;max-width:1100px}</style><h1>04 山岳守卫 · SW 16真实帧审计（未批准）</h1><p>30ms/帧，480ms/圈。旧512帧仅按相同世界尺寸显示；素材字节不放大改写。SW14/15/16为独立staging，尚未写入canonical。</p><button id="play">播放</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="30">30 ms / 帧</option><option value="120">120 ms / 帧诊断</option></select><select id="bg"><option value="#20262e">深底</option><option value="#f0eee4">浅底</option></select><select id="size"><option value="720">720 显示</option><option value="1024">1024 世界像素</option></select><canvas id="canvas" width="1024" height="1024"></canvas><div id="frames"></div><pre id="info"></pre><script>const data=__DATA__,c=document.getElementById('canvas'),ctx=c.getContext('2d'),play=document.getElementById('play'),speed=document.getElementById('speed'),info=document.getElementById('info');let frame=0,playing=false,last=0,elapsed=0;const ims=data.map(r=>{let i=new Image();i.src=r.image;return i}),buttons=data.map((r,i)=>{let b=document.createElement('button');b.textContent=String(r.frame).padStart(2,'0');b.onclick=()=>{frame=i;draw()};document.getElementById('frames').appendChild(b);return b});function draw(){ctx.clearRect(0,0,1024,1024);ctx.drawImage(ims[frame],0,0,1024,1024);let r=data[frame];info.textContent='SW'+String(r.frame).padStart(2,'0')+' | '+r.native_output_size.join('×')+' | '+r.source_kind+'\\nSHA256 '+r.sha256+'\\n'+r.source;buttons.forEach((b,i)=>b.style.background=i===frame?'#a4cdc1':'')}play.onclick=()=>{playing=!playing;play.textContent=playing?'暂停':'播放';elapsed=0};document.getElementById('prev').onclick=()=>{frame=(frame+15)%16;draw()};document.getElementById('next').onclick=()=>{frame=(frame+1)%16;draw()};document.getElementById('bg').onchange=e=>c.style.background=e.target.value;document.getElementById('size').onchange=e=>c.style.width=e.target.value+'px';function tick(t){if(last&&playing){elapsed+=t-last;let ms=+speed.value;if(elapsed>=ms){let step=Math.floor(elapsed/ms);frame=(frame+step)%16;elapsed-=step*ms;draw()}}last=t;requestAnimationFrame(tick)}Promise.all(ims.map(i=>i.decode())).then(()=>{draw();requestAnimationFrame(tick)});</script></html>'''.replace('__DATA__',json.dumps(rows,ensure_ascii=False))
(OUT/'index.html').write_text(html,encoding='utf-8')
for row in rows:del row['image']
scales=[r['body_scale'] for r in rows]
(OUT/'preview-manifest.json').write_text(json.dumps({'created_at_utc':datetime.now(timezone.utc).isoformat(),'character':CHAR,'direction':'SW','status':'visual_review_pending','runtime_assembly':False,'canonical_written':False,'frame_duration_ms':30,'frames':rows,'body_scale_cv':float(np.std(scales)/np.mean(scales)),'gif_validation':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT),'frames':16,'cycle_ms':480,'body_scale_cv':float(np.std(scales)/np.mean(scales))}))
