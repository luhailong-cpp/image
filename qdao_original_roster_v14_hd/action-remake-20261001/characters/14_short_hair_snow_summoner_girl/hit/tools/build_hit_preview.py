from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'hit/preview';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[BASE/'hit/W'/f'{i:02}.png' for i in range(1,7)]
canvas=Image.new('RGB',(6*280,310),(32,42,58));draw=ImageDraw.Draw(canvas)
gif=[]
for i,p in enumerate(files):
    im=Image.open(p).convert('RGBA')
    thumb=im.resize((280,280),Image.Resampling.LANCZOS);canvas.paste(thumb,(i*280,0),thumb)
    draw.text((i*280+8,289),f'W / {i+1:02}',fill='white')
    stage=Image.new('RGB',(512,512),(32,42,58));thumb=im.resize((512,512),Image.Resampling.LANCZOS);stage.paste(thumb,(0,0),thumb);gif.append(stage)
canvas.save(OUT/'hit-W-contact.jpg')
gif[0].save(OUT/'hit-W-normal.gif',save_all=True,append_images=gif[1:],duration=40,loop=0)
gif[0].save(OUT/'hit-W-slow.gif',save_all=True,append_images=gif[1:],duration=200,loop=0)
record={'usage':'Only viewing derived PNG frames. No pose synthesis.','frames':[{'file':p.relative_to(BASE).as_posix(),'sha256':sha(p)} for p in files],'normalDurationPerFrameMs':40,'segmentMs':240,'slowDurationPerFrameMs':200,'derivatives':[{'file':p.name,'sha256':sha(p)} for p in sorted(OUT.iterdir()) if p.suffix in ('.gif','.jpg')]}
(OUT/'hit-W-preview.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>14 受击 W 六帧</title><style>body{background:#182331;color:#ecf1ff;font:16px system-ui;margin:24px}button,select{font:inherit;padding:8px;margin:5px}#stage{width:512px;max-width:85vw;background:#202a3a}#stage.light{background:#eee}img{width:100%}.row{display:flex}.row img{width:180px}code{overflow-wrap:anywhere;font-size:11px}</style><h1>14 唤雪少女 · W 受击</h1><p>6 张独立姿态；40 ms/帧，240 ms/段。仅离线素材预览，未接入客户端。</p><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="40">正常 40 ms</option><option value="200">慢速 200 ms</option><option value="500">慢速 500 ms</option></select><button id="bg">深浅底</button><div id="label"></div><div id="stage"><img id="sprite"></div><code id="hash"></code><div class="row" id="row"></div><script>const files=__FILES__;let i=0,playing=true,last=0;function show(){document.querySelector('#sprite').src='../W/'+String(i+1).padStart(2,'0')+'.png';document.querySelector('#label').textContent='受击 W '+(i+1)+'/6';document.querySelector('#hash').textContent=files[i].sha256}function step(n){playing=false;i=(i+n+6)%6;show();document.querySelector('#play').textContent='播放'}document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'暂停':'播放'};document.querySelector('#bg').onclick=()=>document.querySelector('#stage').classList.toggle('light');for(let n=0;n<6;n++){let im=document.createElement('img');im.src='../W/'+String(n+1).padStart(2,'0')+'.png';im.onclick=()=>{i=n;playing=false;show()};document.querySelector('#row').append(im)}function loop(t){if(playing&&t-last>=Number(document.querySelector('#speed').value)){i=(i+1)%6;show();last=t}requestAnimationFrame(loop)}show();requestAnimationFrame(loop);</script></html>'''.replace('__FILES__',json.dumps(record['frames']))
(OUT/'hit-W.html').write_text(html,encoding='utf-8')
print('W preview ready with 6 real frames')
