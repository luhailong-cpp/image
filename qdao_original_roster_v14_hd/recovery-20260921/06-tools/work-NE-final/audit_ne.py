from pathlib import Path
from datetime import datetime,timezone
import importlib.util,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;TOOLS=HERE.parent;ROOT=TOOLS.parents[1]
OUT=HERE/'candidate/06_thunder_caster_boy';REVIEW=HERE/'review';REVIEW.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
verify=mod('ne_verify',TOOLS/'alpha_verify.py');verify.ROOT=HERE;verify.mod=lambda name:mod('ne_vendor_'+name,ROOT/'tools/vendor'/f'{name}.py')
result=verify.verify('06_thunder_caster_boy','NE',False,None);write(REVIEW/'numeric-verification.json',result)
frames=[Image.open(OUT/f'walk/NE/{i:02d}.png').convert('RGBA') for i in range(1,17)]
files=[]
for i,im in enumerate(frames,1):
 a=np.asarray(im)[:,:,3];y,x=np.where(a>8);files.append({'frame':i,'path':str(OUT/f'walk/NE/{i:02d}.png'),'sha256':sha(OUT/f'walk/NE/{i:02d}.png'),'size':list(im.size),'alpha_bbox_gt8':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1],'edge_alpha_nonzero':int(np.count_nonzero(a[0])+np.count_nonzero(a[-1])+np.count_nonzero(a[:,0])+np.count_nonzero(a[:,-1]))})
gif_results=[]
for theme,color,fg in [('dark',(28,36,44),(255,255,255)),('light',(244,240,228),(15,25,30))]:
 compos=[]
 for i,im in enumerate(frames,1):
  canvas=Image.new('RGB',(512,548),color);canvas.paste(im.resize((512,512),Image.Resampling.LANCZOS),(0,30),im.resize((512,512),Image.Resampling.LANCZOS));ImageDraw.Draw(canvas).text((12,10),f'NE {i:02d}/16  30ms / 480ms loop',fill=fg);compos.append(canvas)
 gif=REVIEW/f'NE-{theme}-30ms.gif';compos[0].save(gif,save_all=True,append_images=compos[1:],duration=30,loop=0,disposal=2,optimize=False)
 g=Image.open(gif);dur=[]
 for k in range(g.n_frames):g.seek(k);dur.append(g.info.get('duration'))
 assert len(dur)==16 and dur==[30]*16
 gif_results.append({'file':gif.name,'sha256':sha(gif),'frames':len(dur),'durations_ms':dur,'total_ms':sum(dur)})
 contact=Image.new('RGB',(1024,1152),color)
 for j,im in enumerate(frames):
  small=im.resize((256,256),Image.Resampling.LANCZOS);x=(j%4)*256;y=(j//4)*288;contact.paste(small,(x,y+28),small);ImageDraw.Draw(contact).text((x+12,y+8),f'NE{j+1:02d}',fill=fg)
 contact.save(REVIEW/f'NE-contact-{theme}.png')
 seam=Image.new('RGB',(2048,1100),color)
 for j,n in enumerate([15,16,1,2]):
  im=frames[n-1].resize((512,512),Image.Resampling.LANCZOS);x=j*512;seam.paste(im,(x,32),im);ImageDraw.Draw(seam).text((x+20,8),f'NE{n:02d}',fill=fg)
  crop=frames[n-1].crop((270,680,880,1010)).resize((512,277),Image.Resampling.LANCZOS);seam.paste(crop,(x,640),crop)
 seam.save(REVIEW/f'NE-seam-{theme}.png')
write(REVIEW/'artifacts.json',{'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'manifest_sha256':sha(OUT/'manifest.json'),'files':files,'gifs':gif_results,'numeric':result,'visual_status':'pending','unity_client_verified':False})
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>06 雷法少年 NE 审核</title><style>body{font:16px system-ui;background:#d8d5ca;margin:20px}button,input{font:inherit;margin:6px}#views{display:flex;gap:16px;flex-wrap:wrap}.box{padding:8px}.dark{background:#1c242c;color:white}.light{background:#f4f0e4;color:#182026}canvas{display:block;width:384px;height:384px}.zoom canvas{width:768px;height:768px}p{max-width:1000px}</style><h1>06 雷法少年 · NE 16帧</h1><p>独立单帧原生1254，固定0.88导出1024。30毫秒/帧，480毫秒/圈。16→01接缝与深浅底复核；未进行Unity/客户端验收。</p><button id="play">暂停</button><button id="previous">上一帧</button><button id="next">下一帧</button><button id="seam">接缝15→16→01→02</button><button id="zoom">放大</button><input id="frame" aria-label="帧" type="range" min="1" max="16" value="1"><strong id="state"></strong><div id="views"><div class="box dark">深底<canvas width="1024" height="1024"></canvas></div><div class="box light">浅底<canvas width="1024" height="1024"></canvas></div></div><p><a href="NE-contact-dark.png">16帧深底</a> · <a href="NE-contact-light.png">16帧浅底</a> · <a href="NE-seam-dark.png">接缝放大</a></p><script>
const images=Array.from({length:16},(_,i)=>{const im=new Image();im.src='../candidate/06_thunder_caster_boy/walk/NE/'+String(i+1).padStart(2,'0')+'.png';return im});let n=1,playing=true,seam=false,last=0;const seq=[15,16,1,2];function draw(){for(const c of document.querySelectorAll('canvas')){const cx=c.getContext('2d');cx.clearRect(0,0,1024,1024);if(images[n-1].complete)cx.drawImage(images[n-1],0,0)}document.getElementById('state').textContent='NE '+String(n).padStart(2,'0')+' / 16 · '+(playing?'30ms 循环':'逐帧暂停')+(seam?' · 接缝模式':'');document.getElementById('frame').value=n}function tick(t){if(playing&&t-last>=30){const steps=Math.floor((t-last)/30);last=t-(t-last)%30;n=seam?seq[(Math.max(0,seq.indexOf(n))+steps)%4]:((n-1+steps)%16)+1;draw()}requestAnimationFrame(tick)}document.getElementById('play').onclick=()=>{playing=!playing;document.getElementById('play').textContent=playing?'暂停':'播放';draw()};document.getElementById('next').onclick=()=>{playing=false;n=n%16+1;draw()};document.getElementById('previous').onclick=()=>{playing=false;n=(n+14)%16+1;draw()};document.getElementById('seam').onclick=()=>{seam=!seam;n=15;draw()};document.getElementById('zoom').onclick=()=>document.getElementById('views').classList.toggle('zoom');document.getElementById('frame').oninput=e=>{playing=false;n=+e.target.value;draw()};Promise.all(images.map(i=>i.decode())).then(()=>{draw();requestAnimationFrame(tick)});
</script></html>'''
(REVIEW/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'numeric':result,'gifs':gif_results,'file_count':len(files)},ensure_ascii=False,indent=2))
