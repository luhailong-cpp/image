"""Build a read-only 30ms preview and mechanical checks for character 14."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np

REC=Path(__file__).resolve().parents[1];OUT=REC/'14-delivery-preview';ASSETS=OUT/'assets'
DIRS=['N','NE','E','SE','S','SW','W','NW']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 qa_path=OUT/'qa-summary.json';qa=json.loads(qa_path.read_text(encoding='utf-8')) if qa_path.is_file() else {}
 approved={x['file']:x['sha256'] for x in qa.get('assets',[]) if x.get('offlineApproved')}
 rows=[];missing=[];frames={d:[] for d in DIRS};idles={};seen={};dupes=[]
 for d in DIRS:
  for i in range(17):
   rel=f'idle/{d}.png' if i==0 else f'walk/{d}/{i:02d}.png';p=ASSETS/rel
   if not p.is_file():missing.append(rel);continue
   im=Image.open(p);a=np.asarray(im.convert('RGBA'));visible=a[:,:,3]>8;y,x=np.where(visible)
   digest=sha(p);side=Path(str(p)+'.generation.json');meta=json.loads(side.read_text(encoding='utf-8')) if side.is_file() else {}
   edge=visible.copy();edge[1:-1,1:-1]&=~(visible[:-2,1:-1]&visible[2:,1:-1]&visible[1:-1,:-2]&visible[1:-1,2:])
   rgb=a[:,:,:3].astype(int);hot=((rgb[:,:,0]-rgb[:,:,1]>80)&(rgb[:,:,2]-rgb[:,:,1]>80))|((rgb[:,:,2]-rgb[:,:,0]>120)&(rgb[:,:,2]-rgb[:,:,1]>120))
   row={'file':rel,'sha256':digest,'size':list(im.size),'mode':im.mode,'transparentFraction':float((a[:,:,3]==0).mean()),'bbox':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1],'sourceArchive':meta.get('sourceArchive'),'nativeSize':meta.get('nativeSize'),'sourceSHA256':meta.get('derivedFrom',{}).get('sha256'),'edgeHotColorPixels':int((edge&hot).sum()),'visualReview':'pending'}
   row['visualReview']='passed' if approved.get(rel)==digest else 'pending'
   rows.append(row)
   if digest in seen:dupes.append([seen[digest],rel])
   seen[digest]=rel
   if i:idles.setdefault(d,None);frames[d].append({'frame':i,'src':'assets/'+rel,'sha256':digest})
   else:idles[d]='assets/'+rel
 report={'character':'14_short_hair_snow_summoner_girl','generatedAt':datetime.now(timezone.utc).isoformat(),'walkCount':sum(len(v) for v in frames.values()),'idleCount':sum(v is not None for v in idles.values()),'expectedWalk':128,'expectedIdle':8,'missing':missing,'duplicatePixelFiles':dupes,'frameDurationMs':30,'cycleMs':480,'rows':rows,'artApproval':False,'clientValidated':False}
 report['artApproval']=len(rows)==136 and not missing and all(r['visualReview']=='passed' for r in rows)
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 data=json.dumps({'dirs':DIRS,'frames':frames,'idles':idles,'inventory':report},ensure_ascii=False)
 html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>14 唤雪少女 · 30ms八向检查</title><style>
 body{margin:0;background:#e9e4d7;color:#253d39;font:16px system-ui}header{padding:18px 24px;background:#164a40;color:#fff}h1{font-size:24px;margin:0 0 8px}button,select{padding:9px 13px;margin:4px;border:1px solid #91a89c;border-radius:7px;background:#fff;color:#25483b;cursor:pointer}button.active{background:#206250;color:#fff}main{padding:14px 24px}.controls{position:sticky;top:0;background:#e9e4d7;z-index:5;padding:8px}#stage{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}.sprite{background:#f8f5ed;border:1px solid #a8b3a7;position:relative;overflow:auto}#hero{display:block;object-fit:contain}#grid{display:grid;grid-template-columns:repeat(4,200px);gap:10px}figure{margin:0;text-align:center;background:#f8f5ed;border-radius:8px;padding:3px}figure img{width:192px;height:192px;object-fit:contain}figcaption{padding:4px}#seam{display:flex;gap:8px;flex-wrap:wrap}#seam img{width:240px;height:240px}.dark .sprite,.dark figure{background:#17232a}.check .sprite,.check figure{background:conic-gradient(#bbb 25%,#eee 0 50%,#bbb 0 75%,#eee 0) 0 0/20px 20px}#status{white-space:pre-wrap;max-width:1100px}small{color:#63746c}input{width:350px}@media(max-width:900px){#grid{grid-template-columns:repeat(2,150px)}figure img{width:144px;height:144px}}</style>
 <header><h1>14 · 唤雪少女</h1><div>8方向 × 16帧 · 30毫秒/帧 · 480毫秒/圈 · 独立站立图</div></header><main><div class="controls"><div id="directions"></div><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><button id="idle">站立 / 行走</button><select id="bg"><option value="">浅底</option><option value="dark">深底</option><option value="check">棋盘底</option></select><select id="zoom"><option value="256">正常 256</option><option value="512">放大 512</option><option value="1024">原尺寸 1024</option><option value="2048">2倍边缘检查</option></select><input id="frame" type="range" min="1" max="16" value="1"><span id="label"></span></div><div id="status"></div><section id="stage"><div class="sprite"><img id="hero" width="256" height="256"></div><div id="grid"></div></section><h2>当前方向首尾：15 → 16 → 01 → 02</h2><div id="seam"></div><p><small>本页仅证明本地素材和预览。美术通过需逐帧及连播复核；未进行Unity或正式客户端验收。</small></p></main><script>const D=__DATA__;
 let direction=D.dirs.includes(new URLSearchParams(location.search).get('dir'))?new URLSearchParams(location.search).get('dir'):'N',frame=1,playing=true,standing=false,start=performance.now();const $=id=>document.getElementById(id),imgs={};let loaded=0,failed=[];$('status').textContent='正在载入本地角色图…';
 const all=[...Object.values(D.frames).flat().map(x=>x.src),...Object.values(D.idles).filter(Boolean)];const promises=all.map(src=>new Promise(resolve=>{const im=new Image();imgs[src]=im;im.onload=()=>{loaded++;resolve()};im.onerror=()=>{failed.push(src);resolve()};im.src=src}));
 const src=(d,n)=>D.frames[d].find(x=>x.frame===n)?.src;const set=(el,s)=>{if(s&&el.getAttribute('src')!==s)el.src=s;if(!s)el.removeAttribute('src')};
 function seams(){ $('seam').innerHTML='';for(const n of [15,16,1,2]){const f=document.createElement('figure');const im=document.createElement('img');set(im,src(direction,n));f.append(im);const c=document.createElement('figcaption');c.textContent=direction+' '+String(n).padStart(2,'0');f.append(c);$('seam').append(f)}}
 function draw(){set($('hero'),standing?D.idles[direction]:src(direction,frame));$('frame').value=frame;$('label').textContent=direction+' / '+(standing?'独立站立':String(frame).padStart(2,'0'))+' / 30ms';for(const d of D.dirs)set($('dir-'+d),standing?D.idles[d]:src(d,frame));window.previewState={direction,frame,playing,standing,frameDurationMs:30,cycleMs:480,loaded,total:all.length,failed,selectedSrc:$('hero').getAttribute('src')};}
 for(const d of D.dirs){const b=document.createElement('button');b.textContent=d;b.onclick=()=>{direction=d;document.querySelectorAll('#directions button').forEach(e=>e.classList.toggle('active',e===b));seams();draw()};$('directions').append(b);const f=document.createElement('figure');f.innerHTML='<img id="dir-'+d+'"><figcaption>'+d+'</figcaption>';$('grid').append(f)}
 $('play').onclick=()=>{playing=!playing;start=performance.now()-(frame-1)*30;$('play').textContent=playing?'暂停':'播放'};for(const [id,delta] of [['prev',-1],['next',1]])$(id).onclick=()=>{playing=false;$('play').textContent='播放';frame=(frame-1+delta+16)%16+1;draw()};$('idle').onclick=()=>{standing=!standing;draw()};$('frame').oninput=e=>{playing=false;frame=+e.target.value;$('play').textContent='播放';draw()};$('zoom').onchange=e=>{$('hero').width=$('hero').height=+e.target.value};$('bg').onchange=e=>document.body.className=e.target.value;
 function tick(now){if(playing&&!standing){frame=Math.floor((now-start)/30)%16+1;draw()}requestAnimationFrame(tick)}Promise.all(promises).then(()=>{$('status').textContent=`行走 ${D.inventory.walkCount}/128，站立 ${D.inventory.idleCount}/8；图片加载 ${loaded}/${all.length}；缺槽 ${D.inventory.missing.length}。`+(D.inventory.artApproval?'离线验收通过。':'美术验收待完成。');seams();draw();requestAnimationFrame(tick)});
 </script></html>'''.replace('__DATA__',data)
 (OUT/'index.html').write_text(html,encoding='utf-8')
 review=OUT/'review-temp';review.mkdir(exist_ok=True)
 for d in DIRS:
  for tag,bg in [('light',(247,244,233)),('dark',(24,34,42))]:
   sheet=Image.new('RGB',(1024,1120),bg);draw=ImageDraw.Draw(sheet)
   for i in range(1,17):
    p=ASSETS/f'walk/{d}/{i:02d}.png';x=(i-1)%4*256;y=(i-1)//4*280
    if p.exists():im=Image.open(p).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+20),im)
    draw.text((x+8,y+4),f'{d} {i:02d}',fill='white' if tag=='dark' else 'black')
   sheet.save(review/f'{d}-contact-{tag}.jpg',quality=94)
 print(json.dumps({k:report[k] for k in ('walkCount','idleCount','duplicatePixelFiles','artApproval')}))
if __name__=='__main__':main()
