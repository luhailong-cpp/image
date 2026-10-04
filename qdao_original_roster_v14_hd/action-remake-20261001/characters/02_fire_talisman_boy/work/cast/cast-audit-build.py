import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.stdout.reconfigure(encoding="utf-8")
root=Path(__file__).resolve().parents[2]
inv=json.loads((root/"inventory-cast.json").read_text(encoding="utf-8"))
metrics=[]
for direction in ("E","W"):
 grid=Image.new("RGB",(1440,1520),"#263142");draw=ImageDraw.Draw(grid)
 for i in range(1,17):
  p=root/"frames"/"cast"/direction/f"{i:02}.png"
  if not p.exists():continue
  with Image.open(p) as im:
   im.load();a=im.getchannel("A");bounds=a.point(lambda p:255 if p>16 else 0).getbbox()
   metrics.append({"direction":direction,"frame":i,"size":list(im.size),"mode":im.mode,"bounds_alpha_gt16":bounds,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
   thumb=im.resize((360,360),Image.Resampling.LANCZOS)
   x=((i-1)%4)*360;y=((i-1)//4)*380
   draw.line((x,y+323,x+359,y+323),fill="#728798")
   grid.paste(thumb,(x,y),thumb);draw.text((x+8,y+362),f"{direction}{i:02} / 45 ms",fill="white")
 grid.save(root/"work"/"cast"/f"cast-{direction}-contact-current.jpg",quality=94)
(root/"records"/"cast-technical-20261003.json").write_text(json.dumps({"total":len(metrics),"frames":metrics,"note":"alpha bounds仅诊断，图像没有按bbox裁切/缩放/贴地。视觉与动态验收另记录。"},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frames":len(metrics),"contacts":["work/cast/cast-E-contact-current.jpg","work/cast/cast-W-contact-current.jpg"]}))

