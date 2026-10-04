from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
phases=["右腿前触地准备，右手回收盾前送","右脚平底承重缓冲，左腿在后","右脚支撑，左膝开始回收穿越","左膝前驱抬脚、右后脚将蹬","左腿前伸，右后脚前掌蹬离","左腿前伸腾空，右腿后折","左脚下降，右后腿抬起","左脚预接触，右腿仍在后","左脚接触，右臂持杖前送","左脚平底承重缓冲","左脚支撑、右腿前穿","右膝前驱，左腿仍在后支撑","右腿前抬，左脚蹬离；杖首低待动态复核","右腿前摆腾空","右脚下降，左腿后收","右脚预接触，准备回到01"]
rows=[]
for i,p in enumerate(sorted((R/"frames"/"run"/"SW").glob("*.png"))):
 g=json.loads(p.with_suffix(".generation.json").read_text(encoding="utf-8-sig"));n=R/g["nativeSource"]["path"]
 im=Image.open(p);a=im.getchannel("A")
 rows.append({"frame":i+1,"file":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"recordShaMatches":g["sha256"]==hashlib.sha256(p.read_bytes()).hexdigest(),"nativeSourcePresent":n.exists(),"nativeSourceShaMatches":n.exists() and hashlib.sha256(n.read_bytes()).hexdigest()==g["nativeSource"]["sha256"],"dimensions":list(im.size),"mode":im.mode,"alphaExtrema":a.getextrema(),"alpha128Bbox":a.point(lambda v:255 if v>=128 else 0).getbbox(),"observedPose":phases[i],"singleFrameInspected":True,"sequenceStatus":"pending_root_dynamic_review"})
out=R/"provenance"/"run"/"SW_static-review-20261003.json"
out.write_text(json.dumps({"updatedAt":datetime.now(timezone.utc).isoformat(),"scope":"16张当前修正帧全图与联系表静态复核；动态由根窗口复核","rows":rows,"focusTransitions":["03→04","11→12","12→13→14持杖","16→01"],"timingTrialsMs":[640,720,800],"timingAccepted":False,"rootAnchor":{"value":[512,928],"status":"declared_not_pixel_verified"},"clientIntegration":"not_integrated"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"frames":len(rows),"bad":[x["frame"] for x in rows if not (x["recordShaMatches"] and x["nativeSourceShaMatches"])]}))

