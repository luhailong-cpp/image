from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
STATE=json.loads(r'''{"E":[["L","forefoot_toe_only","跨圈左脚最终蹬离，后跟高，不能充当满掌承重。"],["air","none","右领先上升腾空，双脚离地。"],["air","none","右腿前摆，脚尖上翘但鞋轴仍E。"],["air","none","右脚预触地，底面仍高于共同面。"],["R","full_sole","近右腿前足落地，全靴底压实，远左腿后折。"],["R","full_sole","近右腿屈膝缓冲，胫骨前倾，左腿前摆悬空。"],["R","forefoot_toe_only","右后支撑跟已明显抬起，缺少第三满掌承重。"],["R","forefoot_toe_only","右腿后伸且跟高，已近蹬离，缺少第四承重。"],["R","forefoot_toe_only","右最终蹬离，保留独立推进阶段。"],["air","none","远左领先腾空，近右屈膝遮挡远腿。"],["air","none","远左前摆，双脚离地。"],["air","none","左脚预触，鞋底仍高于共同面。"],["L","full_sole","远左落地，近右在前层屈膝后折。"],["L","full_sole","左腿屈膝压缩，右膝前摆保持近侧遮挡。"],["L","forefoot_toe_only","左后腿跟已明显抬起，缺少第三满掌承重。"],["L","forefoot_toe_only","左后腿已近蹬离，缺少第四承重。"]],"NE":[["air","none","左预触，两靴底向后下可见，左脚尚悬空。"],["L","full_sole","屏幕左腿初接触，后跟与前掌同落地面。"],["L","full_sole","左膝压缩、头髋降低，左鞋仍承重。"],["L","full_sole","左中支撑，右脚屈膝后折。"],["L","forefoot_toe_only","左跟明显升起露出底面，不能称满掌第四帧。"],["L","forefoot_toe_only","左前足蹬离，保留离地阶段。"],["air","none","右领先腾空，两膝弯曲且双脚离地。"],["air","none","右脚下降，靴底仍离地。"],["air","none","右低预触，靴底距共同面有空隙。"],["R","full_sole","屏幕右脚初触，左腿后折。"],["R","full_sole","右膝压缩，头髋下降，右鞋压实。"],["R","full_sole","右中支撑，左腿后折。"],["R","forefoot_toe_only","右跟抬起露底，不充当第四满掌承重。"],["air","none","右末蹬离将离地，底仍稍高于共同面；不计四帧。"],["air","none","左领先短腾空，两靴底可见。"],["air","none","左领先末段短腾空，高度与15近似，未声称明显下降。"]]}''')
for d,states in STATE.items():
 B=R/"run-contact-revision-20261004"/d;B.mkdir(parents=True,exist_ok=True)
 rows=[]
 for i,(foot,heel,note) in enumerate(states,1):
  p=R/"runtime/run"/d/f"{i:02d}.png";im=Image.open(p)
  rows.append(dict(frame=i,slot=f"run/{d}/{i:02d}",sourceFile=str(p.relative_to(R)).replace(chr(92),"/"),sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),contactFoot=foot,heelOrFullSole=heel,qualifiesForFourFrameLoadedSupport=heel=="full_sole",kneeAnkleSoleAligned=True,visualNote=note,durationMs=75,viewedCurrentRuntimeNative=True))
 report=dict(character="10_crimson_spear_girl",direction=d,reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewStage="before_revision_actual_runtime_32_images_viewed",frameMs=75,cycleMs=1200,threshold="At least4 genuinely grounded loaded frames per foot, including distinct compression/tibia/late support. Toe point is not full sole.",strongContactRuns=([dict(foot="R",frames=[5,6],durationMs=150),dict(foot="L",frames=[13,14],durationMs=150)] if d=="E" else [dict(foot="L",frames=[2,3,4],durationMs=225),dict(foot="R",frames=[10,11,12],durationMs=225)]),passesFourFrameRule=False,targetedFrames=([7,8,15,16] if d=="E" else [5,13]),outputScalePolicy="full-canvas-to1024-no-translation",frames=rows)
 (B/"contact-audit-before.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 (B/"selection.json").write_text(json.dumps({"slots":{}},indent=2),encoding="utf-8")
 print(d,len(rows))

