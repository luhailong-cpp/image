from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
files=sorted((R/"frames"/"run"/"SW").glob("frame_*.png"))
out=R/"provenance"/"run"/"SW_contact.png"
canvas=Image.new("RGB",(1536,1632),(246,242,225));draw=ImageDraw.Draw(canvas);refs=[]
for i,p in enumerate(files):
 im=Image.open(p).convert("RGBA").resize((384,384),Image.Resampling.LANCZOS);x=i%4*384;y=i//4*408
 canvas.paste(im,(x,y+24),im);draw.text((x+8,y+5),p.stem,fill=(15,40,20))
 refs.append({"path":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
canvas.save(out)
out.with_suffix(".png.generation.json").write_text(json.dumps({"file":out.relative_to(R).as_posix(),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"operation":"deterministic_preview_contact_sheet","modelGenerated":False,"createdAt":datetime.now(timezone.utc).isoformat(),"derivedFrom":refs},ensure_ascii=False,indent=2),encoding="utf-8")
print(out)

for name,durations in (("SW_trial720.gif",[40,50]*8),("SW_slow2880.gif",[180]*16)):
 frames=[]
 for p in files:
  im=Image.open(p).convert("RGBA").resize((512,512),Image.Resampling.LANCZOS)
  bg=Image.new("RGBA",(512,512),(246,242,225,255));bg.alpha_composite(im);frames.append(bg.convert("RGB"))
 gif=R/"provenance"/"run"/name
 frames[0].save(gif,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2,optimize=False)
 gif.with_suffix(".gif.generation.json").write_text(json.dumps({"file":gif.relative_to(R).as_posix(),"sha256":hashlib.sha256(gif.read_bytes()).hexdigest(),"operation":"deterministic_animation_preview","modelGenerated":False,"createdAt":datetime.now(timezone.utc).isoformat(),"derivedFrom":refs,"frameDurationsMs":durations,"totalDurationMs":sum(durations),"timingStatus":"trial_not_client_acceptance","gifPrecisionNote":"GIF时间以10ms量化；720ms采用40/50交替保持整圈时长。"},ensure_ascii=False,indent=2),encoding="utf-8")
 print(gif)

