"""Build manifest, file checks, contact sheets and local interactive review from real frames."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
CONTRACT={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    entries=[];groups=[];missing=[];issues=[];pixelhashes={};filehashes={}
    for action,(count,ms) in CONTRACT.items():
        for direction in ['E','W']:
            files=[]
            for n in range(1,count+1):
                p=ROOT/'runtime'/action/direction/f'{n:02d}.png';rel=p.relative_to(ROOT).as_posix()
                if not p.exists():missing.append(rel);continue
                with Image.open(p) as im:
                    mode=im.mode;size=im.size;a=im.getchannel('A') if 'A' in im.getbands() else None
                    bbox=a.getbbox() if a else None;ext=a.getextrema() if a else None
                    counts=a.histogram() if a else []
                    corebbox=a.point(lambda x:255 if x>=16 else 0).getbbox() if a else None
                    edgevalues=list(a.crop((0,0,1,1024)).getdata())+list(a.crop((1023,0,1024,1024)).getdata())+list(a.crop((0,0,1024,1)).getdata())+list(a.crop((0,1023,1024,1024)).getdata()) if a else []
                    edgemax=max(edgevalues) if edgevalues else None
                    ph=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
                record=p.with_suffix('.png.generation.json')
                generation=json.loads(record.read_text(encoding='utf-8-sig')) if record.exists() else None
                h=sha(p)
                if mode!='RGBA' or size!=(1024,1024) or ext!=(0,255):issues.append({'file':rel,'type':'dimensions-or-alpha','mode':mode,'size':size,'alpha':ext})
                if corebbox and (corebbox[0]==0 or corebbox[1]==0 or corebbox[2]==1024 or corebbox[3]==1024):issues.append({'file':rel,'type':'visible-alpha-touches-edge','bbox':corebbox})
                if not generation or generation['sha256']!=h:issues.append({'file':rel,'type':'missing-or-mismatched-generation-record'})
                if ph in pixelhashes:issues.append({'file':rel,'type':'duplicate-pixels','other':pixelhashes[ph]})
                pixelhashes[ph]=rel;filehashes[rel]=h
                event='hit_recoil' if action=='hit' and n==3 else 'attack_contact' if action=='attack' and n==7 else 'cast_release' if action=='cast' and n==10 else None
                entry={'file':rel,'action':action,'direction':direction,'frame':n,'width':size[0],'height':size[1],'durationMs':ms,'pivot':[0.5,0.08],'nominalAnchorTopOrigin':[512,942],'event':event,'sha256':h,'rgbaPixelSha256':ph,'alpha':{'extrema':ext,'bbox':bbox,'transparentPixels':counts[0] if counts else 0,'partialPixels':sum(counts[1:255]) if counts else 0,'opaquePixels':counts[255] if counts else 0},'generationRecord':record.relative_to(ROOT).as_posix() if generation else None,'sourceReceipt':generation.get('evidence',{}).get('receipt') if generation else None,'visualStatus':'pending-final-review'}
                entry['alpha']['visibleBboxThreshold16']=corebbox
                entry['alpha']['edgeMaximum']=edgemax
                entry['alpha']['edgeTraceNote']='Preserved native low-alpha trace; no visible clipping detected' if edgemax and edgemax<16 else None
                entries.append(entry);files.append(rel)
            groups.append({'action':action,'direction':direction,'count':count,'durationMs':ms,'totalMs':count*ms,'files':files})
    manifest={'schemaVersion':1,'character':'赤砂魁','slug':'09-chishakui','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expectedFrames':68,'actualFrames':len(entries),'directions':{'E':'three-quarter front, down-right','W':'independently drawn three-quarter back, up-left'},'anatomy':{'arms':2,'legs':2,'wings':0,'visibleTail':0,'hammerHand':'anatomical-right','kiln':'one, strapped to center back'},'export':{'canvas':[1024,1024],'transform':'whole native square canvas uniformly resized to 1024; no per-frame alignment or crop','nominalAnchor':[512,942],'pivot':[0.5,0.08]},'clientIntegration':'not-performed','groups':groups,'frames':entries}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    check={'checkedAt':manifest['createdAt'],'expected':68,'found':len(entries),'missing':missing,'issues':issues,'technicalPassed':len(entries)==68 and not missing and not issues,'visualReview':'separate, not implied by technicalPassed','clientIntegration':'not-performed'}
    (ROOT/'validation.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {p}' for p,h in filehashes.items())+'\n',encoding='utf-8')
    preview=ROOT/'preview';preview.mkdir(exist_ok=True)
    for g in groups:
        if not g['files']:continue
        cols=4;cell=320;rows=(len(g['files'])+cols-1)//cols
        sheet=Image.new('RGB',(cols*cell,rows*(cell+28)),(39,49,53));d=ImageDraw.Draw(sheet)
        for i,f in enumerate(g['files']):
            x=(i%cols)*cell;y=(i//cols)*(cell+28)
            for cy in range(0,cell,20):
                for cx in range(0,cell,20):
                    d.rectangle([x+cx,y+cy,x+cx+19,y+cy+19],fill=(48,59,62) if (cx//20+cy//20)%2 else (58,69,72))
            with Image.open(ROOT/f) as im:
                s=im.convert('RGBA').resize((cell,cell),Image.Resampling.LANCZOS);sheet.paste(s,(x,y),s)
            d.text((x+10,y+cell+6),f'{g["action"]} {g["direction"]} {i+1:02d} / {g["durationMs"]} ms',fill='white')
        sheet.save(preview/f'{g["action"]}-{g["direction"]}-contact.png')
        if len(g['files'])==g['count']:
            timed=[]
            for f in g['files']:
                with Image.open(ROOT/f) as im:timed.append(im.convert('RGBA').resize((512,512),Image.Resampling.LANCZOS))
            for label,mult in [('normal',1),('slow025',4)]:
                timed[0].save(preview/f'{g["action"]}-{g["direction"]}-{label}.png',save_all=True,append_images=timed[1:],duration=g['durationMs']*mult,loop=0,disposal=0,blend=0)
            sources=[{'file':f,'sha256':filehashes[f]} for f in g['files']]
            (preview/f'{g["action"]}-{g["direction"]}.sources.json').write_text(json.dumps({'derivedFrom':sources,'contactOperation':'4-column contact sheet, uniform resize to 320; checkerboard and frame labels','animationOperation':'APNG, uniform resize to512, straight source frames; normal duration and 4x duration; no interpolation','isNewAIGeneration':False},indent=2),encoding='utf-8')
    data=json.dumps(manifest,ensure_ascii=False)
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>赤砂魁 · 战斗动作预览</title><style>*{box-sizing:border-box}body{margin:24px;background:#17262b;color:#efefda;font:16px system-ui}h1{font-size:24px}header{display:flex;align-items:center;gap:20px;flex-wrap:wrap}button,select,input{accent-color:#8fc7ae}button,select{padding:8px 14px;border-radius:8px;background:#dbe6d7;color:#213f35;border:0}main{display:grid;grid-template-columns:repeat(2,minmax(400px,1fr));gap:20px}.card{padding:16px;border:1px solid #658074;border-radius:12px;background:#20353a}.pair{display:flex;gap:10px}.view{flex:1;min-width:0}canvas{width:100%;display:block;background-color:#52605b;background-image:linear-gradient(45deg,#607068 25%,transparent 25%),linear-gradient(-45deg,#607068 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#607068 75%),linear-gradient(-45deg,transparent 75%,#607068 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}small{display:block;color:#b7cfc2;margin:5px}input[type=range]{width:100%}.readout{font-variant-numeric:tabular-nums}footer{margin:20px;color:#bad1c6}@media(max-width:950px){main{grid-template-columns:1fr}}</style><header><h1>赤砂魁 · 受击 / 普攻 / 施法</h1><button id="toggle">全部暂停</button><button id="reset">从首帧播放</button><label>背景 <select id="bg"><option value="check">棋盘</option><option value="#f1eee2">浅色</option><option value="#182326">深色</option></select></label></header><p>左侧原速，右侧 0.25 倍。每组暂停后可用滑块或左右键逐帧。客户端未接入。</p><main id="cards"></main><footer id="status"></footer><script>const M=__DATA__;const states=[];let allPaused=false;let started=performance.now();const cards=document.getElementById('cards');for(const g of M.groups){const el=document.createElement('section');el.className='card';el.id=g.action+'-'+g.direction;el.innerHTML=`<h2>${g.action} · ${g.direction} <small>${g.count} 帧 × ${g.durationMs} ms = ${g.totalMs} ms</small></h2><div class="pair"><div class="view"><canvas width="1024" height="1024"></canvas><small class="readout normal"></small></div><div class="view"><canvas width="1024" height="1024"></canvas><small class="readout slow"></small></div></div><button class="pause">暂停本组</button> <button class="prev">上一帧</button> <button class="next">下一帧</button><input aria-label="逐帧 ${g.action} ${g.direction}" type="range" min="0" max="${g.count-1}" value="0">`;cards.append(el);const s={g,el,images:g.files.map(f=>{const im=new Image();im.src='../'+f;return im}),paused:false,frame:0,canvases:[...el.querySelectorAll('canvas')]};states.push(s);const scrub=n=>{s.paused=true;s.frame=(n+g.count)%g.count;el.querySelector('input').value=s.frame;el.querySelector('.pause').textContent='播放本组'};el.querySelector('.pause').onclick=()=>{s.paused=!s.paused;el.querySelector('.pause').textContent=s.paused?'播放本组':'暂停本组'};el.querySelector('.prev').onclick=()=>scrub(s.frame-1);el.querySelector('.next').onclick=()=>scrub(s.frame+1);el.querySelector('input').oninput=e=>scrub(+e.target.value);el.onkeydown=e=>{if(e.key==='ArrowLeft'){e.preventDefault();scrub(s.frame-1)}if(e.key==='ArrowRight'){e.preventDefault();scrub(s.frame+1)}}}function draw(t){for(const s of states){const elapsed=t-started;const frames=[s.paused||allPaused?s.frame:Math.floor(elapsed/s.g.durationMs)%s.g.count,s.paused||allPaused?s.frame:Math.floor(elapsed*0.25/s.g.durationMs)%s.g.count];s.canvases.forEach((c,i)=>{const ctx=c.getContext('2d'),im=s.images[frames[i]];ctx.clearRect(0,0,1024,1024);if(im?.complete&&im.naturalWidth)ctx.drawImage(im,0,0);s.el.querySelector(i?'.slow':'.normal').textContent=(i?'0.25×':'1×')+' · '+String(frames[i]+1).padStart(2,'0')+' / '+s.g.count});if(!s.paused&&!allPaused){s.frame=frames[0];s.el.querySelector('input').value=s.frame}}requestAnimationFrame(draw)}requestAnimationFrame(draw);document.getElementById('toggle').onclick=()=>{allPaused=!allPaused;document.getElementById('toggle').textContent=allPaused?'全部播放':'全部暂停'};document.getElementById('reset').onclick=()=>{started=performance.now();allPaused=false;for(const s of states){s.paused=false;s.frame=0;s.el.querySelector('.pause').textContent='暂停本组'}document.getElementById('toggle').textContent='全部暂停'};document.getElementById('bg').onchange=e=>document.querySelectorAll('canvas').forEach(c=>{c.style.backgroundImage=e.target.value==='check'?'':'none';c.style.backgroundColor=e.target.value==='check'?'#52605b':e.target.value});document.getElementById('status').textContent=M.actualFrames+' / 68 帧已导出 · 1024×1024 RGBA · pivot (0.5, 0.08)';</script></html>'''.replace('__DATA__',data)
    (preview/'index.html').write_text(html,encoding='utf-8')
    print(json.dumps(check,ensure_ascii=False))
if __name__=='__main__':main()
