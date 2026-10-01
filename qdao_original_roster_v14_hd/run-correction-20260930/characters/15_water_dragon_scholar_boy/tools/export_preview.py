from pathlib import Path
import json, hashlib, datetime, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
DIRS=['N','NE','E','SE','S','SW','W','NW']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def build():
 # One transform for the entire character; never fit individual bboxes or lowest feet.
 transform={'canvas':[1024,1024],'normalized_source_size':[1254,1254],'resized_canvas':[940,940],'placement':[42,49],'source_virtual_ground_y':1191,'output_virtual_ground_y':942,'scale':940/1254,'per_frame_alignment':False,'per_frame_scale':False,'alpha_cleanup':'alpha <= 8 set to zero; no limb edits'}
 records=[]
 for d in DIRS:
  for n in range(1,17):
   src=ROOT/f'generation/{d}/{n:02}-v1.png'
   row={'direction':d,'frame':n,'expected':f'candidate/walk/{d}/{n:02}.png','status':'missing'}
   if src.exists():
    im=Image.open(src)
    provenance=Path(str(src)+'.generation.json')
    if min(im.size)<1024 or im.width!=im.height or im.mode!='RGBA' or not provenance.exists():
     row.update(status='ineligible_source',source=str(src.relative_to(ROOT)));records.append(row);continue
    rgba=im.convert('RGBA')
    rgba.putalpha(rgba.getchannel('A').point(lambda a:0 if a<=8 else a))
    dst=ROOT/row['expected'];dst.parent.mkdir(parents=True,exist_ok=True)
    out=Image.new('RGBA',(1024,1024))
    out.alpha_composite(rgba.resize((940,940),Image.Resampling.LANCZOS),(42,49))
    out.save(dst)
    bbox=out.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
    derivation={'file':str(dst.relative_to(ROOT)),'sha256':sha(dst),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','nativeSourceDimensions':list(im.size),'derivedFrom':[{'file':str(src.relative_to(ROOT)),'sha256':sha(src),'generationRecord':str(provenance.relative_to(ROOT))}],'operation':transform,'actualModel':None,'actualQuality':None,'acceptance':'unreviewed_candidate'}
    write(Path(str(dst)+'.generation.json'),derivation)
    row.update(status='candidate_unreviewed',file=row['expected'],sha256=sha(dst),source=str(src.relative_to(ROOT)),sourceSHA256=sha(src),sourceDimensions=list(im.size),provenance=str(provenance.relative_to(ROOT)),pixelSHA256=hashlib.sha256(out.tobytes()).hexdigest(),alpha_gt_8_bbox=bbox,lowestAlphaGt8=bbox[3]-1 if bbox else None,edgeAlphaMax=max(out.getchannel('A').crop((0,0,1024,1)).getextrema()[1],out.getchannel('A').crop((0,1023,1024,1024)).getextrema()[1],out.getchannel('A').crop((0,0,1,1024)).getextrema()[1],out.getchannel('A').crop((1023,0,1024,1024)).getextrema()[1]))
   records.append(row)
 manifest={'schemaVersion':1,'characterId':'15_water_dragon_scholar_boy','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expectedFrameCount':128,'candidateFrameCount':sum(r['status']=='candidate_unreviewed' for r in records),'visualAcceptedFrameCount':0,'dynamicAcceptedDirectionCount':0,'clientIntegrated':False,'runtimeTested':False,'frameDurationMs':30,'cycleDurationMs':480,'pivotNormalized':[.5,.08],'pixelsPerUnit':104,'exportTransform':transform,'frames':records}
 write(ROOT/'manifest.json',manifest)
 preview=ROOT/'preview';preview.mkdir(exist_ok=True)
 for d in DIRS:
  rows=[r for r in records if r['direction']==d and r['status']=='candidate_unreviewed']
  if not rows: continue
  sheet=Image.new('RGB',(1024,1104),'#dfebe9');draw=ImageDraw.Draw(sheet)
  for row in rows:
   i=row['frame']-1;x=(i%4)*256;y=(i//4)*276
   out=Image.open(ROOT/row['file']);thumb=out.resize((256,256),Image.Resampling.LANCZOS)
   sheet.paste(thumb,(x,y+20),thumb);draw.text((x+6,y+4),f"{d} {i+1:02}  / lowest {row['lowestAlphaGt8']}",fill='#142727')
   draw.line((x,y+20+round(942/4),x+256,y+20+round(942/4)),fill='#77a399')
  sheet.save(preview/f'{d}-contact.png')
  write(preview/f'{d}-contact.png.provenance.json',{'derivedFrom':[{'file':r['file'],'sha256':r['sha256']} for r in rows],'operation':'inspection montage only, 1/4 scale; not game frames'})
 assets={d:[('../'+r['file']) if r['status']=='candidate_unreviewed' else None for r in records if r['direction']==d] for d in DIRS}
 script='const assets='+json.dumps(assets)+';'
 template=HTML.replace('/*ASSETS*/',script)
 (preview/'index.html').write_text(template,encoding='utf-8')
 print(json.dumps({'candidateFrames':manifest['candidateFrameCount'],'expected':128,'manifestSHA256':sha(ROOT/'manifest.json')}))
HTML="""<!doctype html><html lang="zh"><meta charset="utf-8"><title>15 水龙书生 · 跑步检查</title><style>
body{font:16px system-ui;margin:22px;background:#edf3ef;color:#173b37}h1{font-size:22px}button,select,input{font:inherit;margin:5px;padding:6px} .wrap{display:flex;gap:24px;align-items:flex-start;flex-wrap:wrap}canvas{background:repeating-conic-gradient(#cfdfd9 0 25%,#e8efe9 0 50%) 50%/24px 24px;border:1px solid #799b8b}p{max-width:1000px}#small{width:144px;height:144px}#large{width:512px;height:512px} .warn{color:#903d30}
</style><h1>15 水龙书生 · 跑步候选检查</h1><p class="warn">候选制作中。静态/动态美术尚未通过；未接入客户端，未运行验收。空缺帧显示为缺帧，禁止复制已有帧填补。</p>
<label>方向 <select id="dir"></select></label><label>播放 <select id="speed"><option value="30">正常 30ms / 帧，480ms / 圈</option><option value="120">慢速 120ms / 帧</option><option value="240">慢速 240ms / 帧</option></select></label><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><input id="frame" type="range" min="1" max="16" value="1"><span id="label"></span>
<div class="wrap"><div><p>144px 画布（显示大小参考，非引擎验证）</p><canvas id="small" width="144" height="144"></canvas></div><div><p>512px 放大；横线为固定虚拟地面</p><canvas id="large" width="512" height="512"></canvas></div></div>
<p>观察：腿脚交替、反向摆臂、扇柄握点、支撑/蹬地/腾空/落地、头身体型、方向、16→01接缝。导出对整组使用相同缩放与平移，不按每帧最低脚对齐。</p>
<script>/*ASSETS*/
const $=id=>document.getElementById(id), cache={};let direction='E',frame=0,playing=true,last=0,drawn=new Set();window.reviewPlayback={cycles:0,framesShown:[],direction:'E',frameDurationMs:30};
for(const d in assets){$('dir').add(new Option(d,d));cache[d]=assets[d].map(p=>{if(!p)return null;let im=new Image();im.src=p;im.onload=()=>render();return im})}$('dir').value=direction;
function render(){let im=cache[direction][frame];for(const id of ['small','large']){let c=$(id),ctx=c.getContext('2d');ctx.clearRect(0,0,c.width,c.height);ctx.strokeStyle='#708f83';ctx.beginPath();ctx.moveTo(0,c.height*942/1024);ctx.lineTo(c.width,c.height*942/1024);ctx.stroke();if(im&&im.complete&&im.naturalWidth){ctx.drawImage(im,0,0,c.width,c.height)}else{ctx.fillStyle='#9c372f';ctx.font='16px sans-serif';ctx.fillText('缺帧 '+(frame+1),10,40)}}
$('label').textContent=direction+' '+String(frame+1).padStart(2,'0')+'/16';$('frame').value=frame+1;drawn.add(frame+1);window.reviewPlayback.framesShown=[...drawn].sort((a,b)=>a-b);window.reviewPlayback.currentFrame=frame+1}
function tick(t){if(playing&&t-last>=Number($('speed').value)){frame=(frame+1)%16;if(frame===0)window.reviewPlayback.cycles++;last=t;render()}requestAnimationFrame(tick)}requestAnimationFrame(tick);
$('dir').onchange=()=>{direction=$('dir').value;frame=0;drawn=new Set();window.reviewPlayback={cycles:0,framesShown:[],direction,frameDurationMs:Number($('speed').value)};render()};
$('speed').onchange=()=>window.reviewPlayback.frameDurationMs=Number($('speed').value);
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'暂停':'播放'};
for(const [id,delta] of [['prev',-1],['next',1]])$(id).onclick=()=>{playing=false;$('play').textContent='播放';frame=(frame+delta+16)%16;render()};
$('frame').oninput=()=>{playing=false;$('play').textContent='播放';frame=Number($('frame').value)-1;render()};render();
</script></html>"""
if __name__=='__main__': build()
