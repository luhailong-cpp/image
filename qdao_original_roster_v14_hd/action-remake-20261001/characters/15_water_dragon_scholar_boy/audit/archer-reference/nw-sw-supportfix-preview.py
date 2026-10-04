from pathlib import Path
import json,html
B=Path(__file__).resolve().parents[2]
s=json.loads((B/'audit/archer-reference/nw-sw-supportfix-selection.json').read_text(encoding='utf-8-sig'))
rows=[]
for r in s['rows']:
 p=Path(r['file']).relative_to(B).as_posix()
 rows.append({'slot':r['slot'],'src':'../../'+p,'key':r['candidateKey'],'stage':r['grounding']['spatialStage'],'foot':r['grounding']['supportFoot']})
template='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>15 西北西南接地复核</title>
<style>body{font:16px system-ui;background:#eef2ed;color:#193331;margin:24px}button,select,input{font:inherit;margin:4px;padding:8px}main{display:flex;gap:20px}canvas{width:400px;height:400px;background:#dce5df;border:1px solid #a7bcb4}pre{white-space:pre-wrap;max-width:850px}</style>
<h1>水龙书生 · 西北 / 西南候选复核</h1><p>固定16帧×75ms＝1200ms。仅私有候选，待主交付审核；客户端未接入。</p>
<button id="play">播放</button><button id="pause">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button>
<select id="speed"><option value="1">1× 正常</option><option value=".25">0.25× 慢速</option></select>
<input id="frame" type="range" min="1" max="16" value="1"><span id="num">01/16</span>
<main><section><h2>西北 NW</h2><canvas id="NW" width="1024" height="1024"></canvas><p id="NWlabel"></p></section><section><h2>西南 SW</h2><canvas id="SW" width="1024" height="1024"></canvas><p id="SWlabel"></p></section></main>
<pre id="status">加载中</pre><script>
const rows=DATA; let loaded=0,index=0,playing=false,last=0,carry=0;const assets={};
for(const r of rows){const im=new Image();im.onload=()=>{loaded++;draw()};im.onerror=()=>document.querySelector('#status').textContent='加载失败 '+r.src;im.src=r.src;assets[r.slot]=im;}
function draw(){for(const di of ['NW','SW']){const r=rows.find(r=>r.slot==='run/'+di+'/'+String(index+1).padStart(2,'0')),im=assets[r.slot],c=document.getElementById(di),ctx=c.getContext('2d');ctx.clearRect(0,0,1024,1024);if(im?.complete){if(im.naturalWidth===1254)ctx.drawImage(im,42,49,940,940);else ctx.drawImage(im,0,0,1024,1024);}document.getElementById(di+'label').textContent=(index+1)+' / 16 · '+r.foot+' 支撑 · '+r.stage;}
document.getElementById('num').textContent=String(index+1).padStart(2,'0')+'/16';document.getElementById('frame').value=index+1;document.getElementById('status').textContent=loaded+'/32 张已加载；固定全画布缩放，不按脚底贴地。';}
document.getElementById('play').onclick=()=>{playing=true;last=performance.now();carry=0;};document.getElementById('pause').onclick=()=>playing=false;
document.getElementById('prev').onclick=()=>{playing=false;index=(index+15)%16;draw()};document.getElementById('next').onclick=()=>{playing=false;index=(index+1)%16;draw()};
document.getElementById('frame').oninput=e=>{playing=false;index=+e.target.value-1;draw()};
function loop(t){if(playing&&loaded===32){carry+=(t-last)*+document.getElementById('speed').value;while(carry>=75){carry-=75;index=(index+1)%16;}draw();}last=t;requestAnimationFrame(loop)}requestAnimationFrame(loop);
</script></html>'''.replace('DATA',json.dumps(rows,ensure_ascii=False))
(B/'audit/archer-reference/nw-sw-supportfix-preview.html').write_text(template,encoding='utf-8')
print('private preview created')

