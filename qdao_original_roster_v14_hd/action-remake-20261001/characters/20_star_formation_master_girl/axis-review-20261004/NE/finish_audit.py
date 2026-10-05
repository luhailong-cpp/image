from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
wr=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
candidate=ROOT/"axis-review-20261004/NE/05-axis-v1-1024.png"
native=ROOT/"axis-review-20261004/NE/05-axis-v1.png"
recfile=Path(str(native)+".generation.json")
record=rd(recfile)
reasons={
"NE01-04":"后跟朝镜头、鞋尖斜前，膝踝方向自然连续；抬起另一脚露底属于后摆。",
"NE05":"原图右支撑靴突然变为近纯E侧面，较04和06踝靴朝向突转；最小局部修正右踝与鞋尖，固定膝和接地点。",
"NE06":"后跟可辨、鞋尖短缩；近水平底边不足以证明外八，保留并与修正05连续检查。",
"NE07-08":"后侧支撑转后蹬，足跟升起改变投影，非踝部外翻；膝踝连接连续。",
"NE09-12":"左支撑靴近水平但跟尖中心仍略朝右上，与竹弓NE01同类短缩；无明确脚踝外折，不因鞋底边平而重画。",
"NE13-16":"左后支撑与后蹬足跟上提形成斜投影，腿轴自然；右后摆足露底正常。",
"SE01-04":"左支撑膝踝与鞋尖同向SE，右腿后折可辨，无脚尖外拧。",
"SE05-08":"左脚连续后侧支撑，右膝前摆及露底随自然屈膝；不把前摆露底等同外八。",
"SE09-12":"右支撑踝靴自然，鞋尖保持SE斜前；11/12承重下踩及回收属于已复核重心变化，非本轮轴向新增错误。",
"SE13-16":"左前摆腿膝至踝至鞋面中线连续朝右下；鞋底斜横截面不是纵轴，与竹弓SE05露底同类。13/14比15/16露底宽，但不足以判外扭。右后支撑正确。"
}
frames=[]
for d in ["NE","SE"]:
 for n in range(1,17):
  p=ROOT/f"runtime/run/{d}/{n:02d}.png"
  if d=="NE":
   group="NE01-04" if n<=4 else "NE05" if n==5 else "NE06" if n==6 else "NE07-08" if n<=8 else "NE09-12" if n<=12 else "NE13-16"
   support="right" if n<=8 else "left"
  else:
   group="SE01-04" if n<=4 else "SE05-08" if n<=8 else "SE09-12" if n<=12 else "SE13-16"
   support="left" if n<=8 else "right"
  im=Image.open(p)
  frames.append({"direction":d,"frame":n,"file":p.relative_to(ROOT).as_posix(),"auditedOriginalSha256":record["references"][0]["sha256"] if d=="NE" and n==5 else sha(p),"size":list(im.size),"mode":im.mode,"viewedAtFullFrame":True,"supportFoot":support,"positionPair":((n-1)%8)//2+1,"decision":"local_edit_candidate_ready" if group=="NE05" else "retain","reason":reasons[group]})
refpaths=[
"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/reference-motion-review-20261004/character-detail.jpg",
"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/runtime/run/NE/01.png",
"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/runtime/run/NE/09.png",
"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/runtime/run/NE/11.png",
"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/runtime/run/SE/05.png",
"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/runtime/run/SE/13.png"]
audit={"reviewedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"reviewer":"finish_ne_se","scope":"当前runtime跑步NE与SE共32张，轴向逐图及既有连图静态复核。","criteria":["自然膝踝屈伸，不把关节机械拉直","判跟至尖鞋长轴，不把鞋底横截面或正常露底判为外八","同支撑脚连续8张，四相对位置各两张独立图，75ms/帧、1200ms/圈保持"],
"references":[{"file":p,"sha256":sha(Path(p)),"viewed":True,"role":"仅动作范围参考，人物小且受遮挡，不作精确鞋角测量" if i==0 else "同向自然腿脚和鞋掌透视参考"} for i,p in enumerate(refpaths)],
"contactSheetsViewed":["preview/run-NE-contact.png","preview/run-SE-contact.png"],"frames":frames,"minimalConfirmedCorrection":[{"direction":"NE","frame":5,"leg":"right_support","change":"只将踝与靴回到NE斜前，后跟可见、鞋尖短缩，保留厚圆星靴、膝位与接地点"}],
"candidate":{"file":candidate.relative_to(ROOT).as_posix(),"sha256":sha(candidate),"nativeFile":native.relative_to(ROOT).as_posix(),"nativeSha256":sha(native),"generationRecord":recfile.relative_to(ROOT).as_posix(),"actualModel":None,"actualQuality":None,"modelQualityStatus":"宿主管理，工具未披露","review":"已实看04→新05→06三张：新05后跟朝镜头、鞋尖回右上，保持右脚承重；03/04至05/06身体经过支撑脚的变化保留。厚圆靴、红星和金边保留，未换支撑脚。","staticApproved":True,"dynamicAcceptance":False,"runtimeModifiedByThisAgent":False},
"summary":{"audited":32,"retain":31,"localEdit":1,"newGenerationCalls":1,"generatedNativeSize":[1254,1254],"exportSize":[1024,1024],"exportOperation":"整张画布1254等比缩至1024，offset[0,0]，无裁切、无整图平移、无镜像或插值姿态","clientIntegrated":False,"nextStep":"由root合入当前正式runtime并复核正常与慢放"}}
wr(ROOT/"axis-review-20261004/audit-NE-SE.json",audit)
record["review"]={"status":"passed_static_axis_review","dynamicAcceptance":False,"finding":audit["candidate"]["review"],"comparedWith":["runtime/run/NE/04.png","runtime/run/NE/06.png"],"retainsEightFrameRightSupport":True}
wr(recfile,record)
exportrecfile=Path(str(candidate)+".generation.json")
exportrec=rd(exportrecfile)
exportrec["derivedFrom"]["generationRecordSha256"]=sha(recfile)
wr(exportrecfile,exportrec)
print(json.dumps({"audit":"axis-review-20261004/audit-NE-SE.json","frames":len(frames),"candidate":str(candidate),"sha256":sha(candidate),"nativeSha256":sha(native)},ensure_ascii=False))

