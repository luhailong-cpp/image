import json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[2]
path=root/"inventory-run-ne-cast.json"
inv=json.loads(path.read_text(encoding="utf-8"))
notes={7:"五符，近右符臂远左铃臂可追踪；下落相位仍须动态确认，低左鞋露底较大，不判着地通过。",8:"五符与持手归属通过单图；左腿已伸至初触地、右腿折叠回收，承重需与新09连续实播。",10:"五符局部删除后无第六窄片；左支撑右摆腿清楚，朝NE，无V字外撇。",11:"手持物归属已修到右肩符/左肩铃，删除多余符后五张；左支撑右摆腿，须全组动态复核。",12:"从NE10重新画左后期支撑，恢复同组头身尺度；五符、左右持手正确，前掌着地点在斜后视角仍需实播确认。",13:"左右持手恢复正确且五符；左后伸脚露底较大，蹬离接地判断保留动态待核。",14:"短腾空，两脚不同屈膝相位，五符及持物归属清楚；脚轴随NE无明显V字外撇。",15:"右脚下降、左腿折叠回收，五符/持物归属可读；右后跟朝相机符合NE，非外撇。",16:"右脚初触地候选、左腿回收；五符/持物归属清楚，需与原01循环连接实播。"}
rows=[]
for e in inv["frames"]:
 n=e["frame"];e["visual_status"]="single_frame_reviewed_sequence_pending"
 recpath=root/e["source_record"];rec=json.loads(recpath.read_text(encoding="utf-8"))
 rec["visualQA"]={"status":e["visual_status"],"reviewedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"notes":notes[n],"fiveTalismans":True,"handOwnership":"right_talisman_left_bell","footAxis":"NE方向单图未见V字外撇，脚掌露底由屈膝/踝角造成","fullSequencePassed":False}
 recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 rows.append({"frame":n,"sha256":e["sha256"],"notes":notes[n]})
inv["qa_summary"]={"ownedSlots":9,"nativeMin":1254,"technicalStatus":"9张独立原生图全画布下采样1024 RGBA","dynamicStatus":"本分工工具IAB不可用(listBrowsers空)，未声称正常/慢速实播通过；交主代理统一预览复核","completeSequencePassed":False,"clientStatus":"not_integrated"}
path.write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"records/run-NE-cast-qa-20261003.json").write_text(json.dumps({"ownedFrames":rows,"notPassed":"07/12/13落地蹬离需动态验证，01/02/09原owner继续返修；全组需相邻尺寸/根点/手摆与承重核验","model":"目标gpt-image-2.5-sunburst/max；实际提交和返回版本质量均未披露"},ensure_ascii=False,indent=2),encoding="utf-8")
print("NE9 inventory and QA updated; sequence NOT passed")
