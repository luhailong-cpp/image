"""将已审核的196帧交付到runtime；重建仅验证当前成品，不再次缩放。"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,shutil,argparse,subprocess,sys
from PIL import Image
from timing import RUN_TIMING,ACTION_FRAME_MS
from export_preview import PAGE
ROOT=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inside(p):
 p=p.resolve();assert p.is_relative_to(ROOT),p
 return p
parser=argparse.ArgumentParser();parser.add_argument("--promote",action="store_true");parser.add_argument("--rebuild",action="store_true");args=parser.parse_args()
sel=rd(ROOT/"selection.json")
review=rd(ROOT/"provenance/offline-visual-review.json")
reviewed={(g["action"],g["direction"]):g for g in review["groups"] if g.get("offlineVisualAccepted")}
grounding_complete=all(g.get("grounding4",{}).get("offlineReviewed",False) for g in review["groups"] if g["action"]=="run")
specs={"run":(["N","NE","E","SE","S","SW","W","NW"],16),"hit":(["E","W"],6),"attack":(["E","W"],12),"cast":(["E","W"],16)}
expected={(a,d,i) for a,(ds,n) in specs.items() for d in ds for i in range(1,n+1)}
keys={(f["action"],f["direction"],int(f["frame"])) for f in sel["frames"]}
assert keys==expected and len(sel["frames"])==196,(len(keys),len(expected),expected-keys)
assert len(reviewed)==14,"必须先完成14组实际视觉审核"
stamp=datetime.now(ZoneInfo("America/New_York")).isoformat()
if args.promote and sel.get("status")!="offline_delivery":
 wr(ROOT/"provenance/selected-native-source-index.json",sel)
 for f in sel["frames"]:
  native=inside(ROOT/f["source"]);assert sha(native)==f["sourceSha256"],native
  with Image.open(native) as im:assert min(im.size)>=1024 and im.mode=="RGBA"
  candidate=inside(ROOT/f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png")
  cr=rd(Path(str(candidate)+".generation.json"));assert sha(candidate)==cr["sha256"]
  assert cr["derivedFrom"]["sha256"]==f["sourceSha256"]
  assert cr["derivedFrom"]["generationRecordSha256"]==sha(ROOT/f["generationRecord"]),"来源文字记录已更新；请先重新导出candidate"
  dest=inside(ROOT/f"runtime/{f['action']}/{f['direction']}/{f['frame']:02}.png")
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate,dest)
  native_info={"file":f["source"],"sha256":f["sourceSha256"],"generationRecord":f["generationRecord"],"generationRecordSha256":sha(ROOT/f["generationRecord"]),"nativeSize":cr["operation"]["sourceCanvas"]}
  rec={**cr,"file":dest.relative_to(ROOT).as_posix(),"status":"offline_delivery","visualReview":"offline_reviewed","dynamicReview":"browser_normal_slow_sampled","reviewRecord":"provenance/offline-visual-review.json","clientIntegration":"not_integrated","userFinalAcceptance":False,"nativeOrigin":native_info}
  wr(Path(str(dest)+".generation.json"),rec)
  f.update(nativeOrigin=native_info,source=dest.relative_to(ROOT).as_posix(),sourceSha256=sha(dest),generationRecord=dest.relative_to(ROOT).as_posix()+".generation.json",inputIsFinalExport=True,status="offline_delivery",visualReview="offline_reviewed",dynamicReview="browser_normal_slow_sampled")
 sel.update(status="offline_delivery",updatedAt=stamp,selectionInputsMeaning="历史制作选表；当前成品以frames和merge-manifest为准",sourceInventory="provenance/selected-native-source-index.json")
 wr(ROOT/"selection.json",sel)
assert sel.get("status")=="offline_delivery","首次请在完成审核后使用--promote"
groups=[];files=[]
for a,(ds,count) in specs.items():
 for d in ds:
  fs=sorted([f for f in sel["frames"] if f["action"]==a and f["direction"]==d],key=lambda f:f["frame"])
  assert len({f["sourceSha256"] for f in fs})==count
  rows=[]
  for f in fs:
   p=inside(ROOT/f["source"]);rec=rd(ROOT/f["generationRecord"])
   assert sha(p)==f["sourceSha256"]==rec["sha256"]
   with Image.open(p) as im:
    im.load();assert im.size==(1024,1024) and im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255)
   row={**f,"candidate":f["source"],"runtime":f["source"],"sha256":sha(p),"exported":True,"previewUrl":"../"+f["source"],"generationRecordSha256":sha(ROOT/f["generationRecord"])}
   rows.append(row);files.append(row)
  groups.append({"action":a,"direction":d,"count":count,"required":count,"durationMs":ACTION_FRAME_MS[a],"loopMs":count*ACTION_FRAME_MS[a],"available":count,"frames":rows,"review":reviewed[(a,d)]})
manifest={"character":ROOT.name,"generatedAt":stamp,"status":"offline_delivery","expectedFrames":196,"exportedFrames":196,"staticVisualReviewed":196,"browserPlayback":"normal_and_slow_sampled","userFinalAcceptance":False,"clientIntegration":"not_integrated","clientValidation":"not_run","exportTransform":sel["exportTransform"],"runTiming":RUN_TIMING,"otherTimingsMs":{a:ACTION_FRAME_MS[a] for a in ["hit","attack","cast"]},"actionMarkers":{"attackContactFrame":6,"castReleaseFrame":10,"status":"offline_reference_not_client_validated"},"groups":groups,"errors":[],"selectionSha256":sha(ROOT/"selection.json"),"files":files}
wr(ROOT/"preview/manifest.json",manifest);wr(ROOT/"merge-manifest.json",manifest)
manifest["grounding4Reviewed"]=grounding_complete
manifest["offlineMaterialComplete"]=grounding_complete
wr(ROOT/"preview/manifest.json",manifest);wr(ROOT/"merge-manifest.json",manifest)
page=PAGE.replace("__DATA__",json.dumps(manifest,ensure_ascii=False).replace("<","\\u003c")).replace("__SUMMARY__","本机完整交付196/196帧").replace("__ERROR_COUNT__","0")
page=page.replace("候选动作检查","完整动作预览").replace("素材状态为候选；视觉及动态审核以人工记录为准。本预览不证明动作通过。","已逐图检查脚向与手持物，并抽看浏览器正常及慢放。尚未进行客户端或用户最终验收。").replace("可读取候选","可读取成品").replace("角色候选帧","角色动作帧").replace("槽位齐全；动态未验收","槽位齐全；离线已复核，游戏内待验收").replace("dynamic: not_verified","dynamic: offline_sampled")
(ROOT/"preview/index.html").write_text(page,encoding="utf-8")
state={"character":ROOT.name,"updatedAt":stamp,"expected":196,"selectedCandidates":196,"runtimeExported":196,"staticVisualReviewed":196,"offlineMaterialComplete":True,"userFinalAccepted":False,"clientIntegration":"not_integrated","clientValidation":"not_run","runTiming":RUN_TIMING,"groups":[{"action":g["action"],"direction":g["direction"],"required":g["count"],"exported":g["available"],"missing":[],"durationMs":g["durationMs"],"review":g["review"]} for g in groups],"remaining":["用户最终观感验收","另一台电脑按角色ID与SHA合并","客户端接入和游戏内根点/移动速度验收"]}
wr(ROOT/"STATUS.json",state)
state["offlineMaterialComplete"]=grounding_complete
state["grounding4Reviewed"]=grounding_complete
if not grounding_complete:state["remaining"].insert(0,"八方向每次连续4帧真实接地的新要求仍在复核/修正")
wr(ROOT/"STATUS.json",state)
lines=["# 20 星阵少女 · 本机完整交付","",f"更新：{stamp}。八方向跑步128帧、E/W受击12帧、普攻24帧、施法32帧，共196张1024×1024 RGBA。","", "本机素材与离线预览已整理完成；用户最终观感及客户端验收尚未完成。","", "|动作|方向|帧数|每帧时长|检查|","|---|---|---:|---:|---|"]
for g in groups:lines.append(f"|{g['action']}|{g['direction']}|{g['available']}/{g['count']}|{g['durationMs']}ms|逐帧脚向/手持物；正常及慢放抽看|")
lines+=["","[完整预览](preview/index.html) · [八方向跑步](preview/run-E-grounding.html) · [逐图清单](merge-manifest.json) · [合并交接](MERGE_HANDOFF.md)"]
(ROOT/"STATUS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
handoff=["# 星阵少女 · 合并交接","",f"更新：{stamp}。本机完整196帧已导出至runtime，逐动作逐方向检查如下。","","## 交付与播放","","- 游戏素材：runtime/run/{N,NE,E,SE,S,SW,W,NW}/01–16.png；runtime/hit/{E,W}/01–06.png；runtime/attack/{E,W}/01–12.png；runtime/cast/{E,W}/01–16.png。","- 全部为1024×1024 RGBA，逐图SHA、原生来源与模型记录见merge-manifest.json及图旁generation.json。","- 跑步正常1×1200ms/圈，16×75ms均匀播放，无额外尾帧停留。慢放4倍。","- 受击40ms/帧、普攻30ms/帧、施法45ms/帧。普攻接触第6帧、施法释放第10帧仅离线事件参考。","- 固定完整原生画布缩放到922×922，偏移(51,40)，根点(512,922)。没有逐帧最低像素贴地、bbox缩放、镜像或插值补帧。","","## 已复核与修正","","|动作/方向|保留|修正|当前检查|","|---|---|---|---|"]
for g in groups:
 r=g["review"];handoff.append(f"|{g['action']}/{g['direction']}|{r.get('retained','正确原生帧')}|{r.get('repaired','见逐帧记录')}|{r.get('footDirection','已检查脚向')}；{r.get('pose','已检查动作相位')}|")
handoff+=["","全部组已实看逐帧姿态、靴轴和道具手别；浏览器正常/慢放抽看与逐帧控制完成。固定地面线只是参考，客户端移动位移、投影及碰撞根点仍需游戏内验收。详见provenance/offline-visual-review.json。","","## 来源与合并边界","","目标GPT Image 2.5 Sunburst/max；实际使用内置宿主管理入口，没有型号/质量选择器，回执未披露实际值，实际model/quality均标记null/未确认。每图真实提示词、输入参考、回执、时间、原生尺寸与SHA均保留。","","另一电脑未提交内容未获取。合并时按完整角色ID和SHA对比；本机没有切分支、暂存、提交、推送或覆盖客户端。","","客户端未接入、未运行，用户最终验收未完成。当前离线完成不表示游戏内速度/滑步或用户观感已通过。"]
(ROOT/"MERGE_HANDOFF.md").write_text("\n".join(handoff)+"\n",encoding="utf-8")
contactlines=["","## 连续接地复核（2026-10-04新要求）","","16帧×75ms=1200ms保持不变；以下为实图复核的接地段，至少连续4个独立姿态，非重复图/插值/延长单帧。","","|方向|首次接地段|另一次接地段|本轮局部修正|","|---|---|---|---|"]
for g in groups:
 if g["action"]!="run":continue
 r=g["review"].get("grounding4",{});ss=r.get("contactSegments",[])
 strings=["→".join(f"{n:02}" for n in s["frames"])+f"（{len(s['frames'])*75}ms）" for s in ss]
 contactlines.append(f"|{g['direction']}|{strings[0] if strings else '待复核'}|{strings[1] if len(strings)>1 else '待复核'}|{r.get('replacementFrames',[])}|")
contactlines+=["","本轮局部编辑以既有1024最终构图为输入；返回原生图按整个画布等比导出1024，不再次套用922缩放/偏移，不改变根点。各图真实操作见图旁记录。","","新要求离线复核："+("已完成" if grounding_complete else "进行中，未判通过")+"；用户最终观感及客户端位移/滑步验收仍未完成。"]
with (ROOT/"MERGE_HANDOFF.md").open("a",encoding="utf-8") as f:f.write("\n".join(contactlines)+"\n")
with (ROOT/"STATUS.md").open("a",encoding="utf-8") as f:f.write("\n".join(contactlines)+"\n")
for script in ["build_sequence_previews.py","build_run_preview.py","build_overview.py"]:
 r=subprocess.run([sys.executable,"-X","utf8",str(ROOT/"tools"/script)],check=True,capture_output=True,text=True,encoding="utf-8");print(r.stdout.strip())
print(json.dumps({"runtime":len(files),"staticReviewed":196,"runLoopMs":1200,"clientIntegrated":False},ensure_ascii=False))
