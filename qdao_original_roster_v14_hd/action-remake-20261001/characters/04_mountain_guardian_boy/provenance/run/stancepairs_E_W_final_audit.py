from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
stages=["initial_load","body_passes_support","rear_support","rear_push_contact"]
stage_zh=["初承重：鞋底平直，支撑脚在身体略前","身体经过：同一脚继续承重","后支撑：同一脚后移，另一腿向前摆","后蹬：同一脚仍以鞋底或前脚掌接地"]
records=[]; issues=[]; previews=[]
for d in ("E","W"):
  for i in range(1,17):
    p=ROOT/"frames"/"run"/d/f"frame_{i:02}.png"
    side=p.with_suffix(".generation.json")
    data=json.loads(side.read_text(encoding="utf-8-sig"))
    h=sha(p)
    with Image.open(p) as im:
      if im.size!=(1024,1024) or im.mode!="RGBA":issues.append(f"{d}{i:02}: size/mode")
      alpha=im.getchannel("A").getextrema()
      if alpha[0]!=0 or alpha[1]!=255:issues.append(f"{d}{i:02}: alpha")
    if data["sha256"]!=h:issues.append(f"{d}{i:02}: sidecar hash")
    stage=(i-1)%8//2
    foot=("right" if i<=8 else "left") if d=="E" else ("left" if i<=8 else "right")
    replaced=i not in (2,3,10,11)
    rec={"direction":d,"frame":i,"file":p.relative_to(ROOT).as_posix(),"sha256":h,"generationRecord":side.relative_to(ROOT).as_posix(),"replacedThisPass":replaced,"supportFoot":foot,"supportFootMappingBasis":"侧视逐帧追踪裤腿、近远遮挡与持杖右手/持盾左臂；01–08和09–16各保持同一条支撑腿","supportStage":stages[stage],"stagePair":[stage*2+1+(8 if i>8 else 0),stage*2+2+(8 if i>8 else 0)],"observation":stage_zh[stage],"groundContactVisible":True,"shoeAxis":"随行进轴，未见明显向外翻掌","nativeSource":data.get("nativeSource"),"actualModel":data.get("actualModel"),"actualQuality":data.get("actualQuality"),"visualScope":"已查看原生候选、正式PNG和完整连图；素材静态通过。正常1×256px动态最终由角色根窗口复核。","clientIntegration":"not_integrated"}
    if replaced:
      rec["oldFrameSha256"]=data["replacement"]["oldFrameSha256"]
      if not (ROOT/data["nativeSource"]["path"]).is_file():issues.append(f"{d}{i:02}: native missing")
      if data.get("actualModel") is not None or data.get("actualQuality") is not None:issues.append(f"{d}{i:02}: unverified model not null")
      if data["operation"]["translation"]!=[0,0] or data["operation"]["crop"] is not None or data["operation"]["mirroring"] or data["operation"]["poseInterpolation"]:issues.append(f"{d}{i:02}: forbidden operation")
    records.append(rec)
  hashes=[x["sha256"] for x in records if x["direction"]==d]
  if len(set(hashes))!=16:issues.append(f"{d}: duplicate PNG")
  for speed,target in (("normal",1200),("slow",4800)):
    p=ROOT/"preview"/f"run_{d}_{speed}.apng"
    with Image.open(p) as im:
      durations=[]
      for n in range(im.n_frames):
        im.seek(n);durations.append(im.info.get("duration"))
    if len(durations)!=16 or sum(durations)!=target:issues.append(f"{d} {speed}: APNG timing")
    previews.append({"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"frameCount":len(durations),"durationsMs":durations,"loopMs":sum(durations)})
audit={"createdAt":now,"reviewer":"finish_side_pairs","scope":"04 run E/W 32正式帧；实际修正24、保留8。只写角色独占范围。","configTarget":{"model":"gpt-image-2.5-sunburst","quality":"max"},"actualModel":None,"actualQuality":None,"modelEvidenceNote":"宿主内置image_gen无型号/质量选择器，未回传可核实版本/质量。","reviewStatus":"static_passed_pending_root_dynamic_review","clientIntegration":"not_integrated","worldSpaceFootLock":"not_tested_no_local_client","footMap":{"E":{"01-08":"right","09-16":"left"},"W":{"01-08":"left","09-16":"right"}},"phaseRule":"每半轮8帧，同一支撑脚4位置段，每位置段2独立姿势；不以复制、镜像、插值、整图平移增加帧。","replacedSlots":{d:[x["frame"] for x in records if x["direction"]==d and x["replacedThisPass"]] for d in ("E","W")},"retainedSlots":{d:[2,3,10,11] for d in ("E","W")},"failedAttempt":"stancepairs_E_05_attempt03 网络发送错误；attempt04重新真实调用成功，未造回执。","retention":"本分工未清理任何native/拒稿；交角色根窗口统一按当前引用与用户保留策略处理。","issues":issues,"frames":records,"previews":previews}
out=ROOT/"provenance"/"run"/"stancepairs_E_W_review_20261004.json"
out.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["# E/W 双帧接地修正交接","",f"校验时间：{now}","", "已完成 32 正式帧：每方向替换 01、04、05、06、07、08、09、12、13、14、15、16，保留 02、03、10、11。","", "E：01–08 右腿支撑，09–16 左腿支撑。W：01–08 左腿支撑，09–16 右腿支撑。每半轮按 2 帧初承重、2 帧身体经过、2 帧后支撑、2 帧后蹬接触分段。靴轴随行进方向；同段两帧为独立姿势。","", "正常 APNG：16 × 75ms = 1200ms；慢速：16 × 300ms = 4800ms。静态原图与连图已查看，客户端未接入，世界空间锁脚未验收。正常 1×动态最终由根窗口复核。","", "模型目标 GPT Image 2.5 Sunburst / max；内置入口无选择器，实际型号和质量未确认。候选与回执均保留，E05 attempt03 网络失败记录保留，实际采用 attempt04。","", "文件校验问题："+("无" if not issues else "; ".join(issues)),"", "|方向|帧|本轮|支撑脚|位置段|正式SHA256|","|---|---|---|---|---|---|"]
for x in records:lines.append(f"|{x['direction']}|{x['frame']:02}|{'替换' if x['replacedThisPass'] else '保留'}|{x['supportFoot']}|{x['supportStage']}|{x['sha256']}|")
out.with_suffix(".md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"audit":str(out),"frames":len(records),"replaced":sum(x["replacedThisPass"] for x in records),"issues":issues,"previews":previews},ensure_ascii=False))

