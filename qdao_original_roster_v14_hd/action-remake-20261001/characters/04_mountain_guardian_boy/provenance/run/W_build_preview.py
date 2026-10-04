from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
d=sys.argv[1]
if d not in ("W","NW"):raise ValueError(d)
out=ROOT/"provenance"/"run"
frames=[]
refs=[]
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",18)
sheet=Image.new("RGB",(1280,1360),(237,235,227))
draw=ImageDraw.Draw(sheet)
for n in range(1,17):
 p=ROOT/"frames"/"run"/d/f"frame_{n:02d}.png"
 x=((n-1)%4)*320;y=((n-1)//4)*340
 draw.text((x+10,y+8),f"{d}{n:02d}",fill=(20,30,20),font=font)
 if p.exists():
  im=Image.open(p).convert("RGBA");c=im.resize((320,320),Image.Resampling.LANCZOS)
  sheet.paste(c,(x,y+20),c)
  bg=Image.new("RGBA",(512,512),(240,237,226,255));bg.alpha_composite(im.resize((512,512),Image.Resampling.LANCZOS))
  frames.append(bg.convert("RGB"));refs.append({"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
 else:draw.text((x+80,y+160),"MISSING",fill=(150,80,60),font=font)
paths=[]
p=out/f"{d}_contact.png";sheet.save(p);paths.append(p)
if len(frames)==16:
 for speed,duration in [("normal",[40,50]*8),("slow",180),("trial640",40),("trial720",[40,50]*8),("trial800",50)]:
  p=out/f"{d}_{speed}.gif";frames[0].save(p,save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False);paths.append(p)
for p in paths:
 r={"file":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"derivedFrom":refs,"operation":"deterministic_preview_whole_canvas","modelGenerated":False,"time":datetime.now(timezone.utc).isoformat(),"timingNote":"normal为720ms候选试播，未批准为正式客户端值；slow为其0.25倍2880ms；另附640/720/800ms对比。GIF只有10ms粒度，720ms使用40/50ms交替。没有复制或插值姿态。","clientIntegration":"not_integrated"}
 p.with_suffix(p.suffix+".generation.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"direction":d,"count":len(frames),"paths":[str(p) for p in paths]}))

