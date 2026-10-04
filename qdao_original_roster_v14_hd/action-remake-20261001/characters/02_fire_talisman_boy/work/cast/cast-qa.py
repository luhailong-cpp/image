import json,sys
from pathlib import Path
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
root=Path(__file__).resolve().parents[2]
paths=["frames/cast/E/01.png","frames/cast/E/02.png","frames/cast/E/03.png","frames/cast/E/09.png","work/cast/cast-E-01-v2-1024.png"]
entries=[]
for rel in paths:
 with Image.open(root/rel) as im:
  a=im.getchannel("A")
  entries.append({"path":rel,"size":im.size,"mode":im.mode,"bounds_alpha_gt_16":a.point(lambda p:255 if p>16 else 0).getbbox(),"bounds_alpha_gt_128":a.point(lambda p:255 if p>128 else 0).getbbox(),"edge_max_alpha":{"top":a.crop((0,0,im.width,1)).getextrema()[1],"bottom":a.crop((0,im.height-1,im.width,im.height)).getextrema()[1],"left":a.crop((0,0,1,im.height)).getextrema()[1],"right":a.crop((im.width-1,0,im.width,im.height)).getextrema()[1]}})
report={"character":"02_fire_talisman_boy","action":"cast","registration_target":{"root":[512,920],"ground_fraction":0.90,"nominal_full_hair_silhouette_top_fraction":0.14,"method":"AI修订；只用整画布统一1254至1024导出。不得由bbox诊断值独立缩放或贴地。"},"entries":entries,"visual_findings":[{"path":"frames/cast/E/01.png","status":"needs_registration_review","finding":"起势单独可读；相较09，起势整体画布占比偏大且鞋底偏低。"},{"path":"frames/cast/E/02.png","status":"needs_registration_and_sequence_review","finding":"聚势姿态独立；双手与道具清楚，体型/地面需比09复验，铃由前胸到03后肩的连续性需修订。"},{"path":"frames/cast/E/03.png","status":"needs_registration_and_sequence_review","finding":"聚势重试成功，左铃后抬与右符在胸前可读；与02手臂路径过渡待改。"},{"path":"frames/cast/E/09.png","status":"key_pose_passed_pending_global_registration","finding":"五红符、握持和双脚支撑清楚；脸朝E，躯干开放；待全组相机/尺寸一致性。"},{"path":"work/cast/cast-E-01-v2-1024.png","status":"registration_revision_pending_comparison","finding":"AI调整画布占比，未做bbox后处理；位置改善，头脸大小与五张符数量需再核实，因此未覆盖正式E01。"}],"status":"in_progress","target_frames":32,"exported_slots":4,"visually_passed_complete_sequences":0,"client_status":"not_integrated"}
(root/"records/cast-qa-20261002.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))

