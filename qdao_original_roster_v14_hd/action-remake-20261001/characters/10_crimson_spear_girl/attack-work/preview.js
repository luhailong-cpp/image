"use strict";
const slots = {"E": {"1": "attack-E-01-feet-v1.png", "2": "attack-E-02-feet-v1.png", "3": "attack-E-03-ground-v3.png", "4": "attack-E-04-feet-v1.png", "5": "attack-E-05-feet-v1.png", "6": "attack-E-06-v6.png", "7": "attack-E-07-feet-v1.png", "8": "attack-E-08-feet-v1.png", "9": "attack-E-09-feet-v1.png", "10": "attack-E-10-feet-v1.png", "11": "attack-E-11-feet-v2.png", "12": "attack-E-12-feet-v1.png"}, "W": {"1": "attack-W-01.png", "2": "attack-W-02-feet-v2.png", "3": "attack-W-03-ground-v2.png", "4": "attack-W-04.png", "5": "attack-W-05.png", "6": "attack-W-06-v4.png", "7": "attack-W-07.png", "8": "attack-W-08.png", "9": "attack-W-09-ground-v1.png", "10": "attack-W-10.png", "11": "attack-W-11-ground-v1.png", "12": "attack-W-12.png"}};
const reviews = {"attack-E-01-feet-v1.png": "起势；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-02-feet-v1.png": "后腿加载蓄力；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-03-ground-v3.png": "最深蓄力；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。 ground-v3后脚鞋跟左、鞋头右；原生鞋底约1123，深蹲蓄力，双手和整枪保留。", "attack-E-04-feet-v1.png": "向前切入；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-05-feet-v1.png": "前刺推进；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-06-v6.png": "全伸前刺/接触候选；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。 v6枪尖完整，alpha32右界1247留7px；v4/v5触边弃用。", "attack-E-07-feet-v1.png": "跟进保持；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-08-feet-v1.png": "初始收回；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-09-feet-v1.png": "抬枪收势；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-10-feet-v1.png": "站距收回；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-E-11-feet-v2.png": "收稳近起势；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。 v1头身意外放大已拒绝；v2恢复原头位与尺寸。", "attack-E-12-feet-v1.png": "收势闭合；后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。", "attack-W-01.png": "起势；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。", "attack-W-02-feet-v2.png": "最大后载蓄力；后靴已局部修成鞋跟右/鞋尖左。 v1仍朝右已拒绝；v2鞋跟右、鞋尖左清楚。", "attack-W-03-ground-v2.png": "已开始向前切入；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 ground-v2双鞋跟右、鞋头左，鞋底1090；接新W04约1101–1114，只余11–24nativepx过渡差，不再微调重画。", "attack-W-04.png": "前刺展开；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 本目录保留原选源，接地替换由attack-W-grounding-work负责，总导出须以该目录明确selection为优先；此处不声称旧源接地通过。", "attack-W-05.png": "前刺接近全伸；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 本目录保留原选源，接地替换由attack-W-grounding-work负责，总导出须以该目录明确selection为优先；此处不声称旧源接地通过。", "attack-W-06-v4.png": "全伸前刺/接触候选；后靴已局部修成鞋跟右/鞋尖左。 本目录保留原选源，接地替换由attack-W-grounding-work负责，总导出须以该目录明确selection为优先；此处不声称旧源接地通过。", "attack-W-07.png": "跟进保持；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 本目录保留原选源，接地替换由attack-W-grounding-work负责，总导出须以该目录明确selection为优先；此处不声称旧源接地通过。", "attack-W-08.png": "折肘收回；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 本目录保留原选源，接地替换由attack-W-grounding-work负责，总导出须以该目录明确selection为优先；此处不声称旧源接地通过。", "attack-W-09-ground-v1.png": "抬枪收势；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 ground-v1鞋底1141，较共同面1120低21nativepx，收枪恢复站姿；保留透视容差。", "attack-W-10.png": "直立回收；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。", "attack-W-11-ground-v1.png": "近起势；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。 ground-v1两靴底1138，原1159/1154单帧下沉改善约22nativepx，残差18nativepx保留；枪尖完整左界7，双手/鞋轴W正确。头发顶部约上移27nativepx，须结合收势动态看，不为小漂移继续重画。", "attack-W-12.png": "收势；鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。"};
const el=id=>document.getElementById(id), c=el("canvas"), ctx=c.getContext("2d"), cache={};
let ready=false,playing=false,epoch=0,startFrame=6;
const direction=()=>el("direction").value,frame=()=>Number(el("frame").value);
function render(){
 const bg=el("background").value;ctx.fillStyle=bg==="light"?"#f3f0e8":"#233039";ctx.fillRect(0,0,1024,1024);
 if(bg==="grid"){for(let y=0;y<1024;y+=32)for(let x=0;x<1024;x+=32){ctx.fillStyle=((x+y)/32)%2?"#556768":"#7e8a85";ctx.fillRect(x,y,32,32);}}
 const filename=slots[direction()][frame()];
 if(filename && cache[filename])ctx.drawImage(cache[filename],0,0,1024,1024);
 else{ctx.fillStyle=bg==="light"?"#45574f":"#c0d0c7";ctx.font="32px system-ui";ctx.textAlign="center";ctx.fillText("缺帧 · "+direction()+" / "+String(frame()).padStart(2,"0"),512,512);}
 if(el("guides").checked){ctx.strokeStyle="#39d5c6";ctx.lineWidth=1;ctx.setLineDash([8,8]);ctx.beginPath();ctx.moveTo(0,942);ctx.lineTo(1024,942);ctx.moveTo(512,0);ctx.lineTo(512,1024);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle="#39d5c6";ctx.beginPath();ctx.arc(512,942,5,0,7);ctx.fill();}
 el("position").textContent=direction()+" · "+frame()+" / 12"+(frame()===6?" · 接触标记":"");
 el("status").textContent=filename?"当前为待修候选："+filename:"当前槽位缺失";
 el("review").textContent=filename?reviews[filename]:"缺槽没有图片，不使用占位PNG。";
}
function stop(){playing=false;el("play").textContent="播放";}
function tick(now){if(playing){const elapsed=Math.floor((now-epoch)/(30/Number(el("speed").value)));el("frame").value=((startFrame-1+elapsed)%12)+1;render();}requestAnimationFrame(tick);}
el("play").onclick=()=>{if(!ready)return;if(playing)stop();else{playing=true;startFrame=frame();epoch=performance.now();el("play").textContent="暂停";}};
el("prev").onclick=()=>{stop();el("frame").value=((frame()+10)%12)+1;render();};
el("next").onclick=()=>{stop();el("frame").value=(frame()%12)+1;render();};
el("frame").oninput=()=>{stop();render();};
el("direction").onchange=()=>{stop();el("frame").value=6;render();};
el("speed").onchange=()=>{startFrame=frame();epoch=performance.now();};
el("background").onchange=render;el("guides").onchange=render;
for(const d of ["E","W"])for(let n=1;n<=12;n++){
 const filename=slots[d][n],tr=document.createElement("tr");
 const tag=document.createElement("td");tag.textContent=d+" / "+String(n).padStart(2,"0");tr.append(tag);
 const status=document.createElement("td");status.textContent=filename?"已生成 · 待修":"缺帧";status.className=filename?"":"missing";tr.append(status);
 const link=document.createElement("td");
 if(filename){const a=document.createElement("a");a.href=filename;a.textContent="查看PNG";a.target="_blank";link.append(a,document.createTextNode(" · "));const b=document.createElement("a");b.href=filename+".generation.json";b.textContent="逐图来源";b.target="_blank";link.append(b);}else link.textContent="—";
 tr.append(link);el("rows").append(tr);
}
Promise.all(Object.values(slots).flatMap(o=>Object.values(o)).map(filename=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{cache[filename]=im;resolve();};im.onerror=()=>reject(new Error("无法加载 "+filename));im.src=filename;}))).then(()=>{ready=true;render();}).catch(e=>{el("status").textContent=e.message;});
render();requestAnimationFrame(tick);