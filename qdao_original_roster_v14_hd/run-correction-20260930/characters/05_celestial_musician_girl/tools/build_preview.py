"""05-only local review page, all controls are offline and read-only."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
BASE=Path(__file__).resolve().parents[1]
DIRS=['N','NE','E','SE','S','SW','W','NW']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for d in DIRS:
    for n in range(1,17):
        p=BASE/f'candidate/walk/{d}/{n:02}.png'
        if p.exists():
            records.append({'direction':d,'frame':n,'src':'../'+p.relative_to(BASE).as_posix(),'sha256':digest(p),'status':'candidate'})
        else:
            choices=sorted((BASE/f'generation/{d}').glob(f'{n:02}-v*.png')) if (BASE/f'generation/{d}').exists() else []
            if choices:
                p=choices[-1]
                records.append({'direction':d,'frame':n,'src':'../'+p.relative_to(BASE).as_posix(),'sha256':digest(p),'status':'raw-unaccepted'})
data=json.dumps(records,ensure_ascii=False)
html='''<!doctype html><meta charset="utf-8"><title>05 天音少女 · 跑步逐帧复核</title>
<style>*{box-sizing:border-box}body{margin:0;background:#161d25;color:#e8efef;font:16px system-ui;padding:22px}button,select,input{font:inherit}button,select{padding:8px 12px;border:1px solid #67747b;background:#263846;color:inherit;border-radius:6px}header{display:flex;gap:12px;align-items:center;flex-wrap:wrap}h1{font-size:22px}p{max-width:1050px;color:#bdcaca}#stages{display:flex;gap:20px;align-items:start;flex-wrap:wrap}.stage{position:relative;background:#e9e4d6;border:1px solid #67747b}.stage.dark{background:#202c38}.stage.check{background:repeating-conic-gradient(#ddd 0% 25%,#fff 0% 50%) 50%/24px 24px}.stage img{width:100%;height:100%;display:block}.floor{position:absolute;top:92%;left:0;right:0;border-top:1px dashed #d24d4d;pointer-events:none}.root{position:absolute;top:calc(92% - 5px);left:calc(50% - 5px);width:10px;height:10px;border:1px solid #d24d4d;border-radius:50%;pointer-events:none}#small{width:160px;height:160px}#large{width:600px;height:600px}#strip{display:grid;grid-template-columns:repeat(8,minmax(90px,1fr));gap:5px;margin-top:20px}#strip button{padding:3px;font-size:12px}#strip img{width:100%;background:#ede9de}.missing{color:#cd9696}#info{white-space:pre-wrap;font:13px ui-monospace}footer{padding-top:15px;color:#b9c6c7}</style>
<h1>05 天音少女 · 跑步复核</h1><p>只读本角色候选。原生稿和导出候选分别标记。文件齐全、播放器切帧不等于动态美术通过。160px 是小尺寸可读性检查，未验证为当前游戏屏幕尺寸。红线为固定虚拟地面，腾空时脚应离线；不会逐帧贴地。</p>
<header><label>方向 <select id="direction"></select></label><button id="play">播放</button><button id="prev">上一帧</button><button id="next">下一帧</button>
<label>速度 <select id="speed"><option value="30">正常 30ms / 480ms 一圈</option><option value="120">慢速 120ms / 1920ms 一圈</option><option value="240">极慢 240ms</option></select></label>
<label>背景 <select id="bg"><option value="">米白</option><option value="dark">深色</option><option value="check">棋盘</option></select></label><label><input id="guides" type="checkbox" checked>根点/地面</label><span id="counter"></span></header>
<p id="availability"></p><div id="stages"><div><p>160px · 小尺寸</p><div id="small" class="stage"><img><i class="floor"></i><i class="root"></i></div></div><div><p>600px · 放大</p><div id="large" class="stage"><img><i class="floor"></i><i class="root"></i></div></div></div><p id="info"></p><div id="strip"></div><footer>未接入客户端 / 未运行游戏验收。每张图的SHA、提示词及来源见 generation 与 candidate 相邻记录。</footer>
<script>
const records=DATA; const dirs=['N','NE','E','SE','S','SW','W','NW'];
const $=id=>document.getElementById(id); let current=1,playing=false,last=0; const seen=new Set();
dirs.forEach(d=>{let o=document.createElement('option');o.value=d;o.textContent=d;$('direction').append(o)});$('direction').value='E';
function row(n){return records.find(r=>r.direction==$('direction').value&&r.frame==n)}
function show(){let r=row(current);document.querySelectorAll('.stage img').forEach(i=>{i.style.visibility=r?'visible':'hidden';if(r)i.src=r.src});$('counter').textContent=String(current).padStart(2,'0')+'/16';$('info').textContent=r?(r.status+'\n'+r.src+'\nSHA256 '+r.sha256):'缺少此帧：不复制、补间或镜像替代';if(r)seen.add(r.direction+':'+r.frame);}
function selectDir(){playing=false;$('play').textContent='播放';current=1;$('strip').innerHTML='';for(let n=1;n<=16;n++){let b=document.createElement('button'),r=row(n);if(r){let i=new Image;i.src=r.src;b.append(i)}else{b.className='missing';b.textContent='缺图 '}b.append(document.createTextNode(String(n).padStart(2,'0')));b.onclick=()=>{playing=false;$('play').textContent='播放';current=n;show()};$('strip').append(b)}let count=records.filter(r=>r.direction==$('direction').value).length;$('availability').textContent='当前方向 '+count+'/16 张。'+(count===16?'可播放完整16帧；尚须视觉审阅。':'循环不完整，不启用动态播放。');$('play').disabled=count!==16;show()}
$('direction').onchange=selectDir;$('prev').onclick=()=>{current=(current+14)%16+1;show()};$('next').onclick=()=>{current=current%16+1;show()};
$('play').onclick=()=>{playing=!playing;last=performance.now();$('play').textContent=playing?'暂停':'播放'};
$('bg').onchange=()=>document.querySelectorAll('.stage').forEach(x=>x.className='stage '+$('bg').value);
$('guides').onchange=()=>document.querySelectorAll('.floor,.root').forEach(x=>x.style.display=$('guides').checked?'':'none');
function tick(t){if(playing&&t-last>=Number($('speed').value)){const steps=Math.floor((t-last)/Number($('speed').value));current=(current-1+steps)%16+1;last+=steps*Number($('speed').value);show()}requestAnimationFrame(tick)}selectDir();requestAnimationFrame(tick);
window.reviewState=()=>({direction:$('direction').value,frame:current,playing,ms:Number($('speed').value),seen:[...seen],available:records.length});
</script>'''.replace('DATA',data)
# Escape literal newlines inside JavaScript string literals.
html=html.replace("r.status+'\n'+r.src+'\nSHA256 '", "r.status+'\\n'+r.src+'\\nSHA256 '")
target=BASE/'preview/index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html,encoding='utf-8')
print(json.dumps({'preview':str(target),'availableFrames':len(records)}))

