from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"provenance"/"hit"
frames={}
for direction in ("E","W"):
 paths=[ROOT/"frames"/"hit"/direction/("frame_%02d.png"%i) for i in range(1,7)]
 if not all(p.exists() for p in paths): continue
 rgba=[Image.open(p).convert("RGBA") for p in paths]
 preview=[]
 sheet=Image.new("RGB",(1152,824),(40,45,50))
 draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(rgba):
  tile=Image.new("RGBA",(384,384),(219,222,224,255));d=ImageDraw.Draw(tile)
  for y in range(0,384,24):
   for x in range(0,384,24):
    if (x//24+y//24)%2==0:d.rectangle((x,y,x+23,y+23),fill=(238,239,239,255))
  tile.alpha_composite(im.resize((384,384),Image.Resampling.LANCZOS))
  d=ImageDraw.Draw(tile);d.line((185,348,199,348),fill=(50,120,160,255),width=1);d.line((192,341,192,355),fill=(50,120,160,255),width=1)
  x=(i%3)*384;y=(i//3)*412
  sheet.paste(tile.convert("RGB"),(x,y+28))
  draw.text((x+12,y+8),direction+" "+str(i+1).zfill(2)+" / 40ms",fill=(245,245,245))
  preview.append(tile.convert("RGB"))
 sheet.save(OUT/("hit_"+direction+"_contact.png"))
 for name,ms in (("normal",40),("slow",160)):
  preview[0].save(OUT/("hit_"+direction+"_"+name+".gif"),save_all=True,append_images=preview[1:],duration=ms,loop=0,disposal=2)
 frames[direction]=[p.relative_to(ROOT).as_posix() for p in paths]
payload=json.dumps(frames)
html='''<!doctype html><meta charset="utf-8"><title>04 山岳守卫 · 受击检查</title><style>body{margin:24px;font:16px system-ui;background:#20272b;color:#eee}button,select{font:inherit;padding:8px;margin-right:8px}#stage{width:min(80vw,650px);aspect-ratio:1;background:repeating-conic-gradient(#ddd 0 25%,#f0f0f0 0 50%) 0/32px 32px;position:relative}img{width:100%;height:100%;object-fit:contain}#status{padding:12px 0}p{max-width:800px}</style><h1>04 山岳守卫 · 受击</h1><p>原样画布播放，每帧 40ms，每段 240ms；慢速每帧 160ms。未调整脚底或包围盒。此页供动态与逐帧检查，素材未接客户端。</p><select id="dir"><option>E</option><option>W</option></select><select id="speed"><option value="40">正常 40ms</option><option value="160">慢速 160ms</option></select><button id="play">播放/暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><button id="restart">从头播放一遍</button><div id="status"></div><div id="stage"><img id="sprite"></div><script>const files=PAYLOAD;let index=0,playing=false,timer=null;const dir=document.querySelector('#dir'),speed=document.querySelector('#speed'),img=document.querySelector('#sprite'),status=document.querySelector('#status');function show(){const a=files[dir.value]||[];if(!a.length){status.textContent='该方向未齐';return}img.src='../../'+a[index];status.textContent=dir.value+' 第 '+(index+1)+' / '+a.length+' 帧 · '+speed.value+'ms/帧'}function stop(){playing=false;clearInterval(timer)}function start(loop=true){stop();playing=true;timer=setInterval(()=>{const a=files[dir.value]||[];if(index===a.length-1&&!loop){stop();return}index=(index+1)%a.length;show()},Number(speed.value))}document.querySelector('#play').onclick=()=>playing?stop():start();document.querySelector('#prev').onclick=()=>{stop();index=(index+5)%6;show()};document.querySelector('#next').onclick=()=>{stop();index=(index+1)%6;show()};document.querySelector('#restart').onclick=()=>{index=0;show();start(false)};dir.onchange=()=>{stop();index=0;show()};speed.onchange=()=>{if(playing)start();show()};show();</script>'''.replace("PAYLOAD",payload)
(OUT/"hit_preview.html").write_text(html,encoding="utf-8")
print(json.dumps({"directions":list(frames),"frames":sum(len(v) for v in frames.values()),"output":str(OUT)},ensure_ascii=False))

