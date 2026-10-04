from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib,os
base=Path(__file__).resolve().parents[1]
rp=base/'review'
sel=json.loads((rp/'run-E-selection.json').read_text(encoding='utf-8'))
frames=[]
sheet=Image.new('RGB',(1536,1632),(232,230,222)); d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for i,f in enumerate(sel['frames']):
 p=Path(f['path']); im=Image.open(p).convert('RGBA')
 f['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 f['nativeSize']=list(im.size)
 f['alphaExtrema']=list(im.getchannel('A').getextrema())
 tile=im.resize((384,384),Image.Resampling.LANCZOS)
 x=i%4*384; y=i//4*408
 sheet.paste(tile,(x,y+24),tile)
 d.text((x+8,y+2),str(i+1).zfill(2)+(' NEW' if f['origin'].startswith('new') else ' prior'),font=font,fill=(30,35,45))
 frames.append({'n':i+1,'src':os.path.relpath(p,rp).replace(os.sep,'/'),'origin':f['origin']})
sheet.save(rp/'run-E-contact.png')
(rp/'run-E-selection.json').write_text(json.dumps(sel,ensure_ascii=False,indent=2),encoding='utf-8')
data=json.dumps(frames,ensure_ascii=False).replace('<','\\u003c')
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>07 E向跑步候选连播</title><style>body{font:16px system-ui;background:#20232c;color:#eee;margin:24px}main{display:flex;gap:24px}.stage{width:min(70vh,650px);aspect-ratio:1;background:repeating-conic-gradient(#bbb 0% 25%,#ddd 0% 50%) 0 0/32px 32px;position:relative}.stage img{width:100%;height:100%;object-fit:contain}.line{position:absolute;top:94%;left:0;right:0;border-top:1px dashed red;pointer-events:none}button,select{padding:9px;margin:4px}input{width:260px}small{display:block;max-width:420px;margin:15px 0;color:#bbb}a{color:#abcfff}</style><h1>07 月影少女 · E向跑步16候选</h1><p>真实原生1254画布统一显示；不是正式1024导出。03/11/12为本轮修正，其余复用本机旧图。未声明动态通过。</p><main><div class="stage"><img id="sprite"><div class="line"></div></div><section><h2 id="label"></h2><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><br><select id="speed"><option value="30">正常 30ms/帧 · 480ms/圈</option><option value="120">1/4慢放 120ms/帧</option></select><br><input id="slider" type="range" min="1" max="16" value="1"><p id="loaded"></p><small>红线为固定94%虚拟地面。全帧统一比例；未做逐帧包围盒缩放、最低脚贴地、插值或镜像。E13相位及全循环仍须实际观察。</small><a href="run-E-contact.png">查看联系表</a><br><a href="run-E-selection.json">候选来源清单</a></section></main><script>const frames=DATA;let idx=0,playing=true,timer;const images=frames.map(f=>{const x=new Image();x.src=f.src;return x});const sprite=document.getElementById('sprite'),label=document.getElementById('label'),slider=document.getElementById('slider'),speed=document.getElementById('speed');function show(){sprite.src=frames[idx].src;label.textContent='E '+String(idx+1).padStart(2,'0')+' / 16';slider.value=idx+1}function reset(){clearInterval(timer);timer=setInterval(()=>{if(playing){idx=(idx+1)%16;show()}},Number(speed.value))}document.getElementById('play').onclick=()=>{playing=!playing;document.getElementById('play').textContent=playing?'暂停':'播放'};document.getElementById('prev').onclick=()=>{playing=false;idx=(idx+15)%16;show()};document.getElementById('next').onclick=()=>{playing=false;idx=(idx+1)%16;show()};slider.oninput=()=>{playing=false;idx=Number(slider.value)-1;show()};speed.onchange=reset;Promise.all(images.map(x=>x.decode())).then(()=>{document.getElementById('loaded').textContent='16 / 16 图片加载完成';show();reset()}).catch(e=>{playing=false;document.getElementById('loaded').textContent='图片加载失败：'+e;});</script></html>'''.replace('DATA',data)
(rp/'run-E-preview.html').write_text(html,encoding='utf-8')
print(json.dumps({'frames':len(frames),'contact':str(rp/'run-E-contact.png'),'preview':str(rp/'run-E-preview.html')}))

