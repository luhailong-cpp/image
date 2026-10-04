from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selections={d:json.loads((ROOT/f).read_text(encoding='utf-8-sig')) for d,f in [('E','hit-selection.json'),('W','hit-W-selection.json')]}
data={}
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
for d,s in selections.items():
 fs=sorted([x for x in s['frames'] if x['direction']==d],key=lambda x:x['frame'])
 ims=[Image.open(ROOT/f['source']).convert('RGBA') for f in fs]
 refs=[{'source':f['source'],'sha256':sha(ROOT/f['source']),'generationRecord':f['generationRecord']} for f in fs]
 data[d]=[{'url':'../'+f['source'],'frame':f['frame'],'file':f['source']} for f in fs]
 sheet=Image.new('RGB',(1350,984),(229,227,217));draw=ImageDraw.Draw(sheet)
 for j,im in enumerate(ims):
  tile=im.resize((450,450),Image.Resampling.LANCZOS)
  sheet.paste(tile,((j%3)*450,(j//3)*492),tile)
  draw.text(((j%3)*450+16,(j//3)*492+454),f'{d}{j+1:02d} | '+fs[j]['source'].split('/')[-1],font=font,fill=(35,65,60))
 p=OUT/f'hit-review-{d}-contact.png';sheet.save(p)
 for speed,ms in [('normal',40),('slow',160)]:
  animation=[im.resize((640,640),Image.Resampling.LANCZOS) for im in ims]
  ap=OUT/f'hit-review-{d}-{speed}.png'
  animation[0].save(ap,save_all=True,append_images=animation[1:],duration=ms,loop=0,disposal=0,blend=0)
  meta={'file':ap.relative_to(ROOT).as_posix(),'sha256':sha(ap),'derivedFrom':refs,'operation':'仅预览：完整原生画布统一缩至640，无逐帧裁切、位移或包围盒缩放','frameMs':ms,'notGameExport':True}
  Path(str(ap)+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 Path(str(p)+'.generation.json').write_text(json.dumps({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'derivedFrom':refs,'operation':'接触表：完整原生画布统一450缩略后排版，不修改源图','notGameExport':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
template="""<!doctype html><html lang="zh"><meta charset="utf-8"><title>20星阵少女 · 受击逐帧复核</title>
<style>body{background:#183331;color:#fff3d3;font:18px system-ui;padding:20px}button,select,input{font:inherit;margin:5px}main{display:flex;flex-wrap:wrap;gap:24px}.panel{width:520px}canvas{width:100%;background:#e5e3d9}h1{font-size:24px}p{line-height:1.5}.file{font-size:12px;word-break:break-all;color:#b8d0c3}</style>
<h1>20 星阵少女 · 受击 E/W 复核</h1><p>整幅原生画布统一显示；原图无裁切、无挪脚。双脚与髋部参考线仅用于观察。</p>
<button id="play">暂停</button><select id="speed"><option value="40">正常 · 40 ms/帧</option><option value="160">慢速 · 160 ms/帧</option></select>
<button id="prev">上一帧</button><button id="next">下一帧</button><label>帧 <input type="range" id="scrub" min="0" max="5" value="0"></label><span id="frame"></span>
<main><section class="panel"><h2>E · 右向</h2><canvas id="E" width="1254" height="1254"></canvas><p class="file" id="fileE"></p></section><section class="panel"><h2>W · 左向</h2><canvas id="W" width="1254" height="1254"></canvas><p class="file" id="fileW"></p></section></main>
<script>const records=__DATA__;let index=0,playing=true,duration=40,last=0;const loaded={};Promise.all(['E','W'].flatMap(d=>{loaded[d]=[];return records[d].map((f,i)=>new Promise(r=>{const im=new Image();im.onload=()=>{loaded[d][i]=im;r()};im.src=f.url}))})).then(()=>{paint();requestAnimationFrame(tick)});
function paint(){for(const d of ['E','W']){const c=document.getElementById(d),ctx=c.getContext('2d');ctx.clearRect(0,0,1254,1254);ctx.drawImage(loaded[d][index],0,0,1254,1254);ctx.strokeStyle='#1f9c91aa';ctx.lineWidth=2;ctx.setLineDash([8,7]);ctx.beginPath();ctx.moveTo(627,0);ctx.lineTo(627,1254);ctx.moveTo(0,1196);ctx.lineTo(1254,1196);ctx.stroke();ctx.setLineDash([]);document.getElementById('file'+d).textContent=records[d][index].file}document.getElementById('frame').textContent=(index+1)+' / 6';document.getElementById('scrub').value=index;}
function tick(t){if(playing&&t-last>=duration){index=(index+1)%6;paint();last=t}requestAnimationFrame(tick)}
function pause(){playing=false;document.getElementById('play').textContent='播放'}
document.getElementById('play').onclick=()=>{playing=!playing;document.getElementById('play').textContent=playing?'暂停':'播放';last=performance.now()};
document.getElementById('speed').onchange=e=>duration=+e.target.value;
document.getElementById('prev').onclick=()=>{pause();index=(index+5)%6;paint()};
document.getElementById('next').onclick=()=>{pause();index=(index+1)%6;paint()};
document.getElementById('scrub').oninput=e=>{pause();index=+e.target.value;paint()};
</script></html>"""
(OUT/'hit-review-player.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False)),encoding='utf-8')
print(json.dumps({'previewFiles':[p.name for p in OUT.glob('hit-review-*')],'selected':{d:[f['file'] for f in v] for d,v in data.items()}},ensure_ascii=False))


