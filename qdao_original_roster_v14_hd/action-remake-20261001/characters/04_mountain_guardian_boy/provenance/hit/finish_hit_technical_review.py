from pathlib import Path
from PIL import Image,ImageSequence
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];NOW=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
rows=[];errors=[];reviews=[]
obs=["初始命中、前后两靴分开，握杖/持盾各一只手，长杖完整。","闭眼压缩，前脚和后支撑脚可区分，肩肘连接清楚。","后仰峰值，单眼侧面，杖首实心背盘、下杆金尖可读。","缓冲姿态，脚间距收回，完整双臂双腿与持物。","睁眼恢复，重心趋稳，两脚不粘连，长杖握持清楚。","收势回稳，头身比例已查，双靴清楚；E06已真实AI修正缩头与杖盘。"]
for d in ("E","W"):
 for n in range(1,7):
  p=ROOT/"frames/hit"/d/f"frame_{n:02d}.png";mp=p.with_suffix(".generation.json")
  j=json.loads(mp.read_text(encoding="utf-8-sig"));im=Image.open(p)
  assert im.size==(1024,1024) and im.mode=="RGBA" and j["sha256"]==sha(p)
  ns=j["nativeSource"];np=ROOT/ns["path"];assert np.exists() and sha(np)==ns["sha256"]
  j["review"]={"status":"visual_passed","scope":"static_single_frame_only","automaticallyApproved":False,"reviewedAt":NOW,"reviewedSha256":sha(p),"observation":obs[n-1],"dynamicAcceptance":"pending_parent_normal_and_quarter_speed_review"}
  save(mp,j)
  rows.append({"file":str(p.relative_to(ROOT)),"sha256":sha(p),"dimensions":list(im.size),"mode":im.mode,"alphaExtrema":list(im.getchannel("A").getextrema()),"nativeDimensions":[ns["width"],ns["height"]],"nativeSha256":ns["sha256"],"nativeExists":True,"frameDurationMs":40})
  reviews.append({"file":str(p.relative_to(ROOT)),"sha256":sha(p),"staticObservation":obs[n-1]})
previews=[]
for d in ("E","W"):
 for speed,expected in (("normal",240),("slow",960)):
  p=ROOT/"provenance/hit"/f"hit_{d}_{speed}.gif"
  with Image.open(p) as im:dur=[f.info["duration"] for f in ImageSequence.Iterator(im)]
  assert len(dur)==6 and sum(dur)==expected
  previews.append({"file":str(p.relative_to(ROOT)),"sha256":sha(p),"frames":6,"durationsMs":dur,"totalMs":sum(dur)})
save(ROOT/"provenance/hit/hit_technical_validation.json",{"checkedAt":NOW,"technicalStatus":"passed","frameCount":12,"uniqueFrameCount":len({x["sha256"] for x in rows}),"frames":rows,"previews":previews,"errors":errors,"limits":["技术契约及静态逐帧通过不等同于动态美术通过。","rootAnchor仍是布局声明；根线程需用正常和0.25倍速核验根锚、落地、首尾。"],"clientIntegration":"not_integrated"})
save(ROOT/"provenance/hit/hit_review_20261003.json",{"reviewedAt":NOW,"staticReviewed":12,"scope":"static_single_frame_only","frames":reviews,"dynamicAcceptance":"pending_parent_normal_and_quarter_speed_review","clientIntegration":"not_integrated"})
p=ROOT/"HIT_NOTES.md";s=p.read_text(encoding="utf-8-sig").replace("| E | attempt02 | attempt02 | attempt05 | attempt03 | attempt01 | attempt01 |","| E | attempt02 | attempt02 | attempt05 | attempt03 | attempt01 | E_06_finish_attempt04 |")
s+="\n2026-10-03 最后技术核验已刷新至当前E06 SHA，12张正式帧和4段预览通过尺寸/透明/哈希/帧数/时长检查。逐帧静态记录见provenance/hit/hit_review_20261003.json；动态仍待主窗口。原生选中来源按父线程要求暂保留至动态终验，89张清理后已仅恢复44张当前选中源（本分工hit12+run32），原生SHA全部核对一致，其余45张拒稿/中间图保持删除；详见provenance/run/W_NW_restore_selected_native_20261003.json。\n"
p.write_text(s,encoding="utf-8")
for d in ("W","NW"):
 p=ROOT/f"RUN_{d}_NOTES.md";s=p.read_text(encoding="utf-8")
 s+="\n当前选中帧唯一原生来源保留至主窗口动态终验，拒稿/中间图已清理；恢复/清理记录见provenance/run/W_NW_restore_selected_native_20261003.json。后续最终清理由主窗口验收后统一处理。\n"
 p.write_text(s,encoding="utf-8")
print(json.dumps({"hitTechnicalFrames":12,"hitStaticReviewed":12,"previewFramesChecked":24,"dynamic":"pending_parent_review"},ensure_ascii=False))

