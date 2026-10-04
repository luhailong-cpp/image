import json,sys,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
sys.stdout.reconfigure(encoding="utf-8")
r=Path(__file__).resolve().parents[2]
ip=r/"inventory-cast.json"; inv=json.loads(ip.read_text(encoding="utf-8")); now=datetime.now(ZoneInfo("America/New_York")).isoformat()
notes={"E04":"聚势抬符与前侧铃，五符，两袖；与05到06铃前后路径需动态复核。","E05":"原六符已重画为五符。","E06":"已修掉背面躯干突变；头部相对E01略大，待整段尺寸复核。","E07":"原第三袖已消除；头部相对E09略大，待整段尺寸复核。","E08":"原六符已重画为五符；头部相对E09略大，待整段尺寸复核。","E10":"已修掉背面躯干突变，保留释放跟随。","E11":"从突返准备改为屈肘渐进收势；尺寸仍待整段复核。","E16":"从原末帧偏大改为基于E01的新落定，首尾更接近。","W04":"原多符已重画五符；04到05站宽变化待动态复核。","W09":"以同组W06重画释放峰值，五符与袖臂清楚。","W12":"收招屈膝缓冲可读；11到12收腿速度需动态复核。"}
items=[]
for f in inv["frames"]:
 key=f["direction"]+str(f["frame"]).zfill(2); recp=r/f["source_record"]; rec=json.loads(recp.read_text(encoding="utf-8")); note=notes.get(key,"单图及联系表可辨五红符、左铃、两袖握持和两腿鞋；全段动态未通过。")
 status="pose_reviewed_sequence_pending"
 f["visual_status"]=status
 f["client_status"]="not_integrated"
 rec["visualQA"]={"status":status,"reviewedAt":now,"method":"工具返回完整原图与本地view_image/联系表人工观察","singleFrameFindings":note,"dynamicPassed":False,"registrationPassed":False}
 recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 items.append({"slot":"cast/"+f["direction"]+"/"+str(f["frame"]).zfill(2),"sha256":f["sha256"],"source_record":f["source_record"],"finding":note,"status":status})
for n in (6,7,8,11):
 p=r/"records"/f"cast-E-{n:02}-20261003-registration-v5.generation.json";rec=json.loads(p.read_text(encoding="utf-8"));rec["visualQA"]={"status":"rejected_registration","reason":"AI缩小整主体同时上移鞋底，未保持支撑地面；尤其E08明显。不选入正式槽，保留上一轮手脚修订。","reviewedAt":now};rec["selectedForExport"]=False;p.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
inv["qa_summary"]={"reviewedAt":now,"slots":32,"nativeAllAtLeast1024":True,"singleFrameAnatomyReviewed":32,"completeSequencesPassed":0,"dynamicStatus":"本轮cua.createBrowserTab(iab)返回Browser is not available: iab；listBrowsers=[]。主代理负责可用入口实播。","client_status":"not_integrated"}
ip.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
report={"reviewedAt":now,"character":"02_fire_talisman_boy","action":"cast","frames":items,"summary":inv["qa_summary"],"frame_duration_ms":45,"duration_ms":720,"modelTarget":"gpt-image-2.5-sunburst/max","actualModel":None,"actualQuality":None,"phasePlan":{"gather":"01-05","release":"06-10 peak09","recover":"11-16"},"remaining":["E06/07/08/11和相邻帧头部尺度细微变化；v5未能改善地面故不采用。","W04到05站宽、E05到06铃前后路径、E11到12及W11到12收势需正常与慢速实播确认。","同角色跨动作/跨方向全局配准及客户端移动实播未完成。"],"browserEvidence":{"createBrowserTab":"Browser is not available: iab","listBrowsers":[]},"previewOwner":"root已生成previews/cast-{E,W}-{normal,slow}.gif，PNG已更新须root重新构建确认SHA"}
(r/"records"/"cast-qa-20261003.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
old=r/"records"/"cast-qa-20261002.json"
if old.exists():
 x=json.loads(old.read_text(encoding="utf-8"));x["supersededBy"]="records/cast-qa-20261003.json";old.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(inv["qa_summary"],ensure_ascii=False))

