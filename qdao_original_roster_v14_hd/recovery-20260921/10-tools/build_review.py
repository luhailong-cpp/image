"""Build a character-10 review snapshot from explicit selected real raw sources.
Only deterministic full-cell downsampling and anchor alignment, never new poses.
"""
from pathlib import Path
import argparse, hashlib, json, re
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw

REC = Path(__file__).resolve().parents[1]
ROOT = REC.parents[1]
DIRS = ('N','NE','E','SE','S','SW','W','NW')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def axis(im):
    y,x=np.where(np.asarray(im)[:,:,3]>8)
    top=int(y.min()); height=int(y.max())-top
    return float(np.median(x[y<top+max(1,int(height*.42))])),int(y.max())
def build(selection, revision):
    selected=json.loads(selection.read_text(encoding='utf-8-sig'))
    out=REC/'10-delivery-preview/revisions'/revision
    assert not out.exists(), 'Snapshots are immutable; choose a new revision'
    sources=set(); pixels=set(); rows={}
    for slot,item in selected.items():
        m=re.fullmatch(r'(N|NE|E|SE|S|SW|W|NW)(0[1-9]|1[0-6]|idle)',slot)
        assert m,slot
        direction,index=m.groups(); archive=REC/'10-generation'/item['archive']
        raw=archive/'raw.png'; record=archive/'raw.png.generation.json'
        meta=json.loads(record.read_text(encoding='utf-8'))
        assert sha(raw)==meta['sha256'] and sha(raw) not in sources,'Reused or changed raw'
        sources.add(sha(raw))
        im=Image.open(raw).convert('RGBA'); assert min(im.size)>=1024
        a=np.array(im.getchannel('A')); assert a.min()==0 and a.max()==255
        assert max(a[0].max(),a[-1].max(),a[:,0].max(),a[:,-1].max())<=8,'Native boundary crop'
        factor=1024/max(im.size)*.88
        size=(round(im.width*factor),round(im.height*factor))
        normal=im.resize(size,Image.Resampling.LANCZOS)
        ax,ay=axis(normal); delta=(round(512-ax),942-ay)
        box=normal.getbbox(); moved=[box[0]+delta[0],box[1]+delta[1],box[2]+delta[0],box[3]+delta[1]]
        assert min(moved[:2])>=1 and max(moved[2:])<=1023, (slot,'Would clip',moved)
        final=Image.new('RGBA',(1024,1024)); final.paste(normal,delta)
        rel=f'idle/{direction}.png' if index=='idle' else f'walk/{direction}/{index}.png'
        target=out/rel; target.parent.mkdir(parents=True,exist_ok=True); final.save(target)
        pixel_sha=hashlib.sha256(final.tobytes()).hexdigest()
        assert pixel_sha not in pixels,'Duplicate decoded frame'
        pixels.add(pixel_sha)
        row={'slot':slot,'file':rel,'sha256':sha(target),'pixelSHA256':pixel_sha,'archive':item['archive'],
             'rawSHA256':sha(raw),'nativeSize':list(im.size),'outputSize':[1024,1024],
             'sourceSelectionReview':item.get('review','pending'),'finalVisualReview':'pending',
             'anchor':list(axis(final)),'alphaBBox':final.getbbox()}
        rows[slot]=row
        write(Path(str(target)+'.generation.json'),{
            **row,'derivedFrom':[{'file':raw.relative_to(ROOT).as_posix(),'sha256':sha(raw),
                                 'generationRecord':record.relative_to(ROOT).as_posix(),'generationRecordSHA256':sha(record)}],
            'operation':{'type':'full-cell-LANCZOS-downsample-and-root-align','factor':factor,'commonScale':.88,
                         'translation':delta,'root':[512,942],'newPoseGenerated':False,'nativeAlphaPreserved':True,
                         'colorKeying':False,'despill':False,'noPerSubjectBBoxScaling':True},
            'actualModel':meta['actualModel'],'actualQuality':meta['actualQuality'],'unverifiedReason':meta['unverifiedReason']})
    expected=[d+f'{n:02}' for d in DIRS for n in range(1,17)]+[d+'idle' for d in DIRS]
    manifest={'character':'10_crimson_spear_girl','createdAt':datetime.now(timezone.utc).isoformat(),
              'selectionFile':selection.relative_to(ROOT).as_posix(),'selectionSHA256':sha(selection),
              'frameDurationMs':30,'loopDurationMs':480,'directions':list(DIRS),'frames':rows,
              'walkCount':sum(not s.endswith('idle') for s in rows),'idleCount':sum(s.endswith('idle') for s in rows),
              'missing':[s for s in expected if s not in rows],'visualReview':'pending','clientValidation':'not_performed'}
    write(out/'manifest.json',manifest)
    for direction in DIRS:
        for name,color in [('dark','#242a31'),('light','#f6f1e7')]:
            sheet=Image.new('RGB',(1536,4*408),color); draw=ImageDraw.Draw(sheet)
            for i in range(16):
                slot=direction+f'{i+1:02}'; x=(i%4)*384; y=(i//4)*408
                if slot in rows:
                    sprite=Image.open(out/rows[slot]['file']).convert('RGBA').resize((384,384),Image.Resampling.LANCZOS)
                    sheet.paste(sprite,(x,y),sprite)
                draw.text((x+10,y+388),slot+(' MISSING' if slot not in rows else ''),fill='white' if name=='dark' else 'black')
            path=out/'contact'/f'{direction}-{name}.jpg'; path.parent.mkdir(parents=True,exist_ok=True);sheet.save(path,quality=94)
    html=HTML.replace('__MANIFEST__',json.dumps(manifest,ensure_ascii=False))
    (out/'index.html').write_text(html,encoding='utf-8')
    print(json.dumps({'out':str(out),'walk':manifest['walkCount'],'idle':manifest['idleCount'],'missing':len(manifest['missing'])}))

HTML='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>赤枪少女 · 离线逐帧审阅</title>
<style>body{margin:24px;background:#172026;color:#e9e2d6;font:16px system-ui}h1{font-size:24px}button,select,input{font:inherit;margin:5px;padding:8px}#cards{display:grid;grid-template-columns:repeat(4,minmax(220px,1fr));gap:12px}article{border:1px solid #64736c;padding:8px}canvas{display:block;width:100%;height:auto}#zoom{width:min(1024px,95vw)}#status{color:#ffc879}a{color:#ace2d6}.light{background:#f6f1e7}</style>
<h1>10 赤枪少女 · 离线审阅</h1><p id="status"></p><p>真实图片序列，每帧30毫秒，完整16帧一圈480毫秒。缺槽留空；文件齐全不代表美术通过。</p>
<button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><button id="bg">切换深浅底</button><label><input type="checkbox" id="idle">独立站立</label><label><input type="checkbox" id="seam">仅15→16→01→02</label><input type="range" min="1" max="16" value="1" id="frame"><span id="counter"></span>
<div id="cards"></div><h2>放大逐帧</h2><select id="dir"></select><canvas id="zoom" width="1024" height="1024"></canvas><p>预览仅作素材离线检查，未执行Unity或正式客户端验收。<a href="manifest.json">固定素材与来源清单</a></p>
<script>const M=__MANIFEST__;let playing=true,frame=1,light=false,anchor=performance.now();const imgs={},canvases={};
document.querySelector('#status').textContent=`库存 ${M.walkCount}/128 行走，${M.idleCount}/8 站立；验收状态：${M.visualReview}`;
for(const d of M.directions){const a=document.createElement('article');a.innerHTML=`<b>${d}</b><canvas width="512" height="512"></canvas><a href="contact/${d}-dark.jpg">深底逐帧</a> · <a href="contact/${d}-light.jpg">浅底逐帧</a>`;document.querySelector('#cards').append(a);canvases[d]=a.querySelector('canvas');document.querySelector('#dir').add(new Option(d,d));}
for(const [s,r] of Object.entries(M.frames)){const im=new Image();im.src=r.file;imgs[s]=im;}
function draw(c,d){const ctx=c.getContext('2d'),s=d+(document.querySelector('#idle').checked?'idle':String(frame).padStart(2,'0'));ctx.fillStyle=light?'#f6f1e7':'#242a31';ctx.fillRect(0,0,c.width,c.height);const im=imgs[s];if(im&&im.complete&&im.naturalWidth)ctx.drawImage(im,0,0,c.width,c.height);else{ctx.fillStyle=light?'#933':'#fcc';ctx.font='22px system-ui';ctx.fillText('缺槽 '+s,25,50);}ctx.strokeStyle=light?'#ae9c7d':'#64736c';ctx.beginPath();ctx.moveTo(0,c.height*942/1024);ctx.lineTo(c.width,c.height*942/1024);ctx.stroke();}
function render(){for(const d of M.directions)draw(canvases[d],d);draw(document.querySelector('#zoom'),document.querySelector('#dir').value);document.querySelector('#frame').value=frame;document.querySelector('#counter').textContent=frame+'/16';}
document.querySelector('#play').onclick=()=>{playing=!playing;anchor=performance.now()-(frame-1)*30;document.querySelector('#play').textContent=playing?'暂停':'播放';};
document.querySelector('#prev').onclick=()=>{playing=false;frame=frame===1?16:frame-1;render();};document.querySelector('#next').onclick=()=>{playing=false;frame=frame===16?1:frame+1;render();};
document.querySelector('#frame').oninput=e=>{playing=false;frame=+e.target.value;render();};document.querySelector('#bg').onclick=()=>{light=!light;render();};document.querySelector('#dir').onchange=render;document.querySelector('#idle').onchange=render;
function tick(t){if(playing){frame=document.querySelector('#seam').checked?[15,16,1,2][Math.floor((t-anchor)/30)%4]:Math.floor((t-anchor)/30)%16+1;}render();requestAnimationFrame(tick);}requestAnimationFrame(tick);
</script></html>'''
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+',a.revision)
    build(a.selection.resolve(),a.revision)
