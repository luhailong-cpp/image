import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2];W=B/'work/run-NE-cast'
versions={1:('eight-support',12),2:('eight-support',12),3:('eight-support',12),4:('eight-support',13),5:('eight-support',11),6:('eight-support',12),7:('eight-support',13),8:('eight-support',11),9:('eight-support',11),12:('eight-support',11),13:('eight-support',11),14:('eight-support',11),15:('eight-support',11)}
entries=[];frames=[]
for f in range(1,17):
    if f in (7,15):
        rec=f'records/run-NE-{f:02d}-finish-transition-v2.generation.json';r=json.loads((B/rec).read_text(encoding='utf-8-sig'));src=B/r['file'];im=Image.open(src).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS);status=r.get('visualQA',{}).get('status','not_reviewed')
    elif f in versions:
        phase,v=versions[f];rec=f'records/run-NE-{f:02d}-cast-20261004-{phase}-v{v}.generation.json';r=json.loads((B/rec).read_text(encoding='utf-8-sig'));src=B/r['file'];im=Image.open(src).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS);status=r.get('visualQA',{}).get('status','not_reviewed')
    else:
        rec=next(x['source_record'] for x in json.loads((B/'inventory-run-ne-cast.json').read_text(encoding='utf-8-sig'))['frames'] if x['frame']==f);src=B/f'frames/run/NE/{f:02d}.png';im=Image.open(src).convert('RGBA');status='retained_existing'
    dest=W/f'eight-support-selected-{f:02d}.png';im.save(dest);frames.append(im)
    entries.append({'frame':f,'source':src.relative_to(B).as_posix(),'source_record':rec,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidatePreview':dest.relative_to(B).as_posix(),'status':status})
(W/'eight-support-selection.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
for lower in [False,True]:
    canvas=Image.new('RGB',(1600,1720 if not lower else 1200),(39,51,64));d=ImageDraw.Draw(canvas)
    order=[16,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    for i,f in enumerate(order):
        pic=frames[f-1].copy();cx=(i%4)*400;cy=(i//4)*(430 if not lower else 300)
        if lower:pic=pic.crop((250,620,830,1024)).resize((400,278),Image.Resampling.LANCZOS)
        else:pic=pic.resize((400,400),Image.Resampling.LANCZOS)
        canvas.paste(pic,(cx,cy),pic);d.text((cx+7,cy+(280 if lower else 402)),f'NE {f:02d} / '+('RIGHT' if f in [16,1,2,3,4,5,6,7] else 'LEFT'),fill='white')
    canvas.save(W/('eight-support-lower-body.jpg' if lower else 'eight-support-contact.jpg'),quality=95)
small=[im.resize((512,512),Image.Resampling.LANCZOS) for im in frames]
for name,ms in [('normal',75),('slow',300)]:small[0].save(W/f'eight-support-{name}.apng',save_all=True,append_images=small[1:],duration=ms,loop=0,disposal=0,blend=0)
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>02 NE 连续支撑候选复核</title><style>body{background:#273340;color:white;font:16px sans-serif}img{width:512px;height:512px;object-fit:contain;background:#273340}button,select{font:inherit;margin:8px;padding:6px}small{display:block}</style><h1>NE 连续支撑候选</h1><p>16×75ms=1200ms。右16→07，左08→15。实际观感待复核，非客户端验收。</p><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="75">正常 1200ms</option><option value="300">慢放 4800ms</option></select><output id="label"></output><div><img id="sprite"><img src="eight-support-contact.jpg" style="height:auto;width:640px"></div><small>整画布等比显示，无逐帧贴地或bbox缩放。</small><script>let f=0,run=true,last=performance.now();const im=document.querySelector('#sprite'),lab=document.querySelector('#label'),speed=document.querySelector('#speed');const src=Array.from({length:16},(_,i)=>'eight-support-selected-'+String(i+1).padStart(2,'0')+'.png');src.forEach(s=>{let q=new Image;q.src=s});function show(){im.src=src[f];lab.value='帧 '+(f+1)+' / 16'}function tick(t){if(run&&t-last>=Number(speed.value)){f=(f+1)%16;last=t;show()}requestAnimationFrame(tick)}document.querySelector('#play').onclick=()=>{run=!run;document.querySelector('#play').textContent=run?'暂停':'播放';last=performance.now()};document.querySelector('#prev').onclick=()=>{run=false;f=(f+15)%16;show()};document.querySelector('#next').onclick=()=>{run=false;f=(f+1)%16;show()};show();requestAnimationFrame(tick)</script></html>'''
(W/'eight-support-review.html').write_text(html,encoding='utf-8')
print(json.dumps({'frames':len(entries),'contact':str(W/'eight-support-contact.jpg'),'preview':str(W/'eight-support-review.html')},ensure_ascii=False))
