from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
from datetime import datetime, timezone

A=Path(__file__).resolve().parent; B=A.parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((A/'ne-w-selection.json').read_text(encoding='utf-8'))
chosen={f['slot']:f for f in s['frames'] if not f.get('review','').startswith('rejected')}
records=[]; groups=[]
P=A/'candidate-runtime'; P.mkdir(exist_ok=True)
for direction in ['NE','W']:
    before=[]; after=[]; ref=[]; contact=Image.new('RGB',(1024,1128),(235,238,240)); draw=ImageDraw.Draw(contact)
    for i in range(1,17):
        slot=f'run/{direction}/{i:02d}'; original=B/'runtime/run'/direction/f'{i:02d}.png'; f=chosen.get(slot)
        before.append(f'../../runtime/run/{direction}/{i:02d}.png')
        ref.append(f'../../../09_bamboo_archer_girl/runtime/run/{direction}/{i:02d}.png')
        if f:
            p=B/f['source']; im=Image.open(p).convert('RGBA'); assert im.size==(1254,1254)
            out=Image.new('RGBA',(1024,1024)); out.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
            target=P/f'{direction}-{i:02d}.png'; out.save(target); after.append('candidate-runtime/'+target.name)
            records.append({'slot':slot,'preview':target.relative_to(B).as_posix(),'sha256':sha(target),'source':f['source'],'sourceSha256':sha(p),'operation':'whole1254canvas→940;inset42,49;canvas1024;no local transform','status':'candidate_not_client_not_user_accepted'})
        else:
            out=Image.open(original).convert('RGBA'); after.append(before[-1])
        x=(i-1)%4*256; y=(i-1)//4*282
        draw.text((x+10,y+8),f'{direction}{i:02d} '+('edited candidate' if f else 'existing'),fill=(25,40,60))
        contact.paste(out.resize((256,256),Image.Resampling.LANCZOS),(x,y+26),out.resize((256,256),Image.Resampling.LANCZOS))
    contact.save(A/f'ne-w-{direction}-candidate-contact.png')
    groups.append({'direction':direction,'before':before,'after':after,'reference':ref})
(A/'ne-w-preview-provenance.json').write_text(json.dumps({'generatedAt':datetime.now(timezone.utc).isoformat(),'records':records,'timing':{'cycleMs':1200,'frameDurationsMs':[75]*16},'browserPlaybackReviewed':False},ensure_ascii=False,indent=2),encoding='utf-8')
data=json.dumps(groups,ensure_ascii=False)
html='''<!doctype html><meta charset="utf-8"><title>15 NE/W 局部候选对照</title><style>body{font:16px system-ui;background:#e9eef0;color:#233849;margin:24px}button,select{font:inherit;margin-right:12px;padding:8px}section{display:grid;grid-template-columns:repeat(3,260px);gap:12px;margin:20px 0}article{background:#fff;border-radius:12px;padding:10px}canvas{display:block;background:#f4f1e9;width:240px;height:240px}small{display:block;padding:4px}h2{margin-top:28px}</style><h1>NE/W 原版 · 局部候选 · 09参考</h1><p>75ms均匀 ×16帧＝1200ms。240px同步对照，未表示用户验收或客户端通过。09仅作运动参考，原图只读。</p><button id="play">暂停</button><button id="step">下一帧</button><select id="speed"><option value="1">1× 正常</option><option value="0.25">0.25× 慢放</option></select><span id="state">载入中</span><main></main><script>const groups=DATA;const views=[];for(const g of groups){const h=document.createElement('h2');h.textContent=g.direction;document.querySelector('main').append(h);const s=document.createElement('section');document.querySelector('main').append(s);for(const [key,label] of [['before','15 原版'],['after','15 局部候选'],['reference','09 用户指定参考']]){const a=document.createElement('article');a.innerHTML='<strong>'+label+'</strong><canvas width="240" height="240"></canvas><small></small>';s.append(a);views.push({c:a.querySelector('canvas'),l:a.querySelector('small'),paths:g[key],images:[],direction:g.direction,key});}}let running=true,clock=0,last=null,ready=false;function render(){const n=Math.floor((clock%1200)/75);for(const v of views){const x=v.c.getContext('2d');x.clearRect(0,0,240,240);x.drawImage(v.images[n],0,0,240,240);v.l.textContent=v.direction+' / '+String(n+1).padStart(2,'0')+' / 75ms';}document.querySelector('#state').textContent='第 '+(n+1)+' /16帧';}Promise.all(views.map(async v=>{v.images=await Promise.all(v.paths.map(p=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error(p));i.src=p;})));})).then(()=>{ready=true;render();}).catch(e=>{document.querySelector('#state').textContent='图片载入失败：'+e.message;});function frame(t){if(last!==null&&running&&ready)clock+=(t-last)*Number(document.querySelector('#speed').value);last=t;if(ready)render();requestAnimationFrame(frame);}requestAnimationFrame(frame);document.querySelector('#play').onclick=()=>{running=!running;document.querySelector('#play').textContent=running?'暂停':'播放';};document.querySelector('#step').onclick=()=>{running=false;document.querySelector('#play').textContent='播放';clock=(Math.floor(clock/75)+1)*75;if(ready)render();};</script>'''.replace('DATA',data)
(A/'ne-w-candidate-compare.html').write_text(html,encoding='utf-8')
print(json.dumps({'candidateFrames':len(records),'html':str(A/'ne-w-candidate-compare.html'),'contacts':[str(A/f'ne-w-{d}-candidate-contact.png') for d in ['NE','W']]},ensure_ascii=False))
