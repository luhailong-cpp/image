from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
phases=["右腿前接触准备、左脚底朝后下；右臂腰侧回收、盾臂前送","右脚平底承重缓冲、左脚跟在后抬起","右脚支撑、左膝向前回收","左膝前驱、右脚后蹬；右持杖臂抬高前摆","左腿前伸、右腿后折，盾臂回摆","腾空换侧：右脚底在后下、左靴在前上；两膝弯曲","左脚下降准备接地、右脚后摆","左脚预接触，右脚底在后下","左腿前接触准备、右脚底朝后下；右臂向前、盾臂后摆","左脚平底承重缓冲、右脚跟在后抬起","左脚支撑、右膝前穿","右膝前驱，左后脚后蹬；右持杖臂开始回收","右腿前伸、左腿后折；杖首云纹较简化待动态看","右腿前摆腾空，左腿后摆","右脚下降、左腿在后","右脚预接触，准备回01"]
rows=[]
for i,p in enumerate(sorted((R/"frames"/"run"/"NE").glob("*.png"))):
 g=json.loads(p.with_suffix(".generation.json").read_text(encoding="utf-8-sig"));n=R/g["nativeSource"]["path"]
 im=Image.open(p);a=im.getchannel("A")
 rows.append({"frame":i+1,"file":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"recordShaMatches":g["sha256"]==hashlib.sha256(p.read_bytes()).hexdigest(),"nativeSource":g["nativeSource"],"nativeSourcePresent":n.exists(),"nativeSourceShaMatches":n.exists() and hashlib.sha256(n.read_bytes()).hexdigest()==g["nativeSource"]["sha256"],"dimensions":list(im.size),"mode":im.mode,"alphaExtrema":a.getextrema(),"alpha128Bbox":a.point(lambda v:255 if v>=128 else 0).getbbox(),"observedPose":phases[i],"singleFrameInspected":True,"sequenceStatus":"pending_root_dynamic_review"})
out=R/"provenance"/"run"/"NE_static-review-20261003.json"
out.write_text(json.dumps({"updatedAt":datetime.now(timezone.utc).isoformat(),"scope":"16张当前修正帧全图与联系表静态复核；动态由根窗口复核","rows":rows,"focusTransitions":["03→04杖首抬高与换侧","11→12换侧","12→13→14背盘纹样","16→01"],"timingTrialsMs":[640,720,800],"timingAccepted":False,"rootAnchor":{"value":[512,928],"status":"declared_not_pixel_verified"},"clientIntegration":"not_integrated"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"frames":len(rows),"bad":[x["frame"] for x in rows if not (x["recordShaMatches"] and x["nativeSourceShaMatches"])]}))
