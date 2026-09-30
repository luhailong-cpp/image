"""Start the real 30ms clock only once all final PNGs have decoded."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'10-delivery-preview/current/index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('const imgs={},canvases={};','const imgs={},canvases={};let ready=false,loaded=0;const total=Object.keys(M.frames).length;const statusText=`库存 ${M.walkCount}/128 行走，${M.idleCount}/8 站立；验收状态：离线验收通过`;')
s=s.replace("const im=new Image();im.src=r.file+'?sha='+r.sha256;imgs[s]=im;", "const im=new Image();im.onload=()=>{loaded++;ready=loaded===total;if(ready)anchor=performance.now();document.querySelector('#status').textContent=ready?statusText:statusText+`；加载 ${loaded}/${total}`;};im.onerror=()=>{document.querySelector('#status').textContent='图片加载失败：'+r.file;};im.src=r.file+'?sha='+r.sha256;imgs[s]=im;")
s=s.replace("ctx.fillText('缺槽 '+s,25,50)","ctx.fillText((im?'载入中 ':'缺槽 ')+s,25,50)")
s=s.replace('if(playing){frame=', 'if(playing&&ready){frame=')
p.write_text(s,encoding='utf-8')
