from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib
base=Path(__file__).parent.parent
html='''<!DOCTYPE html><meta charset="utf-8"><title>DIR 跑步检查</title>
<style>body{background:#e9e8e1;font:16px system-ui;margin:20px}canvas{width:480px;max-width:95vw}button,select{padding:8px;margin:4px}p{max-width:860px}</style>
<h2>DIR · 16 帧 × 75 ms = 1200 ms</h2><p>固定方向配准，虚拟根 (512,942)。此为离线检查，客户端位移匹配仍待验证。</p>
<button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button>
<label>速度<select id="speed"><option value="1">正常 1200 ms</option><option value="0.5">慢放 0.5×</option><option value="0.25">慢放 0.25×</option></select></label>
<label><input id="root" type="checkbox" checked>显示根点</label><p id="label">正在读取</p><canvas width="1024" height="1024"></canvas>
<script>
const frames=DATA,offset=OFFSET,ims=frames.map(f=>{const a=new Image();a.src=f.file;return a});
let ready=false,playing=true,elapsed=0,last=null,idx=0;
const q=s=>document.querySelector(s),ctx=q('canvas').getContext('2d');
function draw(){ctx.fillStyle='#e9e8e1';ctx.fillRect(0,0,1024,1024);if(ready)ctx.drawImage(ims[idx],offset[0],offset[1],860,860);if(q('#root').checked){ctx.strokeStyle='#bd5c43';ctx.beginPath();ctx.moveTo(500,942);ctx.lineTo(524,942);ctx.moveTo(512,930);ctx.lineTo(512,954);ctx.stroke()}q('#label').textContent=ready?(idx+1)+'/16 · '+frames[idx].phase:'缺帧或读取失败，整圈播放已禁用'}
function pause(){playing=false;q('#play').textContent='播放'}
q('#play').onclick=()=>{if(!ready)return;playing=!playing;elapsed=idx*75;q('#play').textContent=playing?'暂停':'播放'};
q('#prev').onclick=()=>{pause();idx=(idx+15)%16;draw()};
q('#next').onclick=()=>{pause();idx=(idx+1)%16;draw()};
Promise.all(ims.map(im=>new Promise((resolve,reject)=>{if(im.complete&&im.naturalWidth)resolve();else{im.onload=resolve;im.onerror=reject}}))).then(()=>{ready=frames.length===16;draw()}).catch(()=>{ready=false;pause();q('#play').disabled=true;draw()});
function tick(t){if(last!==null&&playing&&ready){elapsed+=(t-last)*Number(q('#speed').value);idx=Math.floor(elapsed/75)%16}last=t;draw();requestAnimationFrame(tick)}requestAnimationFrame(tick);
</script>'''
for direction,offset in [('W',[125,135]),('NW',[66,135])]:
 d=base/f'run-{direction}-work';sel=json.loads((d/'selection.json').read_text(encoding='utf8'));t=json.loads((d/'timing-grounding.json').read_text(encoding='utf8'))
 phases={f['slot']:f.get('phase','') for f in t.get('frames',t.get('phases',[]))}
 frames=[];sheet=Image.new('RGB',(1280,1392),'#e9e8e1');dr=ImageDraw.Draw(sheet)
 for i in range(1,17):
  p=base/sel['slots'][f'run/{direction}/{i:02d}'];im=Image.open(p).convert('RGBA')
  if im.size!=(1254,1254): raise ValueError(str(p))
  frames.append({'slot':i,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'phase':phases.get(i,''),'durationMs':75})
  c=Image.new('RGBA',(1024,1024));c.alpha_composite(im.resize((860,860),Image.Resampling.LANCZOS),tuple(offset));thumb=c.resize((320,320))
  x=(i-1)%4*320;y=(i-1)//4*348;sheet.paste(thumb,(x,y),thumb);rx=x+160;ry=y+942*320/1024
  dr.line((rx-10,ry,rx+10,ry),fill='#c25a40');dr.line((rx,ry-6,rx,ry+6),fill='#c25a40')
  dr.text((x+5,y+322),f'{i:02d} {p.stem}',fill='#222');dr.text((x+5,y+335),phases.get(i,''),fill='#555')
 if len({f['sha256'] for f in frames})!=16:raise ValueError('Nonunique sequence')
 for k in ['candidateCyclesMs','cyclesMs','equalFrameMs','uniformFrameMs','weighted720Ms','weighted720FrameMs','weightedTrialOnly','phaseWeights']:t.pop(k,None)
 t.update({'cycleMs':1200,'frameMs':75,'frameDurationsMs':[75]*16,'phaseWeightsApplied':False,'timingAuthority':'User explicitly requested 16 frames × 75ms =1200ms on 2026-10-03','frames':frames})
 if 'staticReview' in t:t['staticReview']=t['staticReview'].replace('Flight02-04 subtle, short-weighted.','Flight02-04 subtle, uniformly timed at 75ms.')
 (d/'timing-grounding.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
 (d/'grounding-preview.html').write_text(html.replace('DIR',direction).replace('DATA',json.dumps(frames)).replace('OFFSET',json.dumps(offset)),encoding='utf8')
 sheet.save(d/'contact-grounding.jpg',quality=95)
 (d/'contact-grounding.jpg.generation.json').write_text(json.dumps({'operation':'Diagnostic full-canvas fixed transform. No frame-wise resizing or foot alignment.','scale':860/1254,'offset':offset,'sources':frames},indent=2),encoding='utf8')
 review=d/'REVIEW_20261003.md';s=review.read_text(encoding='utf8')
 if direction=='W':
  # Avoid depending on Markdown quoting by replace one matching paragraph.
  s='\n\n'.join(('当前用户要求跑步16帧均为75ms，整圈1200ms。grounding-preview.html 仅保留此正常档、慢放、暂停和逐帧；不使用相位权重，缺帧禁播。战斗时长未改。' if ('提供同组' in p and 'grounding-preview.html' in p) else p) for p in s.split('\n\n'))
 else:
  s='\n\n'.join(('当前用户要求16帧均为75ms，整圈1200ms。timing-grounding.json 与 grounding-preview.html 已同步；不使用相位权重，保留慢放、暂停和逐帧，缺帧禁播。战斗时长未改。' if '相位、逐帧权重' in p else p) for p in s.split('\n\n'))
 review.write_text(s,encoding='utf8')
 print(direction, len(frames), 'unique16;1200ms;75ms;no weights')

