from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[1]
S=json.loads((B/'attack-selection.json').read_text(encoding='utf-8'))
O=B/'preview';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={}
for direction in ['E','W']:
 rows=sorted([f for f in S['frames'] if f['direction']==direction],key=lambda x:x['frame'])
 ims=[]; inputs=[]
 for f in rows:
  src=B/f['source'];im=Image.open(src).convert('RGBA')
  canvas=Image.new('RGBA',(1024,1024))
  canvas.alpha_composite(im.resize((922,922),Image.Resampling.LANCZOS),(51,40))
  ims.append(canvas)
  inputs.append({'path':f['source'],'sha256':sha(src),'generationRecord':f['generationRecord']})
 for speed,ms in [('normal',30),('slow',150)]:
  p=O/f'attack-review-{direction}-{speed}.png'
  ims[0].save(p,save_all=True,append_images=ims[1:],duration=ms,loop=0,disposal=0,blend=0)
  (Path(str(p)+'.generation.json')).write_text(json.dumps({'file':str(p.relative_to(B)).replace('\\','/'),'sha256':sha(p),'derivedFrom':inputs,'operation':{'type':'APNG review preview','canvas':[1024,1024],'wholeSourceResize':[922,922],'offset':[51,40],'fixedPivot':[512,922],'durationMs':ms,'noBBoxNormalization':True,'noMinPixelFloorNormalization':True},'dynamicAcceptance':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 sheet=Image.new('RGB',(1440,1128),(236,232,221));d=ImageDraw.Draw(sheet)
 for i,im in enumerate(ims):
  x=(i%4)*360;y=(i//4)*376
  for gy in range(0,352,22):
   for gx in range(0,352,22):
    d.rectangle((x+4+gx,y+24+gy,x+4+gx+21,y+24+gy+21),fill=(224,223,218) if (gx//22+gy//22)%2 else (243,241,235))
  sm=im.resize((352,352),Image.Resampling.LANCZOS)
  sheet.paste(sm,(x+4,y+24),sm)
  d.text((x+8,y+5),f'{direction} {i+1:02d}',fill=(0,0,0))
  d.line((x+180,y+335,x+180,y+347),fill=(220,0,80),width=2)
 p=O/f'attack-review-{direction}-contact.png';sheet.save(p)
 Path(str(p)+'.generation.json').write_text(json.dumps({'file':str(p.relative_to(B)).replace('\\','/'),'sha256':sha(p),'derivedFrom':inputs,'operation':{'type':'contact-sheet review only','wholeSourceResize':[922,922],'offset':[51,40],'fixedPivot':[512,922],'noBBoxNormalization':True}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 manifest[direction]=[{'src':'../'+r['source'],'frame':r['frame']} for r in rows]
html='''<!doctype html><meta charset="utf-8"><title>普攻连续性检查</title><style>body{background:#e8e4d8;font:16px sans-serif;margin:20px}main{display:flex;gap:16px}.pane{background:#d9d9d4}.stage{position:relative;width:480px;height:480px;background:repeating-conic-gradient(#e7e7e3 0 25%,#f4f4ef 0 50%) 0/32px 32px}.sprite{position:absolute;width:432.1875px;height:432.1875px;left:23.90625px;top:18.75px}.ground{position:absolute;top:432.1875px;width:100%;border-top:1px solid #d5787899}.root{position:absolute;left:240px;top:432.1875px;color:#d40066;font-weight:bold}.label{text-align:center;padding:8px}button,select{padding:8px;margin-right:8px}</style><h2>星阵少女 · 普攻固定画布连续性检查</h2><p>共用整图缩放 922×922 / 偏移 (51,40) / 固定锚点 (512,922)，没有逐帧贴底。红线只用于观察。</p><p><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="30">正常 30 ms</option><option value="150">慢速 150 ms</option></select><span id="position"></span></p><main><section class="pane"><div class="label">E</div><div class="stage"><div class="ground"></div><div class="root">+</div><img id="E" class="sprite"></div></section><section class="pane"><div class="label">W</div><div class="stage"><div class="ground"></div><div class="root">+</div><img id="W" class="sprite"></div></section></main><script>const frames=MANIFEST;let i=0,playing=true,timer;for(const dir of ['E','W'])for(const f of frames[dir]){let p=new Image();p.src=f.src;}function draw(){for(const dir of ['E','W'])document.getElementById(dir).src=frames[dir][i].src;document.getElementById('position').textContent='帧 '+String(i+1).padStart(2,'0')+' / 12';}function tick(){clearInterval(timer);timer=setInterval(()=>{if(playing){i=(i+1)%12;draw()}},Number(document.getElementById('speed').value))}document.getElementById('play').onclick=()=>{playing=!playing;document.getElementById('play').textContent=playing?'暂停':'播放'};for(const id of ['prev','next'])document.getElementById(id).onclick=()=>{playing=false;document.getElementById('play').textContent='播放';i=(i+(id==='next'?1:11))%12;draw()};document.getElementById('speed').onchange=tick;draw();tick()</script>'''
(O/'attack-review-index.html').write_text(html.replace('MANIFEST',json.dumps(manifest)),encoding='utf-8')
print('Wrote fixed-canvas attack review contact sheets, normal/slow APNG, interactive HTML')

