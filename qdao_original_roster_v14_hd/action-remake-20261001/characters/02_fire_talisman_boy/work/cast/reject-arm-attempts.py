import json,hashlib
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2]
for n,reason in [(6,'仍为胸襟正面，近右肩连接屏左铃臂，未修正归属'),(7,'仍为胸襟正面，近右肩连接屏左铃臂，未修正归属'),(11,'持手已正确，但头部/头顶整体被明显抬高，接近画布边缘，未保持相邻帧构图')]:
 rp=root/f'records/cast-E-{n:02}-20261003-arm-chain-v8.generation.json';r=json.loads(rp.read_text(encoding='utf-8'))
 p=root/r['file'];im=Image.open(p)
 r.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),width=im.width,height=im.height,mode=im.mode,format='PNG')
 r['visualQA']={'status':'rejected','reason':reason,'formalExported':False}
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('3 rejected attempts recorded; formal frames untouched')
