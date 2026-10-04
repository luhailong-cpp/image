from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'run/W/preview'
OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
contact=Image.new('RGB',(4*320,4*354),(232,235,239)); d=ImageDraw.Draw(contact)
for i in range(1,17):
 p=BASE/'run/W'/f'{i:02}.png'; im=Image.open(p).convert('RGBA'); rec=Path(str(p)+'.generation.json'); r=json.loads(rec.read_text(encoding='utf-8')); assert im.size==(1024,1024) and sha(p)==r['sha256']
 x=((i-1)%4)*320; y=((i-1)//4)*354
 tile=Image.new('RGBA',(320,320),(224,228,236,255)); tile.alpha_composite(im.resize((320,320),Image.Resampling.LANCZOS))
 contact.paste(tile.convert('RGB'),(x,y+30)); d.text((x+8,y+8),f'W{i:02}',fill=(15,22,39)); d.line((x+176,y+30,x+176,y+350),fill=(210,90,90),width=1); d.line((x,y+324,x+320,y+324),fill=(90,140,190),width=1)
 files.append({'frame':i,'path':p.relative_to(BASE).as_posix(),'sha256':sha(p),'generationRecord':rec.relative_to(BASE).as_posix(),'nativeSize':r['nativeSize'],'rgba':True,'alphaBBox8':im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox(),'visualApproved':False})
assert len({x['sha256'] for x in files})==16
contact.save(OUT/'contact.jpg',quality=94)
html='''<!doctype html><meta charset="utf-8"><title>角色14 run W16 审核</title><style>body{font:16px system-ui;background:#182131;color:#eaf0ff;margin:24px}button,select,input{font:inherit;margin:6px}canvas{width:min(65vw,700px);height:auto;background:repeating-conic-gradient(#dae0e8 0 25%,#edf1f7 0 50%) 50% / 32px 32px;display:block} .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.grid img{width:100%;background:#dae0e8}p{max-width:900px}</style><h1>14 唤雪少女 · run W · 16 帧</h1><p>审核预览。红线为 x563，蓝线为虚拟地面 y942；它们不是自动校正。检查两腿换脚、两手与狐/晶、头部比例及首尾。当前全组动态验收和根点注册待完成。</p><button id="play">暂停</button><select id="speed"><option value="60">正常 60ms/帧</option><option value="180">慢速 180ms/帧</option><option value="400">逐帧观察 400ms/帧</option></select><input id="slider" type="range" min="0" max="15" value="0"><b id="label"></b><canvas id="c" width="1024" height="1024"></canvas><div class="grid" id="grid"></div><script>let imgs=Array.from({length:16},(_,i)=>{let im=new Image;im.src='../'+String(i+1).padStart(2,'0')+'.png';return im}), f=0,playing=true,last=0;let ctx=c.getContext('2d');function draw(){ctx.clearRect(0,0,1024,1024);ctx.drawImage(imgs[f],0,0);ctx.strokeStyle='#df657e88';ctx.beginPath();ctx.moveTo(563,0);ctx.lineTo(563,1024);ctx.stroke();ctx.strokeStyle='#43aadd99';ctx.beginPath();ctx.moveTo(0,942);ctx.lineTo(1024,942);ctx.stroke();slider.value=f;label.textContent='W'+String(f+1).padStart(2,'0')}function tick(t){if(playing&&t-last>Number(speed.value)){f=(f+1)%16;last=t;if(imgs[f].complete)draw()}requestAnimationFrame(tick)}play.onclick=()=>{playing=!playing;play.textContent=playing?'暂停':'播放'};slider.oninput=()=>{playing=false;f=Number(slider.value);play.textContent='播放';draw()};imgs.forEach((im,i)=>{let cell=document.createElement('div');cell.textContent='W'+String(i+1).padStart(2,'0');let thumb=im.cloneNode();cell.append(thumb);grid.append(cell)});imgs[0].onload=draw;requestAnimationFrame(tick);</script>'''
(OUT/'index.html').write_text(html,encoding='utf-8')
report={'recordedAt':datetime.now(timezone.utc).isoformat(),'scope':'run W01-16','files':files,'checks':{'count':16,'distinctSHA':16,'all1024RGBA':True,'modelQuality':'unconfirmed, target from config only','browserVerified':False,'rootRegistered':False},'observations':['Exactly two girl hands in each viewed image: anatomical left holds fox; right holds crystal, swing replaces rather than duplicates arm.','Two distinct flight portions in W05-08 and W13-16; no sole-based normalization applied.','Sequential-reference drift makes W07-15 hair/robe increasingly extended; W16 re-anchors canonical W01 and W idle. Needs targeted repair before final visual approval.','Actual pixel anatomy root pending integer translation review; x563/y942 are nominal prompt targets only.'],'preview':'run/W/preview/index.html','contact':'run/W/preview/contact.jpg','clientIntegrated':False}
(OUT/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':len(files),'contact':str(OUT/'contact.jpg'),'preview':str(OUT/'index.html')}))

