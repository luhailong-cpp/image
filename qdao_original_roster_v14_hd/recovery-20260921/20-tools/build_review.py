"""Build exact 30ms offline review from exported real frames; missing slots stay missing."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent.parent
P=R/'20-work/export-v1/20_star_formation_master_girl'
O=R/'20-delivery-preview';O.mkdir(exist_ok=True)
dirs=['N','NE','E','SE','S','SW','W','NW'];data={};checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in dirs:
    paths=[P/f'walk/{d}/{n:02d}.png' for n in range(1,17)]
    idle_path=P/f'idle/{d}.png'
    data[d]={'walk':[f'../20-work/export-v1/20_star_formation_master_girl/walk/{d}/{n:02d}.png?v={sha(p)[:16]}' if p.exists() else None for n,p in enumerate(paths,1)],
             'idle':f'../20-work/export-v1/20_star_formation_master_girl/idle/{d}.png?v={sha(idle_path)[:16]}' if idle_path.exists() else None}
    present=[p for p in paths if p.exists()]
    if not present:continue
    for mode,color in [('dark',(27,33,43)),('light',(245,241,230))]:
        tiles=[];contact=Image.new('RGB',(2048,2208),color);draw=ImageDraw.Draw(contact)
        for index,p in enumerate(paths):
            tile=Image.new('RGB',(512,512),color)
            if p.exists():
                im=Image.open(p).convert('RGBA');assert im.size==(1024,1024)
                im.thumbnail((512,512),Image.Resampling.LANCZOS);tile.paste(im,(0,0),im)
            else:ImageDraw.Draw(tile).text((190,245),'MISSING',fill='gray')
            x=index%4*512;y=index//4*552
            contact.paste(tile,(x,y+28));draw.text((x+10,y+8),f'{d} {index+1:02d}',fill='white' if mode=='dark' else 'black');tiles.append(tile)
        contact.save(O/f'{d}-contact-{mode}.png')
        if len(present)==16:
            fp=O/f'{d}-30ms-{mode}.gif';tiles[0].save(fp,save_all=True,append_images=tiles[1:],duration=[30]*16,loop=0,disposal=2,optimize=False)
            with Image.open(fp) as check:
                durations=[]
                for i in range(check.n_frames):check.seek(i);durations.append(check.info['duration'])
                assert check.n_frames==16 and durations==[30]*16
            checks.append({'path':fp.name,'sha256':sha(fp),'frames':16,'durations':durations,'cycleMs':480})
manifest={'at':datetime.now(timezone.utc).isoformat(),'character':'20_star_formation_master_girl','frameMs':30,'cycleMs':480,
    'walkCount':sum(sum(bool(x) for x in v['walk']) for v in data.values()),'idleCount':sum(bool(v['idle']) for v in data.values()),
    'directions':data,'gifChecks':checks,'visualApproval':False,'clientValidation':False}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>20 星阵少女 · 动作审阅</title>
<style>body{margin:20px;font:16px system-ui;background:#eee9de;color:#253d36}header{position:sticky;top:0;padding:12px;background:#eee9def0;z-index:3}button,select,input{margin:5px;padding:7px}main{display:flex;flex-wrap:wrap;gap:12px}article{border:1px solid #89968b;padding:10px}canvas{background:#1b212b;display:block;width:256px;height:256px}h1{font-size:24px}p{margin:6px 0}.missing{color:#a74032}</style>
<header><h1>20 星阵少女 · 动作审阅</h1><p id="status"></p><p>待美术验收；30毫秒/帧，16帧/圈，480毫秒/圈。缺帧不会用其他姿势填补。</p>
<button id="play">播放</button><button id="prev">上一帧</button><button id="next">下一帧</button><input id="frame" type="range" min="1" max="16" value="1"><b id="num">01</b>
<select id="bg"><option value="#1b212b">深底</option><option value="#f5f1e6">浅底</option></select>
<select id="zoom"><option value="256">256正常</option><option value="512">512放大</option><option value="1024">1024原尺寸</option></select>
<select id="direction"><option value="all">八方向</option></select><button id="idle">站立 / 行走</button><button id="seam">接缝15→16→01→02</button></header><main></main>
<script>const M=__DATA__,D=M.directions,C={},I={};let playing=false,frame=0,start=0,isIdle=false,seam=false;const main=document.querySelector('main');
document.querySelector('#status').textContent=`当前候选：${M.walkCount}/128 行走，${M.idleCount}/8 站立`;
for(const [d,v] of Object.entries(D)){document.querySelector('#direction').add(new Option(d,d));let a=document.createElement('article');a.dataset.dir=d;a.innerHTML=`<b>${d}</b><p>${v.walk.filter(Boolean).length}/16 行走 · 站立${v.idle?'有':'缺'}</p><canvas width="1024" height="1024"></canvas>`;main.append(a);C[d]=a.querySelector('canvas');I[d]={walk:v.walk.map(p=>{if(!p)return null;let im=new Image();im.src=p;im.onload=draw;return im}),idle:null};if(v.idle){I[d].idle=new Image();I[d].idle.src=v.idle;I[d].idle.onload=draw}}
function draw(){for(const [d,c]of Object.entries(C)){const x=c.getContext('2d');x.clearRect(0,0,1024,1024);let im=isIdle?I[d].idle:I[d].walk[frame];if(im&&im.complete&&im.naturalWidth)x.drawImage(im,0,0);else{x.fillStyle='#9b9b9b';x.font='32px system-ui';x.fillText('缺少当前帧',370,500)}}document.querySelector('#frame').value=frame+1;document.querySelector('#num').textContent=String(frame+1).padStart(2,'0')}
function stop(){playing=false;document.querySelector('#play').textContent='播放'}
document.querySelector('#play').onclick=()=>{playing=!playing;start=performance.now()-frame*30;document.querySelector('#play').textContent=playing?'暂停':'播放'};
document.querySelector('#prev').onclick=()=>{stop();frame=(frame+15)%16;draw()};document.querySelector('#next').onclick=()=>{stop();frame=(frame+1)%16;draw()};document.querySelector('#frame').oninput=e=>{stop();frame=+e.target.value-1;draw()};
document.querySelector('#bg').onchange=e=>Object.values(C).forEach(c=>c.style.background=e.target.value);document.querySelector('#zoom').onchange=e=>Object.values(C).forEach(c=>{c.style.width=c.style.height=e.target.value+'px'});document.querySelector('#direction').onchange=e=>document.querySelectorAll('article').forEach(a=>a.hidden=e.target.value!=='all'&&a.dataset.dir!==e.target.value);
document.querySelector('#idle').onclick=()=>{isIdle=!isIdle;draw()};document.querySelector('#seam').onclick=()=>{seam=!seam;playing=true;start=performance.now();document.querySelector('#play').textContent='暂停'};
function tick(t){if(playing){const i=Math.floor((t-start)/30);frame=seam?[14,15,0,1][i%4]:i%16;draw()}requestAnimationFrame(tick)}draw();requestAnimationFrame(tick);window.review={manifest:M,setFrame:n=>{stop();frame=n-1;draw()}};
</script></html>'''
(O/'index.html').write_text(html.replace('__DATA__',json.dumps(manifest,ensure_ascii=False)),encoding='utf8')
print(json.dumps({'walk':manifest['walkCount'],'idle':manifest['idleCount'],'exact30msGifs':len(checks),'visualApproval':False}))
